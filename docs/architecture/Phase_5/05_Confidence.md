================================================================================
# 05 Confidence
================================================================================

# Confidence

## Purpose

Confidence is the measure of how reliable a reasoning output is, derived entirely from the evidence that supports it — never from the LLM's self-attribution. This document defines how confidence is computed, propagated, and communicated across the reasoning pipeline, ensuring every insight carries a transparent, evidence-grounded reliability score.

---

## Scope

### In Scope

- Confidence sources and their weights
- Evidence confidence model (float 0.0–1.0)
- Insight confidence computation
- Confidence propagation through pipeline stages
- Mapping internal confidence to display levels
- Thresholds for pipeline behavior
- Response Parser confidence recalculation after validation
- Edge cases (coverage failure, conflicting evidence, fallback)

### Out of Scope

- Cognitive Engine confidence generation (Phase 4)
- Prompt design for confidence (Phase 5/03)
- Explanation formatting of confidence (Phase 5/06)
- UI display of confidence (Phase 1)

---

## Background

Phase 5/01 established the foundational confidence model:
- **Per-evidence confidence**: Each evidence node carries a float 0.0–1.0 representing the producing engine's certainty. Levels: Certain (1.0), High (0.85–0.99), Medium (0.60–0.84), Low (0.30–0.59), Speculative (0.0–0.29).
- **Insight confidence**: `weighted_average(evidence_confidences) × evidence_coverage`
- **Confidence bounds**: Bounded by the highest and lowest evidence in the supporting chain. Coverage < 0.5 triggers low-confidence flag.
- **Display**: Insights < 0.5 shown with caveat. Deterministic fallbacks marked as "evidence summary."

Phase 5/03 defined the output schema where confidence appears as a string field per reasoning type: `"HIGH"`, `"MEDIUM"`, `"LOW"`, `"INSUFFICIENT_EVIDENCE"`, or `"UNAVAILABLE"`.

Phase -1 Principle 4 mandates that confidence is never LLM-generated — it must be computed from evidence structure, not from the model's self-assessment.

---

## Confidence Architecture

```
Evidence Nodes (from SCM)
    │ confidence: float (0.0–1.0)
    │
    ▼
Context Builder
    │  - Assembles evidence with scores
    │  - Tags conflicts, staleness, coverage
    ▼
Prompt Orchestrator
    │  - Selects evidence, formats prompt
    ▼
LLM Inference
    │  - LLM produces answer with evidence_refs
    │  - LLM does NOT produce confidence scores
    ▼
Response Parser  ◄── Primary confidence computation
    │  - Parses LLM response
    │  - Computes insight_confidence from evidence
    │  - Recalculates based on validation results
    │  - Trims confidence for unsubstantiated claims
    ▼
Explanation Formatter
    │  - Maps float confidence to display level
    │  - Attaches confidence breakdown for transparency
```

Confidence is computed in the Response Parser, after the LLM response is parsed and validated. It is never read from the LLM output.

---

## Confidence Sources

### Evidence Confidence (Per-Node)

Each evidence node in the SCM carries a confidence score set by its producing engine:

| Label | Range | Meaning | Source |
|---|---|---|---|
| Certain | 1.0 | Direct observation, no inference | Static analysis, compiler output, lockfile |
| High | 0.85–0.99 | Strong inference from multiple correlated sources | Cross-validated patterns, confirmed trends |
| Medium | 0.60–0.84 | Reasonable inference from limited data | Single-source patterns, partial matches |
| Low | 0.30–0.59 | Weak inference, high uncertainty | Heuristics, incomplete data |
| Speculative | 0.00–0.29 | Hypothesis requiring validation | Best-guess defaults, extrapolation |

These values are set by the Cognitive Engines (Phase 4) and stored in the SCM. The Reasoning Layer inherits them unchanged — it never modifies evidence confidence.

### Coverage

Coverage is the fraction of claims in the insight that are directly supported by evidence. It is computed during Response Parser validation:

```
coverage = count(supported_claims) / count(total_claims)
```

A "supported claim" has an evidence reference in the LLM response that matches a real evidence node in the assembled context. Unsupported claims are those where:
- The evidence reference is invalid (no matching evidence node).
- The claim is not accompanied by any evidence reference.
- The claim contradicts the referenced evidence.

### Consistency (Penalty Factor)

When evidence nodes conflict, confidence is penalized:

```
consistency_penalty = 1.0 - (conflict_severity × conflict_ratio)

where:
  conflict_ratio = count(conflicting_pairs) / count(total_evidence_pairs)
  conflict_severity = 0.10 for LOW, 0.25 for MEDIUM, 0.50 for HIGH
```

### Recency (Adjustment Factor)

When evidence is stale relative to the question's time sensitivity:

```
recency_factor = 1.0 - stale_ratio × stale_penalty

where:
  stale_ratio = count(stale_evidence) / count(total_evidence)
  stale_penalty = depends on recency (0.10 for < 7 days stale, 0.30 for > 30 days)
```

