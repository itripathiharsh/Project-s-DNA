# Implementation Backlog — Project DNA (Rebuilt)

**Source of truth:** Sprint-by-sprint code audit (SPRINT_REPORT.md) + Architecture redesign (ARCHITECTURE_REDESIGN.md)  
**Do NOT trust previous completion estimates.** Every item below is based on actual code examination.  
**All items are NOT STARTED unless marked otherwise.**

---

## How to Read This Backlog

Each task has:

| Field | Meaning |
|-------|---------|
| **ID** | Unique identifier |
| **Phase** | Execution phase (0=Immediate, 1=Foundation, 2=Engines, 3=Delivery, 4=Quality) |
| **Goal** | What completing this achieves |
| **Files** | Files to modify or create |
| **Dependencies** | Tasks that must be done first |
| **Risk** | H/M/L — likelihood of unexpected complexity |
| **Est LOC** | Estimated lines of code (new + modified) |
| **Est Time** | Estimated engineering time |
| **Acceptance** | How to verify completion |
| **Unit Tests** | What unit tests to add |
| **Integration Tests** | What integration tests to add |

---

## Phase 0 — Immediate Bugfixes (Must Fix Before Any Feature Work)

### P0.1 — Fix normalizer re-parsing (Critical Architecture Bug)

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Normalizer accepts parsed data from parser instead of re-reading files |
| **Files** | `backend/dna/models.py` (add source_bytes/ast_tree to ParsedFile), `backend/dna/parser/ast_builder.py` (store parsed tree), `backend/dna/normalizer/orchestrator.py` (remove file I/O + re-parse) |
| **Dependencies** | None |
| **Risk** | Medium — may need to restructure ParsedFile data model |
| **Est LOC** | 150-200 (modify 3 files) |
| **Est Time** | 2-3 days |
| **Acceptance** | Normalizer uses existing parse; file is read once, parsed once |
| **Unit Tests** | Verify normalize_file works from ParsedFile without file access |
| **Integration Tests** | Full pipeline runs with single parse per file |

---

### P0.2 — Fix `FileInventory.categories` never populated

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | `build_file_inventory()` calls `build_classification_map()` and populates `categories` |
| **Files** | `backend/dna/indexer/inventory.py` |
| **Dependencies** | None |
| **Risk** | Low |
| **Est LOC** | 10-15 |
| **Est Time** | 1-2 hours |
| **Acceptance** | `FileInventory.categories` contains classified files after `build_file_inventory()` |
| **Unit Tests** | Verify categories field is populated for source, test, config files |
| **Integration Tests** | Pipeline output includes correct file categories |

---

### P0.3 — Fix evolution hotspot dead code

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | `file_change_counts` dict is populated with real per-file change data from commits |
| **Files** | `backend/dna/git_history/commit_parser.py` (track per-file changes in streaming parse), `backend/dna/engines/evolution.py` (use per-file data), `backend/dna/models.py` (add per_file_changes field to Commit) |
| **Dependencies** | None — parser already receives numstat data |
| **Risk** | Low — numstat data is already available but discarded |
| **Est LOC** | 80-120 |
| **Est Time** | 2-3 days |
| **Acceptance** | `analyze_evolution()` returns non-empty `hotspot_list` for repos with commit history |
| **Unit Tests** | Verify per-file tracking with multi-commit test data |
| **Integration Tests** | E2E pipeline produces hotspot data for git repo |

---

### P0.4 — Add `.next`, `dist`, `build` to ALWAYS_IGNORE

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Build output directories are ignored by scanner |
| **Files** | `backend/dna/discovery/scanner.py` |
| **Dependencies** | None |
| **Risk** | Low |
| **Est LOC** | 5 |
| **Est Time** | 15 minutes |
| **Acceptance** | `.next`, `dist`, `build` directories skipped in scan |
| **Unit Tests** | Verify files inside `.next` are excluded |
| **Integration Tests** | Analysis of Next.js project skips `.next` build artifacts |

---

