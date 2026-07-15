

================================================================================
# 01 System Architecture
================================================================================

# System Architecture

## How Project DNA Works Internally

This document presents the high-level system architecture of Project DNA. It is the technical foundation upon which all implementation decisions are built.

---

## Architectural Principles

1. **Local-first.** All core processing happens on the user's machine.
2. **Deterministic-first.** Evidence is produced by deterministic engines. AI reasoning sits on top.
3. **Modular.** Each Cognitive Engine is independent.
4. **Incremental.** The system analyzes repositories incrementally.
5. **Observable.** Every component emits metrics and logs.

---

## The Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                         │
│  (React Web App / Desktop App — Phase 7)                            │
├─────────────────────────────────────────────────────────────────────┤
│                      API Gateway Layer                               │
│  (REST API / WebSocket — Phase 6)                                    │
├─────────────────────────────────────────────────────────────────────┤
│                    Cognitive Reasoning Layer                         │
│  (Local LLM Orchestration, Prompt Management, Context Assembly)      │
├─────────────────────────────────────────────────────────────────────┤
│                   Software Cognition Model (SCM)                     │
│  (Unified Data Model: Graph, Metrics, History, Knowledge, Evidence)  │
├─────────────────────────────────────────────────────────────────────┤
│                     Cognitive Engines                                │
│  (Structural, Evolution, Knowledge, Dependency, Risk, Architecture, │
│   Decision, Prediction, Security, Collaboration)                     │
├─────────────────────────────────────────────────────────────────────┤
│                    Processing Pipeline                               │
│  (Git Mining, AST Parsing, Dependency Resolution, Metric Calculation)│
├─────────────────────────────────────────────────────────────────────┤
│                      Repository Input                                │
│  (Local Git Repository, File System)                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Repository Input

**Purpose:** The raw material. The software system being understood.

**Components:**
- **Git Repository:** Commit history, branches, merges, tags.
- **File System:** Source code, configuration, documentation, tests.
- **Package Manifests:** package.json, requirements.txt, Cargo.toml, etc.
- **Build Configuration:** Dockerfiles, CI/CD configs, build scripts.

**Interface:**
- File system access (read-only).
- Git command execution (read-only).
- No modification of source code.

---

## Layer 2: Processing Pipeline

**Purpose:** Transform raw repository data into structured, analyzable formats.

**Stages:**

### Stage 2.1: Repository Discovery
- Detect repository type, languages, frameworks.
- Identify build system, test framework, package manager.
- Map file structure and ignore patterns.

### Stage 2.2: Git Mining
- Extract commit history with metadata.
- Build contribution graphs.
- Detect branch/merge patterns.

### Stage 2.3: AST Parsing
- Parse source files into Abstract Syntax Trees.
- Extract: functions, classes, interfaces, imports, exports.
- Language-specific parsers for supported languages.

### Stage 2.4: Dependency Resolution
- Build internal dependency graph.
- Resolve external dependencies from package manifests.
- Map version constraints and lock file versions.

### Stage 2.5: Metric Calculation
- Compute complexity metrics (cyclomatic, cognitive).
- Calculate code coverage.
- Measure duplication.

**Output:**
- Parsed ASTs, dependency graphs, commit history structures, raw metric values.

**Incremental Processing:**
- On first run: Full pipeline execution.
- On subsequent runs: Only changed files and commits are reprocessed.

---

## Layer 3: Cognitive Engines

**Purpose:** Transform processed data into structured evidence and understanding.

Each engine is an independent module with:
- **Input:** Processed data from the pipeline.
- **Output:** Structured evidence nodes added to the SCM.
- **Algorithm:** Deterministic, testable logic.
- **Interface:** Standardized API for registration, execution, and output.

See Phase 4 for detailed engine specifications.

**Engine Orchestration:**
- Engines run in parallel where possible.
- Dependencies between engines are declared and resolved.
- Engine execution is idempotent.
- Failed engines do not block others.

---

## Layer 4: Software Cognition Model (SCM)

**Purpose:** The unified, queryable representation of the software system.

The SCM is a multi-model data structure:

### 4.1 Graph Store
- **Nodes:** Files, functions, classes, modules, services, commits, authors, packages.
- **Edges:** Dependencies, ownership, co-changes, calls, inherits, contains.
- **Properties:** Metrics, timestamps, confidence scores.

### 4.2 Time-Series Store
- **Snapshots:** SCM state at specific points in time.
- **Trends:** Metric values over time.
- **Events:** Significant occurrences.

### 4.3 Evidence Store
- **Evidence Nodes:** Individual pieces of evidence.
- **Evidence Chains:** Linked sequences from raw data to insight.
- **Confidence Metadata:** Certainty levels and validation status.

### 4.4 Knowledge Store
- **Ownership Maps:** Who knows what.
- **Expertise Profiles:** Engineer capabilities and history.
- **Decision Records:** Past decisions with outcomes.

**Query Interface:**
- Graph queries (traversal, pattern matching).
- Time-range queries.
- Evidence chain queries.
- Full-text search.

**Storage Backend:**
- Default: SQLite (embedded, zero-config).
- Optional: PostgreSQL (for larger deployments, V2).
- Graph operations: In-memory with persistence.

---

## Layer 5: Cognitive Reasoning Layer

**Purpose:** Synthesize evidence into insights, explanations, and recommendations.

**Components:**

### 5.1 Context Assembler
- Gather relevant evidence from the SCM.
- Prioritize evidence by relevance, recency, and confidence.
- Format evidence for LLM consumption.

### 5.2 Prompt Orchestrator
- Select appropriate prompt template.
- Inject assembled context into prompt.
- Manage prompt length (token budget, truncation).

### 5.3 Local LLM Interface
- Communicate with local LLM (Ollama).
- Handle model loading, inference, error recovery.
- Support multiple models.

### 5.4 Response Parser
- Parse LLM output into structured insights.
- Extract: conclusion, confidence, reasoning, recommendations.
- Validate against evidence.

### 5.5 Explanation Formatter
- Format insights for UI presentation.
- Generate evidence chain visualizations.
- Produce natural language summaries.

**Constraints:**
- All reasoning must be evidence-bound.
- Confidence scores reflect evidence quality.
- Responses include "insufficient evidence" when appropriate.
- No autonomous actions.

---

## Layer 6: API Gateway

**Purpose:** Expose system capabilities to the UI and external integrations.

**Interfaces:**

### 6.1 REST API
- Standard HTTP endpoints for CRUD operations.
- Query endpoints for insights, evidence, reports.
- Async endpoints for long-running operations.

### 6.2 WebSocket API
- Real-time updates: new insights, analysis progress, alerts.
- Subscription model.
- Bidirectional communication.

### 6.3 GraphQL API [V2]
- Flexible querying for complex relationships.
- Single endpoint.
- Schema-driven.

---

## Layer 7: User Interface

**Purpose:** Present understanding to users and capture input.

**Architecture:**
- Single-page application (SPA) or desktop app.
- Component-based (React).
- State management: Local-first, syncs with API.
- Real-time updates via WebSocket.

See Phase 7 for detailed frontend architecture.

---

## Technology Stack (V1)

