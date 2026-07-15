================================================================================
# 09 Examples
================================================================================

# Examples

## Purpose

This document provides concrete worked examples of the reasoning pipeline across all five reasoning types, plus edge cases. Each example traces a complete request from user question through all six stages to the final formatted insight, demonstrating how the components defined in Phase 5/01 through 5/08 compose in practice.

---

## Scope

### Examples Included

1. **Simple QA** — Direct factual question about a function.
2. **Evidence Synthesis** — Multi-evidence root cause analysis.
3. **Decision Support** — Refactor vs. rewrite comparison.
4. **Risk Evaluation** — Module risk assessment.
5. **Prediction** — Trend forecasting with confidence decay.
6. **Insufficient Evidence** — Empty result handling.
7. **Deterministic Fallback** — LLM unavailable scenario.

### Conventions

- Each example follows the format: Input → Stage 1 → ... → Stage 6 → Output.
- Intermediate data structures are shown in abbreviated JSON.
- Token counts are approximate.
- Confidence values use the model defined in Phase 5/05.
- All examples reference a shared imaginary project: a payment processing system with modules `auth`, `payment`, `notification`.

---

## Example 1: Simple QA

### Input

```
User question: "What does the validateToken function do?"
```

### Stage 1: Intent Recognition

```jsonc
{
    "type": "question",
    "question": "What does the validateToken function do?",
    "entities": [
        { "name": "validateToken", "type": "function" }
    ],
    "reasoning_type": "simple_qa",
    "time_range": null
}
```

### Stage 2: Context Builder

Entity resolution: `validateToken` → `func_auth_validatetoken_001`.

Evidence query returns 3 items:

```jsonc
{
    "entities": [{ "id": "func_auth_validatetoken_001", "name": "validateToken", "type": "function" }],
    "evidence": [
        {
            "id": "struc_001",
            "type": "FUNCTION_DEFINITION",
            "engine": "structural_cognition",
            "value": "validateToken(token: string, config: TokenConfig): Promise<boolean> — Validates a JWT token against the provided config. Calls verifyToken() and checkExpiry().",
            "confidence": 1.0,
            "source": "src/auth/validate.ts:12-48"
        },
        {
            "id": "struc_003",
            "type": "FUNCTION_CALLER",
            "engine": "structural_cognition",
            "value": "Called by: authenticate() in src/auth/provider.ts:55, refreshToken() in src/auth/session.ts:102",
            "confidence": 0.95,
            "source": "src/auth/validate.ts:12"
        },
        {
            "id": "know_001",
            "type": "KNOWLEDGE_OWNERSHIP",
            "engine": "knowledge_cognition",
            "value": "Primary author: Alice (alice@company.com), 12 commits. Last modified 3 days ago.",
            "confidence": 0.90,
            "source": "git log --follow src/auth/validate.ts"
        }
    ],
    "metadata": {
        "total_evidence": 3,
        "total_tokens_estimate": 350,
        "reasoning_type": "simple_qa"
    }
}
```

### Stage 3: Prompt Orchestrator

Template: `simple_qa_v1`

```jsonc
{
    "system": "You are Project DNA, a reasoning engine...",
    "messages": [
        {
            "role": "user",
            "content": "EVIDENCE\n========\n[engine: structural_cognition]\n  ID: struc_001\n  Type: FUNCTION_DEFINITION\n  Detail: validateToken(token: string, config: TokenConfig): Promise<boolean> ...\n  Source: src/auth/validate.ts:12-48\n\n[engine: structural_cognition]\n  ID: struc_003\n  Type: FUNCTION_CALLER\n  Detail: Called by: authenticate() in src/auth/provider.ts:55 ...\n  Source: src/auth/validate.ts:12\n\n[engine: knowledge_cognition]\n  ID: know_001\n  Type: KNOWLEDGE_OWNERSHIP\n  Detail: Primary author: Alice, 12 commits. Last modified 3 days ago.\n  Source: git log\n\n---\n\nQUERY\n=====\nWhat does the validateToken function do?\n\nOutput a JSON object with fields: answer, confidence, evidence_refs, limitations."
        }
    ],
    "schema": { /* simple_qa schema */ },
    "options": { "temperature": 0.2, "max_tokens": 200, "format": "json" }
}
```