### P0.5 — Add evidence type contract between engines and reasoning

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Evidence types defined as shared constants; every insight rule's required types are produced by at least one engine |
| **Files** | `backend/dna/models.py` (make EVIDENCE_TYPES a frozen set or enum), `backend/dna/reasoning/engine.py` (use shared types), `backend/dna/engines/*.py` (use shared types), `tests/test_evidence_contract.py` (new) |
| **Dependencies** | None |
| **Risk** | Low |
| **Est LOC** | 80-120 across 5 files |
| **Est Time** | 1-2 days |
| **Acceptance** | No insight rule requires an evidence type that no engine produces |
| **Unit Tests** | Contract test: for every rule, at least one engine produces the required evidence type |
| **Integration Tests** | Reasoning engine produces all 6 insight types after pipeline run |

---

### P0.6 — Fix gossip_rule evidence type mismatch

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Hotspot_risk rule checks for evidence type that actually gets created (change_frequency from evolution) |
| **Files** | `backend/dna/reasoning/engine.py`, `backend/dna/engines/evolution.py` |
| **Dependencies** | P0.3, P0.5 |
| **Risk** | Low |
| **Est LOC** | 10-30 |
| **Est Time** | 1 day |
| **Acceptance** | After P0.3 + P0.5, hotspot_risk rule fires correctly when evidence exists |
| **Unit Tests** | Integration test with seeded hotspot evidence produces hotspot insight |
| **Integration Tests** | Pipeline on repo with change history produces hotspot insight |

---

### P0.7 — Add large-file and binary-file skipping

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Files >1MB and binary files are skipped by scanner before reaching parser |
| **Files** | `backend/dna/discovery/scanner.py` (add size threshold), `backend/dna/parser/orchestrator.py` (add binary detection) |
| **Dependencies** | None |
| **Risk** | Low |
| **Est LOC** | 30-50 |
| **Est Time** | 1 day |
| **Acceptance** | Binary files and files >1MB are skipped with a warning; parser never receives them |
| **Unit Tests** | Verify binary file detection, size threshold |
| **Integration Tests** | Pipeline on repo with binary files does not crash |

---

### P0.8 — Add input validation and path sanitization to API

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | `POST /analyze` validates repo_path: exists, is directory, is accessible, no path traversal |
| **Files** | `backend/dna/api/app.py`, `backend/dna/api/analysis.py` |
| **Dependencies** | None |
| **Risk** | Medium — need to handle Windows path differences |
| **Est LOC** | 60-80 |
| **Est Time** | 1-2 days |
| **Acceptance** | Invalid paths return 400 (not 500); path traversal returns 400; valid paths work |
| **Unit Tests** | Test invalid paths, non-existent paths, file paths instead of directories |
| **Integration Tests** | API returns proper error codes for all invalid inputs |

---

## Phase 1 — Foundation Stabilization

### P1.1 — Add config management system

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Configuration via env vars + config file; replaces hardcoded values |
| **Files** | `backend/dna/config.py` (new), `backend/dna/discovery/scanner.py` (use config), `backend/dna/parser/orchestrator.py` (use config) |
| **Dependencies** | None |
| **Risk** | Medium |
| **Est LOC** | 150-200 (new file + modifications) |
| **Est Time** | 3-5 days |
| **Acceptance** | Config loaded from env vars or `~/.config/dna/dna.json`; all hardcoded values use config |
| **Unit Tests** | Config loading from env, file, defaults |
| **Integration Tests** | Analysis with custom config produces expected output |

---

### P1.2 — Add SQLite migration system

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | SCStore and EvidenceStore auto-migrate schema on version mismatch |
| **Files** | `backend/dna/storage/store.py`, `backend/dna/evidence/store.py` |
| **Dependencies** | None |
| **Risk** | Low |
| **Est LOC** | 80-120 |
| **Est Time** | 2-3 days |
| **Acceptance** | Schema version stored via `PRAGMA user_version`; new version applies migration SQL automatically |
| **Unit Tests** | Migration from v1 to v2 applies correct SQL |
| **Integration Tests** | Old DB auto-upgraded on open |

---

