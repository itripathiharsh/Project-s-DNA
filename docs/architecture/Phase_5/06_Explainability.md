================================================================================
# 06 Explainability
================================================================================

# Explainability

## Purpose

The Explanation Formatter (Phase 5/01) transforms a validated `ParsedInsight` into a multi-layer, traceable explanation that users can read, trust, and act upon. This document defines how explanations are structured, how evidence chains are constructed, how severity is assigned, and how the system communicates uncertainty, limitations, and recommendations — always grounded in evidence.

---

## Scope

### In Scope

- Explanation Formatter component design
- Evidence chain construction (insight → evidence → raw data)
- Multi-layer explanation format (summary → detail → drill-down)
- Severity assignment heuristic
- Recommendation formatting
- Explanation templates per reasoning type
- Deterministic fallback formatting
- Insight Validator integration
- SCM Reasoning Store write format

### Out of Scope

- Confidence computation (Phase 5/05)
- Response parsing and validation (Phase 5/08, Phase 5/05)
- LLM prompt construction (Phase 5/03)
- UI rendering of explanations (Phase 1)
- Evidence ranking and selection (Phase 5/04)

---

## Background

Phase 5/01 defined the Explanation Formatter as the sixth and final pipeline stage:

```
Intent Recognition → Context Builder → Prompt Orchestrator → LLM Inference
→ Response Parser → [Explanation Formatter] → Insight Validator → Output
```

It receives a `ParsedInsight` (validated LLM output with evidence references, confidence, and recommendations) and produces a `FormattedInsight` — a structured explanation with evidence chain, severity, recommendations, and metadata ready for storage and UI delivery.

Phase 5/05 defined how confidence is computed and how it maps to display levels. The Explanation Formatter uses these confidence values to determine severity and to format uncertainty messages.

Phase 4 defined the evidence node structure and raw data references that the evidence chain traverses.

---

## Architecture

```
ParsedInsight (from Response Parser)
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│                 Explanation Formatter                      │
│                                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │          Evidence Chain Builder                     │   │
│  │  - Resolve evidence_refs UUIDs → full evidence      │   │
│  │  - Build graph: insight → evidence → raw_data       │   │
│  │  - Attach "supports" explanation per link           │   │
│  └────────────────────┬───────────────────────────────┘   │
│                       │                                    │
│  ┌────────────────────▼───────────────────────────────┐   │
│  │          Severity Assigner                         │   │
│  │  - Map confidence + impact heuristics → severity    │   │
│  └────────────────────┬───────────────────────────────┘   │
│                       │                                    │
│  ┌────────────────────▼───────────────────────────────┐   │
│  │          Multi-Layer Formatter                      │   │
│  │  - Summary layer (1 paragraph)                      │   │
│  │  - Detail layer (multi-section body)                │   │
│  │  - Drill-down layer (evidence chain expandable)     │   │
│  └────────────────────┬───────────────────────────────┘   │
│                       │                                    │
│  ┌────────────────────▼───────────────────────────────┐   │
│  │          Recommendation Formatter                   │   │
│  │  - Format each recommendation with effort + risk    │   │
│  │  - Attach evidence references per recommendation    │   │
│  └────────────────────┬───────────────────────────────┘   │
│                       │                                    │
│  ┌────────────────────▼───────────────────────────────┐   │
│  │          Insight Packager                           │   │
│  │  - Assemble all layers into FormattedInsight        │   │
│  │  - Attach metadata (model, tokens, duration)        │   │
│  │  - Write to SCM Reasoning Store                     │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  Output: FormattedInsight → Insight Validator → SCM/API   │
└──────────────────────────────────────────────────────────┘
```

---

## Evidence Chain Construction

The evidence chain is a directed graph from insight conclusion to raw data, preserving provenance at every hop.

### Chain Structure

```
Insight Conclusion
    │  supports: "aggregate assessment of auth module health"
    ▼
Supporting Evidence Node (trace_001)
    │  supports: "36.8% error rate indicates degradation"
    │  derived_from:
    ▼
Raw Data (raw_data_ref: "logs/auth_20260714.json")
    │  type: log_file
    │  line: 847
    │  content_hash: "abc123"
```

### Builder Algorithm

