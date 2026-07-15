================================================================================
# 02 LLM Architecture
================================================================================

# LLM Architecture

## Purpose

The Cognitive Reasoning Layer (Phase 5/01) uses a local LLM to synthesize evidence into human-readable insights. This document defines the architecture governing that LLM — model selection criteria, integration with Ollama, hardware requirements, quantization strategy, fallback behavior, and privacy guarantees. It ensures that the LLM serves the reasoning layer reliably without compromising the local-first, explainability, or evidence-first principles.

---

## Scope

### In Scope

- Model selection criteria for V1
- Primary and fallback model specifications
- Ollama integration architecture
- Quantization strategy
- Model lifecycle (download, cache, update)
- Hardware requirements (CPU, RAM, GPU)
- Context window management
- Error handling and recovery
- Privacy architecture for local inference
- Multi-model routing (V2 design sketch)

### Out of Scope

- Prompt template design (Phase 5/03)
- Context assembly and evidence ranking (Phase 5/04)
- Response parsing and validation (Phase 5/05, 5/08)
- Explanation formatting (Phase 5/06)
- Training or fine-tuning models
- Cloud-based LLM APIs (violates local-first)

---

## Background

Phase 2 (Technology Decisions, Decision 3) established Ollama as the primary local LLM runtime. The rationale was straightforward: Ollama provides the simplest way to run local models with a one-command install, manages model downloads and updates, and exposes a REST API compatible with the OpenAI format, making integration straightforward.

Phase 5/01 defined the Local LLM Interface component and placed it at the center of the reasoning pipeline:

```
Context Assembler → Prompt Orchestrator → Local LLM Interface → Response Parser
```

This document specifies what runs inside that component.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Local LLM Interface                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Model Router / Dispatcher                │   │
│  │  Determines which model to use based on task type,   │   │
│  │  context size, and hardware availability              │   │
│  └────────────┬────────────────────────────────────────┘   │
│               │                                             │
│  ┌────────────▼────────────┐  ┌────────────────────────┐   │
│  │  Primary Model (7B Q4)  │  │  Fallback Model (3B Q4)│   │
│  │  - Standard reasoning   │  │  - Simple questions     │   │
│  │  - Complex synthesis    │  │  - Degraded mode        │   │
│  │  - Decision support     │  │  - Low-resource hosts   │   │
│  └────────────┬────────────┘  └───────────┬────────────┘   │
│               │                             │               │
│  ┌────────────▼─────────────────────────────▼────────────┐  │
│  │              Ollama Client Adapter                     │  │
│  │  - REST API client (OpenAI-compatible)                 │  │
│  │  - Connection pooling                                  │  │
│  │  - Request/response handling                           │  │
│  │  - Streaming support                                   │  │
│  │  - Health checking                                     │  │
│  └────────────────────┬───────────────────────────────────┘  │
│                       │                                       │
│              ┌────────▼────────┐                              │
│              │  Ollama Process  │                              │
│              │  (system service)│                              │
│              │  - Model loading │                              │
│              │  - Inference     │                              │
│              │  - GPU offload   │                              │
│              └─────────────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

The Local LLM Interface communicates with Ollama over HTTP (default: localhost:11434). Ollama manages model persistence, GPU offloading, and inference. The Interface layer handles routing, error recovery, and adaptation.

---

## Model Selection Criteria

Models are evaluated against six criteria, ranked by priority:

| Priority | Criterion | Rationale |
|---|---|---|
| 1 | **Local-first compatibility** | Must run entirely on consumer hardware. No cloud dependency. |
| 2 | **Instruction following** | Must reliably produce structured output (JSON) from prompts with evidence context. |
| 3 | **Context window** | Must accommodate assembled evidence + instructions within available context. Target: 8K tokens minimum, 32K preferred. |
| 4 | **Reasoning quality** | Must accurately synthesize multiple evidence sources and identify causal relationships. |
| 5 | **Hallucination rate** | Must minimize fabricated claims. Evaluated against benchmark evidence sets. |
| 6 | **Inference speed** | Must meet latency targets from Phase 5/01: < 4 seconds for complex synthesis on target hardware. |

### V1 Model Selection

| Property | Primary Model | Fallback Model |
|---|---|---|
| **Family** | Llama 3.1 (or equivalent) | Llama 3.2 3B (or equivalent) |
| **Parameter count** | 7B – 8B | 3B |
| **Quantization** | Q4_K_M | Q4_K_M |
| **VRAM required** | ~6 GB | ~2.5 GB |
| **RAM required** | ~8 GB | ~4 GB |
| **Context window** | 8K – 32K tokens | 8K tokens |
| **Use cases** | Complex synthesis, decision support, prediction | Simple Q&A, fallback, low-resource mode |
| **Ollama tag** | `llama3.1:8b` (or equivalent) | `llama3.2:3b` (or equivalent) |

