# Execution Order — Project DNA Recovery

**Principle:** Fix foundations first. Never build on broken ground.
**Rule:** Each phase must be verified (unit tests + integration tests) before the next phase begins.

---

## Phase 0 — Critical Bugfixes (Do First)

These bugs break core functionality. Everything downstream is affected. Fix before any feature work.

| Order | ID | Title | Sprint | Reason |
|-------|----|-------|--------|--------|
| 0.1 | BLD-014 | Integrate `FileClassificationMap` into `FileInventory` | S3 | Every engine downstream uses file categories. Currently always empty. |
| 0.2 | BLD-024 | Eliminate duplicate parsing in normalizer | S6 | Normalizer re-reads and re-parses every file. 2x parse time, wastes resources. |
| 0.3 | BLD-007 | Add large-file skipping in scanner | S1 | >1MB files crash Tree-sitter parser. Pipeline hard-fails on real repos. |
| 0.4 | BLD-102 | Add edge case handling for binary files | S21 | Binary files crash parser. Same class of bug as BLD-007. |
| 0.5 | BLD-104 | Add input validation and sanitization throughout API | S21 | Path traversal / command injection risk. Security-critical. |
| 0.6 | BLD-074 | Add input validation for API endpoints | S17 | Must be done before any API expansion. |
| 0.7 | BLD-075 | Add proper error handling throughout API | S17 | Bare `except Exception` makes debugging impossible. |

### Phase 0 Verification Gate
- `FileInventory.categories` populated correctly for sample repos
- Normalizer accepts source bytes from parser (no re-read)
- Large files >1MB skipped with warning (not crash)
- Binary files detected and skipped
- `POST /analyze` with invalid/bad paths returns proper 4xx, not 500 or crash
- All existing unit tests still pass

---

## Phase 1 — Core Pipeline Stabilization

### Order 1.1: Discovery (S1 + S5)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 1.1.1 | BLD-001 | Fix `.dnaignore` pattern support | High | None |
| 1.1.2 | BLD-005 | Add symlink handling to scanner | Medium | None |
| 1.1.3 | BLD-006 | Add encoding detection | Medium | None |
| 1.1.4 | BLD-002 | Expand framework detection to all configs | Medium | 1.1.3 |
| 1.1.5 | BLD-003 | Add recursive build system detection | Medium | None |
| 1.1.6 | BLD-004 | Fix inaccurate file count | Low | 1.1.2 |
| 1.1.7 | BLD-022 | Add dynamic grammar download | Medium | None |
| 1.1.8 | BLD-023 | Add language hot-reload | Low | 1.1.7 |
| 1.1.9 | BLD-008 | Add `.gitmodules` detection | Low | None |

### Order 1.2: Git History (S2)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 1.2.1 | BLD-009 | Add per-file change tracking to commit miner | **Critical** | None |
| 1.2.2 | BLD-010 | Add `git blame` support | High | None |
| 1.2.3 | BLD-011 | Improve commit categorization | Medium | None |
| 1.2.4 | BLD-012 | Add merge commit analysis | Low | 1.2.1 |
| 1.2.5 | BLD-013 | Add structured diff analysis | Medium | 1.2.1 |

### Order 1.3: Indexer (S3)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 1.3.1 | BLD-015 | Integrate `DirectoryTree` into pipeline | Low | Phase 0.1 |
| 1.3.2 | BLD-016 | Add incremental indexing | Medium | Phase 0.1 |

### Order 1.4: Parser (S4)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 1.4.1 | BLD-018 | Add support for additional languages (Go, Rust, Java, etc.) | High | 1.1.7 |
| 1.4.2 | BLD-017 | Add proper TypeScript grammar support | High | 1.4.1 |
| 1.4.3 | BLD-020 | Add error reporting for parse failures | Medium | None |
| 1.4.4 | BLD-019 | Store source text in parsed output | Medium | None |
| 1.4.5 | BLD-021 | Implement query-based symbol extraction | Low | 1.4.2 |

### Order 1.5: Normalizer (S6)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 1.5.1 | BLD-025 | Add proper TypeScript normalizer | High | 1.4.2 |
| 1.5.2 | BLD-026 | Fix JS normalizer gaps | High | None |
| 1.5.3 | BLD-027 | Add cross-language canonical normalization | Low | 1.5.2 |

### Order 1.6: Symbols (S7)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 1.6.1 | BLD-028 | Add cross-file symbol resolution | High | Phase 0.2 |
| 1.6.2 | BLD-029 | Add scope and namespace awareness | Medium | 1.6.1 |
| 1.6.3 | BLD-030 | Track line numbers for imports | Low | None |

### Order 1.7: Dependency Graph (S8)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 1.7.1 | BLD-031 | Fix empty exports handling | **Critical** | 1.6.1 |
| 1.7.2 | BLD-032 | Fix absolute import resolution | **Critical** | None |
| 1.7.3 | BLD-033 | Add Node.js import resolution | High | 1.7.2 |
| 1.7.4 | BLD-034 | Add type-based dependency edges | Medium | 1.6.1 |

