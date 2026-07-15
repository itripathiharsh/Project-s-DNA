================================================================================
# Project DNA — Documentation Audit Report
================================================================================

Audit Date: 2026-07-14
Scope: All 120 documents across 12 phases
Auditor: Chief Architect

---

## OVERALL SCORE: 73 / 100

| Dimension | Score | Assessment |
|---|---|---|
| Terminology Consistency | 68 | Multiple naming conflicts between phases |
| Cross-Reference Completeness | 52 | Sparse after Phase 4; Phases 9-12 are orphans |
| Internal Consistency | 71 | Several metric/scope contradictions within phases |
| Philosophical Alignment | 82 | Core principles upheld; some pillar/doctrine drift |
| Specification Depth | 74 | Most docs adequate; several underspecified components |
| Dependency Chain Integrity | 65 | Several dangling references to non-existent endpoints/modules |
| **Overall** | **73** | **Solid foundation with systemic cross-linking gaps** |

---

## EXECUTIVE SUMMARY

The documentation is structurally sound and philosophically coherent. However, three systemic issues degrade the overall quality:

1. **Cross-phase references are sparse after Phase 4.** Phases 9-12 have near-zero references to earlier phases, creating orphan documentation islands.
2. **Versioning strategy is inconsistent.** The V1/V2/V3/V4 scope changes between Phase -1, Phase 0, Phase 2, and Phase 11/12 without reconciliation.
3. **Several concrete specifications are missing.** Components like the Insight Validator, Intent Recognition, auth endpoints, and `POST /v1/reason/suggest` are referenced in multiple places but never defined.

---

## ISSUE INVENTORY

### CRITICAL ISSUES (16)

---

#### C01 — V4 Version Contradiction Across Foundational Docs

| Severity | Critical |
|---|---|
| Documents | `Phase_-1/03` (Category), `Phase_0/10` (Glossary), `Phase_2/01` (Architecture), `Phase_11/01` (Roadmap), `Phase_12/01` (Vision) |
| Description | Phase -1 defines 3 stages: V1 (Repository), V2-V3 (Organization), V4+ (Ecosystem). Phase 0 defines V1-V4 explicitly. Phase 2 has full V1-V4 architecture sections. Phase 11/01 and Phase 12/01 only define V1-V3. Ecosystem Cognition is labeled "V3+ research direction" in Phase 12/06, conflicting with Phase -1 (V4+) and Phase 0 (V4). The roadmap was truncated from 4 versions to 3 without acknowledging the change. |
| Fix | Either add V4 back to Phase 11/01 and Phase 12/01, or formally deprecate V4 in Phase -1, Phase 0, and Phase 2 and explain the consolidation. |

---

#### C02 — V3 Description Contradicts Phase 0 Glossary

| Severity | Critical |
|---|---|
| Documents | `Phase_0/10` (Glossary), `Phase_11/01` (Roadmap), `Phase_12/01` (Vision), `Phase_12/03` (V3 Roadmap) |
| Description | Phase 0 glossary defines V3 as "Runtime-integrated cognition" (codebase + runtime data from Grafana/Datadog). Phase 11/01 and Phase 12/01 define V3 as "Organization Cognition" (enterprise, cross-org analysis). Phase 12/03 never mentions runtime integration at all. |
| Fix | Either add runtime-integration to V3 capabilities, or update Phase 0's V3 definition to match "Organization Cognition." |

---

#### C03 — Audit Logging Scheduled in Two Different Versions

| Severity | Critical |
|---|---|
| Documents | `Phase_11/01` (Roadmap, V3 M10), `Phase_11/02` (Milestones, V2 M6) |
| Description | Phase 11/01 places audit logging under M10 in V3 (Month 24). Phase 11/02 places audit logging under M6 in V2 (Month 12). Same feature, contradictory delivery dates. |
| Fix | Decide one version. If V2, remove from M10. If V3, remove from M6. Update all dependent docs. |

---

#### C04 — V1 Scope Contradiction: 1,000 Repos vs. Single Repo

| Severity | Critical |
|---|---|
| Documents | `Phase_0/02` (Success Metrics), `Phase_2/01` (System Architecture) |
| Description | Phase 0 targets "1,000 active repositories" for V1. Phase 2 states V1 is "One repository, one user, one machine" with limits of ~1M LOC. These are contradictory. |
| Fix | Align all docs. If V1 is single-repo, change "1,000 active repositories" to a V2 target. If the metric means "cumulative across all users", clarify wording. |

---

#### C05 — Time to Understanding Metric Internally Contradictory

| Severity | Critical |
|---|---|
| Documents | `Phase_0/02` (Success Metrics, lines 97-101 vs. lines 1542-1546) |
| Description | Two definitions of the same metric: §1 says baseline 3-6 months, V1=2 weeks, V2=3 days. §4.1 says baseline 3 weeks, V1=2 days, V2=3 days. Percentages are swapped, units differ, and V2 target (3 days) regresses from V1 (2 days). |
| Fix | Unify to one definition. Recommended: baseline 3-6 months, V1=2 days (repo-level), V2=3 hours (module-level). Fix percentages. |

---

#### C06 — Performance Targets Unachievable Against Hardware Specs

| Severity | Critical |
|---|---|
| Documents | `Phase_5/01` (Overview, <2 sec target), `Phase_5/02` (LLM Architecture, 15-25 tok/s on CPU) |
| Description | Phase 5/01 sets <2 sec for simple QA with LLM budget <1 sec. Phase 5/02 shows 3B Q4 on CPU at 15-25 tok/s = 20-33 sec for 500 tokens. No config in Phase 5/02 achieves <1 sec LLM inference for any meaningful output. |
| Fix | Either reduce targets to match hardware (e.g., <10 sec simple QA) or specify minimum hardware (e.g., "Requires RTX 4090 for <2 sec QA"). |

---

#### C07 — Token Budget Contradiction Between Phase 5 Documents

| Severity | Critical |
|---|---|
| Documents | `Phase_5/02` (LLM Architecture, 1000 template tokens), `Phase_5/03` (Prompt Architecture, 400 template tokens) |
| Description | Phase 5/02 allocates 1000 tokens for "Prompt template" (8192 total). Phase 5/03 allocates 400 tokens for "Template" on the same model. Per-type totals in Phase 5/03 sum to 7592-7800, leaving an unexplained 400-600 token gap. |
| Fix | Reconcile budgets. Update Phase 5/02's 1000->400 or Phase 5/03's 400->1000. Make totals consistent. |

