import os
import tempfile
from dna.discovery.scanner import scan_files


def _create_file(dirpath, rel_path, content=""):
    full = os.path.join(dirpath, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    return full


def test_scan_files_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "src/main.py", "print('hello')")
        _create_file(tmpdir, "src/utils.py", "def util(): pass")
        _create_file(tmpdir, "README.md", "# My Project")
        files = scan_files(tmpdir)
        assert len(files) == 3
        paths = {f.relative_path for f in files}
        assert "src/main.py" in paths
        assert "src/utils.py" in paths
        assert "README.md" in paths


def test_scan_files_ignores_git():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, ".git"))
        _create_file(tmpdir, ".git/config", "[core]")
        _create_file(tmpdir, "src/main.py", "x = 1")
        files = scan_files(tmpdir)
        paths = {f.relative_path for f in files}
        assert ".git/config" not in paths
        assert "src/main.py" in paths
        assert len(files) == 1


def test_scan_files_apply_ignore():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "node_modules/pkg/index.js", "")
        _create_file(tmpdir, "src/index.js", "console.log('hello')")
        files = scan_files(tmpdir, ignore_patterns=["node_modules/"])
        paths = {f.relative_path for f in files}
        assert "node_modules/pkg/index.js" not in paths
        assert "src/index.js" in paths
        assert len(files) == 1


def test_scan_files_nested_ignore():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "src/__pycache__/foo.pyc", "")
        _create_file(tmpdir, "src/main.py", "")
        files = scan_files(tmpdir, ignore_patterns=["__pycache__/"])
        paths = {f.relative_path for f in files}
        assert "src/__pycache__/foo.pyc" not in paths
        assert "src/main.py" in paths


def test_scan_files_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = scan_files(tmpdir)
        assert files == []


def test_scan_files_invalid_path():
    files = scan_files("/nonexistent/path/12345")
    assert files == []


def test_scan_files_file_metadata():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "main.py", "x = 1")
        files = scan_files(tmpdir)
        assert len(files) == 1
        f = files[0]
        assert f.filename == "main.py"
        assert f.extension == ".py"
        assert f.language == "Python"
        assert f.size_bytes > 0
        assert f.is_directory is False
        assert f.is_source is True


def test_scan_files_multiple_extensions():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "a.py", "")
        _create_file(tmpdir, "b.ts", "")
        _create_file(tmpdir, "c.json", "{}")
        _create_file(tmpdir, "d.md", "# Title")
        files = scan_files(tmpdir)
        assert len(files) == 4
        langs = {f.language for f in files}
        assert "Python" in langs
        assert "TypeScript" in langs
        assert "JSON" in langs
        assert "Markdown" in langs


def test_scan_files_ignores_build_directories():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, ".next/server/app.js", "console.log(1)")
        _create_file(tmpdir, "dist/index.js", "console.log(2)")
        _create_file(tmpdir, "build/main.js", "console.log(3)")
        _create_file(tmpdir, "src/main.js", "console.log(4)")
        files = scan_files(tmpdir)
        paths = {f.relative_path for f in files}
        assert ".next/server/app.js" not in paths
        assert "dist/index.js" not in paths
        assert "build/main.js" not in paths
        assert "src/main.js" in paths
        assert len(files) == 1


def test_scan_files_large_file_skipping():
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = os.path.join(tmpdir, "large.py")
        with open(fpath, "wb") as f:
            f.write(b"x" * (1024 * 1024 + 100))
        _create_file(tmpdir, "normal.py", "x = 1")
        files = scan_files(tmpdir)
        paths = {f.relative_path for f in files}
        assert "large.py" not in paths
        assert "normal.py" in paths
        assert len(files) == 1
