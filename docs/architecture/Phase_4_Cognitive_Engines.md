================================================================================
# 01 Cognitive Engines Overview
================================================================================

# Cognitive Engines — Overview

## The Perception Layer of Project DNA

Cognitive Engines are the deterministic, testable modules that perceive software systems across multiple dimensions. They transform raw repository data — code, history, dependencies — into structured evidence that populates the Software Cognition Model. Without engines, the SCM is empty. With engines, it becomes a living understanding.

Every engine is independent, deterministic, and evidence-producing. They are the sensory organs of Project DNA.

---

## What Cognitive Engines Are

Cognitive Engines are specialized perception modules that:

1. **Analyze** one dimension of a software system (structure, history, dependencies, etc.).
2. **Produce** structured, deterministic evidence.
3. **Write** evidence to the SCM through a standardized interface.
4. **Declare** their dependencies on other engines and pipeline stages.
5. **Version** their algorithms for reproducibility.

---

## What Cognitive Engines Are Not

| Engines Are Not | Why |
|---|---|
| AI models | Engines are deterministic algorithms. AI reasoning sits above them. |
| Black boxes | Every engine's output is inspectable, testable, and reproducible. |
| Monolithic | Each engine is independent and replaceable. |
| Opinionated | Engines produce facts. Context and meaning come from the Reasoning Layer. |
| One-time tools | Engines run continuously, incrementally updating evidence as code changes. |

---

## Engine Architecture

```
Engine Interface (Protocol)
  - run(repository, config) -> Evidence[]
  - get_dependencies() -> Engine[]
  - get_version() -> string
  - get_evidence_schema() -> Schema

Engine Implementation
  - Input: Processed data from Pipeline
  - Algorithm: Deterministic logic
  - Output: Structured evidence nodes

Engine Registry
  - Discovery, scheduling, execution
  - Dependency resolution, parallelization
  - Progress tracking, error handling
```

---

## Engine Interface Contract

Every engine must implement:

```python
class CognitiveEngine(Protocol):
    def get_name(self) -> str:
        # Unique engine identifier
        ...

    def get_version(self) -> str:
        # Semantic version of engine algorithm
        ...

    def get_dependencies(self) -> List[str]:
        # Names of engines that must run before this one
        ...

    def get_input_schema(self) -> Schema:
        # Schema of processed data this engine requires
        ...

    def get_evidence_schema(self) -> Schema:
        # Schema of evidence this engine produces
        ...

    def run(self, repository: Repository, 
            processed_data: ProcessedData,
            scm: SCMWriter) -> EngineResult:
        # Execute engine, write evidence to SCM, return result
        ...

    def is_incremental(self) -> bool:
        # Whether engine supports incremental updates
        ...
```

---

## Engine Lifecycle

```
[Registered] -> [Scheduled] -> [Running] -> [Completed] -> [Evidence Stored]
                |                |
            [Blocked]        [Failed] -> [Retry] or [Skip]
            (waiting for     (error logged,
             dependencies)    partial evidence if possible)
```

---

## Engine Orchestration

### Dependency Resolution
Engines declare dependencies. The orchestrator builds a DAG and executes in topological order.

```
RepositoryDiscovery -> GitMining -> FileIndexing
                                           |
ASTParsing -> DependencyResolution -> MetricCalculation
                                           |
        +----------+----------+----------+----------+
        |          |          |          |          |
        v          v          v          v          v
   Structural  Evolution  Knowledge  Dependency  Risk
   Cognition   Cognition  Cognition   Cognition  Cognition
        |          |          |          |          |
        +----------+----------+----------+----------+
                           |
                   Architectural Cognition
                           |
                   Decision Cognition
                           |
                   Prediction Cognition
```

### Parallel Execution
Engines with no mutual dependencies run in parallel:
- Structural, Evolution, Knowledge, Dependency, Risk Cognition can run simultaneously after Metric Calculation.
- Architectural Cognition requires Structural + Dependency.
- Decision and Prediction require all preceding engines.

### Incremental Execution
On subsequent runs, only changed files trigger re-execution:
- Changed files -> affected ASTs -> affected metrics -> affected evidence.
- Downstream engines re-run only if their input evidence changed.
- Unchanged evidence is carried forward.

---

## Engine Categories

| Category | Engines | Purpose |
|---|---|---|
| **Structural** | Structural Cognition | Code structure, dependencies, coupling |
| **Evolutionary** | Evolution Cognition | History, growth, refactoring, trends |
| **Social** | Knowledge Cognition, Collaboration Cognition (V2) | Ownership, expertise, team dynamics |
| **Dependency** | Dependency Cognition | Internal/external dependencies, vulnerabilities |
| **Quality** | Risk Cognition, Architectural Cognition | Risk assessment, pattern detection, erosion |
| **Strategic** | Decision Cognition, Prediction Cognition | Option evaluation, forecasting |
| **Security** | Security Cognition (V2) | Vulnerability context, blast radius |
| **Operational** | Operational Cognition (V3) | Runtime correlation, incident context |

---

## Evidence Output Standard

Every engine produces evidence nodes conforming to:

```python
EvidenceNode {
    id: UUID
    type: string (from taxonomy)
    category: EvidenceCategory
    value: JSONB (structured data)
    confidence: ConfidenceLevel
    source: {
        engine: string
        version: string
        timestamp: datetime
    }
    raw_data: {
        type: RawDataType
        ref: string
        content_hash: string
    }
    affected_entities: UUID[]
}
```

---

## The Cognitive Engines Doctrine

> **Cognitive Engines are the senses of Project DNA. They perceive software across all dimensions — structure, history, people, dependencies — and transform raw data into structured evidence. They are deterministic, testable, and independent. They do not reason. They do not explain. They perceive. The understanding they produce is the foundation upon which all reasoning rests.**



================================================================================
# 02 Structural Cognition Engine
================================================================================

# Structural Cognition Engine

## Understanding Code Structure

The Structural Cognition Engine perceives the physical and logical structure of software — files, modules, functions, classes, and the relationships between them. It transforms parsed ASTs and dependency graphs into structured evidence about how the code is organized, how components connect, and where structural risks may exist.

---

## Scope

### In Scope
- File and directory structure
- Module and package organization
- Function, class, and interface definitions
- Import/export relationships
- Call graphs
- Inheritance hierarchies
- Coupling and cohesion metrics
- Complexity metrics (cyclomatic, cognitive)

### Out of Scope
- Git history (Evolution Cognition)
- Author expertise (Knowledge Cognition)
- External package vulnerabilities (Dependency Cognition)
- Architectural pattern detection (Architectural Cognition)
- Runtime behavior (Operational Cognition V3+)

---

## Input

| Input | Source | Format |
|---|---|---|
| Parsed ASTs | AST Parsing Pipeline | Tree-sitter CST/AST |
| File inventory | File Indexing Pipeline | File metadata list |
| Import maps | Dependency Resolution Pipeline | Resolved import graph |
| Symbol tables | AST Parsing Pipeline | Per-file symbol definitions |

---

## Algorithm

### Stage 1: Entity Extraction
Traverse ASTs to extract:
- Files, directories, modules
- Classes, interfaces, enums
- Functions, methods, constructors
- Variables, constants
- Import/export statements

