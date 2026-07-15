================================================================================
# 05 Authentication
================================================================================

# Authentication

## Purpose

Authentication verifies the identity of clients connecting to the Project DNA API. In V1, the system runs on localhost with no authentication required. In V2+, network deployment requires authentication to secure access. This document defines both modes, the authentication mechanisms, token management, and the transition from local to network mode.

---

## Scope

### In Scope

- Local mode (V1 default) — trust-by-default on localhost
- Network mode (V2+) — authentication methods
- API key authentication
- JWT token authentication
- OAuth2 integration (V2+)
- Token lifecycle (issue, validate, refresh, revoke)
- WebSocket authentication
- Post-auth identity propagation

### Out of Scope

- Authorization (permissions per resource — Phase 6/06)
- TLS configuration
- User management UI
- Single sign-on (V3)

---

## Background

Phase 6/01 defined two security modes: Local (no auth, localhost only) and Network (auth required). This document details the authentication mechanisms for both.

Phase 2 established that V1 is a single-user local tool. Authentication exists primarily to enable future team deployments.

---

## Modes

### Local Mode (V1)

| Property | Value |
|---|---|
| Bind address | `127.0.0.1` only |
| Auth required | No |
| Default user | `local` (system user) |
| TLS | No |
| Use case | Single developer on local machine |

In local mode, all API requests are treated as originating from the local user. No authentication headers are checked. The `/health` and all `/v1/*` endpoints are fully accessible.

### Network Mode (V2+)

| Property | Value |
|---|---|
| Bind address | Configurable (`0.0.0.0` for LAN, specific IP for WAN) |
| Auth required | Yes (except `/health`) |
| TLS | Required for WAN, recommended for LAN |
| Use case | Team deployment, CI/CD integration |

In network mode, every request (except `/health`) must include authentication. Unauthenticated requests receive `401 Unauthorized`.

### Mode Detection

The API Gateway determines the mode at startup based on the bind address:

```
if bind_address == "127.0.0.1":
    mode = "local"
else:
    mode = "network"
    auth_middleware.enable()
```

The mode is also configurable explicitly: `AUTH_MODE=local|network`.

---

## Authentication Methods

### API Key (Default for Network Mode)

Simple, static key for programmatic access.

```
GET /v1/insights
Authorization: Bearer dna_key_b7a3f8e12c...
```

| Property | Value |
|---|---|
| Format | `dna_key_` + 20-char hex string |
| Storage | Hashed (bcrypt) in local config file |
| Rotation | Manual — user generates new key, old key revoked |
| Use case | CLI tools, CI/CD scripts, single-user network access |

### JWT Token (V2+)

Time-limited tokens for interactive sessions.

```
POST /v1/auth/login
{ "username": "alice", "password": "..." }

Response:
{
    "access_token": "eyJhbGci...",
    "refresh_token": "dna_ref_...",
    "expires_in": 3600
}
```

| Property | Value |
|---|---|
| Algorithm | RS256 or HS256 |
| Access token TTL | 1 hour |
| Refresh token TTL | 30 days |
| Claims | `sub` (user ID), `scopes` (permissions), `iat`, `exp` |

### OAuth2 (V2+)

Integration with external identity providers (GitHub, GitLab, Google).

```
GET /v1/auth/oauth2/github/authorize
→ Redirects to GitHub OAuth page
→ Callback: POST /v1/auth/oauth2/github/callback
→ Returns JWT tokens
```

| Property | Value |
|---|---|
| Supported providers | GitHub, GitLab (extensible) |
| Scope | `openid`, `profile`, `email` |
| Token exchange | Authorization code flow |

---

## Token Lifecycle

### API Key Management

```
POST /v1/auth/keys          → Create new API key
GET  /v1/auth/keys          → List active keys (partial mask)
DELETE /v1/auth/keys/{id}   → Revoke key
```

### JWT Token Flow

```
1. Client: POST /v1/auth/login → { access_token, refresh_token }
2. Client: Uses access_token for API calls (1 hour TTL)
3. Client: POST /v1/auth/refresh → { "refresh_token": "..." }
4. Server: Validates refresh token → returns new access_token
5. Client: POST /v1/auth/logout → Revokes refresh token
```

### Token Validation

Every authenticated request passes through middleware:

```
1. Extract token from Authorization header
2. If API key: lookup in hashed key store
3. If JWT: verify signature, check expiry, decode claims
4. If OAuth2: validate with provider (optional introspection)
5. If valid: attach identity to request context
6. If invalid: return 401
```

---

## WebSocket Authentication

WebSocket connections authenticate at connection time:

```
1. Client connects to ws://host/v1/ws
2. Server sends { "type": "connected" } (no auth yet)
3. Client sends { "type": "auth", "token": "..." }
4. Server validates token and responds { "type": "auth_ok" }
5. Unauthenticated connections receive no events
6. Connections that fail auth within 5s are closed
```

---

## Edge Cases

### Expired Token During Streaming

If a JWT token expires during an active WebSocket streaming session, the stream continues until complete. New subscriptions or REST requests require a fresh token.

### Concurrent Local and Network Access

Not supported in V1. If the bind address is `127.0.0.1`, external access is impossible by design. V2+ allows binding to `0.0.0.0` with auth required.

### First-Run Key Generation

On first startup in network mode, if no API key exists:
1. Server generates a random key.
2. Key is printed to stdout: `Generated API key: dna_key_b7a3f8e12c...`
3. Key is written to config file.
4. User copies the key before first client use.

---

## Future Work

### Certificate-Based Auth (V3)

For CI/CD and automated tooling, support TLS client certificates as an alternative to API keys.

### Rate-Limit Per Identity (V2)

Track API usage per authenticated identity and enforce per-user rate limits.

### Audit Logging (V2)

Log all authenticated requests with user identity, action, timestamp, and outcome.
