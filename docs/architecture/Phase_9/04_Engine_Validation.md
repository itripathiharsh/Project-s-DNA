================================================================================
# 04 Engine Validation
================================================================================

# Engine Validation

## Purpose

Engine validation ensures that every Cognitive Engine produces correct, deterministic evidence for known inputs. Because engines are the foundation of all reasoning, their correctness is verified through snapshot testing and schema validation.

---

## Validation Strategy

| Method | Detects | Frequency |
|---|---|---|
| Schema validation | Malformed evidence output | Every run |
| Snapshot testing | Unintended output changes | Nightly CI |
| Cross-engine consistency | Contradictory evidence | Nightly CI |
| Coverage analysis | Missing evidence types | Weekly CI |

## Snapshot Testing

Each engine is run against a set of fixture repositories. The output evidence set is compared to a stored snapshot:

```python
def test_structural_engine_snapshot():
    engine = StructuralCognitionEngine()
    result = engine.run(fixture_repo("python-flask-app"))
    
    # First run: --snapshot-create stores the output
    # Subsequent runs: compare to stored snapshot
    assert_snapshot(result.evidence, "structural_python_flask")
```

When the engine algorithm changes intentionally, snapshots are updated:

```bash
pytest --snapshot-update
```

## Schema Validation

Every evidence node produced by any engine must conform to the schema defined in Phase 4:

```python
def test_evidence_schema():
    engine = StructuralCognitionEngine()
    result = engine.run(fixture_repo("simple-python-project"))
    
    for evidence in result.evidence:
        assert evidence.id is not None
        assert evidence.type in EVIDENCE_TYPE_TAXONOMY
        assert 0.0 <= evidence.confidence <= 1.0
        assert evidence.source.engine == "structural_cognition"
```
