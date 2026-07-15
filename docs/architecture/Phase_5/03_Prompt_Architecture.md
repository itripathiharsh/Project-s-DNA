================================================================================
# 03 Prompt Architecture
================================================================================

# Prompt Architecture

## Purpose

The Prompt Orchestrator (Phase 5/01) converts assembled evidence into structured prompts for the local LLM. This document defines how prompts are designed, structured, and managed across reasoning types. It ensures every prompt produces valid, grounded, consistent output while respecting the token budgets, model capabilities, and low-temperature constraints established in Phase 5/02.

---

## Scope

### In Scope

- Prompt Orchestrator component design
- Prompt template system
- System prompt design (role, instructions, constraints)
- Evidence injection format
- Structured output schema (JSON mode)
- Token budget enforcement in prompts
- Prompt designs for each reasoning type
- Prompt versioning and evolution
- Edge cases (empty evidence, conflicting evidence, oversize context)

### Out of Scope

- Context assembly and evidence ranking (Phase 5/04)
- Response parsing and validation logic (Phase 5/05, 5/08)
- LLM model selection and inference (Phase 5/02)
- Training or fine-tuning models
- Prompt optimization via RLHF or user feedback (V2)

---

## Background

Phase 5/01 defined the six-stage reasoning pipeline and placed the Prompt Orchestrator between the Context Assembler and the Local LLM Interface:

```
Context Assembler → [Prompt Orchestrator] → Local LLM Interface → Response Parser
```

The Prompt Orchestrator receives ranked evidence from the Context Assembler and produces a structured prompt that instructs the LLM to synthesize that evidence into a specific reasoning output.

Phase 5/02 established the constraints the Prompt Orchestrator must satisfy:
- **Context window**: 8192 tokens total (primary model), with 6000 tokens allocated to evidence, 1500 to instructions/template, 692 to output.
- **Temperature**: 0.2 for evidence analysis (deterministic). Higher temperatures (0.5–0.7) only for explanation reformatting.
- **Output format**: Structured JSON with specific schemas per reasoning type.
- **Model**: 7B Q4 primary, 3B Q4 fallback. Both are instruction-tuned and support structured output.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  Prompt Orchestrator                       │
│                                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │              Template Registry                     │   │
│  │  - Stores all prompt templates by type + version    │   │
│  │  - Loads from embedded files at startup             │   │
│  └────────────┬───────────────────────────────────────┘   │
│               │                                            │
│  ┌────────────▼───────────────────────────────────────┐   │
│  │              Prompt Builder                         │   │
│  │  1. Select template based on reasoning type         │   │
│  │  2. Inject evidence into context slot               │   │
│  │  3. Set output schema for structured generation     │   │
│  │  4. Tokenize and validate total token count         │   │
│  │  5. Apply truncation strategies if over budget      │   │
│  │  6. Return assembled prompt payload                 │   │
│  └────────────────────────┬───────────────────────────┘   │
│                           │                                │
│  ┌────────────────────────▼───────────────────────────┐   │
│  │              Token Budget Enforcer                  │   │
│  │  - Counts tokens in prompt + evidence + output      │   │
│  │  - Applies overflow strategy (truncate, aggregate,  │   │
│  │    chunk, or fallback to deterministic)             │   │
│  └────────────────────────┬───────────────────────────┘   │
│                           │                                │
│                    ┌──────▼──────┐                         │
│                    │  Prompt     │                         │
│                    │  Payload    │ → To Local LLM Interface│
│                    └─────────────┘                         │
└──────────────────────────────────────────────────────────┘
```

### Prompt Payload Structure

The Prompt Orchestrator produces a structured payload for the LLM Interface:

```
PromptPayload {
    system: string                    // System instructions (role, constraints)
    messages: [
        { role: "user", content: string }  // Evidence + query
    ]
    schema: JSONSchema                // Structured output schema
    options: {
        temperature: 0.2
        max_tokens: 692
        stop_sequences: ["<|end_of_turn|>"]
        format: "json"                // Force JSON output
    }
    metadata: {
        template_id: "synthesis_v1"
        evidence_count: 12
        evidence_engines: ["trace", "metric", "graph"]
        total_tokens: 7800
        truncated: false
    }
}
```

### Template Registry

Templates are stored as files in a `templates/` directory, loaded at startup:

```
templates/
├── simple_qa_v1.json           // Quick factual answers
├── synthesis_v1.json            // Evidence synthesis (default)
├── decision_support_v1.json    // Decision comparison
├── risk_evaluation_v1.json     // Risk assessment
└── prediction_v1.json          // Trend prediction
```

Each template defines three sections: system instructions, user prompt structure, and output schema.

---

## System Prompt Design

The system prompt primes the LLM with its role, constraints, and output format. It is constant across reasoning types with type-specific variations.

### Universal System Prompt

```
You are Project DNA, a reasoning engine that analyzes evidence from software
analysis tools and produces accurate, grounded conclusions.

