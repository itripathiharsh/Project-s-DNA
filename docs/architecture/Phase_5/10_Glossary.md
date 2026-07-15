================================================================================
# 10 Glossary
================================================================================

# Glossary

## Purpose

This glossary defines every key term introduced or refined across the Phase 5 documentation, with cross-references to earlier phases and to related Phase 5 terms. It ensures consistent vocabulary across the Reasoning Layer specification and serves as a quick reference for implementors.

---

## A

### AssembledContext

The output of the Context Builder (Phase 5/04). A structured bundle containing query intent, resolved entities, ranked evidence nodes, aggregate statistics, detected conflicts, token budget metadata, and (when memory is active) past insights. This is the input to the Prompt Orchestrator.

*See also:* Context Builder, Prompt Orchestrator, Evidence Node.

---

## C

### Cognitive Reasoning Layer

The sixth architectural layer of Project DNA (Phase 2, Phase 5/01). Composed of six pipeline stages: Intent Recognition, Context Builder, Prompt Orchestrator, LLM Inference, Response Parser & Validator, and Explanation Formatter. Responsible for synthesizing deterministic engine evidence into human-readable insights via a local LLM.

*See also:* Pipeline, Reasoning Type.

### Confidence

A float 0.0–1.0 representing the reliability of a reasoning output, derived from the weighted average of supporting evidence confidences, multiplied by coverage, consistency, and recency factors. Never read from the LLM output. Mapped to display levels: HIGH (0.80+), MEDIUM (0.50–0.79), LOW (0.00–0.49), plus special levels INSUFFICIENT_EVIDENCE and UNAVAILABLE.

*See:* Phase 5/05.
*See also:* Evidence Confidence, Coverage, Consistency Penalty, Recency Factor.

### Consistency Penalty

A multiplicative factor (0.50–1.00) applied to insight confidence when evidence sources conflict. Depends on conflict severity (LOW: 0.10 penalty, MEDIUM: 0.25, HIGH: 0.50) and the ratio of conflicting evidence pairs.

*See:* Phase 5/05.
*See also:* Confidence.

### Context Builder

The second stage of the reasoning pipeline (Phase 5/04). Receives structured query intent, resolves entity names to SCM IDs, queries the SCM for evidence, ranks and filters by relevance and recency, detects conflicts, estimates token budgets, and produces AssembledContext. Known as "Context Assembler" in Phase 5/01.

*See also:* AssembledContext, Entity Resolution, Reasoning Pipeline.

### Coverage

The fraction of claims in an LLM-generated insight that are directly supported by evidence in the assembled context. Used as a multiplicative factor in confidence computation. If coverage < 0.5, the insight is forced to LOW confidence regardless of other factors.

*See:* Phase 5/05.
*See also:* Confidence, Response Parser.

---

## D

### Deterministic Fallback

A pipeline mode triggered when the LLM cannot be used (Ollama unavailable, model missing, timeout after retries) or when the LLM response fails validation (coverage < 0.3, parse failure, hallucination detected). Produces a structured evidence summary without AI synthesis, clearly marked as "AI unavailable" or "validation failed."

*See:* Phase 5/01 (Principle 2), Phase 5/08.
*See also:* Evidence Summary, Pipeline.

---

## E

### Entity Resolution

The process in the Context Builder of mapping natural-language entity names from the user's question to SCM entity IDs. Uses exact match, fuzzy match, and prefix match. Returns disambiguation data when multiple entities match.

*See:* Phase 5/04.
*See also:* Context Builder.

### Evidence Chain

A directed acyclic graph from a FormattedInsight through its supporting EvidenceNodes to the raw data each node is derived from. Every insight preserves a complete evidence chain. The chain is a first-class output, never discarded or obscured.

*See:* Phase 5/01 (Principle 5), Phase 5/06.
*See also:* Evidence Node, FormattedInsight.

### Evidence Confidence (Per-Node)

A float 0.0–1.0 assigned by the producing Cognitive Engine to each EvidenceNode. Levels: Certain (1.0), High (0.85–0.99), Medium (0.60–0.84), Low (0.30–0.59), Speculative (0.00–0.29). The Reasoning Layer inherits these values and never modifies them.

*See:* Phase 4, Phase 5/05.
*See also:* Evidence Node, Confidence.

### Evidence Node

A structured record produced by a Cognitive Engine (Phase 4). Contains: id, type, category, value, confidence, source (engine, version, timestamp), raw_data_ref, and affected_entities. Stored in the SCM Perception Store. The fundamental unit of evidence consumed by the Reasoning Layer.

*See also:* Evidence Chain, AssembledContext, Software Cognition Model.

### Evidence Summary

The output format used in deterministic fallback mode. A flat list of evidence items relevant to the user's query, without LLM synthesis. Marked as "Evidence Summary (AI unavailable)" or "Evidence Summary (validation failed)" to distinguish it from a full reasoned insight.

