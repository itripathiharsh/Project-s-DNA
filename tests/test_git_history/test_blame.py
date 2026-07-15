import os
import subprocess
import tempfile
import pytest
from dna.git_history.blame import get_file_blame
from dna.discovery.orchestrator import NotAGitRepositoryError


def _init_repo(path: str):
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "alice@test.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Alice"], cwd=path, capture_output=True)


def test_get_file_blame_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        
        # Alice writes line 1 and 2
        fpath = os.path.join(tmpdir, "main.txt")
        with open(fpath, "w") as f:
            f.write("Line 1\nLine 2\n")
            
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, capture_output=True)
        
        # Bob appends line 3 and 4
        subprocess.run(["git", "config", "user.email", "bob@test.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Bob"], cwd=tmpdir, capture_output=True)
        
        with open(fpath, "a") as f:
            f.write("Line 3\nLine 4\n")
            
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "update"], cwd=tmpdir, capture_output=True)
        
        # Get blame
        blame = get_file_blame(tmpdir, "main.txt")
        
        assert blame.get("Alice") == 2
        assert blame.get("Bob") == 2


def test_get_file_blame_not_git():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(NotAGitRepositoryError):
            get_file_blame(tmpdir, "main.txt")


def test_get_file_blame_untracked_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        fpath = os.path.join(tmpdir, "untracked.txt")
        with open(fpath, "w") as f:
            f.write("Line 1\n")
            
        # File is untracked, blame should return {}
        blame = get_file_blame(tmpdir, "untracked.txt")
        assert blame == {}
