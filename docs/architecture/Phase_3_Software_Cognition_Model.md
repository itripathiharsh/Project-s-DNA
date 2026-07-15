================================================================================
# 01 SCM Overview
================================================================================

# Software Cognition Model (SCM) â€” Overview

## The Brain of Project DNA

The Software Cognition Model (SCM) is the unified, queryable, evolving representation of a software system. It is not a database. It is not a graph. It is a **living model of understanding** that captures what software is, how it became that way, who understands it, and where it is heading.

Every other layer of Project DNA exists to populate, query, or present the SCM. The Cognitive Engines perceive and write to it. The Reasoning Layer reads from it and writes insights back to it. The UI queries it. The API exposes it.

This document is the foundation. Subsequent documents in this phase detail each sub-model.

---

## What the SCM Is

The SCM is a **multi-model data structure** that integrates:

| Dimension | What It Captures | Analogy |
|---|---|---|
| **Structure** | Files, functions, classes, modules, dependencies, calls, inheritance | The skeleton |
| **Evolution** | Commits, changes, growth, refactoring, drift, trends | The medical history |
| **Knowledge** | Who understands what, expertise distribution, bus factor, onboarding difficulty | The nervous system |
| **Dependencies** | Internal modules, external packages, versions, vulnerabilities, blast radius | The circulatory system |
| **Architecture** | Patterns, layers, boundaries, violations, erosion | The anatomy |
| **Evidence** | Deterministic facts, chains of reasoning, confidence levels, sources | The DNA sequence |
| **Insights** | Conclusions drawn from evidence, with explanations and recommendations | The diagnosis |

These dimensions are not separate databases. They are **interconnected facets of a single model**. A change in one dimension propagates understanding to the others.

---

## What the SCM Is Not

| The SCM Is Not | Why Not |
|---|---|
| A relational database | Tables isolate data. The SCM connects it. |
| A document store | Documents are unstructured. The SCM is rigorously structured. |
| A graph database | Graphs capture relationships but lack temporal and evidence dimensions natively. |
| A cache | Caches are ephemeral. The SCM is persistent and versioned. |
| A data warehouse | Warehouses store historical snapshots. The SCM stores living understanding. |
| A knowledge graph | Knowledge graphs capture facts. The SCM captures meaning, causation, and uncertainty. |

The SCM uses elements of all of these â€” relational storage, graph structures, document flexibility, temporal versioning â€” but it is **greater than the sum of its parts** because of how they are integrated.

---

## The Four Pillars of the SCM

The SCM is organized around four foundational pillars that mirror the four pillars of cognition (see Phase -1: What Is Cognition):

### Pillar 1: Perception Store
**What:** All raw and processed data from the Cognitive Engines.
**Contains:** ASTs, dependency graphs, commit histories, metric values, ownership maps.
**Nature:** Deterministic, verifiable, timestamped.

### Pillar 2: Representation Store
**What:** The unified model of entities and relationships.
**Contains:** Nodes (files, functions, modules, commits, authors, packages), edges (dependencies, ownership, co-changes, calls, contains), properties (metrics, timestamps, confidence).
**Nature:** Graph-structured, queryable, navigable.

### Pillar 3: Reasoning Store
**What:** Insights, predictions, recommendations, and their supporting evidence.
**Contains:** Insight nodes, evidence chains, confidence scores, causal explanations, decision evaluations.
**Nature:** Probabilistic where appropriate, always evidence-bound.

### Pillar 4: Temporal Store
**What:** The history of the model itself â€” how understanding has evolved.
**Contains:** Snapshots of the SCM at points in time, trend data, event annotations, prediction accuracy tracking.
**Nature:** Immutable append-only, enabling time travel and trend analysis.

---

## SCM Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                         SCM Query Interface                        â”‚
â”‚  (GraphQL-like traversal, time-range queries, evidence retrieval)    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚  â”‚ Perception  â”‚  â”‚Representationâ”‚  â”‚  Reasoning  â”‚  â”‚ Temporal â”‚ â”‚
â”‚  â”‚   Store     â”‚  â”‚    Store     â”‚  â”‚    Store    â”‚  â”‚  Store   â”‚ â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                      Unified Storage Backend                         â”‚
â”‚  (SQLite default / PostgreSQL V2+ / Graph operations in-memory)      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                      Persistence Layer                               â”‚
â”‚  (ACID transactions, versioning, export, backup)                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Core Concepts

### Entity
Anything that exists in the software system or its history.

**Examples:** File, Function, Class, Module, Service, Commit, Author, Package, Vulnerability, Insight.

**Properties:**
- `id`: Unique identifier (UUID).
- `type`: Entity type (from taxonomy).
- `name`: Human-readable name.
- `created_at`: When first perceived.
- `updated_at`: When last modified.
- `version`: Incremental version for optimistic locking.

### Relationship
A directed connection between two entities with a typed meaning.

**Examples:** `File CONTAINS Function`, `Module DEPENDS_ON Module`, `Author OWNS File`, `Commit MODIFIES File`, `Insight SUPPORTED_BY Evidence`.

**Properties:**
- `source_id`: Origin entity.
- `target_id`: Destination entity.
- `type`: Relationship type (from taxonomy).
- `properties`: Weight, confidence, timestamp, metadata.
- `valid_from` / `valid_to`: Temporal validity (null = current).

### Evidence
A deterministic, verifiable fact that supports a conclusion.

**Properties:**
- `id`: Unique identifier.
- `type`: Evidence category (structural, historical, metric, ownership, etc.).
- `value`: Structured data (JSON, numbers, booleans, references).
- `source`: Which Cognitive Engine produced it.
- `raw_data_ref`: Pointer to raw data (commit hash, file path, line range).
- `confidence`: Certain, High, Medium, Low, Speculative.
- `timestamp`: When produced.
- `engine_version`: Version of the producing engine.

### Evidence Chain
A linked sequence from raw data through intermediate evidence to an insight.

**Structure:**
```
Insight: "PaymentService is a bottleneck"
  â† SUPPORTED_BY Evidence: "Complexity increased 133% in 6 months"
    â† DERIVED_FROM Evidence: "Cyclomatic complexity rose from 12 to 28"
      â† DERIVED_FROM Evidence: "AST analysis of PaymentService.java"
        â† RAW_DATA: "Source code of PaymentService.java at commit abc123"
```

### Snapshot
A complete or partial capture of the SCM at a specific point in time.

**Types:**
- **Full Snapshot:** Complete SCM state. Taken on first analysis and on demand.
- **Incremental Snapshot:** Changes since last snapshot. Taken on every commit.
- **Entity Snapshot:** State of a single entity over time.

### Insight
A conclusion drawn from evidence by the Cognitive Reasoning Layer.