*See:* Phase 5/01, Phase 5/06, Phase 5/09 (Example 7).
*See also:* Deterministic Fallback.

### Explanation Formatter

The sixth stage of the reasoning pipeline (Phase 5/06). Transforms a ParsedInsight into a FormattedInsight by building the evidence chain, assigning severity, formatting the multi-layer explanation (summary → detail → drill-down), formatting recommendations, writing to the SCM Reasoning Store, and passing to the Insight Validator.

*See also:* FormattedInsight, ParsedInsight, Insight Validator, Reasoning Pipeline.

---

## F

### Fallback Model

A 3B-parameter quantized (Q4_K_M) local LLM used for simple question-answering tasks and as a degraded-mode fallback when the primary model is unavailable or the host hardware is resource-constrained. Requires ~2.5 GB VRAM or ~4 GB RAM.

*See:* Phase 5/02.
*See also:* Primary Model, Model Quantization.

### FormattedInsight

The output of the Explanation Formatter. A structured insight object with id, type, title, summary, detailed_explanation, confidence, severity, evidence_chain (with full traceability from insight → evidence → raw data), recommendations, and reasoning_metadata. Ready for SCM storage, API delivery, and UI rendering.

*See:* Phase 5/01, Phase 5/06.
*See also:* ParsedInsight, Explanation Formatter, Evidence Chain.

---

## I

### Insight Validator

A quality assurance component that runs after the Explanation Formatter (Phase 5/01). Checks each FormattedInsight for consistency with existing active insights, completeness of fields, freshness of evidence, and redundancy with existing insights. Produces a ValidationReport.

*See also:* Explanation Formatter, FormattedInsight.

### Intent Recognition

The first stage of the reasoning pipeline. Parses user questions or system triggers into structured query intent: type (question, decision, alert, exploration), entities, time constraints, and reasoning type. Uses the fallback 3B model or deterministic NLP.

*See:* Phase 5/01.
*See also:* Reasoning Pipeline, Query Intent.

---

## L

### Local LLM Interface

The fourth stage of the reasoning pipeline (Phase 5/02). Communicates with Ollama over HTTP. Handles model routing (primary vs. fallback), request/response, streaming, health checking, timeouts, and retries. Receives a structured prompt payload from the Prompt Orchestrator and returns raw LLM response text.

*See also:* Ollama, Primary Model, Fallback Model, Prompt Payload.

---

## M

### Memory Recall

The process in the Context Builder (Phase 5/07) of querying the SCM Reasoning Store for past insights relevant to the current query's entities. Past insights are injected into the AssembledContext as PAST_INSIGHT evidence type, subject to the same token budget and ranking as engine evidence.

*See:* Phase 5/07.
*See also:* Context Builder, Reasoning Store, AssembledContext.

### Model Quantization

The technique of reducing LLM parameter precision to reduce memory footprint and increase inference speed. Project DNA uses Q4_K_M as the default quantization level, which preserves ~95% of model quality while reducing memory by ~75% compared to FP16.

*See:* Phase 5/02.
*See also:* Primary Model, Fallback Model.

### Multi-Layer Explanation

The three-tier explanation structure produced by the Explanation Formatter (Phase 5/06):
- **Layer 1 (Summary):** 280-character paragraph with core answer, confidence, and evidence count.
- **Layer 2 (Detail):** Multi-section body with key findings, evidence overview, and type-specific sections.
- **Layer 3 (Drill-Down):** Expandable evidence chain with per-node detail and raw data references.

*See:* Phase 5/06.

---

## O

### Ollama

The local LLM runtime chosen in Phase 2 (Decision 3) for running inference on consumer hardware. Manages model downloads, caching, GPU offloading, and exposes an OpenAI-compatible REST API on localhost:11434. The sole LLM backend for V1.

*See:* Phase 5/02.
*See also:* Local LLM Interface, Primary Model, Fallback Model.

---

## P

### ParsedInsight

The output of the Response Parser. A structured insight with validated fields: title, summary, detailed_explanation, confidence (float), severity, evidence_references (UUIDs), recommendations (with effort, risk, confidence), validation status, and reasoning_metadata. This is the input to the Explanation Formatter.

*See:* Phase 5/01.
*See also:* Response Parser, FormattedInsight, Explanation Formatter.

### Pipeline (Reasoning Pipeline)

The orchestration runtime that executes the six reasoning stages in sequence (Phase 5/08). Manages PipelineContext (shared state per request), stage timeouts, retries, caching, error propagation, deterministic fallback, and configuration. Supports three modes: interactive, batch, and streaming.

*See:* Phase 5/08.
*See also:* The six individual stages: Intent Recognition, Context Builder, Prompt Orchestrator, Local LLM Interface, Response Parser, Explanation Formatter.

### Primary Model