Token estimate: System 500 + Evidence 350 + Template 200 + Output 200 = 1250.

### Stage 4: LLM Inference

```jsonc
{
    "raw_response": "{\n  \"answer\": \"validateToken is a function that validates a JWT token against a provided configuration. It takes a token string and a TokenConfig object, returns a Promise<boolean>, and calls verifyToken() and checkExpiry() internally. It is called by authenticate() and refreshToken(). The function is located at src/auth/validate.ts:12-48.\",\n  \"confidence\": \"HIGH\",\n  \"evidence_refs\": [\"struc_001\", \"struc_003\"],\n  \"limitations\": [\"The response is based on static analysis only — runtime behavior may differ.\"]\n}"
}
```

### Stage 5: Response Parser

Validation:
- All evidence_refs (`struc_001`, `struc_003`) exist in assembled context. ✓
- Claims match evidence: ✅
- Claim "validateToken is at src/auth/validate.ts" matches `struc_001`. ✓
- Claim "calls verifyToken and checkExpiry" matches `struc_001`. ✓
- Claim "called by authenticate and refreshToken" matches `struc_003`. ✓

Confidence computation:
- Evidence confidences: [1.0, 0.95], weights: [1.0, 0.5]
- Weighted average: (1.0×1.0 + 0.95×0.5) / 1.5 = 0.983
- Coverage: 4/4 claims supported = 1.0
- Consistency penalty: 1.0 (no conflicts)
- Recency factor: 1.0
- Insight confidence: 0.983 × 1.0 × 1.0 × 1.0 = 0.983
- Display level: HIGH

### Stage 6: Explanation Formatter

```jsonc
{
    "id": "insight_simple_001",
    "type": "simple_qa",
    "title": "validateToken function analysis",
    "summary": "validateToken validates a JWT token using provided configuration. It calls verifyToken() and checkExpiry(), and is called by authenticate() and refreshToken(). Located at src/auth/validate.ts:12-48.",
    "confidence": 0.983,
    "severity": "INFO",
    "evidence_chain": {
        "insight": { "id": "insight_simple_001", "title": "validateToken function analysis", "confidence": 0.983 },
        "supporting_evidence": [
            {
                "evidence": { "id": "struc_001", "type": "FUNCTION_DEFINITION", "value": "validateToken(token: string, config: TokenConfig): Promise<boolean>", "confidence": 1.0 },
                "supports": "Directly defines the function signature and internal logic.",
                "derived_from": [{ "evidence_id": "struc_001", "raw_data_ref": "src/auth/validate.ts:12-48", "confidence": 1.0 }]
            },
            {
                "evidence": { "id": "struc_003", "type": "FUNCTION_CALLER", "value": "Called by authenticate(), refreshToken()", "confidence": 0.95 },
                "supports": "Provides caller context for the function.",
                "derived_from": [{ "evidence_id": "struc_003", "raw_data_ref": "src/auth/validate.ts:12", "confidence": 0.95 }]
            }
        ]
    },
    "recommendations": []
}
```

---

## Example 2: Evidence Synthesis

### Input

```
User question: "What is causing the authentication failures?"
```

### Stage 1: Intent Recognition

```jsonc
{
    "type": "question",
    "question": "What is causing the authentication failures?",
    "entities": [
        { "name": "authentication", "type": "module", "aliases": ["auth"] }
    ],
    "reasoning_type": "synthesis",
    "time_range": { "start": "2026-07-13T00:00:00Z", "end": "2026-07-14T23:59:59Z" }
}
```

### Stage 2: Context Builder

Entity resolution: `authentication` / `auth` → `mod_auth_001` (src/auth), `func_auth_validatetoken_001` (validateToken).

Evidence query returns 12 items across 2 engines. Abbreviated:

