from dna.reasoning.engine import generate_insights, INSIGHT_RULES


def _seed_store(store):
    store.add_evidence("change_frequency", {"changes": 20}, source="change", file_path="src/hot.py")
    store.add_evidence("complexity_metrics", {"func_count": 12, "avg_depth": 5}, source="structural", file_path="src/hot.py")
    store.add_evidence("ownership_score", {"bus_factor": 1, "bus_factor_risk": "high"}, source="knowledge")
    store.add_evidence("risk_metrics", {"test_file_ratio": 0.05, "dependency_cycles": 3}, source="risk")
    store.add_evidence("growth_trend", {"file_count": 100, "change": 15}, source="evolution")


def test_empty_store():
    import tempfile, os
    from dna.evidence.store import EvidenceStore
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            insights = generate_insights(store)
            assert insights == []


def test_insight_generation():
    import tempfile, os
    from dna.evidence.store import EvidenceStore
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            _seed_store(store)
            insights = generate_insights(store)
            assert len(insights) >= 1


def test_hotspot_insight():
    import tempfile, os
    from dna.evidence.store import EvidenceStore
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            _seed_store(store)
            insights = generate_insights(store)
            hotspots = [i for i in insights if i["category"] == "hotspot_risk"]
            assert len(hotspots) >= 1
            assert hotspots[0]["confidence"] == 0.85


def test_bus_factor_insight():
    import tempfile, os
    from dna.evidence.store import EvidenceStore
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            _seed_store(store)
            insights = generate_insights(store)
            bf = [i for i in insights if i["category"] == "bus_factor"]
            assert len(bf) >= 1
            assert bf[0]["severity"] == "high"


def test_severity_sorting():
    import tempfile, os
    from dna.evidence.store import EvidenceStore
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            _seed_store(store)
            insights = generate_insights(store)
            severities = [i["severity"] for i in insights]
            assert severities == sorted(severities, key=lambda x: {"high": 0, "medium": 1, "low": 2, "info": 3}[x])


def test_rules_defined():
    assert len(INSIGHT_RULES) >= 12
    cats = {r["category"] for r in INSIGHT_RULES}
    assert "hotspot_risk" in cats
    assert "bus_factor" in cats
    assert "test_debt" in cats
    assert "author_contribution_risk" in cats
    assert "module_structure_complexity" in cats
    assert "large_files" in cats


def test_all_new_rules():
    import tempfile, os
    from dna.evidence.store import EvidenceStore
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            store.add_evidence("author_contribution", {"author": "Alice", "percentage": 90, "commits": 10})
            store.add_evidence("module_structure", {"max_depth": 6})
            store.add_evidence("size_metrics", {"functions": 60})
            store.add_evidence("hotspot_list", {"hotspots": [{"file": "main.py", "change_count": 100}]})
            store.add_evidence("commit_distribution", {"total_commits": 150})
            store.add_evidence("refactoring_events", {"refactoring_count": 8}, file_path="main.py")
            store.add_evidence("temporal_coupling", {"coupled_files": ["a.py", "b.py"]}, file_path="main.py")
            store.add_evidence("expertise_score", {"expertise_score": 0.1}, file_path="main.py")
            store.add_evidence("dependency_graph", {"coupling_coefficient": 0.8}, file_path="main.py")
            store.add_evidence("bus_factor", {"bus_factor": 1})
            store.add_evidence("commit_metadata", {"commits": []})

            insights = generate_insights(store)
            categories = {i["category"] for i in insights}
            
            assert "author_contribution_risk" in categories
            assert "module_structure_complexity" in categories
            assert "large_files" in categories
            assert "hotspot_active" in categories
            assert "commit_distribution_balance" in categories
            assert "refactoring_opportunities" in categories
            assert "temporal_coupling_coupling" in categories
            assert "expertise_risk" in categories
            assert "dependency_graph_risk" in categories
            assert "bus_factor_direct" in categories
            assert "commit_metadata_activity" in categories
