import os, sys, tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from dna.parser.orchestrator import parse_repository
from dna.normalizer.orchestrator import normalize_parsed_files
from dna.models import FileInventory, IndexedFile, FileCategory

py_content = "def calculate(x):\n    return x + 1\n\nclass Calculator:\n    def run(self):\n        pass\n"
js_content = "function formatName(name) {\n    return 'Name: ' + name;\n}\n"
with tempfile.TemporaryDirectory() as tmpdir:
    py_path = os.path.join(tmpdir, 'main.py')
    with open(py_path, 'w') as f:
        f.write(py_content)
    js_path = os.path.join(tmpdir, 'helper.js')
    with open(js_path, 'w') as f:
        f.write(js_content)
    inventory = FileInventory(files=[
        IndexedFile(path=py_path, relative_path='main.py', filename='main.py', extension='.py', language='Python', size_bytes=len(py_content), is_directory=False, is_source=True, category=FileCategory.SOURCE, content_hash='a'),
        IndexedFile(path=js_path, relative_path='helper.js', filename='helper.js', extension='.js', language='JavaScript', size_bytes=len(js_content), is_directory=False, is_source=True, category=FileCategory.SOURCE, content_hash='b')
    ])
    parsed = parse_repository(inventory)
    normalized = normalize_parsed_files(parsed)
    for nf in normalized:
        print('File', nf.relative_path)
        print('Functions in symbols (including methods):')
        for f in nf.symbols.functions:
            print('  func', f.name, 'is_method', f.is_method)
        for cls in nf.symbols.classes:
            print('Class', cls.name, 'methods count', len(cls.methods))
            for m in cls.methods:
                print('  method', m.name)
            # Print details of class children canonical nodes
            for child_canonical in []:
                pass
