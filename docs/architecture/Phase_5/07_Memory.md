================================================================================
# 07 Memory
================================================================================

# Memory

## Purpose

The Reasoning Layer writes insights to the SCM Reasoning Store and reads from past insights to inform future reasoning. This document defines how insights are stored, retrieved, linked, expired, and superseded — creating a persistent memory that enables the system to learn from its own past analyses, avoid repeating conclusions, and build on prior understanding.

---

## Scope

### In Scope

- Insight storage and retrieval from the SCM Reasoning Store
- Insight lifecycle (creation → active → acknowledged → resolved/dismissed)
- Memory recall — using past insights as context for new reasoning
- Insight relationships (contradiction, supersession, support)
- Insight expiration and re-evaluation triggers
- Memory-augmented context building
- Edge cases (contradictory memories, expired insights, cycle detection)

### Out of Scope

- SCM storage backend implementation (Phase 3)
- Evidence node storage (Phase 3)
- Explanation formatting (Phase 5/06)
- Confidence computation (Phase 5/05)
- Cognitive Engine evidence production (Phase 4)

---

## Background

Phase 3 defined the SCM Reasoning Store as Pillar 3 of the Software Cognition Model:
- Contains insights, predictions, recommendations, and their supporting evidence.
- Insights have type, severity, confidence, evidence chain, affected entities, and status.
- Relationships include `SUPPORTED_BY` (insight → evidence), `AFFECTS` (insight → entity), `RECOMMENDS` (insight → recommendation), `CONTRADICTS` (insight → insight), and `SUPERSEDES` (insight → insight).
- Insights follow a lifecycle: Active, Acknowledged, Resolved, Dismissed.

Phase 5/01 and Phase 5/06 defined the flow: the Explanation Formatter writes formatted insights to the Reasoning Store, and the Context Builder may retrieve past insights as part of context assembly.

Phase 5/04 defined how the Context Builder queries evidence. Memory recall extends this by also querying past insights for relevant conclusions.

---

## Architecture

```
Pipeline (new reasoning request)
    │
    ▼
┌──────────────────────────────────────────────────┐
│              Context Builder                       │
│                                                    │
│  ┌────────────────────────────────────────────┐   │
│  │          Evidence Query                     │   │
│  │  - Query evidence from Perception Store     │   │
│  │  - Query entities from Representation Store │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
│  ┌────────────────────────────────────────────┐   │
│  │          Memory Recall                      │   │
│  │  - Query past insights from Reasoning Store │   │
│  │  - Filter by entity, time range, type      │   │
│  │  - Rank by recency and relevance           │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
│  Output: AssembledContext (evidence + memories)    │
└──────────────────────────────────────────────────────┘
    │
    ▼
Pipeline (continues to Prompt Orchestrator, LLM, etc.)
    │
    ▼
┌──────────────────────────────────────────────────┐
│           Explanation Formatter                    │
│                                                    │
│  ┌────────────────────────────────────────────┐   │
│  │          SCM Write                          │   │
│  │  - Write FormattedInsight to Reasoning Store│   │
│  │  - Link to evidence via SUPPORTED_BY        │   │
│  │  - Link to entities via AFFECTS             │   │
│  │  - Detect and link contradictions           │   │
│  │  - Supersede outdated insights              │   │
│  └────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

---

## Insight Lifecycle

### States

```
        ┌──────────┐
        │  Created  │  (insight is written to SCM by Explanation Formatter)
        └────┬─────┘
             │
             ▼
        ┌──────────┐
        │  Active   │  (insight is current, visible in queries)
        └────┬─────┘
             │
    ┌────────┼────────────┐
    │        │            │
    ▼        ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│Acknowledged│ │ Resolved │ │ Dismissed│
│(user seen) │ │ (fixed)  │ │(rejected)│
└────────────┘ └──────────┘ └──────────┘
    │        │            │
    │        │            │
    └────────┴────────────┘
             │
             ▼
        ┌──────────┐
        │ Archived │  (no longer active, retained for history)
        └──────────┘
