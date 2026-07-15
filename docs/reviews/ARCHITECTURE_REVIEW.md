# Architecture Review — Project DNA

## Panel Composition

| Panelist | Focus Area | Background |
|---|---|---|
| **Google Staff Engineer** | Scalability, Data Systems | Large-scale distributed storage, query optimization, graph processing at Google scale |
| **Microsoft Principal Engineer** | Maintainability, Developer Experience | Long-lived codebases, API design, engineering systems at Microsoft |
| **Meta Infrastructure Engineer** | Performance, Infrastructure | Real-time systems, frontend performance, production infrastructure at Meta |
| **Netflix Distributed Systems Architect** | Distributed Systems, Fault Tolerance | Microservices, resilience patterns, chaos engineering at Netflix |

---

## Executive Summary

Project DNA proposes a **single-node, local-first, deterministic-graph-plus-LLM architecture** for codebase cognition. The core insight — that deterministic engines produce verifiable evidence which LLMs then reason over — is architecturally sound. The separation of concerns (Engines → SCM → Reasoning → API → UI) follows a clean layered pattern.

**However, the architecture has three existential risks that must be addressed before V1 implementation proceeds:**

1. **Five foundational algorithmic problems are specified as if solved, but have no production precedent** — incremental AST-level analysis, multi-language canonical unification, graph community detection determinism, LLM claim extraction, and evidence conflict resolution.
2. **The V1→V2→V3 roadmap implies a linear progression, but each step requires a fundamental architectural rewrite** — SQLite→PostgreSQL, single-user→multi-user-with-RBAC, single-repo→cross-repo graph. These are not "upgrades." They are new architectures built on top of V1 assumptions that block them.
3. **The local-first constraint creates hard ceilings** — local LLM quality (3B-8B parameters cannot match GPT-4/Claude for complex reasoning), single-node SQLite throughput, and lack of consensus or conflict resolution models.

**Confidence score:** The architecture correctly identifies *what* should be built but does not convincingly solve *how* to build it. Estimated 30-40% of the design is production-viable; the remainder requires substantial re-architecture.

---

## Findings

---

### C-01: Graph Engine Correctness Assumes Deterministic Guarantees for NP-Hard Problems

**Severity:** Critical
**Panelist:** Google Staff Engineer
**Documentation:** Phase_4_Cognitive_Engines_COMBINED.md, Phase_3_Software_Cognition_Model_COMBINED.md

**Description:**
The architecture assumes deterministic engines produce deterministic evidence. However, several proposed engine functions rely on graph algorithms with exponential complexity:
- Community detection (modularity maximization) is NP-hard
- Optimal dependency cycle resolution is NP-hard
- Graph isomorphism (for change detection) has no known polynomial algorithm
- Centrality computation on dynamic graphs requires recomputation

The docs describe engines as "deterministic" but do not acknowledge the algorithmic complexity or fallback strategies for large graphs.

**Impact:**
For a repository with 5000+ nodes and 20000+ edges (a mid-size monorepo), several engines will fail to complete in reasonable time or produce inconsistent results across runs. The "deterministic" guarantee erodes.

**Recommendation:**
- Make algorithmic complexity explicit for each engine in the architecture
- Define approximation strategies, time-bounded execution, and degradation paths
- For community detection: use incremental Louvain or label propagation with bounded iterations
- Specify at what graph size each algorithm switches from exact to approximate

---

### C-02: Incremental Analysis at AST-Node Granularity Is Unsolved in Production

**Severity:** Critical
**Panelist:** Google Staff Engineer
**Documentation:** Phase_4_Cognitive_Engines_COMBINED.md (Incremental Analysis section), Phase_2_System_Architecture_COMBINED.md

**Description:**
The architecture describes incremental analysis — re-analyzing only changed files/modules rather than the full repository. This requires:
1. Detecting changes at AST-node granularity across 6+ languages
2. Tracking which evidence nodes depend on which AST nodes (dependency graph of analysis results)
3. Invalidating only affected evidence
4. Propagating changes through the reasoning pipeline

This is the **cache invalidation problem applied to code analysis** and is an open research area. No production system (SonarQube, CodeClimate, Semgrep) solves this fully. They all re-analyze changed files entirely and do full runs periodically.

**Impact:**
Without incremental analysis, full analysis runs on a 500K-line monorepo could take hours. With 6+ language parsers, incremental state tracking across all of them multiplies complexity. The system will either be too slow to use, or the incremental logic will be buggy and produce stale evidence.

