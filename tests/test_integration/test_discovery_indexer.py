import os
import tempfile
from dna.discovery.orchestrator import discover_repository
from dna.indexer.orchestrator import index_repository

def test_discovery_indexer_flow():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock repository layout
        os.makedirs(os.path.join(tmpdir, "src"))
        os.makedirs(os.path.join(tmpdir, "tests"))
        os.makedirs(os.path.join(tmpdir, ".next"))
        
        with open(os.path.join(tmpdir, "src", "main.py"), "w") as f:
            f.write("def main(): pass\n")
        with open(os.path.join(tmpdir, "tests", "test_main.py"), "w") as f:
            f.write("def test_main(): pass\n")
        with open(os.path.join(tmpdir, ".next", "build.js"), "w") as f:
            f.write("console.log('build');\n")
        with open(os.path.join(tmpdir, "config.json"), "w") as f:
            f.write("{}")
            
        # 1. Discover
        repo = discover_repository(tmpdir)
        assert repo is not None
        assert repo.path == tmpdir
        assert repo.is_git is False
        
        # 2. Index
        inventory = index_repository(tmpdir, repo)
        assert inventory is not None
        
        # Verify category mapping and ignores
        files = {f.relative_path: f.category for f in inventory.files}
        
        # .next should be ignored
        assert ".next/build.js" not in files
        
        # Other files should be categorized correctly
        assert os.path.join("src", "main.py").replace("\\", "/") in [f.replace("\\", "/") for f in files]
        assert os.path.join("tests", "test_main.py").replace("\\", "/") in [f.replace("\\", "/") for f in files]
        assert "config.json" in files
        
        # Check specific category assignments
        for f in inventory.files:
            rel = f.relative_path.replace("\\", "/")
            if rel.startswith("src/"):
                assert f.category == "source"
            elif rel.startswith("tests/"):
                assert f.category == "test"
            elif rel == "config.json":
                assert f.category == "config"