```
1. For each evidence_ref in ParsedInsight.evidence_references:
   a. Resolve UUID to full EvidenceNode from AssembledContext
   b. For each supporting_evidence in the insight:
      - Create link: insight → evidence
      - Generate "supports" string: how this evidence supports the insight
      - Create link: evidence → raw_data_ref
      - Attach raw_data metadata (type, ref, content_hash)
2. Attach confidence per evidence node
3. Order evidence by relevance score descending
4. Tag evidence as "primary" or "secondary" based on role in the insight
```

### Supports String Generation

The "supports" string explains the logical connection between the evidence and the insight:

| Evidence Role | Supports String Pattern |
|---|---|
| Direct contradiction | "Directly contradicts the claim by showing {value}" |
| Direct support | "Directly supports the conclusion: {value}" |
| Trend indicator | "Shows a {trend} trend, consistent with the finding" |
| Contextual | "Provides context: {detail}, relevant to the analysis" |
| Conflict | "Conflicts with {other_evidence_id}: {value} vs {other_value}" |

These strings are generated from evidence metadata (type, value, trend) combined with the insight's claims — not from the LLM. This avoids hallucinated justifications.

---

## Multi-Layer Explanation Format

Every explanation is structured in three layers, consumable at different levels of user engagement.

### Layer 1: Summary

A single paragraph that answers the question directly. Always includes:

```
{summary_sentence}

Confidence: {level} ({float})
Evidence: {evidence_count} items from {engine_names}
```

Character limit: 280 characters (fits in a tooltip or notification).

**Example:**
```
Auth module is degrading: error rate at 36.8%, up from 5% last week,
driven by a recent deployment to validate.ts.

Confidence: MEDIUM (0.62)
Evidence: 12 items from trace_cognition, metric_cognition
```

### Layer 2: Detailed Explanation

Multi-section body with structured content. Sections vary by reasoning type.

**Universal sections** (present in all reasoning types):

```
## Summary
{expanded summary — 2–3 paragraphs}

## Evidence Overview
- Total evidence items consulted: {count}
- Engines represented: {list}
- Time range: {start} — {end}
- Conflicts detected: {count}

## Key Findings
{one bullet per primary claim, each with evidence reference}

## Limitations
{one bullet per limitation, each with explanation}
```

**Type-specific sections:**

| Reasoning Type | Additional Sections |
|---|---|
| synthesis | Patterns Observed, Cross-Engine Correlation Identified |
| decision_support | Options Compared, Trade-off Analysis, Recommendation |
| risk_evaluation | Risk Register, Risk Severity Breakdown, Mitigation Suggestions |
| prediction | Trend Analysis, Prediction Timeline, Confidence Decay |
| simple_qa | Direct Answer, Source Summary |

### Layer 3: Evidence Drill-Down

Expandable detail for each evidence node. Accessible via UI expansion or API `?detail=full` parameter.

```
## Evidence Chain
### trace_001 (FUNCTION_CALL)
- Engine: trace_cognition v1.3
- Severity: LOW
- Value: validateToken() called 847 times, 312 returning errors (36.8%)
- Timestamp: 2026-07-14T10:23:00Z
- Source: src/auth/validate.ts:42
- Confidence: 0.95
- Supports: "Directly supports the conclusion: 36.8% error rate"
- Raw Data Reference:
  - File: logs/auth_20260714.json
  - Line: 847
  - Hash: abc123def456
  - View: {link to raw data in UI}
```

---

## Severity Assignment

Severity communicates the importance of the insight to the user. It is computed from confidence and impact heuristics, not from the LLM.

### Severity Levels

| Level | Meaning | Action Required |
|---|---|---|
| CRITICAL | System integrity at risk. Immediate attention. | Fix within 24 hours. |
| HIGH | Significant degradation or risk. Plan response. | Fix within sprint. |
| MEDIUM | Notable issue. Monitor and schedule. | Add to backlog. |
| LOW | Minor observation. Informational. | No action required. |
| INFO | Positive finding or neutral observation. | Acknowledge. |

### Computation

```
severity_score = impact_heuristic × (1.0 - confidence_penalty)

where:
  impact_heuristic = max evidence severity in the chain:
    CRITICAL evidence = 1.0
    HIGH evidence = 0.8
    MEDIUM evidence = 0.5
    LOW evidence = 0.2
    INFO evidence = 0.05

  confidence_penalty = 0.0 if confidence >= 0.8
                       0.2 if confidence >= 0.5
                       0.5 if confidence < 0.5

mapping:
  severity_score >= 0.70  → CRITICAL or HIGH (based on evidence severity)
  severity_score >= 0.40  → MEDIUM
  severity_score >= 0.15  → LOW
  else                     → INFO
```

