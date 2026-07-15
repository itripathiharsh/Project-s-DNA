================================================================================
# 05 SCM Validation
================================================================================

# SCM Validation

## Purpose

SCM validation ensures the Software Cognition Model maintains data integrity — that entities are uniquely identifiable, relationships are consistent, evidence chains are complete, and the temporal store is append-only.

---

## Validation Checks

| Check | What It Detects | Frequency |
|---|---|---|
| Entity uniqueness | Duplicate entity IDs | Every write |
| Relationship consistency | Orphaned edges (missing source or target) | Every write |
| Evidence chain completeness | Evidence refs pointing to non-existent nodes | Every write |
| Temporal immutability | Modified past events | Nightly CI |
| Referential integrity | Insight references orphaned evidence | Nightly CI |
| Schema conformance | Non-conforming data in JSONB fields | Every write |

## Example

```python
def test_evidence_chain_integrity():
    # Simulate a reasoning run that creates an insight
    insight = reasoning_pipeline.run(question="...", scm=test_scm)
    
    # Every evidence reference must exist
    for ref in insight.evidence_refs:
        evidence = test_scm.get_evidence(ref)
        assert evidence is not None, f"Missing evidence: {ref}"
        
        # Every evidence must have a raw data reference
        assert evidence.raw_data.ref is not None
```
