import os
import tempfile
from dna.evidence.store import EvidenceStore
from dna.reasoning.engine import generate_insights

def test_reasoning_insights_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        ev_db = os.path.join(tmpdir, "ev.db")
        
        with EvidenceStore(ev_db) as store:
            # Seed evidence that represents high complexity + high change frequency
            # (which should trigger a hotspot_risk insight)
            store.add_evidence(
                type="change_frequency",
                data={"changes": 25},
                source="evolution_engine",
                file_path="src/utils.py"
            )
            store.add_evidence(
                type="complexity_metrics",
                data={"avg_complexity": 12, "func_count": 5},
                source="structural_engine",
                file_path="src/utils.py"
            )
            
            # Seed evidence for bus factor risk
            store.add_evidence(
                type="bus_factor",
                data={"bus_factor": 1, "top_contributors_count": 1},
                source="knowledge_engine"
            )
            
            # Seed evidence for high cycle risk
            store.add_evidence(
                type="risk_metrics",
                data={"dependency_cycles": 4, "test_file_ratio": 0.1},
                source="risk_engine"
            )
            
            # Generate insights
            insights = generate_insights(store)
            assert len(insights) >= 3
            
            categories = {ins["category"] for ins in insights}
            assert "hotspot_risk" in categories
            assert "bus_factor_direct" in categories
            assert "dependency_risk" in categories
            
            # Verify details and confidence format
            for ins in insights:
                assert "category" in ins
                assert "label" in ins
                assert "detail" in ins
                assert "severity" in ins
                assert 0.0 <= ins["confidence"] <= 1.0
