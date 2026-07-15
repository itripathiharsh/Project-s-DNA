from dna.models import EVIDENCE_TYPES
from dna.reasoning.engine import INSIGHT_RULES

# Mapping of engines to the evidence types they produce (as checked from their code)
ENGINE_PRODUCED_EVIDENCE = {
    "evolution_engine": {
        "commit_distribution", "growth_trend", "hotspot_list", "change_frequency",
        "temporal_coupling", "refactoring_events", "commit_metadata"
    },
    "knowledge_engine": {
        "author_contribution", "ownership_score", "expertise_score", "bus_factor"
    },
    "risk_engine": {"risk_metrics"},
    "structural_engine": {
        "module_structure", "size_metrics", "complexity_metrics", "dependency_graph"
    },
}


def test_insight_rules_evidence_types_in_contract():
    """Verify that every required evidence type in the insight rules is defined in the EVIDENCE_TYPES contract."""
    for rule in INSIGHT_RULES:
        for req in rule["requires_evidence"]:
            assert req in EVIDENCE_TYPES, f"Rule '{rule['category']}' requires evidence '{req}' which is not in EVIDENCE_TYPES"


def test_insight_rules_produced_by_at_least_one_engine():
    """Verify that every required evidence type in the insight rules is produced by at least one engine."""
    all_produced = set()
    for produced in ENGINE_PRODUCED_EVIDENCE.values():
        all_produced.update(produced)

    for rule in INSIGHT_RULES:
        for req in rule["requires_evidence"]:
            assert req in all_produced, f"Rule '{rule['category']}' requires evidence '{req}' which no engine produces"