### Stage 2: Relationship Building
Build edges between entities:
- CONTAINS: Module -> File -> Class -> Function
- CALLS: Function -> Function
- INHERITS_FROM: Class -> Class
- IMPLEMENTS: Class -> Interface
- IMPORTS: File -> Module/Package
- DEPENDS_ON: Module -> Module (aggregated)

### Stage 3: Metric Calculation
Compute per-entity metrics:
- **Cyclomatic Complexity:** Decision points + 1
- **Cognitive Complexity:** Nested complexity penalties
- **Lines of Code:** Physical and logical
- **Function Count:** Per class/module
- **Dependency Count:** In-degree and out-degree
- **Fan-in / Fan-out:** Incoming/outgoing connections

### Stage 4: Coupling and Cohesion
- **Afferent Coupling (Ca):** Number of modules depending on this module.
- **Efferent Coupling (Ce):** Number of modules this module depends on.
- **Instability (I):** Ce / (Ca + Ce). 0 = stable, 1 = unstable.
- **Lack of Cohesion in Methods (LCOM):** Measure of class cohesion.

### Stage 5: Evidence Generation
Produce evidence nodes:
- module_structure: Hierarchy and containment
- dependency_graph: Module-level dependencies
- call_graph: Function-level calls
- complexity_metrics: Per-function/file complexity
- coupling_metrics: Ca, Ce, I per module
- cohesion_metrics: LCOM per class
- size_metrics: LOC, function count

---

## Output Evidence

| Evidence Type | Description | Example Value |
|---|---|---|
| module_structure | Containment hierarchy | {modules: [...], files: [...], depth: 4} |
| dependency_graph | Module dependencies | {nodes: 12, edges: 34, circular: [...]} |
| call_graph | Function calls | {nodes: 156, edges: 423, recursion: [...]} |
| complexity_metrics | Complexity values | {cyclomatic: 28, cognitive: 45, file: PaymentService.java} |
| coupling_metrics | Coupling values | {ca: 5, ce: 3, instability: 0.375} |
| cohesion_metrics | Cohesion values | {lcom: 0.3, class: PaymentProcessor} |
| size_metrics | Size values | {loc: 1200, functions: 24, classes: 3} |

---

## Complexity Thresholds (Contextual)

The engine does not flag complexity as good or bad. It produces evidence. Thresholds for risk assessment belong in the Risk Cognition Engine.

However, the engine records typical ranges for reference:

| Metric | Typical Range | High Range | Very High |
|---|---|---|---|
| Cyclomatic Complexity (function) | 1-10 | 11-20 | >20 |
| Cognitive Complexity (function) | 1-15 | 16-30 | >30 |
| LOC (file) | 50-300 | 300-500 | >500 |
| Functions (class) | 5-15 | 15-25 | >25 |
| Dependencies (module) | 3-10 | 10-20 | >20 |

---

## Performance Targets

| Repository Size | Target Time |
|---|---|
| < 100K LOC | < 30 seconds |
| 100K-500K LOC | < 2 minutes |
| 500K-1M LOC | < 5 minutes |
| > 1M LOC | < 10 minutes |

---

## The Structural Cognition Doctrine

> **Structure is the skeleton of software. The Structural Cognition Engine maps that skeleton — every bone, every joint, every connection. It does not judge whether the skeleton is healthy. It makes the skeleton visible so that judgment can be informed.**



================================================================================
# 03 Evolution Cognition Engine
================================================================================

# Evolution Cognition Engine

## Understanding How Software Changes

The Evolution Cognition Engine perceives the history of a software system — how it has grown, changed, degraded, and been refactored over time. It transforms Git history into structured evidence about trends, patterns, and trajectories that are invisible in any single snapshot.

---

## Scope

### In Scope
- Commit history analysis
- Code growth trends (size, complexity, feature count)
- Refactoring detection
- Change frequency and churn
- Velocity trends
- Architectural drift detection
- Hotspot identification (frequently changed, complex files)
- Temporal coupling (files changed together)

### Out of Scope
- Author expertise (Knowledge Cognition)
- Current structure analysis (Structural Cognition)
- External dependencies (Dependency Cognition)
- Pattern detection (Architectural Cognition)

---

## Input

| Input | Source | Format |
|---|---|---|
| Commit history | Git Mining Pipeline | Parsed commit objects |
| File change stats | Git Mining Pipeline | Per-commit file changes |
| Current metrics | Structural Cognition Engine | Complexity, size metrics |
| AST snapshots | AST Parsing Pipeline | Historical ASTs (if available) |

---

## Algorithm

### Stage 1: Commit Analysis
Parse and categorize commits:
- **Feature:** New functionality (keywords: feat, add, implement)
- **Fix:** Bug fixes (keywords: fix, bug, patch)
- **Refactor:** Code restructuring (keywords: refactor, clean, rename)
- **Test:** Test additions/changes (keywords: test, spec)
- **Docs:** Documentation (keywords: doc, readme)
- **Chore:** Maintenance (keywords: chore, update, bump)

### Stage 2: Growth Analysis
Track metrics over time:
- Total LOC
- Number of files
- Number of functions/classes
- Average complexity
- Test coverage (if available)

### Stage 3: Hotspot Detection
Identify files that are both complex and frequently changed:
```
hotspot_score(file) = complexity(file) * change_frequency(file)
```
Files in top 10% of hotspot score are flagged.

### Stage 4: Refactoring Detection
Detect refactoring events from commit patterns:
- Large deletions + additions (rewrite)
- File renames with similar content (move/rename)
- Extract method (new function, reduced complexity in caller)
- Inline method (opposite pattern)
- Rename variable/function (consistent token changes)

### Stage 5: Temporal Coupling
Identify files that change together frequently:
```
temporal_coupling(file_a, file_b) = 
    commits_touching_both / commits_touching_either
```
High temporal coupling (>0.5) suggests hidden dependencies.

### Stage 6: Trend Analysis
Fit trends to metric time-series:
- Linear regression for steady trends
- Change-point detection for sudden shifts
- Seasonal decomposition for periodic patterns

### Stage 7: Evidence Generation
Produce evidence nodes:
- growth_trend: LOC, complexity, file count over time
- commit_distribution: Commit types over time
- hotspot_list: Files with high complexity * frequency
- refactoring_events: Detected refactoring occurrences
- temporal_coupling: File pairs that change together
- velocity_trend: Commits, PRs, releases over time
- architectural_drift: Changes to dependency structure over time

---

## Output Evidence

| Evidence Type | Description | Example Value |
|---|---|---|
| growth_trend | Size/complexity over time | {slope_loc: 120, slope_complexity: 2.3} |
| commit_distribution | Commit types | {feature: 0.45, fix: 0.30, refactor: 0.10} |
| hotspot_list | High-risk files | {file: PaymentService.java, score: 840} |
| refactoring_events | Detected refactors | {type: extract_method, file: ..., commit: abc123} |
| temporal_coupling | Co-changing files | {file_a: A.java, file_b: B.java, coupling: 0.72} |
| velocity_trend | Development speed | {commits_per_week: 23, trend: stable} |
| architectural_drift | Structural changes | {new_dependencies: 3, removed_dependencies: 1} |

