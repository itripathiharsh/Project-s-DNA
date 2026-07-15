import os
import subprocess
import tempfile
from dna.git_history.commit_parser import parse_commit_log, categorize_commit
from dna.discovery.git import is_git_repository


def _init_repo(path: str):
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=path, capture_output=True)


def _commit(path: str, msg: str, filename: str = "f.txt", content: str = "x"):
    fpath = os.path.join(path, filename)
    with open(fpath, "a") as f:
        f.write(content)
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=path, capture_output=True)


def test_parse_commit_log_empty_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        result = parse_commit_log(tmpdir)
        assert isinstance(result, list)
        assert len(result) == 0


def test_parse_commit_log_single_commit():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir, "initial commit")
        result = parse_commit_log(tmpdir)
        assert len(result) == 1
        c = result[0]
        assert c.message == "initial commit"
        assert c.author_name == "Tester"
        assert c.author_email == "test@test.com"
        assert len(c.sha) == 40
        assert c.parents == []


def test_parse_commit_log_multiple_commits():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir, "first")
        _commit(tmpdir, "second")
        result = parse_commit_log(tmpdir)
        assert len(result) == 2
        assert result[0].message == "first"
        assert result[1].message == "second"
        assert result[1].parents == [result[0].sha]


def test_parse_commit_log_merge_commit():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir, "base", "base.txt")
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=tmpdir, capture_output=True)
        _commit(tmpdir, "feature work", "feature.txt")
        subprocess.run(["git", "checkout", "master"], cwd=tmpdir, capture_output=True)
        _commit(tmpdir, "master work", "master.txt")
        subprocess.run(
            ["git", "merge", "--no-edit", "feature"],
            cwd=tmpdir, capture_output=True
        )
        result = parse_commit_log(tmpdir)
        merge_commits = [c for c in result if len(c.parents) > 1]
        assert len(merge_commits) == 1


def test_parse_commit_log_invalid_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        import pytest
        from dna.git_history.errors import GitCommandError
        with pytest.raises(GitCommandError):
            parse_commit_log(tmpdir)


def test_categorize_commit():
    assert categorize_commit("feat: add login") == "feat"
    assert categorize_commit("fix crash") == "fix"
    assert categorize_commit("refactor module X") == "refactor"
    assert categorize_commit("test parser") == "test"
    assert categorize_commit("doc usage") == "docs"
    assert categorize_commit("chore bump version") == "chore"
    assert categorize_commit("something random") == "other"
    assert categorize_commit("Feat: uppercase") == "feat"


def test_parse_commit_log_per_file_changes():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        f1 = os.path.join(tmpdir, "a.txt")
        f2 = os.path.join(tmpdir, "b.txt")
        with open(f1, "w") as f:
            f.write("line1\nline2\n")
        with open(f2, "w") as f:
            f.write("hello\n")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add files"], cwd=tmpdir, capture_output=True)

        result = parse_commit_log(tmpdir)
        assert len(result) == 1
        c = result[0]
        assert len(c.per_file_changes) == 2
        paths = {fc.file_path for fc in c.per_file_changes}
        assert paths == {"a.txt", "b.txt"}
        fc_a = [fc for fc in c.per_file_changes if fc.file_path == "a.txt"][0]
        assert fc_a.insertions == 2
        assert fc_a.deletions == 0
