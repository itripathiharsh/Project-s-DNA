from dna.parser.ast_builder import parse_source
from dna.engines.structural import analyze_structure
from dna.entities.builder import build_entity_graph
from dna.models import SymbolIndex


def test_python_complexity():
    source = """
def hello():
    pass
"""
    result = parse_source(source, "Python")
    assert result is not None
    assert result.symbols.functions[0].complexity == 1

    source = """
def check(x):
    if x > 0 and x < 10:
        return True
    return False
"""
    result = parse_source(source, "Python")
    assert result is not None
    assert result.symbols.functions[0].complexity == 3


def test_go_complexity():
    source = """
package main
func process(x int) int {
    if x > 0 {
        return 1
    }
    switch x {
    case 1:
        return 2
    case 2:
        return 3
    }
    return 0
}
"""
    result = parse_source(source, "Go")
    assert result is not None
    assert result.symbols.functions[0].complexity == 4


def test_rust_complexity():
    source = """
fn run(x: i32) {
    match x {
        1 => println!("one"),
        _ => println!("other"),
    }
    loop {
        break;
    }
}
"""
    result = parse_source(source, "Rust")
    assert result is not None
    assert result.symbols.functions[0].complexity == 4


def test_structural_complexity_metrics():
    source_py = """
def f1(x):
    if x > 0:
        return 1
    return 0

def f2(x):
    return x
"""
    parsed = parse_source(source_py, "Python")
    assert parsed is not None
    parsed.relative_path = "f1.py"
    parsed.file_path = "f1.py"

    symbol_index = SymbolIndex()
    graph = build_entity_graph([parsed], symbol_index)

    result = analyze_structure(graph)
    assert result["total_functions"] == 2
    assert result["max_complexity"] == 2
    assert result["avg_complexity"] == 1.5
