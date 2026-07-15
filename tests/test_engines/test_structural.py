from dna.engines.structural import analyze_structure
from dna.models import EntityGraph, Entity, EntityRelation


def _make_graph() -> EntityGraph:
    g = EntityGraph()
    g.add_entity(Entity(uid="file:main.py", name="main.py", kind="file", file_path="main.py"))
    g.add_entity(Entity(uid="file:utils.py", name="utils.py", kind="file", file_path="utils.py"))
    g.add_entity(Entity(uid="function:main.py:foo", name="foo", kind="function", file_path="main.py", line=1))
    g.add_entity(Entity(uid="function:main.py:bar", name="bar", kind="function", file_path="main.py", line=5))
    g.add_entity(Entity(uid="class:utils.py:Helper", name="Helper", kind="class", file_path="utils.py", line=1))
    g.add_entity(Entity(uid="import:main.py:os", name="os", kind="import", file_path="main.py"))
    g.add_relation(EntityRelation(source_uid="file:main.py", target_uid="function:main.py:foo", kind="CONTAINS"))
    g.add_relation(EntityRelation(source_uid="file:main.py", target_uid="import:main.py:os", kind="CONTAINS"))
    g.add_relation(EntityRelation(source_uid="file:utils.py", target_uid="class:utils.py:Helper", kind="CONTAINS"))
    g.add_relation(EntityRelation(source_uid="file:main.py", target_uid="file:utils.py", kind="DEPENDS_ON"))
    return g


def test_analyze_empty():
    result = analyze_structure(EntityGraph())
    assert result["total_files"] == 0
    assert result["total_functions"] == 0


def test_analyze_counts():
    result = analyze_structure(_make_graph())
    assert result["total_files"] == 2
    assert result["total_functions"] == 2
    assert result["total_classes"] == 1
    assert result["total_imports"] == 1


def test_analyze_metrics():
    result = analyze_structure(_make_graph())
    assert result["funcs_per_file"] == 1.0
    assert result["classes_per_file"] == 0.5
    assert result["structural_coupling"] >= 1


def test_analyze_depth():
    result = analyze_structure(_make_graph())
    assert result["max_directory_depth"] >= 1
    assert result["avg_directory_depth"] > 0


def test_analyze_with_evidence_store():
    import tempfile
    import os
    from dna.evidence.store import EvidenceStore

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            result = analyze_structure(_make_graph(), store)
            assert store.count() >= 3
            assert len(store.get_by_source("structural_engine")) >= 3
