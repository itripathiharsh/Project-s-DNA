================================================================================
# 02 Unit Testing
================================================================================

# Unit Testing

## Purpose

Unit tests verify individual functions, classes, and components in isolation. They are the first line of defense against defects and the foundation of the test pyramid.

---

## Standards

| Property | Python | TypeScript | Rust |
|---|---|---|---|
| Framework | pytest | Vitest | cargo test |
| Coverage target | 90%+ (engine, scm) | 80%+ (utils, hooks) | 90%+ |
| File location | `tests/` per module | `.test.tsx` alongside | `tests/` per crate |
| Mocking | pytest-monkeypatch | vi.mock | manual traits |

## What to Test

| Test | Example |
|---|---|
| Pure functions | `calculate_relevance_score()` — input → output |
| Edge cases | Empty list, None/undefined, max values |
| Error paths | Invalid input → correct error type |
| State transitions | `insight.status` valid transitions |
| Component rendering | Given props → rendered output |

## What Not to Test

- Framework internals (React, FastAPI, SQLite).
- Third-party library behavior.
- Configuration values (test the code that reads config, not the values).
- Trivial getters/setters (test the behavior they enable, not the accessor).

## Example

```python
# test_evidence_ranking.py
def test_relevance_score_with_exact_match():
    score = calculate_relevance_score(
        entity_match=1.0, recency=0.8, confidence=0.9
    )
    assert score == pytest.approx(0.4 * 1.0 + 0.25 * 0.8 + 0.2 * 0.9)
```
