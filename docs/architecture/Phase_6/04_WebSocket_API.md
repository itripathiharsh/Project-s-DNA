================================================================================
# 04 WebSocket API
================================================================================

# WebSocket API

## Purpose

The WebSocket API provides real-time, bidirectional communication between clients and the Project DNA backend. It delivers LLM token streams, analysis progress, new insight notifications, and alert events as they happen — without polling. This document defines the connection protocol, event types, subscription model, and message format.

---

## Scope

### In Scope

- Connection lifecycle (connect, authenticate, subscribe, disconnect)
- Message format and envelope
- Event catalog (all push event types)
- Client-to-server messages
- Subscription model (channels, filters)
- LLM token streaming protocol
- Error handling and reconnection

### Out of Scope

- Authentication token exchange (Phase 6/05)
- Authorization checks per event (Phase 6/06)
- REST endpoints (Phase 6/02)
- GraphQL subscriptions (Phase 6/03 — built on this infrastructure)

---

## Background

Phase 6/01 identified WebSocket as the real-time API surface, used for three primary purposes:
1. **LLM token streaming** — push generated tokens to the UI as the model produces them.
2. **Analysis and pipeline progress** — push stage completion events during long operations.
3. **Event-driven notifications** — push new insights, evidence, and alerts as the SCM updates.

Phase 2 established the technology: Python (FastAPI) natively supports WebSocket with the `websockets` library. The WebSocket API shares the same port as the REST API (`ws://localhost:8000/v1/ws`).

---

## Connection Lifecycle

### Connect

```
Client → Server:  ws://localhost:8000/v1/ws
Server → Client:  { "type": "connected", "connection_id": "conn_abc123", "version": "1.0" }
```

### Authenticate (Network Mode)

In local mode, authentication is skipped. In network mode:

```
Client → Server:  { "type": "auth", "token": "jwt_or_api_key" }
Server → Client:  { "type": "auth_ok", "user": "alice", "scopes": ["read", "write"] }
Server → Client:  { "type": "auth_error", "message": "Invalid token" }
```

### Subscribe

After connection, the client subscribes to event channels:

```
Client → Server:  { "type": "subscribe", "channels": ["insights:mod_auth_001", "alerts:severity>=high"] }
Server → Client:  { "type": "subscribed", "channels": ["insights:mod_auth_001", "alerts:severity>=high"], "subscription_id": "sub_001" }
```

### Disconnect

Either side may close the connection. Clean disconnect:

```
Client → Server:  { "type": "unsubscribe_all" }
Client → Server:  Close frame (1000)
```

---

## Message Format

Every message follows a standard envelope:

```jsonc
{
    "type": "string",           // Message type identifier
    "id": "string",             // Unique message ID (UUID)
    "timestamp": "ISO8601",     // Server timestamp
    "channel": "string",        // Source channel (for events)
    "data": {},                 // Type-specific payload
    "error": null               // Error object if applicable
}
```

### Client-to-Server Types

| Type | Purpose |
|---|---|
| `auth` | Send authentication token |
| `subscribe` | Subscribe to event channels |
| `unsubscribe` | Unsubscribe from specific channels |
| `unsubscribe_all` | Unsubscribe from all channels |
| `ping` | Heartbeat keepalive |
| `question` | Submit a question for streaming reasoning |

### Server-to-Client Types

| Type | Purpose |
|---|---|
| `connected` | Connection established |
| `auth_ok` / `auth_error` | Authentication result |
| `subscribed` / `unsubscribed` | Subscription confirmation |
| `event` | A subscribed event occurred |
| `token` | LLM token chunk (streaming) |
| `complete` | LLM streaming complete |
| `error` | Error during message processing |
| `pong` | Heartbeat response |

---

## Event Catalog

### Insight Events

Triggered when new insights are created, updated, or superseded.

```jsonc
{
    "type": "event",
    "channel": "insights:mod_auth_001",
    "data": {
        "event_type": "insight_created",
        "insight": {
            "id": "insight_synth_002",
            "title": "Auth module error rate degradation",
            "severity": "HIGH",
            "confidence": 0.71,
            "type": "risk",
            "entities": ["mod_auth_001"]
        }
    }
}
```

| Event Sub-Type | When |
|---|---|
| `insight_created` | New insight written to Reasoning Store |
| `insight_updated` | Insight status changed (acknowledged, resolved) |
| `insight_superseded` | Existing insight replaced by newer analysis |

**Subscription pattern:** `insights:{entity_id}` or `insights:*` (all entities).

### Evidence Events

Triggered when Cognitive Engines produce new evidence.

```jsonc
{
    "type": "event",
    "channel": "evidence:mod_auth_001",
    "data": {
        "event_type": "evidence_added",
        "evidence": {
            "id": "trace_004",
            "type": "FUNCTION_CALL",
            "engine": "trace_cognition",
            "severity": "MEDIUM",
            "confidence": 0.92,
            "value": "authenticate() call duration increased 300%"
        }
    }
}
```

