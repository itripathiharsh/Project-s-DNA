================================================================================
# 07 AI Evaluation
================================================================================

# AI Evaluation

## Purpose

AI evaluation measures the quality of LLM-generated outputs — hallucination rate, instruction adherence, and reasoning accuracy. Unlike deterministic tests, AI evaluation uses probabilistic metrics and benchmark datasets to track model performance over time.

---

## Evaluation Dimensions

| Dimension | Metric | Target | Measurement |
|---|---|---|---|
| Hallucination rate | % of claims not supported by evidence | < 5% | Manual review of sample |
| Instruction adherence | % outputs matching schema | > 95% | Automated schema validation |
| Reasoning accuracy | % conclusions matching human judgment | > 80% | Expert review |
| Sensitivity | % of relevant evidence cited | > 70% | Coverage analysis |
| Conciseness | Token efficiency (output tokens / evidence tokens) | < 0.5 | Token counting |

## Benchmark Dataset

A curated set of 100 question-answer pairs across all reasoning types, with verified evidence sets and human-authored reference answers:

| Type | Count | Source |
|---|---|---|
| simple_qa | 20 | Function/class lookups |
| synthesis | 30 | Root cause analysis |
| decision_support | 20 | Refactor vs. rewrite |
| risk_evaluation | 15 | Security/complexity assessment |
| prediction | 15 | Trend extrapolation |

## Evaluation Pipeline

```python
def evaluate_model(model_tag: str, benchmark: Benchmark) -> EvaluationReport:
    results = []
    for example in benchmark.cases:
        # Run reasoning pipeline
        insight = pipeline.run(question=example.question, evidence=example.evidence)
        
        # Check hallucination rate
        unsupported = insight.claims - example.valid_evidence_refs
        hallucination_rate = len(unsupported) / len(insight.claims)
        
        # Check schema adherence
        valid_schema = validate_schema(insight.raw_output)
        
        results.append(EvaluationResult(
            hallucination_rate=hallucination_rate,
            valid_schema=valid_schema,
            duration_ms=insight.duration_ms,
        ))
    
    return EvaluationReport.aggregate(results)
```

## Regression Alerts

| Condition | Action |
|---|---|
| Hallucination rate > 10% | Block release. Investigate model changes. |
| Instruction adherence < 90% | Block release. Review prompt templates. |
| Reasoning accuracy < 70% | Flag for review. May indicate model drift. |
| New model version available | Run full evaluation, compare to baseline. |
