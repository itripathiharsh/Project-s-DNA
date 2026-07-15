import os
import tempfile
from dna.indexer.hasher import compute_file_hash, compute_file_hashes, detect_changes
from dna.models import FileInfo


def test_compute_file_hash():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "f.txt")
        with open(path, "w") as f:
            f.write("hello")
        h = compute_file_hash(path)
        assert isinstance(h, str)
        assert len(h) == 32


def test_compute_file_hash_deterministic():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "f.txt")
        with open(path, "w") as f:
            f.write("hello")
        assert compute_file_hash(path) == compute_file_hash(path)


def test_compute_file_hash_different_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        p1 = os.path.join(tmpdir, "a.txt")
        p2 = os.path.join(tmpdir, "b.txt")
        with open(p1, "w") as f: f.write("hello")
        with open(p2, "w") as f: f.write("world")
        assert compute_file_hash(p1) != compute_file_hash(p2)


def test_compute_file_hash_nonexistent():
    assert compute_file_hash("C:\\nonexistent_xyz_file") == ""


def test_compute_file_hashes():
    with tempfile.TemporaryDirectory() as tmpdir:
        p1 = os.path.join(tmpdir, "a.py")
        p2 = os.path.join(tmpdir, "b.py")
        with open(p1, "w") as f: f.write("x")
        with open(p2, "w") as f: f.write("y")
        files = [
            FileInfo(path=p1, relative_path="a.py", filename="a.py", extension=".py", language="Python", size_bytes=1, is_directory=False, is_source=True),
            FileInfo(path=p2, relative_path="b.py", filename="b.py", extension=".py", language="Python", size_bytes=1, is_directory=False, is_source=True),
        ]
        hashes = compute_file_hashes(files)
        assert len(hashes) == 2
        assert "a.py" in hashes
        assert "b.py" in hashes


def test_detect_changes_no_changes():
    old = {"a.py": "hash1", "b.py": "hash2"}
    new = {"a.py": "hash1", "b.py": "hash2"}
    changes = detect_changes(old, new)
    assert len(changes["added"]) == 0
    assert len(changes["removed"]) == 0
    assert len(changes["modified"]) == 0
    assert len(changes["unchanged"]) == 2


def test_detect_changes_added():
    old = {"a.py": "hash1"}
    new = {"a.py": "hash1", "b.py": "hash2"}
    changes = detect_changes(old, new)
    assert "b.py" in changes["added"]
    assert "a.py" in changes["unchanged"]


def test_detect_changes_removed():
    old = {"a.py": "hash1", "b.py": "hash2"}
    new = {"a.py": "hash1"}
    changes = detect_changes(old, new)
    assert "b.py" in changes["removed"]


def test_detect_changes_modified():
    old = {"a.py": "hash1"}
    new = {"a.py": "hash2"}
    changes = detect_changes(old, new)
    assert "a.py" in changes["modified"]
