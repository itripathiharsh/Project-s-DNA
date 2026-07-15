import os
import tempfile
from dna.models import FileInventory, IndexedFile, FileCategory
from dna.parser.orchestrator import parse_repository


def _create_file(tmpdir: str, rel_path: str, content: str):
    full = os.path.join(tmpdir, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    return full


def test_parse_repository_empty():
    inventory = FileInventory(files=[])
    result = parse_repository(inventory)
    assert result == []


def test_parse_repository_python_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        p1 = _create_file(tmpdir, "src/main.py", "import os\n\ndef main():\n    pass\n")
        p2 = _create_file(tmpdir, "src/utils.py", "def helper():\n    return 1\n")
        _create_file(tmpdir, "README.md", "# Project")  # not SOURCE

        files = [
            IndexedFile(path=p1, relative_path="src/main.py", filename="main.py", extension=".py",
                        language="Python", size_bytes=30, is_directory=False, is_source=True,
                        category=FileCategory.SOURCE, content_hash="a"),
            IndexedFile(path=p2, relative_path="src/utils.py", filename="utils.py", extension=".py",
                        language="Python", size_bytes=20, is_directory=False, is_source=True,
                        category=FileCategory.SOURCE, content_hash="b"),
        ]
        inventory = FileInventory(files=files, total_files=2)
        result = parse_repository(inventory, max_workers=2)
        assert len(result) == 2
        assert all(p.relative_path for p in result)


def test_parse_repository_no_source():
    inventory = FileInventory(files=[])
    result = parse_repository(inventory)
    assert result == []


def test_parse_repository_skips_binary_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        p1 = os.path.join(tmpdir, "src/binary.py")
        os.makedirs(os.path.dirname(p1), exist_ok=True)
        with open(p1, "wb") as f:
            f.write(b"import os\n\x00\x00\x00\x00")
            
        p2 = _create_file(tmpdir, "src/utils.py", "def helper():\n    return 1\n")

        files = [
            IndexedFile(path=p1, relative_path="src/binary.py", filename="binary.py", extension=".py",
                        language="Python", size_bytes=30, is_directory=False, is_source=True,
                        category=FileCategory.SOURCE, content_hash="a"),
            IndexedFile(path=p2, relative_path="src/utils.py", filename="utils.py", extension=".py",
                        language="Python", size_bytes=20, is_directory=False, is_source=True,
                        category=FileCategory.SOURCE, content_hash="b"),
        ]
        inventory = FileInventory(files=files, total_files=2)
        result = parse_repository(inventory, max_workers=2)
        assert len(result) == 1
        assert result[0].relative_path == "src/utils.py"


def test_parse_repository_go_rust():
    with tempfile.TemporaryDirectory() as tmpdir:
        p1 = _create_file(tmpdir, "main.go", "package main\nimport \"fmt\"\nfunc main() {}")
        p2 = _create_file(tmpdir, "main.rs", "fn main() {}")

        files = [
            IndexedFile(path=p1, relative_path="main.go", filename="main.go", extension=".go",
                        language="Go", size_bytes=30, is_directory=False, is_source=True,
                        category=FileCategory.SOURCE, content_hash="a"),
            IndexedFile(path=p2, relative_path="main.rs", filename="main.rs", extension=".rs",
                        language="Rust", size_bytes=20, is_directory=False, is_source=True,
                        category=FileCategory.SOURCE, content_hash="b"),
        ]
        inventory = FileInventory(files=files, total_files=2)
        result = parse_repository(inventory, max_workers=2)
        assert len(result) == 2
        langs = {r.language for r in result}
        assert "Go" in langs
        assert "Rust" in langs