```

| State | Meaning | Visibility | Transition |
|---|---|---|---|
| Created | Initial state after pipeline write | Not visible to user | Auto → Active within seconds |
| Active | Current, actionable insight | Visible in queries and UI | → Acknowledged (user action) |
| Acknowledged | User has seen it | Visible but marked as seen | → Resolved (user action) |
| Resolved | Issue addressed | Archived | → Archived (auto after 30 days) |
| Dismissed | User rejected it | Archived | → Archived (immediate) |
| Archived | Historical record | Search only, not in active queries | Immutable |

### Automatic State Changes

| Trigger | From | To |
|---|---|---|
| New insight supersedes old | Active | Archived |
| Insight expires (expires_at reached) | Active | Archived |
| Insight is 90 days past resolution | Resolved | Archived |
| Insight is 30 days past dismissal | Dismissed | Archived |

### Expiration

Each insight has an optional `expires_at` timestamp set by the Explanation Formatter:

| Reasoning Type | Default Expiration | Rationale |
|---|---|---|
| Risk evaluation | 7 days | Risk landscape changes rapidly |
| Simple QA | 30 days | Facts may become stale |
| Synthesis | 30 days | Understanding evolves |
| Decision support | 90 days | Decisions have longer relevance |
| Prediction | Until prediction date + 30 days | Verify accuracy after predicted date |

When an insight expires, it is automatically archived. If a user asks a question that would have been answered by an expired insight, the pipeline runs fresh reasoning.

---

## Memory Recall

When the Context Builder assembles context for a new reasoning request, it may also retrieve relevant past insights from the Reasoning Store.

### Recall Trigger

Memory recall is activated in two scenarios:

| Scenario | Behavior |
|---|---|
| **Same entity, different question** | Retrieve all active insights for the entity. Include summaries in context. |
| **Same question, same entity** | Check for existing active insight. If found and confidence > 0.7, return cached. |
| **Related entities** | Retrieve insights for related entities (dependencies, callers, callees). |
| **No recall** | Simple QA on never-before-analyzed entities. |

### Recall Query

```
query = {
    "entities": entity_ids,         // Entities from intent
    "time_range": last_30_days,     // Default recall window
    "status": "active",             // Only active insights
    "types": ["risk", "synthesis", "decision"],  // Exclude simple_qa
    "limit": 20
}
```

### Recall Ranking

Past insights are ranked by relevance to the current query:

```
recall_score = 0.40 × entity_overlap
             + 0.25 × recency
             + 0.20 × confidence
             + 0.15 × type_match

where:
  entity_overlap = count(matching_entities) / count(query_entities)
  recency = max(0, 1 - age_days / 90)
  confidence = past_insight.confidence
  type_match = 1.0 if matching reasoning type, 0.5 if related
```

### Memory Injection into Context

Past insights are injected into the assembled context as a special evidence type:

```jsonc
{
    "id": "memory_001",
    "type": "PAST_INSIGHT",
    "engine": "reasoning_layer",
    "severity": "MEDIUM",
    "value": "Previous analysis (14 days ago): Auth module error rate was 5.2%. Predicted increase to 15% within 30 days. Prediction accuracy: confirmed (actual: 36.8%).",
    "confidence": 0.85,
    "timestamp": "2026-06-30T10:00:00Z",
    "source": "Reasoning Store: insight_abc123",
    "truncation_priority": "normal"
}
```

The Prompt Orchestrator treats memory items as evidence — they are subject to the same token budget, truncation, and ranking as engine evidence.

---

## Insight Relationships

### SUPPORTED_BY (Insight → Evidence)

Written by the Explanation Formatter for every evidence reference in the insight:

```
Insight (id: insight_001)
    └── SUPPORTED_BY → trace_001
    └── SUPPORTED_BY → metric_001
    └── SUPPORTED_BY → trace_002
