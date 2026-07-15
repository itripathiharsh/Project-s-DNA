================================================================================
# 05 Cross-Repository Cognition
================================================================================

# Cross-Repository Cognition

## Purpose

Cross-repository cognition extends DNA's analysis beyond a single repository, enabling insight into how services, libraries, and applications interact within a broader system.

---

## Why Cross-Repo Matters

| Scenario | Single-Repo | Cross-Repo |
|---|---|---|
| Service A calls Service B | Can't see B's API | Full dependency chain |
| Library upgrade impact | Can only see the library repo | Sees all consumers |
| Security vulnerability | Only checks one repo | Scans entire org |
| Architecture documentation | One component view | Full system view |

## The Cross-Repo Model

DNA builds a unified dependency graph by:

1. **Protocol detection**: Identify HTTP/gRPC/message queue interactions from code
2. **Package resolution**: Map package.json, Cargo.toml, requirements.txt to repositories
3. **API contract analysis**: Parse OpenAPI, protobuf, GraphQL schemas
4. **Cross-reference**: Link consumer calls to provider implementations

## Example

```
User asks: "What happens when I change the /checkout API?"

Cross-repo answer:
→ payment-service (owner: payments-team)
    POST /api/v1/checkout
    ↓ calls
    → auth-service (owner: platform-team)
        POST /api/v1/validate-token
    → inventory-service (owner: logistics-team)
        GET /api/v1/stock/check
    → notification-service (owner: platform-team)
        POST /api/v1/send-email

Impact: 3 downstream services, 4 teams to notify
Estimated: 2 weeks of coordinated changes
```

## Implementation Strategy

| Step | Description | V2 | V3 |
|---|---|---|---|
| 1 | Detect inter-service calls from code | ✅ | ✅ |
| 2 | Resolve repo ownership from service name | — | ✅ |
| 3 | Build cross-repo dependency graph | — | ✅ |
| 4 | Track API contract changes across repos | — | ✅ |
| 5 | Simulate impact of proposed changes | — | ✅ |
