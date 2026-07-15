import os
import tempfile
from dna.parser.ast_builder import parse_file
from dna.normalizer.orchestrator import normalize_parsed_files, normalize_file
from dna.models import ParsedFile, SymbolTable


def test_normalize_python_empty():
    result = normalize_file("test.py", "Python", b"")
    assert result.language == "Python"
    assert result.root.kind == "module"


def test_normalize_python_function():
    result = normalize_file("test.py", "Python", b"def hello():\n    pass\n")
    assert result.root.kind == "module"
    functions = [n for n in result.root.children if n.kind == "function"]
    assert len(functions) == 1
    assert functions[0].name == "hello"


def test_normalize_python_class():
    result = normalize_file("test.py", "Python",
                            b"class MyClass:\n    def method(self): pass\n")
    classes = [n for n in result.root.children if n.kind == "class"]
    assert len(classes) == 1
    assert classes[0].name == "MyClass"
    functions = [n for n in result.root.children if n.kind == "function"]
    assert len(functions) == 0  # methods are nested inside class, not at top level


def test_normalize_python_import():
    result = normalize_file("test.py", "Python", b"import os\nfrom pathlib import Path\n")
    imports = [n for n in result.root.children if n.kind == "import"]
    assert len(imports) == 2


def test_normalize_js_function():
    result = normalize_file("test.js", "JavaScript",
                            b"function greet(name) { return name; }")
    functions = [n for n in result.root.children if n.kind == "function"]
    assert len(functions) == 1
    assert functions[0].name == "greet"


def test_normalize_js_class():
    result = normalize_file("test.js", "JavaScript",
                            b"class Animal {\n  speak() { return ''; }\n}")
    classes = [n for n in result.root.children if n.kind == "class"]
    assert len(classes) == 1
    assert classes[0].name == "Animal"


def test_normalize_js_import():
    result = normalize_file("test.js", "JavaScript",
                            b'import {x} from "./foo";')
    imports = [n for n in result.root.children if n.kind == "import"]
    assert len(imports) == 1


def test_normalize_js_export():
    result = normalize_file("test.js", "JavaScript",
                            b"export function hello() {}")
    exports = [n for n in result.root.children if n.kind == "export"]
    assert len(exports) == 1
    assert exports[0].name == "hello"


def test_normalize_parsed_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        py_path = os.path.join(tmpdir, "a.py")
        js_path = os.path.join(tmpdir, "b.js")
        with open(py_path, "w") as f: f.write("def foo(): pass")
        with open(js_path, "w") as f: f.write("function bar() {}")
        py = parse_file(py_path, "Python")
        js = parse_file(js_path, "JavaScript")
        results = normalize_parsed_files([p for p in [py, js] if p])
        assert len(results) == 2
        langs = {r.language for r in results}
        assert langs == {"Python", "JavaScript"}


def test_normalize_parsed_files_no_disk_io():
    parsed = ParsedFile(
        file_path="mem.py",
        relative_path="mem.py",
        language="Python",
        content_hash="abc",
        source_bytes=b"def foo(): pass",
        symbols=SymbolTable(),
    )
    results = normalize_parsed_files([parsed])
    assert len(results) == 1
    assert results[0].language == "Python"
    assert results[0].relative_path == "mem.py"
    functions = [n for n in results[0].root.children if n.kind == "function"]
    assert len(functions) == 1
    assert functions[0].name == "foo"


def test_normalize_uses_cached_ast_tree(monkeypatch):
    from dna.parser.factory import get_parser
    parser = get_parser("Python")
    assert parser is not None
    tree = parser.parse(b"def foo(): pass")
    
    parsed = ParsedFile(
        file_path="mem.py",
        relative_path="mem.py",
        language="Python",
        content_hash="abc",
        source_bytes=b"def foo(): pass",
        ast_tree=tree,
        symbols=SymbolTable(),
    )
    
    called_get_parser = False
    def mock_get_parser(lang):
        nonlocal called_get_parser
        called_get_parser = True
        return parser
    
    monkeypatch.setattr("dna.normalizer.orchestrator.get_parser", mock_get_parser)
    
    results = normalize_parsed_files([parsed])
    assert not called_get_parser, "Should not call get_parser when ast_tree is provided"
    assert len(results) == 1
    functions = [n for n in results[0].root.children if n.kind == "function"]
    assert len(functions) == 1
    assert functions[0].name == "foo"


def test_normalize_typescript():
    source = """
interface User { id: number; }
enum Color { Red, Green }
type ID = string;
function main(): void {}
class Button {}
"""
    result = normalize_file("test.ts", "TypeScript", source.encode("utf-8"))
    assert result.language == "TypeScript"
    assert result.root.kind == "module"
    
    kinds = [n.kind for n in result.root.children]
    names = [n.name for n in result.root.children]
    
    assert "interface" in kinds
    assert "enum" in kinds
    assert "type_alias" in kinds
    assert "function" in kinds
    assert "class" in kinds
    
    assert "User" in names
    assert "Color" in names
    assert "ID" in names
    assert "main" in names
    assert "Button" in names


def test_normalize_js_arrow_function():
    source = "const double = (x) => x * 2;"
    result = normalize_file("test.js", "JavaScript", source.encode("utf-8"))
    functions = [n for n in result.root.children if n.kind == "function"]
    assert len(functions) == 1
    assert functions[0].name == "double"
    assert functions[0].metadata.get("arrow") == "true"
    assert functions[0].metadata.get("params") == "x"


def test_normalize_js_static_method():
    source = """
    class Utils {
        static format(val) { return val; }
    }
    """
    result = normalize_file("test.js", "JavaScript", source.encode("utf-8"))
    classes = [n for n in result.root.children if n.kind == "class"]
    assert len(classes) == 1
    class_node = classes[0]
    methods = [n for n in class_node.children if n.kind == "function"]
    assert len(methods) == 1
    assert methods[0].name == "format"
    assert methods[0].metadata.get("is_static") == "true"


def test_normalize_js_getter_setter():
    source = """
    class Person {
        get name() { return this._name; }
        set name(val) { this._name = val; }
    }
    """
    result = normalize_file("test.js", "JavaScript", source.encode("utf-8"))
    classes = [n for n in result.root.children if n.kind == "class"]
    assert len(classes) == 1
    class_node = classes[0]
    methods = [n for n in class_node.children if n.kind == "function"]
    assert len(methods) == 2
    names = [m.name for m in methods]
    assert names == ["name", "name"]
    
    getters = [m for m in methods if m.metadata.get("is_getter") == "true"]
    setters = [m for m in methods if m.metadata.get("is_setter") == "true"]
    assert len(getters) == 1
    assert len(setters) == 1


def test_normalize_js_export_default():
    source = "export default class App {}"
    result = normalize_file("test.js", "JavaScript", source.encode("utf-8"))
    exports = [n for n in result.root.children if n.kind == "export"]
    assert len(exports) == 1
    assert exports[0].metadata.get("default") == "true"
    assert exports[0].name == "App"

