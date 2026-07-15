# Sprint-by-Sprint Detailed Report

**Source:** Code audit + architecture document analysis  
**Method:** Every claim verified against actual source code

---

## Sprint 1 — Repository Discovery

### Planned Scope
- Walk repository directory, detect files, detect git status, parse `.gitignore`/`.dnaignore`, detect languages, detect build systems, detect frameworks, classify files, produce `RepositoryMetadata`.

### Actual Implementation
**Files:** `backend/dna/discovery/scanner.py`, `ignore.py`, `git.py`, `languages.py`, `build_system.py`, `frameworks.py`, `orchestrator.py`

**What exists:**
- `scan_files()`: `os.walk`-based file scanner with `ALWAYS_IGNORE` set
- `is_git_repository()`: checks for `.git` directory
- `parse_gitignore()`/`parse_dnaignore()`: reads lines, returns patterns
- `should_ignore()`: fnmatch-based pattern matching
- `detect_language()`: extension-to-language map (32 entries)
- `is_source_file()`: extension set for 17 source types
- `classify_files()`: language statistics aggregation
- `detect_build_systems()`: config-file name matching (23 entries)
- `detect_frameworks()`: regex search of `package.json` + `pyproject.toml`
- `discover_repository()`: orchestrator

### Missing Implementation
- `.gitignore` pattern syntax: no `**`, no negation `!`, no directory-only `pattern/` for content patterns
- No `fnmatch.translate` or `pathlib` usage — manual fnmatch
- Framework detection only checks 2/23+ config file types
- Build system detection only checks root directory
- `_count_visible_files()` only ignores `.git`, not other ALWAYS_IGNORE dirs
- No symlink handling or detection
- No file encoding detection
- No large-file size threshold
- No `.gitmodules` detection

### Broken Implementation
- `_count_visible_files()` at `orchestrator.py:35` has `except OSError: pass` — silently swallows errors

### Fake Implementation
- None identified — this sprint's code is straightforward and functional within its scope

### Technical Debt
- No error propagation from scanner (all errors caught silently)
- No logging
- No configurable ignore patterns (ALWAYS_IGNORE is hardcoded)

### Test Quality (59 tests)
- Good: covers scanner, ignore parsing, git detection, language detection, build systems, frameworks
- Weak: tests use single-file scenarios; no real directory trees tested
- Missing: no symlink tests, no encoding tests, no large-file tests
- `test_scanner_edge.py` exists with edge case tests

### Development Effort to Complete
- Small improvements: 3-5 days
- Full `.gitignore` standard compliance: 3-5 days

---

## Sprint 2 — Git History Engine

### Planned Scope
- Parse git commit history, extract branches, tags, authors, diffs. Support blame, merge analysis, conventional commits.

### Actual Implementation
**Files:** `backend/dna/git_history/miner.py`, `commit_parser.py`, `diff_analyzer.py`, `author_analyzer.py`, `branch_detector.py`, `tag_mapper.py`, `errors.py`

**What exists:**
- Streaming `git log` parser with 9+ fields per commit
- Branch detection via `git branch -a`
- Tag mapping via `git tag -l`
- Author statistics (commit count, insertions, deletions, first/last commit)
- Commit categorization (6 categories based on first-word keyword)
- File change extraction via `git diff-tree --numstat`
- Raw diff output via `git diff-tree -p`
- Merge commit detection (counts parents > 1)

### Missing Implementation
- No `git blame` support
- No per-file change frequency tracking (file_change_counts dict)
- `categorize_commit()` only checks first word — misses `feat(core):` format
- No structured commit diff analysis (patch-level parsing)
- No refactoring detection
- No temporal analysis (per-week/month grouping)

### Broken Implementation
- None identified — streaming parser, branch detector, and tag mapper work correctly

### Fake Implementation
- None identified — the engine is honest about what it does

### Technical Debt
- No caching of parsed commits (re-parses every analysis)
- No streaming progress reporting

### Test Quality (31 tests)
- Good: commit parsing, author analysis, branch detection, tag mapping all covered
- Tests use inline text, not real git output
- Missing: no real git repo tests, no conventional commit tests, no merge commit tests

### Development Effort to Complete
- Add per-file tracking: 2-3 days
- Add blame support: 2-3 days
- Improve categorization: 1 day
- Full completion: 5-8 days

---

## Sprint 3 — Repository Indexer

### Planned Scope
- Classify files by category (source, test, config, build, doc, data), hash file contents, build inventory, detect changes, build directory tree.

### Actual Implementation
**Files:** `backend/dna/indexer/classifier.py`, `hasher.py`, `inventory.py`, `orchestrator.py`, `tree.py`, `errors.py`

**What exists:**
- `classify_file()` — 7 categories with test-dir, test-prefix, config-filename, build-filename, doc-extension rules
- `build_classification_map()` — returns `FileClassificationMap`
- `compute_file_hash()` — BLAKE2b streaming hash
- `detect_changes()` — three-way diff of hash dicts
- `build_file_inventory()` — `IndexedFile` creation with hashing
- `build_directory_tree()` — tree from `IndexedFile` list
- `index_repository()` — orchestrator combining scan + inventory

