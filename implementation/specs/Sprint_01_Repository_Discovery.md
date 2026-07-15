# Sprint 01 — Repository Discovery

## Header

| Field | Value |
|---|---|
| **Sprint Number** | 01 |
| **Sprint Name** | Repository Discovery |
| **Phase** | Processing Pipeline — Stage 1 |
| **Priority** | Critical |
| **Estimated Effort** | 3 days |
| **Dependencies** | None (first sprint) |
| **Status** | In Progress |

## Sprint Goal

Implement the Repository Discovery stage — the entry point of the processing pipeline. This stage scans a local directory to determine repository type, detected languages, build systems, frameworks, and file structure. All subsequent stages depend on this metadata.

After this sprint, the system can accept a local path and produce a structured `RepositoryMetadata` object describing what kind of project it is.

## Objectives

1. Validate that a path points to a valid Git repository
2. Scan directory tree and classify files by extension → language
3. Detect build systems from known config files (package.json, Cargo.toml, etc.)
4. Detect frameworks from dependency manifests
5. Read `.gitignore` and `.dnaignore` patterns
6. Produce `RepositoryMetadata` with all collected information
7. Handle errors gracefully: invalid path, no Git repo, permission denied

## Out of Scope

- Git history mining (Sprint 02)
- File content parsing or AST generation (Sprint 04)
- Dependency resolution (Sprint 08)
- Any SCM storage writes (Sprint 10)
- Any engine execution (Sprint 12+)

## Architecture References

| Document | Section | Reason |
|---|---|---|
| Phase_2_System_Architecture.md | Layer 2: Processing Pipeline — Stage 1 | Defines Repository Discovery outputs |
| Phase_2_System_Architecture.md | Stage 2.1: Repository Discovery | Lists detection responsibilities |
| Phase_3_Software_Cognition_Model.md | Entity Taxonomy — Code Entities | Defines entity types this stage identifies |
| Phase_4_Cognitive_Engines.md | Engine Orchestration DAG | Shows RepositoryDiscovery at DAG root |
| Phase_8_03_Project_Structure.md | Monorepo Structure | Defines where code lives |

## Prerequisites

- Python 3.11+
- `py` available as Python launcher
- Git installed on system

## Requirements

### Functional

| ID | Requirement |
|---|---|
| F01 | Accept a local filesystem path as input |
| F02 | Return error if path does not exist |
| F03 | Return error if path is not a Git repository |
| F04 | Detect repository name from directory name |
| F05 | List all files in directory tree, excluding ignored paths |
| F06 | Classify each file by extension → language |
| F07 | Report language counts and primary language |
| F08 | Detect build system from known config files |
| F09 | Detect frameworks from dependency manifest contents |
| F10 | Read `.gitignore` patterns and apply them |
| F11 | Read `.dnaignore` patterns and apply them (if exists) |
| F12 | Return structured `RepositoryMetadata` |

### Non-Functional

| ID | Requirement |
|---|---|
| NF01 | Scan 10,000 files in < 5 seconds |
| NF02 | Memory usage < 100 MB for scanning |
| NF03 | All public functions have type annotations |
| NF04 | All errors are typed and documented |

## Implementation Plan

### Task R01-01: Project scaffolding

Set up Python package structure under `backend/dna/`.

**Acceptance criteria:**
- `backend/dna/__init__.py` exists
- `backend/dna/discovery/` package exists
- `backend/dna/models.py` exists
- `py -m pytest` works from repo root

### Task R01-02: Data models

Implement `RepositoryMetadata`, `FileInfo`, `Language`, `BuildSystem`, `Framework` types.

**Acceptance criteria:**
- All models are Pydantic or dataclass types with type annotations
- `RepositoryMetadata` includes: name, path, is_git, languages, primary_language, build_systems, frameworks, file_count, total_size_bytes
- Serialize to/from JSON

### Task R01-03: Git validation

Implement `is_git_repository(path)` that checks for `.git` directory.

**Acceptance criteria:**
- Returns `True` if `.git` exists
- Returns `False` if not
- Returns `False` if path doesn't exist

### Task R01-04: File scanning

Implement `scan_files(path, ignore_patterns)` that walks directory tree.

**Acceptance criteria:**
- Walks all subdirectories
- Skips `.git/` directory by default
- Applies ignore patterns from `.gitignore` and `.dnaignore`
- Returns list of `FileInfo` objects
- Handles permission errors gracefully

### Task R01-05: Language detection

Implement language detection from file extensions.

**Support matrix (V1):**

| Extension | Language |
|---|---|
| .py | Python |
| .js | JavaScript |
| .ts, .tsx | TypeScript |
| .jsx | JavaScript (React) |
| .java | Java |
| .go | Go |
| .rs | Rust |
| .c, .h | C |
| .cpp, .hpp, .cc | C++ |
| .rb | Ruby |
| .php | PHP |
| .swift | Swift |
| .kt, .kts | Kotlin |
| .rs | Rust |
| .md | Markdown |
| .json | JSON |
| .yaml, .yml | YAML |
| .toml | TOML |
| .sql | SQL |
| .css, .scss, .less | CSS |
| .html | HTML |
| .sh, .bash | Shell |
| .dockerfile, Dockerfile | Docker |
| .tf | Terraform |

