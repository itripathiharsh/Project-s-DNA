"""Test the run_full_analysis pipeline directly (bypassing HTTP)."""
import tempfile
import os
from dna.api.analysis import run_full_analysis


def test_analysis_on_non_git_directory():
    """Pipeline must handle non-git directories without crashing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "hello.py"), "w") as f:
            f.write("def greet():\n    return 'hello'\n")
        result = run_full_analysis(tmpdir)
        assert result["repository"]["is_git"] is False
        assert result["summary"]["total_commits"] == 0
        assert result["summary"]["total_authors"] == 0
        assert result["summary"]["total_files"] >= 1
        assert result["summary"]["source_files"] >= 1


def test_analysis_with_node_modules():
    """Pipeline must skip node_modules and complete quickly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "main.py"), "w") as f:
            f.write("x = 1\n")
        node = os.path.join(tmpdir, "node_modules", "big_pkg")
        os.makedirs(node)
        for i in range(500):
            with open(os.path.join(node, f"mod{i}.js"), "w") as f:
                f.write(f"module.exports = {{id: {i}}};\n")
        result = run_full_analysis(tmpdir)
        assert result["summary"]["total_files"] < 100
        assert result["summary"]["total_files"] == 1


def test_analysis_on_empty_directory():
    """Pipeline must handle empty directories without crashing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_full_analysis(tmpdir)
        assert result["repository"]["is_git"] is False
        assert result["summary"]["total_files"] >= 0
        assert "structural" in result
        assert "risk" in result
        assert "insights" in result


def test_analysis_hotspot_insight():
    """Pipeline on a git repository with commit history should produce hotspot insights."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Tester"], cwd=tmpdir, capture_output=True)
        
        py_path = os.path.join(tmpdir, "main.py")
        with open(py_path, "w") as f:
            f.write("def greet():\n    pass\n")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial commit"], cwd=tmpdir, capture_output=True)
        
        result = run_full_analysis(tmpdir)
        assert result["repository"]["is_git"] is True
        assert result["summary"]["total_commits"] == 1
        assert "insights" in result
        
        hotspots = [i for i in result["insights"] if i["category"] == "hotspot_risk"]
        assert len(hotspots) == 1
        assert hotspots[0]["file_path"] == "main.py"
