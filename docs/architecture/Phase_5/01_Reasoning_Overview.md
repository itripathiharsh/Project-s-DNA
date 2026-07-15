================================================================================
# 01 Reasoning Overview
================================================================================

# Cognitive Reasoning Layer — Overview

## Purpose

The Cognitive Reasoning Layer transforms deterministic evidence stored in the Software Cognition Model into human-readable, evidence-backed insights, explanations, and recommendations. It is the component that reads what the Cognitive Engines discovered, selects what is relevant to the user's question, synthesizes evidence into coherent understanding, and presents that understanding with traceable evidence chains.

This document defines the architecture, principles, and pipeline of the reasoning layer. It is the foundation for every subsequent document in Phase 5.

---

## Scope

### In Scope

- Architecture of the Cognitive Reasoning Layer
- The reasoning pipeline: from question to explanation
- Component boundaries and interfaces
- Confidence model at the reasoning level
- Evidence chain preservation across reasoning
- Types of reasoning supported in V1
- Performance targets and failure modes
- Relationship to the SCM, Cognitive Engines, and API layer

### Out of Scope

- LLM model selection and configuration (Phase 5/02)
- Prompt template design and management (Phase 5/03)
- Context assembly algorithms and evidence ranking (Phase 5/04)
- Detailed confidence propagation mathematics (Phase 5/05)
- Explainability UI components and rendering (Phase 5/06)
- Memory persistence and recall mechanisms (Phase 5/07)
- Reasoning pipeline implementation details (Phase 5/08)
- API endpoint design (Phase 6)
- UI implementation (Phase 7)

---

## Background

The first four phases of Project DNA established a complete perception and storage system:

- **Phase -1** established that understanding requires explanation, not just measurement. First Principle 2 (Evidence Before Reasoning) mandates that AI never invents understanding — it only explains what evidence proves. First Principle 5 (Explainability is Non-Negotiable) requires every conclusion to be traceable. First Principle 8 (Deterministic Before Probabilistic) establishes that evidence is deterministic while reasoning may be probabilistic.

- **Phase 3** defined the Software Cognition Model, a multi-model data structure with four pillars: Perception Store (raw engine output), Representation Store (entities and relationships), Reasoning Store (insights and evidence chains), and Temporal Store (history and trends). The SCM is the single source of truth for all understanding.

- **Phase 4** defined the Cognitive Engines — eight deterministic, testable modules that perceive software across dimensions (Structural, Evolution, Knowledge, Dependency, Risk, Architectural, Decision, Prediction). Each engine produces structured evidence and writes it to the SCM.

These phases complete the **perception** and **representation** pillars of cognition. What remains is **reasoning** and **explanation** — the transformation of evidence into understanding.