---

## Insight Confidence Computation

### Base Formula

```
insight_confidence = weighted_average(evidence_confidences)
                   × coverage
                   × consistency_penalty
                   × recency_factor
```

### Weighted Average of Evidence Confidences

Each evidence node referenced in the insight contributes to the weighted average:

```
weighted_average = sum(weight_i × confidence_i) / sum(weight_i)
```

Weights are determined by the evidence's role in the insight:

| Role | Weight | Condition |
|---|---|---|
| Primary support | 1.0 | Evidence directly cited as supporting the main claim |
| Secondary support | 0.5 | Evidence cited in supporting patterns or context |
| Conflict evidence | 0.3 | Evidence cited as conflicting with other evidence |
| Background | 0.2 | Evidence present in context but not directly cited |

### Activation of Penalty Factors

| Factor | Applied When | Impact |
|---|---|---|
| Coverage | Always | Multiplicative — erodes confidence for unsupported claims |
| Consistency | Conflicts exist in evidence set | Up to 0.5× for HIGH conflicts |
| Recency | Stale evidence in set | Up to 0.7× for very stale evidence |

### Confidence Bounds

Regardless of the computed value, `insight_confidence` is clamped:

| Bound | Rule |
|---|---|
| Upper bound | Cannot exceed the maximum confidence of any supporting evidence |
| Lower bound | Cannot fall below the minimum confidence of any supporting evidence |
| Coverage floor | If coverage < 0.5, insight_confidence ≤ 0.49 (forced to LOW) |

---

## Mapping to Display Levels

The internal float confidence is mapped to a display level for the output schema:

| Float Range | Display Level | Meaning |
|---|---|---|
| 0.80 – 1.00 | `HIGH` | Strong evidence support. Multiple sources corroborate. |
| 0.50 – 0.79 | `MEDIUM` | Moderate support. Some claims unsubstantiated or conflicting. |
| 0.00 – 0.49 | `LOW` | Weak support. High uncertainty or low coverage. |
| — | `INSUFFICIENT_EVIDENCE` | No evidence was available for the query. |
| — | `UNAVAILABLE` | LLM inference failed; deterministic fallback used. |

### Special Display Levels

| Level | Trigger | Output Behavior |
|---|---|---|
| `INSUFFICIENT_EVIDENCE` | Context Builder returns zero evidence | No LLM call. Deterministic "no evidence" response. |
| `UNAVAILABLE` | LLM inference fails after retries | Deterministic evidence summary. Marked as "Evidence Summary (AI unavailable)." |
| `FALLBACK` | Response Parser validation fails | Deterministic evidence summary. Marked as "Evidence Summary (validation failed)." |

### UI Display Rules

| Confidence Level | UI Treatment |
|---|---|
| HIGH | Normal presentation. Confidence indicator green. |
| MEDIUM | Normal presentation. Confidence indicator yellow. |
| LOW | Explicit caveat banner: "This insight is based on limited evidence." |
| INSUFFICIENT_EVIDENCE | Informational message. No insight rendered. |
| UNAVAILABLE | Warning banner. No AI insight, evidence list shown. |

---

## Pipeline Integration

### Stage: Intent Recognition

Confidence contribution: None. Intent is a parsing step, not a confidence source.

### Stage: Context Builder

Confidence contribution: Assembles evidence with per-node confidence scores. Computes:
- `evidence_count`
- `evidence_confidences` (list of floats)
- `conflict_ratio` and `conflict_severity`
- `stale_ratio`
- `coverage` (set to 1.0 initially — will be recomputed after validation)

These values are stored in `AssembledContext.metadata` and passed to the Response Parser.

### Stage: Prompt Orchestrator

Confidence contribution: None. Prompt assembly does not alter confidence.

### Stage: LLM Inference

Confidence contribution: None. The LLM does NOT output confidence scores. The model's generation parameters (temperature 0.2) are set to minimize variation, but the LLM's output text is treated as unvalidated claims until the Response Parser processes them.

### Stage: Response Parser (Primary Computation)

The Response Parser computes the final insight confidence:

```
1. Extract claims from LLM response
2. For each claim, check evidence_refs against assembled context
3. Compute coverage = supported_claims / total_claims
4. Compute weighted_average of cited evidence confidences
5. Retrieve consistency_penalty and recency_factor from context metadata
6. Compute insight_confidence = weighted_average × coverage × consistency_penalty × recency_factor
7. Apply bounds (upper/lower evidence bounds, coverage floor)
8. Map float to display level
```

**Example computation:**

```jsonc
{
    "evidence_confidences": [0.95, 0.87, 0.72],    // from 3 cited evidence nodes
    "weights": [1.0, 0.5, 0.5],                      // primary, secondary, secondary
    "weighted_average": 0.86,
    "coverage": 0.80,                                 // 4 of 5 claims supported
    "consistency_penalty": 0.90,                      // LOW conflict present
    "recency_factor": 1.0,                            // no stale evidence
    "insight_confidence": 0.86 × 0.80 × 0.90 × 1.0 = 0.62,
    "display_level": "MEDIUM"
}
```