---

## Refactoring Detection Heuristics

| Pattern | Signals | Confidence |
|---|---|---|
| Extract Method | New function, caller complexity drops, similar lines moved | High |
| Inline Method | Function deleted, caller complexity rises, lines merged | Medium |
| Rename | File/function renamed, content similarity >80% | High |
| Move | File moved, content similarity >90%, imports updated | High |
| Large Rewrite | >50% lines changed, structure preserved | Medium |
| Split Module | New files, old file shrinks, imports redistributed | Medium |

---

## Performance Targets

| Repository Size | Target Time |
|---|---|
| < 10K commits | < 30 seconds |
| 10K-50K commits | < 2 minutes |
| 50K-100K commits | < 5 minutes |
| > 100K commits | < 10 minutes |

---

## The Evolution Cognition Doctrine

> **Software is a process, not a snapshot. The Evolution Cognition Engine reveals that process — how code grows, how complexity accumulates, how refactoring happens, and how yesterday's decisions constrain today's options. Without evolution, understanding is frozen in time. With it, understanding lives.**



================================================================================
# 04 Knowledge Cognition Engine
================================================================================

# Knowledge Cognition Engine

## Understanding Who Understands

The Knowledge Cognition Engine perceives the distribution of expertise across a software system and its team. It transforms Git history and code authorship into structured evidence about who knows what, where knowledge is concentrated, where it is missing, and what risks exist when expertise is lost.

---

## Scope

### In Scope
- Author contribution analysis
- Primary and secondary ownership detection
- Bus factor calculation
- Expertise depth and breadth scoring
- Knowledge gap identification
- Onboarding difficulty estimation
- Team knowledge distribution

### Out of Scope
- Code structure (Structural Cognition)
- Historical trends (Evolution Cognition)
- Team dynamics (Collaboration Cognition V2)
- Performance evaluation (explicitly forbidden by Privacy Ethics)

---

## Input

| Input | Source | Format |
|---|---|---|
| Commit history | Git Mining Pipeline | Author, file, line changes per commit |
| Code structure | Structural Cognition Engine | Module/file hierarchy |
| Review data (V2) | GitHub/GitLab API | Reviewer, file, comments |
| Documentation authorship | File analysis | Doc file authors |

---

## Algorithm

### Stage 1: Contribution Analysis
For each author and module/file:
- Total commits
- Lines added/removed
- First commit date (tenure start)
- Last commit date (recency)
- Commit message quality (length, references)

### Stage 2: Ownership Detection
Determine primary and secondary owners:

**Primary Owner:**
```
ownership_score(author, module) = 
    0.4 * commit_share + 
    0.3 * line_share + 
    0.2 * recency_weight + 
    0.1 * tenure_weight

primary_owner = argmax(ownership_score)
```

**Secondary Owners:**
Authors with ownership_score > 0.2 (configurable threshold).

### Stage 3: Expertise Scoring

**Depth Score** (understanding of this specific module):
```
depth = 0.5 * ownership_score +
        0.2 * refactoring_participation +
        0.2 * review_depth (V2) +
        0.1 * documentation_contribution
```

**Breadth Score** (understanding of surrounding system):
```
breadth = 0.4 * cross_module_commits +
          0.3 * dependency_awareness +
          0.2 * architectural_participation +
          0.1 * mentoring_events (V2)
```

### Stage 4: Bus Factor Calculation
```
bus_factor(module) = count of authors where:
    depth_score > 0.5 AND
    last_commit < 90 days ago AND
    not marked as inactive
```

### Stage 5: Knowledge Gap Detection
Identify modules with:
- bus_factor == 0 (orphaned)
- bus_factor == 1 (single point of failure)
- primary_owner.tenure < 30 days (new owner, unstable)
- max(depth_score) < 0.5 (no deep expertise)

### Stage 6: Onboarding Difficulty
Estimate time for new engineer to become productive:
```
onboarding_difficulty(module) = 
    0.3 * complexity +
    0.2 * (1 - documentation_coverage) +
    0.2 * (1 - test_coverage) +
    0.15 * dependency_count +
    0.15 * (1 / bus_factor)
```

### Stage 7: Knowledge Distribution
Compute Gini coefficient of expertise across team:
```
gini = 1 - 2 * integral(Lorenz curve)
```
- 0.0 = perfectly distributed
- 1.0 = perfectly concentrated
- Target for critical modules: < 0.6

### Stage 8: Evidence Generation
Produce evidence nodes:
- ownership_map: Primary/secondary owners per module
- expertise_profile: Depth and breadth per author-module pair
- bus_factor: Bus factor per module
- knowledge_gap: Modules with knowledge risks
- onboarding_difficulty: Estimated days to productivity
- knowledge_distribution: Gini coefficient per module/team

---

## Output Evidence

| Evidence Type | Description | Example Value |
|---|---|---|
| ownership_map | Module ownership | {module: PaymentService, primary: Alex, secondary: [Sarah]} |
| expertise_profile | Author expertise | {author: Alex, module: PaymentService, depth: 0.85, breadth: 0.62} |
| bus_factor | Bus factor | {module: PaymentService, bus_factor: 1, risk: high} |
| knowledge_gap | Knowledge risks | {module: AuthService, gap_type: orphaned, severity: critical} |
| onboarding_difficulty | Onboarding estimate | {module: PaymentService, estimated_days: 14} |
| knowledge_distribution | Expertise concentration | {module: PaymentService, gini: 0.78, risk: high} |

---

## Privacy and Ethics

The Knowledge Cognition Engine adheres strictly to Phase 0: Privacy & Ethics:

- **No individual performance evaluation.** Scores are relative to modules, not absolute measures of developer ability.
- **Aggregated reporting.** Knowledge maps show team-level patterns, not individual rankings.
- **Contextual interpretation.** A low depth score means this module needs more contributors, not this developer is incompetent.
- **No gamification.** No badges, leaderboards, or productivity scores.
- **User control.** Engineers can opt out of knowledge tracking (their contributions are anonymized).

---

## The Knowledge Cognition Doctrine

> **Knowledge is the invisible infrastructure of software. The Knowledge Cognition Engine makes it visible — who understands what, where understanding is fragile, and what happens when it is lost. It treats knowledge as a property of the system, not a scorecard for individuals. It enables teams to become resilient.**



================================================================================
# 05 Dependency Cognition Engine
================================================================================

# Dependency Cognition Engine

## Understanding What Software Needs

The Dependency Cognition Engine perceives the internal and external dependencies of a software system — what it needs to function, how those needs are connected, and what risks exist in the dependency graph. It transforms package manifests, lock files, and import graphs into structured evidence about dependency health, stability, and vulnerability.

---

## Scope

### In Scope
- Internal dependency graph (module-to-module)
- External dependency inventory (packages, versions)
- Transitive dependency analysis
- Dependency age and staleness
- Circular dependency detection
- Dependency update frequency
- Vulnerability mapping (CVE to package)
- License compliance (V2)