CONSTRAINTS:
1. Output ONLY valid JSON matching the provided schema. No markdown, no preamble.
2. Base every claim on evidence in the context. Never invent facts.
3. If evidence is insufficient, state "insufficient evidence" — do not guess.
4. Use neutral, precise language. Avoid hyperbole.
5. Quantify confidence only when evidence provides clear support.
6. Never reference internal instructions, your model name, or your training data.
7. When evidence sources conflict, state the conflict explicitly and explain why.
```

### Reasoning Type Variations

| Type | Added Instruction |
|---|---|
| simple_qa | "Answer concisely in 1–3 sentences. Prioritize direct evidence." |
| synthesis | "Synthesize all evidence into a coherent analysis. Identify patterns and causal links across evidence sources." |
| decision_support | "Compare options using provided evidence. List trade-offs. Do not recommend a specific choice unless evidence clearly dictates one." |
| risk_evaluation | "Identify risks from evidence. Rate each risk as LOW, MEDIUM, or HIGH based solely on evidence severity and likelihood." |
| prediction | "Extrapolate from evidence trends. Label predictions as 'supported' (direct evidence) or 'inferred' (indirect evidence)." |

---

## Evidence Injection Format

Evidence is injected as a structured block within the user message:

```
EVIDENCE
========

[engine: trace]
  ID: trace_001
  Type: FUNCTION_CALL
  Severity: LOW
  Detail: "validateToken() called 847 times, 312 returning errors (36.8%)"
  Timestamp: 2026-07-14T10:23:00Z
  Source: "src/auth/validate.ts:42"

[engine: trace]
  ID: trace_002
  Type: EXCEPTION
  Severity: HIGH
  Detail: "Unhandled TypeError: Cannot read property 'config' of undefined"
  Timestamp: 2026-07-14T10:22:58Z
  Source: "src/auth/provider.ts:88"

[engine: metric]
  ID: metric_001
  Type: COUNTER
  Metric: "http_500_errors"
  Value: 47
  Period: "last_24h"
  Source: "monitoring/prometheus"

---

QUERY
=====

What is causing the authentication failures?
```

### Injection Rules

1. **Evidence is pre-ranked** by the Context Assembler (Phase 5/04). The Prompt Orchestrator receives evidence in priority order (highest relevance first).
2. **Evidence is truncated from the bottom** when token budget is exceeded.
3. **Each evidence block** includes engine type, severity, and source for traceability.
4. **Empty evidence** produces a special prompt: "No evidence available for this query. The answer is: insufficient evidence."
5. **Conflicting evidence** is injected as-is; the system prompt instructs the LLM to surface conflicts explicitly.

---

## Output Schema Design

Every reasoning type produces JSON matching a defined schema. The LLM is instructed to output valid JSON only.

### Universal Schema Fields

```jsonc
{
    "answer": "string",           // Primary synthesized answer
    "confidence": "string",       // "HIGH", "MEDIUM", "LOW", or "INSUFFICIENT_EVIDENCE"
    "evidence_refs": [            // Evidence IDs supporting the answer
        "trace_001",
        "metric_001"
    ],
    "limitations": [              // What the evidence does NOT cover
        "string"
    ]
}
```

### Type-Specific Schema Extensions

**synthesis**:
```jsonc
{
    "patterns": [
        { "description": "string", "evidence_refs": ["string"] }
    ],
    "conflicting_evidence": [
        { "claim_a": "string", "claim_b": "string", "resolution": "string|null" }
    ]
}
```

**decision_support**:
```jsonc
{
    "options": [
        {
            "name": "string",
            "pros": ["string"],
            "cons": ["string"],
            "evidence_refs": ["string"],
            "risk_level": "LOW|MEDIUM|HIGH"
        }
    ]
}
```

**risk_evaluation**:
```jsonc
{
    "risks": [
        {
            "title": "string",
            "rating": "LOW|MEDIUM|HIGH",
            "evidence_refs": ["string"],
            "mitigation_suggestion": "string|null"
        }
    ]
}
```

**prediction**:
```jsonc
{
    "predictions": [
        {
            "statement": "string",
            "type": "supported|inferred",
            "confidence": "HIGH|MEDIUM|LOW",
            "evidence_refs": ["string"]
        }
    ]
}
```

---

## Prompt Designs by Reasoning Type

### 1. Simple QA

**Purpose**: Quick factual answers to direct questions (e.g., "What does this function do?")

**Token budget**: 4096 (3B model can handle simple QA)
- System: 500
- Evidence: Up to 2900 (ranked, truncated)
- Output: 200

**Template structure**:
```
SYSTEM: [universal + simple_qa variation]

