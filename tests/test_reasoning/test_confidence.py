import tempfile
import os
from dna.evidence.store import EvidenceStore
from dna.reasoning.engine import generate_insights


def test_confidence_hotspot_variation():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            # Seed base evidence
            store.add_evidence("change_frequency", {"change_count": 5}, file_path="src/a.py")
            store.add_evidence("complexity_metrics", {"max_complexity": 2}, file_path="src/a.py")
            
            insights = generate_insights(store)
            hotspots = [i for i in insights if i["category"] == "hotspot_risk"]
            assert len(hotspots) == 1
            base_confidence = hotspots[0]["confidence"]
            
            # Now let's test higher evidence quantity/value -> should increase confidence
            # Clear store/re-create or add another file with much higher activity
            store.add_evidence("change_frequency", {"change_count": 50}, file_path="src/high.py")
            store.add_evidence("complexity_metrics", {"max_complexity": 20}, file_path="src/high.py")
            
            insights = generate_insights(store)
            high_hotspots = [i for i in insights if i["category"] == "hotspot_risk" and i["file_path"] == "src/high.py"]
            assert len(high_hotspots) == 1
            high_confidence = high_hotspots[0]["confidence"]
            
            # Confidence should be higher for high activity
            assert high_confidence > base_confidence


def test_confidence_hotspot_mitigation():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            # Hotspot evidence
            store.add_evidence("change_frequency", {"change_count": 20}, file_path="src/a.py")
            store.add_evidence("complexity_metrics", {"max_complexity": 10}, file_path="src/a.py")
            
            insights = generate_insights(store)
            hotspots = [i for i in insights if i["category"] == "hotspot_risk"]
            assert len(hotspots) == 1
            normal_confidence = hotspots[0]["confidence"]
            
            # Add conflicting/mitigating evidence: High test coverage ratio!
            store.add_evidence("risk_metrics", {"test_file_ratio": 0.95})
            
            insights2 = generate_insights(store)
            hotspots2 = [i for i in insights2 if i["category"] == "hotspot_risk"]
            assert len(hotspots2) == 1
            mitigated_confidence = hotspots2[0]["confidence"]
            
            # Conflicting/mitigating test coverage should reduce confidence
            assert mitigated_confidence < normal_confidence