### P1.3 — Add `.gitignore` standard pattern support

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Ignore patterns support `**`, `!` negation, directory-only `pattern/`, and root-relative `/pattern` |
| **Files** | `backend/dna/discovery/ignore.py`, `backend/dna/discovery/scanner.py` |
| **Dependencies** | None |
| **Risk** | Medium — edge cases in pattern matching |
| **Est LOC** | 120-180 |
| **Est Time** | 3-5 days |
| **Acceptance** | Scanner correctly handles all `.gitignore` pattern types from git-scm.com/docs/gitignore |
| **Unit Tests** | Test each pattern type (negation, double-star, directory-only, root-relative) |
| **Integration Tests** | Analysis of repo with complex `.gitignore` produces correct file list |

---

### P1.4 — Fix dependency graph exports loop

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Exports create dependency edges from source module to export targets |
| **Files** | `backend/dna/graph/builder.py` |
| **Dependencies** | P0.1 |
| **Risk** | Low |
| **Est LOC** | 20-40 |
| **Est Time** | 1 day |
| **Acceptance** | JS/TS exports create dependency edges |
| **Unit Tests** | Verify export creates edge between files |
| **Integration Tests** | Pipeline on JS project includes export edges |

---

### P1.5 — Fix absolute import resolution

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Absolute imports (both stdlib and project-root-relative) resolve correctly |
| **Files** | `backend/dna/graph/builder.py` |
| **Dependencies** | None |
| **Risk** | Medium — distinguishing stdlib from project imports |
| **Est LOC** | 60-100 |
| **Est Time** | 2-3 days |
| **Acceptance** | Absolute project imports resolve to correct files; stdlib imports are marked as external |
| **Unit Tests** | Test absolute import resolution for Python and JS/TS |
| **Integration Tests** | Pipeline on Python project includes absolute import edges |

---

### P1.6 — Add Node.js module resolution

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | JS/TS imports resolve through `node_modules` and `index.js`/`index.ts` fallbacks |
| **Files** | `backend/dna/graph/builder.py` |
| **Dependencies** | P1.5 |
| **Risk** | Medium |
| **Est LOC** | 80-120 |
| **Est Time** | 3-5 days |
| **Acceptance** | JS imports like `import { foo } from './utils'` resolve to `./utils.js` or `./utils/index.js` |
| **Unit Tests** | Test node_modules resolution, index.js fallback, extension-less imports |
| **Integration Tests** | Pipeline on JS project resolves all internal imports |

---

### P1.7 — Add TypeScript language support

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | TypeScript has its own grammar (not JS fallback); TS-specific constructs parsed |
| **Files** | `backend/dna/parser/registry.py`, `backend/dna/parser/traverser.py` (add TS traversal), `backend/dna/normalizer/ts_normalizer.py` (new), `backend/dna/normalizer/orchestrator.py`, `requirements.txt` |
| **Dependencies** | P0.1 |
| **Risk** | Medium |
| **Est LOC** | 300-500 across multiple files |
| **Est Time** | 5-7 days |
| **Acceptance** | TypeScript files parse with TS grammar; interfaces, enums, type aliases captured |
| **Unit Tests** | Test TS function, class, interface, enum, import, export extraction |
| **Integration Tests** | Pipeline on TS project produces symbol index with TS-specific symbols |

---

### P1.8 — Add Go and Rust language support

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Go and Rust Tree-sitter grammars installed and configured |
| **Files** | `backend/dna/parser/registry.py`, `backend/dna/parser/traverser.py` (add Go/Rust traversal), `requirements.txt`, `Dockerfile` |
| **Dependencies** | P0.1 |
| **Risk** | High — Rust/Go tree-sitter grammars may have compatibility issues on Windows |
| **Est LOC** | 400-600 |
| **Est Time** | 7-10 days (both languages) |
| **Acceptance** | Go and Rust files parse; functions, structs, imports, exports captured |
| **Unit Tests** | Test Go function/struct/import extraction; Test Rust function/struct/import extraction |
| **Integration Tests** | Pipeline on Go + Rust projects produces correct symbol output |