| Layer | Technology | Rationale |
|---|---|---|
| Repository Input | Git CLI, File System | Native, reliable |
| Processing Pipeline | Python / Rust | Performance, ecosystem |
| Cognitive Engines | Python / Rust | Algorithmic flexibility |
| SCM Storage | SQLite + In-Memory Graph | Embedded, queryable |
| Cognitive Reasoning | Python (Ollama) | LLM orchestration |
| API Gateway | Python (FastAPI) | Fast, typed, async |
| UI | React + TypeScript | Component ecosystem |
| Real-Time | WebSocket | Bidirectional, low latency |
| Packaging | Docker / Tauri | Distribution flexibility |

---

## The Architecture Doctrine

> **Project DNA's architecture is layered, modular, and deterministic. Each layer has a single responsibility. The system is designed to grow from a single repository on a laptop to an enterprise platform — but the core principles of local-first, deterministic evidence, and explainable reasoning never change.**


---



================================================================================
# 02 Service Architecture
================================================================================

# Service Architecture

## Services and Their Responsibilities

This document defines the service boundaries within Project DNA. Each service is a deployable unit with clear inputs, outputs, and interfaces.

---

## Service Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│  UI Service (Frontend)                                      │
│  - React SPA or Desktop App                                 │
│  - User interaction, visualization, state management        │
├─────────────────────────────────────────────────────────────┤
│  API Gateway Service                                        │
│  - REST API, WebSocket, GraphQL (V2)                        │
│  - Authentication, rate limiting, request routing           │
├─────────────────────────────────────────────────────────────┤
│  Query Service                                              │
│  - Query parsing, intent recognition                        │
│  - SCM querying, evidence retrieval                         │
│  - Response formatting                                      │
├─────────────────────────────────────────────────────────────┤
│  Reasoning Service                                          │
│  - LLM orchestration                                        │
│  - Prompt management                                        │
│  - Context assembly                                         │
│  - Response parsing and validation                          │
├─────────────────────────────────────────────────────────────┤
│  Analysis Orchestrator Service                              │
│  - Pipeline execution management                            │
│  - Engine scheduling and dependency resolution              │
│  - Incremental change detection                             │
│  - Progress tracking and reporting                          │
├─────────────────────────────────────────────────────────────┤
│  Cognitive Engine Services (per engine)                     │
│  - Structural, Evolution, Knowledge, Dependency, Risk, etc. │
├─────────────────────────────────────────────────────────────┤
│  Processing Services                                        │
│  - Git Mining, AST Parsing, Dependency Resolution, Metrics  │
├─────────────────────────────────────────────────────────────┤
│  SCM Storage Service                                        │
│  - Graph storage, time-series, evidence, search             │
├─────────────────────────────────────────────────────────────┤
│  Notification Service                                       │
│  - Alert generation and delivery                            │
├─────────────────────────────────────────────────────────────┤
│  Report Service                                             │
│  - Report template management, generation, export           │
└─────────────────────────────────────────────────────────────┘
```

---

## Service Communication

### V1: In-Process (Monolith)

All services run in a single process:
- **Function calls** for synchronous operations.
- **In-memory message bus** for async operations.
- **Shared database** (SQLite) for persistence.

### V2+: Inter-Process

Services can be split into separate processes:
- **HTTP/REST** for synchronous requests.
- **Message queue** for async operations.
- **Shared database** (PostgreSQL) for persistence.

---

## Service Interface Contracts

Every service exposes:

### 1. Health Endpoint
```
GET /health
Response: { status: "healthy" | "degraded" | "unhealthy", details: {...} }
```

### 2. Metrics Endpoint
```
GET /metrics
Response: Prometheus-compatible metrics
```

### 3. API Documentation
- OpenAPI specification, auto-generated from code.

---

## Key Services

### UI Service
- **Responsibility:** Present understanding, capture user input.
- **Dependencies:** API Gateway.
- **State:** Local UI state, cached SCM data, user preferences.

### API Gateway
- **Responsibility:** Single entry point, routing, auth (V2+).
- **Dependencies:** Query, Reasoning, Analysis Orchestrator, Report, Notification services.

### Query Service
- **Responsibility:** Parse questions, retrieve evidence from SCM.
- **Components:** Intent Parser, Query Builder, Evidence Retriever, Result Ranker.
- **Dependencies:** SCM Storage.

### Reasoning Service
- **Responsibility:** Synthesize evidence into insights using local LLMs.
- **Components:** Context Assembler, Prompt Manager, LLM Client, Response Parser, Validator.
- **Dependencies:** Query Service, Local LLM.

### Analysis Orchestrator
- **Responsibility:** Manage analysis pipeline and engine execution.
- **Components:** Pipeline Manager, Engine Scheduler, Change Detector, Progress Reporter.
- **Dependencies:** Processing Services, Engine Services, SCM Storage.

### SCM Storage Service
- **Responsibility:** Store and query the Software Cognition Model.
- **Components:** Graph Store, Time-Series Store, Evidence Store, Search Index.
- **Backends:** V1: SQLite + In-Memory. V2: PostgreSQL + Graph DB.

---

## Deployment Models

### V1: Single Process
- All services in one executable.
- **Pros:** Simple deployment, no network overhead.
- **Cons:** No isolation, limited scaling.

### V2: Modular Process
- Core services in one process. Optional services separate.
- **Pros:** Some isolation, background processing.

### V3: Distributed
- Each service in its own container.
- **Pros:** Independent scaling, fault isolation.
- **Cons:** Network overhead, operational complexity.

---

## The Service Architecture Doctrine

> **Services are boundaries of responsibility, not barriers to understanding. Each service owns a clear capability. Services communicate through contracts, not assumptions.**


---



================================================================================
# 03 Repository Processing
================================================================================

# Repository Processing

## End-to-End Analysis Flow

This document details the complete processing pipeline — how a repository is transformed from raw files into a populated Software Cognition Model.

---

## Processing Philosophy

1. **Read-only.** Never modifies the source repository.
2. **Incremental.** Only changed content is reprocessed.
3. **Resilient.** Errors in one file or stage do not crash the pipeline.
4. **Observable.** Every stage emits progress and metrics.

---

## Pipeline Overview

```
Repository Input
    ↓
[Stage 1] Repository Discovery
    ↓
[Stage 2] Git Mining
    ↓
[Stage 3] File Indexing
    ↓
[Stage 4] AST Parsing
    ↓
[Stage 5] Dependency Resolution
    ↓
[Stage 6] Metric Calculation
    ↓
[Stage 7] Evidence Construction
    ↓
