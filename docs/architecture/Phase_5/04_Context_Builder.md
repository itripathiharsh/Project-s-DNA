================================================================================
# 04 Context Builder
================================================================================

# Context Builder

## Purpose

The Context Builder (called "Context Assembler" in Phase 5/01) bridges the Software Cognition Model — populated with deterministic evidence by the Cognitive Engines — and the reasoning pipeline. It transforms structured query intent into a ranked, token-budgeted evidence bundle that the Prompt Orchestrator (Phase 5/03) injects into LLM prompts. The Context Builder is the gate that determines what evidence the LLM sees, and in what order.

---

## Scope

### In Scope

- SCM query interface design
- Entity resolution (names → SCM entity IDs)
- Evidence selection and relevance ranking
- Recency weighting and time-range filtering
- Cross-engine evidence aggregation
- Conflict detection across evidence sources
- Token budget estimation and truncation readiness
- Historical context retrieval and trend computation
- Edge cases (ambiguous entities, stale evidence, empty results)

### Out of Scope

- Intent parsing and classification (Phase 5/01, Intent Recognition)
- Prompt template selection and injection (Phase 5/03)
- LLM inference and response handling (Phase 5/02)
- Response validation and explanation formatting (Phase 5/05, 5/06, 5/08)
- Cognitive Engine design (Phase 4)

---

## Background

Phase 5/01 defined the Context Assembler as the second stage of the reasoning pipeline:

```
Intent Recognition → [Context Builder] → Prompt Orchestrator → LLM Interface → Response Parser
```

The component receives a structured query intent and produces an `AssembledContext` — an ordered set of evidence nodes ready for prompt injection.

Phase 4 established the evidence structure that the Context Builder queries:
- Every Cognitive Engine produces `EvidenceNode` records with id, type, category, value, confidence, source metadata, and entity references.
- Evidence is stored in the SCM, which provides a query interface.
- Engines are organized across four tiers: Foundational, Analytical, Evaluative, and Strategic.

Phase 5/02 defined the token budget that constrains context size: 6000 tokens max for evidence in the primary model's 8192-token window.

Phase 5/03 defined the evidence injection format that the Context Builder must produce: a structured block with engine name, severity, detail, timestamp, and source for each evidence item.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Context Builder                            │
│                                                                │
│  ┌─────────────┐    ┌────────────────────┐                    │
│  │  Entity      │    │  Evidence           │                    │
│  │  Resolver    │───▶│  Selector           │                    │
│  │  name→ID     │    │  query+rank+filter  │                    │
│  └─────────────┘    └────────┬───────────┘                    │
│                              │                                  │
│  ┌───────────────────────────▼──────────────────────────┐     │
│  │              Aggregator & Scorer                       │     │
│  │  - Merge cross-engine evidence                          │     │
│  │  - Compute relevance scores                             │     │
│  │  - Detect conflicts                                    │     │
│  │  - Compute aggregate statistics                        │     │
│  └───────────────────────────┬──────────────────────────┘     │
│                              │                                  │
│  ┌───────────────────────────▼──────────────────────────┐     │
│  │              Token Budget Estimator                    │     │
│  │  - Tokenize evidence set                               │     │
│  │  - Tag truncation candidates                            │     │
│  │  - Prepare overflow strategy                            │     │
│  └───────────────────────────┬──────────────────────────┘     │
│                              │                                  │
│  ┌───────────────────────────▼──────────────────────────┐     │
│  │              Context Packager                         │     │
│  │  - Format evidence blocks for prompt injection         │     │
│  │  - Attach metadata (counts, engine list, conflicts)    │     │
│  │  - Return AssembledContext                            │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                │
│  Output: AssembledContext                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ {                                                         │  │
│  │   query_intent: {...},                                    │  │
│  │   entities: [{id, name, type}],                           │  │
│  │   evidence: [EvidenceBlock,...],                          │  │
│  │   aggregates: {metric_name: {avg, max, min, trend}},     │  │
│  │   conflicts: [{evidence_a, evidence_b, type}],           │  │
│  │   metadata: {total_tokens, evidence_count, engines}       │  │
│  │ }                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## SCM Query Interface

The Context Builder queries the SCM through a dedicated query interface. The SCM stores evidence nodes indexed by entity, engine, type, and timestamp.

### Query Operations

| Operation | Parameters | Purpose |
|---|---|---|
| `get_entities(query)` | name_pattern, type_filter | Resolve entity names to SCM IDs |
| `get_evidence(entity_ids)` | entity_ids, engine_filter, type_filter, time_range, limit | Retrieve evidence for entities |
| `get_historical(entity_id, metric, time_range)` | entity_id, metric_name, start_time, end_time, granularity | Get trend/time-series data |
| `get_conflicts(entity_id)` | entity_id | Find evidence with conflicting conclusions |
| `count_evidence(query)` | Same filters as get_evidence | Get total count for pagination |