---

### P1.9 — Fix knowledge engine ownership scores

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Per-file ownership calculated from git blame data |
| **Files** | `backend/dna/engines/knowledge.py`, `backend/dna/git_history/blame.py` (new) |
| **Dependencies** | None — blame miner can be built independently |
| **Risk** | Medium — git blame output parsing needs careful handling |
| **Est LOC** | 150-250 (blame module + knowledge changes) |
| **Est Time** | 5-7 days |
| **Acceptance** | Each file has a unique ownership score based on blame line counts |
| **Unit Tests** | Blame parser test; ownership per-file test |
| **Integration Tests** | Pipeline on git repo produces unique per-file ownership scores |

---

### P1.10 — Add structured logging

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | All pipeline stages emit structured JSON logs with correlation IDs |
| **Files** | `backend/dna/logging.py` (new), `backend/dna/api/app.py`, `backend/dna/api/analysis.py`, `backend/dna/discovery/orchestrator.py`, `backend/dna/parser/orchestrator.py`, `backend/dna/engines/*.py`, `backend/dna/reasoning/engine.py` |
| **Dependencies** | P1.1 (config for log level) |
| **Risk** | Low |
| **Est LOC** | 200-300 across many files |
| **Est Time** | 3-5 days |
| **Acceptance** | All stages emit JSON log lines with timestamp, level, stage, duration_ms |
| **Unit Tests** | Log output captured and verified |
| **Integration Tests** | Pipeline run produces structured logs |

---

## Phase 2 — Engine Improvement

### P2.1 — Add cyclomatic complexity to structural engine

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Structural engine computes cyclomatic complexity from AST |
| **Files** | `backend/dna/engines/structural.py`, `backend/dna/parser/complexity.py` (new) |
| **Dependencies** | P0.1 (need source text in parser output) |
| **Risk** | Medium |
| **Est LOC** | 150-250 |
| **Est Time** | 3-5 days |
| **Acceptance** | Each function has a cyclomatic complexity score |
| **Unit Tests** | Verify complexity counts: if, while, for, case, catch, logical operators, ?: ternary |
| **Integration Tests** | Pipeline output includes per-function complexity |

---

### P2.2 — Expand rule-based reasoning (6 → 12-15 rules)

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Reasoning engine has 12-15 insight rules covering all engine output |
| **Files** | `backend/dna/reasoning/engine.py` |
| **Dependencies** | P0.3, P1.9, P2.1 |
| **Risk** | Low |
| **Est LOC** | 100-200 |
| **Est Time** | 3-5 days |
| **Acceptance** | All engine evidence types are covered by at least one insight rule |
| **Unit Tests** | Each new rule tested with seeded evidence |
| **Integration Tests** | Pipeline on real repo produces 8+ distinct insight categories |

---

### P2.3 — Add dynamic confidence computation

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Confidence computed from evidence quality: coverage, consistency, recency, sample size |
| **Files** | `backend/dna/reasoning/engine.py`, `backend/dna/reasoning/confidence.py` (new) |
| **Dependencies** | P2.2 |
| **Risk** | Medium |
| **Est LOC** | 120-180 |
| **Est Time** | 3-5 days |
| **Acceptance** | Confidence varies based on evidence quantity and quality, not hardcoded |
| **Unit Tests** | Confidence increases with more evidence; decreases with conflicting evidence |
| **Integration Tests** | Pipeline on repo with extensive git history produces higher confidence than empty repo |

---

### P2.4 — Add incremental storage updates

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | SCStore upserts entities instead of delete-all-then-reinsert |
| **Files** | `backend/dna/storage/store.py` |
| **Dependencies** | P1.2 (migrations) |
| **Risk** | Medium |
| **Est LOC** | 100-150 |
| **Est Time** | 3-5 days |
| **Acceptance** | Consecutive saves preserve entities not present in new graph |
| **Unit Tests** | Upsert adds new entities, keeps unchanged ones, removes deleted ones |
| **Integration Tests** | Storage persists across multiple analysis runs |

---

