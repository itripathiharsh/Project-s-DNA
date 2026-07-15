================================================================================
# 01 API Overview
================================================================================

# API Overview

## Purpose

The API Gateway Layer (Phase 2, Layer 6) exposes every capability of the Software Cognition Model and Cognitive Reasoning Layer through stable, versioned interfaces. This document defines the API layer's architecture, design principles, surface areas, data flow patterns, and how the three API protocols — REST, WebSocket, and GraphQL (V2) — work together to serve the UI and external integrations.

---

## Scope

### In Scope

- API layer architecture and design principles
- API surface areas and their responsibilities
- Data flow patterns (synchronous, asynchronous, streaming, event-driven)
- Protocol selection criteria (REST vs WebSocket vs GraphQL)
- Deployment model (single process, V2+ split)
- Connection to Phase 2 service architecture
- Security architecture overview (detailed in 05, 06)

### Out of Scope

- REST endpoint specifications (Phase 6/02)
- GraphQL schema design (Phase 6/03)
- WebSocket event types and subscriptions (Phase 6/04)
- Authentication mechanisms (Phase 6/05)
- Authorization model (Phase 6/06)
- Error response formats (Phase 6/07)
- API versioning strategy (Phase 6/08)
- Implementation details

---

## Background

Phase 2 (System Architecture) defined the API Gateway as Layer 6, sitting between the UI Layer (Phase 7) and the internal services (Reasoning, SCM, Analysis Orchestrator). It identified three API surfaces:
- **REST API** — Standard HTTP endpoints for CRUD and synchronous queries.
- **WebSocket API** — Real-time updates, subscriptions, bidirectional communication.
- **GraphQL API (V2)** — Flexible querying for complex SCM relationship traversal.

Phase 2 also defined the technology choice: Python (FastAPI) for the API Gateway, chosen for its async support, type safety, and OpenAPI generation.

Phase 3 (SCM) defined the data model that the API exposes: entities, relationships, evidence, insights. Phase 5 (Reasoning) defined the reasoning pipeline that the API invokes.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     UI Layer (Phase 7)                             │
│  React SPA / Desktop App / CLI                                     │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP / WebSocket
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                              │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │              │  │              │  │                      │    │
│  │  REST API    │  │  WebSocket   │  │  GraphQL (V2)        │    │
│  │  - Sync ops  │  │  - Real-time │  │  - Complex queries   │    │
│  │  - CRUD      │  │  - Events    │  │  - Relationship      │    │
│  │  - Auth      │  │  - Progress  │  │    traversal          │    │
│  │              │  │              │  │                      │    │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘    │
│         │                 │                      │                │
│         └─────────────────┴──────────────────────┘                │
│                           │                                       │
│              ┌────────────▼────────────┐                          │
│              │    Router / Dispatcher   │                          │
│              │  - Route to services    │                          │
│              │  - Auth middleware      │                          │
│              │  - Rate limiting (V2)   │                          │
│              │  - Request validation   │                          │
│              └────────────┬────────────┘                          │
│                           │                                       │
└───────────────────────────┼───────────────────────────────────────┘
                            │ Internal IPC
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Internal Services                             │
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌────────────────┐    │
│  │  Query   │ │ Reasoning│ │  Analysis  │ │ Notification   │    │
│  │  Service │ │ Service  │ │Orchestrator│ │ Service (V2)   │    │
│  └──────────┘ └──────────┘ └────────────┘ └────────────────┘    │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    SCM Storage Service                       │   │
│  └────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## API Design Principles

| Principle | Description |
|---|---|
| **Resource-oriented** | API surfaces map to SCM entities: evidence, insights, entities, relationships. |
| **Consistent conventions** | Uniform naming, status codes, error formats, pagination across all endpoints. |
| **Versioned from day one** | All APIs carry a version prefix (`/v1/`). Breaking changes require a new version. |
| **Local-first compatible** | APIs are designed to run on localhost with no external dependencies. Auth is optional in local mode. |
| **Streaming where appropriate** | Long-running operations return stream IDs or WebSocket subscriptions, not blocking responses. |
| **Self-documenting** | OpenAPI specification is auto-generated from code. |
| **Backward-compatible by default** | New fields are additive. No breaking changes within a major version. |

