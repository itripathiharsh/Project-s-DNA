# Architecture Redesign — Project DNA

## Identified Architecture Mistakes

Based on the complete codebase audit and architecture document review, the following architectural decisions need reconsideration.

---

### MISTAKE 1: Rust Core (Over-engineered for V1)

**Problem:** Phase 2 architecture specifies Rust for the analysis core. Phase 8 coding standards include Rust toolchain. The actual codebase is 100% Python. Implementing Rust interop would require a complete rewrite of the analysis pipeline (discovery, parser, normalizer, symbols, graph, entities) and a FFI bridge.

**Impact:** If we follow the architecture docs literally, we throw away ~4,300 lines of working Python code and reimplement in Rust — 3-6 months of work.

**Recommendation:** **Accept Python as the analysis engine for V1.** Update the architecture docs to reflect this. Python is adequate for single-repo analysis of projects up to ~100K files. Rust can be introduced in V2 for performance-critical paths (parsing, graph traversal) if needed.

**Files affected:** `docs/architecture/Phase_2_System_Architecture.md`, `docs/architecture/Phase_8/02_Coding_Standards.md`, `docs/architecture/Phase_11/*.md`

---

### MISTAKE 2: LLM-Based Reasoning (Premature for V1)

**Problem:** Phase 5 architecture describes a 6-stage LLM reasoning pipeline with Ollama integration, prompt orchestration, context assembly, token budgets, model routing, and explainability. The actual reasoning engine is a simple rule-based matcher with 6 rules and hardcoded confidence values.

The architecture assumes LLM availability, but:
- LLMs require 8GB+ RAM and GPU (Ollama + 7B model)
- LLM inference adds 2-10s per query
- LLM hallucination requires expensive validation
- The current pipeline has no LLM infrastructure at all

**Impact:** Implementing the full Phase 5 architecture as documented would add ~3,000-5,000 LOC, 3-5 external dependencies, and significant operational complexity. It's unrealistic to build this before the core analysis pipeline is production-quality.

**Recommendation:** **Keep rule-based reasoning for V1.** The rule-based approach is deterministic, fast, and verifiable. The 6 existing rules should be fixed and expanded to 12-15 rules. LLM-based reasoning becomes a V2 enhancement. Phase 5 architecture should be updated to describe the current rule-based system as V1 with LLM as V2.

**Files affected:** `docs/architecture/Phase_5/*.md`

---

### MISTAKE 3: React + TypeScript + Vite + Tauri Frontend (Scope Creep)

**Problem:** Phase 7 architecture specifies React 18, TypeScript, Vite, Zustand, React Query, D3.js, Recharts, React Flow, Tailwind CSS, and Tauri for desktop. The actual frontend is a single vanilla HTML page with Chart.js from CDN.

**Impact:** Building the full specified frontend is a 30-50 day engineering task for one experienced frontend engineer. This is disproportionate for V1, where the dashboard is functional with the current page.

**Recommendation:** **Upgrade incrementally.** Phase 1: Convert to React with Vite (no TypeScript). Phase 2: Add TypeScript + component system + routing. Phase 3: Add graph visualization + evidence explorer. Phase 4: Add state management + desktop shell. Defer Tauri to V2. Update architecture docs to reflect this phased approach.

**Files affected:** `docs/architecture/Phase_7/*.md`, `roadmap/PHASE_PLAN.md`

---

### MISTAKE 4: REST + WebSocket + GraphQL API (Too Many Protocols for V1)

**Problem:** Phase 6 architecture specifies three API protocols: REST, WebSocket, GraphQL. The current API has 6 REST endpoints with no versioning, no auth, no error handling.

**Impact:** Implementing all three protocols for V1 is over-engineered. WebSocket and GraphQL add significant complexity (subscriptions, schema design, connection management, DataLoader) with no clear V1 need.

**Recommendation:** **REST-only for V1.** Expand the REST API to cover all resource types (entities, evidence, insights, reasoning, analysis management) with proper versioning, auth, and error handling. WebSocket can be added in V1.5 for streaming. GraphQL remains V2. Update architecture docs.

**Files affected:** `docs/architecture/Phase_6/*.md`

---

### MISTAKE 5: `ALWAYS_IGNORE` Without Configurability

**Problem:** `scanner.py:6` hardcodes `ALWAYS_IGNORE` as a Python set. Users cannot add directories to the ignore list without modifying source code. The `.next` directory (Next.js build output) is not ignored, wasting 9.7s of analysis time on every React project.

**Recommendation:** Make ignore patterns configurable via:
1. Environment variable (`DNA_IGNORE_PATTERNS`)
2. Config file (`~/.config/dna/dna.json` or `.dna/config.toml`)
3. CLI argument

Add `.next`, `dist`, `build`, `.cache`, `.venv` to default ALWAYS_IGNORE.

**Files affected:** `backend/dna/discovery/scanner.py`, new config module

---

### MISTAKE 6: Normalizer Re-Parses Files (Architectural Defect)

**Problem:** The normalizer reads every file from disk and re-parses it with Tree-sitter, duplicating the parser's work. This doubles analysis time and creates a tight coupling between normalizer and filesystem that shouldn't exist.