### Rationale

**7B–8B class models** represent the optimal balance of quality and resource requirements for V1. They fit on consumer hardware with GPU offloading (6 GB VRAM) or run entirely on CPU with acceptable performance (8 GB RAM). Larger models (13B+, 70B+) require hardware that cannot be assumed for a local-first tool targeting individual developers.

**3B class models** serve as a lightweight fallback. They run on minimal hardware (4 GB RAM, no GPU) and handle simple question-answering tasks. They are also used for intent recognition and preliminary classification where deep reasoning is not required.

**Q4_K_M quantization** preserves ~95% of model quality while reducing memory footprint by approximately 75% compared to FP16. This is the recommended default for V1. Users with sufficient hardware may opt for Q5_K_M or Q6_K for higher quality at the cost of more memory.

---

## Ollama Integration

### Client Adapter

The Local LLM Interface communicates with Ollama through an adapter that abstracts the HTTP API:

```
LLMInterface
    ↓
OllamaAdapter implements LLMInterface
    - base_url: string (default "http://localhost:11434")
    - default_model: string
    - timeout: Duration
    - max_retries: integer
```

### API Operations

| Operation | Endpoint | Purpose |
|---|---|---|
| `generate(prompt, model, options)` | `POST /api/generate` | Single-turn text generation |
| `chat(messages, model, options)` | `POST /api/chat` | Chat-style interaction (multi-turn future) |
| `embed(text, model)` | `POST /api/embed` | Embedding generation (future use) |
| `list_models()` | `GET /api/tags` | List available models |
| `pull_model(name)` | `POST /api/pull` | Download a model (user-initiated) |
| `delete_model(name)` | `DELETE /api/tags/:name` | Remove a model |
| `health()` | `GET /` | Check Ollama is running |

### Generation Options

Defaults for the primary model:

```
{
    "model": "llama3.1:8b-q4_K_M",
    "options": {
        "temperature": 0.2,        // Low temperature for deterministic reasoning
        "top_p": 0.9,
        "top_k": 40,
        "num_predict": 2048,       // Max output tokens
        "stop": ["<|end_of_turn|>"], // Model-specific stop tokens
        "num_ctx": 8192            // Context window size
    }
}
```

The low temperature (0.2) is deliberate. The LLM is not asked to be creative — it is asked to reason accurately about existing evidence. Higher temperatures (0.5–0.7) may be used for summarization or explanation rewrites, never for evidence analysis.

### Streaming

For complex questions where users expect progressive output, the adapter supports streaming via Ollama's streaming endpoint:

```
POST /api/generate
{
    "model": "llama3.1:8b-q4_K_M",
    "prompt": "...",
    "stream": true
}
Response: SSE stream of token deltas
```

The UI consumes the stream to show intermediate reasoning steps as they are generated.

---

## Model Lifecycle

### Download

Model downloading is always user-initiated, never automatic:

1. On first run, the system detects whether the required models are available via `GET /api/tags`.
2. If missing, the UI displays: "Project DNA requires a local AI model for reasoning. Download now? (3.8 GB)"
3. The user explicitly approves the download. A progress bar is shown.
4. Download proceeds via `POST /api/pull` with streaming progress.
5. On completion, the model is cached by Ollama and ready for inference.

The fallback model (3B) may be bundled with the installer for offline environments that cannot download models on demand.

### Caching

Ollama caches loaded models in memory. The LLM Interface keeps the primary model loaded after first inference to avoid cold-start latency on subsequent requests. If memory pressure is detected, the model is unloaded and reloaded on demand.

### Updates

Model updates are manual. Users are notified when a newer version of their model is available via Ollama's tag system. They choose when to pull the update.

### Custom Models

Users may configure custom models through settings. The interface validates that the custom model supports the required capabilities (instruction following, structured output) before allowing its use.

---

## Context Window Management

The LLM's context window bounds the amount of evidence that can be included in a single reasoning request.

### Token Budget Allocation

```
Total context window:    8192 tokens (primary model)
  - System instructions:   500 tokens  (6%)
  - Prompt template:       400 tokens  (5%)
  - Evidence context:      6000 tokens (73%)
  - Output budget:         692 tokens  (9%)
  - Safety margin:          600 tokens  (7%)
```

The safety margin accounts for tokenizer variance and model-specific special tokens. The Prompt Orchestrator (Phase 5/03) manages this budget with per-reasoning-type allocations.

