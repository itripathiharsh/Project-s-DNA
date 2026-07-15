================================================================================
# 09 API Examples
================================================================================

# API Examples

## Purpose

This document provides worked examples of the Project DNA API in action — covering REST, WebSocket, and GraphQL interactions for common use cases. Each example traces a complete interaction from request to response, demonstrating how the API surfaces defined in Phase 6/01–08 compose in practice.

---

## Example 1: Ask a Question (REST)

Complete interaction for asking a question and receiving a structured insight.

### Request

```
POST http://localhost:8000/v1/reason/question
Content-Type: application/json

{
    "question": "What is causing the authentication failures?",
    "entities": ["auth"],
    "time_range": {
        "start": "2026-07-13T00:00:00Z",
        "end": "2026-07-14T23:59:59Z"
    },
    "mode": "interactive"
}
```

### Response

```
2026-07-14 10:25:00 POST /v1/reason/question
2026-07-14 10:25:04 200 OK (3.4s)
```

```jsonc
{
    "id": "insight_synth_001",
    "type": "risk",
    "title": "Root cause: Auth deployment introduced null config path",
    "summary": "Authentication failures are caused by a recent deployment to validate.ts (v2.2.0) that introduced an undefined TokenConfig code path, triggering TypeErrors on 36.8% of calls.",
    "detailed_explanation": "## Summary\n...",
    "confidence": 0.71,
    "severity": "HIGH",
    "evidence_chain": {
        "insight": { "id": "insight_synth_001", "title": "Root cause: ...", "confidence": 0.71 },
        "supporting_evidence": [
            {
                "evidence": { "id": "trace_001", "type": "FUNCTION_CALL", "value": "validateToken: 312 errors (36.8%)", "confidence": 0.95 },
                "supports": "Error rate data shows degradation",
                "derived_from": [{ "evidence_id": "trace_001", "raw_data_ref": "logs/auth_20260714.json", "confidence": 0.95 }]
            }
        ]
    },
    "recommendations": [{
        "action": "Roll back src/auth/validate.ts to version 2.1.3",
        "effort_estimate": "30 minutes",
        "risk": "LOW",
        "confidence": 0.85,
        "evidence_refs": ["trace_001", "trace_002"]
    }],
    "reasoning_metadata": {
        "model": "llama3.1:8b-q4_K_M",
        "prompt_tokens": 4520,
        "response_tokens": 412,
        "duration_ms": 3400,
        "evidence_consulted": 12,
        "engines_used": ["trace_cognition", "metric_cognition", "evolution_cognition"]
    }
}
```

---

## Example 2: Ask a Question with Streaming (WebSocket)

Real-time interaction showing LLM token streaming via WebSocket.

### Connect

```
→ ws://localhost:8000/v1/ws
← { "type": "connected", "connection_id": "conn_001", "version": "1.0" }
```

### Submit Question

```
→ {
    "type": "question",
    "id": "q_001",
    "data": {
        "question": "What is causing the authentication failures?",
        "entities": ["auth"],
        "mode": "interactive"
    }
}
```

### Receive Stream

```
← { "type": "ack", "id": "q_001", "data": { "insight_id": "insight_synth_001" } }

← { "type": "event", "channel": "reasoning:insight_synth_001", "data": { "event_type": "reasoning_started", "stages": ["intent", "context", "prompt"] } }

← { "type": "token", "data": { "token": "Authentication", "index": 0 } }
← { "type": "token", "data": { "token": " failures", "index": 1 } }
← { "type": "token", "data": { "token": " are", "index": 2 } }
← { "type": "token", "data": { "token": " caused", "index": 3 } }
← { "type": "token", "data": { "token": " by", "index": 4 } }
... (412 tokens total)

← { "type": "complete", "data": {
    "insight_id": "insight_synth_001",
    "token_count": 412,
    "duration_ms": 3400,
    "confidence": 0.71
}}
```

---

## Example 3: Retrieve Entities and Related Data (REST)

Navigating the SCM from entity to evidence to insights.