---

#### C08 — Fallback Endpoint Referenced But Doesn't Exist

| Severity | Critical |
|---|---|
| Documents | `Phase_6/02` (REST API, 503 response) |
| Description | The 503 error for Ollama unavailability returns `"fallback_endpoint": "/v1/reason/question/evidence-summary"`. This endpoint is not defined anywhere in Phase 6/02's endpoint catalog or Phase 6/09's examples. |
| Fix | Either add the endpoint specification or remove the fallback_endpoint field. |

---

#### C09 — Test Coverage Engine Referenced But Doesn't Exist

| Severity | Critical |
|---|---|
| Documents | `Phase_5/09` (Examples, lines 458, 504) |
| Description | Example 6 recommends "Run test coverage analysis" and mentions "No test coverage engine evidence exists." No such engine exists in Phase 4's 8-engine catalog. |
| Fix | Replace with a reference to an existing engine or add a test coverage engine to Phase 4. |

---

#### C10 — Search History Persistence Contradiction

| Severity | Critical |
|---|---|
| Documents | `Phase_7/03` (State Management), `Phase_7/06` (Search and Query UI) |
| Description | Phase 7/03 says `searchStore` is NOT persisted. Phase 7/06 says search history is stored "in Zustand with localStorage persistence" and defines a `SearchHistoryEntry` interface absent from Phase 7/03. |
| Fix | Either add a `searchHistoryStore` to Phase 7/03 or align Phase 7/06 to use non-persistent ephemeral storage. |

---

#### C11 — UI Depends on Undefined API Endpoint

| Severity | Critical |
|---|---|
| Documents | `Phase_7/06` (Search UI), `Phase_6/02` (REST API) |
| Description | Phase 7/06 references `POST /v1/reason/suggest` for autocomplete. This endpoint does not exist anywhere in Phase 6. |
| Fix | Add the endpoint to Phase 6/02 or replace with an existing endpoint. |

---

#### C12 — `POST /v1/reason/suggest` Also Undefined for Autocomplete

| Severity | Critical |
|---|---|
| Documents | `Phase_7/06` (Search UI) |
| Description | Same as C11 — autocomplete suggestions depend on an endpoint that has no specification. |
| Fix | Add `POST /v1/reason/suggest` to Phase 6/02 endpoint catalog. |

---

#### C13 — Quality Gate Thresholds Contradict Per-Metric Thresholds

| Severity | Critical |
|---|---|
| Documents | `Phase_9/01` (Testing Overview), `Phase_9/08` (Performance Testing) |
| Description | Phase 9/01 says "Latency > 2x baseline" fails release. Phase 9/08 defines per-metric: API p95 > 3x, Reasoning > 4x, Memory > 2x, Frontend TTI > 6s. The blanket 2x rule is stricter than what the detailed doc enforces. |
| Fix | Update Phase 9/01 to cross-reference Phase 9/08's per-metric thresholds. |

---

#### C14 — "Tests Are Deterministic" Doctrine Contradicts AI Evaluation

| Severity | Critical |
|---|---|
| Documents | `Phase_9/01` (Testing Overview), `Phase_9/07` (AI Evaluation) |
| Description | Phase 9/01 declares "Tests are deterministic" as an absolute rule. Phase 9/07 says "Unlike deterministic tests, AI evaluation uses probabilistic metrics." These directly contradict. |
| Fix | Add an exception clause to the Testing Doctrine: "— with the explicit exception of AI Evaluation (Phase 9/07)." |

---

#### C15 — SCM Writer Protocol Undefined

| Severity | Critical |
|---|---|
| Documents | `Phase_3` (SCM Model), `Phase_4` (Engine Architecture) |
| Description | Phase 4's `CognitiveEngine.run()` uses `scm: SCMWriter` — never defined in Phase 3 or Phase 4. Every engine depends on this type. |
| Fix | Define `SCMWriter` protocol in Phase 3 or Phase 4. |

---

#### C16 — Phase 9 Has Zero Cross-References to Phases -1, 3, 5, or 6

| Severity | Critical |
|---|---|
| Documents | All Phase 9 documents |
| Description | Phase 9 uses "SCM," "Cognitive Engines," "Reasoning Layer," "API Gateway" without pointing to their defining documents. Only 2 references to Phase 4 exist across the entire phase. |
| Fix | Add cross-references on first use of each borrowed concept. |

---

### MAJOR ISSUES (35)

---

#### M01 — No Cross-References from Phase 11/12 to Phases 1-9

| Severity | Major |
|---|---|
| Documents | All Phase 11/12 documents |
| Description | Phase 11 describes REST API (M1), LLM (M2), frontend (M3) as if planned for the first time. Phase 5, 6, 7 already have full specifications. Phase 11/12 never references them. |
| Fix | Add "See Also" sections or inline cross-references in every Phase 11/12 document. |

---

#### M02 — No Cross-References from Phase 10 to Phase 9

| Severity | Major |
|---|---|
| Documents | `Phase_10/05` (CI/CD), `Phase_9/01` (Testing Overview) |
| Description | Phase 10/05 defines CI pipeline (lint -> type-check -> unit -> integration) but never references the validation, AI evaluation, performance, or benchmark tests defined in Phase 9. Quality gates in Phase 9/01 specify nightly/weekly/release triggers that don't exist in Phase 10/05. |
| Fix | Add Phase 9 test types to Phase 10/05 CI stages with appropriate triggers. |

---

#### M03 — Missing Cross-References to Phase -1 Across All Phases After Phase 4

| Severity | Major |
|---|---|
| Documents | Phases 7, 8, 9, 10, 11, 12 |
| Description | Phase -1 defines the master glossary and First Principles. No document in Phases 7-12 references Phase -1. Core terms (Evidence, Insight, Confidence Score, Evidence Chain, Cognition) are used without linking to their authoritative definitions. |
| Fix | Add Phase -1 glossary references in Phase 7/10, 8/10, 9/10, 10/10, 11/10, 12/10 glossaries. Add inline references on first use in each document. |

