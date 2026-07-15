from fastapi.testclient import TestClient
from dna.api.app import app
import os
import subprocess
import json

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_status():
    r = client.get("/status")
    assert r.status_code == 200
    data = r.json()
    assert data["version"] == "1.0.0"
    assert data["ready"] is True


def test_frontend_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "Project DNA" in r.text


def test_frontend_assets_served():
    # Parse the index.html served to find actual asset paths
    r = client.get("/")
    assert r.status_code == 200
    import re
    js_match = re.search(r'src="(/assets/[^"]+\.js)"', r.text)
    css_match = re.search(r'href="(/assets/[^"]+\.css)"', r.text)
    
    if js_match:
        js_path = js_match.group(1)
        r_js = client.get(js_path)
        assert r_js.status_code == 200
        
    if css_match:
        css_path = css_match.group(1)
        r_css = client.get(css_path)
        assert r_css.status_code == 200


def test_analyze_no_repo():
    r = client.post("/analyze", json={"repo_path": "C:\\nonexistent_path_xyz"})
    assert r.status_code == 400
    assert "does not exist" in r.json()["detail"]


def test_analyze_path_traversal():
    r = client.post("/analyze", json={"repo_path": "C:\\some\\path\\..\\escape"})
    assert r.status_code == 400
    assert "Path traversal not allowed" in r.json()["detail"]


def test_analyze_file_instead_of_directory(tmp_path):
    fpath = tmp_path / "hello.txt"
    fpath.write_text("hello")
    r = client.post("/analyze", json={"repo_path": str(fpath)})
    assert r.status_code == 400
    assert "not a directory" in r.json()["detail"]


def _create_temp_git_repo(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=path, capture_output=True)
    file_a = os.path.join(path, "main.py")
    file_b = os.path.join(path, "utils.py")
    with open(file_a, "w") as f:
        f.write("def foo():\n    pass\n")
    with open(file_b, "w") as f:
        f.write("def bar():\n    pass\n")
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: initial"], cwd=path, capture_output=True)
    with open(file_a, "a") as f:
        f.write("def new_func():\n    return 1\n")
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: add new_func"], cwd=path, capture_output=True)


def test_analyze_non_git_repo(tmp_path):
    """Analysis of a non-git directory should not raise 500."""
    repo_dir = str(tmp_path / "non_git_project")
    os.makedirs(repo_dir, exist_ok=True)
    with open(os.path.join(repo_dir, "main.py"), "w") as f:
        f.write("x = 1\n")
    with open(os.path.join(repo_dir, "utils.py"), "w") as f:
        f.write("y = 2\n")
    r = client.post("/analyze", json={"repo_path": repo_dir})
    assert r.status_code == 200
    data = r.json()
    assert data["summary"]["total_commits"] == 0
    assert data["summary"]["total_authors"] == 0
    assert data["summary"]["total_files"] >= 2
    assert "evolution" in data
    assert "knowledge" in data


def test_analyze_with_repo(tmp_path):
    repo_dir = str(tmp_path / "test_repo")
    _create_temp_git_repo(repo_dir)
    r = client.post("/analyze", json={"repo_path": repo_dir})
    assert r.status_code == 200
    data = r.json()
    assert data["summary"]["total_commits"] == 2
    assert data["summary"]["total_authors"] >= 1
    assert data["summary"]["total_files"] >= 2
    assert "insights" in data
    assert "evolution" in data
    assert "risk" in data
    assert "knowledge" in data
    assert "structural" in data