**Properties:**
- `id`: Unique identifier.
- `type`: Risk, Opportunity, Change, Prediction, Decision.
- `title`: Human-readable summary.
- `description`: Detailed explanation.
- `severity`: Critical, High, Medium, Low, Info.
- `confidence`: 0.0 to 1.0.
- `evidence_chain`: Linked evidence nodes.
- `recommendation`: Suggested action (optional).
- `affected_entities`: List of entity IDs.
- `created_at`: When generated.
- `expires_at`: When insight should be re-evaluated (optional).
- `status`: Active, Acknowledged, Resolved, Dismissed.

---

## Entity Taxonomy

The SCM defines a strict taxonomy of entity types. Every entity must have a type from this taxonomy.

### Code Entities
| Type | Description | Example |
|---|---|---|
| `Repository` | Root container | "my-project" |
| `Module` | Logical grouping (package, namespace) | "payment-service" |
| `File` | Source file | "PaymentService.java" |
| `Class` | Class or interface | "PaymentProcessor" |
| `Function` | Method or function | "processPayment()" |
| `Variable` | Variable or constant | "MAX_RETRY_COUNT" |
| `Import` | Import or include statement | "import com.stripe.Stripe;" |

### History Entities
| Type | Description | Example |
|---|---|---|
| `Commit` | Git commit | "abc1234" |
| `Branch` | Git branch | "feature/payment-refactor" |
| `Tag` | Git tag | "v2.1.0" |
| `PullRequest` | Pull request (V2+) | "PR #412" |
| `Release` | Software release | "v2.1.0" |

### People Entities
| Type | Description | Example |
|---|---|---|
| `Author` | Person who committed code | "Sarah Chen" |
| `Reviewer` | Person who reviewed code (V2+) | "Marcus Johnson" |
| `Team` | Engineering team (V2+) | "Platform Team" |

### Dependency Entities
| Type | Description | Example |
|---|---|---|
| `Package` | External dependency | "stripe-python 5.2.0" |
| `Vulnerability` | Known CVE | "CVE-2024-1234" |
| `License` | Software license | "MIT" |

### Understanding Entities
| Type | Description | Example |
|---|---|---|
| `Pattern` | Detected architectural pattern | "Clean Architecture" |
| `Boundary` | Architectural boundary | "Payment Domain Boundary" |
| `Violation` | Boundary or rule violation | "Database access from Controller" |
| `Metric` | Calculated metric value | "Cyclomatic Complexity: 28" |
| `Trend` | Temporal trend | "Complexity increasing 5% per month" |

### Reasoning Entities
| Type | Description | Example |
|---|---|---|
| `Insight` | Generated conclusion | "PaymentService is a bottleneck" |
| `Recommendation` | Suggested action | "Refactor PaymentService within 30 days" |
| `Decision` | Evaluated decision | "Split PaymentService: Confidence 76%" |
| `Prediction` | Forecast | "Complexity will reach 40 in 6 months" |

---

## Relationship Taxonomy

### Structural Relationships
| Type | Source | Target | Meaning |
|---|---|---|---|
| `CONTAINS` | Module / File / Class | File / Class / Function | Parent-child containment |
| `DEPENDS_ON` | Module / File / Function | Module / File / Function | Code dependency |
| `CALLS` | Function | Function | Function call |
| `INHERITS_FROM` | Class | Class | Inheritance |
| `IMPLEMENTS` | Class | Interface | Interface implementation |
| `IMPORTS` | File | Package / Module | External import |

### Historical Relationships
| Type | Source | Target | Meaning |
|---|---|---|---|
| `MODIFIES` | Commit | File / Function | Code change |
| `AUTHORED_BY` | Commit | Author | Commit ownership |
| `MERGES` | Commit | Commit | Merge relationship |
| `TAGS` | Tag | Commit | Tag association |

### Knowledge Relationships
| Type | Source | Target | Meaning |
|---|---|---|---|
| `OWNS` | Author | Module / File | Primary responsibility |
| `CONTRIBUTES_TO` | Author | Module / File | Secondary contribution |
| `REVIEWS` | Reviewer | Commit / PR | Review participation |
| `HAS_EXPERTISE_IN` | Author | Module / Pattern | Expertise claim |

### Dependency Relationships
| Type | Source | Target | Meaning |
|---|---|---|---|
| `USES_PACKAGE` | Module / Repository | Package | External dependency |
| `HAS_VULNERABILITY` | Package | Vulnerability | Security risk |
| `REQUIRES_LICENSE` | Package | License | License obligation |

### Reasoning Relationships
| Type | Source | Target | Meaning |
|---|---|---|---|
| `SUPPORTED_BY` | Insight | Evidence | Evidence support |
| `DERIVED_FROM` | Evidence | Evidence / Raw Data | Derivation |
| `AFFECTS` | Insight | Entity | Impact scope |
| `RECOMMENDS` | Insight | Recommendation | Action suggestion |
| `CONTRADICTS` | Insight | Insight | Conflict |
| `SUPERSEDES` | Insight | Insight | Replacement |

---

## SCM Properties

### Immutable Evidence
Once evidence is stored, it is never modified. New evidence supersedes old evidence through the `SUPERSEDES` relationship. This ensures:
- Auditability: Historical conclusions remain valid.
- Reproducibility: Past analysis can be replayed.
- Trust: Evidence cannot be silently altered.

### Temporal Versioning
Every entity and relationship can be queried at any point in time:
- "What did the dependency graph look like 6 months ago?"
- "Who owned PaymentService before Sarah?"
- "When did this boundary violation first appear?"

### Confidence Propagation
Confidence flows through evidence chains:
- An insight's confidence is bounded by the lowest confidence in its evidence chain.
- Low-confidence evidence must be explicitly acknowledged.
- Users can see exactly which evidence is weak and why.

### Incremental Updates
The SCM updates incrementally:
- New commits trigger delta updates, not full rebuilds.
- Changed files trigger re-analysis of affected entities only.
- Downstream effects are computed lazily or on-demand.

### Queryability
The SCM supports:
- **Graph traversal:** "Find all modules that depend on PaymentService, transitively."
- **Pattern matching:** "Find all files with complexity > 20 that changed in the last month."
- **Temporal queries:** "Show me the ownership evolution of this module."
- **Evidence retrieval:** "Show me all evidence for this insight."
- **Full-text search:** "Find all insights mentioning 'refactor'."

---

## SCM Lifecycle

```
[Empty] â†’ [Initializing] â†’ [Populating] â†’ [Active] â†’ [Updating] â†’ [Active] â†’ ...
                                              â†“
                                         [Archiving] â†’ [Archived]
```

### States
| State | Description |
|---|---|
| **Empty** | No data. Repository not yet analyzed. |
| **Initializing** | Schema created, awaiting first analysis. |
| **Populating** | First analysis in progress. |
| **Active** | Normal operation. Incremental updates on commits. |
| **Updating** | Incremental analysis in progress. |
| **Archiving** | Preparing for long-term storage. |
| **Archived** | Read-only. Historical reference. |

---

## The SCM Doctrine

> **The Software Cognition Model is not a database of facts about software. It is a living representation of understanding. It captures not just what software is, but what it means, how it became that way, who understands it, and where it is heading. Every entity, relationship, and insight serves the north star: Understand Software. Completely.**



