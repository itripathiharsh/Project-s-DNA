import os
import json
import logging
import math
import subprocess
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from typing import Any

from dna.storage.store import SCStore
from dna.evidence.store import EvidenceStore
from dna.api.routers.system import _get_store_path, _get_ev_path, _get_active_repo_path
from dna.reasoning.scores_engine import compute_all_scores, _function_metrics

logger = logging.getLogger("dna.api.predictive")
router = APIRouter(prefix="/v1/predictive", tags=["predictive"])


def _git_commit_velocity(repo_path: str):
    """Return (total_commits, monthly_velocity) from real git history."""
    try:
        r1 = subprocess.run(["git", "rev-list", "--count", "HEAD"],
                            cwd=repo_path, capture_output=True, text=True, timeout=15)
        total = int(r1.stdout.strip()) if r1.returncode == 0 and r1.stdout.strip().isdigit() else 0

        r2 = subprocess.run(["git", "log", "--oneline", "--since=90 days ago"],
                            cwd=repo_path, capture_output=True, text=True, timeout=15)
        recent = len([l for l in r2.stdout.strip().splitlines() if l]) if r2.returncode == 0 else 0
        velocity = recent / 3.0  # commits per month over last 3 months

        if velocity < 1.0 and total > 0:
            r3 = subprocess.run(["git", "log", "--reverse", "--format=%ci", "--max-count=1"],
                                cwd=repo_path, capture_output=True, text=True, timeout=15)
            if r3.returncode == 0 and r3.stdout.strip():
                first_date = datetime.strptime(r3.stdout.strip()[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                months_alive = max(1.0, (datetime.now(timezone.utc) - first_date).days / 30.0)
                velocity = total / months_alive

        return max(total, 0), max(velocity, 1.0)
    except Exception:
        return 0, 4.0


def _resolve_coupling(graph, file_entities, file_funcs):
    """Resolve coupling across all relation types (file→file, func→func, mixed)."""
    path_by_uid = {e.uid: e.file_path for e in file_entities}
    path_by_uid.update({"file:" + e.file_path: e.file_path for e in file_entities})
    path_by_uid.update({e.file_path: e.file_path for e in file_entities})

    func_to_file = {}
    for fe in file_entities:
        for fm in file_funcs.get(fe.file_path, []):
            uid = fm.get("uid", "")
            if uid:
                func_to_file[uid] = fe.file_path

    fan_in  = {fe.file_path: 0 for fe in file_entities}
    fan_out = {fe.file_path: 0 for fe in file_entities}
    pairs   = set()

    for r in graph.relations:
        def _resolve(uid):
            if uid in path_by_uid:
                return path_by_uid[uid]
            if uid in func_to_file:
                return func_to_file[uid]
            return None

        s = _resolve(r.source_uid)
        t = _resolve(r.target_uid)
        if s and t and s != t and (s, t) not in pairs:
            pairs.add((s, t))
            if s in fan_out: fan_out[s] += 1
            if t in fan_in:  fan_in[t]  += 1

    return fan_in, fan_out, len(pairs)

def _evidence_value(evidence) -> dict:
    raw = getattr(evidence, "value", "{}")
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}

def _change_count(value: dict) -> int:
    try:
        return int(float(value.get("change_count", value.get("changes", 0))))
    except (TypeError, ValueError):
        return 0

@router.get("/forecast")
async def get_predictive_forecast():
    store_path = _get_store_path()
    ev_path = _get_ev_path()
    repo_path = _get_active_repo_path()

    if not os.path.exists(store_path) or not os.path.exists(ev_path):
        raise HTTPException(
            status_code=400,
            detail="Store or evidence databases do not exist. Please run an onboarding analysis first."
        )

    try:
        # Load all scores to get quality, tech_debt, and health metrics
        all_scores = compute_all_scores(store_path, ev_path)
    except Exception as e:
        logger.exception("Failed to compute codebase scores")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute baseline scores: {str(e)}"
        )

    # 1. Load entities and relations
    with SCStore(store_path) as sc:
        graph = sc.load_entity_graph()

    # 2. Load evidence records
    with EvidenceStore(ev_path) as ev:
        evidence_items = ev.get_all()

    file_entities = [e for e in graph.entities if e.kind == "file"]
    function_entities = [e for e in graph.entities if e.kind == "function"]

    if not file_entities:
        raise HTTPException(
            status_code=400,
            detail="No files found in the analyzed codebase. Please run a full analysis first."
        )

    # Map functions to files for complexity computations
    funcs_metrics = []
    for f in function_entities:
        try:
            funcs_metrics.append(_function_metrics(f))
        except Exception:
            pass

    file_funcs = {}
    for f in funcs_metrics:
        file_funcs.setdefault(f["file_path"], []).append(f)

    # Group churn by file
    churn_by_file = {}
    for item in evidence_items:
        if item.type == "change_frequency" and item.file_path:
            churn_by_file[item.file_path] = churn_by_file.get(item.file_path, 0) + _change_count(_evidence_value(item))

    # Calculate complexity, cognitive complexity, and LOC per file
    file_complexity = {}
    file_cognitive = {}
    file_loc = {}
    for fe in file_entities:
        path = fe.file_path
        funcs = file_funcs.get(path, [])
        if funcs:
            # SUM all function complexities per file (not max) for true aggregate
            file_complexity[path] = sum(f["cyclomatic_complexity"] for f in funcs)
            file_cognitive[path] = sum(f["cognitive_complexity"] for f in funcs)
            file_loc[path] = sum(f["lines_of_code"] for f in funcs)
        else:
            file_complexity[path] = 1
            file_cognitive[path] = 0
            file_loc[path] = 10

    # Coupling: resolve across all relation types (file→file, func→func, mixed)
    file_fan_in, file_fan_out, total_file_edges = _resolve_coupling(
        graph, file_entities, file_funcs
    )
    # Keep file_relations count for compatibility
    file_relations_count = total_file_edges

    # Try-except and Dangerous pattern counts by file
    file_try_except = {}
    file_dangerous = {}
    file_test_coverage = {}

    # Import security scan patterns from scores_engine
    from dna.reasoning.scores_engine import SECURITY_SECRET_RE, SECURITY_DANGEROUS_PATTERNS
    
    for fe in file_entities:
        path = fe.file_path
        abs_path = os.path.join(repo_path, path)
        try_except = 0
        dangerous = 0
        if os.path.isfile(abs_path):
            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    try_except = content.count("except:") + content.count("except ")
                    dangerous += len(SECURITY_SECRET_RE.findall(content))
                    for pat in SECURITY_DANGEROUS_PATTERNS.values():
                        dangerous += len(pat.findall(content))
            except Exception:
                pass
        file_try_except[path] = try_except
        file_dangerous[path] = dangerous

        # Test coverage: test file itself OR has fan_in from a test file
        is_test = path.startswith("tests/") or path.startswith("test/") or "test" in path.lower()
        file_test_coverage[path] = 1.0 if is_test else 0.0

    # Normalization factors
    max_churn      = max(churn_by_file.values(), default=1) or 1
    max_complexity = max(file_complexity.values(), default=1) or 1
    max_loc        = max(file_loc.values(), default=1) or 1
    max_fan_in     = max(file_fan_in.values(), default=1) or 1

    # Filter: exclude cache/, .venv/, node_modules/, test files from predictions
    _SKIP_PREFIXES = ("cache/", ".venv/", "node_modules/", ".git/", "tests/", "test/")
    source_files = [
        f for f in file_entities
        if not any(f.file_path.startswith(p) for p in _SKIP_PREFIXES)
        and "test" not in f.file_path.lower()
    ]
    if not source_files:
        source_files = [f for f in file_entities if not any(f.file_path.startswith(p) for p in ("cache/", ".venv/"))]

    # --- 1. BUG PREDICTION ---
    bug_predictions = []
    for fe in source_files:
        path = fe.file_path
        churn_norm = churn_by_file.get(path, 0) / max(max_churn, 1)
        comp_norm = min(1.0, file_complexity.get(path, 1) / 30.0)
        loc_norm = min(1.0, file_loc.get(path, 10) / 1000.0)
        cov = file_test_coverage.get(path, 0.0)
        dang = min(1.0, file_dangerous.get(path, 0) / 5.0)

        prob = (churn_norm * 0.35) + (comp_norm * 0.25) + (loc_norm * 0.15) + ((1.0 - cov) * 0.15) + (dang * 0.10)
        prob = max(0.02, min(0.98, prob))

        bug_predictions.append({
            "file_path": path,
            "probability": round(prob * 100, 1),
            "reasons": [
                f"Churn impact: {round(churn_norm * 100)}%" if churn_norm > 0.4 else None,
                f"Complexity impact: {round(comp_norm * 100)}%" if comp_norm > 0.4 else None,
                "Lacks unit test coverage" if cov == 0.0 else None,
                f"Dangerous/secret patterns: {file_dangerous.get(path, 0)}" if dang > 0 else None
            ]
        })
    bug_predictions.sort(key=lambda x: -x["probability"])
    for bp in bug_predictions:
        bp["reasons"] = [r for r in bp["reasons"] if r is not None]
        if not bp["reasons"]:
            bp["reasons"] = ["Minor modifications, stable profile."]
    avg_bug_prob = sum(bp["probability"] for bp in bug_predictions) / len(bug_predictions)

    # --- 2. REGRESSION PREDICTION ---
    regression_predictions = []
    for fe in source_files:
        path = fe.file_path
        fan_in_norm = file_fan_in.get(path, 0) / max(max_fan_in, 1)
        comp_norm = min(1.0, file_complexity.get(path, 1) / 30.0)
        cov = file_test_coverage.get(path, 0.0)

        prob = (fan_in_norm * 0.45) + (comp_norm * 0.30) + ((1.0 - cov) * 0.25)
        prob = max(0.01, min(0.95, prob))

        regression_predictions.append({
            "file_path": path,
            "probability": round(prob * 100, 1),
            "reasons": [
                f"High incoming coupling ({file_fan_in.get(path, 0)} dependents)" if fan_in_norm > 0.3 else None,
                f"Complexity: {file_complexity.get(path, 1)}" if comp_norm > 0.4 else None,
                "No test coverage protection" if cov == 0.0 else None
            ]
        })
    regression_predictions.sort(key=lambda x: -x["probability"])
    for rp in regression_predictions:
        rp["reasons"] = [r for r in rp["reasons"] if r is not None]
        if not rp["reasons"]:
            rp["reasons"] = ["Low coupling, protected changes."]
    avg_reg_prob = sum(rp["probability"] for rp in regression_predictions) / len(regression_predictions)

    # --- 3. CRASH PROBABILITY ---
    crash_predictions = []
    for fe in source_files:
        path = fe.file_path
        comp = file_complexity.get(path, 1)
        try_except = file_try_except.get(path, 0)
        dang = file_dangerous.get(path, 0)

        handling_gap = max(0.0, 1.0 - (try_except / max(1, comp / 3)))
        dang_norm = min(1.0, dang / 3.0)
        comp_norm = min(1.0, file_cognitive.get(path, 0) / 20.0)

        prob = (handling_gap * 0.40) + (dang_norm * 0.30) + (comp_norm * 0.30)
        prob = max(0.01, min(0.95, prob))

        crash_predictions.append({
            "file_path": path,
            "probability": round(prob * 100, 1),
            "reasons": [
                f"Insufficient try-except handling ({try_except} blocks for complexity {comp})" if handling_gap > 0.5 else None,
                f"Dangerous API/Secret matches ({dang})" if dang > 0 else None,
                f"High Cognitive Complexity ({file_cognitive.get(path, 0)})" if comp_norm > 0.4 else None
            ]
        })
    crash_predictions.sort(key=lambda x: -x["probability"])
    for cp in crash_predictions:
        cp["reasons"] = [r for r in cp["reasons"] if r is not None]
        if not cp["reasons"]:
            cp["reasons"] = ["Adequate safety patterns, low exceptions."]
    avg_crash_prob = sum(cp["probability"] for cp in crash_predictions) / len(crash_predictions)

    # --- 4. SCALABILITY PREDICTION ---
    scalability_predictions = []
    for fe in source_files:
        path = fe.file_path
        comp = file_complexity.get(path, 1)
        fan_out = file_fan_out.get(path, 0)
        loc = file_loc.get(path, 10)

        bottleneck_score = (min(1.0, comp / 40.0) * 0.4) + (min(1.0, loc / 1500.0) * 0.3) + (min(1.0, fan_out / 10.0) * 0.3)
        bottleneck_score = max(0.0, min(1.0, bottleneck_score))

        scalability_predictions.append({
            "file_path": path,
            "score": round((1.0 - bottleneck_score) * 100, 1),
            "reasons": [
                f"High module complexity ({comp})" if comp > 15 else None,
                f"Large file length ({loc} LOC)" if loc > 600 else None,
                f"Tight outgoing dependencies ({fan_out} links)" if fan_out > 6 else None
            ]
        })
    scalability_predictions.sort(key=lambda x: x["score"])  # lower score means more scaling issues
    for sp in scalability_predictions:
        sp["reasons"] = [r for r in sp["reasons"] if r is not None]
        if not sp["reasons"]:
            sp["reasons"] = ["Highly modular, clean design."]
    avg_scalability_score = sum(sp["score"] for sp in scalability_predictions) / len(scalability_predictions)

    # Real git-based commit velocity (falls back gracefully on shallow clones)
    git_total, git_velocity = _git_commit_velocity(repo_path)

    # Supplement with evidence store commit count
    ev_commit_count = sum(1 for item in evidence_items if item.type == "commit_metadata")
    commit_count  = git_total if git_total > 0 else ev_commit_count
    commit_velocity = git_velocity if git_total > 0 else max(4.0, ev_commit_count / 3.0)

    quality_score_val = all_scores["scores"]["quality"]["score"]
    # drift_factor: 0.2 (high-quality) → 1.5 (low-quality)
    drift_factor = max(0.2, min(1.5, (100.0 - quality_score_val) / 45.0))
    monthly_debt_increase = commit_velocity * drift_factor * 0.55

    # --- 5. FUTURE TECHNICAL DEBT FORECAST ---
    debt_items = all_scores["scores"]["tech_debt"].get("debt_items", [])
    current_debt_units = sum(_as_float(item.get("effort_units"), 0.0) for item in debt_items)
    debt_timeline = []
    for m in range(13):
        projected = current_debt_units + (monthly_debt_increase * m)
        debt_timeline.append({
            "month": m,
            "value": round(projected, 1),
            "label": f"Month {m}" if m > 0 else "Current"
        })

    # --- 6. FUTURE COMPLEXITY FORECAST ---
    current_complexity = sum(file_complexity.values())
    monthly_complexity_increase = commit_velocity * 0.5 * drift_factor
    complexity_timeline = []
    for m in range(13):
        projected = current_complexity + (monthly_complexity_increase * m)
        complexity_timeline.append({
            "month": m,
            "value": round(projected, 1),
            "label": f"Month {m}" if m > 0 else "Current"
        })

    # --- 7. FUTURE COUPLING FORECAST ---
    current_files = len(file_entities)
    arch_violations_count = len(all_scores["scores"]["architecture"].get("affected_files", []))
    # Coupling density = unique file-pair edges / files (expressed as %)
    current_coupling_density = (file_relations_count / max(1.0, current_files)) * 100.0
    # Each commit adds ~0.3-0.5 new cross-file dependencies on average
    new_edges_per_commit = 0.4 * (1.2 if arch_violations_count > 0 else 0.9)
    monthly_new_edges = commit_velocity * new_edges_per_commit
    coupling_timeline = []
    for m in range(13):
        proj_files    = current_files + (commit_velocity * 0.05 * m)
        proj_edges    = file_relations_count + (monthly_new_edges * m)
        proj_density  = (proj_edges / max(1.0, proj_files)) * 100.0
        coupling_timeline.append({
            "month": m,
            "value": round(proj_density, 2),
            "label": f"Month {m}" if m > 0 else "Current"
        })

    # --- 8. FUTURE RISK FORECAST ---
    current_risk_score = 100.0 - all_scores["scores"]["health"]["score"]
    bus_factor_val = 1
    for check in all_scores["scores"]["health"].get("components", []):
        if check.get("name") == "knowledge_distribution_gate":
            bus_factor_val = check.get("measured", 1)
    # Risk grows faster for low-quality / single-owner codebases
    # Cap monthly rise: 0.2 (healthy) → 0.8 (unhealthy) per month
    risk_rise_rate = max(0.2, min(0.8,
        (0.4 if bus_factor_val <= 1 else 0.15) +
        (0.4 if quality_score_val < 75 else 0.1)
    ))
    risk_timeline = []
    for m in range(13):
        projected = min(95.0, current_risk_score + (risk_rise_rate * m))
        risk_timeline.append({
            "month": m,
            "value": round(projected, 1),
            "label": f"Month {m}" if m > 0 else "Current"
        })

    # --- 9. FUTURE ARCHITECTURE DRIFT FORECAST ---
    current_violations_count = 0
    for comp in all_scores["scores"]["architecture"].get("components", []):
        if comp.get("name") == "layer_boundary_score":
            current_violations_count = len(comp.get("measured", {}).get("violations", []))
    # ~0.03 new violations per commit when violations already exist, else 0.01
    monthly_viol_growth = commit_velocity * (0.03 if current_violations_count > 0 else 0.01)
    # Starting drift probability: violations → real signal; 0 violations → 5% base
    base_drift = min(60.0, current_violations_count * 12.0 + 5.0)
    drift_timeline = []
    for m in range(13):
        proj_viols = current_violations_count + (monthly_viol_growth * m)
        drift_prob = min(100.0, base_drift + (monthly_viol_growth * m * 8.0))
        drift_timeline.append({
            "month": m,
            "value": round(drift_prob, 1),
            "label": f"Month {m}" if m > 0 else "Current",
            "projected_violations": round(proj_viols, 1)
        })

    # --- 10. FUTURE MAINTENANCE COST FORECAST ---
    # Industry model: dev hours = files*base + complexity_penalty + bug_debt
    # Isolate from debt_units (which are huge) — use file+complexity driver only
    cost_base_per_file = 1.5 * (1.0 + (100.0 - quality_score_val) / 100.0)
    current_cost = (current_files * cost_base_per_file) + (current_complexity * 0.08)
    monthly_cost_increase = (
        (commit_velocity * 0.05 * cost_base_per_file)  # new files
        + (monthly_complexity_increase * 0.08)          # complexity growth
        + (monthly_debt_increase * 0.02)                # debt interest
    )
    cost_timeline = []
    for m in range(13):
        cost_m = current_cost + (monthly_cost_increase * m)
        cost_timeline.append({
            "month": m,
            "value": round(cost_m, 1),
            "label": f"Month {m}" if m > 0 else "Current",
            "cost_multiplier": round(cost_m / max(1.0, current_cost), 3)
        })

    return {
        "summary": {
            "overall_health": round(all_scores["scores"]["health"]["score"], 1),
            "total_files": len(source_files),
            "total_functions": len(function_entities),
            "total_commits": commit_count,
            "monthly_commit_velocity": round(commit_velocity, 1)
        },
        "bug_prediction": {
            "score": round(avg_bug_prob, 1),
            "top_affected": bug_predictions[:5]
        },
        "regression_prediction": {
            "score": round(avg_reg_prob, 1),
            "top_affected": regression_predictions[:5]
        },
        "crash_probability": {
            "score": round(avg_crash_prob, 1),
            "top_affected": crash_predictions[:5]
        },
        "scalability_prediction": {
            "score": round(avg_scalability_score, 1),
            "top_affected": scalability_predictions[:5]
        },
        "future_technical_debt": {
            "timeline": debt_timeline,
            "current_value": round(current_debt_units, 1)
        },
        "future_complexity": {
            "timeline": complexity_timeline,
            "current_value": round(current_complexity, 1)
        },
        "future_coupling": {
            "timeline": coupling_timeline,
            "current_value": round(current_coupling_density, 2)
        },
        "future_risk": {
            "timeline": risk_timeline,
            "current_value": round(current_risk_score, 1)
        },
        "future_architecture_drift": {
            "timeline": drift_timeline,
            "current_value": round(base_drift, 1)
        },
        "future_maintenance_cost": {
            "timeline": cost_timeline,
            "current_value": round(current_cost, 1)
        }
    }

def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