```
GET /v1/entities?type=module&q=auth
```

```jsonc
{
    "data": [
        { "id": "mod_auth_001", "name": "src/auth", "type": "module", "evidence_count": 47, "insight_count": 12 },
        { "id": "mod_auth_lib_001", "name": "src/auth/lib", "type": "module", "evidence_count": 12, "insight_count": 3 }
    ],
    "pagination": { "page": 1, "per_page": 20, "total": 2, "total_pages": 1 }
}
```

```
GET /v1/entities/mod_auth_001
```

```jsonc
{
    "id": "mod_auth_001",
    "name": "src/auth",
    "type": "module",
    "relationships": {
        "children": [
            { "id": "file_auth_001", "name": "validate.ts", "type": "file" },
            { "id": "file_auth_002", "name": "provider.ts", "type": "file" }
        ],
        "dependencies": [{ "id": "dep_lodash_001", "name": "lodash", "type": "package" }]
    }
}
```

```
GET /v1/evidence?entity_id=mod_auth_001&per_page=3
```

```jsonc
{
    "data": [
        { "id": "trace_001", "type": "FUNCTION_CALL", "engine": "trace_cognition", "value": "validateToken: 312 errors (36.8%)", "confidence": 0.95 },
        { "id": "trace_002", "type": "EXCEPTION", "engine": "trace_cognition", "value": "TypeError at validate.ts:88", "confidence": 0.98 },
        { "id": "metric_001", "type": "COUNTER", "engine": "metric_cognition", "value": "auth error rate avg 0.368, trend increasing", "confidence": 0.85 }
    ],
    "pagination": { "page": 1, "per_page": 3, "total": 47, "total_pages": 16 }
}
```

```
GET /v1/insights?entity_id=mod_auth_001&severity=high
```

```jsonc
{
    "data": [
        {
            "id": "insight_synth_001",
            "type": "risk",
            "title": "Root cause: Auth deployment introduced null config path",
            "severity": "HIGH",
            "confidence": 0.71,
            "status": "active",
            "created_at": "2026-07-14T10:25:00Z"
        }
    ],
    "pagination": { "page": 1, "per_page": 20, "total": 1, "total_pages": 1 }
}
```

---

## Example 4: Run Analysis and Monitor Progress (REST + WebSocket)

Long-running analysis with progress tracking.

### Initiate Analysis

```
POST /v1/analysis/run
Content-Type: application/json
{
    "mode": "full",
    "reasoning": true
}
→ 202 Accepted
{
    "job_id": "job_046",
    "status": "started",
    "estimated_duration_ms": 30000,
    "progress_url": "/v1/analysis/status/job_046",
    "events_url": "ws://localhost:8000/v1/ws/events/job_046"
}
```

### Poll Status (or Subscribe via WebSocket)

```
GET /v1/analysis/status/job_046
→ 200 OK
{
    "job_id": "job_046",
    "status": "running",
    "progress": 0.45,
    "current_stage": "dependency_cognition",
    "stages_completed": ["structural_cognition", "evolution_cognition", "knowledge_cognition"],
    "evidence_produced": 89,
    "started_at": "2026-07-14T10:00:00Z"
}
```

### Completion

```
GET /v1/analysis/status/job_046
→ 200 OK
{
    "job_id": "job_046",
    "status": "completed",
    "progress": 1.0,
    "duration_ms": 28500,
    "engines_run": 6,
    "evidence_produced": 234,
    "insights_generated": 3,
    "new_insight_ids": ["insight_synth_001", "insight_synth_002", "insight_pred_001"]
}
```

---

## Example 5: Acknowledge and Resolve Insight (REST)

Insight lifecycle management.

### List Active Insights

```
GET /v1/insights?status=active&entity_id=mod_auth_001
```

### Acknowledge

```
PATCH /v1/insights/insight_synth_001
Content-Type: application/json
{ "status": "acknowledged" }
→ 200 OK
{
    "id": "insight_synth_001",
    "status": "acknowledged",
    "title": "Root cause: Auth deployment introduced null config path",
    "updated_at": "2026-07-14T11:00:00Z"
}
```

