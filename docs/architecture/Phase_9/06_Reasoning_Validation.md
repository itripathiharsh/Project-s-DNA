================================================================================
# 06 Reasoning Validation
================================================================================

# Reasoning Validation

## Purpose

Reasoning validation tests the full pipeline end-to-end — verifying that evidence flows correctly through all six stages, that the LLM produces valid structured output, and that the deterministic fallback works when the LLM is unavailable.

---

## Validation Scenarios

| Scenario | Tests | Frequency |
|---|---|---|
| Happy path | Question → insight with evidence chain | PR to develop |
| Low confidence | Ambiguous question → LOW confidence | PR to develop |
| Insufficient evidence | Question about unanalyzed entity → INSUFFICIENT_EVIDENCE | Nightly CI |
| LLM failure | Ollama unavailable → deterministic fallback | Nightly CI |
| Malformed LLM output | LLM returns bad JSON → retry + fallback | Nightly CI |
| Empty evidence set | Context builder returns zero items → early return | Nightly CI |
| Conflicting evidence | Two engines disagree → conflict surfaced in insight | Weekly CI |

## Example

```python
def test_deterministic_fallback():
    # Arrange: LLM interface returns failure
    llm = MockLLM(available=False)
    pipeline = ReasoningPipeline(llm=llm, scm=test_scm)
    
    # Act
    result = pipeline.run(question="What is the error rate?")
    
    # Assert: deterministic fallback
    assert result.fallback_reason == "LLM_UNAVAILABLE"
    assert result.confidence == 0.0
    assert len(result.evidence_chain.supporting_evidence) > 0  # evidence still present
```
