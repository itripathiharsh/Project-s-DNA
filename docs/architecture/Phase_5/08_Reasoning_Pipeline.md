================================================================================
# 08 Reasoning Pipeline
================================================================================

# Reasoning Pipeline

## Purpose

The Reasoning Pipeline orchestrates the six stages defined in Phase 5/01 — Intent Recognition, Context Assembly, Prompt Construction, LLM Inference, Response Parsing & Validation, and Explanation Formatting — into a unified, reliable execution flow. This document defines how stages connect, how errors propagate, how the pipeline is configured and monitored, and how it behaves under failure, load, and cancellation.

---

## Scope

### In Scope

- Pipeline orchestration model
- Stage execution and handoff contracts
- Request lifecycle (enter → process → exit)
- Pipeline configuration
- Error propagation and recovery across stages
- Pipeline state management
- Caching strategies across stages
- Pipeline metrics and monitoring
- Pipeline modes (interactive, batch, streaming)
- Cancellation and timeout per stage

### Out of Scope

- Individual stage internals (Phase 5/01–5/07)
- LLM model configuration (Phase 5/02)
- Prompt template design (Phase 5/03)
- Context building algorithms (Phase 5/04)
- Response parsing details (Phase 5/05)
- Explanation formatting (Phase 5/06)
- Memory or insight storage (Phase 5/07)

---

## Background

Phase 5/01 defined the six reasoning stages as a linear pipeline:

```
Query → Intent Recognition → Context Assembly → Prompt Construction
      → LLM Inference → Response Parsing & Validation → Explanation Formatting → Insight
```

Each stage was specified as an independent component with defined inputs and outputs. Phase 5/02 through 5/07 detailed the internal architecture of individual components.

This document defines how these components compose — the runtime that invokes them, the contracts that govern handoff, the policies for error handling, and the interfaces for monitoring and configuration.

---

## Architecture

```
                              ┌─────────────┐
                              │   Pipeline   │
                              │   Config     │
                              └──────┬──────┘
                                     │
┌────────────────────────────────────────────────────────────────────┐
│                      Pipeline Orchestrator                          │
│                                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐         │
│  │ Stage 1  │──▶│ Stage 2  │──▶│ Stage 3  │──▶│ Stage 4  │──┐      │
│  │ Intent   │   │ Context  │   │ Prompt   │   │ LLM      │  │      │
│  │ Recog.   │   │ Builder  │   │ Orches.  │   │ Infer.   │  │      │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘  │      │
│                                                               │      │
│                                         ┌─────────────────────┘      │
│                                         │                            │
│  ┌──────────┐   ┌──────────┐   ┌───────▼──────┐                     │
│  │ Stage 6  │◀──│ Stage 5  │◀──│ Stage 4 (cont)│                    │
│  │ Explain  │   │ Validate │   │ Parse Resp.  │                    │
│  │ Format   │   │ & Parse  │   │              │                    │
│  └──────────┘   └──────────┘   └──────────────┘                    │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                Pipeline Context (shared state)                │   │
│  │  - request_id, start_time, config, cache_refs, error_list    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### Pipeline Context

Every request creates a `PipelineContext` that flows through all stages:

```jsonc
{
    "request_id": "uuid",
    "mode": "interactive",          // interactive | batch | streaming
    "config": {
        "reasoning_type": "synthesis",
        "model_preference": "primary",
        "timeout_ms": 30000,
        "max_retries": 2,
        "fallback_on_timeout": true
    },
    "started_at": "2026-07-14T10:00:00.000Z",
    "stages": {
        "intent_recognition": { "status": "pending", "started_at": null, "duration_ms": null },
        "context_builder": { "status": "pending", "started_at": null, "duration_ms": null },
        "prompt_orchestrator": { "status": "pending", "started_at": null, "duration_ms": null },
        "llm_inference": { "status": "pending", "started_at": null, "duration_ms": null },
        "response_parser": { "status": "pending", "started_at": null, "duration_ms": null },
        "explanation_formatter": { "status": "pending", "started_at": null, "duration_ms": null }
    },
    "errors": [],
    "cache_hits": [],
    "result": null
}
```

---

## Stage Execution Model

### Sequential Execution

Stages execute in strict sequence. Each stage receives the `PipelineContext` and produces an output that is written back into the context for the next stage.

```
for each stage in [intent, context, prompt, llm, parse, explain]:
    context.stages[stage].status = "running"
    context.stages[stage].started_at = now()
    
    result = stage.execute(context)
    
    context.stages[stage].duration_ms = elapsed()
    context.stages[stage].status = "completed"
    context.stages[stage].output = result
    
    if context.has_errors():
        break
