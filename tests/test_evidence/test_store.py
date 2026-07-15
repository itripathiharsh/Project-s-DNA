import os
import tempfile
from dna.evidence.store import EvidenceStore


def test_empty_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            assert store.count() == 0
            assert store.get_all() == []


def test_add_evidence():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            ev = store.add_evidence("commit_metadata", {"hash": "abc123", "author": "alice"},
                                    source="git_miner", file_path="src/main.py")
            assert ev.type == "commit_metadata"
            assert ev.source == "git_miner"
            assert ev.file_path == "src/main.py"
            assert ev.id is not None
            assert store.count() == 1


def test_get_by_type():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            store.add_evidence("complexity_metrics", {"complexity": 5}, file_path="a.py")
            store.add_evidence("complexity_metrics", {"complexity": 3}, file_path="b.py")
            store.add_evidence("size_metrics", {"loc": 100}, file_path="a.py")
            results = store.get_by_type("complexity_metrics")
            assert len(results) == 2
            results = store.get_by_type("size_metrics")
            assert len(results) == 1


def test_get_by_source():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            store.add_evidence("change_frequency", {"changes": 5}, source="evolution_engine")
            store.add_evidence("author_contribution", {"author": "alice"}, source="knowledge_engine")
            results = store.get_by_source("evolution_engine")
            assert len(results) == 1
            assert results[0].type == "change_frequency"


def test_get_by_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            store.add_evidence("size_metrics", {"loc": 50}, file_path="src/main.py")
            store.add_evidence("complexity_metrics", {"complexity": 10}, file_path="src/main.py")
            store.add_evidence("size_metrics", {"loc": 30}, file_path="src/utils.py")
            results = store.get_by_file("src/main.py")
            assert len(results) == 2


def test_clear():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            store.add_evidence("test_type", {"x": 1})
            assert store.count() == 1
            store.clear()
            assert store.count() == 0


def test_multiple_values():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            for i in range(5):
                store.add_evidence("test", {"i": i})
            assert store.count() == 5
            assert len(store.get_by_type("test")) == 5


def test_evidence_store_migration():
    import sqlite3
    from dna.evidence.store import _SCHEMA_SQL_V1
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "legacy.db")
        conn = sqlite3.connect(path)
        conn.executescript(_SCHEMA_SQL_V1)
        cursor = conn.execute("PRAGMA table_info(evidence)")
        cols = [c[1] for c in cursor.fetchall()]
        assert "confidence" not in cols
        conn.close()
        
        with EvidenceStore(path) as store:
            pass
            
        conn = sqlite3.connect(path)
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        assert version == 2
        cursor = conn.execute("PRAGMA table_info(evidence)")
        cols = [c[1] for c in cursor.fetchall()]
        assert "confidence" in cols
        conn.close()