================================================================================
# 02 Graph Model
================================================================================

# SCM Graph Model

## The Structure of Understanding

This document defines the graph component of the SCM â€” how entities and relationships are structured, stored, queried, and traversed. The graph is the connective tissue of the SCM. Without it, the SCM is a collection of isolated facts. With it, the SCM is a unified model of meaning.

---

## Graph Design Principles

1. **Property Graph.** Nodes and edges have typed properties. Not a pure RDF triple store.
2. **Directed Edges.** Relationships have direction. Some are bidirectional in meaning but stored as two directed edges.
3. **Temporal Edges.** Edges can be valid for a time range. Historical relationships are first-class.
4. **Multi-Graph.** Multiple edges of the same type can exist between the same nodes (e.g., two commits modifying the same file at different times).
5. **Typed Schema.** Node and edge types are from strict taxonomies. No ad-hoc types.

---

## Graph Schema

### Node Structure
```
Node {
  id: UUID
  type: EntityType (from taxonomy)
  name: string
  properties: JSONB
  created_at: timestamp
  updated_at: timestamp
  version: integer
  snapshot_ids: UUID[]  // Which snapshots include this node
}
```

### Edge Structure
```
Edge {
  id: UUID
  source_id: UUID (Node)
  target_id: UUID (Node)
  type: RelationshipType (from taxonomy)
  properties: JSONB
  valid_from: timestamp (nullable)
  valid_to: timestamp (nullable)
  created_at: timestamp
  confidence: float (0.0-1.0)
}
```

---

## Graph Storage

### V1: Hybrid Storage

**In-Memory Graph:**
- Library: NetworkX (Python) / petgraph (Rust).
- Holds active subgraphs for fast traversal.
- Loaded on demand, evicted by LRU policy.

**Persistent Storage:**
- Backend: SQLite (default) / PostgreSQL (V2+).
- Tables: `nodes`, `edges`, `node_properties`, `edge_properties`.
- Indices: `nodes(type, name)`, `edges(source_id, type)`, `edges(target_id, type)`, `edges(valid_from, valid_to)`.

**Synchronization:**
- Write-through: Changes written to DB immediately, cache invalidated.
- Read: Check cache first, load from DB on miss.
- Batch loading: Load connected subgraphs in batches to minimize round-trips.

### Graph Partitioning

For large repositories (>1M LOC), the graph is partitioned:
- **By Module:** Each module's subgraph is a partition.
- **By Time:** Historical snapshots are archived partitions.
- **Cross-Partition Edges:** Stored in a separate `cross_partition_edges` table.

---

## Graph Operations

### Core Operations

| Operation | Description | Complexity | Implementation |
|---|---|---|---|
| `get_node(id)` | Retrieve node by ID | O(1) | Hash map lookup |
| `get_neighbors(id, type)` | Get connected nodes | O(k) where k = degree | Adjacency list |
| `traverse(start, depth, filters)` | BFS/DFS traversal | O(V+E) in subgraph | NetworkX BFS |
| `shortest_path(a, b)` | Shortest path between nodes | O(V+E) | NetworkX shortest_path |
| `find_cycles()` | Detect circular dependencies | O(V+E) | NetworkX cycle_basis |
| `subgraph(center, radius)` | Extract neighborhood | O(V+E) in radius | BFS + induced subgraph |
| `temporal_query(time)` | Query graph at specific time | O(E) with time filter | Time-indexed edges |

### Advanced Operations

| Operation | Description | Use Case |
|---|---|---|
| `centrality(type)` | PageRank or betweenness centrality | Identify critical modules |
| `community_detection()` | Detect clusters/modules | Validate architecture boundaries |
| `similarity(a, b)` | Structural similarity of subgraphs | Compare module structures |
| `pattern_match(template)` | Find subgraphs matching pattern | Detect architectural patterns |
| `evolution(start, end)` | Graph diff between two times | Track architectural drift |

---

## Temporal Graph Queries

The graph supports time-travel queries:

```
// What did the dependency graph look like on March 1, 2024?
graph.at("2024-03-01T00:00:00Z").subgraph("PaymentService", radius=2)

// When did the edge between A and B first appear?
graph.edges_between(A, B).order_by(valid_from).first()

// How has the ownership of PaymentService changed?
graph.node("PaymentService").edges(type="OWNS").order_by(valid_from)

// Which dependencies existed in January but not in February?
graph.diff(start="2024-01-01", end="2024-02-01").edges(type="DEPENDS_ON")
```

---

## Graph Visualization

The graph model supports visualization at multiple levels:

### Level 1: Module Graph
- Nodes: Modules.
- Edges: Dependencies.
- Node size: Complexity.
- Node color: Health (green/yellow/red).
- Edge thickness: Coupling strength.

### Level 2: File Graph
- Nodes: Files.
- Edges: Imports, calls.
- Used for: Dependency analysis, circular dependency detection.

### Level 3: Function Graph
- Nodes: Functions.
- Edges: Calls.
- Used for: Impact analysis, refactoring planning.

### Level 4: Knowledge Graph
- Nodes: Authors + Modules.
- Edges: Ownership, contribution.
- Used for: Bus factor analysis, expertise mapping.

---

## Graph Integrity

### Constraints
1. **Type Constraint:** Every node and edge must have a valid type from the taxonomy.
2. **Referential Integrity:** Every edge's source and target must exist.
3. **Temporal Consistency:** `valid_from` <= `valid_to` if both present.
4. **Acyclic Containment:** `CONTAINS` edges must form a DAG (no file contains itself).
5. **Confidence Range:** All confidence values in [0.0, 1.0].

### Validation
- Run on every write.
- Failed validation rejects the write and logs the error.
- Background integrity checks run weekly.

---

## The Graph Model Doctrine

> **The graph is not a visualization. It is the structure of understanding. Every node is a concept. Every edge is a relationship. The graph makes software understandable by making its structure explicit, navigable, and queryable.**



================================================================================
# 03 Time-Series Model
================================================================================

# SCM Time-Series Model

## Time as a First-Class Dimension

This document defines how the SCM stores, queries, and reasons about time. Time is not an afterthought in Project DNA. It is foundational. Software is a process, not a snapshot. The time-series model ensures that every observation, every metric, and every insight includes its temporal context.

---

## Time-Series Design Principles

1. **Immutable Events.** Events (commits, analysis runs, insight generations) are immutable facts. They are never modified, only superseded.
2. **Snapshot Isolation.** The state of the SCM at any point in time can be reconstructed.
3. **Trend Native.** Trends are not computed on demand. They are stored as first-class data.
4. **Event Sourcing.** The history of changes to the SCM is itself stored, enabling replay and audit.

---

## Time-Series Data Types

### Event
A discrete occurrence at a point in time.

```
Event {
  id: UUID
  type: EventType
  timestamp: timestamp
  entity_id: UUID (nullable)
  entity_type: EntityType (nullable)
  properties: JSONB
  source: string (engine or user)
}
```

