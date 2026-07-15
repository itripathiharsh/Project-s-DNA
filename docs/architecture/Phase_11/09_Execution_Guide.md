================================================================================
# 09 Execution Guide
================================================================================

# Execution Guide

## Purpose

The execution guide is the authoritative playbook for building Project DNA. It consolidates the build order, task structure, validation gates, and quality standards into a single actionable reference.

---

## Build Sequence

| Step | What to Build | Validation Gate |
|---|---|---|
| 1 | Core SCM data model + scanner | `pytest tests/test_scm_model.py` |
| 2 | Dependency graph builder | Graph has correct edges for known repos |
| 3 | Evidence storage + query API | `pytest tests/test_scm_storage.py` |
| 4 | REST API endpoints | `pytest tests/test_api.py` |
| 5 | Structural Engine | Evidence count matches expectations |
| 6 | CLI `dna serve` | `dna health` returns healthy |
| 7 | Ollama integration | Model responds to test prompt |
| 8 | Prompt templates | Output follows schema |
| 9 | Context builder | Evidence is correctly injected |
| 10 | Reasoning pipeline | 10/10 test questions pass |
| 11 | Frontend app | UI loads and shows dashboard |
| 12 | Evidence Explorer | Click through 3 insights |
| 13 | Search UI | Search returns expected results |
| 14 | Graph visualization | Graph renders with correct nodes |
| 15 | Full test suite | `pytest && vitest run && cargo test` |
| 16 | Performance benchmarks | All budgets met |
| 17 | AI evaluation | All metrics pass thresholds |
| 18 | Packaging | npm install, docker pull, tauri build |
| 19 | Documentation | All 12 phases complete |

## Quality Gates

| Gate | Requirement |
|---|---|
| **Code Review** | Every PR must have 1 approval |
| **Tests Pass** | CI must be green |
| **No Regressions** | Benchmarks within 10% of baseline |
| **Docs Updated** | Relevant phase docs updated with PR |
| **Changelog** | Entry added to CHANGELOG.md |

## Build Command Reference

```bash
# Python backend
pip install -e ".[dev]"
pytest               # Unit + integration tests
pytest --benchmark   # Run benchmarks

# TypeScript frontend
cd frontend && npm install
npm run dev           # Dev server
npm run build         # Production build
npm run test          # Vitest
npm run lint          # ESLint

# Rust components
cargo test
cargo clippy

# Full pre-release
scripts/ci.sh         # Full CI pipeline locally
```
