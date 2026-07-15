from dna.graph.builder import build_dependency_graph
from dna.entities.builder import build_entity_graph
from dna.symbols.indexer import build_symbol_index
from dna.models import NormalizedFile, SymbolTable, FunctionDef, ClassDef, ImportEntry, SymbolIndex

def test_dependency_and_entity_graph_integration():
    # Setup NormalizedFiles for a dependency relationship
    # a.py defines class A and method foo
    nf_a = NormalizedFile(
        relative_path="a.py",
        language="Python",
        symbols=SymbolTable(
            functions=[],
            classes=[
                ClassDef(
                    name="A",
                    methods=[FunctionDef(name="foo", start_line=2, end_line=3, is_method=True)],
                    start_line=1,
                    end_line=4
                )
            ],
            imports=[],
            exports=[]
        )
    )
    
    # b.py imports class A from a.py and defines class B extending A
    nf_b = NormalizedFile(
        relative_path="b.py",
        language="Python",
        symbols=SymbolTable(
            functions=[],
            classes=[
                ClassDef(
                    name="B",
                    methods=[],
                    start_line=2,
                    end_line=3,
                    bases=["A"] # extends A
                )
            ],
            imports=[
                ImportEntry(source="a", names=["A"], kind="from")
            ],
            exports=[]
        )
    )
    
    normalized_files = [nf_a, nf_b]
    
    # 1. Build symbol index
    symbol_index = build_symbol_index(normalized_files)
    
    # 2. Build dependency graph
    dep_graph = build_dependency_graph(normalized_files, symbol_index)
    assert dep_graph is not None
    # We should have a dependency edge from b.py to a.py
    edges = [(e.source, e.target) for e in dep_graph.edges]
    assert ("b.py", "a.py") in edges
    
    # 3. Build entity graph
    entity_graph = build_entity_graph(normalized_files, symbol_index, dep_graph)
    assert entity_graph is not None
    
    # Verify entity graph nodes
    files = entity_graph.query(kind="file")
    assert len(files) == 2
    assert {f.name for f in files} == {"a.py", "b.py"}
    
    classes = entity_graph.query(kind="class")
    assert len(classes) == 2
    assert {c.name for c in classes} == {"A", "B"}
    
    # Verify relationships (extends)
    relations = entity_graph.relations
    extends_relations = [r for r in relations if r.kind == "EXTENDS"]
    assert len(extends_relations) >= 1
    # B extends A
    b_uid = [c.uid for c in classes if c.name == "B"][0]
    a_uid = [c.uid for c in classes if c.name == "A"][0]
    
    # Verify that there exists an EXTENDS relationship from B to A
    found_extends = False
    for r in extends_relations:
        if r.source_uid == b_uid and r.target_uid == a_uid:
            found_extends = True
            break
    assert found_extends, "EXTENDS relation from B to A not found"
