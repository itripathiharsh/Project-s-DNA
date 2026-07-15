# Sprint 03 — Repository Indexer

## Goal
Build a complete, classified, change-trackable file inventory from a repository scan. Output enables downstream AST parsing, dependency resolution, and metric calculation.

## Package
`backend/dna/indexer/`

## Data Models (in `backend/dna/models.py`)

### FileCategory (str Enum)
- `SOURCE`, `TEST`, `CONFIG`, `DOCUMENTATION`, `BUILD`, `DATA`, `OTHER`

### IndexedFile
Extends FileInfo with: `category: FileCategory`, `content_hash: str = ""`, `mtime: float = 0.0`, `change_type: str = "unchanged"`

### FileClassificationMap
Categories dict keyed by FileCategory

### FileInventory
- `files: list[IndexedFile]`, `categories: FileClassificationMap`, `total_files: int`, `total_size_bytes: int`

### DirectoryNode
- `name: str`, `path: str`, `children: list[DirectoryNode]`, `files: list[IndexedFile]`

### DirectoryTree
- `root: DirectoryNode`, `max_depth: int`, `total_dirs: int`

## Modules

### `classifier.py`
- `classify_file(file_info, repo_metadata) -> FileCategory` — rule-based by path, extension, naming
- `build_classification_map(files, repo_metadata) -> FileClassificationMap`

### `hasher.py`
- `compute_file_hash(path: str) -> str` — blake2b 16-byte hex
- `compute_file_hashes(files: list[FileInfo]) -> dict[str, str]`
- `detect_changes(old, new) -> dict[str, dict[str, str]]` — added/removed/modified/unchanged

### `tree.py`
- `build_directory_tree(files: list[IndexedFile]) -> DirectoryTree`

### `inventory.py`
- `build_file_inventory(files, repo_metadata) -> FileInventory`

### `orchestrator.py`
- `index_repository(path, repo_metadata) -> FileInventory`

### `errors.py`
- `IndexerError`, `FileReadError`

## Test Plan
- `test_classifier.py` — source, test, config, doc, build classification
- `test_hasher.py` — hash computation, change detection
- `test_tree.py` — build tree, empty tree
- `test_inventory.py` — full inventory build
- `test_orchestrator.py` — integration test with temp repo
