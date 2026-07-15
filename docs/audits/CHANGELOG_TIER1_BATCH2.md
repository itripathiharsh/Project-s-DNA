================================================================================
# Tier 1 Batch 2 Fixes — CHANGELOG
================================================================================

## C02 — V3 Description Contradiction

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 0 defined V3 as "Runtime-integrated cognition" (referring to Operational Cognition — correlating runtime behavior with code), while Phase 11/01 and Phase 12/01 define V3 as "Organization Cognition" (enterprise-scale, SSO, audit, on-premise). Two different conceptual frameworks (integration depth vs organizational scale) were used for the same version label. |
| Files modified | `Phase_0_Foundation_Product_Strategy_COMBINED.md` (1 location — glossary) |
| Change | Updated V3 glossary entry from "Runtime-integrated cognition" to "Organization cognition (runtime-integrated)." This unifies both frameworks: V3 is primarily about organization-scale cognition, with runtime integration as a key sub-capability (Operational Cognition remains tagged as V3 in the capabilities table). |
| Why required | The contradiction would confuse implementers about which version's capabilities to build. A V3 targeting "Runtime-integrated" and another targeting "Organization" would lead to divergent roadmaps. |

---

## C03 — Audit Logging Double-Scheduled

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 11/02 M6 (V2, Month 12) listed "Audit logging" as a milestone epic, while Phase 11/01 V3 M10 (Month 24) also includes "audit logging" as part of enterprise features. Same feature name, different versions — contradictory scheduling. |
| Files modified | `Phase_11/02_Milestones.md` (1 location — M6 epic table) |
| Change | Changed V2 M6 "Audit logging" to "Basic audit events" to distinguish it from V3's "Enterprise audit logging." V2 gets lightweight event logging (key actions tracked); V3 gets full audit with retention, search, and compliance reporting. |
| Why required | Two conflicting schedules for the same feature make the roadmap contradictory and erode implementation credibility. |

---

## C08 — Fallback Endpoint Non-Existent

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 6/02 referenced `/v1/reason/question/evidence-summary` as a fallback endpoint in the "Ollama unavailable" error response (line 601), but no such endpoint was defined anywhere in the API specification. |
| Files modified | `Phase_6/02_REST_API.md` (1 location — new endpoint added) |
| Change | Added `POST /v1/reason/question/evidence-summary` endpoint definition with request/response schema. The endpoint bypasses LLM inference and returns raw evidence directly, matching the behavior described in Phase 5/09 Example 7 (Deterministic Fallback). |
| Why required | A referenced endpoint that does not exist in the API spec breaks the dependency chain between documentation and implementation. |

---

## C09 — Test Coverage Engine Reference

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 5/09 Example 6 (Insufficient Evidence) referenced a "test coverage engine" as the source for coverage data. The Phase 4 engine catalog (Engine Registry) contains no test coverage engine — only Structural, Evolution, Knowledge, Dependency, Risk, Architectural, Decision, and Prediction engines. |
| Files modified | `Phase_5/09_Examples.md` (1 location — Example 6 text) |
| Change | Changed the example's language from referencing a specific "test coverage engine" to generic "test coverage data" / "test coverage analysis." Updated the limitation text and recommendation to cross-reference Phase 4's engine catalog rather than naming a non-existent engine. |
| Why required | Referencing an undefined engine in code examples creates confusion about the engine catalog and suggests an inconsistency between Phase 4 and Phase 5. |

---

## C10 — Search History Persistence Contradiction

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 7/03 (State Management) persistence table stated that `searchStore` is NOT persisted, while Phase 7/06 (Search and Query UI) explicitly states "Search history is stored in Zustand with localStorage persistence" and describes features like recent searches, clear history, and saved favorites. |
| Files modified | `Phase_7/03_State_Management.md` (1 location — persistence table) |
| Change | Changed `searchStore` persistence from "No" to "Yes" with medium "localStorage" and fields "query, selectedEntities." This aligns Phase 7/03 with Phase 7/06's defined behavior. |
| Why required | Two contradictory statements about whether search state persists would lead to data loss or confusion during implementation. |

---