```

### Stage Contract

Every stage must implement:

```python
class PipelineStage(Protocol):
    def execute(context: PipelineContext) -> StageResult:
        # Process the context
        # Return StageResult with status + output or error
        ...

class StageResult:
    status: "ok" | "skipped" | "failed" | "partial"
    output: Any          # Stage-specific output
    error: ErrorInfo | None
    cache_key: str | None  # Cache key if output is cacheable
    cache_ttl: int | None   # Cache TTL in seconds
```

### Stage Handoff

Stage outputs are stored in the PipelineContext under the stage name, making them available to subsequent stages:

| Stage | Writes to Context | Read by |
|---|---|---|
| Intent Recognition | `context.parsed_intent` | Context Builder |
| Context Builder | `context.assembled_context` | Prompt Orchestrator |
| Prompt Orchestrator | `context.prompt_payload` | LLM Inference |
| LLM Inference | `context.llm_response` | Response Parser |
| Response Parser | `context.parsed_insight` | Explanation Formatter |
| Explanation Formatter | `context.formatted_insight` | Output |

---

## Pipeline Modes

### Interactive Mode (Default)

For user-facing queries where latency matters.

| Property | Value |
|---|---|
| Timeout | 30 seconds total |
| Stage timeout | 30s max per stage (LLM: 30s, others: 5s) |
| Streaming | Enabled (LLM tokens sent to UI in real time) |
| Retry | 1 retry on LLM failure |
| Caching | Read cache; write cache on completion |
| Error handling | Fail fast — return error to user immediately |

### Batch Mode

For background analysis, scheduled insights, and bulk processing.

| Property | Value |
|---|---|
| Timeout | 5 minutes total |
| Stage timeout | 5 min max per stage |
| Streaming | Disabled |
| Retry | 3 retries with exponential backoff |
| Caching | Read cache; always write cache |
| Error handling | Log and continue; partial results accepted |

### Streaming Mode

For real-time UI where the user sees intermediate output.

| Property | Value |
|---|---|
| Timeout | 60 seconds total |
| Stage timeout | 60s max per stage |
| Streaming | Enabled with token callbacks |
| Retry | No retry (streaming cannot replay) |
| Caching | Read cache for context/prompt; write on completion |
| Error handling | Send error event on stream, terminate |

---

## Error Propagation

### Stage-Level Errors

Each stage returns either success or failure. Failures include:

| Error Type | Cause | Recovery |
|---|---|---|
| `timeout` | Stage exceeded its time budget | Retry (if interactive/batch) or fail |
| `internal_error` | Unexpected exception in stage logic | Log, fail, escalate |
| `validation_error` | Stage output fails schema check | Retry once, then fail |
| `resource_exhausted` | OOM, disk full, GPU OOM | Fail, suggest deterministic fallback |
| `dependency_failure` | Upstream stage failed | Skip, propagate error |

### Error Propagation Rules

1. If a stage fails, subsequent stages are skipped.
2. The pipeline returns either a partial result (if some stages completed) or an error to the caller.
3. The `context.errors` array captures every error with stage name, error type, message, and timestamp.
4. In batch mode, failed stages are retried up to `config.max_retries` before failing.
5. In interactive mode, only the LLM inference stage is retried (once). Other stages fail fast.

### Deterministic Fallback

If the LLM inference stage fails (timeout, OOM, model unavailable) after all retries:

```
1. Response Parser receives fallback signal
2. Response Parser reads context.assembled_context.evidence
3. Produces a structured evidence summary (no AI synthesis)
4. Explanation Formatter formats the summary as:
   "AI reasoning is currently unavailable. Here is a summary of
    the evidence found for your query: [evidence list]"