---

#### M04 — SCM Four Pillars Don't Match Phase -1 Cognition Pillars

| Severity | Major |
|---|---|
| Documents | `Phase_3/01` (SCM Overview), `Phase_-1/07` (What Is Cognition) |
| Description | Phase -1 defines 4 pillars: Perception, Representation, Reasoning, Explanation. Phase 3's SCM maps to Perception Store, Representation Store, Reasoning Store, Temporal Store — swapping Explanation for Temporal. The "mirror the four pillars" claim (line 52) is inaccurate. |
| Fix | Either add Explanation/Explainability as a fifth pillar, or state that SCM merges Explanation into Reasoning and adds Temporal as infrastructure. |

---

#### M05 — Phase 4 Engine Glossary Redefines Phase -1/3 Terms

| Severity | Major |
|---|---|
| Documents | `Phase_4/10` (Glossary), `Phase_-1/12` (Glossary) |
| Description | Phase 4 glossary says "Terms defined in Phase -1, 0, and 3 are not redefined here" but then redefines Bus Factor, Evidence Node, Confidence Level, and many others. |
| Fix | Remove duplicate definitions. Replace with `See: Phase X Glossary` references. |

---

#### M06 — Phase 3 Glossary Also Redefines Phase -1/0 Terms

| Severity | Major |
|---|---|
| Documents | `Phase_3/08` (SCM Glossary) |
| Description | Same pattern as M05 — claims not to redefine but duplicates Bus Factor, Insight, Evidence Chain, Confidence Level from Phase -1/0. |
| Fix | Remove duplicates, add cross-references. |

---

#### M07 — SQLite Schema Uses PostgreSQL `JSONB` Type

| Severity | Major |
|---|---|
| Documents | `Phase_3/07` (SCM Storage) |
| Description | V1 SQLite schema uses `JSONB` column types. SQLite does not support `JSONB` — it stores JSON as `TEXT`. `JSONB` is a PostgreSQL type. |
| Fix | Change `JSONB` to `TEXT` with `CHECK (json_valid(...))` for SQLite. Reserve `JSONB` for V2 PostgreSQL path. |

---

#### M08 — Knowledge Model Heavily Duplicated Between Phase 3 and Phase 4

| Severity | Major |
|---|---|
| Documents | `Phase_3/05` (Knowledge Model), `Phase_4/04` (Knowledge Cognition) |
| Description | ~160 lines of near-duplicate content: expertise scoring, ownership detection, bus factor calculation, knowledge gap detection, onboarding difficulty formula, Gini coefficient calculation — all specified identically in both phases. |
| Fix | Phase 4 should reference Phase 3 for data structures, keeping only engine-specific algorithms. |

---

#### M09 — Insight Validator Has No Specification Despite Being Referenced in 3 Documents

| Severity | Major |
|---|---|
| Documents | `Phase_5/01`, `Phase_5/06`, `Phase_5/10` |
| Description | The Insight Validator appears in three documents as a critical QA component — checks consistency, completeness, freshness, redundancy — but has no dedicated section, data structures, configuration, or algorithm defined anywhere. |
| Fix | Add an Insight Validator section to Phase 5/06 with algorithm, thresholds, and error behaviors. |

---

#### M10 — Intent Recognition Has No Specification

| Severity | Major |
|---|---|
| Documents | `Phase_5/01` (Overview) |
| Description | Intent Recognition is Stage 1 of the 6-stage pipeline with <100ms budget, described as "rule-based, no LLM" but with zero detail on entity extraction, intent classification, or time-range parsing. |
| Fix | Either add an intent recognition section to Phase 5/04 or create a brief specification covering NLP approach and classification rules. |

---

#### M11 — Context Assembler vs. Context Builder Naming Inconsistency

| Severity | Major |
|---|---|
| Documents | `Phase_5/01` ("Context Assembler"), `Phase_5/04` ("Context Builder") |
| Description | Phase 5/01 calls the second pipeline stage "Context Assembler" throughout. Phase 5/04 is titled "Context Builder" and notes the alias. Two names for the same component across sibling documents. |
| Fix | Pick one canonical name. Phase 5/04 is the dedicated doc, so its title should be authoritative. Update Phase 5/01 to match. |

---

#### M12 — Phase 5 Pipeline Diagrams Show Inconsistent Stage Numbering

| Severity | Major |
|---|---|
| Documents | `Phase_5/01` (Overview), `Phase_5/08` (Reasoning Pipeline) |
| Description | Phase 5/01's diagram shows 5 boxes; its pipeline text describes 6 stages. Phase 5/08's diagram shows 6 stages but merges LLM Inference and Parse Response into one stage. Stage boundaries differ between the two. |
| Fix | Align the architecture diagrams to show the same number of stages with the same boundaries. |

---

#### M13 — `GET /v1/health` vs. Unversioned Path Contradiction

| Severity | Major |
|---|---|
| Documents | `Phase_6/02` (REST API), `Phase_6/08` (API Versioning) |
| Description | Phase 6/08 says "Unversioned requests are rejected with a clear error" showing `GET /entities -> 404`. Phase 6/02 defines `GET /health` and `GET /metrics` as unversioned 200 responses. The versioning policy doesn't exempt these paths. |
| Fix | Add an exemption note to Phase 6/08: "Health check and metrics endpoints are exempt from versioning requirements." |

---

#### M14 — GraphQL Endpoint Path Not Specified

| Severity | Major |
|---|---|
| Documents | `Phase_6/03` (GraphQL API) |
| Description | The GraphQL API document defines schema, queries, mutations, and subscriptions but never specifies the URL path (e.g., `/v1/graphql`). |
| Fix | Add explicit path specification. |

---

#### M15 — Auth Endpoints Undefined in REST API Spec

| Severity | Major |
|---|---|
| Documents | `Phase_6/02` (REST API), `Phase_6/05` (Authentication) |
| Description | Phase 6/05 references `POST /v1/auth/login`, `/refresh`, `/logout`, `/keys`, etc. None of these are defined in Phase 6/02's endpoint catalog with request/response schemas. |
| Fix | Add auth endpoint specifications to Phase 6/02, or note they are V2+ and placeholder. |