## C11/C12 — POST /v1/reason/suggest Undefined

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 7/06 (Search and Query UI) references `POST /v1/reason/suggest` for autocomplete suggestions in the search bar dropdown, but this endpoint is never defined in Phase 6/02 (REST API). |
| Files modified | `Phase_6/02_REST_API.md` (1 location — new endpoint added) |
| Change | Added `POST /v1/reason/suggest` endpoint definition with request/response schema. Returns question completions based on partial user input, used by the frontend autocomplete dropdown. |
| Why required | A referenced API endpoint must exist in the API specification or the frontend implementation has no contract to implement against. |

---

## C13 — Quality Gate Thresholds Contradiction

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 9/01 (Testing Overview) quality gate table said "Latency > 2x baseline" as a single blanket threshold for performance regression. Phase 9/08 (Performance Testing) defines per-metric thresholds with different warning/blocking values (API: 1.5x/3x, Reasoning: 2x/4x, Memory: 1.5x/2x, etc.). |
| Files modified | `Phase_9/01_Testing_Overview.md` (1 location — quality gates table) |
| Change | Updated the Performance regression gate from "Latency > 2x baseline" to "Per-metric thresholds — see Phase 9/08." This removes the contradictory blanket rule and cross-references the authoritative source. |
| Why required | A blanket threshold contradicts the more nuanced per-metric thresholds, creating ambiguity about which rule to follow. |

---

## C14 — Deterministic Test Doctrine vs AI Evaluation

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 9/01 Testing Doctrine stated "Tests are deterministic. They run in CI. They fail fast. A test failure means a bug, not a flake." This directly contradicts Phase 9/07 AI Evaluation, which explicitly uses probabilistic metrics (hallucination rate, instruction adherence) with statistical thresholds rather than pass/fail assertions. |
| Files modified | `Phase_9/01_Testing_Overview.md` (1 location — Testing Doctrine) |
| Change | Extended the Testing Doctrine to distinguish between deterministic tests (unit, integration, validation — same input → same output) and probabilistic evaluation (AI eval — uses benchmark datasets with statistical thresholds). The deterministic principle still holds for deterministic tests; AI evaluation operates at a different layer. |
| Why required | The absolute "all tests are deterministic" statement would prevent the introduction of AI evaluation, which is inherently probabilistic and explicitly designed for the Reasoning Layer. |

---

## C15 — SCM Writer Protocol Undefined

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 4/01 (Engine Interface Contract) uses `scm: SCMWriter` as a type annotation in the engine's `run()` method, but `SCMWriter` is never defined as a protocol/class in Phase 3 or Phase 4. The write-side interface for engines to persist evidence into the SCM was missing entirely. |
| Files modified | `Phase_3_Software_Cognition_Model_COMBINED.md` (1 location — new section after Query Interface Doctrine) |
| Change | Added "SCM Writer Protocol" section to Phase 3, defining the write-side counterpart to the Query Interface. The protocol includes methods: write_evidence, write_evidence_batch, update_entity, create_entity, add_relationship, and mark_analysis_complete. Added cross-reference to Phase 4/01. |
| Why required | A type used in the engine interface contract must be defined somewhere. Without the protocol definition, implementers cannot know the correct interface for writing evidence to the SCM. |

---

## C16 — Phase 9 Zero Cross-References

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 9 (Testing) has no cross-references to Phases -1, 3, 5, or 6, despite depending on components defined in those phases (SCM Data Model, Cognitive Engines, Reasoning Pipeline, API Gateway). |
| Files modified | `Phase_9/01_Testing_Overview.md` (1 location — new Phase Dependencies section) |
| Change | Added "Phase Dependencies" table to Phase 9/01 Scope section, listing Phase 3 (SCM Data Model), Phase 4 (Cognitive Engines), Phase 5 (Reasoning Pipeline), and Phase 6 (API Gateway) with their relevance to testing. |
| Why required | Zero cross-references to upstream phases means readers cannot trace which architectural components the testing strategy validates, breaking the documentation's dependency chain. |

---

## Summary

| Issue | Files Changed | Change Type |
|---|---|---|
| C02 | 1 | Glossary update |
| C03 | 1 | Milestone epic rename |
| C08 | 1 | New API endpoint definition |
| C09 | 1 | Example text update |
| C10 | 1 | Persistence table update |
| C11/C12 | 1 | New API endpoint definition |
| C13 | 1 | Quality gate cross-reference |
| C14 | 1 | Doctrine qualification |
| C15 | 1 | Protocol definition |
| C16 | 1 | Cross-reference section added |
| **Total** | **5 files** | **10 fixes applied** |

*End of Tier 1 Batch 2 Fixes*
