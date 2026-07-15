import os
import tempfile
from dna.storage.store import SCStore
from dna.models import EntityGraph, Entity, EntityRelation


def _make_graph() -> EntityGraph:
    g = EntityGraph()
    g.add_entity(Entity(uid="file:main.py", name="main.py", kind="file", file_path="main.py"))
    g.add_entity(Entity(uid="function:main.py:foo", name="foo", kind="function", file_path="main.py", line=1))
    g.add_relation(EntityRelation(source_uid="file:main.py", target_uid="function:main.py:foo", kind="CONTAINS"))
    return g


def test_create_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.db")
        store = SCStore(path)
        store.open()
        assert store.get_stats()["entities"] == 0
        store.close()


def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.db")
        with SCStore(path) as store:
            store.save_entity_graph(_make_graph())
            stats = store.get_stats()
            assert stats["entities"] == 2
            assert stats["relations"] == 1

        with SCStore(path) as store:
            graph = store.load_entity_graph()
            assert len(graph.entities) == 2
            assert len(graph.relations) == 1


def test_metadata():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.db")
        with SCStore(path) as store:
            store.set_metadata("repo_name", "my-project")
            store.set_metadata("language", "Python")
            assert store.get_metadata("repo_name") == "my-project"
            assert store.get_metadata("language") == "Python"
            assert store.get_metadata("nonexistent") is None


def test_overwrite_graph():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.db")
        with SCStore(path) as store:
            store.save_entity_graph(_make_graph())
            assert store.get_stats()["entities"] == 2

            store.save_entity_graph(EntityGraph())
            assert store.get_stats()["entities"] == 0


def test_stats():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.db")
        with SCStore(path) as store:
            store.set_metadata("k1", "v1")
            store.save_entity_graph(_make_graph())
            stats = store.get_stats()
            assert stats["entities"] == 2
            assert stats["relations"] == 1
            assert stats["metadata_keys"] >= 1


def test_context_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.db")
        with SCStore(path) as store:
            store.save_entity_graph(_make_graph())
        # Should be closed now
        import sqlite3
        # Reopen to verify persistence
        conn = sqlite3.connect(path)
        count = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        assert count == 2
        conn.close()


def test_sc_store_migration():
    import sqlite3
    from dna.storage.store import _SCHEMA_SQL_V1
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "legacy.db")
        conn = sqlite3.connect(path)
        conn.executescript(_SCHEMA_SQL_V1)
        cursor = conn.execute("PRAGMA table_info(entities)")
        cols = [c[1] for c in cursor.fetchall()]
        assert "hash" not in cols
        conn.close()
        
        with SCStore(path) as store:
            pass
            
        conn = sqlite3.connect(path)
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        assert version == 2
        cursor = conn.execute("PRAGMA table_info(entities)")
        cols = [c[1] for c in cursor.fetchall()]
        assert "hash" in cols
        conn.close()


def test_incremental_save():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test_inc.db")
        with SCStore(path) as store:
            g1 = EntityGraph()
            g1.add_entity(Entity(uid="file:A", name="A", kind="file", file_path="A"))
            g1.add_entity(Entity(uid="func:A:f1", name="f1", kind="function", file_path="A"))
            g1.add_entity(Entity(uid="file:B", name="B", kind="file", file_path="B"))
            g1.add_entity(Entity(uid="func:B:g1", name="g1", kind="function", file_path="B"))
            g1.add_relation(EntityRelation(source_uid="file:A", target_uid="func:A:f1", kind="CONTAINS"))
            g1.add_relation(EntityRelation(source_uid="file:B", target_uid="func:B:g1", kind="CONTAINS"))
            
            store.save_entity_graph(g1)
            assert store.get_stats()["entities"] == 4
            assert store.get_stats()["relations"] == 2
            
            g2 = EntityGraph()
            g2.add_entity(Entity(uid="file:A", name="A", kind="file", file_path="A"))
            g2.add_entity(Entity(uid="func:A:f2", name="f2", kind="function", file_path="A"))
            g2.add_relation(EntityRelation(source_uid="file:A", target_uid="func:A:f2", kind="CONTAINS"))
            
            store.save_entity_graph(g2)
            
            loaded = store.load_entity_graph()
            uids = {e.uid for e in loaded.entities}
            assert "file:A" in uids
            assert "func:A:f2" in uids
            assert "func:A:f1" not in uids
            assert "file:B" in uids
            assert "func:B:g1" in uids
            assert len(loaded.entities) == 4
            
            rels = {(r.source_uid, r.target_uid) for r in loaded.relations}
            assert ("file:A", "func:A:f2") in rels
            assert ("file:A", "func:A:f1") not in rels
            assert ("file:B", "func:B:g1") in rels
            assert len(loaded.relations) == 2

