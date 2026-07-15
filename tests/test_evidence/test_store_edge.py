import tempfile, os
from dna.evidence.store import EvidenceStore


def test_get_by_source():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            store.add_evidence("type_a", {"k": "v1"}, source="src1")
            store.add_evidence("type_b", {"k": "v2"}, source="src2")
            assert len(store.get_by_source("src1")) == 1
            assert len(store.get_by_source("src2")) == 1
            assert len(store.get_by_source("nonexistent")) == 0


def test_get_by_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            store.add_evidence("type_a", {"k": "v"}, file_path="src/main.py")
            store.add_evidence("type_b", {"k": "v"}, file_path="src/utils.py")
            assert len(store.get_by_file("src/main.py")) == 1
            assert len(store.get_by_file("nonexistent.py")) == 0


def test_get_by_type():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            store.add_evidence("type_a", {"k": "v"}, source="s")
            store.add_evidence("type_b", {"k": "v"}, source="s")
            assert len(store.get_by_type("type_a")) == 1
            assert len(store.get_by_type("type_b")) == 1
            assert len(store.get_by_type("nonexistent")) == 0


def test_clear():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            store.add_evidence("a", {"k": "v"}, source="s")
            store.add_evidence("b", {"k": "v"}, source="s")
            assert store.count() == 2
            store.clear()
            assert store.count() == 0


def test_add_evidence_id_and_timestamp():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            store.add_evidence("test", {"x": 1})
            all_ev = store.get_all()
            assert len(all_ev) == 1
            assert all_ev[0].id
            assert all_ev[0].timestamp


def test_not_opened_raises():
    store = EvidenceStore(":memory:")
    import pytest
    with pytest.raises(RuntimeError, match="not opened"):
        store.get_all()
    with pytest.raises(RuntimeError, match="not opened"):
        store.add_evidence("a", {})
