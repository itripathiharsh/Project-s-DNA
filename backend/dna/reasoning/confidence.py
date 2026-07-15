import json
from datetime import datetime, timezone
from dna.models import Evidence


def calculate_confidence(category: str, matching_evidence: list[Evidence], all_evidence: list[Evidence] = None) -> float:
    if not matching_evidence:
        return 0.5

    all_evidence = all_evidence or matching_evidence

    # Base confidence per category
    base_confidences = {
        "hotspot_risk": 0.75,
        "bus_factor": 0.70,
        "test_debt": 0.75,
        "dependency_risk": 0.80,
        "growth_trend": 0.60,
        "refactoring_needed": 0.70,
        "author_contribution_risk": 0.70,
        "module_structure_complexity": 0.70,
        "large_files": 0.70,
        "hotspot_active": 0.75,
        "commit_distribution_balance": 0.60,
        "refactoring_opportunities": 0.65,
        "temporal_coupling_coupling": 0.70,
        "expertise_risk": 0.60,
        "dependency_graph_risk": 0.70,
        "bus_factor_direct": 0.75,
        "commit_metadata_activity": 0.50,
    }

    confidence = base_confidences.get(category, 0.70)

    # 1. Recency adjustment (aging penalty if evidence is old)
    now = datetime.now(timezone.utc)
    max_age_days = 0
    for ev in matching_evidence:
        try:
            ev_time = datetime.fromisoformat(ev.timestamp.replace("Z", "+00:00"))
            age_days = (now - ev_time).days
            if age_days > max_age_days:
                max_age_days = age_days
        except Exception:
            pass
    if max_age_days > 30:
        confidence -= 0.10
    elif max_age_days > 7:
        confidence -= 0.05

    # 2. Category-specific evidence quantity/quality/consistency rules
    if category == "hotspot_risk":
        # Find change frequency
        cf_ev = next((e for e in matching_evidence if e.type == "change_frequency"), None)
        cx_ev = next((e for e in matching_evidence if e.type == "complexity_metrics"), None)
        
        # Increase confidence with more changes (quantity/sample size)
        if cf_ev:
            try:
                cf_val = json.loads(cf_ev.value) if isinstance(cf_ev.value, str) else cf_ev.value
                changes = cf_val.get("change_count", cf_val.get("changes", 0))
                if changes >= 20:
                    confidence += 0.10
                elif changes > 10:
                    confidence += 0.05
            except Exception:
                pass

        # Increase confidence with higher complexity
        if cx_ev:
            try:
                cx_val = json.loads(cx_ev.value) if isinstance(cx_ev.value, str) else cx_ev.value
                comp = cx_val.get("complexity", cx_val.get("max_complexity", 1))
                if comp > 10:
                    confidence += 0.10
                elif comp > 5:
                    confidence += 0.05
            except Exception:
                pass

        # CONFLICTING/MITIGATING EVIDENCE: High test coverage reduces hotspot risk confidence
        test_ev = next((e for e in all_evidence if e.type == "risk_metrics"), None)
        if test_ev:
            try:
                test_val = json.loads(test_ev.value) if isinstance(test_ev.value, str) else test_ev.value
                coverage = test_val.get("test_file_ratio", test_val.get("test_coverage_ratio", 0.0))
                if coverage > 0.8:
                    confidence -= 0.20  # High coverage mitigates risk significantly
                elif coverage > 0.5:
                    confidence -= 0.10
            except Exception:
                pass

    elif category == "bus_factor":
        ownership_ev = next((e for e in matching_evidence if e.type == "ownership_score"), None)
        if ownership_ev:
            try:
                own_val = json.loads(ownership_ev.value) if isinstance(ownership_ev.value, str) else ownership_ev.value
                bf = own_val.get("bus_factor", 99)
                if bf == 1:
                    confidence += 0.15
                elif bf == 2:
                    confidence += 0.05
                
                # Check for mitigating: if we have high author count overall, bus factor is more reliable
                # Check author_contribution count
                contribs = [e for e in all_evidence if e.type == "author_contribution"]
                if len(contribs) > 5:
                    confidence += 0.05
                elif len(contribs) <= 2:
                    confidence -= 0.10  # Low sample size reduces confidence in risk significance
            except Exception:
                pass

    elif category == "test_debt":
        risk_ev = next((e for e in matching_evidence if e.type == "risk_metrics"), None)
        if risk_ev:
            try:
                risk_val = json.loads(risk_ev.value) if isinstance(risk_ev.value, str) else risk_ev.value
                ratio = risk_val.get("test_file_ratio", risk_val.get("test_coverage_ratio", 1.0))
                if ratio < 0.05:
                    confidence += 0.10  # Extremely low coverage increases confidence of debt
                
                # Conflicting/Mitigating: if the codebase is tiny (few files), debt is less confident
                size_ev = next((e for e in all_evidence if e.type == "size_metrics"), None)
                if size_ev:
                    size_val = json.loads(size_ev.value) if isinstance(size_ev.value, str) else size_ev.value
                    files = size_val.get("files", 10)
                    if files < 5:
                        confidence -= 0.15
            except Exception:
                pass

    elif category == "dependency_risk":
        risk_ev = next((e for e in matching_evidence if e.type == "risk_metrics"), None)
        if risk_ev:
            try:
                risk_val = json.loads(risk_ev.value) if isinstance(risk_ev.value, str) else risk_ev.value
                cycles = risk_val.get("dependency_cycles", 0)
                if cycles > 5:
                    confidence += 0.10
                elif cycles == 0:
                    confidence -= 0.30  # No cycles means no risk
            except Exception:
                pass

    elif category == "large_files":
        size_ev = next((e for e in matching_evidence if e.type == "size_metrics"), None)
        if size_ev:
            try:
                size_val = json.loads(size_ev.value) if isinstance(size_ev.value, str) else size_ev.value
                funcs = size_val.get("functions", 0)
                if funcs > 100:
                    confidence += 0.15
                elif funcs > 50:
                    confidence += 0.05
            except Exception:
                pass

    # Clamp confidence to [0.1, 1.0]
    return max(0.1, min(1.0, round(confidence, 2)))