Software Cognition Model (SCM)
```

---

## Stage 1: Repository Discovery

**Purpose:** Understand what kind of repository this is.

**Process:**
1. Scan root directory for known files (package.json, pom.xml, etc.).
2. Count files by extension.
3. Detect framework from dependency manifests.
4. Detect build system from configuration files.
5. Detect test framework from devDependencies.
6. Infer architecture from directory structure.
7. Read .gitignore and .dnaignore for exclusion patterns.

**Output:** Repository metadata, language map, framework detection, architecture hints.

**Incremental:** Runs once per repository. Re-runs only if root config files change.

---

## Stage 2: Git Mining

**Purpose:** Extract complete history and collaboration data.

**Process:**
1. Execute `git log` with structured format for all commits.
2. Parse commit metadata (author, date, message).
3. Get changed files and line stats per commit.
4. Build author contribution matrix.
5. Detect branch and merge patterns.
6. Map tags to commits.
7. Detect refactoring events from commit messages.

**Output:** Commit objects, file change stats, author timeline, branch history.

**Incremental:** First run: full log. Subsequent: from last processed commit hash.

**Performance:** Target 10,000 commits in < 30 seconds. Stream processing.

---

## Stage 3: File Indexing

**Purpose:** Build complete index of all relevant files.

**Process:**
1. Walk directory tree recursively.
2. Skip files matching ignore patterns.
3. Classify each file: source, test, config, documentation, build.
4. Calculate file hashes for change detection.

**Output:** File inventory, classification map, directory structure.

**Incremental:** Compare hashes and mtimes. Only reprocess changed files.

---

## Stage 4: AST Parsing

**Purpose:** Parse source code into structured representations.

**Supported Languages (V1):** JavaScript/TypeScript, Python, Java, Go, Rust, C/C++.

**Process:**
1. Select parser (tree-sitter) per language.
2. Parse file into AST.
3. Traverse AST to extract:
   - Function definitions (name, params, line range, complexity).
   - Class definitions (name, methods, inheritance).
   - Import/export statements.
   - Variable declarations.
4. Build per-file symbol table.
5. Build cross-file import/export map.

**Output:** ASTs, symbol tables, import/export maps.

**Incremental:** Only parse changed files. Cache ASTs by file hash.

**Performance:** Target 1,000 files in < 60 seconds. Parallel parsing.

---

## Stage 5: Dependency Resolution

**Purpose:** Build complete internal and external dependency graphs.

### Internal Dependencies
1. Resolve import paths to actual files.
2. Build file-level dependency edges.
3. Aggregate to module level.
4. Detect circular dependencies.

### External Dependencies
1. Parse package manifests.
2. Parse lock files for exact versions.
3. Build package dependency tree.
4. Identify outdated packages.

**Output:** Internal dependency graph, external dependency graph, circular dependency list.

**Incremental:** Re-resolve only for changed files and updated manifests.

---

## Stage 6: Metric Calculation

**Purpose:** Compute quantitative metrics for every code unit.

**Metrics:**
- **Complexity:** Cyclomatic, cognitive, Halstead.
- **Size:** LOC, function count, file count.
- **Quality:** Test coverage, documentation coverage, duplication.
- **Change:** Change frequency, code churn, age.

**Output:** Per-function, per-file, per-module metrics.

**Incremental:** Recalculate only for changed files. Aggregate from file metrics.

---

## Stage 7: Evidence Construction

**Purpose:** Transform pipeline outputs into structured evidence.

**Process:**
1. Create evidence nodes for significant findings.
2. Link evidence to raw data (commit hash, file path, line range).
3. Build evidence chains for complex findings.
4. Assign confidence levels.
5. Tag with engine source, timestamp, version.

**Output:** Evidence nodes, evidence edges, raw data references.

---

## Incremental Processing Strategy

### Change Detection
- **Git-based:** Compare current HEAD to last analyzed commit.
- **File watcher:** Monitor filesystem during active development. Debounce 5 seconds.

### Incremental Execution
```
On Change:
  1. Identify changed files and commits.
  2. Re-run affected stages only.
  3. Update SCM incrementally.
  4. Notify affected Cognitive Engines.
  5. Generate new insights if significant.
  6. Push updates to UI via WebSocket.
```

### Full Re-analysis
Triggered by: user request, engine version update, configuration change.

---

## Pipeline Monitoring

Every stage emits:
- **Progress:** Percentage complete, current operation.
- **Metrics:** Files processed, commits analyzed, time elapsed.
- **Warnings:** Non-fatal issues.
- **Errors:** Fatal issues that skip content but don't crash pipeline.

UI displays: progress bar, expandable log, estimated time, cancel button.

---

## The Processing Doctrine

> **The processing pipeline is the sensory system of Project DNA. It perceives the repository through multiple dimensions and transforms raw perception into structured evidence. It is fast, incremental, resilient, and transparent.**


---



================================================================================
# 04 Data Flow
================================================================================

# Data Flow

## How Data Moves Through Project DNA

This document maps every major data flow in the system.

---

## Flow 1: Repository Import and Full Analysis

**Trigger:** User imports a new repository.

```
User (UI)
  │ POST /api/repositories { path: "/path/to/repo" }
  ↓
API Gateway → Analysis Orchestrator
  │ Creates job, emits "analysis.started"
  ↓
  ├─→ WebSocket → UI: "Analysis started..."
  │
  ├─→ Repository Discovery → RepositoryMetadata
  ├─→ Git Mining → CommitHistory, AuthorStats
  ├─→ File Indexing → FileInventory
  ├─→ AST Parsing → ASTs, SymbolTables
  ├─→ Dependency Resolution → InternalDeps, ExternalDeps
  ├─→ Metric Calculation → Metrics
  └─→ Evidence Construction → EvidenceNodes, EvidenceEdges
        ↓
      SCM Storage (stores all evidence)
        ↓
      Cognitive Engines (parallel)
        │ Each reads relevant evidence, produces new evidence
        ↓
      SCM Storage (stores engine outputs)
        ↓
      Cognitive Reasoning Layer
        │ Generates insights with evidence chains
        ↓
      Notification Service
        ├─→ WebSocket → UI: "47 insights generated"
        └─→ UI updates dashboard
```

**Duration:** 5-30 minutes.

---

## Flow 2: Incremental Update on Commit

**Trigger:** New commit detected.

```
Git Hook / File Watcher
  │ Detects change
  ↓
Analysis Orchestrator
  │ Identifies changed files/commits
  │ Runs incremental stages only
  │ Updates SCM incrementally
  │ Re-runs affected engines
  │ Re-evaluates insights
  ↓
WebSocket → UI: Real-time updates
```

**Duration:** 10 seconds to 2 minutes.

---

## Flow 3: User Asks a Question

**Trigger:** User types question in search bar.

```
User: "Why is PaymentService complex?"
  ↓
Query Service
  │ Parses intent, identifies entities
  │ Fetches from SCM: module, metrics, trends, commits, ownership
  ↓
Reasoning Service
  │ Assembles context, selects prompt template
  │ Sends to Local LLM (Ollama)
  │ Parses response, validates against evidence
  ↓
UI renders: Summary, explanation, charts, evidence panel
```

**Duration:** 2-10 seconds.

---

## Flow 4: User Explores Evidence

**Trigger:** User clicks [Show Evidence].

```
UI → GET /api/evidence/{insightId}/chain
  ↓
Query Service retrieves evidence chain from SCM
  │ Traverses: Insight → Evidence Nodes → Raw Data
  ↓
UI renders: Tree visualization, expandable nodes, raw data links
```

**Duration:** < 500ms (pre-computed).

---

## Flow 5: Alert Generation

**Trigger:** Critical insight generated.

```
Cognitive Engine / Reasoning Service
  │ Generates insight with severity "Critical"
  ↓
Notification Service
  │ Checks alert rules (threshold, deduplication, subscriptions)
  │ If passes: creates alert
  ↓
  ├─→ WebSocket: Real-time push
  ├─→ In-app: Notification center
  └─→ Email (V2+, optional)