**Recommendation:**
- Start with file-level granularity, not AST-node-level. Re-analyze changed files in full.
- Track file-level dependency maps instead of AST-node-level
- Accept that some evidence will be stale between full runs (document staleness windows)
- Plan for periodic full re-analysis (nightly, on schedule) as a correctness baseline
- Defer AST-node-level incrementality to V3 or mark as "research direction"

---

### C-03: Multi-Language AST Canonical Unification Is Under-Specified

**Severity:** Critical
**Panelist:** Microsoft Principal Engineer
**Documentation:** Phase_3_Software_Cognition_Model_COMBINED.md

**Description:**
The SCM model requires converting source code from 6+ languages (Python, TypeScript, Rust, Go, Java, C++, etc.) into a single canonical AST representation. Each language has fundamentally different constructs:
- Python: modules, classes, functions, async generators
- TypeScript: interfaces, enums, namespaces, decorators, generics
- Rust: traits, macros, lifetimes, modules, impl blocks
- Go: goroutines, channels, interfaces, packages, methods on types
- Java: annotations, generics, inheritance, interfaces, inner classes

A lossless canonical form across these requires either a superset model (capturing every construct from every language) or lossy abstraction (dropping details). Neither is adequate for the "deep codebase understanding" the product promises.

**Impact:**
- Superset model: explosion in node types, making the graph unqueryable and engines overly complex
- Lossy abstraction: missing critical constructs, producing wrong insights (e.g., missing a goroutine launch, misclassifying a Rust trait)

**Recommendation:**
- Define the canonical model's exact scope: what constructs are captured vs. elided, per language
- Accept that Phase 1 (V1) supports 2-3 languages (TypeScript + Python + one more) rather than 6+
- Add a language-specific "raw analysis" layer below the canonical form for constructs that don't map
- Document explicitly what is lost in translation per language

---

### C-04: No Distribution, Sharding, or Consensus Model for V2→V3 Scaling

**Severity:** Critical
**Panelist:** Netflix Distributed Systems Architect
**Documentation:** Phase_2_System_Architecture_COMBINED.md, Phase_12_02_V2_Roadmap.md, Phase_12_03_V3_Roadmap.md

**Description:**
The architecture is designed as single-node (SQLite, single process, localhost). The V2 plan says "switch to PostgreSQL" and V3 says "cross-repo graph." There is no:
- Sharding strategy (how does the SCM graph partition across machines?)
- Consensus protocol (how do concurrent analyses converge?)
- Conflict resolution (two users run analysis simultaneously — whose evidence wins?)
- Replication model (is the graph leaderless? leader-follower?)
- Query routing (cross-repo queries need to span shards)

A single-node architecture does not "scale to" a distributed architecture. It must be replaced. The SQLite→PostgreSQL migration alone requires rewriting the entire storage layer and query interface.

**Impact:**
V2 and V3 cannot be built on top of V1's architecture. Every storage, query, and consistency assumption changes. The roadmap implies incremental migration but these are architectural breakpoints requiring full rewrites.

**Recommendation:**
- Define the distributed architecture *now* even if V1 doesn't implement it
- Design storage interfaces abstractly so V1's SQLite and V2's PostgreSQL can coexist behind the same contract
- Choose a consensus model (eventual consistency with CRDTs? last-write-wins? vector clocks?)
- Define sharding key (repository ID? entity ID hash?) and query routing strategy upfront
- Accept that V1 is single-node and V2+ is a re-architecture; do not pretend it's a migration

---

### C-05: LLM Claim Extraction from Free-Text Output Is Not Addressed

**Severity:** Critical
**Panelist:** Meta Infrastructure Engineer
**Documentation:** Phase_5_08_Reasoning_Pipeline.md, Phase_5_03_Prompt_Architecture.md

**Description:**
The reasoning pipeline produces insights from evidence by feeding context to an LLM and parsing its output. The architecture requires LLM output to be decomposed into **verifiable claims** that are traced back to evidence. This is an NLP problem (information extraction, NER, relation extraction) running on top of a 3B-8B parameter local model.

Current state-of-the-art open-source models (even 7B-13B) have high hallucination rates (15-35%) on structured extraction tasks. The architecture provides no:
- Constrained decoding or structured output format enforcement
- Post-hoc claim validation against evidence
- Hallucination detection for extracted claims
- Fallback for low-confidence extractions

