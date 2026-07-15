================================================================================
# 06 Monitoring
================================================================================

# Monitoring

## Purpose

Monitoring provides visibility into the health, performance, and behavior of a running Project DNA instance. In local mode, monitoring is minimal (log-based). In team deployments (V2+), structured metrics and health endpoints enable proactive operations.

---

## Health Endpoint

```
GET /health
```

```jsonc
{
    "status": "healthy",          // healthy | degraded | unhealthy
    "version": "1.0.0",
    "uptime_seconds": 86400,
    "services": {
        "scm_storage": { "status": "healthy", "latency_ms": 2 },
        "ollama": { "status": "healthy", "model": "llama3.1:8b", "latency_ms": 45 },
        "reasoning": { "status": "healthy" },
        "api_gateway": { "status": "healthy", "requests_total": 15420 }
    }
}
```

## Metrics Endpoint

```
GET /metrics  → Prometheus format
```

Key metrics:

| Metric | Type | Labels |
|---|---|---|
| `dna_evidence_total` | Gauge | engine, status |
| `dna_insights_total` | Counter | type, severity, status |
| `dna_analysis_duration_seconds` | Histogram | engine |
| `dna_reasoning_duration_seconds` | Histogram | reasoning_type |
| `dna_llm_tokens_per_second` | Gauge | model |
| `dna_api_request_duration_seconds` | Histogram | method, path, status_code |
| `dna_api_requests_total` | Counter | method, path, status_code |
| `dna_scm_query_duration_seconds` | Histogram | query_type |

## Alerting (V2+)

| Alert | Condition | Severity |
|---|---|---|
| High LLM latency | p95 reasoning > 10s | WARNING |
| SCM storage full | Disk usage > 90% | CRITICAL |
| Ollama down | Health check fails > 3 consecutive | CRITICAL |
| High error rate | API 5xx rate > 1% | WARNING |
| Engine failure | Engine run fails > 3 consecutive | WARNING |