### Out of Scope
- Vulnerability scanning (Security Cognition V2)
- Runtime dependency behavior (Operational Cognition V3)
- Dependency resolution algorithms (handled by package managers)
- Build system integration

---

## Input

| Input | Source | Format |
|---|---|---|
| Import graph | Structural Cognition Engine | File/module import map |
| Package manifests | File system | package.json, requirements.txt, Cargo.toml, etc. |
| Lock files | File system | package-lock.json, Cargo.lock, poetry.lock, etc. |
| Vulnerability DB (V2) | External API (opt-in) | CVE feeds, OSV |

---

## Algorithm

### Stage 1: Internal Dependency Graph
Build from import statements:
- File-level imports -> module-level dependencies
- Weight edges by import frequency
- Detect circular dependencies (DFS with cycle detection)
- Compute dependency depth (longest path from entry point)

### Stage 2: External Dependency Inventory
Parse package manifests:
- Direct dependencies (name, version constraint)
- Dev dependencies
- Peer dependencies
- Optional dependencies

Parse lock files for exact versions:
- Resolved version
- Transitive closure
- Dependency tree depth

### Stage 3: Dependency Health Scoring
For each external dependency:
- **Age:** Days since last release
- **Staleness:** Versions behind latest
- **Update Frequency:** Releases per year
- **Adoption:** Download count (if available, V2)
- **Maintenance:** Last commit date, open issues (V2)
- **License:** Compatibility with project license

### Stage 4: Risk Assessment
- **High Risk:** Unmaintained (>2 years), deprecated, major version behind
- **Medium Risk:** Minor version behind, low update frequency
- **Low Risk:** Up-to-date, actively maintained

### Stage 5: Impact Analysis
For each dependency:
- **Direct dependents:** Modules that import it directly
- **Transitive dependents:** All modules affected if removed
- **Blast radius:** Count of files/modules that would break

### Stage 6: Evidence Generation
Produce evidence nodes:
- internal_dependency_graph: Module-to-module dependencies
- external_dependency_inventory: All external packages
- circular_dependencies: Detected cycles
- dependency_health: Health scores per package
- vulnerability_mapping: CVE to package to module (V2)
- dependency_risk: Risk assessment per dependency
- blast_radius: Impact analysis per dependency

---

## Output Evidence

| Evidence Type | Description | Example Value |
|---|---|---|
| internal_dependency_graph | Module dependencies | {nodes: 12, edges: 34, circular: [A->B->C->A]} |
| external_dependency_inventory | External packages | {name: lodash, version: 4.17.21, latest: 4.17.21} |
| circular_dependencies | Cycles | {cycle: [A, B, C], files: [a.js, b.js, c.js]} |
| dependency_health | Health scores | {package: old-lib, age_days: 892, risk: high} |
| vulnerability_mapping | CVE links (V2) | {cve: CVE-2024-1234, package: old-lib, severity: high} |
| dependency_risk | Risk summary | {high: 3, medium: 8, low: 45} |
| blast_radius | Impact scope | {package: stripe, direct: 5, transitive: 12} |

---

## Dependency Health Thresholds

| Metric | Healthy | Warning | At Risk |
|---|---|---|---|
| Age since last release | < 6 months | 6-12 months | > 12 months |
| Versions behind latest | 0 | 1 minor | 1+ major |
| Update frequency | > 4/year | 1-4/year | < 1/year |
| Transitive depth | < 5 | 5-10 | > 10 |
| Circular dependencies | 0 | 1-2 | > 2 |

---

## The Dependency Cognition Doctrine

> **Dependencies are the connective tissue of software — internal and external, visible and hidden. The Dependency Cognition Engine maps that tissue, measures its health, and reveals where a single cut could cause systemic failure. It answers: What does this system need? What needs it? And what happens if that need is not met?**



================================================================================
# 06 Risk Cognition Engine
================================================================================

# Risk Cognition Engine

## Understanding Where Software Breaks

The Risk Cognition Engine perceives fragility in software systems. It synthesizes evidence from all other engines — structure, evolution, knowledge, dependencies — to identify where the system is likely to fail, why, and when. Risk is not a single metric. It is a contextual assessment that combines multiple indicators into a unified understanding of fragility.

---

## Scope

### In Scope
- Complexity risk (high and growing complexity)
- Knowledge risk (bus factor, knowledge gaps)
- Dependency risk (outdated, vulnerable, circular dependencies)
- Evolution risk (declining velocity, accumulating debt)
- Architectural risk (boundary violations, erosion)
- Change risk (high change frequency on fragile code)
- Composite risk scoring
- Risk forecasting (when will this become critical)

### Out of Scope
- Security vulnerability scanning (Security Cognition V2)
- Runtime failure prediction (Operational Cognition V3)
- Business risk assessment

---

## Input

| Input | Source | Format |
|---|---|---|
| Complexity metrics | Structural Cognition | Cyclomatic, cognitive complexity |
| Hotspots | Evolution Cognition | Complexity * frequency |
| Bus factor | Knowledge Cognition | Knowledge distribution |
| Dependency health | Dependency Cognition | Package health scores |
| Growth trends | Evolution Cognition | LOC, complexity trajectories |
| Boundary violations | Architectural Cognition | Pattern drift |

---

## Algorithm

### Stage 1: Risk Indicator Collection
Gather risk indicators from all engines:

| Indicator | Source | Weight |
|---|---|---|
| Complexity trend | Structural + Evolution | 0.20 |
| Hotspot score | Evolution | 0.20 |
| Bus factor | Knowledge | 0.20 |
| Dependency risk | Dependency | 0.15 |
| Change frequency | Evolution | 0.10 |
| Test coverage trend | Structural + Evolution | 0.10 |
| Architectural drift | Architectural | 0.05 |

### Stage 2: Contextual Risk Scoring
Risk is not universal. The same complexity score means different things in different contexts:

```
risk_score(module) = base_risk * context_multiplier

base_risk = weighted_sum(indicators)

context_multiplier = f(
    module.criticality,      # How central is this module?
    module.stability,        # How often does it change?
    module.test_coverage,    # How well is it protected?
    module.documentation,    # How well is it explained?
    team.expertise           # How well is it understood?
)
```

### Stage 3: Risk Classification
```
if risk_score > 0.8:   critical
elif risk_score > 0.6: high
elif risk_score > 0.4: medium
else:                  low
```

### Stage 4: Risk Forecasting
Predict when risk will become critical:
```
time_to_critical(module) = 
    (0.9 - current_risk) / risk_velocity

where risk_velocity = slope of risk_score over last 90 days
```

### Stage 5: Causal Attribution
Identify root causes of risk:
- Risk is high because complexity increased 40% while test coverage remained flat.
- Risk is high because bus factor dropped from 2 to 1 after Sarah's departure.
- Risk is high because this module depends on 3 outdated packages with known vulnerabilities.

### Stage 6: Evidence Generation
Produce evidence nodes:
- risk_assessment: Overall risk score and classification
- risk_indicators: Individual indicator scores
- risk_forecast: Time to critical with confidence interval
- risk_causes: Causal attribution with evidence chain
- risk_trend: Risk score history
- affected_modules: Modules at risk

---

