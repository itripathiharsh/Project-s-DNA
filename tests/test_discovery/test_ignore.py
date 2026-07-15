import os
import tempfile
from dna.discovery.ignore import parse_gitignore, parse_dnaignore, should_ignore


def _create_ignore_file(dirpath, filename, content):
    filepath = os.path.join(dirpath, filename)
    with open(filepath, "w") as f:
        f.write(content)
    return filepath


def test_parse_gitignore_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_ignore_file(tmpdir, ".gitignore", "node_modules/\n*.pyc\n.env\n")
        patterns = parse_gitignore(tmpdir)
        assert "node_modules/" in patterns
        assert "*.pyc" in patterns
        assert ".env" in patterns


def test_parse_gitignore_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        patterns = parse_gitignore(tmpdir)
        assert patterns == []


def test_parse_gitignore_comments_and_blanks():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_ignore_file(tmpdir, ".gitignore", "# comment\n\nnode_modules/\n# another\n*.log\n")
        patterns = parse_gitignore(tmpdir)
        assert "node_modules/" in patterns
        assert "*.log" in patterns
        assert "# comment" not in patterns
        assert "" not in patterns


def test_parse_dnaignore():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_ignore_file(tmpdir, ".dnaignore", "build/\ndist/")
        patterns = parse_dnaignore(tmpdir)
        assert "build/" in patterns
        assert "dist/" in patterns


def test_parse_dnaignore_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        patterns = parse_dnaignore(tmpdir)
        assert patterns == []


def test_should_ignore_match():
    assert should_ignore("node_modules/foo/bar.js", ["node_modules/"]) is True


def test_should_ignore_no_match():
    assert should_ignore("src/foo.py", ["node_modules/"]) is False


def test_should_ignore_wildcard():
    assert should_ignore("foo.pyc", ["*.pyc"]) is True


def test_should_ignore_deep_path():
    assert should_ignore("src/node_modules/pkg/index.js", ["node_modules/"]) is True


def test_should_ignore_empty_patterns():
    assert should_ignore("any/file.py", []) is False
    assert should_ignore("any/file.py", [""]) is False


def test_should_ignore_root_pattern():
    assert should_ignore("build/output.o", ["/build"]) is True


def test_should_ignore_dotfiles():
    assert should_ignore(".env", [".env"]) is True


def test_should_ignore_subdirectory():
    assert should_ignore("src/__pycache__/foo.pyc", ["__pycache__/"]) is True


def test_should_ignore_advanced():
    # Double star test
    assert should_ignore("a/b/c/foo.txt", ["**/foo.txt"]) is True
    assert should_ignore("foo.txt", ["**/foo.txt"]) is True
    assert should_ignore("a/b/c/foo.txt", ["a/**/foo.txt"]) is True
    
    # Negation test
    assert should_ignore("src/important.log", ["*.log", "!important.log"]) is False
    assert should_ignore("src/other.log", ["*.log", "!important.log"]) is True
    
    # Directory-only test
    assert should_ignore("node_modules/foo.js", ["node_modules/"]) is True
    # If a file has the same name as a directory-only pattern but isn't in that directory:
    # E.g. "node_modules" as a file itself:
    assert should_ignore("node_modules", ["node_modules/"]) is False
    
    # Root-relative test
    assert should_ignore("build/output.o", ["/build"]) is True
    assert should_ignore("src/build/output.o", ["/build"]) is False
