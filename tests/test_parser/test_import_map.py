from dna.parser.import_map import build_import_map, resolve_imports
from dna.models import ParsedFile, SymbolTable, ImportEntry


def test_build_import_map_empty():
    assert build_import_map([]) == {}


def test_build_import_map_basic():
    pf = ParsedFile(
        relative_path="src/main.py",
        symbols=SymbolTable(imports=[
            ImportEntry(source="os", kind="import"),
            ImportEntry(source=".utils", kind="from"),
        ]),
    )
    result = build_import_map([pf])
    assert "src/main.py" in result
    assert len(result["src/main.py"]) == 2


def test_build_import_map_skips_no_imports():
    pf = ParsedFile(relative_path="main.py")
    result = build_import_map([pf])
    assert result == {}


def test_resolve_imports():
    imports = [
        ImportEntry(source=".utils", kind="from"),
    ]
    all_files = ["src/main.py", "src/utils.py"]
    resolved = resolve_imports("src/main.py", imports, all_files)
    assert "src/utils.py" in resolved