## Output Evidence

| Evidence Type | Description | Example Value |
|---|---|---|
| risk_assessment | Overall risk | {module: PaymentService, score: 0.82, level: critical} |
| risk_indicators | Component scores | {complexity: 0.9, knowledge: 0.7, dependency: 0.6} |
| risk_forecast | Future prediction | {time_to_critical: 4 months, confidence: 0.75} |
| risk_causes | Root causes | {primary: complexity_growth, secondary: knowledge_loss} |
| risk_trend | Historical risk | {slope: 0.05, direction: increasing} |
| affected_modules | At-risk modules | [PaymentService, OrderService, AnalyticsService] |

---

## Risk Context Multipliers

| Context | Multiplier Effect | Example |
|---|---|---|
| High criticality (many dependents) | x1.5 | Payment service used by 5 modules |
| Low test coverage (<40%) | x1.3 | No tests for retry logic |
| High change frequency (>weekly) | x1.2 | Modified in 80% of sprints |
| Low documentation (<20%) | x1.1 | No README, no inline docs |
| Stable (rarely changed) | x0.7 | Utility function, unchanged for 2 years |
| Well-tested (>80%) | x0.8 | Comprehensive test suite |
| Multiple knowledgeable owners | x0.8 | Bus factor 3+ |

---

## The Risk Cognition Doctrine

> **Risk is not a number. It is a story — a story about how complexity, knowledge, dependencies, and evolution converge to create fragility. The Risk Cognition Engine tells that story with evidence, context, and foresight. It does not just flag problems. It explains why they matter, when they will become critical, and what can be done about them.**



================================================================================
# 07 Architectural Cognition Engine
================================================================================

# Architectural Cognition Engine

## Understanding Design Intent and Drift

The Architectural Cognition Engine perceives the architecture of a software system — the patterns, layers, boundaries, and conventions that govern its structure. It detects how the system was designed to be organized, how it has drifted from that design, and where architectural erosion threatens maintainability.

---

## Scope

### In Scope
- Architectural pattern detection (Clean Architecture, Microservices, MVC, DDD, etc.)
- Layer identification and validation
- Boundary detection and violation tracking
- Architectural drift measurement
- Pattern consistency analysis
- Interface stability tracking
- Abstraction depth analysis

### Out of Scope
- Code-level complexity (Structural Cognition)
- Historical growth trends (Evolution Cognition)
- Runtime architecture (Operational Cognition V3)
- Infrastructure architecture (DevOps tools)

---

## Input

| Input | Source | Format |
|---|---|---|
| Module graph | Structural Cognition | Dependency graph |
| File structure | Structural Cognition | Directory tree |
| Import patterns | Structural Cognition | Import/export map |
| Naming conventions | File analysis | File/class/function names |
| Configuration files | File system | Framework configs, DI configs |
| Historical snapshots | SCM Temporal Store | Past architecture states |

---

## Algorithm

### Stage 1: Pattern Detection
Identify architectural patterns from evidence:

| Pattern | Signals |
|---|---|
| **Clean Architecture** | entities/, usecases/, interfaces/, frameworks/ layers; dependencies point inward |
| **Microservices** | Multiple service directories, independent deploy units, API boundaries |
| **MVC** | models/, views/, controllers/ directories; controller->model->view flow |
| **DDD** | domain/, application/, infrastructure/ layers; aggregate roots, entities, value objects |
| **Layered** | presentation/, business/, data/ layers; strict downward dependencies |
| **Hexagonal** | domain/, ports/, adapters/ structure; dependency inversion |
| **Monolith** | Single deploy unit, shared database, internal module coupling |

### Stage 2: Layer Identification
Map files/modules to architectural layers:
```
layer(file) = f(directory_path, imports, naming_convention, config)
```

### Stage 3: Boundary Detection
Identify architectural boundaries:
- Domain boundaries (DDD)
- Service boundaries (Microservices)
- Layer boundaries (Clean Architecture)
- Module boundaries (Package structure)

Boundaries are inferred from:
- Directory structure
- Dependency patterns
- Naming conventions
- Configuration (service definitions, DI containers)

### Stage 4: Violation Detection
Detect boundary crossings:
```
violation = edge where:
    source.layer > target.layer (wrong direction)
    OR source.domain != target.domain (cross-domain without API)
    OR source.service != target.service AND not_via_api
```

### Stage 5: Drift Measurement
Compare current architecture to detected original pattern:
```
drift_score = 1 - (pattern_compliance / max_possible_compliance)
```

Track drift over time:
- When did each violation first appear?
- Which commits introduced violations?
- Is drift accelerating or stabilizing?

### Stage 6: Evidence Generation
Produce evidence nodes:
- detected_pattern: Identified architectural pattern with confidence
- layer_map: Files/modules mapped to layers
- boundary_definitions: Detected boundaries
- boundary_violations: Crossings with context
- architectural_drift: Drift score and history
- interface_stability: API change frequency
- abstraction_depth: Depth of abstraction hierarchy

---

## Output Evidence

| Evidence Type | Description | Example Value |
|---|---|---|
| detected_pattern | Architecture pattern | {pattern: Clean Architecture, confidence: 0.87} |
| layer_map | Layer assignments | {PaymentService.java: usecases, StripeAdapter.java: interfaces} |
| boundary_definitions | Boundaries | {Payment Domain: [PaymentService, PaymentRepository, ...]} |
| boundary_violations | Violations | {file: Controller.java, rule: no-db-in-controller, severity: high} |
| architectural_drift | Drift score | {current: 0.28, trend: increasing, violations: 12} |
| interface_stability | API stability | {interface: PaymentAPI, changes_per_month: 2.3, stable: false} |
| abstraction_depth | Abstraction levels | {max_depth: 4, average: 2.1} |

---

## Pattern Detection Confidence

| Signal Strength | Confidence | Action |
|---|---|---|
| All signals match | > 0.85 | High confidence pattern detection |
| Most signals match | 0.60-0.85 | Medium confidence; note uncertainty |
| Few signals match | < 0.60 | Low confidence; present as unstructured |
| Conflicting signals | < 0.40 | Mixed patterns; flag for review |

---

## The Architectural Cognition Doctrine

> **Architecture is the invisible blueprint of software — the rules that govern how code should be organized, what can depend on what, and where boundaries must be respected. The Architectural Cognition Engine makes that blueprint visible, detects where reality has diverged from intent, and measures the cost of that divergence. It preserves architectural vision against the entropy of time.**



================================================================================
# 08 Decision Cognition Engine
================================================================================

# Decision Cognition Engine

## Evaluating Engineering Options

The Decision Cognition Engine evaluates engineering decisions — refactor, rewrite, migrate, split, leave alone — by modeling their costs, risks, benefits, and confidence. It transforms evidence from all other engines into structured decision support, enabling engineering leaders to make evidence-based strategic choices.

---

## Scope

### In Scope
- Decision framing (what are we deciding?)
- Option generation (what could we do?)
- Evidence-based evaluation (cost, risk, benefit, confidence)
- Effort estimation (developer-days)
- Outcome prediction (what will happen if we choose X?)
- Recommendation generation (what should we do?)
- Decision tracking (what did we decide, and was it right?)