### Order 1.8: Entity Graph (S9)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 1.8.1 | BLD-036 | Deduplicate import entities | Medium | None |
| 1.8.2 | BLD-035 | Implement CALLS and EXTENDS relations | High | 1.7.4 |
| 1.8.3 | BLD-037 | Add symbol-level entity relations | Medium | 1.7.4 |

### Order 1.9: Storage (S10 + S11)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 1.9.1 | BLD-038 | Add versioning to SCStore | Medium | None |
| 1.9.2 | BLD-039 | Add incremental updates to SCStore | Medium | 1.9.1 |
| 1.9.3 | BLD-040 | Add schema migration system | High | None |
| 1.9.4 | BLD-041 | Add connection pooling | Low | None |
| 1.9.5 | BLD-042 | Add property indexing | Low | 1.9.3 |
| 1.9.6 | BLD-043 | Add time-series queries to EvidenceStore | Medium | None |
| 1.9.7 | BLD-044 | Add evidence deduplication | Medium | None |
| 1.9.8 | BLD-045 | Add evidence TTL and expiry | Low | None |
| 1.9.9 | BLD-046 | Add structured evidence querying | Low | 1.9.3 |

### Phase 1 Verification Gate
- All 3 languages (Python, JS, TS) parse correctly with their specific grammars
- Normalizer receives parsed trees (no re-read from disk)
- Symbol index resolves cross-file references
- Dependency graph resolves both relative AND absolute imports
- Exports loop creates actual dependency edges
- Entity graph creates CALLS and EXTENDS relations
- Storage supports incremental updates (not delete-all)
- Full end-to-end pipeline runs on sample Python project < 5 seconds
- Full end-to-end pipeline runs on sample JS/TS project < 5 seconds

---

## Phase 2 — Intelligence Layer

### Order 2.1: Structural Engine (S12)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 2.1.1 | BLD-047 | Add cyclomatic complexity analysis | High | 1.4.4 (source text) |
| 2.1.2 | BLD-048 | Add cognitive complexity analysis | Medium | 1.4.4 |
| 2.1.3 | BLD-050 | Add coupling metrics beyond raw count | Medium | Phase 1.7 |
| 2.1.4 | BLD-049 | Add cohesion metrics | Low | Phase 1.8 |

### Order 2.2: Evolution Engine (S13)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 2.2.1 | BLD-051 | Fix hotspot detection (broken dead code) | **Critical** | 1.2.1 (per-file tracking) |
| 2.2.2 | BLD-052 | Add per-file change frequency tracking | High | 1.2.1 |
| 2.2.3 | BLD-053 | Add growth trend analysis | Medium | 1.2.1 |
| 2.2.4 | BLD-055 | Add temporal coupling detection | Low | 1.2.1 |
| 2.2.5 | BLD-054 | Add refactoring detection | Low | 1.2.5 |

### Order 2.3: Knowledge Engine (S14)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 2.3.1 | BLD-056 | Fix ownership score calculation (use git blame) | **Critical** | 1.2.2 (blame) |
| 2.3.2 | BLD-057 | Improve bus factor calculation | High | 2.3.1 |
| 2.3.3 | BLD-058 | Add per-file expertise scoring | Medium | 1.2.2 |
| 2.3.4 | BLD-059 | Add knowledge map / knowledge graph | Medium | 2.3.1 |
| 2.3.5 | BLD-060 | Add contributor specialization detection | Low | 2.3.1 |

### Order 2.4: Risk Engine (S15)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 2.4.1 | BLD-061 | Fix test coverage metric | High | None |
| 2.4.2 | BLD-066 | Add unused export detection | Medium | Phase 1.7 |
| 2.4.3 | BLD-063 | Add dependency freshness checking | Medium | 1.4.4 |
| 2.4.4 | BLD-064 | Add code smell detection | Medium | 2.1.1 |
| 2.4.5 | BLD-065 | Calibrate risk score formula | Medium | 2.4.1–2.4.4 |
| 2.4.6 | BLD-062 | Add security risk detection | Medium | 1.4.4 |

### Order 2.5: Reasoning Layer (S16)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 2.5.1 | BLD-067 | Fix dead hotspot_risk rule (evidence mismatch) | **Critical** | 2.2.1 |
| 2.5.2 | BLD-073 | Add insight deduplication | Medium | None |
| 2.5.3 | BLD-068 | Replace hardcoded confidence with dynamic computation | High | Phase 2.1–2.4 |
| 2.5.4 | BLD-070 | Add reasoning pipeline with composable rules | Medium | 2.5.3 |
| 2.5.5 | BLD-069 | Add natural language generation | Medium | 2.5.4 |
| 2.5.6 | BLD-072 | Add explainability output | Low | 2.5.4 |
| 2.5.7 | BLD-071 | Add learning/adaptation | Low | 2.5.4 |

### Phase 2 Verification Gate
- Cyclomatic complexity computed for Python/JS/TS files
- Hotspot detection returns non-empty results for repos with change history
- Ownership scores are per-file (not all files same)
- Test coverage metric is either real coverage or renamed honestly
- No dead insight rules (all 6 rules can trigger given appropriate evidence)
- Confidence values vary based on actual data (not hardcoded)
- All 5 engines return sensible results for sample repos

