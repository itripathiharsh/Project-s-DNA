================================================================================
# 10 Glossary
================================================================================

# Glossary

## Purpose

This glossary defines key terms introduced across Phase 9 (Testing).

---

## A

### AI Evaluation

The process of measuring LLM output quality — hallucination rate, instruction adherence, reasoning accuracy — using benchmark datasets with human-authored reference answers. Run weekly in CI. Defined in Phase 9/07.

---

## B

### Benchmarking

Performance measurement of specific subsystems under controlled workloads. Results compared against a stored baseline. Regression threshold: > 10% slowdown fails the build. Defined in Phase 9/09.

---

## E

### Engine Validation

A testing layer that verifies Cognitive Engines produce correct, deterministic evidence. Uses snapshot testing (compare output to stored baseline) and schema validation (every evidence node conforms to Phase 4 schema). Defined in Phase 9/04.

---

## I

### Integration Testing

Tests that verify module boundaries work correctly — API → service, engine → SCM, reasoning → SCM. Uses in-memory databases and mock LLMs. Defined in Phase 9/03.

---

## P

### Performance Testing

System-level tests that measure latency, throughput, and resource usage under load. Uses k6 for API tests and Lighthouse for frontend. Warning at 1.5x baseline, blocking at 3x. Defined in Phase 9/08.

---

## U

### Unit Testing

Tests of individual functions, classes, and components in isolation. Coverage target: 90%+ for Python/Rust, 80%+ for TypeScript. Framework: pytest, Vitest, cargo test. Defined in Phase 9/02.