### Missing Implementation
- `FileInventory.categories` is NEVER populated — `build_file_inventory()` ignores the classification map
- `DirectoryTree` is built but never used in pipeline
- No incremental scan support

### Broken Implementation
- **BLD-014**: `FileInventory.categories` always empty. This is a structural defect — every downstream engine that queries file categories gets empty data.

### Fake Implementation
- None identified — the bug is an omission, not a deliberate fake

### Technical Debt
- `build_directory_tree()` is dead code (never called)
- Empty classification map downstream

### Test Quality (32 tests)
- Good: classifier edge cases (test dirs, prefixes, config filenames, doc extensions), hasher determinism, inventory building
- Missing: no test that verifies `FileInventory.categories` is populated
- Missing: no `DirectoryTree` integration test

### Development Effort to Complete
- Fix population bug: 1 hour
- Integrate DirectoryTree: 1 day
- Add incremental indexing: 3-5 days

---

## Sprint 4 — Tree-sitter Parser

### Planned Scope
- Parse all source files with Tree-sitter, extract AST nodes (functions, classes, imports, exports), support multiple languages.

### Actual Implementation
**Files:** `backend/dna/parser/ast_builder.py`, `orchestrator.py`, `traverser.py`, `factory.py`, `registry.py`, `errors.py`

**What exists:**
- `parse_file()` — single-file Tree-sitter parsing
- `parse_repository()` — threaded bulk parsing (max_workers=4)
- `extract_symbols()` — Python + JS tree traversal
- `build_import_map()` / `resolve_imports()` — basic import resolution
- Language registry with Python, JavaScript, TypeScript
- Custom error hierarchy (ParserError, UnsupportedLanguageError, ParseError)

### Missing Implementation
- TypeScript uses JavaScript grammar — no TS-specific parsing
- Only 3/17 source languages supported by parser
- `extract_symbols()` silently returns empty SymbolTable for unsupported languages
- No source text stored in ParsedFile (only symbols)
- Tree-sitter queries defined but never used

### Broken Implementation
- None critical — parser works for covered languages

### Fake Implementation
- `_safe_parse()` at `orchestrator.py:39-43`: silently catches all ParserError exceptions and returns None. Parse failures are invisible.
- `extract_symbols()` at `traverser.py:9`: returns empty `SymbolTable()` for unsupported languages — no warning, no error.

### Technical Debt
- Thread pool hardcoded to 4 workers
- No source text caching
- TypeScript queries defined but unused

### Test Quality (25 tests)
- Good: Python/JS function, class, import extraction; registry singleton; factory methods
- Tests use inline source strings, not real files
- Missing: no TypeScript-specific tests, no real-file parse tests, no error-handling tests

### Development Effort to Complete
- Add TypeScript grammar: 1-2 days
- Add 5 more languages: 5-10 days
- Fix error reporting: 1 day
- Add source text storage: 1 day

---

## Sprint 5 — Language Registry

### Planned Scope
- Register/deregister languages, dynamic parser loading, extension mapping, hot-reload.

### Actual Implementation
**Files:** `backend/dna/parser/registry.py`

**What exists:**
- Singleton LanguageRegistry with Python/JS/TS defaults
- `register()`, `unregister()`, `get_language()`, `get_by_extension()`, `get_parser()`, `get_all_languages()`, `is_supported()`
- Dynamic import of tree-sitter modules at runtime

### Missing Implementation
- Only 3 languages configured
- No dynamic grammar download
- No hot-reload mechanism

### Broken Implementation
- `get_parser()` at `registry.py:90`: `except (ImportError, AttributeError): return None` — silently fails to load grammar; no error logged

### Fake Implementation
- None — the registry is correctly implemented for its limited scope

### Technical Debt
- `_DEFAULT_LANGUAGES` hardcoded list
- No grammar version checking
- No validation that installed grammars match expected APIs

### Test Quality (12 tests)
- Good: singleton pattern, register/unregister, extension mapping, language listing
- Tests verify parser creation via module import
- Missing: no tests for dynamic download, no hot-reload tests

### Development Effort to Complete
- Implement grammar auto-download: 3-5 days
- Add hot-reload: 2-3 days
- Add language config files: 1-2 days

---

## Sprint 6 — AST Normalization

### Planned Scope
- Convert language-specific AST to canonical form, cross-language normalization, re-extract symbols from canonical form.

### Actual Implementation
**Files:** `backend/dna/normalizer/orchestrator.py`, `python_normalizer.py`, `js_normalizer.py`

**What exists:**
- `normalize_parsed_files()` — batch normalization
- `normalize_python()` — CST-to-CanonicalNode conversion for Python
- `normalize_javascript()` — CST-to-CanonicalNode conversion for JS
- `_extract_symbols_from_canonical()` — re-extract FunctionDef/ClassDef/ImportEntry/ExportEntry from canonical tree

