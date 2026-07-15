================================================================================
# 07 Error Handling
================================================================================

# Error Handling

## Purpose

Consistent, predictable error responses across all API surfaces. Every error — whether from invalid input, missing resources, authentication failures, or internal faults — follows the same structure, uses the same status codes, and provides actionable information for clients. This document defines the error response format, error catalog, and error handling behavior for REST, WebSocket, and GraphQL APIs.

---

## Scope

### In Scope

- Standard error response envelope
- HTTP status code usage conventions
- Error code catalog (all error types)
- Validation error format
- WebSocket error format
- GraphQL error format
- Error logging and monitoring

### Out of Scope

- Authentication mechanisms (Phase 6/05)
- Authorization scope errors (Phase 6/06)
- Infrastructure errors (network, DNS, TLS)

---

## Background

Phase 6/02 defined the basic HTTP status code usage for REST endpoints. This document expands that into a comprehensive error handling specification covering all three API surfaces.

---

## Error Response Envelope (REST)

All errors follow a consistent JSON structure:

```jsonc
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable description of the error.",
        "details": [],           // Optional — structured detail for validation errors
        "request_id": "uuid",    // Correlates to server logs
        "timestamp": "ISO8601",
        "suggestions": []        // Optional — actionable recovery suggestions
    }
}
```

### Error Field Semantics

| Field | Required | Description |
|---|---|---|
| `code` | Always | Machine-readable error identifier (UPPER_SNAKE_CASE) |
| `message` | Always | Human-readable description (one sentence) |
| `details` | Validation errors | Array of per-field validation failures |
| `request_id` | Always | UUID for log correlation |
| `timestamp` | Always | Server timestamp |
| `suggestions` | When available | Actionable recovery hints |

---

## Error Code Catalog

### Client Errors (4xx)

| HTTP Code | Error Code | Message | When |
|---|---|---|---|
| 400 | `BAD_REQUEST` | "The request could not be processed due to invalid syntax." | Malformed JSON, invalid query params |
| 401 | `UNAUTHENTICATED` | "Authentication is required." | Missing/invalid auth token |
| 403 | `FORBIDDEN` | "You do not have permission to perform this action." | Insufficient scope |
| 404 | `ENTITY_NOT_FOUND` | "The requested resource was not found." | Resource does not exist |
| 404 | `ENDPOINT_NOT_FOUND` | "The requested endpoint does not exist." | Unknown path |
| 409 | `CONFLICT` | "The request conflicts with the current state of the resource." | Invalid status transition |
| 422 | `VALIDATION_ERROR` | "The request body failed validation." | Schema violations |
| 429 | `RATE_LIMITED` | "Too many requests. Please slow down." | Rate limit exceeded |

### Server Errors (5xx)

| HTTP Code | Error Code | Message | When |
|---|---|---|---|
| 500 | `INTERNAL_ERROR` | "An unexpected error occurred." | Unhandled exception |
| 502 | `UPSTREAM_ERROR` | "An upstream service returned an error." | Dependency failure |
| 503 | `SERVICE_UNAVAILABLE` | "The service is temporarily unavailable." | Ollama down, database offline |
| 504 | `GATEWAY_TIMEOUT` | "An upstream service timed out." | Dependency timeout |

### Domain Errors

| HTTP Code | Error Code | Message | When |
|---|---|---|---|
| 400 | `INVALID_QUESTION` | "The question could not be parsed." | Unparseable natural language query |
| 400 | `INVALID_TIME_RANGE` | "The time range is invalid." | Start after end, too wide |
| 400 | `UNSUPPORTED_REASONING_TYPE` | "The requested reasoning type is not supported." | Unknown reasoning type |
| 404 | `EVIDENCE_NOT_FOUND` | "No evidence matches the given criteria." | Empty evidence query |
| 404 | `INSIGHT_NOT_FOUND` | "The insight was not found." | Non-existent insight ID |
| 409 | `INVALID_STATUS_TRANSITION` | "Cannot transition insight from '{current}' to '{requested}'." | Invalid status change |
| 503 | `LLM_UNAVAILABLE` | "The local LLM (Ollama) is not available." | Ollama not running |
| 503 | `MODEL_NOT_FOUND` | "The configured model is not available in Ollama." | Model not pulled |

---

## Validation Error Details

For `422 VALIDATION_ERROR`, the `details` array provides per-field information:

```jsonc
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "The request body failed validation.",
        "details": [
            {
                "field": "question",
                "value": "",
                "constraint": "required",
                "message": "The 'question' field is required."
            },
            {
                "field": "entities",
                "value": "not_an_array",
                "constraint": "array",
                "message": "The 'entities' field must be an array of strings."
            },
            {
                "field": "time_range.start",
                "value": "invalid-date",
                "constraint": "ISO8601 datetime",
                "message": "Must be a valid ISO 8601 datetime string."
            }
        ],
        "request_id": "req_abc123",
        "timestamp": "2026-07-14T10:00:00Z"
    }
}
```

---

## WebSocket Error Format

WebSocket errors use the standard message envelope with type `error`:

```jsonc
{
    "type": "error",
    "id": "msg_err_001",
    "timestamp": "2026-07-14T10:00:00Z",
    "data": {
        "code": "AUTH_FAILED",
        "message": "Invalid authentication token.",
        "suggestions": ["Obtain a new token via POST /v1/auth/login"]
    }
}
```

### WebSocket Error Codes

| Code | Message | When |
|---|---|---|
| `AUTH_FAILED` | "Invalid authentication token." | Bad JWT or API key |
| `AUTH_EXPIRED` | "Authentication token has expired." | Expired JWT |
| `SUBSCRIBE_FAILED` | "Could not subscribe to channel." | Invalid channel pattern |
| `SUBSCRIBE_FORBIDDEN` | "Not authorized for this channel." | Insufficient scope for channel |
| `INVALID_MESSAGE` | "Invalid message format." | Malformed JSON |
| `RATE_LIMITED` | "Message rate exceeded." | Too many messages |
| `REASONING_FAILED` | "Reasoning pipeline failed." | LLM error or timeout |

---

## GraphQL Error Format

GraphQL errors follow the standard GraphQL error specification:

```jsonc
{
    "errors": [
        {
            "message": "Entity not found: mod_nonexistent_001",
            "extensions": {
                "code": "ENTITY_NOT_FOUND",
                "entity_id": "mod_nonexistent_001",
                "request_id": "req_def456",
                "timestamp": "2026-07-14T10:00:00Z"
            },
            "locations": [{ "line": 2, "column": 5 }],
            "path": ["entity"]
        }
    ],
    "data": {
        "entity": null
    }
}
```

---

## Error Logging

Every error is logged with:

| Field | Description |
|---|---|
| `request_id` | Correlation ID |
| `error_code` | Machine-readable error code |
| `message` | Human-readable message |
| `status_code` | HTTP status or WebSocket error type |
| `path` | API endpoint or WebSocket channel |
| `method` | HTTP method or WebSocket message type |
| `identity` | Authenticated user (or "anonymous") |
| `duration_ms` | Time from request to error |
| `stack_trace` | Server-side stack trace (not returned to client) |
| `request_body` | Truncated request body for debugging |

---

## Edge Cases

### Error During Streaming

If an error occurs mid-stream during LLM token streaming:

```jsonc
{
    "type": "error",
    "data": {
        "code": "REASONING_FAILED",
        "message": "The reasoning pipeline encountered an error."
    }
}
// Followed by:
{
    "type": "complete",
    "data": {
        "insight_id": null,
        "error": "REASONING_FAILED",
        "partial_tokens": 142
    }
}
```

The client receives all tokens generated before the error, plus the error notification. Partial insights are discarded.

### Unexpected Error

For unexpected 500 errors, details are intentionally omitted from the client response to avoid leaking internal information:

```jsonc
{
    "error": {
        "code": "INTERNAL_ERROR",
        "message": "An unexpected error occurred.",
        "request_id": "req_xyz789",
        "timestamp": "2026-07-14T10:00:00Z"
    }
}
```

The full error (including stack trace) is logged server-side with the `request_id` for debugging.

### Cascading Dependency Failure

If multiple dependencies fail, the API Gateway reports the first failure encountered and notes the degraded state in the response:

```jsonc
{
    "error": {
        "code": "SERVICE_UNAVAILABLE",
        "message": "The reasoning service is unavailable.",
        "details": {
            "degraded_services": ["ollama", "scm_storage"],
            "operational_services": ["query_service"]
        }
    }
}
```

---

## Suggestions for Recovery

Where possible, errors include actionable suggestions:

| Error Code | Suggestion Example |
|---|---|
| `LLM_UNAVAILABLE` | "Start Ollama with: ollama serve" |
| `MODEL_NOT_FOUND` | "Download the model with: ollama pull llama3.1:8b-q4_K_M" |
| `INVALID_QUESTION` | "Try a more specific question, e.g., 'What is the error rate of the auth module?'" |
| `EVIDENCE_NOT_FOUND` | "Run an analysis first: POST /v1/analysis/run" |
| `INVALID_TIME_RANGE` | "Time range must not exceed 1 year. Use a narrower range." |
