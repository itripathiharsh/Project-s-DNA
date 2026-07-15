import tempfile, os
from dna.storage.store import SCStore
from dna.models import EntityGraph, Entity


def test_metadata_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "sc.db")
        with SCStore(path) as store:
            store.set_metadata("key1", "value1")
            store.set_metadata("key2", "value2")
        with SCStore(path) as store:
            assert store.get_metadata("key1") == "value1"
            assert store.get_metadata("key2") == "value2"
            assert store.get_metadata("nonexistent") is None


def test_save_load_empty_graph():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "sc.db")
        g = EntityGraph()
        with SCStore(path) as store:
            store.save_entity_graph(g)
        with SCStore(path) as store:
            loaded = store.load_entity_graph()
            assert len(loaded.entities) == 0
            assert len(loaded.relations) == 0


def test_save_load_with_entities():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "sc.db")
        g = EntityGraph()
        g.add_entity(Entity(uid="file:a.py", name="a.py", kind="file", file_path="a.py"))
        with SCStore(path) as store:
            store.save_entity_graph(g)
        with SCStore(path) as store:
            loaded = store.load_entity_graph()
            assert len(loaded.entities) == 1
            assert loaded.entities[0].uid == "file:a.py"


def test_metadata_overwrite():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "sc.db")
        with SCStore(path) as store:
            store.set_metadata("k", "v1")
            store.set_metadata("k", "v2")
        with SCStore(path) as store:
            assert store.get_metadata("k") == "v2"


def test_context_manager_commit():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "sc.db")
        with SCStore(path) as store:
            store.set_metadata("a", "b")
        with SCStore(path) as store:
            assert store.get_metadata("a") == "b"


def test_not_opened_raises():
    store = SCStore(":memory:")
    import pytest
    with pytest.raises(RuntimeError, match="not opened"):
        store.save_entity_graph(EntityGraph())
    with pytest.raises(RuntimeError, match="not opened"):
        store.load_entity_graph()
