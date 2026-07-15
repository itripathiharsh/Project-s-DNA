# Sprint 04 — Tree-sitter Parser

## Goal
Parse source code into structured ASTs using tree-sitter, extract symbols (functions, classes, imports), and build per-file symbol tables and cross-file import maps.

## Dependencies
- `tree-sitter` (installed), `tree-sitter-python`, `tree-sitter-javascript`, `tree-sitter-typescript`
- Sprint 03 `FileInventory` (source files to parse)

## Package
`backend/dna/parser/`

## Data Models (in `backend/dna/models.py`)

### ParsedFile
- `file_path: str | None` — original file path
- `relative_path: str | None` — relative path
- `language: str | None` — language name
- `content_hash: str` — hash for caching
- `symbols: SymbolTable` — extracted symbols

### SymbolTable
- `functions: list[FunctionDef]`
- `classes: list[ClassDef]`
- `imports: list[ImportEntry]`
- `exports: list[ExportEntry]`

### FunctionDef
- `name: str`, `params: list[str]`, `start_line: int`, `end_line: int`, `is_method: bool = False`

### ClassDef
- `name: str`, `methods: list[FunctionDef]`, `base_classes: list[str]`, `start_line: int`, `end_line: int`

### ImportEntry
- `source: str`, `names: list[str]`, `kind: str = "import"` (import / require / include)

### ExportEntry
- `name: str`, `kind: str = "export"`

## Modules

### `factory.py`
- `get_parser(language: str) -> Parser | None` — returns tree-sitter Parser for supported languages
- `SUPPORTED_LANGUAGES: set[str]`

### `ast_builder.py`
- `parse_file(file_path, language) -> ParsedFile | None` — parse single file with tree-sitter
- `parse_source(source, language) -> ParsedFile | None` — parse source string

### `traverser.py`
- `extract_symbols(root_node, source_bytes) -> SymbolTable` — walk CST, extract functions/classes/imports
- `_extract_python_symbols`, `_extract_js_symbols` — language-specific traversal

### `import_map.py`
- `build_import_map(parsed_files: list[ParsedFile]) -> dict[str, list[ImportEntry]]`
- `resolve_imports(path: str, imports: list[ImportEntry], all_files: list[str]) -> list[str]`

### `orchestrator.py`
- `parse_repository(inventory: FileInventory) -> list[ParsedFile]`
- Filters to SOURCE files, groups by language, parses in parallel

### `errors.py`
- `ParserError`, `UnsupportedLanguageError`, `ParseError`

## Test Plan
- `test_factory.py` — get_parser for supported/unsupported languages
- `test_ast_builder.py` — parse Python file, parse JS file, parse errors
- `test_traverser.py` — extract symbols from Python, from JS
- `test_import_map.py` — build import map
- `test_orchestrator.py` — full parse of temp repo
