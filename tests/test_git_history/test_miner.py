import os
import subprocess
import tempfile
from dna.git_history.miner import mine_git_history
from dna.discovery.orchestrator import PathNotFoundError, NotAGitRepositoryError


def _init_repo(path: str):
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=path, capture_output=True)


def _commit(path: str, msg: str = "init", filename: str = "f.txt", content: str = "x"):
    fpath = os.path.join(path, filename)
    with open(fpath, "w") as f:
        f.write(content)
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", msg, "--allow-empty"], cwd=path, capture_output=True)


def test_mine_git_history_full():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir, "feat: add login", "login.py", "def login(): pass")
        _commit(tmpdir, "fix: typo", "login.py", "def login(): return True")
        subprocess.run(["git", "tag", "v1.0.0"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "branch", "feature-x"], cwd=tmpdir, capture_output=True)

        result = mine_git_history(tmpdir)
        assert len(result.commits) == 2
        assert len(result.branches) >= 2
        assert len(result.tags) == 1
        assert len(result.author_stats) == 1
        assert result.total_branches >= 2
        assert result.total_tags == 1


def test_mine_git_history_empty_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        result = mine_git_history(tmpdir)
        assert len(result.commits) == 0
        assert len(result.author_stats) == 0


def test_mine_git_history_invalid_path():
    try:
        mine_git_history("C:\\nonexistent_path_xyz")
        assert False, "Expected PathNotFoundError"
    except PathNotFoundError:
        pass


def test_mine_git_history_not_a_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            mine_git_history(tmpdir)
            assert False, "Expected NotAGitRepositoryError"
        except NotAGitRepositoryError:
            pass


def test_mine_git_history_author_stats():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir, "first", content="a")
        subprocess.run(["git", "config", "user.email", "other@o.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Other"], cwd=tmpdir, capture_output=True)
        _commit(tmpdir, "second", content="b")

        result = mine_git_history(tmpdir)
        assert len(result.author_stats) == 2
        names = {a.name for a in result.author_stats}
        assert names == {"T", "Other"}