**Event Types:**
| Type | Description | Example |
|---|---|---|
| `COMMIT` | Code committed | "feat: add payment retry" |
| `ANALYSIS_RUN` | Analysis completed | "Full analysis: 47 insights" |
| `INSIGHT_GENERATED` | New insight created | "PaymentService bottleneck detected" |
| `METRIC_UPDATED` | Metric value changed | "Complexity: 12 â†’ 28" |
| `OWNERSHIP_CHANGED` | Primary owner changed | "PaymentService: Alex â†’ Sarah" |
| `BOUNDARY_VIOLATED` | Architectural boundary crossed | "Controller â†’ Database direct access" |
| `REFACTORING_DETECTED` | Refactoring identified | "Extract method in PaymentService" |
| `PREDiction_MADE` | Prediction generated | "Complexity will reach 40 in 6 months" |
| `DECISION_EVALUATED` | Decision analysis completed | "Split PaymentService: 76% confidence" |
| `USER_ACTION` | User interaction | "Sarah dismissed alert #123" |

### Metric Time-Series
A sequence of metric values over time.

```
MetricSeries {
  id: UUID
  metric_name: string
  entity_id: UUID
  entity_type: EntityType
  unit: string (optional)
  aggregation: enum (point, daily, weekly, monthly)
  values: [
    { timestamp, value, evidence_id }
  ]
}
```

**Stored Metrics:**
| Metric | Entity | Unit | Aggregation |
|---|---|---|---|
| `cyclomatic_complexity` | Function / File / Module | integer | point |
| `lines_of_code` | File / Module | integer | point |
| `commit_frequency` | Module | commits/week | weekly |
| `test_coverage` | Module | percentage | point |
| `bus_factor` | Module | integer | point |
| `dependency_count` | Module | integer | point |
| `change_frequency` | File | changes/month | monthly |
| `author_count` | Module | integer | point |
| `refactoring_rate` | Repository | percentage | monthly |
| `velocity` | Team | story points/sprint | sprint |

### Snapshot
A complete or partial capture of SCM state.

```
Snapshot {
  id: UUID
  type: enum (full, incremental, entity)
  timestamp: timestamp
  repository_id: UUID
  commit_hash: string (nullable)
  node_count: integer
  edge_count: integer
  insight_count: integer
  storage_size_bytes: integer
  previous_snapshot_id: UUID (nullable)
  delta: JSONB (changes from previous, for incremental)
}
```

### Trend
A computed trend over a metric series.

```
Trend {
  id: UUID
  metric_series_id: UUID
  trend_type: enum (linear, exponential, seasonal, step)
  direction: enum (increasing, decreasing, stable, volatile)
  slope: float
  intercept: float
  r_squared: float
  prediction_interval: [float, float]
  forecast: [
    { timestamp, predicted_value, confidence_lower, confidence_upper }
  ]
  generated_at: timestamp
}
```

---

## Temporal Query Interface

### Query Patterns

```python
# Get all events for PaymentService in March 2024
events = scm.events(
    entity_id="PaymentService",
    start="2024-03-01",
    end="2024-04-01",
    types=["COMMIT", "METRIC_UPDATED", "INSIGHT_GENERATED"]
)

# Get complexity trend for PaymentService
trend = scm.metric_series(
    metric="cyclomatic_complexity",
    entity_id="PaymentService"
).trend(forecast_days=180)

# Reconstruct SCM state at a specific commit
scm_at_commit = scm.snapshot_at(commit_hash="abc1234")

# Compare two time points
diff = scm.diff(
    start="2024-01-01",
    end="2024-06-01",
    entity_id="PaymentService"
)
# Returns: added_nodes, removed_nodes, changed_properties, new_edges, removed_edges

# Get predictions made and their accuracy
predictions = scm.predictions(
    entity_id="PaymentService",
    status="resolved"  // Check if prediction came true
)
```

---

## Time-Series Storage

### Storage Strategy

**Hot Data (last 90 days):**
- In-memory time-series cache.
- Fast point queries.
- Updated in real-time.

**Warm Data (90 days to 2 years):**
- SQLite/PostgreSQL with time-series indexing.
- Partitioned by month.
- Aggregated views (daily, weekly).

**Cold Data (> 2 years):**
- Compressed snapshots.
- Archived to disk.
- Loaded on demand for historical analysis.

### Indexing

| Index | Purpose |
|---|---|
| `events(timestamp, entity_id)` | Time-range queries for entity |
| `events(type, timestamp)` | Event type filtering |
| `metric_series(entity_id, metric_name, timestamp)` | Metric retrieval |
| `snapshots(repository_id, timestamp)` | Snapshot lookup |
| `trends(metric_series_id, generated_at)` | Trend retrieval |

---

## The Time-Series Doctrine

> **Software without history is incomprehensible. The time-series model ensures that every observation carries its temporal context â€” how we got here, where we are going, and when things changed. Time is not metadata. It is meaning.**



================================================================================
# 04 Evidence Model
================================================================================

# SCM Evidence Model

## The Foundation of Trust

This document defines how evidence is structured, stored, validated, and traced in the SCM. Evidence is the bedrock of Project DNA. Every insight, every recommendation, every prediction must be grounded in evidence. Without evidence, there is no understanding â€” only opinion.

---

## Evidence Design Principles

1. **Deterministic First.** Evidence is produced by deterministic engines. AI synthesizes, never invents.
2. **Immutable.** Evidence never changes. New evidence supersedes old.
3. **Traceable.** Every evidence item links to raw data.
4. **Confidence-Scored.** Every evidence item carries a confidence level.
5. **Structured.** Evidence is typed data, not free text.

---

## Evidence Structure

### Evidence Node
```
Evidence {
  id: UUID
  type: EvidenceType
  category: EvidenceCategory
  value: JSONB
  confidence: ConfidenceLevel
  source: {
    engine: string
    version: string
    timestamp: timestamp
  }
  raw_data: {
    type: RawDataType
    ref: string (commit hash, file path, line range)
    content_hash: string (for verification)
  }
  derivation: {
    method: string (algorithm name)
    inputs: UUID[] (parent evidence IDs)
    parameters: JSONB
  }
  validation: {
    status: enum (pending, valid, invalid, disputed)
    validated_by: UUID (engine or user)
    validated_at: timestamp
    notes: string
  }
  created_at: timestamp
}
```

### Evidence Types