```

This link enables:
- Traceability from insight back to evidence.
- Evidence impact analysis: "What insights depend on this evidence?"
- Confidence propagation during insight regeneration.

### AFFECTS (Insight → Entity)

Written for each entity in `FormattedInsight.evidence_chain`:

```
Insight (id: insight_001)
    └── AFFECTS → mod_auth_001 (src/auth)
    └── AFFECTS → func_auth_001 (validateToken)
```

This link enables:
- Entity impact analysis: "What insights exist about this module?"
- Dependency-aware recall: "This module changed — what insights might be affected?"

### CONTRADICTS (Insight → Insight)

Detected during insight write. A new insight contradicts an existing active insight when:

```
condition:
    new_insight.affected_entities ∩ existing_insight.affected_entities ≠ ∅
    AND new_insight.confidence > existing_insight.confidence
    AND new_insight.conclusion contradicts existing_insight.conclusion
```

When contradiction is detected:
1. The existing insight is linked via `CONTRADICTS`: `new_insight → CONTRADICTS → existing_insight`
2. Both insights remain active. The system surfaces contradictions in context assembly.
3. A human resolves the contradiction by acknowledging or dismissing one of the two.

### SUPERSEDES (Insight → Insight)

A new insight supersedes an existing one when:

```
condition:
    new_insight.affected_entities == existing_insight.affected_entities
    AND new_insight.type == existing_insight.type
    AND new_insight.confidence > existing_insight.confidence + 0.15
```

When supersession is detected:
1. The existing insight is linked via `SUPERSEDES`: `new_insight → SUPERSEDES → existing_insight`
2. The existing insight is automatically archived.
3. The user is notified: "A new analysis supersedes your previous insight about {entity}."

---

## Memory in Context Assembly

The Context Builder (Phase 5/04) integrates memory recall into its standard assembly flow.

### Extended Assembly Flow

```
1. Entity Resolution (as before)
2. Evidence Query (as before)
3. Memory Recall (new):
   a. Query Reasoning Store for active insights matching entities
   b. Rank by recall_score
   c. Top 5 memories injected into evidence set as PAST_INSIGHT type
   d. Attach contradiction relationships if memories conflict
