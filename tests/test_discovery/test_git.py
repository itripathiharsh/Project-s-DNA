import os
import tempfile
from dna.discovery.git import is_git_repository


def test_is_git_repository_with_git_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, ".git"))
        assert is_git_repository(tmpdir) is True


def test_is_git_repository_no_git():
    with tempfile.TemporaryDirectory() as tmpdir:
        assert is_git_repository(tmpdir) is False


def test_is_git_repository_invalid_path():
    assert is_git_repository("/nonexistent/path/12345") is False


def test_is_git_repository_is_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "file.txt")
        with open(filepath, "w") as f:
            f.write("hello")
        assert is_git_repository(filepath) is False


def test_is_git_repository_git_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        git_path = os.path.join(tmpdir, ".git")
        with open(git_path, "w") as f:
            f.write("gitdir: ../.git/modules/myrepo")
        assert is_git_repository(tmpdir) is True