```

**Duration:** < 1 second.

---

## Data Flow Principles

1. **Unidirectional for analysis.** Repository → Pipeline → Engines → SCM → Reasoning.
2. **Bidirectional for interaction.** User actions → Backend. Updates → WebSocket → UI.
3. **Lazy loading for evidence.** Fetched on demand, not pre-loaded.
4. **Event-driven for updates.** Changes trigger events. Services react.
5. **Idempotent for safety.** Same input → same output.

---

## The Data Flow Doctrine

> **Data flows through Project DNA like understanding flows through an engineer's mind — from perception to representation to reasoning to explanation. Every flow is observable, every transformation is traceable, every output is evidence-backed.**


---



================================================================================
# 05 Module Boundaries
================================================================================

# Module Boundaries

## Defining the Boundaries

This document defines the boundaries between modules — what each owns, exposes, and depends on.

---

## Boundary Principles

1. **Single Responsibility.** Each module does one thing well.
2. **Explicit Interfaces.** Modules communicate through defined APIs.
3. **Dependency Direction.** Dependencies flow inward.
4. **Replaceability.** Any module can be replaced without breaking the system.

---

## The Layered Boundary Model

```
┌─────────────────────────────────────────────┐
│  UI Layer (Presentation)                    │
│  - Owns: Rendering, user interaction        │
│  - Depends on: API Layer                    │
├─────────────────────────────────────────────┤
│  API Layer (Interface)                      │
│  - Owns: Request handling, routing          │
│  - Depends on: Service Layer                │
├─────────────────────────────────────────────┤
│  Service Layer (Application)                │
│  - Owns: Use cases, orchestration           │
│  - Depends on: Domain Layer                 │
├─────────────────────────────────────────────┤
│  Domain Layer (Business Logic)              │
│  - Owns: Engines, reasoning, SCM model      │
│  - Depends on: Infrastructure Layer         │
├─────────────────────────────────────────────┤
│  Infrastructure Layer (Technical)           │
│  - Owns: Storage, parsing, Git access       │
│  - Depends on: External libraries           │
└─────────────────────────────────────────────┘
```

---

## Dependency Rules

### Allowed
```
UI → API → Service → Domain → Infrastructure → External
```

### Forbidden
```
UI → Service (must go through API)
UI → Domain
UI → Infrastructure
API → Domain (must go through Service)
API → Infrastructure
Service → Infrastructure (must go through Domain interfaces)
Domain → External Libraries
Infrastructure → UI/API/Service
```

---

## Domain Layer Modules

### SCM Core
- **Graph Model:** Node/edge definitions, graph operations.
- **Time-Series Model:** Temporal data structures.
- **Evidence Model:** Evidence chain structures.
- **Query Engine:** Graph traversal, pattern matching.

### Cognitive Engines (independent modules)
- Structural, Evolution, Knowledge, Dependency, Risk, Architectural, Decision, Prediction.

### Reasoning Core
- Context Assembler, Prompt Manager, LLM Interface, Response Parser.

---

## Infrastructure Layer Modules

### Storage
- Graph Store, Relational Store (SQLite/PostgreSQL), Search Index, Cache.

### Processing
- Git Client, AST Parser (tree-sitter), Dependency Resolver, Metric Calculator.

### External
- LLM Client (Ollama), File System, Process Runner.

---

## Cross-Cutting Concerns

- **Logging:** All modules emit log events through logging module.
- **Configuration:** Injected through constructor, not read directly.
- **Metrics:** All modules emit metrics through metrics collector.
- **Error Handling:** Domain defines error types. Infrastructure/API handle mapping.

---

## Module Size Guidelines

- **Small:** < 500 lines. Single responsibility.
- **Medium:** 500-2000 lines. Cohesive feature set.
- **Large:** 2000-5000 lines. Justified complexity.
- **Too large:** > 5000 lines. Must split.

---

## The Boundary Doctrine

> **Boundaries are not barriers. They are contracts. Each module owns its responsibility and exposes a clear interface. Dependencies flow inward. Knowledge flows outward.**


---



================================================================================
# 06 Technology Decisions
================================================================================

# Technology Decisions

## Why Each Technology Was Chosen

This document records every major technology decision with rationale, alternatives, and trade-offs.

---

## Decision Framework

Evaluated on:
1. Local-first compatibility.
2. Zero budget (free, open-source).
3. Performance.
4. Ecosystem.
5. Team familiarity.
6. Future-proofing.

---

## Decision 1: Backend Language

**Chosen:** Python (primary) + Rust (performance-critical)

**Rationale:**
- Python: Rich ecosystem for data processing, ML, LLM integration.
- Python: Rapid development, readable, large talent pool.
- Rust: Performance for parsing, graph operations, large repos.
- Rust: Memory safety without GC.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| Go | Weaker data science/ML ecosystem. Less mature AST parsing. |
| Node.js | Weaker for CPU-intensive tasks. |
| Java | Too heavy for local-first. Slower startup. |
| Pure Rust | Would slow development. Python's ecosystem irreplaceable for LLM. |

**Trade-offs:** Python is slower. Mitigated by Rust for hot paths and multiprocessing.

---

## Decision 2: Frontend Language

**Chosen:** TypeScript + React

**Rationale:**
- TypeScript: Type safety, IDE support, refactoring.
- React: Mature ecosystem, component model, visualization libraries.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| Vue | Good, but React has larger viz ecosystem. |
| Svelte | Promising, but smaller ecosystem. Risk for maintenance. |
| Angular | Too opinionated, heavier bundle. |
| Plain JS | No type safety. Unacceptable. |

---

## Decision 3: Local LLM Runtime

**Chosen:** Ollama

**Rationale:**
- Simplest way to run local LLMs. One-command install.
- Manages model downloads, updates, serving.
- REST API compatible with OpenAI format.
- Active development.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| llama.cpp | Lower-level, more setup. Good fallback. |
| vLLM | Better for server deployments. Overkill for local. |
| OpenAI API | Violates local-first. Requires internet and payment. |

**Trade-offs:** macOS/Linux focused. Windows support improving. Fallback to llama.cpp.

---

## Decision 4: Database

**Chosen:** SQLite (default) + PostgreSQL (optional V2+)

**Rationale:**
- SQLite: Embedded, zero-config, single-file. Perfect for local-first.
- SQLite: Sufficient for single-repository SCM.
- PostgreSQL: For V2+ multi-user or large deployments.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| MongoDB | Document model doesn't fit graph + relational well. |
| Neo4j (V1) | Separate process. Too heavy for default local deploy. |
| DuckDB | Good for analytics, less mature for OLTP. |

---

## Decision 5: Graph Processing

**Chosen:** In-memory graph (NetworkX / petgraph) with SQLite persistence

**Rationale:**
- In-memory: Fast traversal, complex algorithms.
- NetworkX (Python): Rich algorithm library.
- petgraph (Rust): Performance-critical operations.
- SQLite: Persistent storage.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| Neo4j | Separate process, heavy. Viable for V2 enterprise. |
| Dgraph | Distributed. Overkill for local. |
| Graph-tool | Harder to install (C++ deps). |

**Trade-offs:** In-memory limits graph size to RAM. Mitigated by lazy loading.

---

## Decision 6: AST Parsing

**Chosen:** Tree-sitter

**Rationale:**
- Fast, incremental parsing.
- 30+ languages with consistent API.
- Battle-tested (GitHub, Neovim).
- Produces concrete syntax trees.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| Language-specific parsers | Fragmented APIs, inconsistent outputs. |
| ANTLR | Requires grammar files per language. Slower. |
| Pygments | Lexer only, no AST. |

---

## Decision 7: API Framework

**Chosen:** FastAPI (Python)

**Rationale:**
- Fast: Built on Starlette and Pydantic.
- Typed: Automatic request/response validation.
- Async: Native async support.
- Auto-docs: OpenAPI/Swagger generated automatically.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| Flask | Less performant, no native async. |
| Django | Too heavy, too opinionated for API-only. |
| Express (Node) | Would require separate Node backend. |
| Tornado | Less ecosystem than FastAPI. |

---

## Decision 8: UI Framework

**Chosen:** React 18 + Vite

**Rationale:**
- React: Mature, large ecosystem, excellent for data viz.
- Vite: Fast dev server, fast builds, modern ES modules.
- TypeScript: Type safety throughout.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| Create React App | Deprecated, slow builds. |
| Next.js | SSR not needed for local-first app. Adds complexity. |
| Webpack | Slower than Vite. More configuration. |

---

## Decision 9: State Management

**Chosen:** Zustand + React Query (TanStack Query)

**Rationale:**
- Zustand: Simple, lightweight global state. No boilerplate.
- React Query: Server state management (caching, synchronization, background updates).
- Combination covers both global UI state and server data.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| Redux | Too much boilerplate for our needs. |
| MobX | More complex than Zustand. |
| Context API | Insufficient for complex state. Prop drilling issues. |
| Apollo Client | GraphQL-specific. We use REST primarily. |

---

## Decision 10: Visualization

**Chosen:** D3.js (low-level) + Recharts (high-level charts) + React Flow (graphs)

**Rationale:**
- D3: Maximum flexibility for custom visualizations.
- Recharts: Quick, beautiful charts for standard metrics.
- React Flow: Interactive node-edge graphs with React integration.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| Chart.js | Less flexible than D3. |
| Highcharts | Commercial license required for some features. |
| Victory | Good, but smaller ecosystem than Recharts. |
| Cytoscape.js | Good for graphs, but React Flow has better React integration. |

---

## Decision 11: Testing

**Chosen:** Vitest (unit) + Playwright (e2e) + pytest (backend)

**Rationale:**
- Vitest: Fast, Vite-native, Jest-compatible API.
- Playwright: Modern, reliable, cross-browser e2e testing.
- pytest: Standard for Python, rich plugin ecosystem.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| Jest | Slower than Vitest. Less Vite integration. |
| Cypress | Slower than Playwright. Less reliable. |
| unittest (Python) | Less ergonomic than pytest. |

---

## Decision 12: Packaging / Distribution

**Chosen:** Docker (server) + Tauri (desktop) + npm (CLI)

**Rationale:**
- Docker: Containerized deployment, reproducible environments.
- Tauri: Lightweight desktop apps (Rust backend, web frontend). Smaller than Electron.
- npm: Easy CLI distribution for developers.

**Alternatives:**

| Alternative | Why Rejected |
|---|---|
| Electron | Large bundle size, memory hungry. |
| PyInstaller | Single executable, but less polished than Tauri. |
| Snap / Flatpak | Platform-specific, less universal than Docker. |

---

## Technology Stack Summary (V1)

| Category | Technology |
|---|---|
| Backend | Python 3.11+, Rust |
| Frontend | TypeScript, React 18, Vite |
| API | FastAPI, WebSocket |
| Database | SQLite (default), PostgreSQL (optional) |
| Graph | NetworkX (Python), petgraph (Rust) |
| AST Parsing | Tree-sitter |
| LLM | Ollama (local) |
| State Management | Zustand, React Query |
| Visualization | D3.js, Recharts, React Flow |
| Testing | Vitest, Playwright, pytest |
| Packaging | Docker, Tauri, npm |

---

## The Technology Doctrine

> **Every technology choice serves the product principles: local-first, zero budget, performance, and maintainability. We do not chase trends. We choose tools that are proven, open, and aligned with our architecture. When a better tool emerges that serves our principles, we evaluate it objectively and migrate if warranted.**


---



================================================================================
# 07 Design Patterns
================================================================================

# Design Patterns

## Patterns Used in Project DNA

This document documents the design patterns used throughout Project DNA. Consistent patterns make the codebase predictable, testable, and maintainable.

---

## 1. Repository Pattern

**Purpose:** Abstract data access. Domain layer defines interfaces. Infrastructure implements them.

**Usage:**
- SCM Storage interfaces defined in domain layer.
- SQLite/PostgreSQL implementations in infrastructure.
- Domain logic depends on interfaces, not implementations.

**Example:**
```python
# Domain layer
class SCMRepository(Protocol):
    def get_node(self, node_id: str) -> Node: ...
    def save_evidence(self, evidence: Evidence) -> None: ...

