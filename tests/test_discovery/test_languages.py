import pytest
from dna.discovery.languages import detect_language, classify_files, is_source_file
from dna.models import FileInfo


def test_detect_language_known():
    assert detect_language(".py") == "Python"
    assert detect_language(".ts") == "TypeScript"
    assert detect_language(".tsx") == "TypeScript"
    assert detect_language(".js") == "JavaScript"
    assert detect_language(".go") == "Go"
    assert detect_language(".rs") == "Rust"
    assert detect_language(".java") == "Java"
    assert detect_language(".md") == "Markdown"
    assert detect_language(".json") == "JSON"


def test_detect_language_unknown():
    assert detect_language(".xyz") == "Unknown"
    assert detect_language(".abc") == "Unknown"


def test_detect_language_case_insensitive():
    assert detect_language(".PY") == "Python"
    assert detect_language(".TS") == "TypeScript"


def test_detect_language_no_extension():
    assert detect_language("") == "Unknown"


def test_is_source_file_true():
    assert is_source_file(".py") is True
    assert is_source_file(".ts") is True
    assert is_source_file(".rs") is True


def test_is_source_file_false():
    assert is_source_file(".json") is False
    assert is_source_file(".md") is False
    assert is_source_file(".png") is False


def test_classify_files_empty():
    assert classify_files([]) == {}


def test_classify_files_counts():
    files = [
        FileInfo(path="/a.py", relative_path="a.py", filename="a.py", extension=".py", language="Python", size_bytes=100, is_directory=False, is_source=True),
        FileInfo(path="/b.py", relative_path="b.py", filename="b.py", extension=".py", language="Python", size_bytes=200, is_directory=False, is_source=True),
        FileInfo(path="/c.ts", relative_path="c.ts", filename="c.ts", extension=".ts", language="TypeScript", size_bytes=300, is_directory=False, is_source=True),
    ]
    stats = classify_files(files)
    assert stats["Python"].file_count == 2
    assert stats["Python"].total_bytes == 300
    assert stats["TypeScript"].file_count == 1
    assert stats["TypeScript"].total_bytes == 300
    assert stats["Python"].percentage == pytest.approx(2 / 3, abs=0.001)
    assert stats["TypeScript"].percentage == pytest.approx(1 / 3, abs=0.001)