### Out of Scope
- Making decisions autonomously (human judgment is final)
- Business case analysis (revenue, market impact)
- Team capacity planning (requires external input)
- Exact effort estimation (estimates are probabilistic)

---

## Input

| Input | Source | Format |
|---|---|---|
| Risk assessment | Risk Cognition | Risk scores, forecasts |
| Complexity metrics | Structural Cognition | Current and trended complexity |
| Dependency graph | Dependency Cognition | Internal/external dependencies |
| Knowledge map | Knowledge Cognition | Expertise distribution |
| Architecture state | Architectural Cognition | Patterns, violations, drift |
| Historical decisions | SCM Reasoning Store | Past decisions and outcomes |
| User question | UI/API | Natural language decision frame |

---

## Algorithm

### Stage 1: Decision Framing
Parse the user's decision question:
- Should we refactor PaymentService?
- Should we migrate from monolith to microservices?
- Should we invest in testing for the auth module?

Extract:
- Decision subject (module, pattern, technology)
- Implicit options (refactor, rewrite, migrate, leave)
- Constraints (budget, timeline, team size)

### Stage 2: Option Generation
Generate standard options based on decision type:

| Decision Type | Standard Options |
|---|---|
| Module complexity | Refactor, Modularize, Rewrite, Leave |
| Architecture drift | Remediate, Redesign, Accept, Monitor |
| Dependency risk | Update, Replace, Isolate, Accept |
| Knowledge gap | Transfer, Document, Hire, Accept |
| Test coverage | Invest, Maintain, Reduce, Accept |

### Stage 3: Evidence Assembly
For each option, gather relevant evidence:

```
Option: Refactor PaymentService
Evidence needed:
  - Current complexity (Structural)
  - Complexity trend (Evolution)
  - Dependency count (Dependency)
  - Bus factor (Knowledge)
  - Similar past refactors (Historical decisions)
  - Estimated effort (Heuristic model)
```

### Stage 4: Option Scoring
Score each option across criteria:

| Criterion | Weight | Source |
|---|---|---|
| Cost (developer-days) | 0.25 | Heuristic model + historical data |
| Risk (0-1) | 0.25 | Risk Cognition + dependency analysis |
| Benefit (0-1) | 0.20 | Complexity reduction + maintainability gain |
| Confidence (0-1) | 0.15 | Evidence completeness + historical accuracy |
| Strategic alignment (0-1) | 0.15 | Architectural fit + team capability |

```
option_score = sum(criterion_score * weight)
```

### Stage 5: Effort Estimation
Estimate effort using heuristics:
```
effort_refactor = complexity * lines_of_code * coupling_factor * knowledge_factor

coupling_factor = 1 + (dependent_modules * 0.1)
knowledge_factor = 1 + (1 / bus_factor)
```

Calibrate against historical decisions:
```
if similar_past_decision.exists:
    effort = historical_actual * complexity_ratio
```

### Stage 6: Outcome Prediction
Predict outcomes for each option:
```
if option == refactor:
    predicted_complexity = current_complexity * 0.6
    predicted_risk = current_risk * 0.7
    predicted_time = effort + 30 days stabilization

if option == rewrite:
    predicted_complexity = initial_complexity * 0.4
    predicted_risk = current_risk * 1.5  # short-term increase
    predicted_time = effort + 90 days stabilization

if option == leave:
    predicted_complexity = trend_extrapolate(6_months)
    predicted_risk = trend_extrapolate(6_months)
    predicted_time = 0
```

### Stage 7: Recommendation
Select highest-scoring option with caveats:
```
recommendation = argmax(option_score)
confidence = option_score[recommendation] / sum(option_scores)
```

Present:
- Recommended option
- Confidence score
- Key evidence supporting recommendation
- Key risks of recommended option
- Alternative options with trade-offs

### Stage 8: Evidence Generation
Produce evidence nodes:
- decision_frame: Parsed decision question
- option_evaluation: Scored options with evidence
- effort_estimate: Estimated developer-days per option
- outcome_prediction: Predicted future states
- recommendation: Suggested option with confidence
- decision_record: Stored for outcome tracking

---

## Output Evidence

| Evidence Type | Description | Example Value |
|---|---|---|
| decision_frame | Parsed question | {subject: PaymentService, type: refactor_decision} |
| option_evaluation | Scored options | {refactor: 0.78, rewrite: 0.52, leave: 0.34} |
| effort_estimate | Estimated effort | {refactor: 18 days, rewrite: 120 days, leave: 0 days} |
| outcome_prediction | Predicted outcomes | {refactor: {complexity: 18, risk: 0.45}} |
| recommendation | Suggested action | {option: refactor, confidence: 0.78, caveats: [...]} |
| decision_record | Stored decision | {id: ..., timestamp: ..., selected_option: refactor} |

---

## Decision Outcome Tracking

After a decision is implemented:
- Record actual effort vs. estimated effort.
- Record actual outcome vs. predicted outcome.
- Update historical decision database.
- Improve future estimates based on accuracy.

---

## The Decision Cognition Doctrine

> **Engineering decisions are bets. The Decision Cognition Engine makes those bets informed — not certain, but grounded in evidence, calibrated by history, and transparent in uncertainty. It never decides. It illuminates the options so that humans can decide with confidence.**



================================================================================
# 09 Prediction Cognition Engine
================================================================================

# Prediction Cognition Engine

## Forecasting the Future of Software

The Prediction Cognition Engine forecasts future states of a software system based on historical trends, current trajectories, and modeled interventions. It transforms time-series evidence into predictions about complexity, risk, velocity, and health — always with confidence intervals and always evidence-bound.

---

## Scope

### In Scope
- Complexity trajectory forecasting
- Risk escalation prediction
- Velocity trend projection
- Technical debt accumulation forecasting
- Maintenance burden prediction
- Outcome prediction for decisions (with Decision Cognition)
- Prediction accuracy tracking

### Out of Scope
- Business outcome prediction (revenue, user growth)
- Exact date prediction (probabilistic ranges only)
- Causal intervention modeling (beyond simple trend extrapolation)
- External event prediction (market changes, team changes)

---

## Input

| Input | Source | Format |
|---|---|---|
| Metric time-series | SCM Temporal Store | Historical values with timestamps |
| Current trends | Evolution Cognition | Slopes, change points |
| Risk assessments | Risk Cognition | Current risk scores |
| Decision records | Decision Cognition | Past decisions and outcomes |
| Historical predictions | SCM Reasoning Store | Past predictions vs. actuals |

---

## Algorithm

### Stage 1: Trend Extraction
Extract trends from metric time-series:
- **Linear trend:** Simple linear regression
- **Exponential trend:** For accelerating growth
- **Change-point detection:** When did the trend shift?
- **Seasonal patterns:** Sprint cycles, release cycles

### Stage 2: Model Selection
Select prediction model based on data characteristics:

| Data Characteristic | Model | Use Case |
|---|---|---|
| Steady linear trend | Linear regression | Complexity growth |
| Accelerating trend | Exponential smoothing | Debt accumulation |
| Cyclical pattern | Seasonal ARIMA | Velocity cycles |
| Sparse data | Conservative heuristic | New modules |
| Rich historical data | Ensemble (linear + exponential) | Mature modules |