### Stage: Explanation Formatter

Receives the computed `insight_confidence` and `display_level`. Formats the confidence breakdown for user visibility:

```
Confidence: MEDIUM (0.62)

Breakdown:
  - Evidence strength: 0.86 (weighted average of 3 evidence items)
  - Coverage: 0.80 (4 of 5 claims supported)
  - Consistency: 0.90 (1 minor conflict detected)
  - Recency: 1.00 (all evidence current)
```

---

## Thresholds for Pipeline Behavior

| Threshold | Condition | Pipeline Action |
|---|---|---|
| `coverage < 0.5` | More than half of claims unsupported | Force display to LOW. Add caveat. |
| `insight_confidence < 0.30` | Very weak evidence support | Consider deterministic fallback. Add strong caveat. |
| `max_evidence_confidence < 0.50` | No high-confidence evidence exists | Flag insight as "exploratory." All claims tentative. |
| `conflict_severity = HIGH` | Irreconcilable evidence contradictions | Display both interpretations with their confidences. |
| `LLM validation failure` | Response fails to parse or validate | Fallback to deterministic evidence summary. |

### Deterministic Fallback Decision

The Response Parser decides whether to use deterministic fallback:

```
if (parse_failure) OR (validation_failure_after_repair) OR (coverage < 0.3):
    → Fallback to deterministic evidence summary
    → confidence.display_level = "UNAVAILABLE" or "FALLBACK"
```

---

## Edge Cases

### No Evidence Available

```
evidence = []
coverage = 0  (no claims to check)
insight_confidence = 0.0
display_level = "INSUFFICIENT_EVIDENCE"
Pipeline action: No LLM call, return early.
```

### All Evidence is Speculative

```
evidence_confidences = [0.15, 0.22, 0.10]
max_confidence = 0.22
weighted_average = 0.16
coverage = 1.0 (all claims reference evidence, but evidence is weak)
insight_confidence = 0.16
display_level = "LOW"
Pipeline action: Present with strong caveat. Label as "exploratory."
```

### All LLM Claims are Unsupported

```
coverage = 0.0
insight_confidence = 0.0 → forced 0.0
display_level = "LOW"
Pipeline action: Fallback to deterministic. LLM output discarded.
```

### Conflicting Evidence with Equal Support

```
evidence_a.confidence = 0.90
evidence_b.confidence = 0.85
conflict_severity = HIGH
consistency_penalty = 0.50
insight_confidence = weighted_average(0.90, 0.85) × 1.0 × 0.50 × 1.0 = 0.44
display_level = "LOW"
Pipeline action: Display both interpretations with their individual confidences.
```

### Stale Evidence Only

```
evidence is 60 days old for a real-time question
recency_factor = 1.0 - 1.0 × 0.30 = 0.70
insight_confidence = adjusted downward by 30%
Pipeline action: Tag insight as "based on historical data."
```

### Fallback Mode

When LLM inference fails or response validation fails catastrophically:

```
insight_confidence = 0.0
display_level = "UNAVAILABLE" or "FALLBACK"
Pipeline action: Format the evidence summary directly from AssembledContext.
No LLM insight is presented.
```

---

## Future Work

### Evidence Calibration (V2)

Track how often HIGH-confidence insights are validated by user actions (e.g., user accepts a refactor recommendation) and adjust evidence confidence calibration across engines. If an engine consistently produces HIGH evidence that leads to incorrect conclusions, its confidence multiplier is decreased.

### Confidence Decomposition (V2)

Show users a breakdown of which evidence contributed what to the confidence score, with expandable detail per evidence node. This is the UI side of the breakdown data the Explanation Formatter already produces.

### Confidence Thresholds per Use Case (V2)

Allow per-question-type confidence thresholds:

| Use Case | Minimum Confidence | Behavior Below |
|---|---|---|
| Casual exploration | 0.20 | Present anyway with caveat |
| Code review | 0.50 | Flag as insufficient |
| Production change | 0.80 | Block insight, require more evidence |

---

## The Confidence Doctrine

> **Confidence is not what the model feels. It is what the evidence proves. Every number is computed, not guessed. Every level is mapped, not generated. Confidence is the weighted sum of evidence strengths, tempered by coverage, penalized by conflict, and degraded by staleness. It is never influenced by the LLM's phrasing, tone, or self-assessed certainty. If the evidence is weak, confidence is LOW — no matter how convincingly the LLM writes its answer. If the evidence is strong, confidence is HIGH — even if the LLM hedges. The system is transparent about why every score is what it is. Users can always drill into the breakdown: which evidence, what weight, which penalty, and why. Confidence is not a magic number. It is an audit trail.**