---

## API Surface Areas

### REST API (Phase 6/02)

The primary synchronous interface. Used for:
| Category | Examples |
|---|---|
| **Entity queries** | `GET /v1/entities`, `GET /v1/entities/{id}` |
| **Evidence retrieval** | `GET /v1/evidence`, `GET /v1/evidence/{id}` |
| **Insight access** | `GET /v1/insights`, `GET /v1/insights/{id}` |
| **Reasoning invocation** | `POST /v1/reason/question`, `POST /v1/reason/evaluate` |
| **Analysis management** | `POST /v1/analysis/run`, `GET /v1/analysis/status/{id}` |
| **Health and metrics** | `GET /health`, `GET /metrics` |

REST is the default API surface. All other protocols supplement REST — they do not replace it.

### WebSocket API (Phase 6/04)

The real-time interface. Used for:
| Category | Examples |
|---|---|
| **Insight streams** | Real-time push of new insights as they are generated |
| **Analysis progress** | Pipeline stage completion events, evidence count updates |
| **Alert notifications** | Critical risk detection, threshold crossings |
| **Interactive reasoning** | Streaming LLM tokens during question answering |
| **Connection management** | Subscribe/unsubscribe to specific entity or insight channels |

WebSocket is the primary channel for any operation that produces output over time.

### GraphQL API (Phase 6/03 — V2)

The flexible query interface. Used for:
| Category | Examples |
|---|---|
| **Complex graph traversal** | "Find all functions in the auth module that call a vulnerable dependency, written by Alice." |
| **Custom response shapes** | Clients request exactly the fields they need. |
| **Relationship exploration** | Navigate entity → evidence → insight → recommendation chains in a single query. |

GraphQL is V2 because V1's REST API + WebSocket covers all core use cases. GraphQL adds query flexibility for complex relationship traversal at the cost of implementation complexity.

---

## Data Flow Patterns

### Synchronous Request-Response (REST)

```
Client                  API Gateway                  Internal Service
  │                         │                              │
  │── GET /v1/insights ────▶│                              │
  │                         │──── query service ──────────▶│
  │                         │◀──── response ──────────────│
  │◀──── 200 OK + JSON ────│                              │
```

Used for: entity lookup, evidence retrieval, insight history.

### Asynchronous Operation (REST + Polling)

```
Client                  API Gateway              Analysis Orchestrator
  │                         │                              │
  │── POST /v1/analysis ───▶│                              │
  │                         │── start analysis ───────────▶│
  │◀── 202 Accepted ──────│                              │
  │     { job_id }         │                              │
  │                         │                              │
  │── GET /v1/jobs/{id} ──▶│                              │
  │                         │── check status ─────────────▶│
  │◀── 200 OK ────────────│                              │
  │     { status: "running" }                              │
```

Used for: long-running analysis, batch reasoning.

### Streaming (WebSocket)

```
Client                  API Gateway              Reasoning Service
  │                         │                              │
  │══ WebSocket connect ═══▶│                              │
  │── subscribe:insights ──▶│                              │
  │                         │                              │
  │                         │◀══ new insight event ═══════│
  │◀══ event:insight.new ═══│                              │
  │                         │                              │
  │── question: "Why..." ──▶│                              │
  │                         │── start reasoning ──────────▶│
  │◀══ stream:token "The" ══│◀══ token stream ═══════════│
  │◀══ stream:token " auth"═│                              │
  │◀══ stream:token " module"                             │
```

Used for: real-time insight delivery, LLM token streaming, progress updates.

### Event-Driven (Internal)