| Type | Description | Example Value |
|---|---|---|
| `ast_node_count` | Count of AST nodes | `{"count": 47, "language": "python"}` |
| `cyclomatic_complexity` | Complexity metric | `{"value": 28, "method": "mccabe"}` |
| `dependency_graph` | Dependency structure | `{"nodes": [...], "edges": [...]}` |
| `commit_metadata` | Git commit info | `{"hash": "abc123", "author": "sarah", "date": "..."}` |
| `change_frequency` | How often file changes | `{"changes_per_month": 12.5}` |
| `author_contribution` | Author's share of commits | `{"author": "alex", "percentage": 0.73}` |
| `pattern_match` | Detected architectural pattern | `{"pattern": "Clean Architecture", "confidence": 0.89}` |
| `boundary_violation` | Architectural rule break | `{"rule": "no-db-in-controller", "file": "..."}` |
| `metric_trend` | Trend over time | `{"slope": 2.3, "r_squared": 0.94}` |
| `vulnerability_scan` | Security finding | `{"cve": "CVE-2024-1234", "severity": "high"}` |

### Evidence Categories

| Category | Description | Producing Engines |
|---|---|---|
| `structural` | Code structure facts | Structural Cognition |
| `historical` | Git history facts | Evolution Cognition |
| `metric` | Computed measurements | Structural, Evolution Cognition |
| `ownership` | Who knows what | Knowledge Cognition |
| `dependency` | Internal/external dependencies | Dependency Cognition |
| `architectural` | Patterns, boundaries, violations | Architectural Cognition |
| `behavioral` | Runtime behavior (V3+) | Operational Cognition |
| `cross_dimensional` | Combined evidence | Multiple engines |

### Confidence Levels

| Level | Numeric Range | Meaning | Example |
|---|---|---|---|
| `certain` | 1.0 | Directly observable, no inference | "File X has 500 lines" |
| `high` | 0.85-0.99 | Strong inference, multiple sources | "Module Y is tightly coupled" |
| `medium` | 0.60-0.84 | Reasonable inference, limited data | "Refactoring occurred" |
| `low` | 0.30-0.59 | Weak inference, high uncertainty | "Expert on Module V" |
| `speculative` | 0.0-0.29 | Hypothesis, needs validation | "Will become unstable in 3 months" |

---

## Evidence Chain

An evidence chain is a directed acyclic graph (DAG) from raw data to insight.

```
Insight: "PaymentService is a maintenance bottleneck"
  â† SUPPORTED_BY [Evidence E1] "Complexity increased 133% in 6 months"
    â† DERIVED_FROM [Evidence E2] "Cyclomatic complexity: 12 â†’ 28"
      â† DERIVED_FROM [Evidence E3] "AST analysis of PaymentService.java"
        â† RAW_DATA [Commit abc123] "Source code at commit abc123"
    â† DERIVED_FROM [Evidence E4] "Change frequency: 4x average"
      â† DERIVED_FROM [Evidence E5] "Commit history analysis"
        â† RAW_DATA [Git log] "Commits to PaymentService.java"
  â† SUPPORTED_BY [Evidence E6] "Bus factor = 1"
    â† DERIVED_FROM [Evidence E7] "Author contribution: Alex 73%"
      â† RAW_DATA [Git log] "Author statistics"
```

### Chain Properties
- **Acyclic:** No circular reasoning.
- **Connected:** Every insight has at least one chain.
- **Complete:** Every node in the chain is inspectable.
- **Confidence-Propagated:** The insight's confidence is the minimum confidence along its primary chain.

---

## Evidence Validation

### Automated Validation
- **Reproducibility:** Re-run engine on same input â†’ same evidence.
- **Consistency:** Evidence from different engines should not contradict without explanation.
- **Freshness:** Evidence timestamp must be >= raw data timestamp.
- **Completeness:** Required fields present and valid.

### Manual Validation
- Users can flag evidence as incorrect or incomplete.
- Flagged evidence triggers re-analysis.
- Disputed evidence is marked and excluded from new insights until resolved.

---

## Evidence Storage

### Storage Format
- Evidence nodes: JSONB in relational store.
- Evidence chains: Edge table linking evidence nodes.
- Raw data: Stored by reference (commit hash, file hash) not by content to avoid duplication.
- Content verification: SHA-256 hash of raw data for integrity.

### Retention
- **Active evidence:** Last 90 days. Hot storage.
- **Historical evidence:** 90 days to 2 years. Warm storage.
- **Archived evidence:** > 2 years. Compressed, load on demand.
- **Superseded evidence:** Retained for audit, marked inactive.

---

## The Evidence Doctrine

> **Evidence is the currency of understanding. Every claim must be paid for with evidence. Every evidence must be traceable to its source. Every source must be verifiable. This is what makes Project DNA trustworthy where other tools are merely suggestive.**



================================================================================
# 05 Knowledge Model
================================================================================

# SCM Knowledge Model

## Understanding Who Understands

This document defines how the SCM represents knowledge â€” who understands what, how well, where expertise is concentrated, and where it is missing. Knowledge is as critical to software understanding as code structure. A module with perfect architecture and no knowledgeable owners is still a risk.

---

## Knowledge Design Principles

1. **Knowledge â‰  Activity.** Writing code does not equal understanding code. The model distinguishes between contribution and expertise.
2. **Distributed, Not Centralized.** Knowledge is a property of the relationship between people and code, not a score assigned to individuals.
3. **Temporal.** Expertise evolves. Today's expert may be tomorrow's stranger.
4. **Actionable.** Knowledge maps must reveal risks (bus factor) and opportunities (knowledge transfer).

---

## Knowledge Entities

### Expertise Profile
```
ExpertiseProfile {
  id: UUID
  author_id: UUID
  module_id: UUID
  depth_score: float (0.0-1.0)
  breadth_score: float (0.0-1.0)
  tenure_days: integer
  last_contribution: timestamp
  contribution_count: integer
  review_participation: float (0.0-1.0)
  documentation_authored: integer
  mentoring_events: integer (V2+)
  confidence: ConfidenceLevel
}
```

**Depth Score:** How well the author understands this specific module.
- Derived from: commit complexity, refactoring participation, review depth, documentation quality.

**Breadth Score:** How well the author understands the broader system around this module.
- Derived from: cross-module contributions, architectural decision participation, dependency awareness.

### Ownership
```
Ownership {
  id: UUID
  module_id: UUID
  primary_owner_id: UUID (nullable)
  secondary_owners: UUID[]
  ownership_type: enum (single, shared, orphaned, contested)
  bus_factor: integer
  risk_level: enum (low, medium, high, critical)
  last_evaluated: timestamp
}
```

**Ownership Types:**
| Type | Description | Risk |
|---|---|---|
| `single` | One primary owner | High if bus factor = 1 |
| `shared` | Multiple knowledgeable owners | Low |
| `orphaned` | No active owner | Critical |
| `contested` | Multiple owners disagree | Medium |

### Knowledge Gap
```
KnowledgeGap {
  id: UUID
  module_id: UUID
  gap_type: enum (no_owner, single_owner, outdated_expertise, onboarding_difficulty)
  severity: enum (low, medium, high, critical)
  recommended_action: string
  estimated_resolution_time: string
  created_at: timestamp
  resolved_at: timestamp (nullable)
}
```

---

## Knowledge Metrics

### Bus Factor
The number of engineers who would need to leave before a module becomes unmaintainable.