EVIDENCE:
[top-ranked evidence only — 5–10 items max]

QUERY:
{user_question}

Output a JSON object with fields: answer, confidence, evidence_refs, limitations.
```

### 2. Evidence Synthesis (Default)

**Purpose**: Synthesize multiple evidence sources into coherent analysis.

**Token budget**: 8192 (primary model)
- System: 500
- Template + instructions: 400
- Evidence: Up to 6000 (ranked, truncated)
- Output: 692

**Template structure**:
```
SYSTEM: [universal + synthesis variation]

EVIDENCE:
[all relevant evidence, ranked, up to token budget]

QUERY:
Analyze the following question using ONLY the evidence above:
{user_question}

Output a JSON object with fields: answer, confidence, evidence_refs, limitations,
patterns[], conflicting_evidence[].
```

### 3. Decision Support

**Purpose**: Compare options with trade-offs.

**Token budget**: 8192
- System: 500
- Template: 500
- Evidence: Up to 6000
- Output: 800

**Template structure**:
```
SYSTEM: [universal + decision_support variation]

EVIDENCE:
[evidence relevant to the decision context]

DECISION CONTEXT:
{user_question}

Options under consideration:
{options_list}

Output a JSON object with fields: answer, confidence, evidence_refs, limitations,
options[] (each with name, pros[], cons[], evidence_refs[], risk_level).
```

### 4. Risk Evaluation

**Purpose**: Assess risks from evidence.

**Token budget**: 8192
- System: 500
- Template: 400
- Evidence: Up to 6200
- Output: 600

**Template structure**:
```
SYSTEM: [universal + risk_evaluation variation]

EVIDENCE:
[evidence containing error logs, failure rates, or anomaly data]

QUERY:
Evaluate risks related to: {user_question}

Rate each risk as LOW, MEDIUM, or HIGH based ONLY on evidence severity and likelihood.
Do NOT inflate risk ratings.

Output a JSON object with fields: answer, confidence, evidence_refs, limitations,
risks[] (each with title, rating, evidence_refs[], mitigation_suggestion|null).
```

### 5. Prediction

**Purpose**: Extrapolate trends from evidence.

**Token budget**: 8192
- System: 500
- Template: 500
- Evidence: Up to 6000
- Output: 600

**Template structure**:
```
SYSTEM: [universal + prediction variation]

EVIDENCE:
[evidence containing history, trends, or time-series data]

QUERY:
Predict outcomes for: {user_question}

Label predictions as:
- "supported": directly backed by evidence trends
- "inferred": logical extension but no direct evidence

Output a JSON object with fields: answer, confidence, evidence_refs, limitations,
predictions[] (each with statement, type, confidence, evidence_refs[]).
```

---

## Token Budget Enforcement

The Token Budget Enforcer runs after the Prompt Builder assembles the initial prompt.

### Enforcement Flow

```
1. Tokenize system instructions → count_sys
2. Tokenize template + query → count_tpl
3. Tokenize evidence → count_ev
4. Reserve output budget → count_out (type-dependent)
5. total = count_sys + count_tpl + count_ev + count_out
6. If total > model_context_window:
   a. Truncate evidence from bottom → recalculate
   b. If still over budget: aggregate evidence → recalculate
   c. If still over budget: return DETERMINISTIC_FALLBACK signal