### Stage 3: Prediction Generation
Generate predictions with confidence intervals:
```
prediction(time) = trend_model(time) +/- confidence_interval

confidence_interval = z_score * standard_error

where standard_error increases with forecast horizon
```

### Stage 4: Threshold Crossing Prediction
Predict when metrics will cross critical thresholds:
```
time_to_critical = (threshold - current_value) / trend_slope

if time_to_critical < 90 days:
    urgency = immediate
elif time_to_critical < 180 days:
    urgency = short-term
else:
    urgency = monitor
```

### Stage 5: Intervention Modeling
Model effect of proposed interventions:
```
if intervention == refactor:
    predicted_complexity = current_complexity * 0.6
    intervention_effect = -40% complexity
    confidence = 0.65

if intervention == knowledge_transfer:
    predicted_bus_factor = current_bus_factor + 1
    intervention_effect = +1 bus factor
    confidence = 0.80
```

### Stage 6: Accuracy Tracking
Compare predictions to actual outcomes:
```
prediction_error = abs(predicted - actual) / actual

if prediction_error < 0.1: accurate
elif prediction_error < 0.3: acceptable
else: inaccurate — model needs recalibration
```

### Stage 7: Evidence Generation
Produce evidence nodes:
- metric_forecast: Predicted values with confidence intervals
- threshold_prediction: When metrics cross thresholds
- intervention_forecast: Effect of proposed actions
- prediction_accuracy: Historical accuracy metrics
- trend_analysis: Trend type, slope, change points

---

## Output Evidence

| Evidence Type | Description | Example Value |
|---|---|---|
| metric_forecast | Future values | {metric: complexity, 6_months: 42, ci_lower: 38, ci_upper: 46} |
| threshold_prediction | Critical crossing | {metric: complexity, threshold: 40, estimated_date: 2024-10-15, confidence: 0.70} |
| intervention_forecast | Action effects | {intervention: refactor, complexity_reduction: 0.40, confidence: 0.65} |
| prediction_accuracy | Model accuracy | {mape: 0.12, bias: 0.03, calibration: good} |
| trend_analysis | Trend details | {type: linear, slope: 2.3, r_squared: 0.89, change_points: [2024-03]} |

---

## Prediction Confidence Levels

| Horizon | Expected Accuracy | Confidence Interval |
|---|---|---|
| 1 month | +/-10% | Narrow |
| 3 months | +/-20% | Moderate |
| 6 months | +/-30% | Wide |
| 12 months | +/-50% | Very wide |

Predictions beyond 6 months are labeled speculative regardless of model fit.

---

## The Prediction Cognition Doctrine

> **The future of software is not random. It is the continuation of trends set in motion by past decisions. The Prediction Cognition Engine reads those trends, models their trajectories, and forecasts where they lead — always with humility, always with uncertainty quantified, always with evidence. It does not predict the future. It illuminates the probable futures so that humans can choose which to pursue.**



================================================================================
# 10 Engine Orchestration
================================================================================

# Engine Orchestration

## Running the Engines

This document defines how Cognitive Engines are discovered, scheduled, executed, and monitored. Engine orchestration is the nervous system of the perception layer — coordinating multiple independent engines to produce a unified understanding.

---

## Orchestration Principles

1. **Deterministic Scheduling.** Same repository state -> same engine execution order.
2. **Parallel Execution.** Independent engines run concurrently.
3. **Incremental Awareness.** Only changed data triggers re-execution.
4. **Failure Isolation.** One engine failing does not crash others.
5. **Observability.** Every execution is logged, timed, and reported.

---

## Engine Registry

Engines self-register on system startup:

```python
registry.register(StructuralCognitionEngine())
registry.register(EvolutionCognitionEngine())
registry.register(KnowledgeCognitionEngine())
registry.register(DependencyCognitionEngine())
registry.register(RiskCognitionEngine())
registry.register(ArchitecturalCognitionEngine())
registry.register(DecisionCognitionEngine())
registry.register(PredictionCognitionEngine())
```

Registry validates:
- Unique names
- No circular dependencies
- Required pipeline stages available

---

## Execution DAG

```
RepositoryDiscovery
    |
GitMining -> FileIndexing
                |
            ASTParsing -> DependencyResolution -> MetricCalculation
                                                            |
        +----------+----------+----------+----------+
        |          |          |          |          |
        v          v          v          v          v
   Structural  Evolution  Knowledge  Dependency  Risk
   Cognition   Cognition  Cognition   Cognition  Cognition
        |          |          |          |          |
        +----------+----------+----------+----------+
                           |
                   Architectural Cognition
                           |
                   Decision Cognition
                           |
                   Prediction Cognition
```

---

## Scheduling Algorithm

### Full Analysis
```python
def run_full_analysis(repository):
    dag = build_dependency_dag(registry.get_all_engines())

    for stage in topological_stages(dag):
        # Run engines in this stage in parallel
        results = await asyncio.gather(
            *[engine.run(repository, processed_data, scm) 
              for engine in stage]
        )

        # Check for failures
        for result in results:
            if result.status == failed:
                log_failure(result)
                if result.engine.is_critical:
                    raise CriticalEngineFailure()

    return AnalysisResult(engines_run=len(dag), evidence_produced=...)
```

### Incremental Analysis
```python
def run_incremental_analysis(repository, changed_files, changed_commits):
    # Determine which engines need re-running
    affected_engines = determine_affected_engines(changed_files)

    # Re-run pipeline stages for changed files only
    incremental_data = pipeline.run_incremental(changed_files)

    # Re-run affected engines
    for engine in affected_engines:
        engine.run(repository, incremental_data, scm)

    # Re-run downstream engines if their inputs changed
    for engine in get_downstream_engines(affected_engines):
        if engine.input_changed():
            engine.run(repository, scm)
```

---

## Failure Handling

| Failure Type | Behavior | Recovery |
|---|---|---|
| Engine crash | Log error, skip engine, continue others | Retry on next analysis |
| Partial output | Store partial evidence, mark as incomplete | Re-run on next analysis |
| Dependency unavailable | Block dependent engines, run others | Retry when dependency completes |
| Timeout | Kill engine, log timeout, continue | Manual investigation |
| Schema mismatch | Reject evidence, log version conflict | Update engine or schema |

---

## Performance Monitoring

Per-engine metrics:
- Execution time (p50, p95, p99)
- Memory usage
- Evidence produced
- Cache hit rate (for incremental)
- Failure rate

Dashboard:
```
Engine                | Status | Time  | Evidence | Cache Hit
----------------------|--------|-------|----------|----------
Structural Cognition  | OK     | 12s   | 1,247    | 85%
Evolution Cognition   | OK     | 45s   | 89       | 60%
Knowledge Cognition   | OK     | 8s    | 156      | 90%
Dependency Cognition  | OK     | 15s   | 423      | 75%
Risk Cognition        | OK     | 3s    | 12       | 95%
Architectural Cognition| OK    | 22s   | 34       | 80%
Decision Cognition    | --     | --    | --       | -- (on demand)
Prediction Cognition  | --     | --    | --       | -- (on demand)
```