**Calculation:**
```
bus_factor(module) = count of authors with expertise_depth > 0.5
                     AND last_contribution < 90 days ago
```

**Interpretation:**
| Bus Factor | Risk Level | Action |
|---|---|---|
| 0 | Critical | Immediate knowledge transfer required |
| 1 | High | Pair programming, documentation sprint |
| 2 | Medium | Cross-training recommended |
| 3+ | Low | Healthy knowledge distribution |

### Onboarding Difficulty
How long it takes a new engineer to become productive in a module.

**Factors:**
- Complexity of the module.
- Quality of documentation.
- Availability of knowledgeable owners.
- Test coverage.
- Architectural clarity.

**Score:** Estimated days to first meaningful contribution (with and without Project DNA).

### Knowledge Concentration
The distribution of expertise across the team.

**Gini Coefficient for Knowledge:**
- 0.0 = Perfectly distributed (everyone knows everything equally).
- 1.0 = Perfectly concentrated (one person knows everything).
- Target: < 0.6 for critical modules.

---

## Knowledge Graph

The knowledge model is a bipartite graph connecting authors to modules.

```
Author --[HAS_EXPERTISE_IN {depth, breadth, confidence}]--> Module
Author --[CONTRIBUTES_TO {frequency, recency}]--> Module
Author --[MENTORS {topic}]--> Author (V2+)
Module --[REQUIRES_KNOWLEDGE_OF]--> Module (dependency-based knowledge transfer)
```

### Graph Queries
```python
# Who can review changes to PaymentService?
reviewers = scm.knowledge_graph
    .neighbors("PaymentService", edge_type="HAS_EXPERTISE_IN")
    .filter(depth > 0.6)
    .exclude(author == current_author)

# What modules are at risk if Alex leaves?
at_risk = scm.knowledge_graph
    .neighbors("Alex", edge_type="HAS_EXPERTISE_IN")
    .filter(depth > 0.7)
    .where(module.bus_factor == 1)

# What is the shortest knowledge transfer path?
path = scm.knowledge_graph
    .shortest_path("NewEngineer", "PaymentService", 
                   edge_type="HAS_EXPERTISE_IN", 
                   weight="mentoring_capacity")
```

---

## The Knowledge Model Doctrine

> **Code without knowledge is a liability. The knowledge model ensures that understanding is visible, distributed, and preserved. It answers not just what the software is, but who understands it â€” and what happens when they don't.**



================================================================================
# 06 Query Interface
================================================================================

# SCM Query Interface

## Asking Questions of Understanding

This document defines how the SCM is queried â€” the interface between the model and its consumers (Cognitive Engines, Reasoning Layer, UI, API). The query interface is the voice of the SCM. It must be expressive enough to capture complex questions and fast enough to answer them interactively.

---

## Query Design Principles

1. **Graph-Native.** Queries traverse relationships naturally.
2. **Temporal-Aware.** Every query can include a time dimension.
3. **Evidence-Bound.** Query results include evidence references, not just values.
4. **Composable.** Complex queries built from simple ones.
5. **Optimized.** Common queries are pre-computed and cached.

---

## Query Types

### 1. Entity Queries
Retrieve entities by properties.

```python
# Find all modules with complexity > 20
modules = scm.query()
    .entities(type="Module")
    .where("cyclomatic_complexity", ">", 20)
    .execute()

# Find PaymentService
payment = scm.query()
    .entities(type="Module")
    .where("name", "=", "PaymentService")
    .at_time("2024-06-01")
    .execute()
```

### 2. Relationship Queries
Traverse the graph.

```python
# What depends on PaymentService?
dependents = scm.query()
    .from_entity("PaymentService")
    .traverse(edge_type="DEPENDS_ON", direction="incoming")
    .depth(3)
    .execute()

# Who owns PaymentService?
owners = scm.query()
    .from_entity("PaymentService")
    .traverse(edge_type="OWNS")
    .execute()
```

### 3. Temporal Queries
Query history and trends.

```python
# How has PaymentService complexity changed?
trend = scm.query()
    .entity("PaymentService")
    .metric("cyclomatic_complexity")
    .range("2024-01-01", "2024-06-01")
    .aggregation("weekly")
    .execute()

# What did the architecture look like in January?
arch = scm.query()
    .entities(type="Module")
    .at_time("2024-01-15")
    .execute()
```

### 4. Evidence Queries
Retrieve evidence and chains.

```python
# Show me all evidence for this insight
evidence = scm.query()
    .from_entity(insight_id)
    .traverse(edge_type="SUPPORTED_BY")
    .depth(-1)  # All the way to raw data
    .execute()

# What insights are supported by this commit?
insights = scm.query()
    .from_entity(commit_hash)
    .traverse(edge_type="SUPPORTED_BY", direction="incoming")
    .execute()
```

### 5. Pattern Queries
Find subgraphs matching a pattern.

```python
# Find all god classes (large, many dependencies, central)
god_classes = scm.query()
    .pattern()
    .node(type="Class", complexity=">", 50)
    .outgoing(edge_type="DEPENDS_ON", count=">", 10)
    .incoming(edge_type="DEPENDS_ON", count=">", 10)
    .execute()

# Find knowledge silos (high complexity, single owner)
silos = scm.query()
    .pattern()
    .node(type="Module", complexity=">", 30)
    .outgoing(edge_type="OWNS", count="=", 1)
    .execute()
```

### 6. Aggregate Queries
Compute statistics over sets.

```python
# Average complexity by module
avg_complexity = scm.query()
    .entities(type="Module")
    .aggregate("avg", "cyclomatic_complexity")
    .group_by("layer")
    .execute()

# Bus factor distribution
bus_factor_dist = scm.query()
    .entities(type="Module")
    .aggregate("histogram", "bus_factor")
    .execute()
```

---

## Query Language

The SCM query interface is implemented as a fluent API in Python and a GraphQL-like syntax for the API layer.

### Fluent API (Python)
```python
result = scm.query()
    .entities(type="Module")
    .where("health_score", "<", 40)
    .traverse(edge_type="DEPENDS_ON", depth=2)
    .include_evidence()
    .at_time("2024-06-01")
    .limit(10)
    .execute()
```

### GraphQL-Like Syntax (API)
```graphql
query {
  modules(where: {health_score_lt: 40}) {
    name
    complexity
    owners {
      name
      expertise_depth
    }
    dependencies(depth: 2) {
      name
      health_score
    }
    evidence {
      type
      confidence
      raw_data_ref
    }
  }
}
```

---

## Query Optimization

### Caching Strategy
| Cache Level | Key | TTL | Scope |
|---|---|---|---|
| Query Result | Query hash + repo state | 1 hour | Per-repository |
| Subgraph | Entity ID + depth + filters | 30 min | Cross-query |
| Metric | Metric name + entity ID | 5 min | Per-entity |
| Evidence Chain | Insight ID | Infinite | Immutable |

### Pre-Computation
- Common queries run in background after each analysis.
- Results stored in `precomputed_queries` table.
- Dashboard queries served from pre-computation, not computed on load.