### P2.5 — Fix JS normalizer gaps

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | JS normalizer handles arrow functions, static methods, getters/setters, export default |
| **Files** | `backend/dna/normalizer/js_normalizer.py` |
| **Dependencies** | P0.1 |
| **Risk** | Medium |
| **Est LOC** | 80-150 |
| **Est Time** | 3-5 days |
| **Acceptance** | All major JS constructs produce correct canonical nodes |
| **Unit Tests** | Test each JS construct: arrow fn, static method, getter, setter, export default |
| **Integration Tests** | Pipeline on JS project captures all constructs |

---

### P2.6 — Add CALLS and EXTENDS entity relations

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Entity graph includes CALLS (function-to-function) and EXTENDS (class-to-class) relations |
| **Files** | `backend/dna/entities/builder.py` |
| **Dependencies** | P1.4, P1.7 |
| **Risk** | High — requires accurate call detection from AST |
| **Est LOC** | 100-200 |
| **Est Time** | 5-7 days |
| **Acceptance** | Function calls create CALLS edges; class inheritance creates EXTENDS edges |
| **Unit Tests** | Verify CALLS and EXTENDS relations created correctly |
| **Integration Tests** | Pipeline on Python/TS project includes CALLS and EXTENDS edges |

---

### P2.7 — Fix risk engine test coverage metric

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Rename "test_coverage_ratio" to "test_file_ratio" or implement real coverage analysis |
| **Files** | `backend/dna/engines/risk.py` |
| **Dependencies** | None |
| **Risk** | Low |
| **Est LOC** | 10-30 |
| **Est Time** | 1 day |
| **Acceptance** | Metric is accurately named; no claim of actual code coverage |
| **Unit Tests** | Update existing tests to use new metric name |
| **Integration Tests** | Pipeline output uses correct metric name |

---

## Phase 3 — Delivery

### P3.1 — Expand REST API with version prefix and resource endpoints

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | API endpoints for entities, evidence, insights with `/v1/` prefix |
| **Files** | `backend/dna/api/routers/` (new directory), `backend/dna/api/app.py` |
| **Dependencies** | P0.8 |
| **Risk** | Medium |
| **Est LOC** | 400-600 |
| **Est Time** | 10-15 days |
| **Acceptance** | GET /v1/entities, GET /v1/evidence, GET /v1/insights return correct data |
| **Unit Tests** | Each endpoint tested with TestClient |
| **Integration Tests** | Full pipeline + query endpoints produce consistent results |

---

### P3.2 — Add authentication

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | API key auth for network mode; no auth for localhost |
| **Files** | `backend/dna/api/auth.py` (new), `backend/dna/api/app.py` |
| **Dependencies** | P1.1 (config) |
| **Risk** | Medium |
| **Est LOC** | 200-300 |
| **Est Time** | 5-7 days |
| **Acceptance** | Requests without auth get 401 (network mode); requests with valid key succeed |
| **Unit Tests** | Test auth middleware, key validation |
| **Integration Tests** | API returns 401 for unauthenticated requests in network mode |

---

### P3.3 — Add request timeout and rate limiting

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Analysis requests timeout after 120s; rate limited to 10/min |
| **Files** | `backend/dna/api/app.py`, `backend/dna/api/middleware.py` (new) |
| **Dependencies** | P0.8 |
| **Risk** | Low |
| **Est LOC** | 80-120 |
| **Est Time** | 2-3 days |
| **Acceptance** | Long-running analysis returns 503; excessive requests return 429 |
| **Unit Tests** | Test timeout middleware, rate limiter |
| **Integration Tests** | API does not hang on large repos |

---

### P3.4 — Build React frontend (Phase 1: shell + dashboard)

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | React app with Vite, basic routing, dashboard replacing the vanilla HTML page |
| **Files** | `frontend/` — rebuild with React + Vite + basic component system |
| **Dependencies** | P3.1 (API must exist) |
| **Risk** | High — frontend engineer needed |
| **Est LOC** | 800-1200 |
| **Est Time** | 15-20 days |
| **Acceptance** | React app serves; dashboard shows all current data in improved layout |
| **Unit Tests** | Jest/React Testing Library for components |
| **Integration Tests** | Frontend + API integration test |

