from dna.engines.risk import analyze_risks
from dna.models import EntityGraph, Entity, EntityRelation, DependencyGraph, DependencyEdge


def _make_graph() -> EntityGraph:
    g = EntityGraph()
    g.add_entity(Entity(uid="file:main.py", name="main.py", kind="file", file_path="main.py"))
    g.add_entity(Entity(uid="file:utils.py", name="utils.py", kind="file", file_path="utils.py"))
    g.add_entity(Entity(uid="file:tests/test_main.py", name="test_main.py", kind="file",
                        file_path="tests/test_main.py"))
    g.add_entity(Entity(uid="function:main.py:foo", name="foo", kind="function", file_path="main.py"))
    g.add_entity(Entity(uid="function:main.py:bar", name="bar", kind="function", file_path="main.py"))
    g.add_entity(Entity(uid="function:utils.py:helper", name="helper", kind="function", file_path="utils.py"))
    g.add_entity(Entity(uid="import:main.py:os", name="os", kind="import", file_path="main.py"))
    g.add_relation(EntityRelation(source_uid="file:main.py", target_uid="file:utils.py", kind="DEPENDS_ON"))
    return g


def test_empty():
    result = analyze_risks(EntityGraph())
    assert result["total_files"] == 0
    assert result["test_file_ratio"] == 0


def test_file_counts():
    result = analyze_risks(_make_graph())
    assert result["total_files"] == 3
    assert result["source_files"] >= 2
    assert result["test_files"] == 1


def test_test_coverage():
    result = analyze_risks(_make_graph())
    assert result["test_file_ratio"] > 0


def test_risk_indicators():
    dg = DependencyGraph()
    dg.add_edge(DependencyEdge(source="a.py", target="b.py", kind="import"))
    dg.add_edge(DependencyEdge(source="b.py", target="a.py", kind="import"))
    result = analyze_risks(_make_graph(), dg)
    assert len(result["risk_indicators"]) >= 1


def test_with_evidence_store():
    import tempfile
    import os
    from dna.evidence.store import EvidenceStore

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            result = analyze_risks(_make_graph(), evidence_store=store)
            assert store.get_by_type("risk_metrics") != []