### Query Flow

```
1. Intent arrives with parsed entities and time constraints
2. Entity Resolver maps names to SCM IDs via get_entities()
3. Evidence Selector queries get_evidence() for each entity
4. If time constraints exist, apply time_range filter
5. Historical context retrieved via get_historical() for trendable metrics
6. Cross-engine conflicts queried via get_conflicts()
```

### Query Limits

| Environment | Max Evidence Items | Max Entities | Max Historical Points |
|---|---|---|---|
| V1 default | 200 | 20 | 100 per metric |
| V1 memory-constrained | 50 | 10 | 50 per metric |
| V2 (planned) | 1000 | 100 | 500 per metric |

---

## Entity Resolution

Entity resolution maps natural-language entity references from the user's question to SCM entity IDs.

### Entity Types

| Type | Examples | SCM Index |
|---|---|---|
| Module | `auth`, `payment-api`, `src/utils` | Entity ID prefix: `mod_` |
| Function | `validateToken`, `calculateTotal` | Entity ID prefix: `func_` |
| Class | `AuthProvider`, `OrderService` | Entity ID prefix: `cls_` |
| File | `auth.ts`, `server.py` | Entity ID prefix: `file_` |
| Person | `alice`, `bob` | Entity ID prefix: `person_` |
| Dependency | `lodash`, `express` | Entity ID prefix: `dep_` |
| Metric | `error_rate`, `latency_p99` | Entity ID prefix: `metric_` |

### Resolution Algorithm

```
1. Extract entity candidates from parsed intent (named entities, noun phrases)
2. For each candidate:
   a. Exact match on SCM entity name
   b. Fuzzy match (Levenshtein distance ≤ 2)
   c. Prefix match (candidate is substring of entity name)
3. If multiple matches: return all with disambiguation metadata
4. If no matches: return AmbiguousEntity error with suggestions
```

### Disambiguation

When a name resolves to multiple entities (e.g., "auth" could be module `src/auth` or class `AuthProvider`):

```
{
    "entity": "auth",
    "matches": [
        { "id": "mod_auth_001", "name": "src/auth", "type": "module", "score": 0.95 },
        { "id": "cls_auth_001", "name": "AuthProvider", "type": "class", "score": 0.45 }
    ],
    "disambiguation_needed": false    // auto-select if top score >> others
}
```

If the top score is significantly higher than alternatives (threshold: > 0.3 gap), the Context Builder auto-selects. Otherwise, it returns a disambiguation prompt to the user.

---

## Evidence Selection and Ranking

### Relevance Scoring

Each evidence item is scored on a 0–1 scale using a weighted combination:

```
relevance = 0.40 × entity_match
          + 0.25 × recency
          + 0.20 × confidence
          + 0.10 × engine_authority
          + 0.05 × specificity
```

| Factor | Description | Weight |
|---|---|---|
| `entity_match` | Exact entity match = 1.0, parent module match = 0.7, sibling = 0.3, unrelated = 0 | 0.40 |
| `recency` | Age in hours: `max(0, 1 - hours/720)` (30-day half-life) | 0.25 |
| `confidence` | Normalized evidence confidence score | 0.20 |
| `engine_authority` | Engine tier: Foundational=1.0, Analytical=0.8, Evaluative=0.6, Strategic=0.5 | 0.10 |
| `specificity` | Evidence with more detail fields = higher specificity | 0.05 |

### Recency Computation

```
recency_score = max(0, 1.0 - age_hours / decay_period)

Decay periods by question type:
  - Real-time ("what is happening now"):  decay_period = 24 hours
  - General analysis (default):            decay_period = 720 hours (30 days)
  - Historical trends:                     decay_period = 8760 hours (1 year)
```

### Filtering

Before ranking, evidence is filtered by:

| Filter | Criterion | Applied When |
|---|---|---|
| **Minimum confidence** | `confidence >= 0.3` | Always |
| **Engine filter** | Match engine types relevant to intent | Intent specifies engines |
| **Type filter** | Match evidence types for reasoning type | Always per type mapping |
| **Time range** | `timestamp` within intent time range | Intent specifies time constraints |
| **Dead evidence** | Not superseded by newer evidence of same type | Always |

### Evidence-Type-to-Reasoning-Type Mapping

The Context Builder selects evidence types appropriate for the reasoning type:

| Reasoning Type | Preferred Evidence Types |
|---|---|
| simple_qa | Direct entity evidence, metrics, function/class details |
| synthesis | Cross-engine evidence, structural + evolution + dependency |
| decision_support | Option evaluations, risk assessments, cost/benefit data |
| risk_evaluation | Risk items, error rates, complexity metrics, dependency issues |
| prediction | Historical trends, time-series metrics, evolution patterns |

