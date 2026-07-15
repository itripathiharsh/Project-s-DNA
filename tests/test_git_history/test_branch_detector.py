import os
import subprocess
import tempfile
from dna.git_history.branch_detector import detect_branches, detect_merge_commits
from dna.models import Commit


def _init_repo(path: str):
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=path, capture_output=True)


def _commit(path: str, msg: str, filename: str = "f.txt"):
    fpath = os.path.join(path, filename)
    with open(fpath, "a") as f:
        f.write("x")
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=path, capture_output=True)


def test_detect_branches_single():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir, "init")
        branches = detect_branches(tmpdir)
        names = [b.name for b in branches]
        assert any(b.is_head for b in branches)
        assert len(branches) >= 1


def test_detect_branches_multiple():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir, "init")
        subprocess.run(["git", "branch", "feature-x"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "branch", "feature-y"], cwd=tmpdir, capture_output=True)
        branches = detect_branches(tmpdir)
        names = [b.name for b in branches]
        assert "feature-x" in names
        assert "feature-y" in names


def test_detect_branches_empty_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        branches = detect_branches(tmpdir)
        assert len(branches) >= 1


def test_detect_merge_commits():
    commits = [
        Commit(sha="a", parents=[]),
        Commit(sha="b", parents=["a"]),
        Commit(sha="c", parents=["a", "b"]),
        Commit(sha="d", parents=["c"]),
    ]
    merges = detect_merge_commits(commits)
    assert len(merges) == 1
    assert merges[0].sha == "c"


def test_detect_merge_commits_none():
    commits = [
        Commit(sha="a", parents=[]),
        Commit(sha="b", parents=["a"]),
    ]
    assert detect_merge_commits(commits) == []


def test_detect_merge_commits_empty():
    assert detect_merge_commits([]) == []