```jsonc
{
    "entities": [
        { "id": "mod_auth_001", "name": "src/auth", "type": "module" },
        { "id": "func_auth_validatetoken_001", "name": "validateToken", "type": "function" }
    ],
    "evidence": [
        {
            "id": "trace_001",
            "type": "FUNCTION_CALL",
            "engine": "trace_cognition",
            "confidence": 0.95,
            "value": "validateToken called 847 times, 312 errors (36.8%)"
        },
        {
            "id": "trace_002",
            "type": "EXCEPTION",
            "engine": "trace_cognition",
            "confidence": 0.98,
            "value": "TypeError: Cannot read property 'config' of undefined at validate.ts:88"
        },
        {
            "id": "trace_003",
            "type": "FUNCTION_CALL",
            "engine": "trace_cognition",
            "confidence": 0.90,
            "value": "authenticate() calls validateToken 100% of executions",
            "truncation_priority": "normal"
        },
        // ... 9 more items including metric data, evolution history
    ],
    "aggregates": {
        "error_rate": { "engine": "metric_cognition", "avg": 0.368, "trend": "increasing", "count": 847 }
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
        "reasoning_type": "synthesis"
    }
}
```

### Stage 3: Prompt Orchestrator

Template: `synthesis_v1`. Evidence fits within the 6000-token budget (4800 used, 1200 remaining). No truncation needed.

### Stage 4: LLM Inference

```jsonc
{
    "raw_response": "{\n  \"answer\": \"Authentication failures are caused by a recent deployment to src/auth/validate.ts (version 2.2.0, deployed 3 hours ago). The deployment introduced a code path where TokenConfig is undefined when the caller does not pass configuration explicitly. This causes a TypeError at line 88 in validate.ts, which is thrown before the JWT verification completes. The error rate increased from 5% to 36.8% immediately after deployment.\",\n  \"confidence\": \"MEDIUM\",\n  \"evidence_refs\": [\"trace_001\", \"trace_002\", \"metric_003\", \"evol_001\"],\n  \"patterns\": [\n    { \"description\": \"Error rate spike correlates precisely with deployment timestamp\", \"evidence_refs\": [\"trace_001\", \"evol_001\"] },\n    { \"description\": \"All errors trace to the same code path (validate.ts:88)\", \"evidence_refs\": [\"trace_002\"] }\n  ],\n  \"conflicting_evidence\": [\n    { \"claim_a\": \"error rate is 36.8%\", \"claim_b\": \"error rate is 42.1%\", \"resolution\": \"Discrepancy may be due to sampling window — trace data covers last 3 hours, metric data covers last 24 hours including pre-deployment baseline.\" }\n  ],\n  \"limitations\": [\"No direct evidence that version 2.2.0 introduced the undefined config path. Inference based on temporal correlation.\"]\n}"
}
```

### Stage 5: Response Parser

Validation:
- All evidence_refs reference valid evidence nodes. ✓
- Claims check:
  - "Error rate increased from 5% to 36.8%" — trace_001 shows 36.8%. No evidence for "5%" specifically (pre-deployment baseline not in context). Partial support.
  - "Deployment 3 hours ago" — evol_001 is a deployment record. ✓
  - "TypeError at line 88" — trace_002. ✓
  - "Deployment version 2.2.0" — evol_001. ✓
- Coverage: 4/5 claims supported = 0.80

Confidence computation:
- Evidence confidences: [0.95, 0.98, 0.85, 0.90], weights: [1.0, 1.0, 0.5, 0.5]
- Weighted average: (0.95 + 0.98 + 0.425 + 0.45) / 3 = 0.935
- Coverage: 0.80
- Consistency penalty: 0.95 (LOW conflict)
- Insight confidence: 0.935 × 0.80 × 0.95 = 0.711
- Display level: MEDIUM

### Stage 6: Explanation Formatter