A 7B–8B parameter quantized (Q4_K_M) local LLM used as the default reasoning engine for all standard inference tasks. Requires ~6 GB VRAM or ~8 GB RAM. Default: Llama 3.1 8B (or equivalent). Context window: 8192 tokens for V1.

*See:* Phase 5/02.
*See also:* Fallback Model, Model Quantization, Generation Options.

### Prompt Orchestrator

The third stage of the reasoning pipeline (Phase 5/03). Selects a prompt template based on reasoning type, injects evidence from AssembledContext, sets structured output schema, enforces token budget, and produces a PromptPayload for the Local LLM Interface.

*See:* Phase 5/03.
*See also:* AssembledContext, Prompt Payload, Template Registry, Token Budget.

### Prompt Payload

The output of the Prompt Orchestrator. Contains: system instructions, user message with evidence, output JSON schema, generation options (temperature 0.2, max_tokens, stop sequences), and metadata (template_id, evidence_count, total_tokens). Passed to the Local LLM Interface.

*See:* Phase 5/03.
*See also:* Prompt Orchestrator, Local LLM Interface.

---

## Q

### Query Intent

The output of Intent Recognition. A structured object containing: type (question, decision, alert, exploration), original question string, resolved entity references, time range, and reasoning type (simple_qa, synthesis, decision_support, risk_evaluation, prediction).

*See:* Phase 5/01.
*See also:* Intent Recognition, Reasoning Type, Context Builder.

---

## R

### Reasoning Store

Pillar 3 of the Software Cognition Model (Phase 3). Stores insights, predictions, recommendations, decisions, and their supporting evidence chains. Provides query operations for memory recall. Insights have lifecycle states: Created, Active, Acknowledged, Resolved, Dismissed, Archived.

*See:* Phase 3, Phase 5/07.
*See also:* Memory Recall, Insight Lifecycle, SCM.

### Reasoning Type

The classification of a reasoning request that determines which prompt template, evidence filters, and output schema are used. V1 defines five types: simple_qa, synthesis, decision_support, risk_evaluation, prediction.

*See:* Phase 5/01, Phase 5/03.
*See also:* Query Intent, Prompt Orchestrator.

### Recency Factor

A multiplicative factor (0.70–1.00) applied to insight confidence when some evidence is stale relative to the question's time sensitivity. Computed as `1.0 - stale_ratio × stale_penalty`. Penalty increases with staleness duration.

*See:* Phase 5/05.
*See also:* Confidence, Context Builder.

### Response Parser

The fifth stage of the reasoning pipeline (Phase 5/05). Receives raw LLM response text, parses JSON, validates each claim against the AssembledContext, computes confidence (weighted average × coverage × consistency × recency), detects unsupported claims, and either returns a ParsedInsight or triggers deterministic fallback.

*See:* Phase 5/01, Phase 5/05.
*See also:* ParsedInsight, Confidence, Deterministic Fallback.

---

## S

### SCM (Software Cognition Model)

The unified data model of Project DNA (Phase 3). Four pillars: Perception Store (raw engine evidence), Representation Store (entities and relationships), Reasoning Store (insights and memory), Temporal Store (history and trends). The single source of truth for all understanding. The Reasoning Layer reads evidence from and writes insights to the SCM.

*See:* Phase 3.
*See also:* Reasoning Store, Evidence Node, AssembledContext.

### Severity

A qualitative level (CRITICAL, HIGH, MEDIUM, LOW, INFO) assigned to each FormattedInsight by the Explanation Formatter. Computed from the maximum evidence severity in the chain, discounted by confidence penalty. Communicates the importance and urgency of the insight.

*See:* Phase 5/06.
*See also:* Explanation Formatter, FormattedInsight.

### Streaming

A mode of LLM inference where tokens are sent to the UI as they are generated, rather than waiting for the complete response. Used in interactive and streaming pipeline modes. Implemented via Ollama's SSE streaming endpoint.

*See:* Phase 5/02, Phase 5/08.
*See also:* Local LLM Interface, Pipeline.

---

## T

### Template Registry

A file-based registry of prompt templates loaded by the Prompt Orchestrator at startup. Contains templates for each reasoning type (simple_qa_v1, synthesis_v1, decision_support_v1, risk_evaluation_v1, prediction_v1) and explanation format. Templates are versioned (v1, v2, ...).

*See:* Phase 5/03, Phase 5/06.
*See also:* Prompt Orchestrator, Explanation Formatter.

### Token Budget

The allocation of the LLM's context window across system instructions, template, evidence, and output. For the primary model (8192 total): system 500, template 1000, evidence 6000, output 692. The Context Builder and Prompt Orchestrator jointly enforce the budget: the Builder tags truncation candidates, the Orchestrator performs actual truncation.

*See:* Phase 5/02, Phase 5/03, Phase 5/04.
*See also:* Context Builder, Prompt Orchestrator.
