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

    # Calculate confidence and fill in canonical schemas
    from dna.reasoning.confidence import calculate_confidence
    
    formatted_insights = []
    for idx, insight in enumerate(insights):
        category = insight.get("category")
        ev_id = insight.get("evidence_id")
        matching = [e for e in all_evidence if e.id == ev_id] if ev_id else []
        if not matching:
            rule = next((r for r in INSIGHT_RULES if r["category"] == category), None)
            if rule:
                matching = [e for e in all_evidence if e.type in rule["requires_evidence"]]
        
        confidence = calculate_confidence(category, matching, all_evidence)
        insight["confidence"] = confidence

        # Apply strict schema mapping
        title = insight.get("label", "Codebase Insight")
        summary = insight.get("detail", "")
        file_path = insight.get("file_path", "")
        severity = insight.get("severity", "info")
        
        # Build extra contract fields based on category
        recommendations = []
        impact = ""
        risk_score = 0.0
        visualization_hints = {"type": "default"}
        actions = []
        
        if category == "hotspot_risk":
            recommendations = [
                "Break down the file into smaller modules or classes.",
                "Introduce comprehensive unit tests to cover the high change surface.",
                "Conduct a peer review specifically targeting structural complexity."
            ]
            impact = "High change rate combined with high complexity increases regression rates and developer fatigue."
            risk_score = 8.5 * confidence
            visualization_hints = {"type": "heatmap", "axis": "complexity_vs_churn", "highlight": file_path}
            actions = [
                {"name": "Create Review Roster", "path": f"/reviews/new?file={file_path}"},
                {"name": "Define Refactor Steps", "path": f"/refactoring/new?file={file_path}"}
            ]
        elif category == "bus_factor" or category == "bus_factor_direct":
            recommendations = [
                "Cross-train team members on this area of the codebase.",
                "Establish pair-programming routines.",
                "Improve documentation and structural annotations."
            ]
            impact = "Loss of primary contributors will lead to severe delays in debugging or extending features."
            risk_score = 9.0 * confidence
            visualization_hints = {"type": "pie_chart", "highlight": "knowledge_distribution"}
            actions = [
                {"name": "Delegate Ownership", "path": "/organization"}
            ]
        elif category == "test_debt":
            recommendations = [
                "Configure a pre-commit hook enforcing minimum test ratios.",
                "Schedule a dedicated test writing sprint for uncovered files."
            ]
            impact = "Low test coverage causes hidden regressions to slip into production environments."
            risk_score = 6.0 * confidence
            visualization_hints = {"type": "bar_chart", "highlight": "coverage_ratio"}
            actions = [
                {"name": "Initialize Test Pipeline", "path": "/refactoring"}
            ]
        elif category == "dependency_risk":
            recommendations = [
                "Extract common abstractions to a shared models or utils layer.",
                "Use Dependency Injection to decouple cyclic classes."
            ]
            impact = "Circular dependencies prevent modular testing, complicate compilation, and hide side effects."
            risk_score = 7.8 * confidence
            visualization_hints = {"type": "dependency_graph", "highlight": file_path}
            actions = [
                {"name": "Analyze Cycle Graph", "path": "/graph"}
            ]
        else:
            recommendations = ["Monitor complexity and evolution stats over the next release cycle."]
            impact = "Minor structural or organizational layout issues may gradually degrade maintainability."
            risk_score = 3.5 * confidence
            visualization_hints = {"type": "metric_card"}
            actions = [{"name": "View File", "path": f"/explorer?file={file_path}"}]

        strict_insight = {
            "id": f"insight-{idx}",
            "title": title,
            "label": title,  # Compatibility
            "summary": summary,
            "detail": summary,  # Compatibility
            "severity": severity,
            "confidence": confidence,
            "category": category,
            "file_path": file_path,
            "supporting_evidence": [ev_id] if ev_id else [],
            "evidence_id": ev_id,  # Compatibility
            "affected_entities": [file_path] if file_path else [],
            "recommendations": recommendations,
            "impact": impact,
            "risk_score": round(risk_score, 2),
            "visualization_hints": visualization_hints,
            "actions": actions,
            "related_insights": []
        }
        formatted_insights.append(strict_insight)

    logger.info("Generated %d insights", len(formatted_insights))
    formatted_insights.sort(key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(x["severity"], 5))
    return formatted_insights


def _add_hotspot_insights(insights: list, evidence: list, rule: dict):
    hotspots = [e for e in evidence if e.type == "change_frequency"]
    for h in hotspots[:5]:
        insights.append({
            "category": rule["category"],
            "label": rule["label"],
            "severity": rule["severity"],
            "file_path": h.file_path,
            "evidence_id": h.id,
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
            "detail": "Commit metadata analyzed",
        })