If evidence exceeds the budget:

| Strategy | Behavior | When Used |
|---|---|---|
| **Truncation** | Remove lowest-ranked evidence | Default — used when ranking is reliable |
| **Aggregation** | Replace individual evidence with summary statistics | Used for large metric sets |
| **Chunking** | Split reasoning into multiple LLM calls | Used for cross-module comparisons |
| **Fallback to deterministic** | Skip LLM, produce evidence summary | Used when truncation loses critical evidence |

### Context Window Selection

| Model | Native Context | V1 Target | Rationale |
|---|---|---|---|
| 3B fallback | 8K | 4K | Limited context; simpler questions only |
| 7B–8B primary | 8K–32K | 8K | Balances quality and resource usage |
| 13B+ (optional) | 32K–128K | 32K+ | For complex cross-module analysis (V2) |

---

## Hardware Requirements

### Recommended Configuration

| Component | Minimum | Recommended | Optimal |
|---|---|---|---|
| CPU | 4 cores | 8 cores | 8+ cores |
| RAM | 8 GB | 16 GB | 32 GB |
| GPU (optional) | None | 6 GB VRAM | 8+ GB VRAM |
| Disk (models) | 4 GB free | 8 GB free | 16 GB free |
| Disk (SCM data) | 1 GB free | 5 GB free | 10 GB free |

### CPU-Only Mode

In CPU-only mode (no GPU), inference is approximately 3–5x slower than with GPU offloading. Mitigations:
- Use the fallback 3B model for simple questions to maintain responsiveness.
- Accept longer latency for complex synthesis (10–15 seconds instead of 3–5).
- Pre-warm the model on system startup.

### GPU Offloading

Ollama automatically detects and uses NVIDIA GPUs via CUDA. For AMD GPUs, ROCm support is available in recent Ollama versions. Apple Silicon (M-series) uses Metal acceleration.

| GPU | VRAM | Models Supported | Speed |
|---|---|---|---|
| None | 0 GB | 3B Q4, 7B Q4 (slow) | 10–30 tok/s (CPU) |
| Apple M1/M2 | Unified | 7B Q4, 13B Q5 | 20–40 tok/s |
| NVIDIA RTX 3060 | 12 GB | 7B Q4, 13B Q5, 7B FP16 | 40–60 tok/s |
| NVIDIA RTX 4090 | 24 GB | 13B Q4, 34B Q4 | 60–100 tok/s |
| A100 (not local-first) | 40 GB | All | > 100 tok/s |

---

## Multi-Model Routing (V2)

V1 uses a single primary model with a fallback. V2 introduces a model router that selects the optimal model per request:

```
Model Router
    │
    ├── Compute complexity heuristic from assembled context
    │     context_complexity = f(
    │         evidence_count,
    │         cross_engine_count,    // evidence from 2+ engines
    │         reasoning_type,        // simple QA vs. decision support
    │         context_tokens
    │     )
    │
    ├── If context_complexity < threshold:
    │     → Use 3B model (fast, low resource)
    │
    ├── If context_complexity > threshold:
    │     → Use 7B model (thorough synthesis)
    │
    └── If GPU available AND context_complexity > high_threshold:
          → Use 13B model (deep analysis)
```

The router is not implemented in V1. The architecture reserves the flexibility to add it without changing the interface.

---

## Error Handling and Recovery

| Error | Detection | Recovery |
|---|---|---|
| **Ollama not running** | Health check fails on startup and before every request | Display setup instructions: "Ollama is not running. Start it with: ollama serve" |
| **Model not found** | `POST /api/generate` returns 404 | Prompt user to download the model. Offer to download now. |
| **Out of memory** | Ollama returns error or process is killed | Fall back to smaller model. Advise user to close other applications. |
| **Inference timeout** | Request exceeds timeout (default 30s) | Retry once. If still fails, fall back to deterministic mode. |
| **Model hang** | No response for 60s | Kill request, reload model, retry once. Fall back to deterministic on second failure. |
| **GPU out of memory** | CUDA OOM error | Disable GPU offloading, retry on CPU. Offer persistent configuration change. |
| **Request rate limit** | N/A (single user) | No limit needed for V1. V2+ may need queuing. |

All errors are logged with model version, request size, and hardware state for debugging.

---

## Privacy Architecture

The LLM architecture must satisfy Phase -1 Principle 4 (Local-First, Privacy-First) and Phase 0 Privacy & Ethics:

### Data Never Leaves

