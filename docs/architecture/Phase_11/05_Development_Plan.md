================================================================================
# 05 Development Plan
================================================================================

# Development Plan

## Purpose

The development plan specifies how to build Project DNA in the correct order — which components to build first, what to parallelize, and how to validate each layer before depending on it.

---

## Build Order

```
Phase 1: Foundation (Weeks 1–12)
├── Week 1-4:    E-01 Core SCM
├── Week 5-7:    E-02 Structural Engine
├── Week 8-9:    E-03 Evidence Storage
├── Week 10-12:  E-04 REST API + E-05 CLI
└── Validation:  smoke_test.py (import repo, query evidence)

Phase 2: Reasoning (Weeks 13–20)
├── Week 13-14:  E-06 Ollama Integration
├── Week 15-17:  E-07 Prompt Architecture + E-08 Context Builder
├── Week 18-20:  E-09 Reasoning Pipeline
└── Validation:  Ask 10 questions, verify all produce grounded insights

Phase 3: Frontend (Weeks 21–28)
├── Week 21-23:  E-10 Frontend Foundation
├── Week 24-26:  E-11 Dashboard + E-12 Evidence Explorer
├── Week 27-28:  E-13 Search UI + E-14 Graph Visualization
└── Validation:  User can find any insight in 3 clicks

Phase 4: Polish (Weeks 29–36)
├── Week 29-30:  E-15 Testing + E-16 Performance
├── Week 31-32:  E-17 AI Evaluation
├── Week 33-34:  E-18 Packaging
└── Week 35-36:  E-19 Documentation
└── Validation:  All tests pass, benchmarks meet budgets, packages published
```

## Parallelization

| Track 1 (Backend) | Track 2 (Frontend) |
|---|---|
| E-01 Core SCM | — |
| E-02 Structural Engine | — |
| E-03 Evidence Storage | — |
| E-04 REST API | — |
| E-06, E-07, E-08, E-09 (Reasoning) | E-10, E-11, E-12, E-13, E-14 (Frontend) |
| E-15, E-16, E-17 (Testing + Perf) | E-18, E-19 (Packaging + Docs) |

## Dependency Graph

```
E-01 → E-02 → E-03 → E-04 → E-05 (CLI)
                  ↓
E-06 → E-07 → E-08 → E-09
                        ↓
E-10 → E-11 → E-12 → E-13 → E-14
                                    ↓
E-15, E-16, E-17, E-18, E-19 (parallel)
```