### Resolve

```
PATCH /v1/insights/insight_synth_001
Content-Type: application/json
{ "status": "resolved" }
→ 200 OK
{
    "id": "insight_synth_001",
    "status": "resolved",
    "title": "Root cause: Auth deployment introduced null config path",
    "resolution_note": "Rolled back to v2.1.3. Error rate returned to 4.8%.",
    "updated_at": "2026-07-14T12:30:00Z"
}
```

---

## Example 6: GraphQL Query (V2)

Complex cross-modality query in a single request.

### Request

```graphql
{
    entity(id: "mod_auth_001") {
        name
        type
        evidence(engine: "trace_cognition", first: 5) {
            edges {
                node {
                    id
                    type
                    value
                    confidence
                }
            }
        }
        insights(status: ACTIVE) {
            id
            title
            severity
            confidence
            recommendations {
                action
                effortEstimate
                risk
            }
        }
    }
    search(q: "auth", types: [ENTITY]) {
        edges {
            node {
                ... on Entity { id name type }
            }
        }
    }
}
```

### Response

```jsonc
{
    "data": {
        "entity": {
            "name": "src/auth",
            "type": "MODULE",
            "evidence": {
                "edges": [
                    { "node": { "id": "trace_001", "type": "FUNCTION_CALL", "value": "validateToken: 312 errors (36.8%)", "confidence": 0.95 } }
                ]
            },
            "insights": [
                {
                    "id": "insight_synth_001",
                    "title": "Root cause: Auth deployment introduced null config path",
                    "severity": "HIGH",
                    "confidence": 0.71,
                    "recommendations": [{
                        "action": "Roll back src/auth/validate.ts to version 2.1.3",
                        "effortEstimate": "30 minutes",
                        "risk": "LOW"
                    }]
                }
            ]
        },
        "search": {
            "edges": [
                { "node": { "id": "mod_auth_001", "name": "src/auth", "type": "MODULE" } },
                { "node": { "id": "file_auth_001", "name": "validate.ts", "type": "FILE" } }
            ]
        }
    }
}
```

**REST equivalent:** 4 separate HTTP requests (entity, evidence, insights, search). GraphQL: 1 request.

---

## Example 7: Error Handling

### Validation Error

```
POST /v1/reason/question
Content-Type: application/json
{ "question": "" }
→ 422 Unprocessable Entity
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "The request body failed validation.",
        "details": [
            { "field": "question", "value": "", "constraint": "required", "message": "The 'question' field is required." }
        ],
        "request_id": "req_val_001",
        "timestamp": "2026-07-14T10:00:00Z"
    }
}
```

### LLM Unavailable

```
POST /v1/reason/question
Content-Type: application/json
{ "question": "What is the error rate?" }
→ 503 Service Unavailable
{
    "error": {
        "code": "LLM_UNAVAILABLE",
        "message": "The local LLM (Ollama) is not available.",
        "request_id": "req_503_001",
        "timestamp": "2026-07-14T10:00:00Z",
        "suggestions": ["Start Ollama with: ollama serve"]
    }
}
```

### Entity Not Found

```
GET /v1/entities/nonexistent
→ 404 Not Found
{
    "error": {
        "code": "ENTITY_NOT_FOUND",
        "message": "Entity 'nonexistent' was not found.",
        "request_id": "req_404_001",
        "timestamp": "2026-07-14T10:00:00Z",
        "suggestions": ["GET /v1/entities to list all entities"]
    }
}
```

### Insufficient Authorization

```
PATCH /v1/insights/insight_synth_001
Authorization: Bearer viewer_token
{ "status": "resolved" }
→ 403 Forbidden
{
    "error": {
        "code": "FORBIDDEN",
        "message": "You do not have permission to perform this action.",
        "details": { "required_scope": "insights:write", "current_scopes": ["insights:read"] },
        "request_id": "req_403_001",
        "timestamp": "2026-07-14T10:00:00Z"
    }
}
```
