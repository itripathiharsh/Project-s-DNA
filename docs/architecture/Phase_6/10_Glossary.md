================================================================================
# 10 Glossary
================================================================================

# Glossary

## Purpose

This glossary defines every key term introduced or refined across the Phase 6 documentation, with cross-references to earlier phases and to related Phase 6 terms. It ensures consistent vocabulary across the API & Integration Layer specification.

---

## A

### API Gateway

Layer 6 of the Project DNA architecture (Phase 2). The single entry point for all external access — REST API, WebSocket, and GraphQL (V2). Routes requests to internal services (Query, Reasoning, Analysis Orchestrator), enforces authentication and authorization, and handles error responses.

*See:* Phase 6/01.
*See also:* REST API, WebSocket API, GraphQL API.

### API Key

A static token used for authentication in network mode. Format: `dna_key_` + 20-char hex string. Hashed (bcrypt) in the server config. Used for programmatic access (CLI, CI/CD).

*See:* Phase 6/05.
*See also:* Authentication, JWT.

### Authorization Scope

A granular permission string in the format `<resource>:<action>` (e.g., `insights:write`, `evidence:read`). Roles grant collections of scopes. Scopes are checked by the authorization middleware on each request.

*See:* Phase 6/06.
*See also:* RBAC, Role.

---

## D

### DataLoader

A batching pattern used in GraphQL resolvers to prevent N+1 queries. Groups multiple individual data fetches into a single batch query. Used for resolving entity → evidence and entity → insight relationships.

*See:* Phase 6/03.

---

## E

### Event (WebSocket)

A server-to-client message pushed to subscribed WebSocket channels when something happens (new insight, evidence added, analysis progress, alert triggered). Each event has a type, channel, and data payload.

*See:* Phase 6/04.
*See also:* Channel, Subscription, WebSocket API.

---

## G

### GraphQL API (V2)

A flexible query API (Phase 6/03) that supplements REST. Enables clients to query nested entity→evidence→insight relationships in a single request and request exactly the fields they need. Uses standard GraphQL over HTTP with subscriptions over WebSocket.

*See:* Phase 6/03.
*See also:* REST API, WebSocket API, API Gateway.

---

## J

### JWT (JSON Web Token)

A time-limited token format used for session-based authentication in network mode. Contains claims: `sub` (user ID), `scopes` (permissions), `iat`, `exp`. Access token TTL: 1 hour. Refresh token TTL: 30 days.

*See:* Phase 6/05.
*See also:* Authentication, API Key.

---

## L

### Local Mode

The V1 default API security mode. The server binds to `127.0.0.1` only. No authentication, no authorization, no TLS. All requests are treated as the local admin user. Designed for zero-config single-developer use.

*See:* Phase 6/01, Phase 6/05.
*See also:* Network Mode.

---

## N

### Network Mode

The V2+ API security mode. The server binds to a configurable address (LAN or WAN). Authentication is required for all requests. Authorization is enforced per scope. TLS is required for WAN access.

*See:* Phase 6/01, Phase 6/05, Phase 6/06.
*See also:* Local Mode.

---

## R

### RBAC (Role-Based Access Control)

The authorization model used by Project DNA. Users are assigned roles (admin, engineer, viewer, observer). Each role grants a set of permission scopes. The authorization middleware checks the required scope against the user's role on every request.

*See:* Phase 6/06.
*See also:* Authorization Scope, Role.

### REST API

The primary synchronous API surface (Phase 6/02). Resource-oriented HTTP endpoints for CRUD operations on entities, evidence, insights, and analysis management. All endpoints prefixed with `/v1/`. Returns JSON responses with consistent pagination, filtering, and error formats.

*See:* Phase 6/02.
*See also:* API Gateway, WebSocket API, GraphQL API.

### Role

A named collection of authorization scopes. Built-in roles: admin (full access), engineer (read + write), viewer (read only), observer (limited read). Roles are assigned to users in network mode.

*See:* Phase 6/06.
*See also:* RBAC, Authorization Scope.

---

## S

### Subscription (WebSocket)

A client-initiated registration to receive events on a specific channel. Subscription patterns: `insights:{entity_id}`, `evidence:{entity_id}`, `analysis:{job_id}`, `alerts:severity>=high`. Multiple subscriptions per connection are supported.

*See:* Phase 6/04.
*See also:* WebSocket API, Event.

### Sunset Header

An HTTP header (`Sunset: Sat, 14 Oct 2027 00:00:00 GMT`) included in responses from deprecated endpoints. Indicates when the endpoint will be removed. Part of the deprecation policy requiring minimum 90 days between deprecation and removal.

*See:* Phase 6/08.
*See also:* API Versioning.

---

## W

### WebSocket API

The real-time API surface (Phase 6/04). Provides bidirectional communication for LLM token streaming, analysis progress events, and event-driven notifications (new insights, alerts). Uses the standard WebSocket protocol on the same port as the REST API.

*See:* Phase 6/04.
*See also:* REST API, GraphQL API, Event, Subscription.
