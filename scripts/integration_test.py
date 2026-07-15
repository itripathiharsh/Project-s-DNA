import sys
import os
import subprocess
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from dna.api.analysis import run_full_analysis

with tempfile.TemporaryDirectory() as tmpdir:
    repo_path = os.path.join(tmpdir, "test_repo")
    os.makedirs(repo_path, exist_ok=True)
    subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "dev@dna.io"], cwd=repo_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "DNA Dev"], cwd=repo_path, capture_output=True)

    for name in ["main.py", "utils.py", "tests/test_main.py"]:
        full = os.path.join(repo_path, name)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(f"# {name}\ndef {os.path.splitext(os.path.basename(name))[0]}():\n    pass\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: initial commit"], cwd=repo_path, capture_output=True)

    with open(os.path.join(repo_path, "main.py"), "a") as f:
        f.write("\ndef new_func():\n    return 42\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: add new_func\n\nrefs #1"], cwd=repo_path, capture_output=True)

    with open(os.path.join(repo_path, "utils.py"), "a") as f:
        f.write("\ndef helper():\n    pass\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "fix: add helper"], cwd=repo_path, capture_output=True)

    print(f"Analyzing: {repo_path}")
    start = time.time()
    result = run_full_analysis(repo_path)
    elapsed = time.time() - start

    print(f"Analysis completed in {elapsed:.2f}s")
    print(f"  Commits: {result['summary']['total_commits']}")
    print(f"  Authors: {result['summary']['total_authors']}")
    print(f"  Total files: {result['summary']['total_files']}")
    print(f"  Source files: {result['summary'].get('source_files', 0)}")
    print(f"  Test files: {result['summary'].get('test_files', 0)}")
    print(f"  Risk indicators: {len(result['risk']['risk_indicators'])}")
    print(f"  Insights: {len(result['insights'])}")
    print(f"  Bus factor: {result['knowledge']['bus_factor']}")
    print(f"  Bus factor risk: {result['knowledge']['bus_factor_risk']}")
    print(f"  Top contributor: {result['knowledge']['top_contributor']}")
    print(f"  Evolution categories: {result['evolution']['commit_categories']}")