# Infrastructure layer
class SQLiteSCMRepository:
    def get_node(self, node_id: str) -> Node: ...
    def save_evidence(self, evidence: Evidence) -> None: ...
```

---

## 2. Strategy Pattern

**Purpose:** Interchangeable algorithms. Used for engine selection, parsing strategies, metric calculations.

**Usage:**
- Different complexity calculation strategies per language.
- Different prompt strategies per question type.
- Different export formats (PDF, HTML, Markdown).

**Example:**
```python
class ComplexityStrategy(Protocol):
    def calculate(self, ast: AST) -> int: ...

class CyclomaticComplexity:
    def calculate(self, ast: AST) -> int: ...

class CognitiveComplexity:
    def calculate(self, ast: AST) -> int: ...
```

---

## 3. Observer Pattern / Event Bus

**Purpose:** Decoupled communication between components. One emits, many listen.

**Usage:**
- Analysis progress updates.
- New insight notifications.
- Engine completion events.
- UI state changes.

**Example:**
```python
event_bus.subscribe("analysis.completed", on_analysis_complete)
event_bus.subscribe("analysis.completed", send_notification)
event_bus.publish("analysis.completed", { repository_id: "..." })
```

---

## 4. Pipeline Pattern

**Purpose:** Sequential processing stages. Output of one stage is input to next.

**Usage:**
- Repository processing pipeline (Stage 1 → Stage 2 → ...).
- Evidence chain construction.
- Report generation pipeline.

**Example:**
```python
pipeline = Pipeline([
    RepositoryDiscovery(),
    GitMining(),
    FileIndexing(),
    ASTParsing(),
    DependencyResolution(),
    MetricCalculation(),
    EvidenceConstruction()
])
result = pipeline.execute(repository)
```

---

## 5. Factory Pattern

**Purpose:** Create objects without specifying exact class. Used for engine instantiation, parser selection.

**Usage:**
- Create appropriate parser based on file extension.
- Create appropriate engine based on configuration.
- Create appropriate storage backend based on settings.

**Example:**
```python
class ParserFactory:
    @staticmethod
    def create(language: str) -> Parser:
        if language == "python":
            return PythonParser()
        elif language == "javascript":
            return JavaScriptParser()
        ...
```

---

## 6. Builder Pattern

**Purpose:** Construct complex objects step by step. Used for evidence chains, insights, reports.

**Usage:**
- Build evidence chains incrementally.
- Build insights with multiple optional fields.
- Build reports with configurable sections.

**Example:**
```python
insight = (InsightBuilder()
    .with_title("PaymentService is a bottleneck")
    .with_severity(Severity.HIGH)
    .with_evidence(evidence_chain)
    .with_confidence(0.87)
    .with_recommendation("Refactor within 30 days")
    .build())
```

---

## 7. Command Pattern

**Purpose:** Encapsulate actions as objects. Enables queuing, undo, logging.

**Usage:**
- Analysis jobs in the orchestrator queue.
- User actions for undo/redo.
- Report generation tasks.

**Example:**
```python
class AnalyzeRepositoryCommand:
    def __init__(self, repository_id: str, config: Config): ...
    def execute(self) -> AnalysisResult: ...
    def undo(self) -> None: ...  # Remove analysis results
