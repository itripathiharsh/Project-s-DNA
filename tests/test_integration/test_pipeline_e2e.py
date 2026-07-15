import os
import subprocess
import tempfile
from dna.api.analysis import run_full_analysis

def _create_temp_git_repo(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "e2e@test.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "E2E Tester"], cwd=path, capture_output=True)
    
    # Commit 1
    file_py = os.path.join(path, "main.py")
    with open(file_py, "w") as f:
        f.write("def add(x, y):\n    return x + y\n")
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: add main function"], cwd=path, capture_output=True)
    
    # Commit 2 (Hotspot creation / changes)
    with open(file_py, "a") as f:
        f.write("\ndef multiply(x, y):\n    return x * y\n")
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: add multiply function"], cwd=path, capture_output=True)

def test_pipeline_e2e_flow():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_temp_git_repo(tmpdir)
        
        # Run full analysis
        result = run_full_analysis(tmpdir)
        
        # Verify result structure
        assert "repository" in result
        assert "summary" in result
        assert "evolution" in result
        assert "knowledge" in result
        assert "risk" in result
        assert "structural" in result
        assert "insights" in result
        
        # Verify repository details
        assert result["repository"]["is_git"] is True
        assert result["repository"]["path"] == tmpdir
        
        # Verify summary
        assert result["summary"]["total_commits"] == 2
        assert result["summary"]["total_authors"] >= 1
        assert result["summary"]["total_files"] == 1
        
        # Verify evolution metrics
        assert result["evolution"]["total_commits"] == 2
        assert len(result["evolution"]["hotspots"]) >= 1
        assert result["evolution"]["hotspots"][0]["file"] == "main.py"
        
        # Verify knowledge metrics
        assert result["knowledge"]["bus_factor"] >= 1
        
        # Verify structural metrics
        assert result["structural"]["total_functions"] == 2
        
        # Verify risk metrics
        assert result["risk"]["overall_risk_score"] >= 0
        
        # Verify insights
        assert len(result["insights"]) >= 0
