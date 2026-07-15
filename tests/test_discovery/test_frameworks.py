import os
import json
import tempfile
from dna.discovery.frameworks import detect_frameworks
from dna.models import BuildSystem


def _create_file(dirpath, filename, content):
    filepath = os.path.join(dirpath, filename)
    with open(filepath, "w") as f:
        f.write(content)
    return filepath


def test_detect_frameworks_react():
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg = {"dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"}}
        _create_file(tmpdir, "package.json", json.dumps(pkg))
        result = detect_frameworks(tmpdir, [BuildSystem(name="npm", config_file="package.json")])
        names = {fw.name for fw in result}
        assert "React" in names


def test_detect_frameworks_fastapi():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "pyproject.toml", '[project]\ndependencies = ["fastapi>=0.100"]')
        result = detect_frameworks(tmpdir, [BuildSystem(name="pip", config_file="pyproject.toml")])
        names = {fw.name for fw in result}
        assert "FastAPI" in names


def test_detect_frameworks_none():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = detect_frameworks(tmpdir, [])
        assert result == []


def test_detect_frameworks_no_package_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = detect_frameworks(tmpdir, [])
        assert result == []


def test_detect_frameworks_no_duplicates():
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg = {"dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"}}
        _create_file(tmpdir, "package.json", json.dumps(pkg))
        _create_file(tmpdir, "pyproject.toml", "")
        result = detect_frameworks(tmpdir, [BuildSystem(name="npm", config_file="package.json")])
        react_count = sum(1 for fw in result if fw.name == "React")
        assert react_count == 1


def test_detect_frameworks_malformed_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "package.json", "not valid json")
        result = detect_frameworks(tmpdir, [BuildSystem(name="npm", config_file="package.json")])
        assert result == []