---

### P3.5 — Fix Dockerfile and add CI/CD

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Dockerfile builds; CI pipeline runs tests on push |
| **Files** | `Dockerfile` (fix), `.github/workflows/ci.yml` (new) |
| **Dependencies** | BLD-095 tree-sitter fix |
| **Risk** | Medium |
| **Est LOC** | 50-100 |
| **Est Time** | 3-5 days |
| **Acceptance** | `docker build` succeeds; CI pipeline runs tests and reports status |
| **Unit Tests** | N/A — infrastructure change |
| **Integration Tests** | Docker container serves API |

---

## Phase 4 — Quality

### P4.1 — Add integration test suite

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Status** | **Completed** |
| **Goal** | Automated integration tests that run the full pipeline on temp repos and verify output |
| **Files** | `tests/test_integration/` (new directory, 5-10 test files) |
| **Dependencies** | P0.1, P0.2, P0.3 |
| **Risk** | Medium |
| **Est LOC** | 500-800 |
| **Est Time** | 10-15 days |
| **Acceptance** | Each sprint has at least one integration test |
| **Unit Tests** | N/A — this IS integration tests |
| **Integration Tests** | Tests pass in CI |

---

### P4.2 — Add E2E tests against sample repositories

| Field | Value |
|-------|-------|
| **Status** | **Completed** |
| **Goal** | Pipeline tested against 3 real open-source repos (Python, JS, mixed) |
| **Files** | `tests/test_e2e/` (new directory), sample repos as git submodules or scripts |
| **Dependencies** | P4.1 |
| **Risk** | Medium |
| **Est LOC** | 300-500 |
| **Est Time** | 5-7 days |
| **Acceptance** | All 3 sample repos produce correct analysis output |
| **Unit Tests** | N/A |
| **Integration Tests** | E2E tests pass in CI |

---

### P4.3 — Add .gitignore at project root

| Field | Value |
|-------|-------|
| **Goal** | Prevent accidental commits of __pycache__, .pytest_cache, node_modules, .venv |
| **Files** | `.gitignore` (new) |
| **Dependencies** | None |
| **Risk** | Low |
| **Est LOC** | 15-25 |
| **Est Time** | 1 hour |
| **Acceptance** | Git ignores all build artifacts |
| **Unit Tests** | N/A |
| **Integration Tests** | N/A |

---

## Backlog Summary

| Phase | Items | Est LOC | Est Time | Critical Path |
|-------|-------|---------|----------|---------------|
| P0: Immediate Bugfixes | 8 | 425-755 | 10-15 days | P0.1 → everything |
| P1: Foundation | 10 | 1610-2670 | 33-52 days | P1.1, P1.3 → P1.4 |
| P2: Engines | 7 | 660-1170 | 22-33 days | P2.1 → P2.2 → P2.3 |
| P3: Delivery | 5 | 1530-2120 | 35-50 days | P3.1 → P3.4 |
| P4: Quality | 3 | 815-1325 | 15-22 days | P4.1 → P4.2 |

**Total: 33 items, ~5-7K LOC, 115-172 engineering days**

Note: These estimates assume a single engineer familiar with the codebase. Parallel work on independent items (e.g., P1.1 config + P1.3 ignore patterns) reduces calendar time.

## What Is NOT in This Backlog

The following items from the architecture docs are intentionally excluded for V1:

| Feature | Reason |
|---------|--------|
| Rust core | Deferred to V2 (MISTAKE 1) |
| LLM/Ollama integration | Deferred to V2 (MISTAKE 2) |
| GraphQL API | Deferred to V2 (MISTAKE 4) |
| WebSocket API | Deferred to V1.5 |
| Tauri desktop app | Deferred to V2 |
| TypeScript frontend | Frontend starts with JS; TS added in later phase |
| Performance benchmarks | Deferred until engines are stable |
| AI evaluation | Requires LLM (V2) |
