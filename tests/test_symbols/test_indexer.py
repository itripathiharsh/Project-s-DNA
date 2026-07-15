from dna.symbols.indexer import build_symbol_index, query_symbol
from dna.models import NormalizedFile, SymbolTable, FunctionDef, ClassDef, ImportEntry, ExportEntry


def _make_nf(rel_path: str, functions=None, classes=None, imports=None, exports=None) -> NormalizedFile:
    return NormalizedFile(
        relative_path=rel_path,
        language="Python",
        symbols=SymbolTable(
            functions=functions or [],
            classes=classes or [],
            imports=imports or [],
            exports=exports or [],
        ),
    )


def test_empty_index():
    index = build_symbol_index([])
    assert index.symbols == {}


def test_functions_indexed():
    nf = _make_nf("a.py", functions=[
        FunctionDef(name="hello", start_line=1, end_line=3),
        FunctionDef(name="world", start_line=5, end_line=7),
    ])
    index = build_symbol_index([nf])
    assert len(index.find("hello")) == 1
    assert index.find("hello")[0].role == "definition"
    assert index.find("hello")[0].file_path == "a.py"
    assert index.find("hello")[0].kind == "function"


def test_classes_indexed():
    nf = _make_nf("a.py", classes=[
        ClassDef(name="MyClass", methods=[
            FunctionDef(name="method1", start_line=2, end_line=4, is_method=True),
        ], start_line=1, end_line=5),
    ])
    index = build_symbol_index([nf])
    assert len(index.find("MyClass")) == 1
    assert len(index.find("MyClass.method1")) == 1


def test_imports_as_references():
    nf = _make_nf("a.py", imports=[
        ImportEntry(source="os", names=["os"], kind="import"),
        ImportEntry(source=".utils", names=["helper"], kind="from"),
    ])
    index = build_symbol_index([nf])
    os_occ = index.find("os")
    assert len(os_occ) >= 1
    assert all(o.role == "reference" for o in os_occ)
    assert index.find("helper") != []


def test_exports_as_definitions():
    nf = _make_nf("a.py", exports=[
        ExportEntry(name="hello", kind="export"),
    ])
    index = build_symbol_index([nf])
    assert len(index.find("hello")) == 1
    assert index.find("hello")[0].role == "definition"


def test_multiple_files():
    nf1 = _make_nf("a.py", functions=[FunctionDef(name="foo", start_line=1, end_line=2)])
    nf2 = _make_nf("b.py", functions=[FunctionDef(name="foo", start_line=3, end_line=4)])
    index = build_symbol_index([nf1, nf2])
    assert len(index.find("foo")) == 2


def test_query_symbol():
    nf = _make_nf("a.py", functions=[FunctionDef(name="foo", start_line=1, end_line=2)])
    index = build_symbol_index([nf])
    result = query_symbol(index, "foo")
    assert result["name"] == "foo"
    assert result["total_count"] == 1
    assert len(result["definitions"]) == 1
    assert result["references"] == []