- All inference happens locally. No code, evidence, or context is sent to any external API.
- The Ollama process runs on the same machine as Project DNA.
- Network activity is limited to:
  - Model downloads (user-initiated and explicitly approved).
  - Optional anonymous usage telemetry (opt-in, no code data).

### Model Integrity

- Only verified models from trusted sources (Ollama library, HuggingFace) are used.
- Model hash verification before first use.
- No fine-tuning on user code or evidence data.

### Isolation

- Ollama runs as a separate process, sandboxed from the file system (no access to source code directly).
- The LLM Interface passes only pre-processed, tokenized evidence — never raw source files.
- Evidence is stripped of identifying metadata where possible before prompt injection.

### Opt-In Model Download

The default installation ships without models. Users explicitly approve the download of each model. This ensures:
- No unexpected bandwidth usage.
- No data transfer without consent.
- Users with strict air-gap policies can bundle models manually.

---

## Performance Targets

### Inference Speed

| Model | Hardware | Tokens/sec | Time for 500-token response |
|---|---|---|---|
| 3B Q4 | CPU only | 15–25 tok/s | 20–33 seconds |
| 3B Q4 | Apple M1 | 30–50 tok/s | 10–16 seconds |
| 7B Q4 | CPU only | 5–10 tok/s | 50–100 seconds |
| 7B Q4 | Apple M1 | 20–35 tok/s | 14–25 seconds |
| 7B Q4 | RTX 3060 | 40–60 tok/s | 8–12 seconds |
| 7B Q4 | RTX 4090 | 60–100 tok/s | 5–8 seconds |

### Cold Start Latency

| Event | Latency | Mitigation |
|---|---|---|
| First inference after startup | 2–5 seconds (model load) | Pre-warm on idle |
| Model switch (primary → fallback) | 1–3 seconds | Keep both cached if memory permits |
| Model download (first time) | 2–15 minutes (3.8 GB) | Background download, progress notification |

### Target: End-to-End Latency

From Phase 5/01 (targets assume minimum hardware — CPU with 3B Q4; GPU significantly improves all targets):

| Reasoning Type | Target (CPU) | Target (GPU) | LLM Budget |
|---|---|---|---|
| Simple question | < 10 sec | < 3 sec | < 6 sec |
| Complex question | < 20 sec | < 8 sec | < 12 sec |
| Decision support | < 25 sec | < 12 sec | < 18 sec |
| Risk evaluation | < 8 sec | < 4 sec | < 5 sec |
| Prediction | < 15 sec | < 8 sec | < 10 sec |

---

## Edge Cases

### Insufficient Hardware

If the user's machine has less than 4 GB RAM, neither model can run. The system operates in deterministic-only mode: evidence summaries, no LLM synthesis. A clear message explains what hardware is needed for AI reasoning.

### Multiple Users (V2)

When multiple users access the same Project DNA instance, inference requests are queued. The queue is FIFO with a configurable concurrency limit (default: 1 concurrent inference). Long-running inferences show progress to users.

### Model Deprecation

When a model version is deprecated by Ollama (e.g., `llama3.1:8b` updated to `llama3.2:8b`), the user is notified and offered to migrate. The old model remains available until explicitly removed.

### Offline First Use

If the user installs Project DNA on a machine without internet access:
1. Deterministic mode only (no models available).
2. Documentation guides them to transfer model files via USB.
3. Alternatively, the fallback 3B model can be bundled in the installer.

---

## Future Work

### Bundled Small Model (V2)

Bundle the 3B fallback model with the Project DNA installer so that first-time users get basic AI reasoning without a download. The download prompt only appears for the primary 7B model.

### ROCm and Vulkan Support (V2)

As Ollama expands GPU support, the LLM Interface should auto-detect available backends (CUDA, ROCm, Metal, Vulkan) and configure accordingly.

### Speculative Decoding (V3)

Use a small draft model to generate candidate tokens, verified by the larger model. This can speed inference by 2–3x without quality loss. Requires Ollama support.

### Embedded Model Runtime (V4)

Replace the external Ollama dependency with an embedded runtime (llama.cpp bindings directly in the Project DNA process). This eliminates the separate Ollama process, reduces startup latency, and simplifies distribution.

---

## The LLM Architecture Doctrine

> **The LLM is not the source of understanding. The evidence is. The LLM is a reasoning engine that reads evidence and produces explanations — nothing more. It runs locally, respects privacy, and never generates facts it cannot trace to deterministic sources. It is chosen for reliability, not capability. It is deployed with fallbacks, not as a single point of failure. The architecture treats the LLM as a powerful but fallible component, carefully constrained by guardrails that ensure every output is grounded in evidence.**
