import os
import tempfile
from dna.discovery.orchestrator import (
    discover_repository,
    PathNotFoundError,
    NotAGitRepositoryError,
)


def _create_file(dirpath, rel_path, content=""):
    full = os.path.join(dirpath, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    return full


def test_discover_repository_invalid_path():
    import pytest
    with pytest.raises(PathNotFoundError):
        discover_repository("/nonexistent/path/12345")


def test_discover_repository_complete():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, ".git"))
        _create_file(tmpdir, "src/main.py", "print('hello')")
        _create_file(tmpdir, "src/utils.py", "def util(): pass")
        _create_file(tmpdir, "README.md", "# Project")
        _create_file(tmpdir, "pyproject.toml", "[project]\nname = 'test'")

        metadata = discover_repository(tmpdir)

        assert metadata.is_git is True
        assert metadata.file_count == 4
        assert metadata.primary_language == "Python"
        assert len(metadata.languages) > 0
        assert any(bs.name == "pip" for bs in metadata.build_systems)
        assert metadata.scan_duration_ms > 0
        assert metadata.path == os.path.abspath(tmpdir)


def test_discover_repository_no_git():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "main.py", "x = 1")
        metadata = discover_repository(tmpdir)
        assert metadata.is_git is False
        assert metadata.file_count == 1


def test_discover_repository_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        metadata = discover_repository(tmpdir)
        assert metadata.file_count == 0
        assert metadata.languages == []
        assert metadata.primary_language is None


def test_discover_repository_metrics():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, ".git"))
        _create_file(tmpdir, "a.py", "x = 1")
        metadata = discover_repository(tmpdir)
        assert metadata.scan_duration_ms > 0
        assert metadata.file_count >= 1


def test_discover_repository_ignores_git():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, ".git"))
        _create_file(tmpdir, ".git/config", "[core]")
        _create_file(tmpdir, "main.py", "x = 1")
        metadata = discover_repository(tmpdir)
        asserts = [f for f in [".git/config"]]  # should be ignored
        assert metadata.file_count == 1


def test_discover_repository_with_dna_ignore():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, ".git"))
        _create_file(tmpdir, ".dnaignore", "build/\n")
        _create_file(tmpdir, "build/output.o", "")
        _create_file(tmpdir, "src/main.py", "x = 1")
        metadata = discover_repository(tmpdir)
        assert metadata.has_dna_ignore is True
        assert metadata.file_count == 1
        assert metadata.ignored_files_count > 0


def test_discover_repository_name():
    with tempfile.TemporaryDirectory() as tmpdir:
        metadata = discover_repository(tmpdir)
        assert metadata.name == os.path.basename(tmpdir)
