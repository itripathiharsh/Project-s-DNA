================================================================================
# 09 Development Workflow
================================================================================

# Development Workflow

## Purpose

The development workflow defines how engineers take a task from idea to merged code. It is the day-to-day process that implements the branching strategy and code review policies.

---

## Workflow Steps

```
1. Pick task from project board
2. Create branch from develop
3. Implement + write tests
4. Run pre-commit checks
5. Push branch
6. Create PR
7. Address review feedback
8. Merge (squash)
9. Delete branch
```

## Day-to-Day

```bash
# Start a new feature
git checkout develop
git pull
git checkout -b feat/my-feature

# During development
git add <files>
git commit -m "feat(scope): description"

# Sync with develop daily
git fetch origin
git rebase origin/develop

# Push
git push -u origin feat/my-feature

# Create PR via GitHub CLI
gh pr create --fill
```

## Pre-Commit Checks

Run before every commit:

```bash
# Format
ruff format .
prettier --write .

# Lint
ruff check .
eslint .

# Type check
mypy .
tsc --noEmit
cargo check

# Test
pytest
vitest run
cargo test
```

## CI Pipeline

| Stage | Tool | Trigger |
|---|---|---|
| Format check | Ruff, Prettier | Every push |
| Lint | Ruff, ESLint, clippy | Every push |
| Type check | mypy, tsc, cargo | Every push |
| Unit tests | pytest, vitest | Every push |
| Integration tests | pytest | PR to develop |
| Security scan | pip-audit, npm audit | Weekly |
