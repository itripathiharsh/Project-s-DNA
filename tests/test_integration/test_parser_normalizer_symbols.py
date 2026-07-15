import os
import tempfile
from dna.parser.orchestrator import parse_repository
from dna.normalizer.orchestrator import normalize_parsed_files
from dna.symbols.indexer import build_symbol_index
from dna.models import FileInventory, IndexedFile, FileCategory

def test_parser_normalizer_symbols_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files
        file_py = os.path.join(tmpdir, "main.py")
        file_js = os.path.join(tmpdir, "helper.js")
        
        py_content = "def calculate(x):\n    return x + 1\n\nclass Calculator:\n    def run(self):\n        pass\n"
        js_content = "function formatName(name) {\n    return 'Name: ' + name;\n}\n"
        
        with open(file_py, "w") as f:
            f.write(py_content)
            
        with open(file_js, "w") as f:
            f.write(js_content)
            
        # Create a mock FileInventory
        inventory = FileInventory(
            files=[
                IndexedFile(
                    path=file_py,
                    relative_path="main.py",
                    filename="main.py",
                    extension=".py",
                    language="Python",
                    size_bytes=len(py_content),
                    is_directory=False,
                    is_source=True,
                    category=FileCategory.SOURCE,
                    content_hash="a",
                ),
                IndexedFile(
                    path=file_js,
                    relative_path="helper.js",
                    filename="helper.js",
                    extension=".js",
                    language="JavaScript",
                    size_bytes=len(js_content),
                    is_directory=False,
                    is_source=True,
                    category=FileCategory.SOURCE,
                    content_hash="b",
                )
            ]
        )
        
        # 1. Parse repository
        parsed_files = parse_repository(inventory)
        assert len(parsed_files) == 2
        
        # 2. Normalize parsed files
        normalized_files = normalize_parsed_files(parsed_files)
        assert len(normalized_files) == 2
        
        # 3. Build symbol index
        symbol_index = build_symbol_index(normalized_files)
        assert symbol_index is not None
        
        # Verify definitions are found
        calc_defs = symbol_index.find("calculate")
        assert len(calc_defs) == 1
        assert calc_defs[0].file_path == "main.py"
        assert calc_defs[0].kind == "function"
        
        class_defs = symbol_index.find("Calculator")
        assert len(class_defs) == 1
        assert class_defs[0].file_path == "main.py"
        assert class_defs[0].kind == "class"
        
        method_defs = symbol_index.find("Calculator.run")
        assert len(method_defs) == 1
        
        fn_defs = symbol_index.find("formatName")
        assert len(fn_defs) == 1
        assert fn_defs[0].file_path == "helper.js"
        assert fn_defs[0].kind == "function"
