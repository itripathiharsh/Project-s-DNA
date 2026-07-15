import os
import subprocess
import tempfile
from dna.git_history.miner import mine_git_history
from dna.git_history.blame import get_file_blame

def _create_temp_git_repo(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "tester@test.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Integration Tester"], cwd=path, capture_output=True)
    
    file_a = os.path.join(path, "hello.py")
    with open(file_a, "w") as f:
        f.write("print('Hello, World!')\n")
        
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: initial commit"], cwd=path, capture_output=True)
    
    # Author B commits
    subprocess.run(["git", "config", "user.email", "another@test.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Author B"], cwd=path, capture_output=True)
    
    with open(file_a, "a") as f:
        f.write("print('Line 2')\n")
        
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: modify hello.py"], cwd=path, capture_output=True)

def test_git_miner_and_blame_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_temp_git_repo(tmpdir)
        
        # 1. Mine history
        history = mine_git_history(tmpdir)
        assert history is not None
        assert len(history.commits) == 2
        
        # Verify authors
        authors = {c.author for c in history.commits}
        assert "Integration Tester" in authors
        assert "Author B" in authors
        
        # 2. Get file blame
        blame = get_file_blame(tmpdir, "hello.py")
        assert blame is not None
        assert blame.get("Integration Tester") == 1
        assert blame.get("Author B") == 1