### Missing Implementation
- No TypeScript-specific normalizer (falls through to JS normalizer — same bug as parser)
- JS normalizer doesn't handle: arrow functions on object properties, static methods, getters/setters, async/await, export default
- No cross-language normalization

### Broken Implementation
- **BLD-024 (Critical)**: Normalizer reads every file from disk and re-parses it with Tree-sitter. This completely duplicates the Parser (Sprint 4). Files are read twice, parsed twice, wasting 100% of the parsing time.
  - `_normalize_single()` at `orchestrator.py:56-64`: opens file, reads bytes, calls `parser.parse()`
  - Same code in `normalize_file()` at `orchestrator.py:23-26`
  - This doubles analysis time and makes the normalizer an architectural dead end

### Fake Implementation
- `_normalize_single()` at `orchestrator.py:48-84`: five `return None` fallback paths that silently return None for any error condition

### Technical Debt
- Re-parsing means normalization is not composable — can't pipe from parser
- 9 tests only — lowest coverage of any package

### Test Quality (9 tests)
- Minimal: tests Python empty file, single function, class, import; JS function, class, import, export
- Missing: no normalizer integration test, no re-parsing issue caught
- Missing: no TS normalizer tests, no edge cases

### Development Effort to Complete
- Fix re-parsing to accept parser output: 1-2 days
- Add TypeScript normalizer: 2-3 days
- Fix JS gaps: 2-3 days
- Add cross-language normalization: 5-10 days

---

## Sprint 7 — Symbol Extraction

### Planned Scope
- Build symbol index with definitions and references across files, resolve cross-file references, support scope/namespace awareness.

### Actual Implementation
**Files:** `backend/dna/symbols/indexer.py`

**What exists:**
- `build_symbol_index()` — creates SymbolIndex from NormalizedFile list
- `query_symbol()` — lookup by name with def/ref split
- `_resolve_relative_import()` — dot-path resolution
- SymbolOccurrence with kind, file_path, line, role

### Missing Implementation
- **No cross-file resolution**: symbols are grouped by name string only; `foo` in module A and `foo` in module B are treated as same symbol
- No scope/namespace awareness
- Import line numbers are always 0
- No symbol renaming API

### Broken Implementation
- Import line numbers at `indexer.py:42,51,64`: `line=0` hardcoded for imports; should be extracted from AST

### Fake Implementation
- None — the index honestly records what it finds, it just doesn't resolve across files

### Technical Debt
- No qualified name resolution
- No type resolution

### Test Quality (7 tests)
- Thin: empty index, functions, classes, imports, exports, multiple files, query
- Missing: no cross-file resolution tests, no scope tests

### Development Effort to Complete
- Add cross-file resolution: 3-5 days
- Add namespace awareness: 2-3 days
- Fix line tracking: 1 day

---

## Sprint 8 — Dependency Graph

### Planned Scope
- Build dependency graph from imports/exports, resolve import targets, detect cycles, analyze fan-in/fan-out.

### Actual Implementation
**Files:** `backend/dna/graph/builder.py`

**What exists:**
- `build_dependency_graph()` — DependencyGraph from NormalizedFile + SymbolIndex
- `_resolve_import_target()` — candidate-based file resolution with 7 fallback patterns
- `analyze_dependencies()` — fan-in, fan-out top 10, cycle detection
- `DependencyGraph.detect_cycles()` — DFS-based cycle detection
- Dependency edges with source, target, kind, weight

### Missing Implementation
- No export propagation (exports loop is empty)
- No absolute import resolution
- No Node.js module resolution
- No type-based dependency edges (function A calls function B)

### Broken Implementation
- **BLD-031 (Critical)**: `for exp in nf.symbols.exports: pass` at `builder.py:40` — the exports loop is completely empty. Exports generate zero dependency edges. This means for JS/TS modules that export symbols, the dependency graph has no edges from the export to its target.
- **BLD-032 (Critical)**: `_resolve_import_target()` at `builder.py:45-82` only handles dot-relative imports (starting with `.`). Absolute imports like `from typing import List` or `import os` or `from django.db import models` all return None at line 82. The entire dependency graph for a Python/JS project's standard library and external dependencies is empty.

### Fake Implementation
- None — the bugs are omissions, not fakes

### Technical Debt
- No dependency version tracking
- No external package registry lookup

### Test Quality (7 tests)
- Thin: empty graph, single file, import edge, relative import, symbol reference, cycle detection
- Missing: no absolute import test, no exports test, no Node.js resolution test
- All tests use hand-crafted normalized_files, not real parser output

### Development Effort to Complete
- Fix exports loop: 1 day
- Fix absolute imports: 2-3 days
- Add Node.js resolution: 3-5 days
- Add type-based edges: 5-7 days

---

## Sprint 9 — Entity Builder

### Planned Scope
- Build entity graph from files, symbols, and dependencies. Implement relation types: CONTAINS, IMPORTS, DEPENDS_ON, CALLS, EXTENDS.

