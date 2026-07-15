from dna.entities.builder import build_entity_graph
from dna.models import (
    NormalizedFile, SymbolTable, FunctionDef, ClassDef,
    ImportEntry, ExportEntry, SymbolIndex, SymbolOccurrence,
    DependencyGraph, DependencyEdge,
)


def _make_nf(rel_path: str, functions=None, classes=None, imports=None) -> NormalizedFile:
    return NormalizedFile(
        relative_path=rel_path,
        language="Python",
        symbols=SymbolTable(
            functions=functions or [],
            classes=classes or [],
            imports=imports or [],
        ),
    )


def test_empty_graph():
    graph = build_entity_graph([], SymbolIndex())
    assert len(graph.entities) == 0
    assert len(graph.relations) == 0


def test_file_entity():
    nf = _make_nf("main.py")
    graph = build_entity_graph([nf], SymbolIndex())
    entities = graph.query(kind="file")
    assert len(entities) == 1
    assert entities[0].name == "main.py"


def test_function_entity():
    nf = _make_nf("main.py", functions=[FunctionDef(name="hello", start_line=1, end_line=3)])
    graph = build_entity_graph([nf], SymbolIndex())
    funcs = graph.query(kind="function")
    assert len(funcs) == 1
    assert funcs[0].name == "hello"


def test_class_entity_with_method():
    nf = _make_nf("app.py", classes=[ClassDef(
        name="MyClass",
        methods=[FunctionDef(name="method1", start_line=2, end_line=4, is_method=True)],
        start_line=1, end_line=5,
    )])
    graph = build_entity_graph([nf], SymbolIndex())
    classes = graph.query(kind="class")
    assert len(classes) == 1
    funcs = graph.query(kind="function")
    assert len(funcs) == 1
    assert funcs[0].name == "method1"


def test_import_entity():
    nf = _make_nf("main.py", imports=[ImportEntry(source="os", names=["os"], kind="import")])
    graph = build_entity_graph([nf], SymbolIndex())
    imports = graph.query(kind="import")
    assert len(imports) == 1
    assert imports[0].name == "os"


def test_contains_relation():
    nf = _make_nf("main.py", functions=[FunctionDef(name="foo", start_line=1, end_line=2)])
    graph = build_entity_graph([nf], SymbolIndex())
    file_uid = "file:main.py"
    func_uid = "function:main.py:foo"
    relations = graph.get_relations(file_uid)
    contains = [r for r in relations if r.kind == "CONTAINS"]
    assert len(contains) == 1
    assert contains[0].target_uid == func_uid


def test_depends_on_relation():
    si = SymbolIndex()
    si.add("helper", SymbolOccurrence(
        symbol_name="helper", kind="function",
        file_path="utils.py", line=1, role="definition",
    ))
    si.add("helper", SymbolOccurrence(
        symbol_name="helper", kind="function",
        file_path="main.py", line=0, role="reference",
    ))
    nf_main = _make_nf("main.py", imports=[ImportEntry(source="", names=["helper"], kind="import")])
    nf_utils = _make_nf("utils.py")
    graph = build_entity_graph([nf_main, nf_utils], si)
    file_relations = graph.get_relations("file:main.py")
    depends = [r for r in file_relations if r.kind == "DEPENDS_ON"]
    assert len(depends) >= 1


def test_imports_from_dep_graph():
    nf_a = _make_nf("a.py", imports=[ImportEntry(source="b", names=[], kind="import")])
    nf_b = _make_nf("b.py")
    si = SymbolIndex()
    dg = DependencyGraph()
    dg.add_edge(DependencyEdge(source="a.py", target="b.py", kind="import"))
    graph = build_entity_graph([nf_a, nf_b], si, dg)
    relations = graph.get_relations("file:a.py")
    imports_rel = [r for r in relations if r.kind == "IMPORTS"]
    assert len(imports_rel) == 1
    assert imports_rel[0].target_uid == "file:b.py"


def test_calls_relations():
    # caller in main.py calls helper in utils.py
    nf_main = _make_nf("main.py", functions=[
        FunctionDef(name="caller", start_line=1, end_line=5, calls=["helper"])
    ])
    nf_utils = _make_nf("utils.py", functions=[
        FunctionDef(name="helper", start_line=1, end_line=3)
    ])
    
    si = SymbolIndex()
    si.add("helper", SymbolOccurrence(
        symbol_name="helper", kind="function",
        file_path="utils.py", line=1, role="definition"
    ))
    
    graph = build_entity_graph([nf_main, nf_utils], si)
    
    # We should have function:main.py:caller entity
    caller_uid = "function:main.py:caller"
    helper_uid = "function:utils.py:helper"
    
    caller_entity = graph.get_entity(caller_uid)
    helper_entity = graph.get_entity(helper_uid)
    assert caller_entity is not None
    assert helper_entity is not None
    
    relations = graph.get_relations(caller_uid)
    calls_rels = [r for r in relations if r.kind == "CALLS"]
    assert len(calls_rels) == 1
    assert calls_rels[0].target_uid == helper_uid


def test_extends_relations():
    # SubClass extends BaseClass
    nf_base = _make_nf("base.py", classes=[
        ClassDef(name="BaseClass", start_line=1, end_line=10)
    ])
    nf_sub = _make_nf("sub.py", classes=[
        ClassDef(name="SubClass", base_classes=["BaseClass"], start_line=1, end_line=10)
    ])
    
    si = SymbolIndex()
    si.add("BaseClass", SymbolOccurrence(
        symbol_name="BaseClass", kind="class",
        file_path="base.py", line=1, role="definition"
    ))
    
    graph = build_entity_graph([nf_base, nf_sub], si)
    
    sub_uid = "class:sub.py:SubClass"
    base_uid = "class:base.py:BaseClass"
    
    sub_entity = graph.get_entity(sub_uid)
    base_entity = graph.get_entity(base_uid)
    assert sub_entity is not None
    assert base_entity is not None
    
    relations = graph.get_relations(sub_uid)
    extends_rels = [r for r in relations if r.kind == "EXTENDS"]
    assert len(extends_rels) == 1
    assert extends_rels[0].target_uid == base_uid