If evidence includes CRITICAL items but confidence is LOW, the severity is capped at MEDIUM — the system acknowledges the potential severity but communicates that evidence is insufficient for a definitive call.

---

## Recommendation Formatting

Each recommendation includes action, effort estimate, risk, and confidence.

### Recommendation Schema

```jsonc
{
    "recommendations": [
        {
            "action": "Roll back deployment of validate.ts to version 2.1.3",
            "effort_estimate": "30 minutes",
            "risk": "LOW",
            "confidence": 0.85,
            "evidence_refs": ["trace_001", "trace_002", "metric_001"],
            "expected_impact": "Reduce error rate from 36.8% to ~5%"
        }
    ]
}
```

### Effort Estimation Rules

Effort estimates are derived from the evidence context:

| Evidence Signal | Effort Estimate |
|---|---|
| Single file change | "minutes" |
| Multi-file refactor (< 5 files) | "hours" |
| Cross-module change | "days" |
| Architecture migration | "weeks" |
| Unknown | "not estimated" |

### Risk Assignment Rules

| Condition | Risk Level |
|---|---|
| Rollback or revert possible | LOW |
| Change affects 1 module, testable | LOW |
| Change affects 2+ modules | MEDIUM |
| Change modifies shared infrastructure | HIGH |
| Change has no clear rollback path | HIGH |

Both effort and risk are computed from evidence metadata and the scope of entities affected. They are not generated by the LLM.

---

## Explanation Templates

The Explanation Formatter uses templates to structure explanations per reasoning type. Templates are stored as files:

```
templates/
├── explanation_synthesis_v1.json
├── explanation_simple_qa_v1.json
├── explanation_decision_support_v1.json
├── explanation_risk_evaluation_v1.json
└── explanation_prediction_v1.json
```

### Template Structure (synthesis example)

```jsonc
{
    "type": "synthesis",
    "sections": [
        {
            "name": "summary",
            "required": true,
            "max_chars": 280,
            "format": "paragraph",
            "content": "{summary_sentence} Confidence: {confidence_level} ({confidence_float}). Evidence: {evidence_count} items from {engine_names}."
        },
        {
            "name": "expanded_summary",
            "required": true,
            "format": "paragraphs",
            "content": "{expanded_summary}"
        },
        {
            "name": "patterns",
            "required": true,
            "format": "bullets",
            "content": "{#each patterns}{description} — supported by {evidence_refs}{/each}"
        },
        {
            "name": "evidence_overview",
            "required": true,
            "format": "key_value",
            "fields": [
                {"key": "Total evidence items", "value": "{evidence_count}"},
                {"key": "Engines", "value": "{engine_names}"},
                {"key": "Conflicts", "value": "{conflict_count}"}
            ]
        },
        {
            "name": "evidence_chain",
            "required": false,
            "format": "drill_down",
            "visible_by_default": false
        },
        {
            "name": "limitations",
            "required": true,
            "format": "bullets",
            "content": "{#each limitations}{text}{/each}"
        }
    ]
}
```

---

## Deterministic Fallback Formatting

When the pipeline falls back to deterministic mode (LLM unavailable or validation failed):

### Fallback Insight Structure

```jsonc
{
    "id": "uuid",
    "type": "evidence_summary",
    "title": "Evidence Summary: {query_question}",
    "summary": "AI reasoning is currently unavailable. Here is a summary of the evidence found for your query.",
    "detailed_explanation": "The following evidence was found in the SCM matching your query. No AI synthesis was performed.",
    "confidence": 0.0,
    "severity": "INFO",
    "fallback_reason": "LLM_UNAVAILABLE"  // or "VALIDATION_FAILED"
    "evidence_chain": {
        "insight": { "id": "...", "title": "Evidence Summary", "confidence": 0.0 },
        "supporting_evidence": [
            // All evidence items from AssembledContext, formatted as a flat list
        ]
    },
    "recommendations": [],
    "reasoning_metadata": {
        "model": "none",
        "prompt_tokens": 0,
        "response_tokens": 0,
        "duration_ms": 1234,
        "fallback": true
    }
}
```