### Actual Implementation
**Files:** `backend/dna/entities/builder.py`

**What exists:**
- `build_entity_graph()` — EntityGraph from NormalizedFile + SymbolIndex + DependencyGraph
- File/function/class/import entities with CONTAINS/DEPENDS_ON relations
- UID generation: `file:`, `function:`, `class:`, `import:` prefixes
- `EntityGraph.get_entity()`, `add_entity()`, `add_relation()`, `query()`

### Missing Implementation
- No CALLS relation type
- No EXTENDS relation type
- No deduplication of import entities (same import in 5 files = 5 duplicate entities)
- Symbol references create only file-level edges, not symbol-level

### Broken Implementation
- **BLD-036**: Import entities are created per-file-per-name. If `json` is imported in 5 files, 5 separate import entities exist with UIDs `import:file1.py:json`, `import:file2.py:json`, etc. This is massive duplication for widely-used imports.

### Fake Implementation
- None — the entity graph is functionally correct for what it does

### Technical Debt
- No entity-level indexing in storage
- Import duplication wastes DB space

### Test Quality (8 tests)
- OK: entities per file, functions, classes, methods, relations, cross-file deps
- Missing: no CALLS/EXTENDS tests, no dedup tests

### Development Effort to Complete
- Implement CALLS/EXTENDS: 2-3 days
- Deduplicate imports: 1-2 days
- Add symbol-level relations: 2-3 days

---

## Sprint 10 — SCM Storage

### Planned Scope
- Persistent storage of entity graph with versioning, metadata, backup/restore, migration support.

### Actual Implementation
**Files:** `backend/dna/storage/store.py`

**What exists:**
- SQLite-based SCStore with WAL mode
- `save_entity_graph()` / `load_entity_graph()`
- `set_metadata()` / `get_metadata()`
- `get_stats()`
- Context manager support
- Schema: entities (uid, name, kind, file_path, line, properties), relations (source_uid, target_uid, kind), metadata (key, value)

### Missing Implementation
- No versioning despite "SCM" in name
- No incremental updates (delete-all-then-reinsert)
- No schema migration system
- No connection pooling
- No property indexing (properties stored as opaque JSON)

### Broken Implementation
- `save_entity_graph()` at `store.py:56-57`: `DELETE FROM entities` + `DELETE FROM relations` — destructive write pattern loses all previous data
- No `PRAGMA foreign_keys = ON` — foreign key constraints are declared but never enforced

### Fake Implementation
- None — the store is correctly implemented for simple CRUD

### Technical Debt
- Delete-all pattern means no history tracking
- Properties as JSON means no property queries

### Test Quality (12 tests across 2 files)
- Good: CRUD, metadata, overwrite, context manager, edge cases (not opened, empty graph)
- Missing: no versioning tests, no migration tests, no incremental update tests

### Development Effort to Complete
- Add incremental updates: 2-3 days
- Add migration system: 3-5 days
- Add connection pooling: 1 day

---

## Sprint 11 — Evidence Store

### Planned Scope
- Store evidence from cognitive engines, query by type/source/file/time, deduplication, TTL.

### Actual Implementation
**Files:** `backend/dna/evidence/store.py`

**What exists:**
- SQLite EvidenceStore with WAL mode
- `add_evidence()` — insert with auto-UUID
- `get_by_type()`, `get_by_source()`, `get_by_file()`, `get_all()`
- `count()`, `clear()`
- Context manager support
- Schema: evidence (id, type, value, source, file_path, timestamp)

### Missing Implementation
- No time-series queries (needed by evolution for trend analysis)
- No evidence deduplication
- No evidence TTL/expiry
- Value is opaque JSON string — no structured queries

### Broken Implementation
- None identified — basic CRUD works correctly

### Fake Implementation
- None — the store is honest about its capabilities

### Technical Debt
- JSON values cannot be queried structurally
- Evidence accumulates indefinitely with no cleanup

### Test Quality (13 tests across 2 files)
- Good: CRUD for all query methods, edge cases (not opened, empty), context manager
- Missing: no time-series tests, no dedup tests, no TTL tests

### Development Effort to Complete
- Add time-series queries: 2-3 days
- Add deduplication: 1 day
- Add TTL/expiry: 1-2 days

---

## Sprint 12 — Structural Engine

### Planned Scope
- Analyze code structure: file counts, directory depth, coupling, complexity metrics.

### Actual Implementation
**Files:** `backend/dna/engines/structural.py`

**What exists:**
- File/function/class/import counts
- Directory depth (avg, max)
- Top directories by file count
- Functions-per-file and classes-per-file ratios
- Structural coupling (dependency count)
- Evidence storage for module_structure, size_metrics, complexity_metrics

### Missing Implementation
- No cyclomatic complexity analysis
- No cognitive complexity (nested control flow weighting)
- No cohesion metrics (LCOM, etc.)
- No real coupling metrics (afferent/efferent, instability)

### Broken Implementation
- Complexity at `structural.py`: "complexity" is just `function_count > 5` — not actual cyclomatic complexity