---

#### M16 — Evidence Chain Has Three Different Definitions

| Severity | Major |
|---|---|
| Documents | `Phase_7/04` (Component System), `Phase_7/05` (Graph Visualization), `Phase_7/01` (Overview) |
| Description | Phase 7/04 defines `EvidenceChain` as a linear Stack+EvidenceRow+Arrow. Phase 7/05 defines an interactive React Flow node-edge diagram. Phase 7/01 mentions `EvidenceChainView` (different name). No document explains when to use which view. |
| Fix | Clarify relationship: linear chain = collapsed/default view, graph = expanded view. Or consolidate into one representation. |

---

#### M17 — Undefined Route `/reports/new` Referenced but Not in Router

| Severity | Major |
|---|---|
| Documents | `Phase_7/08` (Dashboard), `Phase_7/02` (App Architecture) |
| Description | Quick Actions table specifies "New Report" navigates to `/reports/new`. This route is not defined in Phase 7/02's routing hierarchy — only `/reports` and `/reports/:id` exist. |
| Fix | Add `/reports/new` route to Phase 7/02 routing table. |

---

#### M18 — Phase 8 Principle Names Inconsistent with Phase -1 Glossary

| Severity | Major |
|---|---|
| Documents | `Phase_8/01` (Engineering Principles), `Phase_-1/12` (Glossary) |
| Description | Phase -1 defines "Deterministic-First" (with hyphen) and "Local-First" (with hyphen). Phase 8/01 uses "Deterministic First" (space) and "Local by Default" (different phrasing). These should match. |
| Fix | Standardize on hyphenated forms matching Phase -1. |

---

#### M19 — Phase 10 Introduces Auth Config Without Auth Document

| Severity | Major |
|---|---|
| Documents | `Phase_10/04` (Configuration), `Phase_10/07` (Logging) |
| Description | Phase 10/04 shows `auth` config block (`mode`, `jwt_secret`, `api_keys`). Phase 10/07 lists `dna.auth` logger. But Phase 10 has no authentication document. Config is defined without specification. |
| Fix | Either add an auth document to Phase 10 or cross-reference Phase 6/05. |

---

#### M20 — Phase 11 SCM Definition Ambiguous vs. Phase -1

| Severity | Major |
|---|---|
| Documents | `Phase_11/03` (Epics — "Core SCM"), `Phase_-1/12` (Glossary) |
| Description | Phase -1 defines "SCM" as the unified Software Cognition Model. Phase 11 introduces "Core SCM" as an epic (E-01) — a lower-level component (data model, scanner, dependency graph) separate from the "Structural Cognition Engine" (E-02). The relationship is unexplained. |
| Fix | Define "Core SCM" in Phase 11/10 glossary and explain how it relates to the Phase -1 SCM definition. |

---

#### M21 — Phase 11/06 AI Agent Workflow Has Wrong File Paths

| Severity | Major |
|---|---|
| Documents | `Phase_11/06` (AI Agent Workflow) |
| Description | References `LOOP.md` at root — actual path is `prompts/LOOP.md`. References `docs/Phase_1/` as a directory — Phase 1 is a single combined file `Phase_1_Product_Design_UX_COMBINED.md`. |
| Fix | Update path references to match actual file locations. |

---

#### M22 — Phase 11/09 References Non-Existent `scripts/ci.sh`

| Severity | Major |
|---|---|
| Documents | `Phase_11/09` (Execution Guide) |
| Description | Lists `scripts/ci.sh` as "Full CI pipeline locally." No such file exists. |
| Fix | Either create the script or replace with inline command sequence. |

---

#### M23 — Phase 11/10 Glossary Missing Key Terms Used in Phase 11

| Severity | Major |
|---|---|
| Documents | `Phase_11/10` (Glossary) |
| Description | Defines only 7 terms. Missing: SCM, Structural Engine, Evidence, Ollama, Confidence Score, REST API, GraphQL, Tauri, Svelte — all used throughout Phase 11. |
| Fix | Add missing terms or acknowledge core terms are defined in Phase -1. |

---

#### M24 — Phase 0 Success Metrics Not Carried into Phase 11/12

| Severity | Major |
|---|---|
| Documents | `Phase_0/02` (Success Metrics), `Phase_11/01` (Roadmap), `Phase_12/02`, `Phase_12/03` |
| Description | Phase 0 defines concrete adoption targets (V1: 1,000 repos, V2: 10,000 repos across 500 orgs, >70% recommendation action rate by V2). These never appear in Phase 11/12 roadmaps. |
| Fix | Add success metrics section to Phase 11/01 mapping Phase 0 targets to milestones. |

---

#### M25 — Phase 11/02 V3 Milestones Too Shallow vs. V1/V2

| Severity | Major |
|---|---|
| Documents | `Phase_11/02` (Milestones) |
| Description | V3 milestones (M8-M10) are just a summary table. V1 (M1-M4) and V2 (M5-M7) have detailed epic tables and dependencies. |
| Fix | Expand M8-M10 with same detail level. |

---

#### M26 — GraphQL Listed in V2 Roadmap but Missing from Milestones

| Severity | Major |
|---|---|
| Documents | `Phase_11/01` (Roadmap), `Phase_11/02` (Milestones), `Phase_12/02` (V2 Roadmap) |
| Description | Phase 11/01 lists GraphQL as a V2 capability. Phase 11/02 has no epic for it. Phase 12/02 doesn't mention it. |
| Fix | Add GraphQL as a V2 epic or note it's deferred. |

---

#### M27 — Phase 4 Missing Cross-References to Phase 5

| Severity | Major |
|---|---|
| Documents | `Phase_4` (all) |
| Description | Phase 4 mentions "Reasoning Layer" (line 34) but never references Phase 5. Decision Cognition and Prediction Cognition feed the reasoning pipeline but no connection is documented. |
| Fix | Add `(see Phase 5: Reasoning Overview)` after every "Reasoning Layer" reference. |

---

#### M28 — Risk Cognition References Non-Existent Test Coverage Evidence

