================================================================================
# 02 Milestones
================================================================================

# Milestones

## Purpose

Milestones decompose the product roadmap into concrete delivery gates. Each milestone has a clear definition of done, a target date, and a set of epics that must be complete.

---

## V1 Milestones

### M1: Foundation (Month 3)

| Epic | Dependencies | Status |
|---|---|---|
| Core SCM implementation | None | Planned |
| Structural Cognition Engine | Core SCM | Planned |
| Evidence storage (SQLite) | Core SCM | Planned |
| REST API (evidence query) | Core SCM, Storage | Planned |
| CLI: `dna serve` | REST API | Planned |

**Definition of Done:** User can run `dna serve`, import a repo, and query evidence via REST API.

### M2: Reasoning (Month 5)

| Epic | Dependencies | Status |
|---|---|---|
| Ollama integration | M1 | Planned |
| Prompt architecture | M1 | Planned |
| Context builder | M1 | Planned |
| Reasoning pipeline | Ollama, Context | Planned |
| Insight storage | Storage | Planned |

**Definition of Done:** User can ask natural language questions and receive grounded insights.

### M3: UI (Month 7)

| Epic | Dependencies | Status |
|---|---|---|
| Frontend framework (Tauri + Svelte) | M2 | Planned |
| Dashboard | M2 | Planned |
| Evidence Explorer | M2 | Planned |
| Search UI | M2 | Planned |
| Graph visualization | M1 | Planned |

**Definition of Done:** User can run `dna ui` and perform all analysis tasks from the browser.

### M4: Polish (Month 8)

| Epic | Dependencies | Status |
|---|---|---|
| Unit + integration test suite | M3 | Planned |
| Performance benchmarks | M3 | Planned |
| AI evaluation pipeline | M3 | Planned |
| Installation packages (npm, Tauri, Docker) | M3 | Planned |
| Documentation | M3 | Planned |

**Definition of Done:** All tests pass, benchmarks meet budgets, packages published.

## V2 Milestones

### M5: Multi-user (Month 10)

| Epic | Dependencies |
|---|---|
| PostgreSQL backend | M4 |
| Auth system (JWT, API keys) | M4 |
| Team management | M4 |
| Role-based access control | M4 |

### M6: Collaboration (Month 12)

| Epic | Dependencies |
|---|---|
| Shared dashboards | M5 |
| Insight commenting | M5 |
| Notification system | M5 |
| Basic audit events | M5 |

### M7: Integrations (Month 14)

| Epic | Dependencies |
|---|---|
| GitHub webhook handler | M5 |
| GitLab webhook handler | M5 |
| Slack bot | M6 |
| CI/CD integration | M6 |

## V3 Milestones

| Milestone | Focus | Target |
|---|---|---|
| M8: Scale | Plugin system, custom engines | Month 18 |
| M9: Ecosystem | VSCode extension, public API | Month 20 |
| M10: Enterprise | SSO, audit, on-premise | Month 24 |

## V4 Milestones

| Milestone | Focus | Target |
|---|---|---|
| M11: External Data | CVE feeds, package registries, license data | Month 28 |
| M12: Cross-Org | Vulnerability blast radius, ecosystem trends | Month 32 |
| M13: Research | Industry-scale patterns, open-source health | Month 36 |