### Fake Implementation
- **BLD-047**: The "complexity_metrics" evidence type stores `structural_coupling` and `import_count` with the label "complexity", but there is no actual complexity computation. The metric is a count of relations, which is coupling, not complexity.

### Technical Debt
- 5 tests only
- No metric validation

### Test Quality (5 tests)
- Minimal: empty graph, counts, metrics, depth, evidence store
- No real complexity verification

### Development Effort to Complete
- Add cyclomatic complexity: 3-5 days
- Add cognitive complexity: 3-5 days
- Add proper coupling metrics: 2-3 days

---

## Sprint 13 — Evolution Engine

### Planned Scope
- Analyze commit trends, change frequency hotspots, growth patterns, temporal coupling.

### Actual Implementation
**Files:** `backend/dna/engines/evolution.py`

**What exists:**
- Commit count, author count
- Commit categories (feat/fix/refactor/test/docs/chore/other)
- Total insertions/deletions
- Changes-per-author average
- First/last commit dates
- Merge commit count
- Evidence for commit_distribution, growth_trend

### Missing Implementation
- No per-file change frequency tracking
- No hotspot detection
- No growth trend charting
- No refactoring detection
- No temporal coupling analysis

### Broken Implementation
- **BLD-051 (Critical)**: `file_change_counts` dict at `evolution.py:24` is initialized but never populated. Lines 25-27:
  ```python
  for c in commits:
      for _ in range(c.files_changed):
          pass
  ```
  The inner loop does nothing. `file_change_counts` remains empty. `hotspot_list` at line 60-61 will always be empty because `file_change_counts.get(fe.file_path, 0)` always returns 0.
  - This means the "evolution" engine produces no hotspot data whatsoever. The `hotspot_list` key in the result is always an empty list.

### Fake Implementation
- The hotspot feature is structurally present (code path, result key, evidence type) but never produces data. This is a dead feature.

### Technical Debt
- 5 tests only
- No per-file tracking dependency on git history

### Test Quality (5 tests)
- Minimal: empty history, commit count, categories, insertions/deletions, evidence store
- Missing: no hotspot test (can't — it's broken)
- Missing: no per-file frequency test

### Development Effort to Complete
- Fix hotspot via per-file tracking from git history: 3-5 days
- Add growth trends: 2-3 days
- Full evolution engine: 10-15 days

---

## Sprint 14 — Knowledge Engine

### Planned Scope
- Analyze authors, bus factor, per-file ownership, expertise scoring, knowledge map.

### Actual Implementation
**Files:** `backend/dna/engines/knowledge.py`

**What exists:**
- Author contribution counts and percentages
- Top contributor with share
- Bus factor calculation (contributors to 50%)
- Ownership scores (same score for every file)
- Expertise scores (per-author commit ratio)
- Evidence for author_contribution, ownership_score

### Missing Implementation
- No per-file ownership (git blame not implemented)
- No per-file expertise scoring
- No knowledge map / knowledge graph
- No specialization detection

### Broken Implementation
- **BLD-056 (Critical)**: Ownership scores at `knowledge.py:41-43`:
  ```python
  score = 0.0
  if contributions:
      score = contributions[0]["share"]
  ownership_scores[fe.file_path] = {"primary_owner": top_contributor, "ownership_score": round(score, 4)}
  ```
  Every file gets the same ownership score (`top_contributor.share`). The loop over `file_entities` produces identical values for every file. Real per-file ownership requires `git blame`, which does not exist.

### Fake Implementation
- Ownership scores are universally the same — this is a placeholder, not a real computation
- Expertise scores are global (per-author commit ratio), not per-file

### Technical Debt
- 8 tests across 2 files
- Blame dependency not implemented

### Test Quality (8 tests across 2 files)
- OK: empty history, contributions, top contributor, bus factor, evidence store, edge cases (single author, many authors, sorting)
- Missing: no ownership test (can't — it's fake), no per-file expertise test

### Development Effort to Complete
- Fix ownership via git blame: 5-7 days
- Add per-file expertise: 3-5 days
- Build knowledge map: 5-10 days

---

## Sprint 15 — Risk Engine

### Planned Scope
- Risk indicators: test coverage, dependency cycles, orphaned modules, high complexity, code smells, security issues.

### Actual Implementation
**Files:** `backend/dna/engines/risk.py`

**What exists:**
- Source vs test file count ratio
- Orphaned modules (no incoming dependencies)
- High-complexity files (>5 functions)
- Cycle risk detection
- 4 risk indicator types
- Evidence for risk_metrics

### Missing Implementation
- No actual code coverage analysis
- No security scanning
- No dependency freshness checking
- No code smell detection
- No unused export detection
- No calibrated risk scoring

### Broken Implementation
- **BLD-061**: "Test coverage" is `len(test_files) / max(len(source_files), 1)` — a file-count ratio. A project with 0 tests and 100 source files gets 0%. A project with 100 empty test files and 100 source files gets 50%. Neither tells you anything about actual code coverage.
- **BLD-065**: Risk score is `min(10, cycle_risk * 2 + len(top_risk_indicators))` — this is an arbitrary formula with no empirical basis.