**Acceptance criteria:**
- Maps extensions to languages
- Returns `Unknown` for unrecognized extensions
- Handles uppercase extensions

### Task R01-06: Build system detection

Detect build systems from config files at repository root.

| Config File | Build System |
|---|---|
| package.json | npm |
| Cargo.toml | Cargo |
| pom.xml | Maven |
| build.gradle | Gradle |
| requirements.txt, setup.py, pyproject.toml | pip / Poetry |
| go.mod | Go Modules |
| Cargo.toml | Cargo |
| Makefile | Make |
| Dockerfile | Docker |
| CMakeLists.txt | CMake |
| tsconfig.json | TypeScript |

**Acceptance criteria:**
- Scans root directory for known config files
- Returns list of detected build systems
- Handles multiple build systems in one project

### Task R01-07: Framework detection

Detect frameworks from dependency manifest contents (for V1: package.json and pyproject.toml).

**Acceptance criteria:**
- Parse package.json if present, detect frameworks from dependencies
- Parse pyproject.toml if present, detect frameworks from dependencies
- Default framework detection: React (react dependency), Vue (vue), Django (django), FastAPI (fastapi), Flask (flask), Next.js (next), Express (express)

### Task R01-08: Ignore pattern handling

Implement `.gitignore` and `.dnaignore` parsing.

**Acceptance criteria:**
- Parse standard `.gitignore` pattern format
- Parse `.dnaignore` with same format
- Apply patterns to file list
- Handle comments and blank lines in ignore files

### Task R01-09: Main discovery orchestrator

Implement `discover_repository(path)` that runs all steps and returns `RepositoryMetadata`.

**Acceptance criteria:**
- Calls all sub-steps in order
- Returns complete `RepositoryMetadata`
- Metrics collected: files scanned, scan duration, ignored files count

## File Changes

| File | Action | Purpose |
|---|---|---|
| `backend/dna/__init__.py` | Create | Package init |
| `backend/dna/models.py` | Create | Data models |
| `backend/dna/discovery/__init__.py` | Create | Discovery package |
| `backend/dna/discovery/scanner.py` | Create | File scanning |
| `backend/dna/discovery/languages.py` | Create | Language detection |
| `backend/dna/discovery/build_system.py` | Create | Build system detection |
| `backend/dna/discovery/frameworks.py` | Create | Framework detection |
| `backend/dna/discovery/ignore.py` | Create | Ignore pattern handling |
| `backend/dna/discovery/git.py` | Create | Git validation |
| `backend/dna/discovery/orchestrator.py` | Create | Main orchestrator |
| `tests/__init__.py` | Create | Test package |
| `tests/test_discovery/__init__.py` | Create | Discovery test package |
| `tests/test_discovery/test_scanner.py` | Create | Scanner tests |
| `tests/test_discovery/test_languages.py` | Create | Language detection tests |
| `tests/test_discovery/test_build_system.py` | Create | Build system tests |
| `tests/test_discovery/test_frameworks.py` | Create | Framework tests |
| `tests/test_discovery/test_ignore.py` | Create | Ignore pattern tests |
| `tests/test_discovery/test_git.py` | Create | Git validation tests |
| `tests/test_discovery/test_orchestrator.py` | Create | Orchestrator tests |
| `backend/requirements.txt` | Create | Python dependencies |
| `backend/pyproject.toml` | Create | Project configuration |
| `configs/.dnaignore` | Create | Default DNA ignore file |

## Interfaces

### Python Functions

```python
# models.py
@dataclass
class FileInfo:
    path: str
    relative_path: str
    filename: str
    extension: str
    language: str
    size_bytes: int
    is_directory: bool
    is_source: bool

@dataclass
class BuildSystem:
    name: str
    config_file: str
    version: str | None

@dataclass
class Framework:
    name: str
    category: str  # frontend, backend, testing, etc.
    confidence: float

@dataclass
class LanguageStats:
    language: str
    file_count: int
    total_bytes: int
    percentage: float

@dataclass
class RepositoryMetadata:
    name: str
    path: str
    is_git: bool
    languages: list[LanguageStats]
    primary_language: str | None
    build_systems: list[BuildSystem]
    frameworks: list[Framework]
    file_count: int
    total_size_bytes: int
    ignored_files_count: int
    scan_duration_ms: float
    has_dna_ignore: bool

# git.py
def is_git_repository(path: str) -> bool

# scanner.py
def scan_files(path: str, ignore_patterns: list[str] | None = None) -> list[FileInfo]

# languages.py
def detect_language(extension: str) -> str
def classify_files(files: list[FileInfo]) -> dict[str, LanguageStats]

# build_system.py
def detect_build_systems(path: str) -> list[BuildSystem]

# frameworks.py
def detect_frameworks(path: str, build_systems: list[BuildSystem]) -> list[Framework]

# ignore.py
def parse_gitignore(path: str) -> list[str]
def parse_dnaignore(path: str) -> list[str]
def should_ignore(file_path: str, patterns: list[str]) -> bool

# orchestrator.py
def discover_repository(path: str) -> RepositoryMetadata
```