**Subscription pattern:** `evidence:{entity_id}` or `evidence:{entity_id}:{engine}`.

### Analysis Progress Events

Triggered during analysis runs.

```jsonc
{
    "type": "event",
    "channel": "analysis:job_046",
    "data": {
        "event_type": "stage_completed",
        "stage": "knowledge_cognition",
        "progress": 0.55,
        "evidence_produced": 89,
        "duration_ms": 4200
    }
}
```

| Event Sub-Type | When |
|---|---|
| `analysis_started` | Job initiated |
| `stage_started` | Stage began execution |
| `stage_completed` | Stage finished |
| `analysis_completed` | All stages done |
| `analysis_failed` | Unrecoverable error |
| `analysis_cancelled` | User cancelled |

**Subscription pattern:** `analysis:{job_id}`.

### Alert Events

Triggered by threshold crossings or critical findings.

```jsonc
{
    "type": "event",
    "channel": "alerts:severity>=high",
    "data": {
        "event_type": "alert",
        "alert": {
            "id": "alert_001",
            "severity": "HIGH",
            "title": "Auth module error rate exceeded threshold",
            "message": "Error rate at 36.8% (threshold: 10%)",
            "entity_id": "mod_auth_001",
            "insight_id": "insight_synth_001",
            "threshold": { "metric": "error_rate", "value": 10, "actual": 36.8 }
        }
    }
}
```

**Subscription pattern:** `alerts:severity>=high`, `alerts:entity={entity_id}`, or `alerts:*`.

---

## LLM Token Streaming

The WebSocket API enables real-time streaming of LLM-generated tokens during question answering.

### Flow

```
1. Client sends question via WebSocket
2. Server acknowledges and begins reasoning
3. Server streams tokens as the model generates them
4. Server sends complete event with insight summary
5. Full insight is available via REST for retrieval
```

### Client Request

```jsonc
{
    "type": "question",
    "id": "msg_001",
    "data": {
        "question": "What is causing the authentication failures?",
        "entities": ["auth"],
        "mode": "interactive"
    }
}
```

### Server Response Stream

```jsonc
// Server acknowledges
{ "type": "ack", "id": "msg_001", "data": { "insight_id": "insight_synth_002" } }

// Reasoning started
{ "type": "event", "channel": "reasoning:insight_synth_002", "data": { "event_type": "reasoning_started", "stages": ["intent", "context", "prompt"] } }

// Token chunks
{ "type": "token", "channel": "reasoning:insight_synth_002", "data": { "token": "The", "index": 0 } }
{ "type": "token", "channel": "reasoning:insight_synth_002", "data": { "token": " auth", "index": 1 } }
{ "type": "token", "channel": "reasoning:insight_synth_002", "data": { "token": " module", "index": 2 } }

// Reasoning complete
{
    "type": "complete",
    "channel": "reasoning:insight_synth_002",
    "data": {
        "insight_id": "insight_synth_002",
        "token_count": 412,
        "duration_ms": 3400,
        "confidence": 0.71
    }
}
```

---

## Heartbeat and Reconnection

### Heartbeat

The client sends `ping` every 30 seconds. The server responds with `pong`. If no `pong` is received within 10 seconds, the client attempts reconnection.

### Reconnection

```
1. Client detects connection drop
2. Client waits 1s, then attempts reconnect
3. If fails: exponential backoff (1s, 2s, 4s, 8s, max 30s)
4. On reconnect:
   a. Client re-authenticates (if network mode)
   b. Client re-subscribes to active channels
   c. Server replays last event per channel (if within 60s)
5. If reconnect fails after 5 minutes: client reports "disconnected"
```

### Replay on Reconnect

When a client reconnects and resubscribes within 60 seconds, the server replays the most recent event per subscribed channel. This prevents missed events during brief disconnections.

---

## Edge Cases

### Subscription to Non-Existent Entity

```
Client subscribes to insights:nonexistent_entity
Server accepts subscription, but no events will fire until evidence or insights
exist for that entity.
```

### Rate Limiting

In network mode (V2+), WebSocket message rate is limited:
- Max 60 messages per minute per connection (control messages excluded).
- Exceeding the limit triggers a warning, then disconnect on third violation.

### Connection Limit

In local mode, no connection limit (typically 1 client). In network mode (V2+), configurable per-user limit (default: 5 concurrent connections).

### Unsolicited Events

Clients receive events only for channels they have explicitly subscribed to. Server never pushes to unsubscribed clients.

---

## Future Work

### Message Persistence (V3)

Persist undelivered events for offline clients. When a client reconnects after extended disconnection, it receives all missed events within a configurable window (default: 24 hours).

### Compression (V2)

Apply per-message deflate compression for large event payloads, reducing bandwidth for evidence and insight data.

### Channel Groups (V2)

Allow subscribing to pre-defined channel groups (e.g., `"project:dashboard"` expands to `insights:mod_auth_001`, `insights:mod_payment_001`, `alerts:*`).
