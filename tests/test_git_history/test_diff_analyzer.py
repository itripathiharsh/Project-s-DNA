import os
import subprocess
import tempfile
from dna.git_history.diff_analyzer import get_file_changes, get_commit_diff
from dna.git_history.commit_parser import parse_commit_log
from dna.git_history.errors import GitCommandError


def _init_repo(path: str):
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=path, capture_output=True)


def _commit(path: str, msg: str = "init"):
    fpath = os.path.join(path, "f.txt")
    with open(fpath, "w") as f:
        f.write("hello")
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=path, capture_output=True)


def _sha(path: str) -> str:
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True
    )
    return out.stdout.strip()


def test_get_file_changes():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir, "first")
        sha = _sha(tmpdir)
        changes = get_file_changes(tmpdir, sha)
        assert len(changes) == 1
        assert changes[0].file_path == "f.txt"
        assert changes[0].insertions > 0


def test_get_commit_diff():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir, "first")
        sha = _sha(tmpdir)
        diff = get_commit_diff(tmpdir, sha)
        assert "hello" in diff


def test_get_file_changes_invalid_sha():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir)
        try:
            get_file_changes(tmpdir, "0" * 40)
            assert False, "Expected GitCommandError"
        except GitCommandError:
            pass