```

---

## 8. Adapter Pattern

**Purpose:** Convert one interface to another. Used for external integrations.

**Usage:**
- Adapt Ollama API to internal LLM interface.
- Adapt Git CLI output to internal commit objects.
- Adapt tree-sitter AST to internal AST format.

**Example:**
```python
class OllamaAdapter(LLMInterface):
    def __init__(self, client: OllamaClient): ...
    def generate(self, prompt: str) -> str:
        return self.client.chat(model="llama3", messages=[...])
```

---

## 9. Decorator Pattern

**Purpose:** Add behavior to objects dynamically. Used for caching, logging, validation.

**Usage:**
- Cache decorator for expensive queries.
- Log decorator for engine execution.
- Validate decorator for API inputs.

**Example:**
```python
@cache(ttl=3600)
def get_module_complexity(module_id: str) -> Complexity:
    ...

@log_execution_time
def run_engine(engine: Engine) -> Evidence:
    ...
```

---

## 10. Singleton Pattern (Careful Use)

**Purpose:** One instance of a class. Used for configuration, event bus, connection pools.

**Usage:**
- Configuration manager (one config per process).
- Event bus (central communication).
- Database connection pool.

**Caution:** Overuse leads to tight coupling and testing difficulty. Prefer dependency injection where possible.

---

## 11. Chain of Responsibility

**Purpose:** Pass request along chain of handlers until one handles it. Used for evidence validation.

**Usage:**
- Evidence chain validation: each validator checks one aspect.
- Request handling: middleware chain.

**Example:**
```python
validators = [
    SourceValidator(),
    ConfidenceValidator(),
    ConsistencyValidator(),
    FreshnessValidator()
]
for validator in validators:
    if not validator.validate(evidence):
        raise ValidationError(validator.error_message)
```

---

## 12. State Machine

**Purpose:** Manage object states and transitions. Used for analysis jobs, alerts, decisions.

**Usage:**
- Analysis job: Pending → Running → Completed | Failed.
- Alert: Active → Acknowledged → Resolved | Dismissed.
- Decision: Open → Evaluating → Decided → Tracked → Resolved.

**Example:**
```python
class AnalysisJob:
    state: StateMachine[AnalysisState]

    # Transitions:
    # PENDING → RUNNING (on start)
    # RUNNING → COMPLETED (on success)
    # RUNNING → FAILED (on error)
    # FAILED → RUNNING (on retry)
