from dna.graph.builder import build_dependency_graph, analyze_dependencies
from dna.models import (
    NormalizedFile, SymbolTable, ImportEntry, ExportEntry,
    FunctionDef, SymbolIndex, SymbolOccurrence,
)


def _make_nf(rel_path: str, imports=None, exports=None) -> NormalizedFile:
    return NormalizedFile(
        relative_path=rel_path,
        language="Python",
        symbols=SymbolTable(
            imports=imports or [],
            exports=exports or [],
        ),
    )


def test_empty_graph():
    graph = build_dependency_graph([], SymbolIndex())
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0


def test_single_file_no_deps():
    nf = _make_nf("main.py")
    si = SymbolIndex()
    graph = build_dependency_graph([nf], si)
    assert len(graph.nodes) == 1
    assert len(graph.edges) == 0


def test_import_edge():
    nf_main = _make_nf("main.py", imports=[ImportEntry(source="utils", names=["helper"], kind="import")])
    nf_utils = _make_nf("utils.py")
    si = SymbolIndex()
    graph = build_dependency_graph([nf_main, nf_utils], si)
    assert len(graph.nodes) >= 2
    main_deps = graph.get_dependencies("main.py")
    assert any(e.target == "utils.py" for e in main_deps)


def test_relative_import():
    nf_main = _make_nf("src/main.py", imports=[ImportEntry(source=".utils", names=["helper"], kind="from")])
    nf_utils = _make_nf("src/utils.py")
    si = SymbolIndex()
    graph = build_dependency_graph([nf_main, nf_utils], si)
    main_deps = graph.get_dependencies("src/main.py")
    dep_targets = [e.target for e in main_deps]
    assert "src/utils.py" in dep_targets


def test_symbol_reference_edge():
    nf = _make_nf("consumer.py", imports=[ImportEntry(source="", names=["helper"], kind="import")])
    si = SymbolIndex()
    si.add("helper", SymbolOccurrence(
        symbol_name="helper", kind="function",
        file_path="utils.py", line=1, role="definition",
    ))
    graph = build_dependency_graph([nf], si)
    consumer_deps = graph.get_dependencies("consumer.py")
    dep_targets = [e.target for e in consumer_deps]
    assert "utils.py" in dep_targets


def test_cycle_detection():
    nf_a = _make_nf("a.py", imports=[ImportEntry(source="b", names=[], kind="import")])
    nf_b = _make_nf("b.py", imports=[ImportEntry(source="a", names=[], kind="import")])
    si = SymbolIndex()
    graph = build_dependency_graph([nf_a, nf_b], si)
    cycles = graph.detect_cycles()
    assert len(cycles) >= 1


def test_analyze_dependencies():
    nf_main = _make_nf("main.py", imports=[ImportEntry(source="lib", names=[], kind="import")])
    nf_lib = _make_nf("lib.py")
    si = SymbolIndex()
    graph = build_dependency_graph([nf_main, nf_lib], si)
    analysis = analyze_dependencies(graph)
    assert analysis["total_nodes"] >= 2
    assert analysis["total_edges"] >= 1


def test_export_dependency_edge():
    nf_main = _make_nf("main.js", exports=[ExportEntry(source="./utils", kind="export")])
    nf_utils = _make_nf("utils.js")
    si = SymbolIndex()
    graph = build_dependency_graph([nf_main, nf_utils], si)
    assert len(graph.nodes) >= 2
    main_deps = graph.get_dependencies("main.js")
    assert any(e.target == "utils.js" and e.kind == "export" for e in main_deps)


def test_absolute_import_resolution():
    # Python stdlib
    nf_py = _make_nf("main.py", imports=[ImportEntry(source="os", names=[], kind="import")])
    si = SymbolIndex()
    graph_py = build_dependency_graph([nf_py], si)
    os_node = next((n for n in graph_py.nodes if n.name == "os"), None)
    assert os_node is not None
    assert os_node.kind == "external"

    # JS stdlib
    nf_js = _make_nf("main.js", imports=[ImportEntry(source="fs", names=[], kind="import")])
    graph_js = build_dependency_graph([nf_js], si)
    fs_node = next((n for n in graph_js.nodes if n.name == "fs"), None)
    assert fs_node is not None
    assert fs_node.kind == "external"

    # Absolute project import
    nf_app = _make_nf("backend/app.py", imports=[ImportEntry(source="dna.models", names=[], kind="import")])
    nf_models = _make_nf("backend/dna/models.py")
    graph_project = build_dependency_graph([nf_app, nf_models], si)
    app_deps = graph_project.get_dependencies("backend/app.py")
    assert any(e.target == "backend/dna/models.py" for e in app_deps)


def test_nodejs_module_resolution():
    # 1. node_modules resolution
    nf_main = _make_nf("src/main.js", imports=[ImportEntry(source="lodash", names=[], kind="import")])
    nf_lodash = _make_nf("node_modules/lodash/index.js")
    si = SymbolIndex()
    graph = build_dependency_graph([nf_main, nf_lodash], si)
    main_deps = graph.get_dependencies("src/main.js")
    assert any(e.target == "node_modules/lodash/index.js" for e in main_deps)

    # 2. nested node_modules resolution
    nf_nested = _make_nf("src/components/button.js", imports=[ImportEntry(source="react", names=[], kind="import")])
    nf_react = _make_nf("src/node_modules/react/index.js")
    graph_nested = build_dependency_graph([nf_nested, nf_react], si)
    nested_deps = graph_nested.get_dependencies("src/components/button.js")
    assert any(e.target == "src/node_modules/react/index.js" for e in nested_deps)

    # 3. index.js fallback in relative import
    nf_index_caller = _make_nf("src/app.js", imports=[ImportEntry(source="./utils", names=[], kind="import")])
    nf_index_file = _make_nf("src/utils/index.js")
    graph_index = build_dependency_graph([nf_index_caller, nf_index_file], si)
    index_deps = graph_index.get_dependencies("src/app.js")
    assert any(e.target == "src/utils/index.js" for e in index_deps)