---

## Cross-Engine Aggregation

### Aggregation Strategies

| Strategy | Description | Used When |
|---|---|---|
| **Concatenation** | All evidence items listed individually | Evidence count < 50 |
| **Grouping** | Group by engine, then by entity | Evidence count 50–200 |
| **Statistical summary** | Replace individual items with aggregate metrics | Large metric sets (100+ items) |
| **Temporal bucketing** | Group by time window | Time-series with many data points |

### Aggregate Computation

For numeric evidence (metrics, counts, durations), the Context Builder computes:

```jsonc
{
  "error_rate": {
    "engine": "metric_cognition",
    "count": 120,
    "min": 0.01,
    "max": 0.35,
    "avg": 0.08,
    "p50": 0.05,
    "p95": 0.22,
    "p99": 0.31,
    "trend": "increasing",    // linear regression slope direction
    "period": "last_24h",
    "unit": "requests / total"
  }
}
```

These aggregates are injected as compact evidence blocks, saving tokens compared to listing 120 individual values.

---

## Conflict Detection

The Context Builder identifies conflicts between evidence items from different engines. Conflicts are surfaced in the `AssembledContext.conflicts` array and included in the prompt so the LLM can address them explicitly.

### Conflict Types

| Type | Detection | Example |
|---|---|---|
| **Numerical contradiction** | Two evidence items claim different values for the same metric | Engine A: error_rate=0.05, Engine B: error_rate=0.35 |
| **Categorical contradiction** | Two evidence items assign different categories to the same entity | Engine A: complexity=HIGH, Engine B: complexity=LOW |
| **Temporal contradiction** | Trend direction disagrees | Engine A: trend=increasing, Engine B: trend=decreasing |
| **Dependency contradiction** | Dependency is both healthy and at risk | Engine A: lodash@4.17, Engine B: lodash@4.17 (vulnerable) |

### Conflict Resolution Context

The Context Builder does not resolve conflicts — that is the LLM's reasoning task. It packages conflicts as:

```jsonc
{
    "conflicts": [
        {
            "type": "numerical_contradiction",
            "evidence_a": { "id": "metric_001", "value": 0.05, "engine": "structural_cognition", "timestamp": "2026-07-14T10:00:00Z" },
            "evidence_b": { "id": "metric_002", "value": 0.35, "engine": "risk_cognition", "timestamp": "2026-07-14T09:30:00Z" },
            "possible_explanation": null   // filled by LLM during reasoning
        }
    ]
}
```

Conflicts are tagged with a severity (LOW = minor disagreement, MEDIUM = partial contradiction, HIGH = irreconcilable). The Prompt Orchestrator highlights HIGH conflicts in the prompt.

---

## Token Budget Estimation

### Pre-Tokenization

Before packaging, the Context Builder estimates the token count of the assembled evidence:

```
estimated_tokens = sum(token_count(evidence.format)) for each evidence item
```

Token counts are estimated using model-specific tokenizer heuristics:
- **Primary (7B)**: ~4 characters per token for code, ~3.5 for natural language
- **Fallback (3B)**: ~4.5 characters per token

### Budget Check

```
If estimated_tokens ≤ evidence_budget:
    → Proceed with full evidence set

If estimated_tokens > evidence_budget:
    → Mark low-relevance items as truncation candidates (bottom 20% by score)
    → If still over budget: mark next 20% as candidates
    → Repeat until under budget
    → If truncation removes critical cross-module evidence: flag for chunking
```

The Context Builder does NOT truncate — it tags candidates. The Prompt Orchestrator (Phase 5/03) performs the actual truncation when constructing the prompt. This separation of concerns allows the Prompt Orchestrator to make final token decisions based on the specific model in use.

### Truncation Tags

Each evidence item receives a `truncation_priority` label:

| Label | Meaning |
|---|---|
| `essential` | Must include. Removal would break cross-module analysis. |
| `important` | Include if possible. Remove after all `normal` items are gone. |
| `normal` | Remove in score order when budget is exceeded. |
| `candidate` | First to be removed. Low relevance or redundant. |

---

## AssembledContext Output

The Context Builder produces an `AssembledContext` object:

```jsonc
{
    "query_intent": {
        "type": "synthesis",
        "question": "What is causing the authentication failures?",
        "entities": [
            { "id": "mod_auth_001", "name": "src/auth", "type": "module" },
            { "id": "func_auth_001", "name": "validateToken", "type": "function" }
        ],
        "time_range": { "start": "2026-07-13T00:00:00Z", "end": "2026-07-14T23:59:59Z" }
    },
    "entities": [
        { "id": "mod_auth_001", "name": "src/auth", "type": "module", "aliases": ["auth"] }
    ],
    "evidence": [
        {
            "id": "trace_001",
            "type": "FUNCTION_CALL",
            "engine": "trace_cognition",
            "severity": "LOW",
            "value": "validateToken() called 847 times, 312 returning errors (36.8%)",
            "confidence": 0.95,
            "timestamp": "2026-07-14T10:23:00Z",
            "source": "src/auth/validate.ts:42",
            "entity_id": "func_auth_001",
            "truncation_priority": "essential"
        }
    ],
    "aggregates": {
        "error_rate": {
            "engine": "metric_cognition",
            "count": 1,
            "avg": 0.368,
            "trend": "stable",
            "unit": "error_rate"
        }
    },
    "conflicts": [
        {
            "type": "numerical_contradiction",
            "severity": "LOW",
            "evidence_a": { "id": "trace_001", "value": "36.8% error rate" },
            "evidence_b": { "id": "metric_003", "value": "42.1% error rate" }
        }
    ],
    "metadata": {
        "total_evidence": 12,
        "total_tokens_estimate": 4800,
        "evidence_budget": 6000,
        "under_budget": true,
        "engines_represented": ["trace_cognition", "metric_cognition"],
        "reasoning_type": "synthesis"
    }
}
```

---

## Edge Cases

### No Matching Entities

If entity resolution finds zero matches for any entity in the query:

```
Output AssembledContext:
{
    "query_intent": {...},
    "entities": [],
    "evidence": [],
    "aggregates": {},
    "conflicts": [],
    "metadata": {
        "total_evidence": 0,
        "status": "NO_MATCHING_ENTITIES",
        "suggestions": [
            "Did you mean 'src/auth'?",
            "Available modules: src/api, src/db, src/ui"
        ]
    }
}
```

The pipeline short-circuits: no LLM call, returns a deterministic "entity not found" response.

### Ambiguous Entities

If an entity name matches multiple SCM entities with no clear winner:

```
metadata: {
    "status": "AMBIGUOUS_ENTITY",
    "entity": "auth",
    "matched_entities": ["src/auth (module)", "AuthProvider (class)"],
    "disambiguation_required": true
}
```

The pipeline short-circuits and returns a disambiguation prompt to the user.

### Stale Evidence

If the most recent evidence for a requested entity is older than a configurable threshold (default: 7 days for real-time questions):

- The evidence is still included but tagged with `stale: true`
- The tag propagates to the prompt: "[STALE] error_rate averaged 0.05 over the last 30 days"
- The LLM's confidence in stale evidence is adjusted downward in the prompt

### Empty Evidence Set

If entities resolve but no matching evidence exists:

```
metadata: {
    "status": "NO_EVIDENCE",
    "reason": "No evidence found for entity 'src/auth' with metric type 'error_rate'"
}
```

The pipeline returns a deterministic "insufficient evidence" response without calling the LLM.

### Cross-Module Analysis

When the query spans multiple modules (e.g., "How does auth affect payment?"):

1. Entity resolver identifies both modules.
2. Evidence selector queries evidence for both modules.
3. Cross-module evidence is explicitly linked: `cross_module: [{entity_a: "mod_auth", entity_b: "mod_payment", link_type: "dependency"}]`
4. The Prompt Orchestrator may trigger chunking if cross-module evidence exceeds the budget.

---

## Future Work

### Incremental Context Refresh (V2)

When the SCM is updated (new engine run), the Context Builder refreshes only the evidence items affected by the change rather than rebuilding the entire context. This reduces latency for follow-up questions that reference the same entities.

### Learned Relevance Ranking (V3)

Replace the static relevance scoring formula with a model trained on user feedback. The model learns which evidence types and sources are most useful for different question types.

### Context Caching (V2)

Cache assembled contexts for common queries (e.g., "What is the state of the auth module?"). Invalidate cache when new evidence arrives for the cached entities. Cache hit avoids entity resolution and evidence query overhead.

### Multi-Step Context Building (V3)

For complex decision support, build context in steps:
1. First pass: broad evidence query across all mentioned entities
2. Identify gaps in the evidence
3. Second pass: targeted queries for missing evidence
4. Final assembly with all available data

---

## The Context Builder Doctrine

> **The LLM sees only what the Context Builder shows it. No evidence, no reasoning. The Context Builder is the gatekeeper of attention — it decides which facts matter, which conflicts exist, and which context fits within the token budget. Every piece of evidence is scored, ranked, tagged, and budgeted before it reaches the prompt. The Context Builder does not interpret evidence — it organizes it. It does not resolve conflicts — it surfaces them. Its job is to present the truth, completely and impartially, within the constraints of the model's window. If the evidence is insufficient, it says so. If entities are ambiguous, it asks for clarification. The Context Builder ensures that the LLM never reasons about incomplete, irrelevant, or stale evidence.**