```

---

## Pattern Selection Guidelines

When implementing a feature, ask:

1. **Is this data access?** → Repository Pattern
2. **Is this an interchangeable algorithm?** → Strategy Pattern
3. **Is this cross-component communication?** → Observer/Event Bus
4. **Is this sequential processing?** → Pipeline Pattern
5. **Is this object creation?** → Factory Pattern
6. **Is this complex object construction?** → Builder Pattern
7. **Is this an action to be queued/logged?** → Command Pattern
8. **Is this external integration?** → Adapter Pattern
9. **Is this adding behavior dynamically?** → Decorator Pattern
10. **Is this state management?** → State Machine

---

## The Pattern Doctrine

> **Patterns are not rules. They are tools. We use them where they clarify, not where they complicate. The goal is not pattern purity. The goal is code that is understandable, testable, and maintainable. When a pattern adds more complexity than clarity, we choose simplicity.**


---



================================================================================
# 08 Performance Strategy
================================================================================

# Performance Strategy

## Making Project DNA Fast

This document defines the performance targets, bottlenecks, and optimization strategies for Project DNA. Performance is a feature. Slow understanding is not understanding.

---

## Performance Principles

1. **Perceived performance matters.** Users should feel the system is responsive even if background tasks take time.
2. **Lazy loading.** Don't load what isn't needed.
3. **Incremental everything.** Only process what changed.
4. **Cache aggressively.** Recompute only when inputs change.
5. **Measure before optimizing.** Profile first, optimize second.

---

## Performance Targets

### Repository Analysis

| Metric | Target | Stretch |
|---|---|---|
| Small repo (< 100K LOC) | < 5 min | < 2 min |
| Medium repo (100K-500K LOC) | < 15 min | < 8 min |
| Large repo (500K-1M LOC) | < 30 min | < 15 min |
| Very large repo (> 1M LOC) | < 60 min | < 30 min |

### Query Response

| Metric | Target | Stretch |
|---|---|---|
| Simple question | < 2 sec | < 1 sec |
| Complex question | < 5 sec | < 3 sec |
| Evidence retrieval | < 500 ms | < 200 ms |
| Dashboard load | < 1 sec | < 500 ms |

### Incremental Update

| Metric | Target |
|---|---|
| Single file change | < 10 sec |
| Small commit (< 10 files) | < 30 sec |
| Large commit (> 50 files) | < 2 min |

### UI

| Metric | Target |
|---|---|
| Time to interactive | < 2 sec |
| First contentful paint | < 1 sec |
| Animation frame rate | 60 fps |
| Graph render (1000 nodes) | < 1 sec |

---

## Bottleneck Analysis

### Known Bottlenecks

1. **AST Parsing:** CPU-intensive, especially for large files.
2. **Git Mining:** I/O bound for large histories.
3. **Graph Operations:** Memory-bound for large graphs.
4. **LLM Inference:** CPU/GPU bound, inherently slow.
5. **Dependency Resolution:** Can be O(n²) for large codebases.

### Profiling Strategy

- **Backend:** cProfile (Python), cargo flamegraph (Rust).
- **Frontend:** Chrome DevTools Performance tab, React Profiler.
- **Database:** SQLite EXPLAIN QUERY PLAN, query timing logs.
- **Continuous:** Automated performance regression tests.

---

## Optimization Strategies

### 1. Parallel Processing

- **AST Parsing:** Parse files in parallel (thread pool).
- **Metric Calculation:** Calculate metrics in parallel.
- **Engine Execution:** Run independent engines in parallel.
- **Implementation:** Python multiprocessing, Rust async/parallel iterators.

### 2. Incremental Processing

- Only reprocess changed files/commits.
- Cache ASTs by file hash.
- Cache dependency graphs per commit.
- Incremental SCM updates (don't rebuild from scratch).

### 3. Lazy Loading

- **UI:** Load dashboard sections on demand.
- **Graph:** Load node details on click, not on graph render.
- **Evidence:** Fetch evidence chains on demand.
- **Reports:** Generate sections on demand in preview.

### 4. Caching

| Cache | Key | TTL | Storage |
|---|---|---|---|
| AST Cache | File hash | Until file changes | Disk (SQLite) |
| Query Cache | Query string + repo state | 1 hour | Memory |
| Evidence Cache | Evidence ID | Infinite (immutable) | Memory + Disk |
| Metric Cache | File hash + metric version | Until file changes | Disk |
| UI Data Cache | Endpoint + params | 5 minutes | IndexedDB |
| LLM Response Cache | Prompt hash | 1 hour | Disk |

### 5. Streaming

- **Git Mining:** Stream commits, don't load all into memory.
- **File Processing:** Stream large files, don't read entirely.
- **UI:** Stream analysis progress updates.
- **Reports:** Stream PDF generation (write pages as generated).

### 6. Graph Optimization

- **Lazy graph loading:** Load subgraphs on demand.
- **Graph summarization:** Aggregate nodes above threshold.
- **Spatial indexing:** R-tree or quadtree for fast spatial queries.
- **Level-of-detail:** Simplify graph at zoomed-out levels.

### 7. Database Optimization

- **Indexing:** Index frequently queried columns (node_id, type, timestamp).
- **Query optimization:** Use EXPLAIN QUERY PLAN. Avoid N+1 queries.
- **Batching:** Batch inserts/updates. Use transactions.
- **Connection pooling:** Reuse database connections.

### 8. LLM Optimization

- **Model selection:** Use smaller models for simple tasks (3B params), larger for complex (7B+).
- **Prompt caching:** Cache similar prompts.
- **Context pruning:** Send only relevant evidence, not entire SCM.
- **Streaming responses:** Show tokens as they arrive, not after completion.
- **Quantization:** Use quantized models (Q4, Q5) for faster inference.

### 9. Frontend Optimization

- **Code splitting:** Lazy load routes and heavy components.
- **Virtualization:** Virtual scroll for long lists (react-window).
- **Memoization:** React.memo, useMemo, useCallback for expensive renders.
- **Debouncing:** Debounce search input, resize handlers.
- **Web Workers:** Offload heavy computations (graph layout) to workers.
- **Asset optimization:** Compress images, tree-shake dependencies.

### 10. Memory Management

- **Backend:** Release ASTs after processing. Use generators for large collections.
- **Frontend:** Dispose WebGL contexts. Unsubscribe from observables.
- **Graph:** Evict least-recently-used nodes from memory.

---

## Performance Monitoring

### Metrics to Track

- Analysis duration per stage.
- Query response time (p50, p95, p99).
- LLM inference time.
- UI frame rate.
- Memory usage (heap, RSS).
- Cache hit/miss rates.
- Error rates and timeouts.

### Tools

- **Backend:** Prometheus metrics, structured logging.
- **Frontend:** Web Vitals, React Profiler, Chrome DevTools.
- **CI:** Performance regression tests (fail if > 10% slower).

---

## The Performance Doctrine

> **Performance is not an afterthought. It is designed in from the start. Every feature must meet performance targets before shipping. We optimize for perceived speed, incremental processing, and intelligent caching. Slow understanding is not understanding.**


---



================================================================================
# 09 Scalability
================================================================================

# Scalability

## Growing from One Repository to an Ecosystem

This document defines how Project DNA scales from analyzing a single repository on a laptop to understanding an entire software ecosystem. Scalability is architectural, not just technical.

---

## Scalability Dimensions

Project DNA scales across three dimensions:

1. **Repository Size:** Lines of code, file count, commit history depth.
2. **Repository Count:** Number of repositories in an organization.
3. **User Count:** Number of concurrent users accessing the system.

---

## V1: Single Repository (Current)

**Target:** One repository, one user, one machine.

**Architecture:**
- Single process monolith.
- SQLite database.
- In-memory graph.
- Local LLM (Ollama).

**Limits:**
- Repository: ~1M LOC, ~10K commits.
- Users: 1 (single-user desktop app).
- Hardware: Consumer laptop (8GB RAM, 4 cores).

**Optimizations:**
- Incremental analysis.
- Lazy loading.
- AST caching.
- Query caching.

---

## V2: Multi-Repository Organization

**Target:** Multiple repositories, small team, shared server or powerful workstation.

**Architecture Changes:**
- **Storage:** PostgreSQL replaces SQLite for concurrent access.
- **Graph:** Optional Neo4j for cross-repository graph queries.
- **Processing:** Background job queue (Redis + Celery/RQ).
- **API:** Separate API server process.
- **UI:** Web app accessible to team.
- **Auth:** JWT-based authentication.

**Limits:**
- Repositories: 50-100.
- Users: 10-50 concurrent.
- Hardware: Server-grade (32GB RAM, 8+ cores).

**New Features:**
- Cross-repository dependency analysis.
- Organization-wide knowledge maps.
- Team health dashboards.
- Shared reports and annotations.

---

## V3: Enterprise

**Target:** Large organization, many repositories, many users.

**Architecture Changes:**
- **Distributed:** Services in containers (Docker/Kubernetes).
- **Database:** PostgreSQL with read replicas.
- **Graph:** Dedicated graph database cluster.
- **Cache:** Redis cluster for query and evidence caching.
- **Queue:** Distributed job queue (Celery with RabbitMQ/Redis).
- **Load Balancer:** Multiple API server instances.
- **Storage:** Object storage for large artifacts (S3-compatible, but self-hosted MinIO).

**Limits:**
- Repositories: 500+.
- Users: 500+ concurrent.
- Hardware: Kubernetes cluster or cloud VMs.

**New Features:**
- Runtime integration (Grafana, Datadog).
- Advanced security scanning.
- Custom engine plugins.
- SSO integration.

---

## V4: Ecosystem

**Target:** Industry-wide understanding. Cross-organization intelligence.

**Architecture Changes:**
- **Federation:** Organizations share anonymized patterns.
- **Global Graph:** Industry-wide dependency and pattern graph.
- **Distributed Learning:** Models improve from aggregated, anonymized data.
- **API Platform:** Third-party integrations and plugins.

**Limits:**
- Repositories: Millions (open-source + anonymized enterprise).
- Users: Tens of thousands.

**New Features:**
- Industry benchmarking.
- Open-source health monitoring.
- Pattern propagation tracking.
- Software ecosystem risk assessment.

---

## Scaling Strategies by Dimension

### Scaling Repository Size

| Technique | V1 | V2 | V3 |
|---|---|---|---|
| Incremental analysis | ✅ | ✅ | ✅ |
| Parallel parsing | ✅ | ✅ | ✅ |
| Streaming processing | ✅ | ✅ | ✅ |
| Distributed parsing | ❌ | ❌ | ✅ |
| Partial analysis (subsets) | ❌ | ✅ | ✅ |
| External storage for ASTs | ❌ | ✅ | ✅ |

### Scaling Repository Count

| Technique | V1 | V2 | V3 |
|---|---|---|---|
| Per-repository databases | ✅ | ❌ | ❌ |
| Shared database with partitioning | ❌ | ✅ | ✅ |
| Cross-repository graph | ❌ | ✅ | ✅ |
| Background sync between repos | ❌ | ❌ | ✅ |
| Repository federation | ❌ | ❌ | ✅ |

### Scaling User Count

| Technique | V1 | V2 | V3 |
|---|---|---|---|
| Single-user desktop | ✅ | ❌ | ❌ |
| Multi-user web app | ❌ | ✅ | ✅ |
| Read replicas | ❌ | ❌ | ✅ |
| API load balancing | ❌ | ❌ | ✅ |
| CDN for static assets | ❌ | ✅ | ✅ |
| WebSocket connection pooling | ❌ | ❌ | ✅ |

---

## Resource Requirements by Scale

### V1: Single Repository

| Resource | Minimum | Recommended |
|---|---|---|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Disk | 1 GB | 5 GB |
| GPU | None | Optional (speeds LLM) |

### V2: Organization

| Resource | Minimum | Recommended |
|---|---|---|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Disk | 10 GB | 50 GB |
| GPU | Optional | Recommended |

### V3: Enterprise

| Resource | Per Node | Cluster |
|---|---|---|
| API Servers | 2 cores, 4 GB | 3+ nodes |
| Workers | 4 cores, 8 GB | 5+ nodes |
| Database | 4 cores, 16 GB | Primary + 2 replicas |
| Graph DB | 4 cores, 16 GB | 3-node cluster |
| Cache | 2 cores, 4 GB | 3-node cluster |

---

## The Scalability Doctrine

> **Project DNA scales by adding capability, not complexity. V1 is a single executable that runs on a laptop. V4 is a distributed platform. But the core architecture — the layers, the engines, the SCM — remains the same. We scale the deployment, not the philosophy.**


---



================================================================================
# 10 Risk Assessment
================================================================================

# Risk Assessment

## Technical Risks and Mitigations

This document identifies the technical risks in Project DNA's architecture and implementation, along with mitigation strategies. Every risk is rated by likelihood and impact.

---

## Risk Matrix

| Likelihood \ Impact | Low | Medium | High |
|---|---|---|---|
| **High** | Monitor | Plan mitigation | Critical priority |
| **Medium** | Accept | Monitor | Plan mitigation |
| **Low** | Accept | Accept | Monitor |

---

## Risk 1: LLM Hallucination in Reasoning

**Description:** The Cognitive Reasoning Layer generates insights not supported by evidence.

**Likelihood:** Medium
**Impact:** High

**Mitigation:**
- Deterministic-first architecture: evidence before reasoning.
- Response validator checks every conclusion against evidence.
- Confidence scores reflect evidence quality, not model certainty.
- Users can inspect evidence chains and override conclusions.
- Continuous testing: benchmark hallucination rate, fail if > 5%.

**Contingency:**
- If hallucination cannot be controlled, reduce LLM scope to explanation only (no inference).
- Fall back to rule-based reasoning for critical insights.

---

## Risk 2: Performance Degradation on Large Repositories

**Description:** Analysis takes too long or consumes too much memory for large codebases.

**Likelihood:** High
**Impact:** Medium

**Mitigation:**
- Incremental analysis: only process changes.
- Streaming: don't load entire repository into memory.
- Parallel processing: multi-core utilization.
- Lazy loading: load data on demand.
- Caching: avoid recomputation.
- Performance budgets: fail CI if analysis exceeds time limit.

**Contingency:**
- Offer "quick analysis" mode with reduced depth.
- Recommend hardware upgrades for very large repos.
- V3 distributed processing for enterprise scale.

---

## Risk 3: Language Support Gaps

**Description:** Important languages lack parser support or engine coverage.

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- Tree-sitter supports 30+ languages with consistent API.
- Graceful degradation: skip unsupported files, continue analysis.
- Community contribution: open-source parsers welcome.
- Clear documentation of supported languages.

**Contingency:**
- Fallback to regex-based parsing for unsupported languages (limited accuracy).
- Prioritize language support based on user demand.

---

## Risk 4: Data Corruption in SCM

**Description:** The Software Cognition Model becomes inconsistent or corrupted.

**Likelihood:** Low
**Impact:** High

**Mitigation:**
- ACID transactions (SQLite/PostgreSQL).
- Immutable evidence: once stored, evidence is not modified, only superseded.
- Versioning: SCM schema versions with migration scripts.
- Backup: Automatic SCM export on schedule.
- Validation: Integrity checks on startup.

**Contingency:**
- Rebuild SCM from repository (full re-analysis).
- Restore from backup.

---

## Risk 5: Local LLM Unavailability

**Description:** Ollama fails to start, model download fails, or inference crashes.

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- Graceful degradation: system works without LLM (deterministic insights only).
- Clear error messages: "LLM unavailable. Reasoning limited to evidence-based insights."
- Multiple model support: fallback to smaller models if large model fails.
- Offline model bundling: include small model in installer.

**Contingency:**
- System operates in "evidence-only mode" without LLM.
- User can manually configure alternative LLM runtime.

---

## Risk 6: Security Vulnerability in Parsing

**Description:** Malicious repository content exploits parser or processing pipeline.

**Likelihood:** Low
**Impact:** High

**Mitigation:**
- Read-only access: never execute repository code.
- Parser sandboxing: tree-sitter is memory-safe (Rust).
- File size limits: reject files > 10MB.
- Depth limits: limit recursion depth in parsing.
- Input validation: sanitize all file paths and names.
- Regular security audits of dependencies.

**Contingency:**
- Isolate parsing in separate process with resource limits.
- Skip suspicious files, log security event.

---

## Risk 7: Cross-Platform Compatibility

**Description:** Features work on macOS/Linux but fail on Windows.

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- Cross-platform testing in CI (GitHub Actions: ubuntu, macos, windows).
- Abstract OS-specific operations (file paths, process spawning).
- Pure Python where possible (avoid OS-specific libraries).
- Docker as fallback for problematic platforms.

**Contingency:**
- Document known platform limitations.
- Prioritize fixes based on user base per platform.

---

## Risk 8: Memory Exhaustion

**Description:** Large repositories cause out-of-memory errors.

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- Streaming processing: don't load everything into memory.
- Memory limits: configurable max memory usage.
- Spill to disk: when memory threshold reached, use temporary files.
- Graph summarization: reduce node count for visualization.
- Monitor memory usage: alert when approaching limit.

**Contingency:**
- Reduce analysis depth automatically when memory constrained.
- Recommend hardware with more RAM.

---

## Risk 9: Dependency Obsolescence

**Description:** Key dependencies (tree-sitter, Ollama, React) become unmaintained or introduce breaking changes.

**Likelihood:** Low
**Impact:** Medium

**Mitigation:**
- Pin dependency versions (lock files).
- Monitor dependency health (activity, maintainers, security).
- Abstract external dependencies behind internal interfaces (Adapter pattern).
- Maintain fork capability for critical dependencies.
- Regular dependency updates (monthly).

**Contingency:**
- Replace dependency with alternative (e.g., switch from Ollama to llama.cpp).
- Maintain fork if upstream abandoned.

---

## Risk 10: User Data Loss

**Description:** User's SCM, settings, or reports are lost.

**Likelihood:** Low
**Impact:** High

**Mitigation:**
- Automatic backups: daily SCM export to user-specified location.
- Data export: one-click full export in standard formats.
- Transaction safety: all writes are transactional.
- Versioned storage: old data retained until explicitly purged.

**Contingency:**
- Restore from backup.
- Rebuild from repository (full re-analysis).

---

## Risk Register

| ID | Risk | Likelihood | Impact | Priority | Owner |
|---|---|---|---|---|---|
| R1 | LLM Hallucination | Medium | High | Critical | Reasoning Team |
| R2 | Performance Degradation | High | Medium | High | Performance Team |
| R3 | Language Support Gaps | Medium | Medium | Medium | Engine Team |
| R4 | Data Corruption | Low | High | High | Storage Team |
| R5 | Local LLM Unavailability | Medium | Medium | Medium | Infrastructure Team |
| R6 | Security Vulnerability | Low | High | High | Security Team |
| R7 | Cross-Platform Issues | Medium | Medium | Medium | Platform Team |
| R8 | Memory Exhaustion | Medium | Medium | Medium | Performance Team |
| R9 | Dependency Obsolescence | Low | Medium | Low | Maintenance Team |
| R10 | User Data Loss | Low | High | High | Storage Team |

---

## The Risk Doctrine

> **Every technical risk in Project DNA is identified, assessed, and mitigated before it becomes a problem. We do not ignore risks. We do not hope they go away. We plan for them, test against them, and build contingencies. The system is resilient because we designed it to be.**