**Root cause:** `ParsedFile` does not store the source text or the parsed tree. The normalizer has to re-read and re-parse because the parser's output is discarded after symbol extraction.

**Recommendation:** Store the parsed tree (or at minimum the source bytes) in `ParsedFile`. The normalizer should accept a `ParsedFile` and work from its stored data, never touching the filesystem.

**Files affected:** `backend/dna/models.py` (ParsedFile), `backend/dna/parser/ast_builder.py`, `backend/dna/normalizer/orchestrator.py`

---

### MISTAKE 7: No Integration Test Strategy

**Problem:** Despite 262 tests, there are zero automated integration tests that verify the full pipeline works end-to-end. The `test_analysis.py` tests are the closest but only test individual scenarios (non-git, with-node_modules) not the full pipeline output quality.

**Impact:** Bugs like the evolution hotspot dead code, the empty exports loop, and the reasoning evidence type mismatch were not caught by tests because there are no tests that track data through the full pipeline.

**Recommendation:** Build an integration test suite that:
1. Creates a real git repo with Python, JS, and mixed files
2. Runs the full analysis pipeline
3. Asserts specific properties of the output (expected number of symbols, specific dependency edges, non-empty hotspot list, per-file ownership scores)
4. Runs on every PR/commit

**Files affected:** `tests/test_integration/` (new directory)

---

### MISTAKE 8: Migration System Not Included (Tech Debt)

**Problem:** Both SCStore and EvidenceStore use raw SQLite with no migration support. Schema changes require manual database deletion. There's no version tracking of the database schema.

**Recommendation:** Add a lightweight migration system using SQLite's `PRAGMA user_version` for schema version tracking. Version numbers in code, migrations applied automatically on open.

**Files affected:** `backend/dna/storage/store.py`, `backend/dna/evidence/store.py`

---

### MISTAKE 9: `DependencyGraph.detect_cycles()` Has No Cycle Pruning

**Problem:** Cycle detection uses naive DFS with path tracking. For a graph with N nodes, this visits every node in every cycle it belongs to. In practice, for large dependency graphs (>5000 nodes), this can be slow. There's also no cycle reporting beyond listing them.

**Recommendation:** Add Tarjan's or Kosaraju's algorithm for strongly connected components. Report cycles per SCC. Add cycle length and severity (cross-module cycles > within-module cycles).

**Files affected:** `backend/dna/models.py` (DependencyGraph.detect_cycles), `backend/dna/graph/builder.py`

---

### MISTAKE 10: Evidence Type Mismatch Between Engines and Reasoning Layer

**Problem:** `EVIDENCE_TYPES` in `models.py:424-429` lists 13 evidence types. Engines produce evidence with their own type strings. The reasoning layer checks for evidence types that engines never create. There's no shared contract for evidence type names.

**Impact:** The `hotspot_risk` insight rule can never trigger because it looks for `change_frequency` but no engine creates that type.

**Recommendation:** Define evidence types as an enum or frozen set, shared between engines and reasoning layer. Add a test that verifies: for every insight rule, the required evidence types are produced by at least one engine.

**Files affected:** `backend/dna/models.py`, `backend/dna/reasoning/engine.py`, `backend/dna/engines/evolution.py`, `backend/dna/engines/structural.py`, `backend/dna/engines/knowledge.py`, `backend/dna/engines/risk.py`

---

## Summary of Redesign Decisions

| # | Issue | Decision | Rationale |
|---|-------|----------|-----------|
| 1 | Rust core | **Defer to V2** | Python is adequate for V1; Rust rewrite is 3-6 months |
| 2 | LLM reasoning | **Defer to V2** | Fix rule-based engine for V1; LLM adds 3-5K LOC and operational complexity |
| 3 | React+TS+Vite+Tauri | **Incremental V1** | Start with React+Vite; defer Tauri+TS to later phases |
| 4 | WebSocket+GraphQL | **Defer to V1.5/V2** | REST-only for V1; WebSocket for streaming, GraphQL for complex queries later |
| 5 | Hardcoded ignores | **Add config system** | Quick fix with high impact (`.next` saves 9.7s per analysis) |
| 6 | Normalizer re-parses | **Fix immediately** | Architectural defect doubling parse time |
| 7 | No integration tests | **Add test suite** | Critical gap — bugs slipping through without it |
| 8 | No DB migrations | **Add lightweight system** | Prevents schema changes from breaking existing databases |
| 9 | Slow cycle detection | **Optimize with SCC** | Affects large-repo performance |
| 10 | Evidence type mismatch | **Add shared contract** | Prevents dead rules and unreachable insight types |

## What This Means for the Backlog

**Stop work on:** Rust interop, LLM integration, WebSocket, GraphQL, Tauri desktop, TypeScript frontend.

**Fix immediately:** Normalizer re-parsing, evidence type contract, `ALWAYS_IGNORE` configurability, migration system, integration tests.

**Build incrementally:** React frontend (phases), REST API expansion (phased), rule-based reasoning expansion (from 6 to 12-15 rules), proper complexity metrics.

**These decisions override the original architecture docs.** We prioritize working software over following aspirational plans.
