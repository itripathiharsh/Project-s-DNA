================================================================================
# 05 Branching Strategy
================================================================================

# Branching Strategy

## Purpose

A lightweight branching strategy that supports continuous development, parallel feature work, and clean releases without the overhead of Git Flow.

---

## Model

### Branches

| Branch | Base | Purpose | Lifetime |
|---|---|---|---|
| `main` | — | Production-ready code. Always deployable. | Permanent |
| `develop` | `main` | Integration branch for feature work. | Permanent |
| `feat/<name>` | `develop` | Single feature or bug fix. | Short-lived (days) |
| `fix/<name>` | `develop` | Bug fix. | Short-lived (days) |
| `release/v<ver>` | `develop` | Release preparation. | Short-lived (days) |
| `hotfix/<name>` | `main` | Critical production fix. | Short-lived (hours) |

### Flow

```
main ────●────────────────●──────────●────
          \              /          /
develop ──●──●──●────●──●──────────●─────
              \    /  \    /
feat/auth      ●──●    ●──●
                          \
fix/null-check            ●──●

1. Feature branches branch from develop
2. PR merges to develop (squash merge)
3. develop is always integration-ready
4. Release branch from develop for final testing
5. Release merges to main (merge commit) and back to develop
6. Hotfix branches from main, merge to main and develop
```

## Rules

| Rule | Reason |
|---|---|
| No direct commits to `main` or `develop` | All changes go through PRs |
| Feature branches rebase daily | Avoid merge conflicts |
| Delete branch after merge | Keep branch list clean |
| `main` must never be force-pushed | History is sacred |
| One feature = one branch | Clear scope, easy review |
