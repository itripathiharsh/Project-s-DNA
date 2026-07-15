================================================================================
# 09 Benchmarking
================================================================================

# Benchmarking

## Purpose

Benchmarks measure the performance of specific subsystems against controlled workloads. They provide baselines for performance budgets and detect regressions from code changes.

---

## Benchmark Suites

| Suite | What It Measures | Frequency | Format |
|---|---|---|---|
| Engine throughput | Evidence items per second per engine | Per commit | pytest-benchmark |
| SCM query speed | Query latency by complexity | Per commit | pytest-benchmark |
| LLM inference | Tokens per second (by model, hardware) | Weekly | Custom script |
| Graph layout | Layout time by node count | Per commit | Custom script |
| Evidence chain | Chain resolution time by depth | Per commit | Custom script |

## Baseline Tracking

Benchmark results are compared against a stored baseline:

```bash
# Run benchmarks with comparison
pytest --benchmark-compare --benchmark-compare-fail=min:10%
# Fails if any benchmark is > 10% slower than baseline
```

## Example

```python
# test_engine_benchmarks.py
def test_structural_engine_speed(benchmark):
    engine = StructuralCognitionEngine()
    repo = fixture_repo("large-python-project")
    
    result = benchmark(engine.run, repo)
    
    # Assert minimum throughput
    assert len(result.evidence) > 100  # Produced meaningful evidence
```

## Performance Budget

| Benchmark | Baseline | Budget |
|---|---|---|
| Structural engine (large repo) | 12s | < 30s |
| SCM evidence query (1000 items) | 45ms | < 100ms |
| LLM 7B Q4 inference (500 tokens) | 3.4s | < 8s |
| Dependency graph layout (500 nodes) | 200ms | < 500ms |
| Frontend initial bundle | 180 KB | < 250 KB |