```
Engine           SCM Service        API Gateway        WebSocket Clients
  │                  │                  │                    │
  │── write evd. ───▶│                  │                    │
  │                  │── event ────────▶│                    │
  │                  │                  │── broadcast ──────▶│
  │                  │                  │   "new evidence"   │
```

Used for: engine completion events, threshold alerts, insight supersession.

---

## Connection to Service Architecture

Phase 2 defined the internal services that the API Gateway routes to:

| API Route Group | Internal Service | Description |
|---|---|---|
| `/v1/entities/**` | Query Service | Entity resolution, retrieval, search |
| `/v1/evidence/**` | Query Service + SCM Storage | Evidence query, filter, detail |
| `/v1/insights/**` | Query Service + SCM Storage | Insight retrieval, status updates |
| `/v1/reason/**` | Reasoning Service | Question answering, evaluation, prediction |
| `/v1/analysis/**` | Analysis Orchestrator | Pipeline execution, engine scheduling |
| `/v1/notifications/**` | Notification Service (V2) | Alert configuration, delivery |
| `/health`, `/metrics` | All services | Health aggregation, metric collection |

In V1, all services run in a single process (FastAPI with internal modules). The API Gateway routes to Python modules via dependency injection. In V2+, services can be split into separate processes with HTTP/gRPC communication.

---

## Security Architecture Overview

Security has two modes:

### Local Mode (V1 Default)

- Runs on localhost only (`127.0.0.1`).
- No authentication required.
- No TLS.
- No authorization checks.
- Assumes trust: the user running the process is the sole consumer.

### Network Mode (V2+)

- Binds to configurable host/port.
- Authentication required (API key, OAuth2, or JWT — see Phase 6/05).
- Authorization enforced per resource (see Phase 6/06).
- TLS required for non-localhost connections.
- Rate limiting and audit logging.

---

## API Documentation

Every endpoint is documented via auto-generated OpenAPI specification:

| Artifact | Location | Format |
|---|---|---|
| OpenAPI spec | `GET /openapi.json` | JSON |
| Swagger UI | `GET /docs` | Browser UI |
| ReDoc | `GET /redoc` | Browser UI |
| WebSocket events | Phase 6/04 | Markdown reference |

---

## Edge Cases

### API Gateway Unavailable

If the API Gateway process is not running, all external access is blocked. The CLI (running in the same process or a sibling process) can still access services directly via IPC. The UI shows a "Connecting..." state with automatic reconnection.

### Concurrent Clients (V2)

Multiple concurrent clients (team mode) share the same API Gateway. Considerations:
- WebSocket connections are per-client, with independent subscriptions.
- REST requests are stateless and scale horizontally.
- Long-running analysis jobs are associated with the requesting client for progress updates.
- Rate limiting prevents one client from starving others.

### Offline Mode

In V1, the API runs on localhost and is always available when the process is running. There is no external network dependency. Offline mode is the default, not a special case.

---

## Future Work

### gRPC API (V3)

For internal service-to-service communication when services are split into separate processes. gRPC provides typed contracts, streaming, and better performance than HTTP/REST for inter-service calls.

### CLI-First API Access (V2)

A CLI tool that wraps the REST API for scripting and automation:
```
dna query "What is causing auth failures?"
dna insights list --entity auth --severity high
dna analysis run --full
```

### API Client Libraries (V2)

Generated client libraries in Python and TypeScript for programmatic access to Project DNA capabilities.

---

## The API Doctrine

> **The API is the contract between Project DNA and everything outside it. Every capability — querying the SCM, invoking reasoning, managing analysis, receiving alerts — flows through the API Gateway. The API is resource-oriented, versioned, self-documenting, and consistent. It speaks three protocols because different interactions demand different patterns: synchronous for queries, streaming for progress, flexible for exploration. It runs on localhost in V1 and scales to team deployments in V2 without changing the client-facing interface. The API does not expose internal complexity. It presents a clean, predictable surface that the UI and CLI depend on.**