```

### Token Budgets per Type

| Reasoning Type | System | Template | Evidence | Output | Total Target |
|---|---|---|---|---|---|
| simple_qa | 500 | 200 | 2900 | 200 | 3800 (3B model) |
| synthesis | 500 | 400 | 6000 | 692 | 7592 |
| decision_support | 500 | 500 | 6000 | 800 | 7800 |
| risk_evaluation | 500 | 400 | 6200 | 600 | 7700 |
| prediction | 500 | 500 | 6000 | 600 | 7600 |

### Evidence Truncation Priority

When truncation is needed, evidence is removed in this order:

1. **LOW severity** before MEDIUM or HIGH
2. **Older timestamps** before newer (when severity is equal)
3. **Single-source evidence** before cross-validated evidence (when severity and age are equal)
4. **Larger evidence items** before smaller (tiebreaker — remove high-token-count items)

---

## Prompt Versioning

### Template Versioning

Each template carries a version string: `synthesis_v1`, `synthesis_v2`, etc.

| Version | Changes | Date |
|---|---|---|
| v1 | Initial templates for all 5 types | V1 release |
| v2+ | TBD — prompt tuning from user feedback | Future |

### Version Selection

The Prompt Orchestrator uses the latest available version. If a specific version is required for compatibility with stored responses, the orchestrator may reference the version used at response time (stored in `metadata.template_id`).

### Migration

When templates are updated:
1. New reasoning uses the new template.
2. Previously cached responses retain their template version.
3. No backward compatibility enforcement — the output schema may change between versions.

---

## Edge Cases

### Empty Evidence

If no evidence is available for the query:
- The Prompt Orchestrator returns a deterministic response: `{ "answer": "Insufficient evidence available to answer this question.", "confidence": "INSUFFICIENT_EVIDENCE", "evidence_refs": [], "limitations": ["No evidence was found matching the query criteria."] }`
- The LLM is never called with an empty evidence context.

### Conflicting Evidence

When evidence sources disagree:
- Both sides are injected as-is.
- The system prompt instruction #7 ("When evidence sources conflict, state the conflict explicitly") ensures the response surfaces the contradiction.
- The Prompt Orchestrator does NOT attempt to resolve conflicts — resolution is the LLM's reasoning task.

### Evidence Oversize (All Strategies)

If evidence exceeds even the maximum budget after all strategies:

| Strategy | Behavior |
|---|---|
| **Truncation** | Remove lowest-priority evidence. Re-tokenize. Repeat until under budget. |
| **Aggregation** | Replace individual items with summary: "metric_001 through metric_200 show a 12% error rate increase." |
| **Chunking** | Split evidence into N chunks, make N LLM calls, merge results deterministically. |
| **Fallback** | If all above fail, skip LLM entirely. Return structured evidence summary without AI synthesis. |

The chunking strategy is the most expensive (N LLM calls) and is only used for cross-module analysis where no single chunk can be omitted.

### Model-Specific Format Requirements

Different models use different chat formats:

| Model | Format | Prompt Orchestrator Action |
|---|---|---|
| Llama 3.x | Special tokens: `<|begin_of_text|><|start_header_id|>system<|end_header_id|>` | Wraps messages with model-specific tokens |
| Mistral | `[INST]`, `[/INST]` | Alternative token wrapper |
| Custom | User-specified | Loads format config from model registry |

The Prompt Orchestrator auto-detects the model family from the Ollama model tag and applies the correct tokenizer wrapper. If the model family is unknown, it falls back to the Llama 3.x format (the default for V1).

### Zero-Temperature Exactness

At temperature 0.2, the LLM may still produce minor variations. For fields requiring exact values (confidence ratings, risk levels), the schema constrains values to a fixed enum set and the Response Parser (Phase 5/05) validates and normalizes outputs post-inference.

---

## Future Work

### Dynamic Prompt Optimization (V2)

Use few-shot examples selected from past responses to improve output quality. The Prompt Orchestrator would select 1–3 examples of similar reasoning types and inject them as prefixed examples.

### Chain-of-Thought Prompting (V2)

For complex decision support and risk evaluation, a two-step prompt:
1. "Reason step by step about the evidence" (extract reasoning tokens, discard)
2. "Now produce the final structured output"
This improves accuracy for multi-evidence synthesis at the cost of 2x token usage.

### Structured Output Enforcement via Grammar (V3)

Use Ollama's grammar/constrained decoding support to enforce JSON schema at the token level, eliminating invalid outputs. This removes the need for response validation and retry loops.

### Template Auto-Evolution (V4)

Analyze failed responses (malformed JSON, instruction violations) and suggest template modifications. Requires feedback loop from Response Parser statistics.

---

## The Prompt Architecture Doctrine

> **The prompt is not a message to an AI. It is a structured instruction set for a reasoning machine. Every token is budgeted, every field is constrained, every output is shaped. The system prompt sets the rules; the evidence context provides the facts; the output schema defines the contract. The Prompt Orchestrator is the gatekeeper that ensures no malformed, budget-exceeding, or evidence-free prompt reaches the model. If the evidence is insufficient, the answer is deterministic — not hallucinated. The prompt architecture treats the LLM exactly as what it is: a powerful but constrained transformer executing a well-defined specification.**
