================================================================================
# 10 Glossary
================================================================================

# Glossary

## Purpose

This glossary defines key terms introduced across Phase 8 (Engineering Standards).

---

## A

### ADR (Architecture Decision Record)

A short document capturing an architecture decision, its context, alternatives considered, and the rationale for the chosen approach. Stored in `docs/adr/`. Used when engineering principles conflict and a clear resolution is needed.

*See:* Phase 8/01.

### AI Agent Handbook

A set of rules governing how AI coding agents operate in the Project DNA codebase. Defines permitted use cases, prompt construction rules, output validation gates, and prohibited behaviors. Located at `docs/Phase_8/07_AI_Agent_Handbook.md`.

---

## C

### Coding Standards

Mandatory rules for code style, naming, typing, error handling, and file organization across Python, TypeScript, and Rust. Enforced by automated formatters and linters. Defined in Phase 8/02.

### Code Review Checklist

A set of verification items reviewers check for every PR: coding standards compliance, principle alignment, test coverage, error handling, security, backward compatibility, and documentation. Defined in Phase 8/06.

### Commit Convention

A structured format for Git commit messages: `type(scope): description`. Types include feat, fix, docs, refactor, test, chore, perf. Defined in Phase 8/04.

---

## E

### Engineering Principles

The 10 foundational values that guide all implementation decisions: Deterministic First, Local by Default, Evidence-Bound Output, Test the Contract, Fail Explicitly, Prefer Composition, Write Code for Humans, Small Modules, Progress Over Perfection, Everything as Code. Defined in Phase 8/01.

---

## P

### Pre-Commit Checks

Automated checks that run before every commit: formatting (Ruff, Prettier), linting (Ruff, ESLint, clippy), type checking (mypy, tsc, cargo), and tests (pytest, vitest, cargo test). Defined in Phase 8/09.