---

## Phase 3 — Delivery Layer

### Order 3.1: API Expansion (S17)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 3.1.1 | BLD-076 | Add request timeout for long analysis | High | None |
| 3.1.2 | BLD-082 | Add streaming responses for long analysis | Medium | None |
| 3.1.3 | BLD-081 | Add rate limiting | Medium | None |
| 3.1.4 | BLD-083 | Add stored analysis query endpoints | Medium | 1.3.2 |
| 3.1.5 | BLD-080 | Add API versioning | Medium | None |
| 3.1.6 | BLD-079 | Add authentication and authorization | High | None |
| 3.1.7 | BLD-077 | Add WebSocket API | Medium | 3.1.2 |
| 3.1.8 | BLD-078 | Add GraphQL API | Low | 3.1.4 |

### Order 3.2: Frontend (S18)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 3.2.1 | BLD-089 | Add JavaScript bundling (Webpack/Vite) | Medium | None |
| 3.2.2 | BLD-084 | Build React application | High | 3.2.1 |
| 3.2.3 | BLD-088 | Add frontend test suite | Medium | 3.2.2 |
| 3.2.4 | BLD-085 | Add graph visualization component | Medium | 3.2.2 |
| 3.2.5 | BLD-086 | Add evidence explorer | Medium | 3.2.2 |
| 3.2.6 | BLD-087 | Add search and query UI | Low | 3.2.2, 3.1.4 |

### Order 3.3: Deployment & Integration (S20 + S21)

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 3.3.1 | BLD-095 | Fix Dockerfile (add build deps) | **Critical** | None |
| 3.3.2 | BLD-099 | Add configuration management | High | None |
| 3.3.3 | BLD-098 | Add structured logging | Medium | 3.3.2 |
| 3.3.4 | BLD-097 | Add monitoring and observability | Medium | 3.3.3 |
| 3.3.5 | BLD-096 | Add CI/CD pipeline | High | 3.3.1 |
| 3.3.6 | BLD-105 | Fix CORS configuration | High | None |
| 3.3.7 | BLD-101 | Add edge case handling for empty repos | High | None |
| 3.3.8 | BLD-103 | Add edge case handling for symlinks | Medium | 1.1.2 |

### Phase 3 Verification Gate
- `POST /analyze` times out gracefully (>60s returns 503)
- API has version prefix (`/v1/analyze`)
- Auth works (authenticated requests pass, unauthenticated get 401)
- React app serves and renders all components
- Graph visualization renders for a sample project
- Dockerfile builds successfully
- CI/CD pipeline passes (tests + lint + build)
- Full integration test suite passes

---

## Phase 4 — Testing & Quality

| Order | ID | Title | Priority | Depends On |
|-------|----|-------|----------|------------|
| 4.1 | BLD-090 | Add integration tests for full pipeline | **Critical** | Ongoing (parallel) |
| 4.2 | BLD-100 | Add E2E integration test suite | **Critical** | 4.1 |
| 4.3 | BLD-091 | Add E2E tests against real repositories | High | 4.2 |
| 4.4 | BLD-092 | Add performance/benchmarking tests | Medium | 4.1 |
| 4.5 | BLD-093 | Add security tests | High | None |
| 4.6 | BLD-094 | Consolidate duplicate/trivial tests | Low | 4.1 |

### Phase 4 Verification Gate
- Integration tests cover all 21 sprints
- E2E tests pass against 3 sample repos (Python, JS/TS, mixed)
- Performance benchmarks established (baseline timing)
- Security tests pass (no path traversal, no command injection)

---

## Summary

```
Phase 0: Critical Bugfixes (7 items)
    ↓ verification gate
Phase 1: Core Pipeline Stabilization (38 items)
    ├── 1.1 Discovery      (9 items)
    ├── 1.2 Git History     (5 items)
    ├── 1.3 Indexer         (2 items)
    ├── 1.4 Parser          (5 items)
    ├── 1.5 Normalizer      (3 items)
    ├── 1.6 Symbols         (3 items)
    ├── 1.7 Dependency Graph (4 items)
    ├── 1.8 Entity Graph    (3 items)
    └── 1.9 Storage         (9 items)
    ↓ verification gate
Phase 2: Intelligence Layer (24 items)
    ├── 2.1 Structural (4)
    ├── 2.2 Evolution   (5)
    ├── 2.3 Knowledge   (5)
    ├── 2.4 Risk        (6)
    └── 2.5 Reasoning   (7)
    ↓ verification gate
Phase 3: Delivery Layer (18 items)
    ├── 3.1 API Expansion     (8)
    ├── 3.2 Frontend         (6)
    └── 3.3 Deploy & Integrate (8)
    ↓ verification gate
Phase 4: Testing & Quality (6 items)
```

**Total backlog items: 105**
**Phases: 5 (0–4)**
**Estimated phases to complete before production readiness: All 5**
