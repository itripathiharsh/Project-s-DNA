================================================================================
# 06 Authorization
================================================================================

# Authorization

## Purpose

Authorization controls what authenticated users can do with the Project DNA API. In V1 (local mode), no authorization is needed — the single user has full access. In V2+ (network mode), role-based access control ensures that users can only read or modify resources according to their assigned permissions. This document defines the authorization model, roles, permission scopes, and enforcement points.

---

## Scope

### In Scope

- Authorization model (RBAC)
- Roles and their permission sets
- Permission scopes (read, write, admin)
- Resource-level authorization
- Endpoint-to-scope mapping
- Enforcement architecture (middleware)
- Local mode bypass

### Out of Scope

- Authentication mechanisms (Phase 6/05)
- User management
- Group or team management (V3)
- Attribute-based access control (V3)

---

## Background

Phase 6/01 defined the security split: authentication verifies identity (Phase 6/05), authorization controls what that identity can do. In local mode, both are bypassed. In network mode, the API Gateway enforces authorization via middleware.

Phase 2 identified that V1 is a single-user tool. Authorization infrastructure is designed for V2+ but the architecture is defined in V1 to ensure the permission model is baked in from the start.

---

## Authorization Model

Project DNA uses **Role-Based Access Control (RBAC)**:

```
Identity (user) ─── assigned to ───> Role ─── grants ───> Permissions (scopes)
```

| Component | Description |
|---|---|
| **User** | Authenticated identity (from Phase 6/05) |
| **Role** | Named collection of permission scopes |
| **Scope** | Granular permission: `<resource>:<action>` |
| **Policy** | Additional constraints (entity-level restrictions, V3) |

---

## Roles

### Built-In Roles

| Role | Level | Description |
|---|---|---|
| `admin` | Full access | All resources, all actions, user management |
| `engineer` | Read + write | Query SCM, read insights, trigger analysis, acknowledge insights |
| `viewer` | Read only | Query SCM, read insights and evidence. No mutations. |
| `observer` | Limited read | Read public insights and health only. No evidence detail. |

### Role-Permission Matrix

| Permission Scope | admin | engineer | viewer | observer |
|---|---|---|---|---|
| `entities:read` | ✅ | ✅ | ✅ | ✅ |
| `evidence:read` | ✅ | ✅ | ✅ | ❌ |
| `evidence:detail` | ✅ | ✅ | ✅ | ❌ |
| `insights:read` | ✅ | ✅ | ✅ | ✅ (summary only) |
| `insights:write` | ✅ | ✅ | ❌ | ❌ |
| `insights:delete` | ✅ | ❌ | ❌ | ❌ |
| `analysis:run` | ✅ | ✅ | ❌ | ❌ |
| `analysis:cancel` | ✅ | ✅ | ❌ | ❌ |
| `reason:question` | ✅ | ✅ | ❌ | ❌ |
| `reason:evaluate` | ✅ | ✅ | ❌ | ❌ |
| `admin:users` | ✅ | ❌ | ❌ | ❌ |
| `admin:config` | ✅ | ❌ | ❌ | ❌ |
| `admin:keys` | ✅ | ❌ | ❌ | ❌ |

---

## Permission Scopes

### Scope Format

```
<resource>:<action>
```

| Resource | Actions | Description |
|---|---|---|
| `entities` | `read` | List and get entities |
| `evidence` | `read`, `detail` | Query evidence nodes. `detail` allows raw data access. |
| `insights` | `read`, `write`, `delete` | Query and manage insights |
| `analysis` | `run`, `cancel`, `read_status` | Manage analysis jobs |
| `reason` | `question`, `evaluate` | Invoke reasoning pipeline |
| `admin` | `users`, `config`, `keys`, `health` | Administrative operations |

### Scope to Endpoint Mapping

```
entities:read     → GET /v1/entities, GET /v1/entities/{id}
evidence:read     → GET /v1/evidence
evidence:detail   → GET /v1/evidence/{id} (full detail with raw_data)
insights:read     → GET /v1/insights, GET /v1/insights/{id}
insights:write    → PATCH /v1/insights/{id} (status changes)
insights:delete   → DELETE /v1/insights/{id} (V2+)
analysis:run      → POST /v1/analysis/run
analysis:cancel   → DELETE /v1/analysis/status/{job_id}
reason:question   → POST /v1/reason/question, WebSocket question
```

---

## Enforcement Architecture

```
Request → Auth Middleware (Phase 6/05) → [Identity Context]
       → Authorization Middleware → [Check scope] → Allowed | Denied
```

### Middleware Flow

```
1. Request arrives at API Gateway
2. Auth middleware extracts and validates token → attaches identity
3. Authorization middleware:
   a. Look up identity's role
   b. Resolve required scopes for the endpoint + method
   c. If all required scopes present in role: allow
   d. If any scope missing: 403 Forbidden
4. Request reaches the handler
```

### WebSocket Authorization

WebSocket authorization is per-connection, not per-message:

```
1. Client authenticates via WebSocket auth message
2. Server assigns role based on token claims
3. All subsequent messages on that connection are authorized
   by the connection's role
4. If a message attempts an action outside the role's scopes:
   → Server sends { "type": "error", "code": "FORBIDDEN" }
```

---

## Local Mode Bypass

In local mode (V1 default), authorization is bypassed entirely:

```python
if config.auth_mode == "local":
    # Bypass all authorization checks
    # All requests are treated as admin role
    request.identity = Identity(user="local", role="admin")
    return  # No further checks
```

This ensures V1 has zero configuration overhead while the authorization infrastructure is in place for V2+.

---

## Edge Cases

### Unknown Role

```python
role = role_registry.get(claims["role"])
if role is None:
    raise HTTPException(403, "Unknown role")
```

### Insufficient Scope

```
GET /v1/evidence/{id}/raw  (requires evidence:detail)
User has evidence:read only
→ 403 Forbidden
{
    "error": {
        "code": "INSUFFICIENT_SCOPE",
        "message": "Required scope: evidence:detail",
        "current_scopes": ["evidence:read"]
    }
}
```

### Disabled Authorization (Local Mode)

In local mode, even if scopes are missing from a hypothetical role, all requests succeed. The bypass is explicit and logs a warning on startup: `"Running in local mode — authorization disabled."`.

---

## Future Work

### Entity-Level Authorization (V3)

Restrict user access to specific entities (modules, projects):

```
alice: {"entity_restrictions": ["mod_auth_001", "mod_payment_001"]}
bob:   {"entity_restrictions": ["mod_notification_001"]}
```

Alice cannot read evidence for `mod_notification_001` even though her role grants `evidence:read`.

### Attribute-Based Access Control (V3)

ABAC extends RBAC with dynamic conditions:
- "Allow write only during business hours."
- "Allow delete only if insight.created_by == current_user."

### Audit Trail (V2)

Log every authorization decision (allow/deny) with identity, endpoint, and scopes for compliance and debugging.