5. Insight is returned with confidence = "UNAVAILABLE"
```

This ensures the tool is never completely unresponsive when the LLM is down.

---

## Caching

### Cache Layers

| Layer | Key | TTL | Invalidated By |
|---|---|---|---|
| **Intent cache** | `question_hash` | 1 hour | None (identical question = identical intent) |
| **Context cache** | `entity_ids_hash + time_range` | 30 minutes | New evidence for any entity in the set |
| **Prompt cache** | `template_id + context_hash` | 1 hour | Template update |
| **LLM response cache** | `prompt_hash` | 24 hours | None (same prompt = same response) |
| **Insight cache** | `request_id` | Until superseded | New insight for same query from batch |

### Cache Hit Behavior

```
Pipeline:
1. Intent Recognition: check intent cache → hit: skip, use cached
2. Context Builder: check context cache → hit: skip SCM query
3. Prompt Orchestrator: check prompt cache → hit: skip assembly
4. LLM Inference: check response cache → hit: skip inference
5-6: Always execute (parse + format have no cache)
```

Cache hits are logged in `context.cache_hits` for telemetry.

### Cache Invalidation

The pipeline subscribes to SCM change events. When new evidence is written for entities that are in the context cache, the corresponding cache entries are invalidated at the granularity of the entity set.

---

## Pipeline Configuration

### Configuration Schema

```jsonc
{
    "pipeline": {
        "mode": "interactive",              // interactive | batch | streaming
        "timeout_ms": 30000,
        "max_retries": 2,
        "fallback_on_error": true,
        "enable_caching": true,
        "stream_tokens": true               // Send LLM tokens as they are generated
    },
    "stages": {
        "intent_recognition": {
            "enabled": true,
            "timeout_ms": 5000,
            "model": "fallback"              // 3B model for lightweight classification
        },
        "context_builder": {
            "enabled": true,
            "timeout_ms": 5000,
            "max_evidence_items": 200,
            "max_entities": 20,
            "decay_period_hours": 720
        },
        "prompt_orchestrator": {
            "enabled": true,
            "timeout_ms": 2000,
            "template_version": "latest"
        },
        "llm_inference": {
            "enabled": true,
            "timeout_ms": 30000,
            "model": "primary",
            "temperature": 0.2,
            "max_tokens": 2048
        },
        "response_parser": {
            "enabled": true,
            "timeout_ms": 5000,
            "strict_validation": true
        },
        "explanation_formatter": {
            "enabled": true,
            "timeout_ms": 2000,
            "format": "markdown"
        }
    }
}
```

### Configuration Profiles

| Profile | Mode | Caching | Retries | Use Case |
|---|---|---|---|---|
| `default` | interactive | On | 2 | Standard user queries |
| `realtime` | streaming | Read only | 0 | Live monitoring dashboard |
| `scheduled` | batch | Full | 3 | Nightly automated insights |
| `degraded` | interactive | Off | 0 | When LLM is unavailable |
| `minimal` | interactive | Off | 0 | Memory-constrained environments |

---

## Pipeline Metrics

### Per-Request Metrics

Recorded in `context.stages[*]` and exported to telemetry:

| Metric | Description |
|---|---|
| `duration_ms` | Wall-clock time for the stage |
| `cpu_ms` | CPU time consumed |
| `tokens_in` | Input tokens (for LLM stage) |
| `tokens_out` | Output tokens (for LLM stage) |
| `cache_hit` | Boolean — was stage output served from cache |
| `retry_count` | Number of retries attempted |
| `evidence_count` | Items in assembled context |
| `error_count` | Errors encountered in the stage |

### Pipeline-Level Metrics

| Metric | Aggregation | Source |
|---|---|---|
| `pipeline.success_rate` | Rolling 24h | Ratio of completed vs. started pipelines |
| `pipeline.p50_latency` | Rolling 24h | Median end-to-end latency |
| `pipeline.p95_latency` | Rolling 24h | 95th percentile latency |
| `pipeline.cache_hit_rate` | Rolling 24h | Ratio of cache hits across all layers |
| `pipeline.fallback_rate` | Rolling 24h | Ratio of requests using deterministic fallback |
| `pipeline.stage_breakdown` | Rolling 24h | Average duration per stage as % of total |

---

## Cancellation and Timeout

### Cancellation

The pipeline supports cancellation at every stage boundary:

```
1. Cancel signal received
2. If a stage is running:
   a. Send cancellation token to the stage
   b. Stage stops processing, marks status as "cancelled"
3. All subsequent stages are skipped
4. Pipeline returns partial result if any stage completed
```

Cancellation is triggered by:
- User closing the query UI
- A new query superseding the current one
- System shutdown
- Parent process termination (SIGTERM)

### Per-Stage Timeout

Each stage has an independent timeout (configured in `config.stages[*].timeout_ms`):

```
If stage.duration_ms > stage.timeout_ms:
    stage.status = "timeout"
    context.errors.append({ stage: stage_name, error: "timeout", ... })
    If config.pipeline.fallback_on_error:
        Initiate deterministic fallback
    Else:
        Fail pipeline
