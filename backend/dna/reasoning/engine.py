import json
import logging
from dna.evidence.store import EvidenceStore

logger = logging.getLogger("dna.reasoning")


INSIGHT_RULES = [
    {
        "category": "hotspot_risk",
        "label": "High-Risk Hotspot Detected",
        "description": "File with both high change frequency and high complexity",
        "requires_evidence": ["change_frequency", "complexity_metrics"],
        "severity": "high",
    },
    {
        "category": "bus_factor",
        "label": "Bus Factor Risk",
        "description": "Project relies on a small number of contributors",
        "requires_evidence": ["ownership_score"],
        "severity": "high",
    },
    {
        "category": "test_debt",
        "label": "Test Coverage Gap",
        "description": "Low test-to-source file ratio indicates testing debt",
        "requires_evidence": ["risk_metrics"],
        "severity": "medium",
    },
    {
        "category": "dependency_risk",
        "label": "Dependency Cycle Risk",
        "description": "Circular dependencies detected in the codebase",
        "requires_evidence": ["risk_metrics"],
        "severity": "high",
    },
    {
        "category": "growth_trend",
        "label": "Codebase Growth Trend",
        "description": "Codebase size change over time",
        "requires_evidence": ["growth_trend"],
        "severity": "info",
    },
    {
        "category": "refactoring_needed",
        "label": "Refactoring Opportunity",
        "description": "Files with high complexity may benefit from refactoring",
        "requires_evidence": ["complexity_metrics"],
        "severity": "medium",
    },
    {
        "category": "author_contribution_risk",
        "label": "High Contributor Concentration",
        "description": "A single author has a very high share of contributions",
        "requires_evidence": ["author_contribution"],
        "severity": "medium",
    },
    {
        "category": "module_structure_complexity",
        "label": "Complex Module Structure",
        "description": "Deep directory structure detected",
        "requires_evidence": ["module_structure"],
        "severity": "medium",
    },
    {
        "category": "large_files",
        "label": "Large File Size Warning",
        "description": "File has a large number of functions, indicating high complexity",
        "requires_evidence": ["size_metrics"],
        "severity": "medium",
    },
    {
        "category": "hotspot_active",
        "label": "Highly Active Hotspot",
        "description": "The file has high change frequency in the hotspot list",
        "requires_evidence": ["hotspot_list"],
        "severity": "medium",
    },
    {
        "category": "commit_distribution_balance",
        "label": "Unbalanced Commit Distribution",
        "description": "Repository commits are distributed unevenly across categories",
        "requires_evidence": ["commit_distribution"],
        "severity": "info",
    },
    {
        "category": "refactoring_opportunities",
        "label": "High Refactoring Activity",
        "description": "File shows frequent historical refactoring events",
        "requires_evidence": ["refactoring_events"],
        "severity": "low",
    },
    {
        "category": "temporal_coupling_coupling",
        "label": "High Temporal Coupling",
        "description": "Strong historical coupling found between modules",
        "requires_evidence": ["temporal_coupling"],
        "severity": "medium",
    },
    {
        "category": "expertise_risk",
        "label": "Low Team Expertise",
        "description": "Files modified by authors with low area expertise",
        "requires_evidence": ["expertise_score"],
        "severity": "low",
    },
    {
        "category": "dependency_graph_risk",
        "label": "Complex Dependency Graph Structure",
        "description": "The codebase has a high density of dependencies",
        "requires_evidence": ["dependency_graph"],
        "severity": "medium",
    },
    {
        "category": "bus_factor_direct",
        "label": "High Bus Factor Risk (Direct)",
        "description": "Direct bus factor evidence suggests low contributor resilience",
        "requires_evidence": ["bus_factor"],
        "severity": "high",
    },
    {
        "category": "commit_metadata_activity",
        "label": "Repository Commit Activity Status",
        "description": "Analysis of commit metadata shows repo activity levels",
        "requires_evidence": ["commit_metadata"],
        "severity": "info",
    },
]


def generate_insights(evidence_store: EvidenceStore) -> list[dict]:
    logger.info("Generating insights from evidence store")
    all_evidence = evidence_store.get_all()
    evidence_types = {e.type for e in all_evidence}

    insights = []

    for rule in INSIGHT_RULES:
        has_all = all(req in evidence_types for req in rule["requires_evidence"])
        if not has_all:
            continue

        matching = [e for e in all_evidence if e.type in rule["requires_evidence"]]

        if rule["category"] == "hotspot_risk":
            _add_hotspot_insights(insights, matching, rule)
        elif rule["category"] == "bus_factor":
            _add_bus_factor_insight(insights, matching, rule)
        elif rule["category"] == "test_debt":
            _add_test_debt_insight(insights, matching, rule)
        elif rule["category"] == "dependency_risk":
            _add_dependency_risk_insight(insights, matching, rule)
        elif rule["category"] == "growth_trend":
            _add_growth_insight(insights, matching, rule)
        elif rule["category"] == "refactoring_needed":
            _add_refactoring_insight(insights, matching, rule)
        elif rule["category"] == "author_contribution_risk":
            _add_author_contribution_insight(insights, matching, rule)
        elif rule["category"] == "module_structure_complexity":
            _add_module_structure_insight(insights, matching, rule)
        elif rule["category"] == "large_files":
            _add_large_files_insight(insights, matching, rule)
        elif rule["category"] == "hotspot_active":
            _add_hotspot_active_insight(insights, matching, rule)
        elif rule["category"] == "commit_distribution_balance":
            _add_commit_distribution_insight(insights, matching, rule)
        elif rule["category"] == "refactoring_opportunities":
            _add_refactoring_opportunity_events_insight(insights, matching, rule)
        elif rule["category"] == "temporal_coupling_coupling":
            _add_temporal_coupling_coupling_insight(insights, matching, rule)
        elif rule["category"] == "expertise_risk":
            _add_expertise_risk_insight(insights, matching, rule)
        elif rule["category"] == "dependency_graph_risk":
            _add_dependency_graph_risk_insight(insights, matching, rule)
        elif rule["category"] == "bus_factor_direct":
            _add_bus_factor_direct_insight(insights, matching, rule)
        elif rule["category"] == "commit_metadata_activity":
            _add_commit_metadata_insight(insights, matching, rule)

    from dna.reasoning.confidence import calculate_confidence
    for insight in insights:
        ev_id = insight.get("evidence_id")
        matching = [e for e in all_evidence if e.id == ev_id] if ev_id else []
        if not matching:
            rule = next((r for r in INSIGHT_RULES if r["category"] == insight["category"]), None)
            if rule:
                matching = [e for e in all_evidence if e.type in rule["requires_evidence"]]
        
        insight["confidence"] = calculate_confidence(insight["category"], matching, all_evidence)

    logger.info("Generated %d insights from %d evidence items", len(insights), len(all_evidence))
    insights.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2, "info": 3}.get(x["severity"], 4))
    return insights


