================================================================================
# 02 REST API
================================================================================

# REST API

## Purpose

The REST API is the primary synchronous interface to Project DNA. It exposes entities, evidence, insights, reasoning, and analysis management through resource-oriented HTTP endpoints. This document defines every endpoint — its path, method, request format, response schema, status codes, pagination, filtering, and error behavior.

---

## Scope

### In Scope

- All REST endpoints for V1
- Request and response schemas
- Path and query parameter conventions
- Pagination, filtering, sorting conventions
- HTTP status code usage
- Content negotiation
- Endpoint grouping by resource

### Out of Scope

- Authentication and authorization (Phase 6/05, 6/06)
- Error response format details (Phase 6/07)
- API versioning strategy (Phase 6/08)
- WebSocket events (Phase 6/04)
- GraphQL schema (Phase 6/03)
- Implementation code

---

## Background

Phase 6/01 defined the API layer architecture: REST for synchronous operations, WebSocket for real-time, GraphQL (V2) for flexible queries. REST is the default and most complete API surface.

Phase 2 identified FastAPI as the technology choice for the API Gateway, with auto-generated OpenAPI documentation.

Phase 3 defined the SCM data model: entities, evidence nodes, insights, relationships. Phase 5 defined the reasoning pipeline and its input/output interfaces.

---

## Conventions

### Base URL

All endpoints are prefixed with the API version:

```
http://localhost:8000/v1/
```

In local mode (V1 default), the server binds to `127.0.0.1:8000`. In network mode (V2+), the host and port are configurable.

### HTTP Methods

| Method | Semantics |
|---|---|
| `GET` | Retrieve a resource or collection |
| `POST` | Create a resource or invoke an action |
| `PUT` | Full replacement of a resource |
| `PATCH` | Partial update of a resource |
| `DELETE` | Remove a resource |

### Content Type

- Request: `application/json`
- Response: `application/json`
- Streaming response: `text/event-stream` (for LLM token streams)

### Status Codes

| Code | Usage |
|---|---|
| `200 OK` | Successful retrieval, update, or action |
| `201 Created` | Successful resource creation |
| `202 Accepted` | Async operation started (returns job_id) |
| `204 No Content` | Successful deletion |
| `400 Bad Request` | Invalid request body or parameters |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Authenticated but not authorized |
| `404 Not Found` | Resource does not exist |
| `409 Conflict` | Resource state conflict |
| `422 Unprocessable Entity` | Schema validation failure |
| `429 Too Many Requests` | Rate limit exceeded (V2) |
| `500 Internal Server Error` | Unexpected server failure |
| `503 Service Unavailable` | Dependency unavailable (e.g., Ollama down) |

### Pagination

List endpoints return paginated results:

```
GET /v1/entities?page=2&per_page=20
```

Response:

```jsonc
{
    "data": [...],
    "pagination": {
        "page": 2,
        "per_page": 20,
        "total": 147,
        "total_pages": 8,
        "next": "/v1/entities?page=3&per_page=20",
        "prev": "/v1/entities?page=1&per_page=20"
    }
}
```

**Defaults:** `page=1`, `per_page=20`. Max `per_page`: 100.

### Filtering

Query parameters for collection endpoints:

| Operator | Example | Behavior |
|---|---|---|
| Exact match | `?type=module` | Equals |
| Multiple values | `?type=module,function` | IN clause |
| Range | `?confidence=0.5..1.0` | Between |
| Minimum | `?confidence=0.5..` | Greater than or equal |
| Maximum | `?confidence=..0.5` | Less than or equal |
| Full-text | `?q=auth+validation` | Text search (SCM search index) |
| Time range | `?created_at=2026-07-01..2026-07-14` | ISO 8601 date range |

### Sorting

```
GET /v1/insights?sort=-confidence
```

Prefix with `-` for descending order. Default sort is `-created_at` (most recent first). Multi-sort: `?sort=-severity,confidence`.

---

## Entity Endpoints

### List Entities

```
GET /v1/entities
```

| Parameter | Type | Description |
|---|---|---|
| `type` | string | Filter by entity type (module, function, class, file, etc.) |
| `q` | string | Full-text search on entity name |
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Items per page (default: 20, max: 100) |

