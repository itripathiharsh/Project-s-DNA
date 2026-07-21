"""
Refactoring Suite API — 10 real-world refactoring analyses derived from
the SCStore entity graph and EvidenceStore. No mocked data.
"""
import os
import json
import logging
from collections import defaultdict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from dna.storage.store import SCStore
from dna.evidence.store import EvidenceStore
from dna.api.routers.system import _get_store_path, _get_ev_path, _get_active_repo_path
from dna.reasoning.scores_engine import (
    compute_all_scores, _function_metrics, _duplicate_function_details,
    _file_dependency_cycles, _layer_for_path,
)

logger = logging.getLogger("dna.api.refactoring_suite")
router = APIRouter(prefix="/v1/refactoring-suite", tags=["refactoring-suite"])

_SKIP = ("cache/", ".venv/", "node_modules/", ".git/", "tests/", "test/")


def _is_source(path: str) -> bool:
    return not any(path.startswith(p) for p in _SKIP) and "test" not in path.lower()


def _as_float(v: Any, d: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def _load(store_path, ev_path):
    with SCStore(store_path) as sc:
        graph = sc.load_entity_graph()
    with EvidenceStore(ev_path) as ev:
        evidence = ev.get_all()
    return graph, evidence


def _coupling(graph, file_entities, file_funcs):
    """Resolve all relation types into file-pair edges."""
    path_by_uid = {e.uid: e.file_path for e in file_entities}
    path_by_uid.update({"file:" + e.file_path: e.file_path for e in file_entities})
    func_to_file = {}
    for fe in file_entities:
        for fm in file_funcs.get(fe.file_path, []):
            uid = fm.get("uid", "")
            if uid:
                func_to_file[uid] = fe.file_path
    fan_in  = defaultdict(int)
    fan_out = defaultdict(int)
    pairs   = set()
    for r in graph.relations:
        def res(uid):
            return path_by_uid.get(uid) or func_to_file.get(uid)
        s, t = res(r.source_uid), res(r.target_uid)
        if s and t and s != t and (s, t) not in pairs:
            pairs.add((s, t))
            fan_out[s] += 1
            fan_in[t]  += 1
    return dict(fan_in), dict(fan_out), len(pairs)


def _churn(evidence):
    churn = defaultdict(int)
    for item in evidence:
        if item.type == "change_frequency" and item.file_path:
            try:
                v = json.loads(item.value) if isinstance(item.value, str) else item.value
                churn[item.file_path] += int(float(v.get("change_count", v.get("changes", 0))))
            except Exception:
                logger.debug("Failed to parse change_frequency evidence for %s", item.file_path)
    return dict(churn)


# ── shared loader ─────────────────────────────────────────────────────────────
def _build_context():
    store_path = _get_store_path()
    ev_path    = _get_ev_path()
    repo_path  = _get_active_repo_path()
    if not os.path.exists(store_path) or not os.path.exists(ev_path):
        raise HTTPException(400, "No analysis data. Run an analysis first.")
    graph, evidence = _load(store_path, ev_path)
    all_entities   = graph.entities
    file_entities  = [e for e in all_entities if e.kind == "file"]
    func_entities  = [e for e in all_entities if e.kind == "function"]
    src_files      = [e for e in file_entities if _is_source(e.file_path)]

    funcs_metrics: list[dict] = []
    for f in func_entities:
        try:
            m = _function_metrics(f)
            m["uid"] = f.uid
            funcs_metrics.append(m)
        except Exception:
            logger.debug("Failed to compute function metrics for %s", f.name if f else "?")
    file_funcs: dict[str, list] = defaultdict(list)
    for m in funcs_metrics:
        file_funcs[m["file_path"]].append(m)

    churn_map         = _churn(evidence)
    fan_in, fan_out, total_edges = _coupling(graph, file_entities, file_funcs)
    scores            = compute_all_scores(store_path, ev_path)
    return {
        "graph": graph, "evidence": evidence, "repo_path": repo_path,
        "file_entities": file_entities, "func_entities": func_entities,
        "src_files": src_files, "funcs_metrics": funcs_metrics,
        "file_funcs": file_funcs, "churn": churn_map,
        "fan_in": fan_in, "fan_out": fan_out, "total_edges": total_edges,
        "scores": scores,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 1. DEAD CODE CLEANUP
# ═══════════════════════════════════════════════════════════════════════════════
def _dead_code(ctx):
    fan_in  = ctx["fan_in"]
    fan_out = ctx["fan_out"]
    src     = ctx["src_files"]

    # Dead files: no other file imports them and they import nothing
    dead_files = []
    for fe in src:
        p = fe.file_path
        if fan_in.get(p, 0) == 0 and fan_out.get(p, 0) == 0:
            dead_files.append({
                "file_path": p, "reason": "No incoming or outgoing dependencies detected",
                "effort_hours": 0.5, "priority": "medium"
            })

    # Dead functions: uid has no incoming CALLS relations
    all_call_targets = {r.target_uid for r in ctx["graph"].relations if r.kind == "CALLS"}
    dead_funcs = []
    for m in ctx["funcs_metrics"]:
        if not _is_source(m["file_path"]):
            continue
        uid = m.get("uid", "")
        if uid and uid not in all_call_targets and not m["name"].startswith("__"):
            dead_funcs.append({
                "file_path": m["file_path"], "function": m["name"],
                "line": m["line"], "loc": m["lines_of_code"],
                "reason": "No CALLS relations pointing to this function",
                "effort_hours": 0.25, "priority": "low"
            })

    return {
        "dead_files": dead_files[:20],
        "dead_functions": dead_funcs[:30],
        "total_savings_loc": sum(m["lines_of_code"] for m in ctx["funcs_metrics"]
                                  if m.get("uid") not in all_call_targets
                                  and _is_source(m["file_path"])
                                  and not m["name"].startswith("__")),
        "summary": f"{len(dead_files)} unreferenced files, {len(dead_funcs)} potentially dead functions"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. DUPLICATE REMOVAL
# ═══════════════════════════════════════════════════════════════════════════════
def _duplicate_removal(ctx):
    details = _duplicate_function_details(ctx["funcs_metrics"], ctx["repo_path"])
    dups = details["duplicate_items"]

    # Also find files with same basename in different dirs
    by_name: dict[str, list] = defaultdict(list)
    for fe in ctx["src_files"]:
        by_name[os.path.basename(fe.file_path)].append(fe.file_path)
    dup_files = {name: paths for name, paths in by_name.items() if len(paths) > 1}

    groups = []
    for name, paths in list(dup_files.items())[:10]:
        groups.append({"filename": name, "occurrences": paths,
                        "action": "Consolidate into a shared module",
                        "effort_hours": len(paths) * 1.5})
    return {
        "duplicate_functions": dups[:20],
        "duplicate_filenames": groups,
        "total_duplicate_functions": details["duplicate_functions"],
        "summary": f"{details['duplicate_functions']} duplicate function bodies, {len(dup_files)} duplicate filenames"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. CLASS / FILE SPLIT
# ═══════════════════════════════════════════════════════════════════════════════
def _class_splits(ctx):
    suggestions = []
    for fe in ctx["src_files"]:
        p = fe.file_path
        funcs = ctx["file_funcs"].get(p, [])
        if len(funcs) < 7:
            continue
        # Group by name prefix
        groups: dict[str, list] = defaultdict(list)
        for f in funcs:
            name = f["name"]
            prefix = name.split("_")[0] if "_" in name else name[:4]
            groups[prefix].append(f)
        proposed_splits = [
            {"name": f"{prefix}_{os.path.basename(p)}",
             "functions": [f["name"] for f in fs],
             "estimated_loc": sum(f["lines_of_code"] for f in fs)}
            for prefix, fs in groups.items() if len(fs) >= 2
        ]
        if proposed_splits:
            total_complexity = sum(f["cyclomatic_complexity"] for f in funcs)
            suggestions.append({
                "file_path": p,
                "function_count": len(funcs),
                "total_complexity": total_complexity,
                "proposed_splits": proposed_splits[:5],
                "effort_hours": round(len(funcs) * 0.5, 1),
                "priority": "high" if total_complexity > 60 else "medium",
                "reason": f"{len(funcs)} functions — exceeds single-responsibility threshold"
            })
    suggestions.sort(key=lambda x: -x["total_complexity"])
    return {
        "suggestions": suggestions[:15],
        "summary": f"{len(suggestions)} files exceed single-responsibility threshold"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. PACKAGE SPLIT
# ═══════════════════════════════════════════════════════════════════════════════
def _package_splits(ctx):
    dirs: dict[str, list] = defaultdict(list)
    for fe in ctx["src_files"]:
        d = os.path.dirname(fe.file_path) or "root"
        dirs[d].append(fe.file_path)

    suggestions = []
    for d, files in dirs.items():
        if len(files) < 6:
            continue
        total_funcs = sum(len(ctx["file_funcs"].get(f, [])) for f in files)
        total_complexity = sum(
            m["cyclomatic_complexity"]
            for f in files
            for m in ctx["file_funcs"].get(f, [])
        )
        # Cluster by filename tokens
        sub_groups: dict[str, list] = defaultdict(list)
        for f in files:
            base = os.path.basename(f)
            key = base.split("_")[0] if "_" in base else base[:6]
            sub_groups[key].append(f)
        proposed = [{"sub_package": k, "files": v} for k, v in sub_groups.items() if len(v) >= 2]
        suggestions.append({
            "directory": d, "file_count": len(files), "total_functions": total_funcs,
            "total_complexity": total_complexity,
            "proposed_sub_packages": proposed[:4],
            "effort_hours": round(len(files) * 0.75, 1),
            "priority": "high" if len(files) > 12 else "medium",
            "reason": f"{len(files)} files in one directory — split into domain sub-packages"
        })
    suggestions.sort(key=lambda x: -x["file_count"])
    return {"suggestions": suggestions[:10], "summary": f"{len(suggestions)} directories suitable for splitting"}


# ═══════════════════════════════════════════════════════════════════════════════
# 5. DEPENDENCY BREAK PLANNER
# ═══════════════════════════════════════════════════════════════════════════════
def _dependency_breaks(ctx):
    graph = ctx["graph"]
    cycles = _file_dependency_cycles(graph)

    # Bottleneck files: high fan_in
    fan_in = ctx["fan_in"]
    bottlenecks = sorted(
        [(p, v) for p, v in fan_in.items() if _is_source(p) and v >= 3],
        key=lambda x: -x[1]
    )[:10]

    cycle_suggestions = []
    for cycle in cycles[:8]:
        paths = [uid.removeprefix("file:") for uid in cycle]
        cycle_suggestions.append({
            "cycle": paths,
            "length": len(paths),
            "action": "Introduce an abstraction (interface/protocol) at the entry point",
            "entry_point": paths[0],
            "effort_hours": len(paths) * 2.0,
            "priority": "critical"
        })

    bottleneck_suggestions = []
    for path, count in bottlenecks:
        bottleneck_suggestions.append({
            "file_path": path, "dependents": count,
            "action": f"Extract interface/facade — {count} files depend on this module",
            "effort_hours": round(count * 1.5, 1),
            "priority": "high" if count > 6 else "medium"
        })

    return {
        "cycles": cycle_suggestions,
        "bottlenecks": bottleneck_suggestions,
        "total_cycles": len(cycles),
        "summary": f"{len(cycles)} dependency cycles, {len(bottlenecks)} bottleneck modules"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 6. MODULARIZATION
# ═══════════════════════════════════════════════════════════════════════════════
def _modularization(ctx):
    fan_in  = ctx["fan_in"]
    fan_out = ctx["fan_out"]

    # Files with high internal-to-external ratio: good module candidates
    dirs: dict[str, list] = defaultdict(list)
    for fe in ctx["src_files"]:
        d = os.path.dirname(fe.file_path) or "root"
        dirs[d].append(fe.file_path)

    suggestions = []
    for d, files in dirs.items():
        if len(files) < 3:
            continue
        file_set = set(files)
        internal_edges = 0
        external_in = 0
        for f in files:
            external_in += sum(1 for p, _ in ctx["fan_in"].items()
                                if p == f and p not in file_set)
        # High cohesion: many functions, low external dependency
        total_funcs = sum(len(ctx["file_funcs"].get(f, [])) for f in files)
        ext_deps = sum(fan_out.get(f, 0) for f in files)
        cohesion_score = round(min(100, total_funcs * 5 / max(1, ext_deps)), 1)
        suggestions.append({
            "directory": d, "files": files, "file_count": len(files),
            "total_functions": total_funcs, "external_deps": ext_deps,
            "cohesion_score": cohesion_score,
            "action": f"Formalize as a proper Python package with __init__.py exports",
            "effort_hours": round(len(files) * 0.5, 1),
            "priority": "high" if cohesion_score > 70 else "medium"
        })
    suggestions.sort(key=lambda x: -x["cohesion_score"])
    return {"suggestions": suggestions[:12], "summary": f"{len(suggestions)} module candidates identified"}


# ═══════════════════════════════════════════════════════════════════════════════
# 7. MICROSERVICE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════
def _microservices(ctx):
    fan_in  = ctx["fan_in"]
    fan_out = ctx["fan_out"]
    dirs: dict[str, list] = defaultdict(list)
    for fe in ctx["src_files"]:
        d = os.path.dirname(fe.file_path) or "root"
        dirs[d].append(fe.file_path)

    candidates = []
    for d, files in dirs.items():
        if len(files) < 2:
            continue
        file_set = set(files)
        # Count external incoming deps (other dirs importing this dir's files)
        ext_in = sum(fan_in.get(f, 0) for f in files)
        ext_out = sum(fan_out.get(f, 0) for f in files)
        total_funcs = sum(len(ctx["file_funcs"].get(f, [])) for f in files)
        isolation_score = round(max(0, 100 - (ext_in + ext_out) * 8), 1)

        if isolation_score < 40:
            continue  # too coupled

        # Detect domain from dir name
        domain = d.split("/")[-1] if "/" in d else d
        candidates.append({
            "directory": d, "domain": domain, "files": files,
            "isolation_score": isolation_score,
            "external_incoming": ext_in, "external_outgoing": ext_out,
            "total_functions": total_funcs,
            "proposed_service_name": f"{domain}-service",
            "transport": "REST" if any("api" in f or "router" in f for f in files) else "gRPC",
            "effort_hours": round(len(files) * 4.0, 1),
            "priority": "high" if isolation_score > 75 else "medium",
            "action": f"Extract '{domain}' into an independent service with defined API contract"
        })
    candidates.sort(key=lambda x: -x["isolation_score"])
    return {"candidates": candidates[:10], "summary": f"{len(candidates)} microservice extraction candidates"}


# ═══════════════════════════════════════════════════════════════════════════════
# 8. ARCHITECTURE MIGRATION PLAN
# ═══════════════════════════════════════════════════════════════════════════════
def _architecture_migration(ctx):
    graph   = ctx["graph"]
    scores  = ctx["scores"]

    # Layer violations from architecture score
    violations = []
    for comp in scores["scores"]["architecture"].get("components", []):
        if comp.get("name") == "layer_boundary_score":
            violations = comp.get("measured", {}).get("violations", [])

    # Detect current layers
    layer_map: dict[str, list] = defaultdict(list)
    for fe in ctx["src_files"]:
        layer = _layer_for_path(fe.file_path)
        layer_map[layer].append(fe.file_path)

    target_layers = [
        {"layer": "api", "pattern": "api/routers/", "description": "HTTP handlers only — no business logic"},
        {"layer": "domain", "pattern": "engines/ or services/", "description": "Core business logic, framework-agnostic"},
        {"layer": "storage", "pattern": "storage/ or repositories/", "description": "Database and persistence layer"},
        {"layer": "model", "pattern": "models/ or entities/", "description": "Pure data models, no dependencies"},
    ]

    steps = []
    steps.append({
        "step": 1, "action": "Enforce import guards between layers",
        "detail": "Add linting rules to prevent api → storage direct imports",
        "effort_hours": 4.0, "priority": "high"
    })
    if violations:
        steps.append({
            "step": 2, "action": f"Fix {len(violations)} existing layer violations",
            "detail": "Move or refactor files that violate layer boundaries",
            "affected": [v.get("from", "") + " → " + v.get("to", "") for v in violations[:5]],
            "effort_hours": len(violations) * 2.0, "priority": "critical"
        })
    steps.append({
        "step": 3, "action": "Introduce domain service layer",
        "detail": "Extract business logic from API routers into dedicated service classes",
        "effort_hours": 12.0, "priority": "medium"
    })
    steps.append({
        "step": 4, "action": "Apply Dependency Inversion to storage layer",
        "detail": "Define repository interfaces in domain layer, implement in storage layer",
        "effort_hours": 8.0, "priority": "medium"
    })

    return {
        "current_layers": {layer: {"files": files[:5], "count": len(files)}
                           for layer, files in layer_map.items()},
        "target_architecture": target_layers,
        "violations": violations[:10],
        "migration_steps": steps,
        "total_effort_hours": sum(s["effort_hours"] for s in steps),
        "summary": f"{len(violations)} layer violations detected, {len(steps)}-step migration plan"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 9. ONE-CLICK REFACTORING PLAN
# ═══════════════════════════════════════════════════════════════════════════════
def _one_click_plan(ctx, all_analyses):
    actions = []

    # Pull top items from each analysis
    for item in all_analyses["dead_code"]["dead_files"][:3]:
        actions.append({"type": "dead_code", "priority": 2, "file": item["file_path"],
                         "action": "Delete unreferenced file", "effort_hours": 0.5})
    for item in all_analyses["duplicate_removal"]["duplicate_functions"][:3]:
        actions.append({"type": "duplicate", "priority": 3, "file": item["file_path"],
                         "action": f"Remove duplicate function `{item['name']}`",
                         "effort_hours": 1.0})
    for item in all_analyses["dependency_breaks"]["cycles"][:2]:
        actions.append({"type": "dep_cycle", "priority": 1, "file": item["entry_point"],
                         "action": f"Break {item['length']}-node dependency cycle",
                         "effort_hours": item["effort_hours"]})
    for item in all_analyses["class_splits"]["suggestions"][:3]:
        actions.append({"type": "class_split", "priority": 2, "file": item["file_path"],
                         "action": f"Split into {len(item['proposed_splits'])} focused modules",
                         "effort_hours": item["effort_hours"]})
    for item in all_analyses["microservices"]["candidates"][:2]:
        actions.append({"type": "microservice", "priority": 3, "file": item["directory"],
                         "action": f"Extract '{item['domain']}' as independent service",
                         "effort_hours": item["effort_hours"]})

    actions.sort(key=lambda x: x["priority"])
    total_hours = sum(a["effort_hours"] for a in actions)
    return {
        "actions": actions,
        "total_actions": len(actions),
        "estimated_effort_hours": round(total_hours, 1),
        "estimated_effort_days": round(total_hours / 8, 1),
        "summary": f"{len(actions)} prioritized refactoring actions, ~{round(total_hours/8,1)} dev days"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 10. REFACTORING SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════
class SimulateRequest(BaseModel):
    file_path: str

@router.post("/simulate")
async def simulate_refactoring(req: SimulateRequest):
    ctx = _build_context()
    path = req.file_path
    fan_in  = ctx["fan_in"]
    fan_out = ctx["fan_out"]
    churn   = ctx["churn"]

    funcs   = ctx["file_funcs"].get(path, [])
    total_complexity = sum(f["cyclomatic_complexity"] for f in funcs)
    total_loc        = sum(f["lines_of_code"] for f in funcs)
    dependents_count = fan_in.get(path, 0)
    deps_count       = fan_out.get(path, 0)
    churn_count      = churn.get(path, 0)

    # Risk: high dependents + high complexity = risky refactor
    risk_score = min(100, (dependents_count * 15) + (total_complexity * 2) + (churn_count * 3))
    # Benefit: high complexity reduction potential
    benefit_score = min(100, total_complexity * 3 + len(funcs) * 5)
    effort_hours = round((len(funcs) * 0.5) + (dependents_count * 1.5) + (total_complexity * 0.2), 1)

    breakage = []
    for fe in ctx["src_files"]:
        if fan_in.get(path, 0) > 0:
            breakage.append(fe.file_path)
    breakage = breakage[:dependents_count]

    return {
        "file_path": path,
        "metrics": {
            "functions": len(funcs), "total_complexity": total_complexity,
            "total_loc": total_loc, "dependents": dependents_count,
            "dependencies": deps_count, "churn_events": churn_count,
        },
        "simulation": {
            "risk_score": risk_score,
            "benefit_score": benefit_score,
            "effort_hours": effort_hours,
            "complexity_reduction": f"{round(total_complexity / max(1, len(ctx['src_files'])) * 100, 1)}% of codebase complexity",
            "files_requiring_update": dependents_count,
            "affected_files": breakage[:8],
            "recommendation": (
                "Proceed with care — high dependent count" if risk_score > 60
                else "Good candidate — isolated with high complexity" if benefit_score > 50
                else "Low priority — consider other refactoring targets first"
            )
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER ENDPOINT: /v1/refactoring-suite/analysis
# ═══════════════════════════════════════════════════════════════════════════════
@router.get("/analysis")
async def get_refactoring_analysis():
    try:
        ctx = _build_context()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to build refactoring context")
        raise HTTPException(500, str(e))

    try:
        analyses = {
            "dead_code":          _dead_code(ctx),
            "duplicate_removal":  _duplicate_removal(ctx),
            "class_splits":       _class_splits(ctx),
            "package_splits":     _package_splits(ctx),
            "dependency_breaks":  _dependency_breaks(ctx),
            "modularization":     _modularization(ctx),
            "microservices":      _microservices(ctx),
            "architecture_migration": _architecture_migration(ctx),
        }
        analyses["one_click_plan"] = _one_click_plan(ctx, analyses)
    except Exception as e:
        logger.exception("Analysis computation failed")
        raise HTTPException(500, f"Analysis failed: {e}")

    return {
        "repo_path": ctx["repo_path"],
        "total_source_files": len(ctx["src_files"]),
        "total_functions": len(ctx["func_entities"]),
        **analyses,
    }