---

## The Engine Orchestration Doctrine

> **Cognitive Engines are independent thinkers that must work together. The orchestrator ensures they run in the right order, at the right time, with the right data — without any engine knowing about the others. It is the conductor of the perception symphony, ensuring every instrument plays its part in harmony.**



================================================================================
# 11 Engine Testing
================================================================================

# Engine Testing

## Ensuring Engines Are Trustworthy

This document defines the testing strategy for Cognitive Engines. Because engines produce the evidence upon which all reasoning rests, their correctness is non-negotiable. Every engine must be thoroughly tested, versioned, and validated.

---

## Testing Principles

1. **Determinism.** Same input -> same output, always.
2. **Reproducibility.** Tests use fixed inputs and expected outputs.
3. **Isolation.** Engines tested independently, with mocked dependencies.
4. **Coverage.** Every code path, every edge case, every evidence type.
5. **Regression.** Every bug fix includes a test that would have caught it.

---

## Test Categories

### Unit Tests
Test individual functions within an engine:
- Complexity calculation
- Commit categorization
- Ownership scoring
- Dependency resolution

```python
def test_cyclomatic_complexity():
    ast = parse("def f(x):\n  if x:\n    return 1\n  return 2")
    assert cyclomatic_complexity(ast) == 2

def test_commit_categorization():
    assert categorize("feat: add payment") == "feature"
    assert categorize("fix: bug in auth") == "fix"
    assert categorize("docs: update readme") == "docs"
```

### Integration Tests
Test engine execution with real pipeline data:
- End-to-end engine run on sample repository
- Evidence schema validation
- SCM write verification
- Cross-engine consistency

```python
def test_structural_cognition_on_sample_repo():
    repo = load_fixture("sample-python-project")
    engine = StructuralCognitionEngine()
    result = engine.run(repo, processed_data, mock_scm)

    assert len(result.evidence) > 0
    assert all(e.confidence in VALID_CONFIDENCES for e in result.evidence)
    assert result.evidence[0].source.engine == "structural_cognition"
```

### Regression Tests
Test against known inputs with known outputs:
- Fixture repositories with expected evidence
- Version-to-version output comparison
- Performance benchmarks

```python
def test_engine_output_unchanged_since_v1_2_0():
    repo = load_fixture("standard-java-project")
    result = engine.run(repo, processed_data, mock_scm)
    expected = load_expected("structural_v1_2_0_standard-java")

    assert evidence_equal(result.evidence, expected)
```

### Property-Based Tests
Test invariants that must hold:
- Bus factor <= number of contributors
- Complexity >= 1 for any function
- Dependency graph has no self-loops
- All evidence has raw_data_ref

```python
def test_bus_factor_bounded_by_contributors():
    for repo in generate_random_repos():
        evidence = KnowledgeCognitionEngine().run(repo, ...)
        for e in evidence:
            if e.type == "bus_factor":
                assert e.value <= count_contributors(repo)
```

---

## Test Fixtures

Standard test repositories:

| Fixture | Language | Size | Purpose |
|---|---|---|---|
| minimal-python | Python | 3 files | Basic functionality |
| standard-java | Java | 50 files | Typical project |
| complex-javascript | JavaScript | 200 files | Complex dependencies |
| legacy-monolith | Java | 500 files | Legacy patterns |
| microservices-go | Go | 10 services | Service boundaries |
| empty-repo | -- | 0 files | Edge cases |
| circular-deps | Python | 10 files | Circular dependencies |
| high-complexity | Java | 20 files | Complexity thresholds |

---

## Continuous Integration

Engine tests run on every commit:
- Unit tests: < 30 seconds
- Integration tests: < 5 minutes
- Regression tests: < 10 minutes
- Full fixture suite: < 30 minutes

Failure criteria:
- Any unit test failure -> block merge
- Integration test failure -> block merge
- Regression test failure -> investigate, may block merge
- Performance regression > 10% -> investigate

---

## The Engine Testing Doctrine

> **Cognitive Engines are the foundation of trust. If an engine is wrong, every insight built upon it is suspect. Testing is not optional. It is the guarantee that perception is accurate, deterministic, and reliable. We test not because we doubt our code, but because we respect the users who will act upon its output.**



================================================================================
# 12 Engine Glossary
================================================================================

# Engine Glossary

## Terms Specific to Cognitive Engines

---

## A

### Afferent Coupling (Ca)
The number of modules that depend on a given module. Measure of responsibility.

---

## B

### Bus Factor
The number of engineers who would need to leave before a module becomes unmaintainable. Calculated by Knowledge Cognition.

---

## C

### Cognitive Engine
A deterministic module that perceives one dimension of a software system and produces structured evidence.

### Commit Categorization
Classifying commits by type (feature, fix, refactor, test, docs, chore).

### Cyclomatic Complexity
A measure of code complexity: number of linearly independent paths through code.

---

## D

### Decision Frame
The parsed structure of a user's decision question, including subject, options, and constraints.

### Dependency Health
A composite score measuring the maintenance status of an external dependency.

### Drift Score
A measure of how much the current architecture has diverged from the detected original pattern.

---

## E

### Efferent Coupling (Ce)
The number of modules a given module depends on. Measure of independence.

### Engine Orchestration
The scheduling, execution, and monitoring of Cognitive Engines.

### Engine Registry
The system that discovers, registers, and manages Cognitive Engines.

### Evidence Node
A structured record produced by an engine, conforming to the SCM evidence schema.

### Expertise Profile
A record of an author's knowledge depth and breadth for a specific module.

---

## F

### Full Analysis
Running all engines on a complete repository. Contrasts with incremental analysis.

---

## H

### Hotspot
A file with high complexity and high change frequency. Identified by Evolution Cognition.

---

## I

### Incremental Analysis
Re-running only affected engines on changed files/commits.

### Instability (I)
Ce / (Ca + Ce). Measures module stability. 0 = stable, 1 = unstable.

---

## K

### Knowledge Gap
A module where expertise is insufficient (orphaned, single owner, outdated).

### Knowledge Distribution
The concentration of expertise across a team, measured by Gini coefficient.

---

## L

### LCOM (Lack of Cohesion in Methods)
A measure of class cohesion. Higher values indicate lower cohesion.

---

## O

### Onboarding Difficulty
Estimated time for a new engineer to become productive in a module.

### Ownership Map
The mapping of modules to primary and secondary owners.

---

## P

### Pattern Detection
Identifying architectural patterns from code structure and conventions.

### Prediction Horizon
The time range of a forecast. Accuracy decreases with horizon.

---

## R

### Refactoring Detection
Identifying refactoring events from commit patterns and code changes.

### Risk Velocity
The rate at which risk scores are changing. Used for forecasting.

---

## T

### Temporal Coupling
The degree to which two files change together in commits.

### Threshold Crossing
When a metric is predicted to cross a critical value.

---

## Document Conventions

- Terms defined in Phase -1, 0, and 3 are not redefined here.
- New terms introduced in Phase 4 are defined here.
- Terms are organized alphabetically.