```jsonc
{
    "title": "Root cause: Auth deployment introduced null config path",
    "summary": "Authentication failures are caused by a recent deployment to validate.ts (v2.2.0) that introduced an undefined TokenConfig code path, triggering TypeErrors on 36.8% of calls. Confidence: MEDIUM (0.71). Evidence: 12 items from trace_cognition, metric_cognition, evolution_cognition.",
    "detailed_explanation": "## Summary\n...\n## Key Findings\n- Error rate spike from 5% to 36.8% correlates with deployment at 07:00 UTC\n- All 312 errors trace to validate.ts:88 (TypeError: config is undefined)\n- authenticate() calls validateToken on every request — no bypass possible\n\n## Patterns Observed\n- Deployment-error correlation: error rate increased precisely at deployment time\n- Single code path: all TypeErrors originate from the same line\n\n## Evidence Overview\n- 12 items total\n- Conflict: 36.8% vs 42.1% error rate (explained by different time windows)\n\n## Limitations\n- No direct evidence linking version 2.2.0 to the undefined config. Inference based on temporal correlation.\n\n## Recommendation\n- Roll back src/auth/validate.ts to version 2.1.3 and verify error rate returns to baseline.",
    "confidence": 0.711,
    "severity": "HIGH",
    "recommendations": [{
        "action": "Roll back src/auth/validate.ts to version 2.1.3",
        "effort_estimate": "30 minutes",
        "risk": "LOW",
        "confidence": 0.85,
        "evidence_refs": ["trace_001", "trace_002"]
    }]
}
```

---

## Example 3: Decision Support

### Input

```
User question: "Should we refactor auth or rewrite it?"
```

### Stage 1: Intent Recognition

```jsonc
{
    "type": "decision",
    "question": "Should we refactor auth or rewrite it?",
    "entities": [{ "name": "auth", "type": "module" }],
    "reasoning_type": "decision_support",
    "time_range": null,
    "options": ["refactor", "rewrite"]
}
```

### Stage 2: Context Builder

Returns evidence about auth module: complexity metrics, evolution history, dependency graph, ownership data. 18 evidence items across 4 engines.

### Stage 3: Prompt Orchestrator

Template: `decision_support_v1`, with options ["refactor", "rewrite"] injected.

### Stage 4: LLM Inference

```jsonc
{
    "raw_response": "{\n  \"options\": [\n    {\n      \"name\": \"refactor\",\n      \"pros\": [\"Lower initial cost (estimated 2 weeks vs 6 weeks)\", \"Preserves existing interfaces — no breaking changes\", \"Team knows the codebase\"],\n      \"cons\": [\"May not address fundamental design issues\", \"Cyclomatic complexity of 47 remains high\", \"Might need repeated refactors\"],\n      \"evidence_refs\": [\"struc_002\", \"evol_005\", \"know_003\"],\n      \"risk_level\": \"MEDIUM\"\n    },\n    {\n      \"name\": \"rewrite\",\n      \"pros\": [\"Clean slate — can implement proper architecture\", \"Opportunity to reduce complexity from 47 to target < 20\"],\n      \"cons\": [\"High cost (estimated 6 weeks)\", \"Risk of new bugs in a critical path\", \"Alice is the only person who understands auth fully — rewrite would lose her context\"],\n      \"evidence_refs\": [\"risk_001\", \"know_001\", \"evol_003\"],\n      \"risk_level\": \"HIGH\"\n    }\n  ],\n  \"answer\": \"The evidence suggests refactoring is lower risk. The rewrite option carries significant knowledge loss risk because Alice is the sole owner (know_001).\",\n  \"confidence\": \"MEDIUM\",\n  \"evidence_refs\": [\"struc_002\", \"evol_005\", \"know_003\", \"risk_001\", \"know_001\"],\n  \"limitations\": [\"Effort estimates are from evolution velocity data, not project management inputs.\"]\n}"
}
```

### Stage 5: Response Parser

Confidence: 0.65 (MEDIUM). Coverage good (7/8 claims supported). No conflicts detected.

### Stage 6: Explanation Formatter

Produces full decision support explanation with options compared, trade-off table, and recommendation with risk levels.

---

## Example 4: Risk Evaluation

### Input

```
User question: "What are the risks in the auth module?"
```

### Stage 1: Intent Recognition

`reasoning_type: "risk_evaluation"`, entities: `auth`.

