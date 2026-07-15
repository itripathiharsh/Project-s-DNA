================================================================================
# 07 Logging
================================================================================

# Logging

## Purpose

Structured logging provides auditable records of system activity — who did what, when, and what happened. Logs are the primary debugging tool in local mode and a compliance requirement in team deployments.

---

## Log Format

All logs are structured JSON lines:

```jsonc
{
    "timestamp": "2026-07-14T10:00:00.000Z",
    "level": "INFO",
    "logger": "dna.reasoning",
    "message": "Reasoning pipeline completed",
    "request_id": "req_abc123",
    "duration_ms": 3400,
    "insight_id": "insight_synth_001",
    "evidence_count": 12,
    "model": "llama3.1:8b-q4_K_M"
}
```

## Log Levels

| Level | Usage |
|---|---|
| `ERROR` | Recoverable errors (LLM timeout, SCM query failure) |
| `WARNING` | Degraded behavior (slow query, retry attempted) |
| `INFO` | Normal operations (pipeline completed, insight created) |
| `DEBUG` | Detailed diagnostics (evidence filtered, token stream) |

## Log Sources

| Logger | Events Logged |
|---|---|
| `dna.api` | Request start/end, status code, duration |
| `dna.scm` | Query execution, evidence write, cache operations |
| `dna.engine` | Engine start/stop, evidence count, duration |
| `dna.reasoning` | Pipeline stage start/complete, LLM response |
| `dna.auth` | Login, logout, token validation, API key usage |
