================================================================================
# 03 GraphQL API
================================================================================

# GraphQL API

## Purpose

The GraphQL API (V2) provides a flexible query interface for traversing the complex relationship graph of the Software Cognition Model. Where REST excels at resource-oriented operations, GraphQL enables clients to query across entities, evidence, and insights in a single request — requesting exactly the fields they need. This document defines the GraphQL schema, query patterns, mutations, and how GraphQL complements the existing REST and WebSocket APIs.

---

## Scope

### In Scope

- GraphQL schema design principles
- Root query types and example queries
- Mutations for state changes
- Subscriptions for real-time events
- Integration with existing REST API
- Performance considerations
- Security model for GraphQL

### Out of Scope

- Full exhaustive schema listing (auto-generated from code)
- REST endpoint replacement (REST remains primary)
- WebSocket event replacement (Phase 6/04)
- Authentication and authorization details (Phase 6/05, 6/06)

---

## Background

Phase 6/01 identified GraphQL as a V2 API surface, motivated by the need to traverse entity → evidence → insight → recommendation chains in a single query. REST requires multiple round-trips for such traversals; GraphQL's nested query model handles them natively.

Phase 2 identified the SCM as a graph-structured data model with entities, relationships, and evidence. GraphQL's schema model maps naturally to graph queries.

---

## When to Use GraphQL vs REST

| Use Case | API Surface | Reason |
|---|---|---|
| **CRUD operations** (list entities, get insight, update status) | REST | Simple, well-defined resources |
| **Complex graph traversal** (entity → dependencies → evidence → insights) | GraphQL | Nested queries avoid N+1 round trips |
| **Custom field selection** (client needs 3 of 20 fields) | GraphQL | Over-fetch elimination |
| **File upload / download** | REST | GraphQL has poor file handling |
| **Long-running operations** | REST (202) + WebSocket | GraphQL mutations for async are awkward |
| **Real-time subscriptions** | WebSocket (Phase 6/04) | Native WebSocket support |
| **Ad-hoc exploration** ("what relationships exist?") | GraphQL | Introspection enables discovery |

GraphQL supplements REST — it does not replace it. REST remains the primary API surface for V1 and V2.

---

## Schema Design

### Root Types

```graphql
type Query {
    # Entities
    entities(filter: EntityFilter, page: Int, perPage: Int): EntityConnection!
    entity(id: ID!): Entity

    # Evidence
    evidence(filter: EvidenceFilter, page: Int, perPage: Int): EvidenceConnection!
    evidenceNode(id: ID!): EvidenceNode

    # Insights
    insights(filter: InsightFilter, page: Int, perPage: Int): InsightConnection!
    insight(id: ID!): Insight

    # Graph Traversal
    traverse(from: ID!, relationship: RelationshipType!, depth: Int = 1): [GraphNode!]!
    path(from: ID!, to: ID!, maxDepth: Int = 5): [GraphEdge!]!

    # Search
    search(q: String!, types: [SearchableType!]): SearchResultConnection!

    # Health
    health: ServiceHealth!
}

type Mutation {
    # Insight lifecycle
    updateInsightStatus(id: ID!, status: InsightStatus!): Insight!

    # Analysis
    runAnalysis(input: AnalysisInput!): AnalysisJob!
    cancelAnalysis(jobId: ID!): Boolean!

    # Reasoning
    askQuestion(input: QuestionInput!): Insight!
}

type Subscription {
    # Real-time events
    insightCreated(entityIds: [ID!]): Insight!
    evidenceAdded(entityIds: [ID!]): EvidenceNode!
    analysisProgress(jobId: ID!): AnalysisProgress!
    alertTriggered(severity: [Severity!]): Alert!
}
```

### Core Types

```graphql
type Entity {
    id: ID!
    name: String!
    type: EntityType!
    aliases: [String!]
    path: String
    evidence(engine: String, type: String): [EvidenceNode!]
    insights(status: InsightStatus): [Insight!]
    relationships(type: RelationshipType): [Relationship!]
    metrics: EntityMetrics
    metadata: EntityMetadata!
}

type EvidenceNode {
    id: ID!
    type: String!
    category: EvidenceCategory!
    engine: String!
    version: String!
    severity: Severity!
    confidence: Float!
    value: JSON!
    timestamp: DateTime!
    source: EvidenceSource!
    rawData: RawDataReference
    affectedEntities: [Entity!]
    insightsUsing: [Insight!]
}

type Insight {
    id: ID!
    type: InsightType!
    title: String!
    summary: String!
    detailedExplanation: String
    confidence: Float!
    severity: Severity!
    status: InsightStatus!
    evidenceChain: EvidenceChain!
    recommendations: [Recommendation!]
    entities: [Entity!]
    createdAt: DateTime!
    expiresAt: DateTime
}
```

### Graph Traversal Types

GraphQL's strength is traversing relationships in a single query:

```graphql
type Relationship {
    type: RelationshipType!
    source: GraphNode!
    target: GraphNode!
    properties: JSON
}

union GraphNode = Entity | EvidenceNode | Insight

type GraphEdge {
    type: RelationshipType!
    from: GraphNode!
    to: GraphNode!
}
```