**Response:** Paginated list of entity summaries.

```jsonc
{
    "data": [
        {
            "id": "mod_auth_001",
            "name": "src/auth",
            "type": "module",
            "aliases": ["auth", "authentication"],
            "evidence_count": 47,
            "insight_count": 12,
            "last_analyzed": "2026-07-14T10:00:00Z"
        }
    ],
    "pagination": { "page": 1, "per_page": 20, "total": 147, "total_pages": 8 }
}
```

### Get Entity

```
GET /v1/entities/{id}
```

**Response:**

```jsonc
{
    "id": "mod_auth_001",
    "name": "src/auth",
    "type": "module",
    "aliases": ["auth"],
    "path": "src/auth",
    "evidence_count": 47,
    "insight_count": 12,
    "relationships": {
        "parents": [{ "id": "repo_001", "name": "payment-system", "type": "repository" }],
        "children": [
            { "id": "file_auth_001", "name": "validate.ts", "type": "file" },
            { "id": "file_auth_002", "name": "provider.ts", "type": "file" }
        ],
        "dependencies": [{ "id": "dep_lodash_001", "name": "lodash", "type": "package" }]
    },
    "metadata": {
        "created_at": "2026-01-15T08:00:00Z",
        "last_analyzed": "2026-07-14T10:00:00Z"
    }
}
```

---

## Evidence Endpoints

### List Evidence

```
GET /v1/evidence
```

| Parameter | Type | Description |
|---|---|---|
| `entity_id` | string | Filter by affected entity |
| `engine` | string | Filter by producing engine |
| `type` | string | Filter by evidence type |
| `severity` | string | Filter by severity (low, medium, high, critical) |
| `confidence` | string | Range filter (e.g., `0.5..1.0`) |
| `created_at` | string | Time range filter |
| `q` | string | Full-text search on evidence value |
| `sort` | string | Sort field (default: `-created_at`) |
| `page`, `per_page` | pagination | Standard pagination |

**Response:** Paginated list of evidence nodes.

```jsonc
{
    "data": [
        {
            "id": "trace_001",
            "type": "FUNCTION_CALL",
            "engine": "trace_cognition",
            "severity": "LOW",
            "confidence": 0.95,
            "value": "validateToken() called 847 times, 312 returning errors (36.8%)",
            "timestamp": "2026-07-14T10:23:00Z",
            "source": "src/auth/validate.ts:42",
            "entity_id": "func_auth_validatetoken_001"
        }
    ],
    "pagination": { "page": 1, "per_page": 20, "total": 47, "total_pages": 3 }
}
```

### Get Evidence

```
GET /v1/evidence/{id}
```

**Response:** Full evidence node with raw data reference.

```jsonc
{
    "id": "trace_001",
    "type": "FUNCTION_CALL",
    "category": "behavioral",
    "engine": "trace_cognition",
    "version": "1.3.0",
    "severity": "LOW",
    "confidence": 0.95,
    "value": { "calls": 847, "errors": 312, "error_rate": 0.368 },
    "timestamp": "2026-07-14T10:23:00Z",
    "source": { "file": "src/auth/validate.ts", "line": 42 },
    "raw_data": {
        "type": "log_file",
        "ref": "logs/auth_20260714.json",
        "content_hash": "abc123def456",
        "preview": "2026-07-14 10:23:00 [TRACE] validateToken called from authenticate() caller_id=req_847"
    },
    "affected_entities": ["func_auth_validatetoken_001", "mod_auth_001"],
    "insights_using": ["insight_synth_001"]
}
```

---

## Insight Endpoints

### List Insights

```
GET /v1/insights
```

| Parameter | Type | Description |
|---|---|---|
| `entity_id` | string | Filter by affected entity |
| `type` | string | Filter by insight type (risk, opportunity, change, prediction, decision) |
| `severity` | string | Filter by severity (info, low, medium, high, critical) |
| `status` | string | Filter by status (active, acknowledged, resolved, dismissed) |
| `confidence` | string | Range filter |
| `created_at` | string | Time range filter |
| `q` | string | Full-text search on title and summary |
| `sort` | string | Sort field (default: `-created_at`) |
| `page`, `per_page` | pagination | Standard pagination |