### Indexing
- B-tree indices on `nodes(type, name)`, `edges(source_id, type)`, `events(timestamp)`.
- GIN indices on JSONB properties for flexible filtering.
- Time-series indices on `metric_series(entity_id, metric_name, timestamp)`.

---

## The Query Interface Doctrine

> **The query interface is how understanding is accessed. It must be as natural as asking a colleague a question and as fast as looking up a file. Every query returns not just data, but meaning â€” with evidence, context, and confidence.**



=
---

## SCM Writer Protocol

The SCM Writer is the write-side counterpart to the Query Interface. It defines how Cognitive Engines produce and persist evidence into the SCM. Every engine receives an scm: SCMWriter instance during execution (see Phase 4/01 - Engine Interface Contract).

`python
class SCMWriter(Protocol):
    def write_evidence(self, evidence: EvidenceNode) -> str:
        """Persist a single evidence node. Returns the assigned evidence ID."""
        ...

    def write_evidence_batch(self, evidence: List[EvidenceNode]) -> List[str]:
        """Persist multiple evidence nodes in a single transaction."""
        ...

    def update_entity(self, entity_id: str, properties: dict) -> None:
        """Update entity properties (e.g., latest metric values)."""
        ...

    def create_entity(self, entity: Entity) -> str:
        """Create a new entity in the SCM. Returns entity ID."""
        ...

    def add_relationship(self, source_id: str, target_id: str, rel_type: str, properties: dict = None) -> None:
        """Add a typed relationship between two entities."""
        ...

    def mark_analysis_complete(self, engine_name: str, version: str, summary: dict) -> None:
        """Record that an engine completed its analysis for provenance tracking."""
        ...
`

The SCM Writer ensures all writes are transactional, validated against the evidence schema, and timestamped. Engines never access the storage backend directly - they write through this protocol.
===============================================================================
# 07 SCM Storage
================================================================================

# SCM Storage

## Persisting Understanding

This document defines how the SCM is stored on disk â€” the persistence layer that ensures understanding survives restarts, enables backup and export, and supports querying at scale. Storage is the foundation of durability.

---

## Storage Design Principles

1. **Embedded First.** Default to SQLite for zero-config local deployment.
2. **ACID.** All writes are transactional. No corrupted states.
3. **Versioned.** Schema evolves with migration scripts.
4. **Portable.** Data can be exported, imported, and migrated.
5. **Efficient.** Minimal overhead. Fast reads. Acceptable write speed.

---

## Storage Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              Query Interface                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚  â”‚  Cache  â”‚  â”‚  Index  â”‚  â”‚  Precompute â”‚ â”‚
â”‚  â”‚ (LRU)   â”‚  â”‚ (B-tree â”‚  â”‚  Store      â”‚ â”‚
â”‚  â”‚         â”‚  â”‚  + GIN) â”‚  â”‚             â”‚ â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚              Storage Backend                  â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚  SQLite (default) / PostgreSQL (V2+) â”‚   â”‚
â”‚  â”‚  - nodes, edges, properties          â”‚   â”‚
â”‚  â”‚  - events, metrics, snapshots        â”‚   â”‚
â”‚  â”‚  - evidence, insights, trends        â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚              Persistence Layer                â”‚
â”‚  - WAL (Write-Ahead Logging)                â”‚
â”‚  - Checkpoints                              â”‚
â”‚  - Backup / Export                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Schema (V1 â€” SQLite)

### Core Tables

```sql
-- Nodes (entities)
CREATE TABLE nodes (
    id UUID PRIMARY KEY,
    type VARCHAR(64) NOT NULL,
    name VARCHAR(512) NOT NULL,
    properties JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_nodes_type_name ON nodes(type, name);

-- Edges (relationships)
CREATE TABLE edges (
    id UUID PRIMARY KEY,
    source_id UUID NOT NULL REFERENCES nodes(id),
    target_id UUID NOT NULL REFERENCES nodes(id),
    type VARCHAR(64) NOT NULL,
    properties JSONB NOT NULL DEFAULT '{}',
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT CHECK (confidence >= 0.0 AND confidence <= 1.0)
);
CREATE INDEX idx_edges_source ON edges(source_id, type);
CREATE INDEX idx_edges_target ON edges(target_id, type);
CREATE INDEX idx_edges_temporal ON edges(valid_from, valid_to);

-- Events (time-series)
CREATE TABLE events (
    id UUID PRIMARY KEY,
    type VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    entity_id UUID REFERENCES nodes(id),
    entity_type VARCHAR(64),
    properties JSONB NOT NULL DEFAULT '{}',
    source VARCHAR(128) NOT NULL
);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_entity ON events(entity_id, timestamp);
CREATE INDEX idx_events_type ON events(type, timestamp);

-- Metric Series
CREATE TABLE metric_series (
    id UUID PRIMARY KEY,
    metric_name VARCHAR(128) NOT NULL,
    entity_id UUID NOT NULL REFERENCES nodes(id),
    entity_type VARCHAR(64) NOT NULL,
    unit VARCHAR(32),
    aggregation VARCHAR(32) NOT NULL DEFAULT 'point'
);
CREATE INDEX idx_metric_series_entity ON metric_series(entity_id, metric_name);

-- Metric Values
CREATE TABLE metric_values (
    id UUID PRIMARY KEY,
    series_id UUID NOT NULL REFERENCES metric_series(id),
    timestamp TIMESTAMP NOT NULL,
    value FLOAT NOT NULL,
    evidence_id UUID REFERENCES nodes(id)
);
CREATE INDEX idx_metric_values_series ON metric_values(series_id, timestamp);

-- Snapshots
CREATE TABLE snapshots (
    id UUID PRIMARY KEY,
    type VARCHAR(32) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    repository_id UUID NOT NULL,
    commit_hash VARCHAR(64),
    node_count INTEGER NOT NULL,
    edge_count INTEGER NOT NULL,
    insight_count INTEGER NOT NULL,
    storage_size_bytes INTEGER NOT NULL,
    previous_snapshot_id UUID REFERENCES snapshots(id),
    delta JSONB
);
CREATE INDEX idx_snapshots_repo ON snapshots(repository_id, timestamp);

-- Evidence
CREATE TABLE evidence (
    id UUID PRIMARY KEY,
    type VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL,
    value JSONB NOT NULL,
    confidence VARCHAR(32) NOT NULL,
    source_engine VARCHAR(128) NOT NULL,
    source_version VARCHAR(32) NOT NULL,
    raw_data_type VARCHAR(64),
    raw_data_ref VARCHAR(512),
    content_hash VARCHAR(64),
    derivation_method VARCHAR(128),
    derivation_inputs UUID[],
    derivation_parameters JSONB,
    validation_status VARCHAR(32) DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_evidence_type ON evidence(type);
CREATE INDEX idx_evidence_engine ON evidence(source_engine, source_version);

-- Evidence Chains
CREATE TABLE evidence_chain_links (
    id UUID PRIMARY KEY,
    parent_evidence_id UUID NOT NULL REFERENCES evidence(id),
    child_evidence_id UUID NOT NULL REFERENCES evidence(id),
    relationship_type VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_chain_parent ON evidence_chain_links(parent_evidence_id);
CREATE INDEX idx_chain_child ON evidence_chain_links(child_evidence_id);

-- Insights
CREATE TABLE insights (
    id UUID PRIMARY KEY,
    type VARCHAR(64) NOT NULL,
    title VARCHAR(512) NOT NULL,
    description TEXT,
    severity VARCHAR(32),
    confidence FLOAT CHECK (confidence >= 0.0 AND confidence <= 1.0),
    recommendation TEXT,
    affected_entities UUID[],
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    status VARCHAR(32) DEFAULT 'active'
);
CREATE INDEX idx_insights_type ON insights(type);
CREATE INDEX idx_insights_status ON insights(status);
CREATE INDEX idx_insights_severity ON insights(severity);

-- Precomputed Queries
CREATE TABLE precomputed_queries (
    id UUID PRIMARY KEY,
    query_hash VARCHAR(64) NOT NULL UNIQUE,
    query_type VARCHAR(64) NOT NULL,
    result JSONB NOT NULL,
    computed_at TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    repository_id UUID NOT NULL
);
```