```

### Total Pipeline Timeout

The pipeline also enforces a total timeout (`config.pipeline.timeout_ms`). If the total elapsed time exceeds this limit, the currently executing stage is cancelled and the pipeline returns a timeout error with any partial results available.

---

## Edge Cases

### All Evidence Filtered Out

If the Context Builder produces zero evidence items (but entities matched):

```
Pipeline proceeds to LLM with prompt indicating no evidence.
Phase 5/03 Prompt Orchestrator handles "empty evidence" case.
LLM returns: "No evidence available for this query."
Phase 5/05 validates that the response correctly states insufficient evidence.
Pipeline completes normally with confidence = "INSUFFICIENT_EVIDENCE".
```

### LLM Returns Malformed JSON

```
Stage 4 (LLM Inference): Response is valid but not JSON
Stage 5 (Response Parser): JSON parse fails:
    1. Attempt repair (Phase 5/05 handles repair logic)
    2. If repair fails: retry LLM (in interactive mode)
    3. If retry also fails: fallback to deterministic
Stage 6 (Explanation Formatter): Formats the deterministic summary
Pipeline completes with confidence = "FALLBACK"
```

### Cascade of Failures

If three stages fail (e.g., Intent Recognition → internal error, Context Builder → timeout, Prompt Orchestrator → skipped):

```
context.stages.intent_recognition.status = "failed"
context.stages.context_builder.status = "skipped"
context.stages.prompt_orchestrator.status = "skipped"
context.stages.llm_inference.status = "skipped"
context.stages.response_parser.status = "skipped"
context.stages.explanation_formatter.status = "skipped"

Pipeline returns: {
    status: "failed",
    errors: [
        { stage: "intent_recognition", error: "internal_error", message: "...", ... },
        { stage: "context_builder", error: "dependency_failure", message: "Skipped due to upstream failure", ... }
    ],
    partial_result: null
}
```

### Pipeline Called with Invalid Configuration

If the pipeline is initialized with invalid config (e.g., `mode: "unknown"`, invalid timeout value):

```
Pipeline validates config at startup:
    1. Check mode is one of [interactive, batch, streaming]
    2. Check timeouts are positive integers
    3. Check stage names match registered stages
    4. If validation fails: return configuration error immediately
    5. No stages execute
```

### Concurrent Requests

For multiple simultaneous pipeline invocations (V2):

| Scenario | Behavior |
|---|---|
| Same user, different queries | Parallel — each gets its own PipelineContext |
| Same user, same query | Return cached result if still valid; otherwise parallel |
| LLM concurrency | Ollama handles 1 concurrent inference by default; queue additional requests |
| SCM concurrency | SCM queries are non-blocking; multiple Context Builders can query simultaneously |

---

## Future Work

### Parallel Stage Execution (V2)

Some stages have no data dependency and could run in parallel:

- **Context Building** and **Memory Retrieval** (Phase 5/07) can run simultaneously.
- **Response Parsing** and **Confidence Calculation** (Phase 5/05) can run simultaneously.
- The pipeline orchestrator would use a DAG instead of a linear sequence.

### Adaptive Stage Timeouts (V3)

Adjust per-stage timeouts dynamically based on historical latency data:

```
If stage.avg_duration > stage.timeout_ms * 0.8 over last 100 requests:
    Increase stage.timeout_ms by 20%
```

### Pipeline as Graph (V4)

Replace the linear pipeline with a directed acyclic graph (DAG) where stages can be added, removed, or reordered dynamically through configuration. This enables:
- Custom pipelines for different use cases (security audit, performance review, onboarding)
- Plugin-based stages from third parties
- A/B testing different stage implementations

---

## The Reasoning Pipeline Doctrine

> **The pipeline is not a sequence of libraries — it is a contract. Each stage has one job, one input, one output, and one failure mode. Stages do not reach into each other's internals. The PipelineContext is the only shared state, and it is read-only except for the owning stage's output slot. The pipeline is linear because reasoning is linear: understand the question, gather the facts, construct the inquiry, perform inference, validate the result, format the answer. Every stage is timed, cached, and monitored. Every failure has a fallback. The pipeline never leaves the user without an answer — even if that answer is "I don't know, and here is why."**
