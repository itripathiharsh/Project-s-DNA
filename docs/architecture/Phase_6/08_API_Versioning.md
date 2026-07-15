================================================================================
# 08 API Versioning
================================================================================

# API Versioning

## Purpose

Project DNA's API is versioned from day one to ensure backward compatibility, enable safe evolution, and give clients predictable upgrade paths. This document defines the versioning strategy — how versions are expressed, when breaking changes are allowed, how deprecation works, and how clients discover available versions.

---

## Scope

### In Scope

- Version numbering scheme
- URL-based versioning
- Breaking vs. non-breaking changes
- Deprecation policy
- Version lifecycle (introduce → stabilize → deprecate → sunset)
- Client discovery of available versions

### Out of Scope

- Internal service versioning
- SCM data model versioning
- Cognitive Engine versioning
- LLM model versioning

---

## Background

Phase 6/02 established the version prefix convention: all REST endpoints begin with `/v1/`. This document formalizes the versioning strategy that prefix represents.

---

## Version Numbering

### Scheme: `v{major}`

Project DNA uses a simple major-version prefix:

```
/v1/entities
/v1/insights
/v1/reason/question
```

| Component | Meaning | Example |
|---|---|---|
| `v` | Version prefix | `v` |
| `major` | Breaking change indicator | `1`, `2`, `3` |

There are no minor or patch versions in the URL path. Non-breaking changes (new fields, new endpoints, new optional parameters) are additive within a major version.

### Version Status

| Major Version | Status | Since | Until |
|---|---|---|---|
| v1 | Active (current) | V1 release | V2+ release |
| v2 | Planned | V2+ release | V3+ release |

---

## Breaking vs. Non-Breaking Changes

### Breaking Changes (Require New Major Version)

| Change Type | Example |
|---|---|
| Removing a field from a response | Deleting `evidence_refs` from insight response |
| Renaming a field | `created_at` → `generated_at` |
| Changing a field type | `confidence` from float to string |
| Removing an endpoint | `DELETE /v1/insights/{id}` removed |
| Changing request schema | Adding a required field |
| Changing error codes | `NOT_FOUND` → `RESOURCE_NOT_FOUND` |
| Changing status code | 200 → 201 for creation |

### Non-Breaking Changes (Allowed Within a Major Version)

| Change Type | Example |
|---|---|
| Adding a new endpoint | `POST /v1/reason/compare` |
| Adding an optional field to response | New `metadata` object |
| Adding an optional request parameter | New `sort` parameter |
| Adding a new error code | New domain-specific error code |
| Changing response field order | JSON object key reordering |
| Performance improvements | Faster query execution |
| Expanding enum values | New insight type added |

---

## Deprecation Policy

### Deprecation Process

```
1. Announce: Deprecated features are announced in changelog and API docs
2. Sunset header: Deprecated endpoints include Sunset header
3. Grace period: Minimum 90 days between deprecation and removal
4. Removal: Feature removed in next major version
```

### Sunset Header

Deprecated endpoints include the `Sunset` HTTP header:

```
GET /v1/evidence/deprecated-endpoint
→ 200 OK
Sunset: Sat, 14 Oct 2027 00:00:00 GMT
```

### Deprecation Warning in Response

For softly deprecated fields, a warning is included in the response:

```jsonc
{
    "data": { ... },
    "warnings": [
        {
            "code": "DEPRECATED_FIELD",
            "message": "The 'evidence_refs' field is deprecated. Use 'evidence_chain' instead.",
            "deprecated_in": "v1",
            "removed_in": "v2"
        }
    ]
}
```

---

## Version Discovery

### Root Endpoint

```
GET /
→ 200 OK
{
    "versions": {
        "v1": {
            "status": "active",
            "base_url": "/v1",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "since": "2026-07-14",
            "deprecated": false
        }
    },
    "current_version": "v1",
    "latest_version": "v1"
}
```

### Content Negotiation (Alternative)

Clients can also specify version via `Accept` header:

```
Accept: application/vnd.dna.v1+json
```

Both URL prefix and content negotiation are supported. URL prefix is the primary mechanism.

---

## Backward Compatibility Guarantees

Within a major version (e.g., `v1`):

1. **No existing endpoint will be removed** without 90 days' notice.
2. **No existing field will be removed** from responses.
3. **No existing required fields** will be added to request schemas.
4. **Error codes** will not be reused with different semantics.
5. **HTTP status codes** for existing endpoints will not change.
6. **New fields in responses** are additive — clients that ignore unknown fields will continue to work.

---

## Version Lifecycle

```
Introduce → Stabilize → Deprecate → Sunset
```

| Phase | Description | Timeline |
|---|---|---|
| **Introduce** | New major version available alongside previous version | Day 0 |
| **Stabilize** | Bug fixes only. No new features added. | After 3 months |
| **Deprecate** | Announced publicly. Sunset header included. | After 12 months |
| **Sunset** | Endpoint removed. Clients must migrate. | After 15 months (90 days post-deprecation) |

### Client Migration Guidance

When a new major version is released:
1. Previous version remains available for 12 months.
2. Migration guides are published for every breaking change.
3. Deprecated endpoints log warnings to assist client maintainers in discovering usage.

---

## Edge Cases

### Unversioned Request

```
GET /entities (no version prefix)
→ 404 Not Found (or redirect to latest version)
```

Unversioned requests are rejected with a clear error:

```jsonc
{
    "error": {
        "code": "ENDPOINT_NOT_FOUND",
        "message": "Use a versioned endpoint. Try: /v1/entities",
        "suggestions": ["GET /v1/entities", "GET / to list available versions"]
    }
}
```

### Non-Existent Version

```
GET /v99/entities
→ 404 Not Found
{
    "error": {
        "code": "ENDPOINT_NOT_FOUND",
        "message": "API version 'v99' does not exist.",
        "suggestions": ["Available versions: v1"]
    }
}
```

### Client on Outdated Version After Sunset

If a client continues to call a sunset version, the server responds with `410 Gone`:

```
GET /v0/entities
→ 410 Gone
{
    "error": {
        "code": "VERSION_SUNSET",
        "message": "API version 'v0' has been sunset since 2026-01-01.",
        "suggestions": ["Migrate to v1. See migration guide at /docs/migration/v0-to-v1"]
    }
}
```