### Fake Implementation
- The "coverage" metric is misnamed; it should be "test file ratio"
- Risk score is a made-up formula

### Technical Debt
- Orphan detection only checks zero deps (doesn't detect unused exports)
- High-complexity threshold of 5 functions is arbitrary

### Test Quality (9 tests across 2 files)
- OK: empty graph, file counts, coverage, risk indicators, evidence store, edge cases (no source, no tests, orphans, high complexity)
- Missing: no real coverage calculation tests (can't — it's not real coverage)

### Development Effort to Complete
- Rename/fix test coverage metric: 1 day
- Add smell detection: 5-7 days
- Calibrate scoring: 3-5 days

---

## Sprint 16 — Reasoning Layer

### Planned Scope
- Generate insights from evidence with dynamic confidence scoring, natural language explanations, reasoning pipeline with composable rules, learning/adaptation.

### Actual Implementation
**Files:** `backend/dna/reasoning/engine.py`

**What exists:**
- 6 insight rules with categories, labels, descriptions, evidence requirements, severity
- Evidence matching logic (type-based lookup)
- Severity sorting (high → medium → low → info)
- Insight generators for all 6 rules
- Evidence seeding for testing

### Missing Implementation
- No LLM integration (docs specify Ollama-based pipeline)
- No reasoning pipeline (docs specify 6-stage pipeline)
- No confidence computation
- No natural language generation
- No explainability output
- No learning/adaptation
- No insight deduplication

### Broken Implementation
- **BLD-067 (Critical)**: The "hotspot_risk" rule checks for evidence type `change_frequency`, but the evolution engine (Sprint 13) creates evidence with types `commit_distribution` and `growth_trend`. The rule can never trigger because the required evidence type is never created.
  - Evidence types defined in `models.py:424-429` (`EVIDENCE_TYPES` list) include `change_frequency` and `hotspot_list`, but no engine produces evidence of these types.
  - This means 1 of 6 rules (16%) is permanently dead code.
- **BLD-068**: All 6 insight generators use hardcoded confidence values: hotspot=0.85, bus_factor=0.9, test_debt=0.75, dependency=0.9, growth=0.6, refactoring=0.7. No computation occurs. These values are not derived from data quality, sample size, or signal strength.

### Fake Implementation
- The reasoning engine is a rule matcher with hardcoded confidences, not a reasoning system
- 1 of 6 rules can never trigger (dead code)
- The system pretends to compute insights but uses pre-baked values

### Technical Debt
- No pipeline architecture — rules run independently
- No caching
- No evidence chain tracking

### Test Quality (6 tests)
- Minimal: empty store, insight generation, hotspot insight, bus factor insight, severity sorting, rules defined
- Tests seed evidence directly (not through engines) — test evidence types don't match what engines produce
- Missing: no confidence tests (all hardcoded), no NLG tests

### Development Effort to Complete
- Fix evidence type mismatch: 1 day
- Add dynamic confidence: 5-7 days
- Build reasoning pipeline: 10-15 days
- Add LLM integration: 10-15 days

---

## Sprint 17 — REST API

### Planned Scope
- REST API endpoints for analysis, entities, evidence, insights, reasoning. Versioning, auth, WebSocket, GraphQL, error handling, pagination.

### Actual Implementation
**Files:** `backend/dna/api/app.py`, `analysis.py`

**What exists:**
- `POST /analyze` — run full pipeline
- `GET /` — serve frontend HTML
- `GET /styles.css` — serve CSS
- `GET /app.js` — serve JS
- `GET /health` — `{"status": "ok"}`
- `GET /status` — version and engine list
- CORS middleware (allow all origins)

### Missing Implementation
- No entity endpoints (`GET /v1/entities`, etc.)
- No evidence endpoints (`GET /v1/evidence`, etc.)
- No insight endpoints (`GET /v1/insights`, etc.)
- No reasoning endpoints (`POST /v1/reason/question`, etc.)
- No analysis management (`POST /v1/analysis/run` with 202, status, cancel)
- No WebSocket API (Phase 6 doc specifies)
- No GraphQL API (Phase 6 doc specifies)
- No authentication (Phase 6 doc specifies)
- No authorization (Phase 6 doc specifies)
- No API version prefix (Phase 6 doc specifies)
- No rate limiting (Phase 6 doc specifies)
- No pagination or filtering (Phase 6 doc specifies)
- No request timeout (large repos hang indefinitely)
- No streaming responses
- No structured error envelope
- No stored analysis query endpoints

### Broken Implementation
- **BLD-074**: `POST /analyze` accepts any string as `repo_path`. No validation for existence, accessibility, or malicious content. Path traversal risk.
- **BLD-075**: Bare `except Exception: raise HTTPException(500, detail=str(e))` at `app.py:80-81`. Catches everything including `NameError`, `ImportError`, `TypeError` (programming bugs). Exposes full traceback details to client.
- CORS allows all origins (`*`) — security risk

### Fake Implementation
- None — the API is honest about its limited scope

### Technical Debt
- 6 endpoints only (docs specify 20+)
- No OpenAPI documentation beyond FastAPI auto-generated
- No response model validation (AnalysisResponse model exists but not enforced)

### Test Quality (7 tests across 2 files)
- Good: health, status, frontend serving, non-git repo, git repo, nonexistent path error
- Tests use real temp repos with git init — good E2E coverage
- Missing: no auth tests, no timeout tests, no validation tests
- `test_analyze_no_repo` at `test_app.py:31`: asserts status=500 — this is testing the error, not proper validation

### Development Effort to Complete
- Full API as specified: 20-30 days
- Minimum viable API (entities, evidence, insights, versioning): 10-15 days

---

## Sprint 18 — Frontend

### Planned Scope
- React 18 + TypeScript SPA with routing, component system, state management, graph visualization, evidence explorer, search/query UI, accessibility, performance.

### Actual Implementation
**Files:** `frontend/index.html`, `styles.css`, `app.js`

**What exists:**
- Single vanilla HTML page
- Repository path input field + Analyze button
- 5 summary cards (commits, authors, total/source/test files)
- Evolution bar chart (Chart.js from CDN)
- Author contribution doughnut chart (Chart.js from CDN)
- Risk indicators list (color-coded)
- Insights list (with confidence percentage)
- Loading spinner
- Error display
- Dark theme CSS

### Missing Implementation
- **Not React at all** — ROADMAP.md says "React UI", Phase 7 docs specify React 18 + TypeScript + Vite + Zustand + React Query
- No component system at all
- No state management
- No routing (docs specify 12 routes)
- No application shell (header, sidebar, content, status bar)
- No graph visualization (docs specify 4 graph types)
- No evidence explorer
- No search/query UI
- No dashboard health scorecard
- No accessibility (WCAG 2.1 AA specified)
- No tests (0 frontend tests)
- No build system (Chart.js from CDN)
- No TypeScript
- No performance optimization

### Broken Implementation
- None — it's a simple page that works

### Fake Implementation
- Calling this a "React UI" in the roadmap is false
- Phase 7 architecture describes an elaborate system that doesn't exist

### Technical Debt
- 90 lines CSS, 127 lines JS, 55 lines HTML — monolithic, no structure
- No separation of concerns

### Test Quality (0 tests)

### Development Effort to Complete
- Full React SPA as specified: 30-50 days (experienced frontend engineer)
- Minimum viable frontend (React shell + dashboard + evidence view): 15-20 days

---

## Sprint 19 — Testing

### Planned Scope
- Unit tests + integration tests + edge cases for all packages. 90%+ coverage.

### Actual Implementation
**Files:** 42 test files across 13 test directories

**What exists:**
- 262 tests passing
- Test coverage: discovery (59), indexer (32), git_history (31), parser (25), engines (20), evidence (13), storage (12), symbols (7), graph (7), api (7), reasoning (6), entities (8), normalizer (9)
- Edge case test files for evidence, store, knowledge, risk, scanner
- Integration tests in test_app.py (creates temp git repos)

### Missing Implementation
- No integration tests for full pipeline (test_app.py tests the API, not the pipeline itself)
- No end-to-end tests against real repositories
- No performance/benchmark tests
- No security tests
- No frontend tests
- No coverage measurement

### Broken Implementation
- Many tests are trivial (create empty X, assert default values)
- Test evidence types don't match what engines produce (reasoning test seeds `change_frequency` but evolution never creates it)

### Fake Implementation
- Test count of 262 including trivial tests inflates perceived coverage
- "257 tests passing" in TODO.md is misleading when many tests are default-value assertions

### Technical Debt
- No `pytest-cov` configuration despite listing it as dependency
- No E2E test suite
- No test fixtures for real repositories

### Test Quality Summary
- Unit test coverage is moderate (~60% of functions tested minimally)
- Integration coverage is minimal (API layer only)
- E2E coverage is zero

### Development Effort to Complete
- Add integration tests for all packages: 10-15 days
- Add E2E tests: 5-7 days
- Add performance tests: 5-7 days

---

## Sprint 20 — Deployment

### Planned Scope
- Dockerfile, docker-compose, CI/CD, monitoring, logging, configuration, backup/restore, CLI.

### Actual Implementation
**Files:** `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `requirements.txt`, `start.py`

**What exists:**
- Dockerfile with python:3.12-slim, installs requirements, copies backend/frontend
- docker-compose.yml with DNA service
- .dockerignore with 8 entries
- requirements.txt with 7 pinned dependencies
- start.py (4 lines: `uvicorn.run(...)`)

### Missing Implementation
- Dockerfile won't build (tree-sitter needs C compiler, not installed)
- No CI/CD (no `.github/workflows/`)
- No monitoring (only trivial `/health`)
- No structured logging
- No configuration management
- No backup/restore
- No CLI commands
- No multi-stage Docker build
- No GPU/CPU image variants
- No model caching for LLM
- No npm/Tauri packaging

### Broken Implementation
- **BLD-095 (Critical)**: Dockerfile at line 6: `pip install --no-cache-dir -r requirements.txt`. `tree-sitter==0.26.0` is a native C extension that requires a C compiler. `python:3.12-slim` does not include `build-essential`. The Docker build will fail with a C compilation error.

### Fake Implementation
- Dockerfile exists but can't build — it's a placeholder
- docker-compose.yml exists but references a non-buildable image

### Technical Debt
- No environment variable configuration
- Hardcoded port (8000), host (0.0.0.0)

### Test Quality (0 tests)

### Development Effort to Complete
- Fix Dockerfile: 1 day
- Add CI/CD: 3-5 days
- Add configuration management: 3-5 days
- Add structured logging: 2-3 days
- Full deployment pipeline: 15-20 days

---

## Sprint 21 — Final Integration

### Planned Scope
- E2E pipeline test against real repositories, API verification, all bugs fixed, integration tests passing, production-ready.

### Actual Implementation
**Files:** `scripts/integration_test.py`, `tests/test_api/test_analysis.py`

**What exists:**
- `scripts/integration_test.py` — runs analysis on temp repo
- `scripts/verify_fix2.py` — runs analysis on `ig-costing-main`
- `scripts/verify_api_time.py` — API timing verification
- Bugfix for non-git repos (catches `NotAGitRepositoryError`)
- Bugfix for `node_modules` (added to `ALWAYS_IGNORE`)
- Pipeline runs end-to-end in ~10s for small repos

### Missing Implementation
- No automated E2E test suite
- No edge case handling for empty repos
- No binary file handling (crashes parser)
- No symlink handling
- No input sanitization (path traversal risk)
- CORS wide open
- No rate limiting
- No request timeout

### Broken Implementation
- After all bugfixes, analysis of `ig-costing-main` takes 10.5s — includes 5.8s parsing `.next` build artifacts and 3.9s normalizing them. The `.next` directory contains compiled JS files that produce zero symbols but consume 9.7s to process.

### Fake Implementation
- "E2E pipeline test against temp repo" in TODO.md exists as a manual script, not an automated test
- No repeatable, CI-friendly E2E tests

### Technical Debt
- No `.gitignore` file in project root
- `.next` directory not in ALWAYS_IGNORE (build output, no analysis value)

### Development Effort to Complete
- Add E2E test suite: 5-7 days
- Add edge case handling: 3-5 days
- Add `.next` to ALWAYS_IGNORE: 1 hour (quick win)
- Full production readiness: 20-30 days

---

## Summary: Sprint Completion (Recalculated)

| Sprint | Previous Claim | Actual (Code Only) | Actual (vs Architecture Docs) |
|--------|---------------|-------------------|------------------------------|
| S1: Discovery | COMPLETE | PARTIAL (65%) | PARTIAL (60%) |
| S2: Git History | COMPLETE | PARTIAL (70%) | PARTIAL (65%) |
| S3: Indexer | COMPLETE | PARTIAL (60%) | PARTIAL (55%) |
| S4: Parser | COMPLETE | PARTIAL (55%) | PARTIAL (30%) |
| S5: Registry | COMPLETE | PARTIAL (70%) | PARTIAL (50%) |
| S6: Normalizer | COMPLETE | PARTIAL (50%) | PARTIAL (25%) |
| S7: Symbols | COMPLETE | PARTIAL (40%) | PARTIAL (20%) |
| S8: Dependency Graph | COMPLETE | PARTIAL (45%) | PARTIAL (25%) |
| S9: Entity Builder | COMPLETE | PARTIAL (50%) | PARTIAL (30%) |
| S10: SCM Storage | COMPLETE | PARTIAL (60%) | PARTIAL (35%) |
| S11: Evidence Store | COMPLETE | PARTIAL (65%) | PARTIAL (40%) |
| S12: Structural | COMPLETE | PARTIAL (40%) | PARTIAL (25%) |
| S13: Evolution | COMPLETE | PARTIAL (30%) | PARTIAL (15%) |
| S14: Knowledge | COMPLETE | PARTIAL (35%) | PARTIAL (20%) |
| S15: Risk | COMPLETE | PARTIAL (40%) | PARTIAL (25%) |
| S16: Reasoning | COMPLETE | PARTIAL (25%) | PARTIAL (5%) |
| S17: REST API | COMPLETE | PARTIAL (40%) | PARTIAL (10%) |
| S18: Frontend | COMPLETE | PARTIAL (20%) | PARTIAL (5%) |
| S19: Testing | COMPLETE | PARTIAL (40%) | PARTIAL (20%) |
| S20: Deployment | COMPLETE | PARTIAL (15%) | PARTIAL (5%) |
| S21: Integration | COMPLETE | PARTIAL (25%) | PARTIAL (10%) |

**Overall vs Code Only:** ~42%  
**Overall vs Architecture Docs:** ~27%