### Stage 2: Context Builder

Returns risk-oriented evidence: error rates, complexity metrics, dependency vulnerabilities, knowledge bus factor, trend data.

### Stage 3–4: Prompt Orchestrator → LLM

```
Risk evaluation template. LLM outputs structured risks with ratings.

Output: 4 risks identified:
1. "Single point of knowledge" — rating: HIGH (only Alice knows auth)
2. "Error rate degradation" — rating: HIGH (36.8%, increasing)
3. "Dependency vulnerability" — rating: MEDIUM (lodash@4.17 has 2 CVEs)
4. "Complexity hotspot" — rating: MEDIUM (cyclomatic 47)
```

### Stage 5: Response Parser

Confidence: 0.74 (MEDIUM). All risks reference real evidence.

### Stage 6: Explanation Formatter

```jsonc
{
    "title": "Auth module: 4 risks identified",
    "summary": "Auth module has 4 risks: a knowledge bus factor (HIGH), error rate degradation (HIGH), dependency vulnerabilities (MEDIUM), and complexity (MEDIUM).",
    "severity": "HIGH",
    "recommendations": [
        { "action": "Cross-train a second engineer on auth module", "risk": "HIGH", "effort": "2 weeks" },
        { "action": "Roll back recent validate.ts deployment", "risk": "HIGH", "effort": "30 minutes" },
        { "action": "Update lodash to 4.18+", "risk": "MEDIUM", "effort": "1 hour" },
        { "action": "Refactor validate.ts to reduce cyclomatic complexity", "risk": "MEDIUM", "effort": "3 days" }
    ]
}
```

---

## Example 5: Prediction

### Input

```
User question: "How will auth module health trend over the next 3 months?"
```

### Stage 1: Intent Recognition

`reasoning_type: "prediction"`, time range: next 3 months.

### Stage 2: Context Builder

Returns historical trend data: error rates over 6 months, complexity evolution, deployment frequency, team changes.

### Stage 3–4: Prompt Orchestrator → LLM

Prediction template with trend evidence. LLM outputs:

```
Predictions:
1. "Error rate will exceed 50% within 6 weeks if no intervention" — supported, confidence HIGH
2. "Cyclomatic complexity will reach 60 within 3 months at current growth rate" — supported, confidence HIGH
3. "Knowledge bus factor risk will increase if Alice leaves" — inferred, confidence MEDIUM
4. "Dependency vulnerabilities will accumulate as lodash version ages" — supported, confidence HIGH
```

### Stage 5: Response Parser

Confidence: 0.68 (MEDIUM). 3 of 4 predictions are "supported" (direct evidence), 1 is "inferred" (logical extension).

### Stage 6: Explanation Formatter

Produces prediction timeline with confidence intervals. "Supported" predictions shown with solid trend lines. "Inferred" shown as dashed with caveat.

---

## Example 6: Insufficient Evidence

### Input

```
User question: "What is the test coverage of the notification module?"
```

### Stage 1: Intent Recognition

`reasoning_type: "simple_qa"`, entities: `notification`.

### Stage 2: Context Builder

Entity resolution: `notification` → `mod_notification_001`.

Evidence query returns 0 items — no test coverage data has been collected for this module.

```jsonc
{
    "entities": [{ "id": "mod_notification_001", "name": "src/notification", "type": "module" }],
    "evidence": [],
    "metadata": {
        "total_evidence": 0,
        "status": "NO_EVIDENCE",
        "reason": "No evidence found for entity 'src/notification' with type 'test_coverage'."
    }
}
```

### Stages 3–4: Skipped

Context Builder returns `status: "NO_EVIDENCE"`. Pipeline short-circuits: no LLM call, no prompt construction.

### Stage 5: Response Parser

Receives empty context. Returns deterministic response:

```jsonc
{
    "answer": "Insufficient evidence available to answer this question.",
    "confidence": 0.0,
    "display_level": "INSUFFICIENT_EVIDENCE",
    "evidence_refs": [],
    "limitations": ["No test coverage data exists for the notification module. See Phase 4 for available engines that produce coverage-related evidence."]
}
```