| Severity | Major |
|---|---|
| Documents | `Phase_4/06` (Risk Cognition) |
| Description | Risk Cognition's indicator table lists "Test coverage trend" from "Structural + Evolution" as 0.10-weighted input. No engine in Phase 4 computes test coverage. |
| Fix | Either add test coverage to an existing engine, remove the indicator, or label it V2+. |

---

#### M29 — Decision/Prediction Engines Contradict Engine Doctrine

| Severity | Major |
|---|---|
| Documents | `Phase_4/06` (Doctrine), `Phase_4/07` (Decision Cognition), `Phase_4/08` (Prediction Cognition) |
| Description | The doctrine says "Engines do not reason — they perceive." Decision Cognition (evaluates options) and Prediction Cognition (forecasts futures) perform analysis that borders on reasoning. This contradicts the deterministic/reasoning boundary. |
| Fix | Clarify doctrine to accommodate higher-order deterministic analysis, or adjust the engine categories. |

---

#### M30 — Phase 9/06 Reasoning Validation Does Not Reference Phase 5

| Severity | Major |
|---|---|
| Documents | `Phase_9/06` (Reasoning Validation) |
| Description | Tests the "full pipeline end-to-end" and "all six stages" but never links to Phase 5/01 where the 6-stage pipeline is defined. |
| Fix | Add cross-reference in the Purpose section. |

---

#### M31 — Phase 9/01 Testing Pyramid and Testing Table Use Different Tier Counts

| Severity | Major |
|---|---|
| Documents | `Phase_9/01` (Testing Overview) |
| Description | ASCII pyramid has 4 labeled tiers. The table below has 5 rows. "Validation" and "Performance" appear merged in the pyramid but separate in the table. |
| Fix | Align the pyramid and table to the same tier count and grouping. |

---

#### M32 — Phase 9/01 Testing-by-Layer Table Not Cross-Referenced

| Severity | Major |
|---|---|
| Documents | `Phase_9/01` (Testing Overview) |
| Description | The "Testing by Layer" table uses column headers (Unit, Integration, Validation, etc.) with no links to the individual test documents. A reader cannot navigate from the overview to the detail docs. |
| Fix | Turn column headers into cross-references (e.g., "Unit (Phase 9/02)"). |

---

#### M33 — Phase 10 CI/CD Cannot Enforce Phase 9 Quality Gates

| Severity | Major |
|---|---|
| Documents | `Phase_10/05` (CI/CD), `Phase_9/01` (Quality Gates) |
| Description | Phase 10/05 runs all test frameworks in one combined step. Phase 9/01 defines separate gates (pre-commit, PR, nightly, weekly, release). The single step cannot selectively enforce these. |
| Fix | Split CI into gated sub-stages matching Phase 9/01's Quality Gates. |

---

#### M34 — Phase 10/01 Package Name Mismatch

| Severity | Major |
|---|---|
| Documents | `Phase_10/01` (Deployment Overview), `Phase_10/02` (Local Installation) |
| Description | Phase 10/01 lists npm artifact as "`dna` CLI." Phase 10/02 uses `@project-dna/cli`. Different names. |
| Fix | Change Phase 10/01 to use the scoped package name `@project-dna/cli`. |

---

#### M35 — Phase 10/09 References Undefined CLI Commands

| Severity | Major |
|---|---|
| Documents | `Phase_10/09` (Operations Runbook) |
| Description | References `dna stop`, `dna start` commands. No Phase 10 document defines these. Only `dna serve` and `dna ui` are documented. |
| Fix | Add command definitions or cross-reference a CLI reference doc. |

---

### MINOR ISSUES (73)

---

#### N01 — Phase 4 `ProcessedData` Type Undefined

| Severity | Minor |
|---|---|
| Docs | `Phase_4/01` (Engine Architecture) |
| Fix | Define or cross-reference the pipeline output schemas from Phase 2. |

#### N02 — Phase 4 `MetricCalculation` DAG Node Undefined

| Severity | Minor |
|---|---|
| Docs | `Phase_4/01` (Engine Architecture) |
| Fix | Either promote to documented stage or remove from DAG. |

#### N03 — Phase 4 Engine Lifecycle Missing "Cancelled" State

| Severity | Minor |
|---|---|
| Docs | `Phase_4/01` (Engine Architecture) |
| Fix | Add "Cancelled" state for user-initiated cancellation. |

#### N04 — Phase 4 "Sensory Organs" vs "Senses" Terminology Drift

| Severity | Minor |
|---|---|
| Docs | `Phase_4/01` (intro vs. doctrine) |
| Fix | Standardize on one metaphor. |

#### N05 — Phase 4 Engine Categories List Undocumented Engines (Security, Collaboration, Operational)

| Severity | Minor |
|---|---|
| Docs | `Phase_4/01` (Categories Table) |
| Fix | Add stubs referencing V2/V3 roadmap documents. |

#### N06 — Phase 4 `is_incremental()` Method Semantics Unclear

| Severity | Minor |
|---|---|
| Docs | `Phase_4/01` (Engine Protocol) |
| Fix | Clarify purpose or remove if orchestration handles this externally. |

#### N07 — Phase 4 `EvidenceCategory` Not Mapped to Phase 3 Values

| Severity | Minor |
|---|---|
| Docs | `Phase_4/01` (Evidence Output), `Phase_3` (Evidence Model) |
| Fix | Add reference to Phase 3's 7 defined categories. |

#### N08 — Phase 3 Event Type `PREDiction_MADE` Inconsistent Capitalization

| Severity | Minor |
|---|---|
| Docs | `Phase_3/03` (Time-Series Model) |
| Fix | Change to `PREDICTION_MADE`. |

#### N09 — "Ground Truth" Term Introduced in Phase 3 Without Phase -1 Entry

| Severity | Minor |
|---|---|
| Docs | `Phase_3/08` (Glossary) |
| Fix | Add "Ground Truth" to Phase -1 master glossary. |

#### N10 — Phase 0 Capabilities Table Mixes Engines with Pipeline Capabilities

| Severity | Minor |
|---|---|
| Docs | `Phase_0/03` (Product Overview) |
| Fix | Separate into "Cognitive Engines" and "Pipeline Capabilities" sections. |

#### N11 — Phase 3 Storage Section Missing Cross-Reference to Phase 2 Technology Decisions

