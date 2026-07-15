import sys, os, tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from dna.parser.orchestrator import parse_repository
from dna.normalizer.orchestrator import normalize_parsed_files
from dna.models import FileInventory, IndexedFile, FileCategory

py_content = "def calculate(x):\n    return x + 1\n\nclass Calculator:\n    def run(self):\n        pass\n"
with tempfile.TemporaryDirectory() as tmp:
    py_path = os.path.join(tmp, 'main.py')
    with open(py_path, 'w') as f:
        f.write(py_content)
    inventory = FileInventory(files=[IndexedFile(path=py_path, relative_path='main.py', filename='main.py', extension='.py', language='Python', size_bytes=len(py_content), is_directory=False, is_source=True, category=FileCategory.SOURCE, content_hash='a')])
    parsed = parse_repository(inventory)
    normalized = normalize_parsed_files(parsed)
    for nf in normalized:
        print('Functions in symbols:')
        for f in nf.symbols.functions:
            print('  ', f.name, f.is_method)