---

## Storage Operations

### Write Path
```
Cognitive Engine â†’ Evidence Node â†’ Validate â†’ Transaction â†’ SQLite â†’ Invalidate Cache
```

### Read Path
```
Query â†’ Check Cache â†’ Load Subgraph â†’ Return Result
```

### Backup
- **Automatic:** Daily export to JSON/GraphML.
- **Manual:** One-click export in UI.
- **Format:** Standard formats (JSON, GraphML, CSV) for portability.

---

## Migration Strategy

### Schema Versioning
- Schema version stored in `scm_metadata` table.
- Migration scripts named `migrate_v{N}_to_v{N+1}.sql`.
- Migrations run automatically on startup.
- Rollback scripts maintained for each migration.

### V1 to V2 Migration (PostgreSQL)
When upgrading to PostgreSQL:
1. Export V1 SQLite to JSON.
2. Import JSON to PostgreSQL.
3. Rebuild indices.
4. Verify integrity.
5. Update connection string.

---

## The Storage Doctrine

> **Understanding that disappears when the power goes out is not understanding. The storage layer ensures that the Software Cognition Model persists, survives, and can be transported. It is the memory of Project DNA.**



================================================================================
# 08 SCM Glossary
================================================================================

# SCM Glossary

## Terms Specific to the Software Cognition Model

This document defines terms introduced in Phase 3. For the master glossary, see Phase -1 and Phase 0.

---

## A

### Affected Entities
The list of entities (modules, files, authors) that an insight impacts or references.

### Aggregate Query
A query that computes statistics (count, average, histogram) over a set of entities.

---

## B

### Breadth Score
A measure of how well an author understands the broader system around a specific module. See: Knowledge Model.

### Bus Factor
The number of engineers who would need to leave before a module becomes unmaintainable. A key metric in the Knowledge Model.

---

## C

### Confidence Level
The certainty assigned to evidence or an insight. Levels: Certain, High, Medium, Low, Speculative.

### Cross-Dimensional Evidence
Evidence that combines data from multiple Cognitive Engines. More reliable than single-dimensional evidence.

---

## D

### Depth Score
A measure of how well an author understands a specific module. See: Knowledge Model.

### Evidence Chain
A linked sequence from raw data through intermediate evidence to an insight. Enables traceability.

---

## E

### Entity
Anything that exists in the software system or its history: file, function, commit, author, module, insight, etc.

### Evidence
Deterministic, verifiable data that supports a conclusion. The foundation of trust in the SCM.

### Evidence Node
A structured record of a single piece of evidence, including type, value, source, and confidence.

### Expertise Profile
A record of an author's knowledge about a specific module, including depth, breadth, and tenure.

---

## G

### Graph Partition
A subset of the SCM graph, typically by module or time range, used for scaling large repositories.

### Ground Truth
The verifiable source data (commit hash, file content, AST output) that evidence is derived from.

---

## I

### Immutable Evidence
Evidence that, once stored, is never modified. New evidence supersedes old through the SUPERSEDES relationship.

### Incremental Snapshot
A snapshot capturing only changes since the previous snapshot, not the full SCM state.

### Insight
A conclusion drawn from evidence by the Cognitive Reasoning Layer. Always includes confidence and evidence chain.

---

## K

### Knowledge Concentration
The distribution of expertise across a team, measured by Gini coefficient. Lower is better.

### Knowledge Gap
A module or area where expertise is insufficient, identified by the Knowledge Model.

### Knowledge Graph
The bipartite graph connecting authors to modules via expertise and contribution relationships.

---

## M

### Metric Series
A time-ordered sequence of metric values for a specific entity and metric type.

### Metric Value
A single measurement at a point in time, linked to the evidence that produced it.

### Multi-Model Data Structure
The SCM's architecture combining graph, relational, time-series, and document models.

---

## O

### Onboarding Difficulty
Estimated time for a new engineer to become productive in a module. Derived from complexity, documentation, and expertise availability.

### Ownership
The relationship between authors and modules, indicating responsibility and expertise.

---

## P

### Pattern Query
A query that finds subgraphs matching a specified template, used for detecting architectural patterns or anti-patterns.

### Perception Store
The pillar of the SCM containing all raw and processed data from Cognitive Engines.

### Precomputed Query
A query result computed in the background and cached for fast retrieval.

---

## R

### Raw Data Ref
A pointer to the original source data (commit hash, file path, line range) that evidence is derived from.

### Reasoning Store
The pillar of the SCM containing insights, predictions, recommendations, and decisions.

### Relationship
A directed, typed connection between two entities in the SCM graph.

### Representation Store
The pillar of the SCM containing the unified graph of entities and relationships.

---

## S

### Snapshot
A complete or partial capture of the SCM state at a specific point in time.

### Subgraph
A subset of the SCM graph, typically centered on an entity with a specified radius.

### Superseded Evidence
Evidence that has been replaced by newer evidence. Retained for audit but marked inactive.

---

## T

### Temporal Edge
An edge with `valid_from` and `valid_to` timestamps, enabling historical relationship queries.

### Temporal Query
A query that includes a time dimension, enabling time-travel through the SCM.

### Temporal Store
The pillar of the SCM containing events, metric series, snapshots, and trends.

### Trend
A computed pattern over a metric series, including direction, slope, and forecast.

---

## V

### Validation Status
The state of evidence verification: pending, valid, invalid, or disputed.

---

## Document Conventions

- Terms defined in Phase -1 and Phase 0 are not redefined here. Cross-reference those glossaries.
- New terms introduced in Phase 3 are defined here and will be added to the master glossary.
- Terms are organized alphabetically within the phase glossary.

