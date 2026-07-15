================================================================================
# 01 Testing Overview
================================================================================

# Testing Overview

## Purpose

Testing is the primary mechanism for ensuring correctness in Project DNA. Because Cognitive Engines produce deterministic evidence that feeds into the SCM and Reasoning Layer, a defect in any stage propagates upward and erodes trust in every insight. This document defines the testing strategy across all system layers, the test pyramid, the environments, and the quality gates.

---

## Scope

### In Scope

- Test pyramid for Project DNA
- Testing levels (unit, integration, validation, evaluation, performance)
- Test environments
- Quality gates for each layer
- Test data strategy
- CI integration

### Out of Scope

- Specific test implementations (Phase 9/02–09)
- Individual test frameworks

### Phase Dependencies

The testing strategy relies on components defined in earlier phases:

| Dependency | Phase | Relevance |
|---|---|---|
| **SCM Data Model** | Phase 3 | Evidence schema, entity types, relationships validated by SCM Validation |
| **Cognitive Engines** | Phase 4 | Engine interface contract, evidence output schema verified by Engine Validation |
| **Reasoning Pipeline** | Phase 5 | Pipeline stages (Context Builder, LLM Inference, Response Parser) tested via Reasoning Validation |
| **API Gateway** | Phase 6 | REST, WebSocket, and GraphQL endpoints tested via Integration Tests |

---

## Test Pyramid

```
              ╱╲
             ╱  ╲          AI Evaluation (Phase 9/07)
            ╱    ╲         Performance + Benchmark (Phase 9/08, 09)
           ╱      ╲
          ╱────────╲       Integration + Validation (Phase 9/03, 04, 05, 06)
         ╱          ╲
        ╱────────────╲     Unit Tests (Phase 9/02)
       ╱              ╲
      ╱────────────────╲
```

| Level | Count | Speed | Purpose |
|---|---|---|---|
| Unit | Thousands | Milliseconds | Individual functions, classes, components |
| Integration | Hundreds | Seconds | Module boundaries, API contracts |
| Validation | Dozens | Minutes | Engine output correctness, SCM integrity |
| AI Evaluation | Tens | Minutes | LLM output quality, hallucination rate |
| Performance | Few | Minutes-Hours | Latency, throughput, resource usage |

---

## Testing by Layer

| Layer | Unit | Integration | Validation | AI Eval | Perf |
|---|---|---|---|---|---|
| Cognitive Engines | ✅ | ✅ | ✅ | — | ✅ |
| SCM | ✅ | ✅ | ✅ | — | ✅ |
| Reasoning | ✅ | ✅ | — | ✅ | ✅ |
| API Gateway | ✅ | ✅ | — | — | ✅ |
| Frontend | ✅ | ✅ | — | — | ✅ |
| CLI | ✅ | ✅ | — | — | — |

---

## Quality Gates

| Gate | Enforced At | Fails If |
|---|---|---|
| Unit tests pass | Pre-commit, CI | Any test fails |
| Lint passes | Pre-commit, CI | Any lint rule violation |
| Integration tests pass | PR to develop | Any test fails |
| Engine validation | Nightly CI | Evidence output changes unexpectedly |
| AI evaluation | Weekly CI | Hallucination rate > threshold |
| Performance regression | Release CI | Per-metric thresholds — see Phase 9/08 |

---

## Test Data Strategy

| Data Type | Source | Used For |
|---|---|---|
| Synthetic repositories | Generated fixtures | Engine unit tests |
| Historical snapshots | Real repository snapshots | Integration tests, validation |
| Benchmark suites | Curated open-source repos | Performance, AI evaluation |
| Mock SCM data | JSON fixtures | Reasoning, API, frontend tests |

---

## The Testing Doctrine

> **Every level of the system is tested at the appropriate granularity — units for logic, integration for contracts, validation for correctness, evaluation for quality, and benchmarks for performance. Deterministic tests (unit, integration, validation) must be reproducible: same input → same output, always. Probabilistic evaluation (AI eval, Phase 9/07) uses benchmark datasets with statistical thresholds rather than pass/fail assertions. All tests run in CI. A deterministic test failure means a bug, not a flake. If a deterministic test is flaky, it is fixed or removed — never ignored.**