| Severity | Minor |
|---|---|
| Docs | `Phase_3/07` (SCM Storage), `Phase_2/06` (Technology Decisions) |
| Fix | Add cross-reference at top of Storage section. |

#### N12 — Phase 0 Layer Diagram Phase Labels Don't Match Doc Content

| Severity | Minor |
|---|---|
| Docs | `Phase_0/03` (Product Overview) |
| Fix | Remove parenthetical Phase numbers or rename for clarity. |

#### N13 — No Cross-Reference from Phase 0 to Phase 1

| Severity | Minor |
|---|---|
| Docs | `Phase_0` (all), `Phase_1` (all) |
| Fix | Add a reference to UX/Design context from Phase 0. |

#### N14 — Phase 4 Engine Doctrine No Explicit Reference to Phase -1 Pillar Framework

| Severity | Minor |
|---|---|
| Docs | `Phase_4/01` (doctrine) |
| Fix | Add: "Engines implement the Perception pillar of Software Cognition (see Phase -1)." |

#### N15 — Phase 5/07 Defines Interface That Belongs in Phase 3

| Severity | Minor |
|---|---|
| Docs | `Phase_5/07` (Memory), `Phase_3` (SCM) |
| Fix | Move reasoning store query interface to Phase 3 or add cross-reference. |

#### N16 — Phase 5/01 Interface Tables Missing `/v1/` Prefix

| Severity | Minor |
|---|---|
| Docs | `Phase_5/01` (Overview) |
| Fix | Add `/v1/` prefix to endpoint paths. |

#### N17 — Evidence Field Mismatch Between Phase 3 and Phase 5/04

| Severity | Minor |
|---|---|
| Docs | `Phase_3` (Evidence Model), `Phase_5/04` (Context Builder) |
| Fix | Add derivation/validation fields to Context Builder's evidence block or note they're stripped. |

#### N18 — Phase 5/05 Confidence Table Replicates Phase 3

| Severity | Minor |
|---|---|
| Docs | `Phase_5/05` (Confidence), `Phase_3` (Evidence Model) |
| Fix | Replace with cross-reference to Phase 3. |

#### N19 — Phase 5/09 Example 2 References Evidence ID Not in Listing

| Severity | Minor |
|---|---|
| Docs | `Phase_5/09` (Examples) |
| Fix | Add representative `evol_001` item to abbreviated listing. |

#### N20 — Pipeline Diagram Missing Insight Validator

| Severity | Minor |
|---|---|
| Docs | `Phase_5/08` (Reasoning Pipeline) |
| Fix | Add Insight Validator as substep of Stage 6 or distinct Stage 7. |

#### N21 — Phase 5/03 and Phase 5/06 Both Use `templates/` Directory

| Severity | Minor |
|---|---|
| Docs | `Phase_5/03` (Prompt Architecture), `Phase_5/06` (Explainability) |
| Fix | Clarify template directory structure or use separate subdirectories. |

#### N22 — Phase 6/01 REST Port Not Explicitly Stated

| Severity | Minor |
|---|---|
| Docs | `Phase_6/01` (API Overview) |
| Fix | Add "Default port: 8000." |

#### N23 — GraphQL Does Not Define HTTP Method

| Severity | Minor |
|---|---|
| Docs | `Phase_6/03` (GraphQL API) |
| Fix | Add note: "All GraphQL operations use POST." |

#### N24 — Cross-Phase Principle References Sparse in Phase 6

| Severity | Minor |
|---|---|
| Docs | All Phase 6 documents |
| Fix | Add Phase -1/3/4 cross-references where relevant. |

#### N25 — Reason Channel Not in WebSocket Event Catalog

| Severity | Minor |
|---|---|
| Docs | `Phase_6/04` (WebSocket API) |
| Fix | Add `reasoning:{insight_id}` as a formal channel pattern. |

#### N26 — Page Components Referenced in Routes Missing from Directory

| Severity | Minor |
|---|---|
| Docs | `Phase_7/02` (App Architecture) |
| Fix | Add missing page components to directory listing. |

#### N27 — `./lib/navigation` Referenced But Not in Directory Structure

| Severity | Minor |
|---|---|
| Docs | `Phase_7/02` (App Architecture) |
| Fix | Add `navigation.ts` to directory listing. |

#### N28 — `RecommendationCard` Defined But Never Consumed

| Severity | Minor |
|---|---|
| Docs | `Phase_7/04` (Component System) |
| Fix | Either remove or add to appropriate feature area. |

#### N29 — CLI `dna serve` Not Listed in Phase 7/01 CLI Commands

| Severity | Minor |
|---|---|
| Docs | `Phase_7/01` (Frontend Overview) |
| Fix | Add `dna serve` to CLI commands table. |

#### N30 — "PWA Ready" Mentioned But Not Explained

| Severity | Minor |
|---|---|
| Docs | `Phase_7/01` (Frontend Overview) |
| Fix | Clarify which PWA capabilities are implemented. |

#### N31 — `npm run build:cli` Not Defined Elsewhere

| Severity | Minor |
|---|---|
| Docs | `Phase_7/01` (Frontend Overview) |
| Fix | Add package.json script example or cross-reference. |

#### N32 — Phase 8/03 Project Structure Too Shallow

| Severity | Minor |
|---|---|
| Docs | `Phase_8/03` (Project Structure) |
| Fix | Expand with per-module subdirectory trees and naming conventions. |

#### N33 — Phase 8/05 Branching Strategy Too Shallow

| Severity | Minor |
|---|---|
| Docs | `Phase_8/05` (Branching Strategy) |
| Fix | Add edge cases (stale branches, revert scenarios, hotfix during release). |

#### N34 — Pre-Commit Checks Documented Inconsistently Across Phase 8

| Severity | Minor |
|---|---|
| Docs | `Phase_8/06`, `Phase_8/09`, `Phase_8/10` |
| Fix | Consolidate definitive list in one place. |

#### N35 — Phase 9/02 Unit Test Coverage Targets Need Clarification

| Severity | Minor |
|---|---|
| Docs | `Phase_9/02` (Unit Testing) |
| Fix | Clarify "90%+ (engine, scm)" to reference actual code packages. |

#### N36 — Phase 9/03 Integration Test Example Uses Undocumented APIs

