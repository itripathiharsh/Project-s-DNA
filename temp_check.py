import os, json, tempfile
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from dna.parser.orchestrator import parse_repository
from dna.parser.factory import is_language_supported
from dna.models import FileInventory, IndexedFile, FileCategory
from dna.normalizer.orchestrator import normalize_parsed_files
from dna.symbols.indexer import build_symbol_index

# create temp files
import textwrap, pathlib
tmp_dir = tempfile.mkdtemp()
py_path = os.path.join(tmp_dir, 'main.py')
with open(py_path, 'w') as f:
    f.write(textwrap.dedent('''
    def calculate(x):
        return x+1
    
    class Calculator:
        def run(self):
            pass
    '''))

# Build inventory manually
files = []
files.append(IndexedFile(
    path=py_path,
    relative_path='main.py',
    filename='main.py',
    extension='.py',
    language='Python',
    size_bytes=os.path.getsize(py_path),
    is_directory=False,
    is_source=True,
    category=FileCategory.SOURCE,
    content_hash='hash',
))
inventory = FileInventory(files=files)
parsed = parse_repository(inventory)
normalized = normalize_parsed_files(parsed)
index = build_symbol_index(normalized)
print('class_defs:', [occ for occ in index.find('Calculator')])
print('functions in symbols:', normalized[0].symbols.functions)
print('methods:', [occ for occ in index.find('Calculator.run')])
