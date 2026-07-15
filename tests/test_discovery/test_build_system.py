import os
import json
import tempfile
from dna.discovery.build_system import detect_build_systems


def _create_file(dirpath, filename, content=""):
    filepath = os.path.join(dirpath, filename)
    with open(filepath, "w") as f:
        f.write(content)
    return filepath


def test_detect_build_systems_python():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "pyproject.toml", "[project]\nname = 'test'")
        result = detect_build_systems(tmpdir)
        assert any(bs.name == "pip" for bs in result)
        assert any(bs.config_file == "pyproject.toml" for bs in result)


def test_detect_build_systems_node():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "package.json", json.dumps({"name": "test"}))
        result = detect_build_systems(tmpdir)
        assert any(bs.name == "npm" for bs in result)
        assert any(bs.config_file == "package.json" for bs in result)


def test_detect_build_systems_none():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = detect_build_systems(tmpdir)
        assert result == []


def test_detect_build_systems_multiple():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_file(tmpdir, "package.json", "{}")
        _create_file(tmpdir, "Makefile", "all:")
        _create_file(tmpdir, "Dockerfile", "FROM alpine")
        result = detect_build_systems(tmpdir)
        names = {bs.name for bs in result}
        assert "npm" in names
        assert "Make" in names
        assert "Docker" in names


def test_detect_build_systems_invalid_path():
    result = detect_build_systems("/nonexistent")
    assert result == []


def test_detect_build_systems_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = detect_build_systems(tmpdir)
        assert result == []