The Cognitive Reasoning Layer fills that gap.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  User Interface (Phase 7) / External API (Phase 6)                  │
├─────────────────────────────────────────────────────────────────────┤
│                   Cognitive Reasoning Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │ Context  │  │ Prompt   │  │ Local LLM│  │  Explanation        │ │
│  │ Assembler│→│Orchestrator│→│ Interface│→│  Formatter          │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────────┘ │
│       │              │              │               │               │
│       ▼              ▼              ▼               ▼               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Response Parser & Validator                                 │   │
│  │  (Extracts structured insights, validates against evidence)  │   │
│  └─────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│  Software Cognition Model (SCM) — Phase 3                           │
│  (Evidence Store, Reasoning Store, Query Interface)                 │
├─────────────────────────────────────────────────────────────────────┤
│  Cognitive Engines (Phase 4) / Processing Pipeline (Phase 2)        │
└─────────────────────────────────────────────────────────────────────┘
```

The Reasoning Layer is invoked on demand (when a user asks a question or when a new insight is evaluated) rather than continuously like the engines. It is a stateless or semi-stateless computation layer that reads from the SCM, processes, and writes insights back to the SCM's Reasoning Store.

---

## The Reasoning Pipeline

The reasoning pipeline transforms a user's question or a system-triggered evaluation into a structured insight through six stages:

### Stage 1: Intent Recognition

The pipeline receives input — either a natural language question from the user or a trigger event from the system (e.g., a new piece of evidence crosses a significance threshold).

**Input:** Raw question string or trigger event.
**Process:** Parse the input to identify intent (question, decision, alert, exploration), entities mentioned (module names, metric types, people), and time constraints.
**Output:** Structured query intent with entity references.

### Stage 2: Context Assembly

The Context Assembler gathers relevant evidence from the SCM based on the parsed intent.

**Input:** Structured query intent.
**Process:**
1. Query the SCM for entities matching the intent.
2. Retrieve evidence nodes related to those entities.
3. Retrieve historical context (trends, past insights).
4. Rank and filter evidence by relevance, recency, and confidence.
5. Compute aggregate statistics where needed.
**Output:** Assembled context — a structured set of evidence nodes, metrics, and historical data ready for reasoning.

### Stage 3: Prompt Construction

The Prompt Orchestrator formats the assembled context into a prompt for the local LLM.

**Input:** Assembled context.
**Process:**
1. Select the appropriate prompt template based on reasoning type.
2. Inject context into the template.
3. Apply token budget constraints (truncate or summarize if context exceeds model limits).
4. Attach system instructions governing reasoning behavior.
**Output:** A complete prompt ready for LLM inference.

### Stage 4: LLM Inference

The Local LLM Interface sends the prompt to the local LLM and receives a response.

**Input:** Prompt.
**Process:**
1. Send prompt to Ollama (or configured alternative).
2. Stream response tokens if real-time output is required.
3. Handle errors, timeouts, and retries.
**Output:** Raw LLM response text.

### Stage 5: Response Parsing and Validation

The Response Parser extracts structured data from the LLM response and validates it against the original evidence.

**Input:** Raw LLM response text + original assembled context.
**Process:**
1. Parse the response into structured fields: conclusion, reasoning, confidence, recommendations, evidence references.
2. Validate every claim against the original evidence set.
3. Flag claims that contradict or extend beyond the evidence.
4. Compute overall confidence based on evidence strength.
5. If validation fails below a threshold, fall back to deterministic insight.
**Output:** Structured insight with validated evidence references.

### Stage 6: Explanation Formatting

The Explanation Formatter structures the validated insight into a human-readable explanation with traceable evidence chains.

**Input:** Structured insight.
**Process:**
1. Generate the evidence chain linking insight → supporting evidence → raw data.
2. Format the explanation in layers (summary → detail → evidence drill-down).
3. Assign severity, confidence, and recommendation metadata.
4. Write the insight to the SCM Reasoning Store.
**Output:** Formatted insight ready for API delivery and UI rendering.

---

## Guiding Principles

The Reasoning Layer operates under six principles derived from Phase -1:

### Principle 1: Evidence-Bound Reasoning

Every conclusion the Reasoning Layer produces must be directly supported by evidence in the SCM. The LLM is never asked to generate facts, only to reason about existing facts. If the evidence is insufficient, the insight must state that explicitly.

### Principle 2: Deterministic Fallback

If the LLM response cannot be validated against the evidence (confidence below threshold, hallucination detected, parse failure), the system falls back to a deterministic insight — a structured summary of evidence without LLM synthesis. Users always receive something grounded, never a fabricated explanation.

### Principle 3: Transparency of Uncertainty

Every insight carries a confidence score derived from the strength of its supporting evidence. Users can always see why a particular confidence was assigned. Confidence is never hidden or glossed over.

### Principle 4: Minimal AI Surface

The LLM is used only where probabilistic reasoning adds value — synthesizing multiple evidence sources, identifying causal relationships, generating natural language explanations. Where deterministic logic suffices (sorting, filtering, aggregating), the system uses deterministic code, not the LLM. This minimizes hallucination risk.

### Principle 5: Traceability Always

Every insight preserves a complete evidence chain from conclusion to raw data. The Reasoning Layer never discards or obscures evidence references. The evidence chain is a first-class output, not an afterthought.

### Principle 6: Human Primacy

The Reasoning Layer suggests. It never commands. All outputs are recommendations with confidence scores. The human remains the decision-maker.

---

## Components

### Context Assembler

**Responsibility:** Gather, rank, and package relevant evidence from the SCM for a given reasoning request.

**Inputs:** Structured query intent, SCM Query Interface.
**Outputs:** AssembledContext — ordered list of evidence nodes with metadata.
**Key Behaviors:**
- Entity resolution: map names in the question to SCM entity IDs.
- Evidence selection: choose evidence relevant to the question type.
- Recency weighting: prefer recent evidence for time-sensitive questions.
- Token budget management: estimate total tokens, prepare truncation strategy.

### Prompt Orchestrator

**Responsibility:** Select the correct prompt template, inject context, manage token limits, and produce a final prompt.

**Inputs:** AssembledContext, PromptTemplate registry.
**Outputs:** Final prompt string.
**Key Behaviors:**
- Template selection by reasoning type.
- Variable substitution (evidence, entities, time range).
- Token counting and truncation.
- System instruction injection.

### Local LLM Interface

**Responsibility:** Communicate with the local LLM runtime (Ollama), handle inference, manage failures.

**Inputs:** Prompt string.
**Outputs:** Raw LLM response string or stream.
**Key Behaviors:**
- Model loading and caching.
- Request/response handling.
- Timeout and retry logic.
- Model fallback (switch to smaller model if primary fails).
- Streaming support for real-time UI.

### Response Parser

**Responsibility:** Extract structured fields from LLM output and validate every claim against the evidence.

**Inputs:** Raw LLM response, AssembledContext.
**Outputs:** ParsedInsight — structured insight with validated evidence references.
**Key Behaviors:**
- Structured output extraction (JSON, XML, or constrained format).
- Evidence reference cross-checking.
- Hallucination detection (claims without supporting evidence).
- Confidence recalculation based on validation results.
- Fallback trigger on failed validation.

### Explanation Formatter

**Responsibility:** Transform a ParsedInsight into a formatted explanation ready for storage and delivery.

**Inputs:** ParsedInsight.
**Outputs:** FormattedInsight — explanation with evidence chain, severity, confidence, and recommendations.
**Key Behaviors:**
- Evidence chain construction (graph of insight → evidence → raw data).
- Multi-layer explanation generation (summary, detail, drill-down).
- Severity assignment based on confidence and impact heuristics.
- Recommendation formatting with effort estimates and risk levels.
- SCM write (insight stored in Reasoning Store).

### Insight Validator

**Responsibility:** Continuous validation and quality assurance of insights produced by the pipeline.

**Inputs:** FormattedInsight, historical insight data.
**Outputs:** ValidationReport — pass/fail with reasons.
**Key Behaviors:**
- Consistency check: does this insight contradict any active insight in the SCM?
- Completeness check: are all required fields present?
- Freshness check: is the evidence recent enough?
- Redundancy check: does this insight duplicate an existing active insight?

---

## Interfaces

### Input Interfaces

| Interface | Source | Format | Description |
|---|---|---|---|
| `POST /reason/question` | API Gateway (Phase 6) | `{ question: string, context: optional }` | Natural language question |
| `POST /reason/evaluate` | Engine Orchestrator | `{ trigger: Event, evidence: UUID[] }` | System-triggered insight evaluation |
| `SCM Query` | SCM Query Interface | Query builder pattern | Evidence retrieval during assembly |

### Output Interfaces

| Interface | Destination | Format | Description |
|---|---|---|---|
| `Insight` | SCM Reasoning Store | Structured Insight object | Persistent storage |
| `Explanation` | API Gateway (Phase 6) | Formatted explanation with evidence chain | Delivery to UI |
| `ValidationReport` | Monitoring / Logging | Structured report | Quality assurance |

### Internal Interfaces

| Interface | Between | Format | Description |
|---|---|---|---|
| `AssembledContext` | Context Assembler → Prompt Orchestrator | Structured evidence bundle | Context for reasoning |
| `Prompt` | Prompt Orchestrator → LLM Interface | String | Formatted prompt |
| `RawResponse` | LLM Interface → Response Parser | String | LLM output |
| `ParsedInsight` | Response Parser → Explanation Formatter | Structured insight | Validated reasoning result |
| `FormattedInsight` | Explanation Formatter → Insight Validator | Formatted insight | Pre-storage validation |

---

## Data Structures

### AssembledContext

```
AssembledContext {
    intent: {
        type: enum (question, decision, alert, exploration)
        entities: Entity[]
        time_range: TimeRange (optional)
        question: string (original)
    }
    evidence: [
        {
            id: UUID
            type: EvidenceType
            category: EvidenceCategory
            value: JSONB
            confidence: ConfidenceLevel
            source: { engine, version, timestamp }
            raw_data_ref: string
            recency_score: float
            relevance_score: float
        }
    ]
    token_budget: {
        total_allowed: integer
        evidence_tokens: integer
        remaining: integer
    }
}
```

### ParsedInsight

```
ParsedInsight {
    title: string
    summary: string
    detailed_explanation: string
    confidence: float (0.0 - 1.0)
    severity: enum (critical, high, medium, low, info)
    evidence_references: UUID[]
    recommendations: [
        {
            action: string
            effort_estimate: string
            risk: enum (low, medium, high)
            confidence: float
        }
    ]
    validation: {
        status: enum (valid, partial, failed, fallback)
        issues: string[]
        evidence_coverage: float
    }
    reasoning_metadata: {
        model: string
        prompt_tokens: integer
        response_tokens: integer
        duration_ms: integer
    }
}
```

### FormattedInsight

```
FormattedInsight {
    id: UUID
    type: enum (risk, opportunity, change, prediction, decision)
    title: string
    summary: string (one paragraph)
    detailed_explanation: string (multi-section)
    confidence: float
    severity: enum
    evidence_chain: {
        insight: { id, title, confidence }
        supporting_evidence: [
            {
                evidence: { id, type, value, confidence }
                supports: string (explanation of how this evidence supports the insight)
                derived_from: [
                    { evidence_id, raw_data_ref, confidence }
                ]
            }
        ]
    }
    recommendations: Recommendation[]
    affected_entities: Entity[]
    created_at: timestamp
    expires_at: timestamp (optional)
    status: enum (active, acknowledged, resolved, dismissed)
    reasoning_metadata: { model, tokens, duration }
}
```

---

## Types of Reasoning

V1 supports five reasoning types:

### 1. Question Answering

The user asks a natural language question about their software system. The pipeline retrieves relevant evidence, synthesizes an answer, and presents it with supporting evidence chains.

**Examples:** "Why is PaymentService complex?", "Who owns the authentication module?", "What has changed in the last week?"

### 2. Decision Support

The pipeline evaluates engineering options by assembling evidence for each option and comparing them. The output includes pros, cons, effort estimates, confidence, and a recommendation.

**Examples:** "Should we refactor or rewrite PaymentService?", "Which dependency should we update first?"

### 3. Risk Evaluation

The system generates insights about emerging risks based on new evidence or scheduled re-evaluation. These insights are pushed to the user as alerts or appear in the Insights Feed.

**Examples:** "PaymentService complexity increased 15% this week. Trend is accelerating.", "Bus factor for AuthModule dropped to 1."

### 4. Explanation

The user drills into an existing insight to understand its evidence chain. This type of reasoning does not generate new insights — it retrieves and visualizes the existing evidence chain.

**Examples:** "Show me why you think PaymentService is a bottleneck.", "What evidence supports this risk score?"

### 5. Prediction

The pipeline extrapolates current trends to forecast future states. Predictions always include confidence intervals and are labeled as speculative beyond 6 months.

**Examples:** "When will PaymentService complexity reach 40?", "What will our velocity be in 3 months?"

---

## Confidence Model

The Reasoning Layer does not generate confidence from the LLM. Confidence is derived from the evidence:

### Per-Evidence Confidence

Each evidence node in the SCM carries a confidence level from its producing engine:
- **Certain (1.0):** Direct observation, no inference.
- **High (0.85–0.99):** Strong inference from multiple sources.
- **Medium (0.60–0.84):** Reasonable inference from limited data.
- **Low (0.30–0.59):** Weak inference, high uncertainty.
- **Speculative (0.0–0.29):** Hypothesis requiring validation.

See Phase 3, SCM Evidence Model for the full definition.

### Insight Confidence

An insight's confidence is computed from its supporting evidence:

```
insight_confidence = weighted_average(evidence_confidences) * evidence_coverage
```

Where `evidence_coverage` is the fraction of claims in the insight that have direct evidence support.

### Confidence Bounds

- Maximum confidence is bounded by the highest-confidence evidence in the chain.
- Minimum confidence is bounded by the lowest-confidence evidence in the chain.
- If evidence_coverage < 0.5, the insight is flagged as "low confidence" regardless of individual evidence scores.

### Confidence Display

- Insights with confidence < 0.5 are presented with an explicit caveat.
- Insights that fell back to deterministic mode are marked as "evidence summary" rather than "reasoned insight."
- All confidence scores in the UI are accompanied by an evidence count indicator.

---

## Evidence Chain Preservation

Every insight produced by the Reasoning Layer maintains a complete evidence chain:

```
Insight: "PaymentService is a maintenance bottleneck"
  ← SUPPORTED_BY [Evidence: "Complexity increased 133% in 6 months"]
    ← DERIVED_FROM [Evidence: "Cyclomatic complexity: 12 → 28"]
      ← DERIVED_FROM [Evidence: "AST analysis of PaymentService.java"]
        ← RAW_DATA [Commit abc123: "PaymentService.java source code"]
  ← SUPPORTED_BY [Evidence: "Bus factor = 1"]
    ← DERIVED_FROM [Evidence: "Author contribution: Alex 73%"]
      ← RAW_DATA [Git log: "Author statistics"]
  ← SUPPORTED_BY [Evidence: "Change frequency is 4x average"]
    ← DERIVED_FROM [Evidence: "Commit history analysis"]
      ← RAW_DATA [Git log: "Commits to PaymentService.java"]
