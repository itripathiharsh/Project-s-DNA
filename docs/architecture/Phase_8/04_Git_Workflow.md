================================================================================
# 04 Git Workflow
================================================================================

# Git Workflow

## Purpose

A consistent Git workflow ensures clean commit history, predictable collaboration, and reliable releases. This document defines commit conventions, pull request practices, and repository management rules.

---

## Commit Conventions

### Format

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

### Types

| Type | Usage | Example |
|---|---|---|
| `feat` | New feature | `feat(engine): add trace cognition engine` |
| `fix` | Bug fix | `fix(api): handle null evidence_refs in insight response` |
| `docs` | Documentation | `docs(phase7): add dashboard architecture doc` |
| `refactor` | Code change with no behavior change | `refactor(scm): extract query builder` |
| `test` | Adding or fixing tests | `test(engine): add structural engine edge cases` |
| `chore` | Maintenance, tooling, dependencies | `chore: update ruff to v0.5` |
| `perf` | Performance improvement | `perf(ui): memoize evidence list rows` |

### Scope

| Scope | Module |
|---|---|
| `engine` | Cognitive Engines |
| `scm` | SCM storage |
| `reasoning` | Reasoning layer |
| `api` | API Gateway |
| `ui` | Frontend |
| `cli` | CLI tool |
| `docs` | Documentation |
| `infra` | CI/CD, Docker |

### Rules

- Description: imperative mood, no period, max 72 chars.
- Body: wrap at 72 chars. Explain what and why, not how.
- Footer: reference issues: `Closes PROJ-123`.
- No `WIP` commits. Use draft PRs instead.
- No merge commits. Use rebase or squash merge.

### Examples

```
feat(engine): implement trace cognition engine

Adds a new engine that traces function calls from log files.
Supports incremental mode (tail new log entries).
Closes PROJ-456.

fix(ui): handle empty evidence list in dashboard

The dashboard alert section crashes when no evidence exists
for the active repository. Check for empty array before rendering.
Fixes PROJ-789.
```