## Data Models

### RepositoryMetadata JSON Schema

```json
{
    "name": "project-dna",
    "path": "/home/user/project-dna",
    "is_git": true,
    "languages": [
        {"language": "Python", "file_count": 45, "total_bytes": 125000, "percentage": 0.52},
        {"language": "TypeScript", "file_count": 28, "total_bytes": 89000, "percentage": 0.32}
    ],
    "primary_language": "Python",
    "build_systems": [
        {"name": "pip", "config_file": "pyproject.toml", "version": null}
    ],
    "frameworks": [
        {"name": "FastAPI", "category": "backend", "confidence": 1.0}
    ],
    "file_count": 73,
    "total_size_bytes": 214000,
    "ignored_files_count": 12,
    "scan_duration_ms": 1432,
    "has_dna_ignore": true
}
```

## Error Handling

| Error | Condition | Behavior |
|---|---|---|
| PathNotFoundError | Path does not exist | Raise with message, no retry |
| NotAGitRepositoryError | No `.git` directory | Raise with suggestion to init |
| PermissionDeniedError | Cannot read directory | Log warning, skip directory, continue |
| InvalidIgnorePatternError | Malformed `.gitignore` line | Log warning, skip pattern, continue |

## Testing Plan

### Unit Tests

| Test | Coverage |
|---|---|
| `test_is_git_repository_with_git_dir` | Validates true when `.git` exists |
| `test_is_git_repository_no_git` | Validates false when no `.git` |
| `test_is_git_repository_invalid_path` | Validates false for bad path |
| `test_scan_files_basic` | Scans a real directory, counts files |
| `test_scan_files_ignores_git` | `.git` directory excluded |
| `test_scan_files_apply_ignore` | Custom ignore patterns applied |
| `test_scan_files_permission_error` | Permission denied handled gracefully |
| `test_detect_language_known` | .py → Python, .ts → TypeScript, etc. |
| `test_detect_language_unknown` | .xyz → Unknown |
| `test_detect_language_case_insensitive` | .PY → Python |
| `test_classify_files_counts` | Correctly counts files by language |
| `test_detect_build_systems_python` | pyproject.toml → pip detected |
| `test_detect_build_systems_node` | package.json → npm detected |
| `test_detect_build_systems_none` | Empty dir → no build systems |
| `test_detect_frameworks_react` | package.json with react → React |
| `test_detect_frameworks_fastapi` | pyproject.toml with fastapi → FastAPI |
| `test_detect_frameworks_none` | No deps → no frameworks |
| `test_parse_gitignore_basic` | Standard patterns parsed correctly |
| `test_parse_gitignore_not_found` | Missing file → empty list |
| `test_should_ignore_match` | Path matches pattern |
| `test_should_ignore_no_match` | Path doesn't match pattern |
| `test_should_ignore_comment` | Comment lines ignored |
| `test_should_ignore_blank` | Blank lines ignored |
| `test_discover_repository_invalid_path` | PathNotFoundError raised |
| `test_discover_repository_complete` | Full discovery returns complete metadata |
| `test_discover_repository_metrics` | Scan duration and counts populated |

### Integration Tests

| Test | Coverage |
|---|---|
| `test_full_discovery_python_project` | Create temp Python project, run discovery, verify all fields |
| `test_full_discovery_node_project` | Create temp Node project, run discovery, verify all fields |
| `test_full_discovery_empty_dir` | Empty directory → discovered with no languages |

## Validation Checklist

- [ ] Architecture followed — outputs match Phase 2 Stage 1 spec
- [ ] All functional requirements satisfied (F01-F12)
- [ ] All non-functional requirements satisfied (NF01-NF04)
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Type annotations on all public functions
- [ ] Error types defined and documented
- [ ] No hardcoded paths
- [ ] No secrets

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Large repos with 100K+ files | Performance | Use generator-based walking, not loading all into memory |
| Permission denied on system files | Partial data | Log warning, skip unreadable paths |
| Git not installed | Feature unavailable | Detect git CLI, set `is_git = False` |

## Deliverables

- Source code: `backend/dna/discovery/*.py`
- Data models: `backend/dna/models.py`
- Tests: `tests/test_discovery/*.py`
- Configuration: `backend/pyproject.toml`, `backend/requirements.txt`, `configs/.dnaignore`
- Documentation: This specification

## Definition of Done

1. All tasks implemented
2. All tests pass
3. `py -m pytest tests/test_discovery/` exits 0
4. Cover ignored patterns, permission errors, unknown extensions
5. Works on Windows paths

## Future Sprints

This sprint enables:
- **Sprint 02** — Git History Engine: uses repository path and Git validation
- **Sprint 03** — Repository Indexer: uses file list for indexing
- **Sprint 04** — Tree-sitter Parser: uses language detection for parser selection
- **Sprint 05** — Language Registry: extends the language detection table