4. Aggregation & Scoring (as before)
5. Token Budget Estimation (as before)
6. Packaging (as before)
```

### Memory Budget

Within the 6000-token evidence budget:

| Component | Tokens | Notes |
|---|---|---|
| Engine evidence | 4000–5500 | Core evidence from engines |
| Memory (past insights) | 500–1000 | Up to 5 memories at ~200 tokens each |
| Reserve | 0–500 | For aggregation metadata |

If the budget for memory is exceeded, the lowest-scored memories are truncated first — before any engine evidence is removed.

---

## Edge Cases

### Contradictory Memories

When memory recall retrieves two insights that contradict each other:

```
Memory A: "Auth module error rate is stable at 5%." (7 days old, confidence 0.90)
Memory B: "Auth module error rate is spiking to 36.8%." (today, confidence 0.85)
```

Both are injected into context. The contradiction is surfaced in `AssembledContext.conflicts`. The LLM is explicitly asked to address the contradiction. The resulting insight includes a "Changed Assessment" section.

### Cyclic Dependencies

If Insight A supports B, B supports C, and C relates back to A's entities:

The memory recall system does not follow relationship chains — it queries by entity only. This means:
- Insight A about module X is recalled when querying module X.
- Insight B about module Y is recalled when querying module Y.
- Cyclic dependencies cannot form because each insight is independently linked to its own entities.
- No cycle detection is needed in V1.

### Expired Insight Re-Query

If a user asks the same question they asked 30 days ago, and the old insight has expired:

```
1. Memory recall finds no active insight (expired → archived).
2. Pipeline runs fresh reasoning.
3. New insight is created.
4. Old insight is linked via SUPERSEDES if entities and type match.
5. User sees: "This replaces your analysis from 30 days ago."
```

### Memory with No Matching Entities

If memory recall finds zero insights for the queried entities:

```
Context Builder proceeds with engine evidence only.
No memory is injected.
Pipeline behaves exactly as Phase 5/04 defines.
```

### User Dismisses an Insight Repeatedly

If a user dismisses the same type of insight for the same entity three times:

```
1. After third dismissal, the system marks the insight pattern as "dismissed_pattern."
2. Future pipeline runs still produce the insight (the evidence hasn't changed).
3. But the insight is stored with status "dismissed_by_pattern" and is not surfaced to the user.
4. If evidence changes significantly (new data, higher confidence), the pattern resets.
```

This prevents alert fatigue while preserving the ability to re-alert when circumstances change.

---

## Insight Store — Query Interface

The SCM Reasoning Store provides a query interface for memory operations:

| Operation | Parameters | Purpose |
|---|---|---|
| `get_insights(entity_ids)` | entity_ids, status, type, time_range, limit | Retrieve insights by entity |
| `get_insight(id)` | insight_id | Get single insight with full chain |
| `get_contradictions(insight_id)` | insight_id | Find contradictory insights |
| `get_predecessors(insight_id)` | insight_id | Find superseded insights |
| `write_insight(insight)` | FormattedInsight | Store new insight |
| `update_status(insight_id, status)` | insight_id, new_status | Acknowledge, resolve, dismiss |
| `resolve_contradiction(insight_id_a, insight_id_b, resolution)` | two IDs + resolution | Human resolves contradiction |

### Write Operation Detail

When `write_insight` is called, the Reasoning Store performs:

```
1. Validate insight schema
2. Detect contradictions with existing active insights
3. Detect supersession candidates
4. Create SUPPORTED_BY links for each evidence reference
5. Create AFFECTS links for each affected entity
6. Create CONTRADICTS links if contradictions found
7. Create SUPERSEDES links if supersession found
8. Archive superseded insights
9. Store insight with status: "active"
10. Return insight_id
```

---

## Future Work

### Episodic Memory (V2)

Store not just individual insights but the context in which they were generated — the question asked, the evidence available at the time, the model used, the pipeline configuration. This enables:
- "Why did you think that last week?" queries.
- Comparison of reasoning across time: "How has your assessment changed?"
- Rollback: "Re-run the analysis as if it were last week."

### Active Learning (V3)

When the system produces a low-confidence insight that turns out to be correct (as determined by user feedback or subsequent events), increase the relevance score of similar evidence patterns. When a high-confidence insight is wrong, decrease it. This tunes the reasoning system without retraining the LLM.

### Cross-Session Context (V2)

Maintain short-term memory within a user session:
- If a user asks "What about the payment module?" after asking about auth, the system infers the comparison intent.
- The Context Builder retrieves evidence for both modules and presents the comparative context without needing a new query.

### Memory Consolidation (V3)

Periodically scan the Reasoning Store for insights that can be consolidated:
- Multiple low-confidence insights about the same entity → combine into one higher-confidence insight.
- Contradictory insights with no resolution → flag for human review.
- Outdated predictions → mark as inaccurate and adjust prediction engine parameters.

---

## The Memory Doctrine

> **An insight without memory is a conversation without context. The Reasoning Store is not a log — it is a living memory. Every insight knows what it supports, what it affects, what contradicts it, and what it replaces. The system remembers past conclusions not to repeat them, but to build upon them, challenge them, and learn from their accuracy. Memory recall ensures that no reasoning request starts from zero — it carries forward the understanding earned by every previous analysis. When the evidence changes, the memory does not lie — it is superseded, not rewritten. When insights contradict, the system presents both views rather than silence the past. Memory makes the system smarter over time, not through model training, but through persistent, structured recall of what it has already discovered.**
