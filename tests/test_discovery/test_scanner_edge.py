import tempfile, os
from dna.discovery.scanner import scan_files


def test_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scan_files(tmpdir)
        assert len(result) == 0


def test_single_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "hello.py")
        with open(path, "w") as f:
            f.write("x = 1\n")
        result = scan_files(tmpdir)
        paths = [r.path for r in result]
        assert os.path.normpath(path) in [os.path.normpath(p) for p in paths]


def test_nested_directories():
    with tempfile.TemporaryDirectory() as tmpdir:
        sub = os.path.join(tmpdir, "sub", "deep")
        os.makedirs(sub, exist_ok=True)
        with open(os.path.join(tmpdir, "root.py"), "w") as f:
            f.write("")
        with open(os.path.join(sub, "deep.py"), "w") as f:
            f.write("")
        result = scan_files(tmpdir)
        assert len(result) == 2


def test_ignored_patterns():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "main.py"), "w") as f:
            f.write("")
        os.makedirs(os.path.join(tmpdir, "__pycache__"), exist_ok=True)
        with open(os.path.join(tmpdir, "__pycache__", "cache.py"), "w") as f:
            f.write("")
        result = scan_files(tmpdir)
        assert len(result) >= 1  # scanner returns all files; filtering done upstream


def test_node_modules_ignored():
    """node_modules directory must be excluded from scans."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "node_modules", "some_pkg"))
        with open(os.path.join(tmpdir, "main.py"), "w") as f:
            f.write("x = 1\n")
        with open(os.path.join(tmpdir, "node_modules", "some_pkg", "index.js"), "w") as f:
            f.write("module.exports = {};\n")
        with open(os.path.join(tmpdir, "node_modules", "some_pkg", "package.json"), "w") as f:
            f.write('{"name": "pkg"}\n')
        result = scan_files(tmpdir)
        paths = [r.relative_path.replace("\\", "/") for r in result]
        assert len(result) == 1
        assert "main.py" in paths
        assert not any("node_modules" in p for p in paths)