| Severity | Minor |
|---|---|
| Docs | `Phase_9/03` (Integration Testing) |
| Fix | Add note: "For reasoning pipeline interface, see Phase 5/01." |

#### N37 — Phase 9/04 References Phase 4 Schema — Unverified Dependency

| Severity | Minor |
|---|---|
| Docs | `Phase_9/04` (Engine Validation) |
| Fix | Verify Phase 4 has formal evidence schema document. |

#### N38 — Phase 9/01 Test Data Strategy Missing Storage Location

| Severity | Minor |
|---|---|
| Docs | `Phase_9/01` (Testing Overview) |
| Fix | Document repository location and format for test fixtures. |

#### N39 — Phase 10/01 V1/V2+ Boundary Undefined

| Severity | Minor |
|---|---|
| Docs | `Phase_10/01` (Deployment Overview) |
| Fix | Add versioning note or cross-reference roadmap. |

#### N40 — Phase 10/02 Docker Section Missing Image Variants

| Severity | Minor |
|---|---|
| Docs | `Phase_10/02` (Local Installation) |
| Fix | Add note: "See Phase 10/03 for all image variants." |

#### N41 — Phase 10/03 Docker Socket Mount Without Security Note

| Severity | Minor |
|---|---|
| Docs | `Phase_10/03` (Docker) |
| Fix | Add security advisory for Docker socket mount. |

#### N42 — Phase 10/06 Monitoring Missing System-Level Metrics

| Severity | Minor |
|---|---|
| Docs | `Phase_10/06` (Monitoring) |
| Fix | Add CPU/RAM/disk metrics or note they're available via host OS. |

#### N43 — Phase 10 Docker Image Variants: Glossary vs Spec Consistent — No Fix Needed

| Severity | Minor |
|---|---|
| Docs | `Phase_10/10` (Glossary), `Phase_10/03` (Docker) |
| Status | These are actually consistent on second review. No action. |

#### N44 — Phase 10/07 `dna.auth` Logger References Undocumented Auth (see M19)

| Severity | Minor |
|---|---|
| Docs | `Phase_10/07` (Logging) |
| Fix | Same as M19 — add auth doc or cross-reference. |

#### N45 — Phase 11/04 Task ID Registry Has Examples for Only 2 of 19 Epics

| Severity | Minor |
|---|---|
| Docs | `Phase_11/04` (Task Breakdown) |
| Fix | Add example tasks for each epic or note that tasks are defined per-epic. |

#### N46 — Phase 11/03 Epic Template Empty for All 19 Epics

| Severity | Minor |
|---|---|
| Docs | `Phase_11/03` (Epics) |
| Fix | Populate epics with Goal, Scope, Acceptance Criteria, or expand table. |

#### N47 — Phase 11/05 Build Order Inconsistency

| Severity | Minor |
|---|---|
| Docs | `Phase_11/05` (Development Plan) |
| Fix | Clarify whether CLI depends on REST API or can be parallel. |

#### N48 — Phase 11/07 References Non-Existent `CHANGELOG.md`

| Severity | Minor |
|---|---|
| Docs | `Phase_11/07` (Release Strategy), `Phase_11/09` (Execution Guide) |
| Fix | Create CHANGELOG.md or replace with GitHub Releases reference. |

#### N49 — Phase 11/09 Validation Gates Reference Non-Existent Test Files

| Severity | Minor |
|---|---|
| Docs | `Phase_11/09` (Execution Guide) |
| Fix | Note that test files are created during E-15 and gates are retroactive. |

#### N50 — Phase 12/06 Ecosystem Cognition Labeling Mismatch

| Severity | Minor |
|---|---|
| Docs | `Phase_12/06` (Ecosystem Cognition), `Phase_12/10` (Glossary) |
| Fix | Either label as research (add Status section) or upgrade to planned spec. |

#### N51 — Phase 12/04/05/06 Overlapping Scope

| Severity | Minor |
|---|---|
| Docs | `Phase_12/04`, `Phase_12/05`, `Phase_12/06` |
| Fix | Add explicit boundary definitions between Org Graph, Cross-Repo, and Ecosystem. |

#### N52 — Phase 12/08 Plugin API Forward References Non-Existent `dna.plugins` Module

| Severity | Minor |
|---|---|
| Docs | `Phase_12/08` (Extensibility) |
| Fix | Mark code blocks as "Proposed API — subject to change." |

#### N53 — Phase 12/10 Glossary No Cross-Reference to Phase -1

| Severity | Minor |
|---|---|
| Docs | `Phase_12/10` (Glossary) |
| Fix | Add header stating core domain terms are defined in Phase -1. |

#### N54 — Phase -1 Glossary Contains Orphan "Architecture Engine" Entry

| Severity | Minor |
|---|---|
| Docs | `Phase_-1/12` (Glossary) |
| Fix | Either remove or add usage note. Not used in any document. |

#### N55 — Phase 5/02 References "Phase 0 Privacy & Ethics" — No Such Document

| Severity | Minor |
|---|---|
| Docs | `Phase_5/02` (LLM Architecture) |
| Fix | Update reference to correct Phase 0 document section. |

#### N56 — Phase 5/01 Reference Format "First Principle N" vs "Principle N"

| Severity | Minor |
|---|---|
| Docs | `Phase_5/01` (Overview), `Phase_-1` (First Principles) |
| Fix | Normalize format. Phase -1 uses "Principle N," not "First Principle N." |

#### N57 — Phase 6/09 Examples Missing in Phase 6 (already noted as present)

| Severity | Minor |
|---|---|
| Docs | — |
| Status | Phase 6/09 (`API_Examples.md`) exists and is substantive. No issue. |

#### N58 — Phase 9/10 Glossary Oversimplifies Performance Thresholds

| Severity | Minor |
|---|---|
| Docs | `Phase_9/10` (Glossary) |
| Fix | Replace blanket statement with cross-reference to Phase 9/08 thresholds. |

#### N59 — Phase 10 Glossary "Performance Testing" Entry Mismatch

| Severity | Minor |
|---|---|
| Docs | `Phase_9/10` (Glossary) |
| Status | Duplicate of N58. Consolidated. |

