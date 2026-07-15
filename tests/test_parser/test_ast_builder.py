import os
import tempfile
from dna.parser.ast_builder import parse_source, parse_file
from dna.parser.errors import UnsupportedLanguageError


def test_parse_source_python():
    source = "def hello():\n    pass\n"
    result = parse_source(source, "Python")
    assert result is not None
    assert result.language == "Python"
    assert len(result.symbols.functions) == 1
    assert result.symbols.functions[0].name == "hello"


def test_parse_source_javascript():
    source = "function greet(name) { return name; }"
    result = parse_source(source, "JavaScript")
    assert result is not None
    assert result.language == "JavaScript"
    assert len(result.symbols.functions) == 1
    assert result.symbols.functions[0].name == "greet"


def test_parse_source_unsupported():
    try:
        parse_source("fn main() {}", "Cobol")
        assert False, "Expected UnsupportedLanguageError"
    except UnsupportedLanguageError:
        pass


def test_parse_file_nonexistent():
    result = parse_file("C:\\nonexistent.py", "Python")
    assert result is None


def test_parse_file_real():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.py")
        with open(path, "w") as f:
            f.write("x = 1\n")
        result = parse_file(path, "Python")
        assert result is not None
        assert result.file_path == path