def _add_hotspot_insights(insights: list, evidence: list, rule: dict):
    hotspots = [e for e in evidence if e.type == "change_frequency"]
    for h in hotspots[:5]:
        insights.append({
            "category": rule["category"],
            "label": rule["label"],
            "severity": rule["severity"],
            "file_path": h.file_path,
            "evidence_id": h.id,
            "confidence": 0.85,
            "detail": f"File {h.file_path} has high change frequency",
        })


def _add_bus_factor_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        bf = d.get("bus_factor", 99)
        if bf <= 2:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.9 if bf == 1 else 0.8,
                "detail": f"Bus factor is {bf} — project knowledge is concentrated",
            })


def _add_test_debt_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        ratio = d.get("test_file_ratio", d.get("test_coverage_ratio", 1))
        if ratio < 0.15:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.75,
                "detail": f"Test file ratio is {ratio}",
            })


def _add_dependency_risk_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        cycles = d.get("dependency_cycles", 0)
        if cycles > 0:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.9,
                "detail": f"{cycles} dependency cycles detected",
            })


def _add_growth_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        insights.append({
            "category": rule["category"],
            "label": rule["label"],
            "severity": rule["severity"],
            "file_path": e.file_path,
            "evidence_id": e.id,
            "confidence": 0.6,
            "detail": "Codebase growth trend available",
        })


def _add_refactoring_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        avg_depth = d.get("avg_depth", 0)
        if avg_depth > 4:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.7,
                "detail": f"Average module depth {avg_depth} suggests deep nesting",
            })


def _add_author_contribution_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        pct = d.get("percentage", 0)
        if pct > 75:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.8,
                "detail": f"Author {d.get('author')} contributed {pct}% of commits",
            })


def _add_module_structure_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        max_depth = d.get("max_depth", 0)
        if max_depth > 5:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.7,
                "detail": f"Max directory depth is {max_depth}",
            })


def _add_large_files_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        funcs = d.get("functions", 0)
        if funcs > 50:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.75,
                "detail": f"File contains {funcs} functions",
            })


def _add_hotspot_active_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        hotspots = d.get("hotspots", [])
        for h in hotspots[:3]:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": h.get("file"),
                "evidence_id": e.id,
                "confidence": 0.8,
                "detail": f"File is an active hotspot with {h.get('change_count')} changes",
            })


def _add_commit_distribution_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        total = d.get("total_commits", 0)
        insights.append({
            "category": rule["category"],
            "label": rule["label"],
            "severity": rule["severity"],
            "file_path": e.file_path,
            "evidence_id": e.id,
            "confidence": 0.6,
            "detail": f"Repository has {total} commits parsed in total",
        })


def _add_refactoring_opportunity_events_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        count = d.get("refactoring_count", 0)
        if count > 5:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.65,
                "detail": f"File was refactored {count} times",
            })


def _add_temporal_coupling_coupling_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        couplings = d.get("coupled_files", [])
        if couplings:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.7,
                "detail": f"Temporal coupling with {len(couplings)} other files",
            })


def _add_expertise_risk_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        score = d.get("expertise_score", 1.0)
        if score < 0.3:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.6,
                "detail": f"Expertise score is low: {score}",
            })


def _add_dependency_graph_risk_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        coupling = d.get("coupling_coefficient", 0.0)
        if coupling > 0.5:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.7,
                "detail": f"Dependency graph coupling coefficient is {coupling}",
            })


def _add_bus_factor_direct_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        d = json.loads(e.value) if isinstance(e.value, str) else e.value
        val = d.get("bus_factor", 1)
        if val <= 2:
            insights.append({
                "category": rule["category"],
                "label": rule["label"],
                "severity": rule["severity"],
                "file_path": e.file_path,
                "evidence_id": e.id,
                "confidence": 0.85,
                "detail": f"Direct bus factor is {val}",
            })


def _add_commit_metadata_insight(insights: list, evidence: list, rule: dict):
    for e in evidence:
        insights.append({
            "category": rule["category"],
            "label": rule["label"],
            "severity": rule["severity"],
            "file_path": e.file_path,
            "evidence_id": e.id,
            "confidence": 0.5,
            "detail": "Commit metadata analyzed",
        })
