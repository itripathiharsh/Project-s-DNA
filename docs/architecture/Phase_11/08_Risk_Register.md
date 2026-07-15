================================================================================
# 08 Risk Register
================================================================================

# Risk Register

## Purpose

The risk register identifies, assesses, and tracks risks that could impact the successful delivery of Project DNA. It is a living document reviewed at each milestone.

---

## Risk Assessment Matrix

| Likelihood \ Impact | Low | Medium | High |
|---|---|---|---|
| **High** | R-005 | R-003 | R-001 |
| **Medium** | R-006 | R-002, R-004 | — |
| **Low** | — | — | — |

## Registered Risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R-001 | LLM hallucination reduces trust in insights | High | High | Grounding pipeline, confidence scores, AI eval suite | ML team |
| R-002 | Performance degrades on large repositories (> 100K files) | Medium | Medium | Benchmark budget, pagination, lazy loading | Backend team |
| R-003 | Ollama dependency breaks or changes | High | Medium | Multiple model support, fallback model, container isolation | DevOps |
| R-004 | Frontend becomes slow with large evidence graphs | Medium | Medium | Virtual scrolling, graph LOD levels, Web Workers | Frontend team |
| R-005 | SCM storage grows unbounded | High | Low | Data retention policies, archiving, paginated queries | Backend team |
| R-006 | User onboarding friction (Python not installed, etc.) | Medium | Low | Binary distribution via Tauri, Docker, npm | DevOps |

## Risk Response Strategies

| Strategy | When Used |
|---|---|
| **Avoid** | Remove the risky feature from scope |
| **Mitigate** | Reduce likelihood or impact |
| **Transfer** | Use external service (e.g., managed LLM API) |
| **Accept** | Document and monitor; take no action |
