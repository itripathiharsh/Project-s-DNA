================================================================================
# 03 Integration Testing
================================================================================

# Integration Testing

## Purpose

Integration tests verify that modules work correctly together — that the API Gateway routes to the correct service, that the SCM returns the expected data shape, and that the full pipeline error propagates correctly.

---

## Test Boundaries

| Boundary | Test | Example |
|---|---|---|
| API → Service | Request → response contract | `POST /v1/reason/question` returns 200 with `FormattedInsight` |
| Engine → SCM | Engine writes evidence → SCM stores it | Run engine, query SCM, verify evidence |
| Reasoning → SCM | Insight written → can be queried | Run reasoning, query insight |
| Service → Service | Orchestrator calls engine → engine completes | Mock engine, verify orchestrator flow |

## Environment

| Component | Integration Test |
|---|---|
| SCM | In-memory SQLite |
| API Gateway | TestClient (FastAPI) |
| Cognitive Engines | Real engine, fixture repository |
| Reasoning Layer | Real pipeline, mock LLM |
| Frontend | Vitest + MSW (mock service worker) |

## Example

```python
# test_reasoning_pipeline.py
def test_question_to_insight_flow():
    # Arrange: seed SCM with evidence
    scm = create_test_scm()
    scm.write_evidence(trace_evidence())

    # Act: run the reasoning pipeline
    result = reasoning_pipeline.run(
        question="What is the error rate?",
        scm=scm,
    )

    # Assert: insight contains the evidence reference
    assert result.confidence > 0.0
    assert "trace_001" in result.evidence_refs
```