```

The evidence chain is stored as a first-class structure in the SCM Reasoning Store (see Phase 3, SCM Evidence Model). The Reasoning Layer never discards intermediate evidence references. Every hop from insight to raw data is preserved and accessible.

### Chain Integrity Rules

1. **Every insight has at least one evidence chain.** No orphan insights.
2. **Every chain terminates at raw data.** No chains that end at another inference without a raw data leaf.
3. **Every hop is typed.** Relationships (SUPPORTED_BY, DERIVED_FROM) are explicit.
4. **Chains are acyclic.** No circular reasoning.
5. **Chain depth is unlimited** but minimum depth is two hops (insight → evidence → raw data).

---

## Edge Cases

### Insufficient Evidence

If the Context Assembler finds no evidence matching the user's question, the Reasoning Layer returns an "insufficient evidence" response rather than attempting to answer. The response includes suggestions for acquiring relevant evidence (e.g., "Analysis must include this module" or "Add X engine to the pipeline").

**Pipeline behavior:** Skips stages 3–5. Explanation Formatter generates a structured "insufficient evidence" message.

### Conflicting Evidence

If evidence sources contradict each other (e.g., complexity is high but stability is also high), the pipeline must surface both sides rather than hiding the conflict.

**Pipeline behavior:** The Context Assembler tags evidence sets with conflict markers. The prompt explicitly asks the LLM to address conflicting evidence. The response includes both interpretations with their respective confidences.

### Ambiguous Question

If the Intent Recognizer cannot confidently determine what the user is asking, it returns clarifying questions rather than guessing.

**Pipeline behavior:** The pipeline returns a set of possible interpretations with clarifying questions. No insight is generated until the user disambiguates.

### LLM Failure

If the local LLM fails (timeout, crash, model unavailable), the pipeline falls back to a deterministic insight.

**Pipeline behavior:** The Explanation Formatter receives a "fallback" signal from the Response Parser. It generates a structured evidence summary without LLM synthesis: a list of relevant evidence items with their source, confidence, and raw data links. This deterministic output is marked as "Evidence Summary (AI unavailable)" rather than "Reasoned Insight."

### Partial LLM Response

If the LLM responds but fails validation (hallucinated claim, missing fields, malformed output), the pipeline retries once with a stricter prompt. If validation fails again, the pipeline falls back to deterministic mode.

### Empty Recommendation

If the evidence supports a conclusion but does not support any specific recommendation, the insight presents the conclusion without a recommendation. The system never generates recommendations without evidence support.

---

## Performance Targets

Targets assume minimum hardware: 3B Q4 fallback model on CPU (see Phase 5/02 for full hardware benchmarks). GPU acceleration significantly improves all targets.

| Reasoning Type | Target Latency (CPU) | Target Latency (GPU) | Maximum | Notes |
|---|---|---|---|---|
| Question answering (simple) | < 10 sec | < 3 sec | < 15 sec | Evidence retrieval dominates |
| Question answering (complex) | < 20 sec | < 8 sec | < 30 sec | Cross-evidence synthesis |
| Decision support | < 25 sec | < 12 sec | < 35 sec | Multiple option evaluations |
| Risk evaluation | < 8 sec | < 4 sec | < 15 sec | Triggered by system, not user |
| Explanation drill-down | < 500 ms | < 500 ms | < 1 sec | No LLM, pure retrieval |
| Prediction | < 15 sec | < 8 sec | < 20 sec | Trend extrapolation + LLM |
| Deterministic fallback | < 1 sec | < 1 sec | < 2 sec | No LLM inference |

### Latency Budget (Complex Question, GPU)

| Stage | Budget | Description |
|---|---|---|
| Intent recognition | < 100 ms | Rule-based, no LLM |
| Context assembly | < 500 ms | SCM queries + ranking |
| Prompt construction | < 50 ms | Template selection + injection |
| LLM inference | < 6 sec | Model loading + generation (7B Q4 on RTX 3060) |
| Response parsing | < 200 ms | JSON extraction + validation |
| Explanation formatting | < 150 ms | Chain construction + formatting |
| **Total (GPU)** | **< 7 sec** | |
| **Total (CPU, 3B)** | **< 20 sec** | |

---

## Future Work

The following capabilities are deferred to V2+ and documented here to ensure V1 architecture does not preclude them:

### Multi-Turn Reasoning (V2)

The ability to maintain conversation context across multiple user questions, enabling follow-up questions that reference previous answers.

### Proactive Insight Generation (V2)

The system autonomously generates insights based on new evidence thresholds, without requiring a user question. These insights appear in the Insights Feed and alerts.

### Reinforcement from User Feedback (V2)

The system learns from user actions (dismiss, accept, override) to improve future reasoning quality by adjusting evidence weighting and recommendation calibration.

### Multi-Model Reasoning (V2)

Use different LLM sizes for different reasoning types (small fast model for simple questions, large model for complex synthesis). Model selection is driven by a complexity heuristic on the assembled context.

### Streaming Reasoning (V2)

Stream reasoning output to the UI as it is generated, showing intermediate conclusions and evidence references before the final insight is complete. This reduces perceived latency for complex questions.

### Causal Graph Reasoning (V3)

Move beyond correlation-based insight to explicit causal modeling, where the Reasoning Layer constructs causal graphs from evidence and reasons about intervention effects.

---

## The Reasoning Doctrine

> **The Cognitive Reasoning Layer is the interpreter between evidence and understanding. It does not invent. It does not guess. It reads what the engines discovered, selects what matters, synthesizes what is connected, and explains everything with evidence. Every insight it produces is a claim about the software system — and every claim is backed by a chain of evidence that anyone can verify. The reasoning layer is not the source of truth. The evidence is. The reasoning layer is the voice of that evidence.**