**Impact:**
The pipeline will produce insights with embedded hallucinated claims that cannot be distinguished from grounded claims. The "evidence-bound output" principle (Principle 3) is violated at the LLM output boundary because there is no mechanism to verify claims against evidence after generation.

**Recommendation:**
- Implement structured output (JSON mode / grammar-constrained decoding) for the reasoning LLM
- Add a post-generation validation stage: extract claims, attempt to ground each in evidence, reject ungroundable claims
- Define hallucination detection: cross-claim consistency checks, confidence calibration
- If Ollama is used, ensure the model supports constrained decoding (llama.cpp grammar, vLLM guided decoding)
- Document the expected hallucination rate and how it degrades insight quality

---

### C-06: V1's Single-Process Architecture Prevents V2 Multi-User Isolation

**Severity:** Critical
**Panelist:** Netflix Distributed Systems Architect
**Documentation:** Phase_6_05_Authentication.md, Phase_6_06_Authorization.md

**Description:**
V1 runs as a single FastAPI process with no process isolation, no auth, and SQLite as a single-writer database. V2 introduces multi-user with JWT auth and RBAC. The architecture assumes auth can be "added later" because the API is designed with auth headers.

However:
- SQLite is single-writer; concurrent reads block on writes
- No session management, rate limiting per user, or resource isolation exists
- RBAC enforcement at the SCM query layer is undefined (SQLite queries can't be filtered by user without application-level interposition)
- WebSocket connections in V1 are a single hub; V2 needs per-user WebSocket routing and subscription isolation

**Impact:**
Adding multi-user to a single-process, single-database, no-auth architecture requires re-architecting the API gateway, storage layer, and WebSocket infrastructure. The auth "headers" are the easy part; the enforcement points throughout the entire stack are not defined.

**Recommendation:**
- Define RBAC enforcement points at every layer (API → Query Service → SCM Storage)
- Design the Query Service abstraction with user context from day one, even if it's a no-op in V1
- SQLite cannot serve multi-user with writes; plan for PostgreSQL or a write-ahead-log-based shared-db architecture
- WebSocket connection management must support per-user multiplexing from the start

---

### C-07: Evidence Conflict Resolution Strategy Is Missing

**Severity:** Critical
**Panelist:** Google Staff Engineer
**Documentation:** Phase_7_07_Evidence_Explorer.md, Phase_3_Software_Cognition_Model_COMBINED.md

**Description:**
Evidence can — and will — conflict. Two engines measuring the same metric produce different values. LLM-generated evidence contradicts deterministic evidence. The UI shows a "conflict" badge but there is no:
- Resolution strategy (confidence-weighted? engine-priority? recency?)
- Evidence supersession model (new evidence replaces old? coexists with staleness tagging?)
- Consensus algorithm for conflicting claims
- User-facing reconciliation workflow

**Impact:**
Conflicting evidence produces conflicting insights, which erodes user trust. Without a resolution model, users will see contradictory "facts" about their codebase with no way to determine which is correct.

**Recommendation:**
- Define a conflict resolution hierarchy (deterministic > probabilistic, higher-confidence > lower, more-recent > less-recent)
- Implement evidence versioning: old evidence is not deleted, it is superseded and linked to its replacement
- For irresolvable conflicts, present both with confidence-weighted display and require user resolution (similar to Git merge conflicts)
- Document staleness: evidence older than N days is demoted in priority

---

### H-01: Ollama as a Hard Dependency with No Cloud Fallback

**Severity:** High
**Panelist:** Meta Infrastructure Engineer
**Documentation:** Phase_5_02_LLM_Architecture.md, Phase_6_02_REST_API.md

**Description:**
The architecture has Ollama as the only LLM provider. The fallback (`POST /v1/reason/question/evidence-summary`) returns raw evidence without reasoning. The system's core value (insights with recommendations) requires the LLM.

Local models at 3B-8B parameters have significant quality gaps vs. cloud models for code reasoning tasks. The architecture offers no path to use cloud models (GPT-4, Claude) even as an opt-in.

**Impact:**
Insight quality is capped by local model capability. Users with real codebase complexity will find insights too shallow or hallucinated. The system cannot improve its reasoning quality without an architectural change.

**Recommendation:**
- Add an abstraction layer for LLM providers (Ollama, OpenAI, Anthropic, etc.) with a pluggable interface
- Define a "reasoning quality tier" mapping: local (fast, shallow), hybrid (local evidence + cloud reasoning), cloud (full)
- Make cloud providers opt-in with clear privacy warnings (Principle 2: Local by Default)
- Ship with Ollama default but document the quality ceiling

---

### H-02: No IPC Contract or Service Boundary Definition for Internal Services

**Severity:** High
**Panelist:** Microsoft Principal Engineer
**Documentation:** Phase_2_System_Architecture_COMBINED.md, Phase_6_01_API_Overview.md

**Description:**
The architecture diagram shows internal services (Query, Reasoning, Analysis Orchestrator, SCM Storage) connected by "Internal IPC." In V1, services are Python modules in the same process. In V2+, they split into separate processes. There is no:
- IPC contract definition (gRPC? message queue? shared memory? REST?)
- Service boundary interface (what is each service's public contract?)
- Service discovery mechanism
- Failure isolation (if Reasoning crashes, does SCM Storage survive?)
- Version negotiation between services

**Impact:**
The V1 implementation will tightly couple services through direct function calls, making the V2+ split a rewrite. Service boundaries will be ambiguous, leading to circular dependencies and implicit contracts.

**Recommendation:**
- Define service interfaces as abstract contracts in V1 (Python ABCs or Protocol classes)
- Use dependency injection to wire services together in V1, making the split straightforward
- Specify the V2 IPC mechanism (recommend gRPC for typed contracts + streaming)
- Define failure semantics: retry policy, circuit breaker thresholds, degradation modes per service

---

### H-03: Frontend Visualization Stack Has Three Overlapping Libraries

**Severity:** High
**Panelist:** Meta Infrastructure Engineer
**Documentation:** Phase_7_05_Graph_Visualization.md

**Description:**
The frontend bundles React Flow, Recharts, and D3.js — all for visualization. React Flow and D3 both do directed graphs. Recharts and D3 both do charts. This is ~400KB+ of visualization code:
- React Flow: ~150KB gzipped
- Recharts: ~80KB gzipped
- D3.js (tree-shaken): ~50KB+ gzipped (core + modules)

The docs specify D3 for "custom visualizations" (timeline, heatmap, force layout) but React Flow's custom node/edge API can handle most of these. Recharts handles standard charts sufficiently.

**Impact:**
Bundle bloat increases initial load time, especially for the Tauri desktop app. Three visualization libraries with overlapping capabilities create confusion about which to use for new visualizations, leading to inconsistent patterns.

**Recommendation:**
- Remove D3.js as a direct dependency. Use React Flow's custom rendering API for graph visualizations and Recharts (or implement in React Flow) for timelines/funnels
- If D3-based force layout is required, wrap it in a React-friendly component and isolate it via code splitting so it's lazy-loaded only when user visits the graph tab
- Set a visualization library budget: max 2 visualization libraries
- Consolidate color scales, layout algorithms, and zoom/pan utilities into a shared visualization utility module

---

### H-04: No Performance Budget or Benchmark Specification for Engines

**Severity:** High
**Panelist:** Meta Infrastructure Engineer
**Documentation:** Phase_9_01_Testing_Overview.md, Phase_9_08_Performance_Testing.md

**Description:**
Phase 9 defines testing levels but provides no specific performance budgets for Cognitive Engines:
- How long should a full analysis take for a 100K-line repo? 500K? 1M?
- What's the memory budget per engine?
- What's the maximum evidence node count before degradation?
- What's the cold-start time (first analysis of a repo)?
- What's the incremental analysis time (single file change)?

The frontend has explicit budgets (FCP < 1.5s, INP < 200ms) but the engine layer, which is the system's computational core, has none.

**Impact:**
Without performance budgets, there is no quality gate for engine implementation. Engines can be correct but unusably slow. The architecture cannot validate its own feasibility claim (running on consumer hardware) without measurable targets.

**Recommendation:**
- Define per-engine performance budgets: max execution time per engine, per file (e.g., structural_cognition: < 500ms per 1000 LOC)
- Define system-level budgets: full analysis < 5min for 500K lines on a 16GB MBP
- Add bench tests that run on CI with sample repos of increasing size
- Define memory budgets per engine and enforce with memory profiling in CI

---

### H-05: Temporal Indexing and Evidence History Strategy Is Not Defined

**Severity:** High
**Panelist:** Google Staff Engineer
**Documentation:** Phase_3_Software_Cognition_Model_COMBINED.md

**Description:**
The SCM model includes temporal indexing (evidence has timestamps, temporal queries are planned) but there is no:
- Data retention policy (how long is evidence kept? does old evidence get pruned?)
- Snapshots vs. streaming (is the SCM state point-in-time snapshot or continuous stream?)
- Time-travel queries (can I query the SCM as it was on July 1?)
- Evidence lifecycle (does evidence ever get deleted? soft-deleted? expired?)
- Storage growth projection (how much storage per 100K lines per day of analysis?)

**Impact:**
Without a data retention and lifecycle model, the SCM database grows unboundedly. Evidence from 2 years ago is as prominent as evidence from 2 minutes ago. Queries over all time become slow. Storage costs for a local machine balloon.

**Recommendation:**
- Define evidence lifecycle: creation → active → stale → archived (or deleted)
- Implement time-to-live (TTL) policies per evidence type or engine
- Add database partitioning by time range (monthly or quarterly partitions)
- Define "active evidence window" (default: last 90 days) for queries, with explicit opt-in for historical queries
- Project storage growth: estimate evidence nodes per day, per engine, and project for 1 year

---

### M-01: No Graceful Degradation Path When Individual Engines Fail

**Severity:** Medium
**Panelist:** Netflix Distributed Systems Architect
**Documentation:** Phase_4_Cognitive_Engines_COMBINED.md

**Description:**
The orchestration DAG runs engines in sequence. If one engine fails (timeout, bug, corrupt input), there is no defined behavior:
- Does the entire analysis fail?
- Does the DAG skip the failed engine and continue?
- Are partial results from earlier engines preserved?
- How does the user know which engines succeeded and which failed?
- Can a failed engine be re-run independently?

**Impact:**
A single engine failure causes either silent data loss (skip) or a blocked pipeline (fail). Neither is a good user experience. Users cannot distinguish "analysis complete, all engines ran" from "analysis complete but risk_cognition failed silently."

**Recommendation:**
- Implement per-engine status tracking: `pending | running | passed | failed | skipped`
- On engine failure: log the error, skip the engine, mark its status as "failed", and continue the DAG
- Report per-engine status in analysis results and via WebSocket events
- Allow users to re-run individual failed engines without restarting the full analysis
- Define which engines are "critical path" (failure blocks dependent engines) vs. "independent" (failure does not block)

---

### M-02: GraphQL in V2 Adds Significant Complexity for Questionable Value

**Severity:** Medium
**Panelist:** Microsoft Principal Engineer
**Documentation:** Phase_6_03_GraphQL_API.md

**Description:**
The docs position GraphQL as V2's flexible query interface. However:
- REST already provides CRUD and paginated queries
- WebSocket already provides real-time streaming
- GraphQL subscriptions build on the WebSocket layer
- The complex traversal examples (entity → evidence → insight) can be achieved with REST batching or a dedicated `GET /v1/traverse` endpoint

Adding GraphQL requires: schema management, resolver layer, DataLoader/N+1 prevention, depth limiting, complexity scoring, persisted queries, federation for V3. This is significant infrastructure for a system that already has three API protocols (REST, WebSocket, CLI).

**Impact:**
GraphQL adds ~30-50% more API infrastructure code for an incremental benefit over batched REST. The architecture suffers from API protocol sprawl (4 protocols: REST, WebSocket, GraphQL, CLI).

**Recommendation:**
- Defer GraphQL to V3 or drop it entirely
- Add a dedicated `GET /v1/traverse?from=X&relationship=Y&depth=Z` REST endpoint to handle complex graph traversal
- Use OpenAPI overfetch is a minor concern for a localhost-only API (bandwidth is free)
- Focus API maintenance budget on REST + WebSocket quality rather than spreading across GraphQL

---

### M-03: CI/CD Pipeline Does Not Address LLM-Dependent Testing

**Severity:** Medium
**Panelist:** Meta Infrastructure Engineer
**Documentation:** Phase_10_05_CI_CD.md, Phase_9_07_AI_Evaluation.md

**Description:**
The CI/CD docs define standard build-test-deploy pipelines but do not address how to test the Reasoning Pipeline (which requires Ollama + an LLM). Running Ollama in CI requires:
- GPU or significant CPU resources (3-8B models need 4-8GB RAM)
- Model download (multiple GB)
- Stochastic output (tests cannot assert exact strings)
- Long inference times (10-30s per query)

The AI Evaluation section mentions "weekly CI" with "statistical thresholds" but doesn't specify how these tests are triggered, what the thresholds are, or how failures are handled.

**Impact:**
The CI pipeline cannot meaningfully test the system's core value proposition (reasoning from evidence). Changes to prompt architecture or LLM configuration won't be caught in CI until the weekly evaluation (1-week feedback loop). Bugs in the reasoning pipeline ship to users.

**Recommendation:**
- Add a CI stage that runs deterministic reasoning tests with a small model (llama3.2:1b or phi-3:mini) and recorded expected outputs
- Define statistical test thresholds: "confidence for test queries must be > 0.6", "hallucination rate < 10%"
- Cache downloaded models in CI (persistent volume or S3)
- For PR pre-submit: run only deterministic engine + SCM tests; reasoning pipeline tests run post-submit with full model
- Store evaluation results over time to detect regressions

---

### M-04: No Circuit Breaker or Resilience Pattern for LLM Dependency

**Severity:** Medium
**Panelist:** Netflix Distributed Systems Architect
**Documentation:** Phase_5_02_LLM_Architecture.md, Phase_6_07_Error_Handling.md

**Description:**
Ollama is treated as a service dependency but there's no:
- Health check polling with degradation signal
- Circuit breaker (if Ollama fails 3 times in 60s, stop trying for 5 minutes)
- Timeout hierarchy (per-query timeout, per-session timeout, per-model timeout)
- Queue management (concurrent LLM requests on a single GPU)
- Graceful degradation (revert to evidence-summary mode)

The error handling docs cover `LLM_UNAVAILABLE` and `MODEL_NOT_FOUND` as HTTP error codes, but the system-level resilience is not designed.

**Impact:**
LLM failures cascade. A single slow query blocks the reasoning service. Repeated failures cause timeouts upstream. Without circuit breaking, the system degrades from "smart insights" to "503 errors" with no intermediate state.

**Recommendation:**
- Implement a circuit breaker for Ollama with configurable thresholds (failure count, time window)
- Add an LLM query queue with configurable concurrency (default: 1 for local GPU)
- Implement per-query timeout (default: 30s), per-analysis timeout (default: 5min)
- On Ollama degradation, automatically fall back to evidence-summary mode with a notification
- Monitor LLM health separately from system health in the `/health` endpoint

---

### M-05: No Data Integrity or Corruption Detection for the SCM Database

**Severity:** Medium
**Panelist:** Netflix Distributed Systems Architect
**Documentation:** Phase_10_08_Backup_and_Recovery.md

**Description:**
The SCM database (SQLite in V1) stores the entire evidence graph. If corruption occurs (disk full, power loss, bug), the database can become unrecoverable. The docs mention backup but not:
- Integrity checking (PRAGMA integrity_check, sha256 of evidence nodes)
- Corruption detection during normal operation
- Repair strategy (can the SCM graph be rebuilt from source re-analysis?)
- Partial corruption isolation (one corrupt page vs. full database loss)

For a system whose value proposition is "a trustworthy model of your codebase," data integrity is existential. A corrupt database means all evidence and insights are suspect.

**Impact:**
A single silent write error or power loss can corrupt the SCM database. Without integrity checks, users trust data that may be partially or fully corrupted. Recovery requires a full re-analysis of the repository.

**Recommendation:**
- Run `PRAGMA integrity_check` on the SCM database at startup and after each analysis
- Store sha256 checksums of evidence node IDs and raw data content for verification
- Implement snapshot-based SCM state: store evidence batch hashes; verify integrity on read
- Design for rebuildability: the SCM graph is derived from source + engines; if corrupt, re-analysis should reproduce the same graph
- Add a "SCM Health" section to the dashboard showing database integrity status
- Use SQLite WAL mode for crash safety (already likely planned but not documented)

---

### M-06: No Explicit Data Model for the Analysis Orchestration DAG

**Severity:** Medium
**Panelist:** Microsoft Principal Engineer
**Documentation:** Phase_4_Cognitive_Engines_COMBINED.md

**Description:**
The orchestration DAG is described in prose: "engines run in sequence, results feed into the next stage." There is no:
- Formal DAG definition (YAML, JSON, or config-driven)
- Engine input/output schema (what does each engine consume and produce?)
- Dependency graph visualization
- Conditional execution (run engine B only if engine A produced evidence of type X)
- Concurrency model (which engines can run in parallel?)

**Impact:**
Engine orchestration will be hardcoded in Python, making it difficult to debug, extend, or reorder. New engines require code changes to the orchestrator rather than DAG configuration.

**Recommendation:**
- Define engine DAG as a declarative configuration (YAML or JSON) with:
  - Engine ID, version, dependencies
  - Input/output schemas (what SCM types does it read/write)
  - Timeout per engine
  - Concurrency group (parallel-safe or serial)
- Implement a DAG executor that parses the config and runs engines accordingly
- This makes the orchestrator testable and new engines configurable without orchestrator changes

---

### M-07: Prompt Architecture References External Files That Are Not Versioned

**Severity:** Medium
**Panelist:** Microsoft Principal Engineer
**Documentation:** Phase_5_03_Prompt_Architecture.md

**Description:**
The prompt architecture document describes prompt templates stored in `prompts/` directory with versioned templates. However, the prompts/ directory is not part of the monorepo structure (Phase 8/03 shows it at root but does not specify versioning or CI testing). Prompts are the most impactful and fragile part of the LLM integration — a single word change can affect all insights.

**Impact:**
Prompt changes are not tracked, tested, or reviewed with the same rigor as code changes. A prompt regression can silently degrade all insights for days before detection.

**Recommendation:**
- Version prompts in the same repository as code, under `prompts/` with semantic versioning
- Add prompt tests: given known input evidence, does the prompt produce expected structured output?
- Implement prompt change review: prompt PRs require AI evaluation results showing no regression
- Track prompt version in evidence metadata: `engine_version + prompt_version` for reproducibility
- Run nightly prompt evaluation on CI against a benchmark dataset

---

### L-01: Tauri + Browser Dual Deployment Is Over-Engineering for V1

**Severity:** Low
**Panelist:** Meta Infrastructure Engineer
**Documentation:** Phase_2_System_Architecture_COMBINED.md, Phase_10_01_Deployment_Overview.md

**Description:**
The architecture commits to both Tauri desktop and browser-based frontend from V1. This duplicates:
- Build configuration (Vite config, Tauri config, CI matrix)
- Distribution (npm + .msi/.dmg/.AppImage)
- Testing (headless browser + Tauri integration tests)
- Security model (browser CORS/SOP vs Tauri IPC)

**Impact:**
Duplicating delivery mechanisms doubles frontend infrastructure work. For V1 (single-user local), browser-only (served by the FastAPI process on localhost) is sufficient.

**Recommendation:**
- Ship browser-only for V1 (the API Gateway serves the frontend at `http://localhost:8000`)
- Add Tauri in V2 when desktop-specific needs arise (system tray, local file system access, background process)
- This eliminates Tauri build complexity, native testing, and distribution concerns for V1

---

### L-02: No Explicit Testing Strategy for Tauri/Native Desktop Features

**Severity:** Low
**Panelist:** Microsoft Principal Engineer
**Documentation:** Phase_9_01_Testing_Overview.md

**Description:**
The testing overview covers unit → integration → validation → AI eval → performance for the backend and frontend React app. There is no testing strategy for:
- Tauri IPC bridge (Rust→JS)
- Native file system access (repository import via OS dialogs)
- Tauri window management (multi-window, tray)
- Tauri update mechanism

**Impact:**
Native features will be untested or tested ad-hoc. Tauri IPC bugs could leak file system access or corrupt repository data.

**Recommendation:**
- Add a testing layer for Tauri-specific features: IPC integration tests, window management smoke tests
- If Tauri is deferred to V2 (per L-01), this is naturally addressed later

---

### L-03: Documentation State Management Has No Code Synchronization

**Severity:** Low
**Panelist:** Google Staff Engineer
**Documentation:** Phase_8_08_Documentation_Standards.md

**Description:**
The docs reference a "Documentation Standards" file (Phase_8/08) that describes how docs are structured and maintained. However, there is no mechanism to verify documentation matches implementation. The 111 documentation issues found in the audit (AUDIT_REPORT.md) highlight this gap.

**Impact:**
Documentation drifts from implementation. Architecture decisions made during implementation are not reflected in docs, misleading future developers and making the review itself less useful over time.

**Recommendation:**
- This is a process recommendation, not architectural. The audit already identified this. No additional action needed beyond the audit's fixes.

---

### L-04: Edge Cases for Very Large Repositories Are Acknowledged but Not Designed

**Severity:** Low
**Panelist:** Google Staff Engineer
**Documentation:** Phase_7_05_Graph_Visualization.md, Phase_9_08_Performance_Testing.md

**Description:**
Several documents mention large-graph concerns (5000+ nodes, 20000+ edges) but defer the actual design:
- "Graph Too Large" shows a warning banner and suggests filtering
- Benchmark section references "curated open-source repos" but doesn't specify which or at what scale
- No maximum supported repository size is defined

**Impact:**
The architecture is designed for "typical" repos (100K-500K lines) but doesn't define what happens at "large" (1M+ lines, 5000+ files). Users with large monorepos will hit undefined behavior.

**Recommendation:**
- Define a supported scale envelope: maximum lines, files, evidence nodes, insights for V1
- Document expected performance at the envelope boundary
- Add a "scale warning" in the UI when repos exceed documented limits
- Define the architectural bottleneck that determines the limit (likely SQLite single-writer throughput)

---

## Summary of Recommendations by Priority

### Critical (7 findings — must fix before V1 implementation)

| ID | Finding | Panelist |
|---|---|---|
| C-01 | Graph engine correctness — NP-hard assumptions undocumented | Google |
| C-02 | Incremental analysis at AST-node granularity is unsolved | Google |
| C-03 | Multi-language AST canonical unification under-specified | Microsoft |
| C-04 | No distribution/sharding/consensus for V2→V3 | Netflix |
| C-05 | LLM claim extraction from free-text output not addressed | Meta |
| C-06 | V1 single-process architecture prevents V2 multi-user | Netflix |
| C-07 | Evidence conflict resolution strategy is missing | Google |

### High (5 findings — should fix before V1 launch)

| ID | Finding | Panelist |
|---|---|---|
| H-01 | Ollama hard dependency with no cloud fallback | Meta |
| H-02 | No IPC contract for internal services | Microsoft |
| H-03 | Frontend visualization stack 3 overlapping libraries | Meta |
| H-04 | No performance budgets for engines | Meta |
| H-05 | Temporal indexing and evidence history undefined | Google |

### Medium (7 findings — plan to fix in V1 or early V2)

| ID | Finding | Panelist |
|---|---|---|
| M-01 | No graceful degradation when engines fail | Netflix |
| M-02 | GraphQL adds complexity for questionable value | Microsoft |
| M-03 | CI/CD doesn't address LLM-dependent testing | Meta |
| M-04 | No circuit breaker for LLM dependency | Netflix |
| M-05 | No data integrity detection for SCM database | Netflix |
| M-06 | No explicit data model for orchestration DAG | Microsoft |
| M-07 | Prompt architecture not versioned/tested in CI | Microsoft |

### Low (4 findings — track but can defer)

| ID | Finding | Panelist |
|---|---|---|
| L-01 | Tauri + Browser dual deployment is over-engineering | Meta |
| L-02 | No testing strategy for native/Tauri features | Microsoft |
| L-03 | Documentation has no code synchronization | Google |
| L-04 | Large-repo edge cases acknowledged but not designed | Google |

---

## Panel Closing Statements

**Google Staff Engineer:**
"The deterministic-first principle is the right call. But deterministic algorithms still have complexity ceilings, and the architecture does not acknowledge them. The graph engine claims determinism for problems that require approximation. The incremental analysis design, if attempted at AST-node granularity, will be the project's hardest engineering challenge — it is harder than the LLM integration. I recommend starting with file-level incrementality and proving correctness before attempting finer granularity."

**Microsoft Principal Engineer:**
"The module boundaries and engineering principles are well-structured. However, the architecture has multiple implicit service interfaces that will become rewrite blockers. The internal IPC contracts, engine DAG format, and LLM provider abstraction should be defined as interfaces before implementation begins — even if V1 uses direct function calls. The GraphQL addition is premature; simplify the API surface to REST + WebSocket and defer. The prompt versioning gap is a silent regression risk."

**Meta Infrastructure Engineer:**
"The frontend architecture is solid — React Query + Zustand is a proven combination. But the visualization stack has library bloat (React Flow + Recharts + D3 = 3 libraries with overlapping capability). Choose two at most. The hard dependency on Ollama without cloud fallback caps insight quality. If this is a local-first product, own that constraint and design within it — do not pretend local 7B models match cloud 200B models. Add performance budgets for engines before implementation begins, or you will ship an unusably slow app."

**Netflix Distributed Systems Architect:**
"This is a single-node architecture pretending to have a multi-node future. The V2 roadmap (PostgreSQL, multi-user, RBAC) is a complete rewrite from V1's SQLite single-process design — not a migration. The lack of consensus, conflict resolution, data integrity, and circuit breaking will be painful in production. The architecture should either commit to single-user-local as the permanent state and optimize for that, or design the distributed abstractions from day one. V2 cannot be layered on top of V1's architectural decisions."
