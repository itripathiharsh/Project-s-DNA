import os
import tempfile
from dna.indexer.inventory import build_file_inventory
from dna.models import FileInfo, RepositoryMetadata


_EMPTY_META = RepositoryMetadata(name="test", path="/test", is_git=True)


def _create_files(tmpdir: str, file_specs: list[tuple[str, str]]) -> list[FileInfo]:
    files = []
    for rel_path, content in file_specs:
        full = os.path.join(tmpdir, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)
        ext = "." + rel_path.split(".")[-1] if "." in rel_path else ""
        files.append(FileInfo(
            path=full,
            relative_path=rel_path,
            filename=os.path.basename(rel_path),
            extension=ext,
            language="Python" if rel_path.endswith(".py") else "Unknown",
            size_bytes=len(content),
            is_directory=False,
            is_source=rel_path.endswith(".py"),
        ))
    return files


def test_build_inventory_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = _create_files(tmpdir, [("main.py", "print(1)"), ("README.md", "# Hello")])
        inv = build_file_inventory(files, _EMPTY_META)
        assert inv.total_files == 2
        assert inv.total_size_bytes > 0
        assert all(f.content_hash for f in inv.files)


def test_build_inventory_hashes():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = _create_files(tmpdir, [("a.py", "hello"), ("b.py", "world")])
        inv = build_file_inventory(files, _EMPTY_META)
        assert inv.files[0].content_hash != inv.files[1].content_hash


def test_build_inventory_incremental_unchanged():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = _create_files(tmpdir, [("a.py", "hello")])
        inv1 = build_file_inventory(files, _EMPTY_META)
        inv2 = build_file_inventory(files, _EMPTY_META, inv1)
        for f in inv2.files:
            assert f.change_type == "unchanged"


def test_build_inventory_incremental_modified():
    with tempfile.TemporaryDirectory() as tmpdir:
        files1 = _create_files(tmpdir, [("a.py", "hello")])
        inv1 = build_file_inventory(files1, _EMPTY_META)
        files2 = _create_files(tmpdir, [("a.py", "modified")])
        inv2 = build_file_inventory(files2, _EMPTY_META, inv1)
        for f in inv2.files:
            assert f.change_type == "modified"


def test_build_inventory_incremental_added():
    with tempfile.TemporaryDirectory() as tmpdir:
        files1 = _create_files(tmpdir, [("a.py", "hello")])
        inv1 = build_file_inventory(files1, _EMPTY_META)
        files2 = _create_files(tmpdir, [("a.py", "hello"), ("b.py", "new")])
        inv2 = build_file_inventory(files2, _EMPTY_META, inv1)
        for f in inv2.files:
            if f.relative_path == "b.py":
                assert f.change_type == "added"


def test_build_inventory_incremental_removed():
    with tempfile.TemporaryDirectory() as tmpdir:
        files1 = _create_files(tmpdir, [("a.py", "hello"), ("b.py", "bye")])
        inv1 = build_file_inventory(files1, _EMPTY_META)
        files2 = _create_files(tmpdir, [("a.py", "hello")])
        inv2 = build_file_inventory(files2, _EMPTY_META, inv1)
        for f in inv2.files:
            assert f.change_type == "unchanged"


def test_build_inventory_categories_populated():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = _create_files(tmpdir, [
            ("src/main.py", "print(1)"),
            ("tests/test_main.py", "def test_x(): pass"),
            ("package.json", "{}"),
            ("README.md", "# Hello"),
        ])
        inv = build_file_inventory(files, _EMPTY_META)
        assert len(inv.categories.source) == 1
        assert "src/main.py" in inv.categories.source
        assert len(inv.categories.test) == 1
        assert "tests/test_main.py" in inv.categories.test
        assert len(inv.categories.config) == 1
        assert "package.json" in inv.categories.config
        assert len(inv.categories.documentation) == 1
        assert "README.md" in inv.categories.documentation
