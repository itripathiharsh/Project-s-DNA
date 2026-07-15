import os
import tempfile
from dna.indexer.orchestrator import index_repository
from dna.models import RepositoryMetadata


def test_index_repository_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, ".git"))
        src = os.path.join(tmpdir, "src")
        os.mkdir(src)
        with open(os.path.join(src, "main.py"), "w") as f: f.write("x = 1")
        with open(os.path.join(tmpdir, "README.md"), "w") as f: f.write("# Readme")
        with open(os.path.join(tmpdir, "package.json"), "w") as f: f.write("{}")

        meta = RepositoryMetadata(name="test", path=tmpdir, is_git=True, primary_language="Python")
        inv = index_repository(tmpdir, meta)

        assert inv.total_files == 3
        assert all(f.content_hash for f in inv.files)


def test_index_repository_invalid_path():
    meta = RepositoryMetadata(name="test", path="/nonexistent", is_git=True)
    try:
        index_repository("C:\\nonexistent_path_xyz", meta)
        assert False, "Expected PathNotFoundError"
    except Exception as e:
        from dna.discovery.orchestrator import PathNotFoundError
        assert isinstance(e, PathNotFoundError)


def test_index_repository_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, ".git"))
        meta = RepositoryMetadata(name="test", path=tmpdir, is_git=True)
        inv = index_repository(tmpdir, meta)
        assert inv.total_files == 0
        assert inv.files == []