**Response:** Paginated list of insight summaries.

```jsonc
{
    "data": [
        {
            "id": "insight_synth_001",
            "type": "risk",
            "title": "Auth module error rate degradation",
            "severity": "HIGH",
            "confidence": 0.71,
            "status": "active",
            "created_at": "2026-07-14T10:25:00Z",
            "evidence_count": 12,
            "entities": ["mod_auth_001"]
        }
    ],
    "pagination": { "page": 1, "per_page": 20, "total": 34, "total_pages": 2 }
}
```

### Get Insight

```
GET /v1/insights/{id}
```

**Response:** Full FormattedInsight with evidence chain.

### Update Insight Status

```
PATCH /v1/insights/{id}
```

Request:

```jsonc
{
    "status": "acknowledged"
}
```

Valid status transitions: `active → acknowledged`, `acknowledged → resolved|dismissed`.

### Get Insight Evidence Chain

```
GET /v1/insights/{id}/evidence-chain
```

**Response:** The full evidence chain graph (insight → evidence → raw data).

---

## Reasoning Endpoints

### Ask Question (Synchronous)

```
POST /v1/reason/question
```

Request:

```jsonc
{
    "question": "What is causing the authentication failures?",
    "entities": ["auth"],
    "time_range": { "start": "2026-07-13T00:00:00Z", "end": "2026-07-14T23:59:59Z" },
    "mode": "interactive"
}
```

**Response (200 OK):** Full FormattedInsight.

### Ask Question (Streaming)

```
POST /v1/reason/question/stream
```

Same request body. Response is `text/event-stream`:

```
event: token
data: "The"

event: token
data: " auth"

event: token
data: " module"

event: complete
data: { "insight_id": "insight_synth_002" }
```

### Evaluate (System-Triggered)

```
POST /v1/reason/evaluate
```

Request:

```jsonc
{
    "trigger": "new_evidence",
    "evidence_ids": ["trace_001", "trace_002"],
    "context": { "reasoning_type": "risk_evaluation" }
}
```

**Response (202 Accepted):**

```jsonc
{
    "job_id": "job_045",
    "status": "started",
    "estimated_duration_ms": 5000
}
```

Results are pushed via WebSocket when complete.

### Get Prediction

```
POST /v1/reason/predict
```

Request:

```jsonc
{
    "entity_id": "mod_auth_001",
    "metric": "error_rate",
    "horizon_days": 90
}
```

**Response (200 OK):** Prediction insight with forecast data.

### Get Evidence Summary (Fallback)

```
POST /v1/reason/question/evidence-summary
```

Request (same as `/v1/reason/question`):

```jsonc
{
    "question": "What is causing the authentication failures?",
    "entities": ["auth"],
    "time_range": { "start": "2026-07-13T00:00:00Z", "end": "2026-07-14T23:59:59Z" }
}
```

**Response (200 OK):**

```jsonc
{
    "fallback_reason": "LLM_UNAVAILABLE",
    "summary": "AI reasoning is currently unavailable. Here is a summary of the evidence found.",
    "evidence": [
        { "id": "trace_001", "type": "FUNCTION_CALL", "detail": "validateToken: 312 errors (36.8%)", "source": "trace_cognition" }
    ],
    "insight_confidence": 0.0,
    "display_level": "UNAVAILABLE"
}
```

This endpoint bypasses LLM inference and returns raw evidence directly. Used when Ollama is unavailable (see Error Handling — Edge Cases).

### Suggest Autocomplete

```
POST /v1/reason/suggest
```

Request:

```jsonc
{
    "question_prefix": "What is causing the auth"
}
```

**Response (200 OK):**

```jsonc
{
    "suggestions": [
        "What is causing the authentication failures?",
        "What is causing the auth module errors?"
    ]
}
```

Returns question completions based on partial user input. Used by the frontend autocomplete dropdown. Suggestions are generated from prior queries and entity names.

---

## Analysis Endpoints

### Run Analysis

```
POST /v1/analysis/run
```