#### N60 — Phase 9/10 Glossary "Engine Validation" Repeats Schema Reference

| Severity | Minor |
|---|---|
| Docs | `Phase_9/10` (Glossary) |
| Fix | Same root issue as N37 — verify Phase 4 schema dependency. |

---

## SUMMARY

| Category | Count |
|---|---|
| **Critical** | **16** |
| **Major** | **35** |
| **Minor** | **60** |
| **Total Issues** | **111** |

### Issues by Phase

| Phase | Critical | Major | Minor | Total |
|---|---|---|---|---|
| Phase -1 (Philosophy) | 0 | 1 | 2 | 3 |
| Phase 0 (Product Strategy) | 2 | 0 | 2 | 4 |
| Phase 1 (UX/Design) | 0 | 0 | 0 | 0 |
| Phase 2 (Architecture) | 1 | 0 | 0 | 1 |
| Phase 3 (SCM) | 1 | 3 | 3 | 7 |
| Phase 4 (Engines) | 1 | 4 | 6 | 11 |
| Phase 5 (Reasoning) | 2 | 5 | 7 | 14 |
| Phase 6 (API) | 1 | 4 | 3 | 8 |
| Phase 7 (Frontend) | 2 | 3 | 5 | 10 |
| Phase 8 (Standards) | 0 | 2 | 3 | 5 |
| Phase 9 (Testing) | 3 | 4 | 7 | 14 |
| Phase 10 (Deployment) | 1 | 5 | 8 | 14 |
| Phase 11 (Execution) | 2 | 8 | 6 | 16 |
| Phase 12 (Future Vision) | 0 | 0 | 6 | 6 |

### Grade by Phase

| Phase | Grade |
|---|---|
| Phase -1 (Philosophy) | B+ |
| Phase 0 (Product Strategy) | B |
| Phase 1 (UX/Design) | A (no issues found) |
| Phase 2 (Architecture) | A- (few issues) |
| Phase 3 (SCM) | B |
| Phase 4 (Engines) | B- |
| Phase 5 (Reasoning) | B- |
| Phase 6 (API) | B |
| Phase 7 (Frontend) | B |
| Phase 8 (Standards) | B+ |
| Phase 9 (Testing) | C+ |
| Phase 10 (Deployment) | C+ |
| Phase 11 (Execution) | C |
| Phase 12 (Future Vision) | B |

---

## PRIORITY ORDER FOR FIXING

### Tier 1 — Fix Immediately (Blocking Issues)

| Priority | Issue | Reason |
|---|---|---|
| 1 | C04 — V1 scope contradiction | Core identity — "is V1 single-repo or 1,000-repo?" |
| 2 | C05 — Time to Understanding metric | Metric contradiction makes the doc unusable |
| 3 | C06 — Performance targets unachievable | Implementors cannot target impossible specs |
| 4 | C07 — Token budget contradiction | Directly affects prompt template implementation |
| 5 | C01 — V4 version inconsistency | Versioning is referenced everywhere |

### Tier 2 — Fix Before V1 Build

| Priority | Issue | Reason |
|---|---|---|
| 6 | C08 — Fallback endpoint doesn't exist | API doc references non-existent route |
| 7 | C09 — Test coverage engine doesn't exist | Example references non-existent component |
| 8 | C10 — Search history contradiction | UI implementation will hit conflicting specs |
| 9 | C11 — Autocomplete endpoint undefined | UI feature depends on non-existent API |
| 10 | C15 — SCM Writer protocol undefined | Every engine depends on this type |
| 11 | M07 — SQLite uses JSONB | Schema invalid against SQLite |
| 12 | M09 — Insight Validator unspecified | Critical QA component has no spec |
| 13 | M10 — Intent Recognition unspecified | Stage 1 of pipeline has no spec |

### Tier 3 — Fix Before V2

| Priority | Issue | Reason |
|---|---|---|
| 14 | C02 — V3 scope contradiction | Affects V2/V3 roadmap alignment |
| 15 | C03 — Audit logging double-booked | Different versions, same feature |
| 16 | M04 — Four pillars mismatch | Philosophical inconsistency in SCM foundation |
| 17 | M13 — Health endpoint versioning | Versioning policy contradicts spec |
| 18 | M14 — GraphQL path unspecified | API cannot be implemented |
| 19 | M15 — Auth endpoints undefined | Security-critical endpoints lack spec |

### Tier 4 — Cross-Reference and Consistency Pass

| Priority | Issue | Files |
|---|---|---|
| 20 | M01 — Phase 11/12 cross-refs | Add links to Phases 1-9 |
| 21 | M02 — Phase 10 CI/CD → Phase 9 | Wire quality gates into CI |
| 22 | M03 — Phase -1 cross-refs across all phases | Add master glossary references |
| 23 | C16, M05, M06 — Glossary dedup | Remove duplicated glossary entries |

### Tier 5 — Documentation Housekeeping

| Priority | Description |
|---|---|
| 24 | All N-level issues (60 items) — terminology, path fixes, shallow sections, missing details |

---

## RECOMMENDATIONS

1. **Cross-Reference Pass:** Every document after Phase 4 needs to reference its dependencies. Minimum: Phase 7→6→5, Phase 9→5→4→3, Phase 10→9, Phase 11/12→Phase 0 (metrics) and Phase 1-9.

2. **Version Alignment:** Phase -1, Phase 0, Phase 2, Phase 11, and Phase 12 need a unified versioning scheme. Recommend following Phase 11/01's V1/V2/V3 scheme and updating the foundational docs to match, or restoring V4.

3. **Glossary Consolidation:** Each phase has its own glossary, many duplicating Phase -1. Convention should be: Phase -1 = master; Phase X glossaries only define terms unique to that phase.

4. **Sign-off Review for V1 Documents:** Before V1 build begins, every document in Phases 3, 4, 5, 6, and 7 should have its concrete specifications validated for internal consistency and implementability.

5. **Add Missing Specifications:**
   - Insight Validator (Phase 5/06)
   - Intent Recognition (Phase 5/01 or 5/04)
   - SCM Writer protocol (Phase 3)
   - Auth endpoints (Phase 6/02)
   - `POST /v1/reason/suggest` (Phase 6/02)

---

*End of Audit Report*