### Stage 6: Explanation Formatter

```jsonc
{
    "title": "Insufficient evidence: test coverage of notification module",
    "summary": "Project DNA has no evidence about test coverage for the notification module. No test coverage analysis has been run.",
    "confidence": 0.0,
    "severity": "INFO",
    "evidence_chain": { "insight": {}, "supporting_evidence": [] },
    "recommendations": [{
        "action": "Run analysis that produces coverage-related evidence (see Phase 4 — Cognitive Engines)",
        "effort_estimate": "Automated — add module to analysis scope",
        "risk": "LOW",
        "confidence": 1.0
    }]
}
```

---

## Example 7: Deterministic Fallback

### Input

```
User question: "What is causing the auth failures?" (same as Example 2)
```

### Scenario

Ollama is not running. Stage 4 (LLM Inference) health check fails. Retry once, still fails.

### Stage 4: LLM Inference

```jsonc
{
    "status": "failed",
    "error": "Ollama not running at localhost:11434. Model llama3.1:8b-q4_K_M unavailable.",
    "fallback": true
}
```

### Stage 5: Response Parser

Receives fallback signal. Reads AssembledContext directly. Produces deterministic evidence summary:

```jsonc
{
    "fallback_reason": "LLM_UNAVAILABLE",
    "summary": "AI reasoning is currently unavailable. Here is a summary of the evidence found.",
    "evidence": [
        { "id": "trace_001", "type": "FUNCTION_CALL", "detail": "validateToken: 312 errors (36.8%)", "source": "trace_cognition" },
        { "id": "trace_002", "type": "EXCEPTION", "detail": "TypeError at validate.ts:88", "source": "trace_cognition" }
        // ... 10 more items listed as-is
    ],
    "insight_confidence": 0.0,
    "display_level": "UNAVAILABLE"
}
```

### Stage 6: Explanation Formatter

```jsonc
{
    "title": "Evidence Summary: auth failures",
    "summary": "AI reasoning is currently unavailable. Here is a summary of the evidence found for your query.",
    "detailed_explanation": "The following evidence was found. No AI synthesis was performed.",
    "confidence": 0.0,
    "severity": "INFO",
    "fallback_reason": "LLM_UNAVAILABLE",
    "evidence_chain": {
        "insight": { "title": "Evidence Summary", "confidence": 0.0 },
        "supporting_evidence": [
            { "evidence": { "id": "trace_001", "type": "FUNCTION_CALL", "value": "validateToken called 847 times, 312 errors (36.8%)", "confidence": 0.95 } },
            { "evidence": { "id": "trace_002", "type": "EXCEPTION", "value": "TypeError at validate.ts:88", "confidence": 0.98 } }
        ]
    },
    "recommendations": []
}
```

The user receives a transparent evidence list to reason about themselves, clearly marked as "AI unavailable" rather than a simulated insight.

---

## Summary of All Examples

| Example | Reasoning Type | Evidence Count | Confidence | Pipeline Stages Executed | Outcome |
|---|---|---|---|---|---|
| 1 — Simple QA | simple_qa | 3 | 0.983 (HIGH) | 1–6 all | Direct answer with high confidence |
| 2 — Synthesis | synthesis | 12 | 0.711 (MEDIUM) | 1–6 all | Root cause analysis with recommendation |
| 3 — Decision Support | decision_support | 18 | 0.650 (MEDIUM) | 1–6 all | Option comparison with trade-offs |
| 4 — Risk Evaluation | risk_evaluation | 15 | 0.740 (MEDIUM) | 1–6 all | Risk register with 4 items |
| 5 — Prediction | prediction | 20 | 0.680 (MEDIUM) | 1–6 all | Forecast with confidence intervals |
| 6 — Insufficient Evidence | simple_qa | 0 | 0.000 (INSUFFICIENT) | 1–2 only | Early return, no LLM call |
| 7 — Fallback | synthesis | 12 (unused) | 0.000 (UNAVAILABLE) | 1–2, 4–6 (skipped) | Evidence summary, no AI |