The fallback explanation shows users all available evidence so they can reason about it themselves. It is a transparent "here is what we found" rather than a pretended "here is what we think."

---

## SCM Reasoning Store Integration

Every formatted insight is written to the SCM Reasoning Store (Phase 3) for persistence, retrieval, and historical context.

### Write Schema

```
SCM Reasoning Store:
  - id: UUID
  - type: "reasoning_insight"
  - value: {
        formatted_insight: FormattedInsight (full object)
    }
  - confidence: float
  - source: {
        engine: "reasoning_layer"
        version: "1.0"
        timestamp: datetime
    }
  - raw_data: {
        type: "reasoning_pipeline_context"
        ref: request_id
        content_hash: string
    }
  - affected_entities: UUID[]  (all entities referenced in evidence)
```

### Retrieval

Insights are queryable by:
- `entity_id`: Find all insights about a specific module, function, or person.
- `time_range`: Find insights from a specific period.
- `type`: Filter by reasoning type (risk, prediction, decision, etc.).
- `severity`: Filter by importance.

### Supersession

When a new insight addresses the same question or entities as an existing active insight, the old insight is marked `superseded_by: new_insight_id`. This preserves history while keeping the active insight set current.

---

## Edge Cases

### Empty Evidence Set

If no evidence was available:
- Summary: "No evidence was found matching your query. Project DNA cannot provide a reasoned answer without data."
- Evidence chain: Empty.
- Severity: INFO.
- The insight is stored as a "null result" for future reference.

### Low Confidence Insight

If confidence < 0.30:
- Summary includes prefix: "Low Confidence: {summary}"
- Limitations section is promoted to appear immediately after summary.
- A "why low confidence" explanation is auto-generated from the confidence breakdown:
  - "Only {coverage}% of claims are directly supported."
  - "Evidence conflicts reduce confidence by {penalty}%."
  - "Primary evidence is {max_confidence} confidence — too weak for a strong conclusion."

### Conflicting Evidence

When conflicts are detected:
- Detailed explanation includes a "Conflicting Evidence" section.
- Both interpretations are presented with their respective confidences.
- The conflict is surfaced in the evidence chain as linked nodes.
- No attempt is made to reconcile contradictory evidence in the explanation.

### Multi-Entity Analysis

When the insight covers multiple entities (e.g., "How does auth affect payment?"):
- Summary covers the relationship.
- Detailed explanation includes per-entity sections.
- Evidence chain shows cross-entity links.
- Each entity's evidence is grouped under its own heading in the drill-down.

### Stale Evidence

When all evidence is stale:
- Summary includes: "(based on historical data — evidence is {age} old)"
- Limitations section notes: "Evidence may not reflect current state."
- Severity is capped at MEDIUM regardless of content.

---

## Future Work

### Interactive Evidence Chain (V2)

Allow users to click through the evidence chain in the UI:
- Click a claim → highlights supporting evidence.
- Click evidence → shows drill-down to raw data.
- Click raw data → opens file at the relevant line.

### Explanation Summarization (V2)

For users who want progressively more detail, generate summaries at multiple lengths:
- One-line (60 chars): tooltip-friendly.
- Paragraph (280 chars): notification-friendly.
- Full (unlimited): deep dive.

### Multi-Language Explanations (V3)

Translate explanations into the user's preferred language while keeping evidence and data in their original form. Evidence values, file paths, and code remain untranslated.

### Explanation Feedback Loop (V2)

Collect user feedback on explanation clarity:
- "Was this explanation helpful?" (thumbs up/down).
- Track which sections users expand most.
- Use feedback to tune explanation templates.

---

## The Explainability Doctrine

> **An explanation is not an answer — it is a traceable narrative from data to conclusion. Every claim points to evidence. Every evidence points to raw data. Every recommendation carries its own confidence, effort, and risk. The explanation is structured so that users can consume it at the depth they need: a summary for the busy, a detailed analysis for the curious, and a complete evidence chain for the skeptical. If the system cannot reason, it shows the evidence directly — respecting the user's intelligence rather than pretending to understand. The explanation is never authored by the LLM. It is assembled from validated components: evidence, confidence, severity, and templates. The LLM contributes the synthesis; the Explanation Formatter contributes the trust.**