| Parameter | Type | Description |
|---|---|---|
| `mode` | string | `full` (all engines) or `incremental` (changed files only) |
| `engines` | string[] | Specific engines to run (default: all registered engines) |
| `reasoning` | boolean | Run reasoning pipeline after analysis (default: true) |

**Response (202 Accepted):**

```jsonc
{
    "job_id": "job_046",
    "status": "started",
    "estimated_duration_ms": 30000,
    "progress_url": "/v1/analysis/status/job_046",
    "events_url": "ws://localhost:8000/v1/ws/events/job_046"
}
```

### Get Analysis Status

```
GET /v1/analysis/status/{job_id}
```

Response:

```jsonc
{
    "job_id": "job_046",
    "status": "running",
    "progress": 0.65,
    "current_stage": "knowledge_cognition",
    "stages_completed": ["structural_cognition", "evolution_cognition"],
    "evidence_produced": 142,
    "started_at": "2026-07-14T10:00:00Z",
    "estimated_completion": "2026-07-14T10:30:00Z"
}
```

### Cancel Analysis

```
DELETE /v1/analysis/status/{job_id}
```

**Response:** `204 No Content`.

---

## Health and Metrics

### Health Check

```
GET /health
```

Response:

```jsonc
{
    "status": "healthy",
    "version": "1.0.0",
    "services": {
        "scm_storage": { "status": "healthy", "latency_ms": 2 },
        "ollama": { "status": "healthy", "model": "llama3.1:8b-q4_K_M", "latency_ms": 45 },
        "reasoning": { "status": "healthy" }
    },
    "uptime_seconds": 86400
}
```

Degraded status: one or more non-critical services unavailable. Unhealthy: critical service unavailable.

### Metrics

```
GET /metrics
```

**Response:** Prometheus-compatible metrics in text format:

```
# HELP dna_evidence_total Total evidence nodes in SCM
# TYPE dna_evidence_total gauge
dna_evidence_total 15420
# HELP dna_insights_total Total insights generated
# TYPE dna_insights_total counter
dna_insights_total{status="active"} 34
dna_insights_total{status="resolved"} 128
```

---

## Edge Cases

### Entity Not Found

```
GET /v1/entities/nonexistent_id
→ 404 Not Found
{
    "error": {
        "code": "ENTITY_NOT_FOUND",
        "message": "Entity 'nonexistent_id' was not found.",
        "suggestions": ["Search for entities with GET /v1/entities?q=nonexistent"]
    }
}
```

### Evidence with No Insights

Evidence exists but no insight references it. The `insights_using` field is an empty array. This is valid — evidence is produced by engines before any reasoning runs.

### Analysis Job Not Found

```
GET /v1/analysis/status/job_nonexistent
→ 404 Not Found
```

### Query with No Results

```
GET /v1/insights?entity_id=nonexistent
→ 200 OK
{
    "data": [],
    "pagination": { "page": 1, "per_page": 20, "total": 0, "total_pages": 0 }
}
```

Empty results return 200 with an empty data array, not 404.

### Ollama Unavailable During Reasoning

```
POST /v1/reason/question
→ 503 Service Unavailable
{
    "error": {
        "code": "LLM_UNAVAILABLE",
        "message": "The local LLM (Ollama) is not available. Evidence summary mode is available as a fallback.",
        "fallback_endpoint": "/v1/reason/question/evidence-summary"
    }
}
```

### Invalid Parameters

```
GET /v1/entities?per_page=500
→ 422 Unprocessable Entity
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "per_page must be between 1 and 100.",
        "details": [{ "field": "per_page", "value": 500, "constraint": "max: 100" }]
    }
}
```

---

## Future Endpoints (V2+)

| Endpoint | Purpose | Phase |
|---|---|---|
| `GET /v1/relationships` | Query entity relationships (graph traversal) | V2 |
| `POST /v1/reason/compare` | Compare multiple entities in a single request | V2 |
| `POST /v1/analysis/schedule` | Schedule recurring analyses (cron) | V2 |
| `GET /v1/notifications` | Alert and notification preferences | V2 |
| `GET /v1/activity` | Audit log of user and system actions | V2 |