---

## Example Queries

### Entity with All Related Data

```graphql
{
    entity(id: "mod_auth_001") {
        name
        type
        evidence(engine: "trace_cognition") {
            id
            type
            value
            confidence
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
        relationships(type: DEPENDS_ON) {
            target {
                ... on Entity { id name type }
            }
        }
    }
}
```

**REST equivalent:** 4 separate requests (`GET /v1/entities/{id}`, `GET /v1/evidence?entity_id=mod_auth_001`, `GET /v1/insights?entity_id=mod_auth_001`, `GET /v1/entities/{id}/relationships`). GraphQL does it in one.

### Insight with Full Evidence Chain

```graphql
{
    insight(id: "insight_synth_001") {
        title
        confidence
        evidenceChain {
            insight { id title }
            supportingEvidence {
                evidence {
                    id
                    type
                    value
                    confidence
                    source { file line }
                }
                supports
                derivedFrom {
                    rawDataRef
                    confidence
                }
            }
        }
    }
}
```

### Cross-Module Impact Analysis

```graphql
{
    traverse(from: "mod_auth_001", relationship: DEPENDS_ON, depth: 2) {
        ... on Entity {
            id
            name
            type
            insights(severity: HIGH) {
                title
                summary
            }
        }
    }
}
```

### Search Across All Types

```graphql
{
    search(q: "auth failure", types: [ENTITY, INSIGHT]) {
        nodes {
            ... on Entity { id name type }
            ... on Insight { id title summary confidence }
        }
        totalCount
    }
}
```

---

## Mutations

Mutations follow the same semantics as their REST counterparts but return the modified object directly:

```graphql
mutation {
    updateInsightStatus(id: "insight_synth_001", status: ACKNOWLEDGED) {
        id
        status
        title
    }
}
```

```graphql
mutation {
    askQuestion(input: {
        question: "What is causing auth failures?",
        entities: ["auth"],
        mode: INTERACTIVE
    }) {
        id
        title
        summary
        confidence
        evidenceChain { ... }
        recommendations { action effortEstimate risk }
    }
}
```

---

## Subscriptions

GraphQL subscriptions use WebSocket transport (built on the same WebSocket infrastructure as Phase 6/04).

```graphql
subscription {
    insightCreated(entityIds: ["mod_auth_001"]) {
        id
        title
        severity
        confidence
    }
}
```

```graphql
subscription {
    analysisProgress(jobId: "job_046") {
        progress
        currentStage
        stagesCompleted
        evidenceProduced
    }
}
```

---

## Performance Considerations

### N+1 Prevention

GraphQL resolvers use DataLoader-style batching to prevent N+1 queries:

```
Query: entity(id: "mod_auth_001") { evidence { ... } }
→ Single SCM query: "SELECT * FROM evidence WHERE entity_id = 'mod_auth_001'"
NOT: N queries for each evidence item.
```

### Depth Limiting

Maximum query depth: 5 levels. Prevents abusive deeply-nested queries.

```
Query with depth 6 → 400 Bad Request: "Maximum query depth exceeded (max: 5)."
```

### Complexity Scoring

Each field has a cost. Queries with total cost exceeding a threshold are rejected:

| Field | Cost |
|---|---|
| Scalar field (id, name) | 1 |
| List field (evidence, insights) | 5 + per-item cost |
| Traversal (traverse, path) | 10 + per-node cost |

Default max cost per query: 500. Configurable.

### Pagination

List fields use cursor-based pagination (Relay spec) for consistency:

```graphql
{
    entities(first: 20, after: "cursor") {
        edges {
            node { id name type }
            cursor
        }
        pageInfo { hasNextPage endCursor }
        totalCount
    }
}
```

---

## Security

GraphQL shares the same authentication and authorization infrastructure as REST (Phase 6/05, 6/06):

- **Local mode:** No auth. Introspection enabled. All queries allowed.
- **Network mode:** Auth required. Introspection disabled by default. Queries scoped to authorized resources.

Rate limiting is applied per client, shared with REST rate limits.

---

## Edge Cases

### Deeply Nested Circular References

The SCM graph can contain cycles (e.g., two modules depend on each other). The traversal resolver detects cycles and returns nodes at first visit only — subsequent visits through different paths return a reference stub rather than re-expanding the node.

### Introspection in Production

In network mode, introspection is disabled by default to avoid schema exposure. It can be enabled via configuration for internal tooling.

### Partial Failure

If a resolver fails (e.g., SCM query times out for one field), GraphQL returns partial data with an `errors` array for the failed field. The rest of the query succeeds.

---

## Future Work

### Federation (V3)

When services are split into separate processes, use Apollo Federation to compose the GraphQL schema from multiple subgraphs (SCM Graph, Reasoning Graph, Analysis Graph).

### Persisted Queries (V3)

For performance-critical queries, register persisted queries at deploy time. Clients send a hash instead of the full query string, reducing request size and preventing arbitrary query execution.

### Live Queries (V3)

Replace polling patterns with live queries that push updates when the underlying data changes. Combines query semantics with subscription freshness.
