================================================================================
# 01 Engineering Principles
================================================================================

# Engineering Principles

## Purpose

Engineering principles guide every decision made during the implementation of Project DNA. They are the shared values that ensure consistency across modules, contributors, and time. When engineers face trade-offs, these principles resolve them.

---

## Scope

### In Scope

- Core engineering principles (10 principles)
- Decision framework for trade-offs
- Principles by discipline (backend, frontend, data, AI)
- Principle enforcement in code review

### Out of Scope

- Coding standards (Phase 8/02)
- Specific tool configurations
- Project management practices

---

## The Principles

### Principle 1: Deterministic First

Every computation that can be done deterministically must be done deterministically. AI is used only where probabilistic reasoning adds unique value — never where a simple algorithm suffices.

**Why:** Deterministic code is testable, debuggable, and auditable. AI outputs are probabilistic and require validation. Using AI as a default introduces unnecessary uncertainty.

**Trade-off:** Sometimes deterministic code is harder to write than calling an LLM. Write it anyway.

### Principle 2: Local by Default

All data and computation stay on the user's machine unless explicitly configured otherwise. No telemetry, no cloud dependencies, no data egress.

**Why:** Users must trust Project DNA with their entire codebase. That trust is earned by keeping data local. Network activity must always be opt-in.

**Trade-off:** Local execution limits hardware (no large GPU clusters). Design for consumer hardware from the start.

### Principle 3: Evidence-Bound Output

Every output — every insight, prediction, recommendation — must be traceable to source evidence. If a claim cannot cite evidence, it is not included.

**Why:** Trust requires traceability. Users must be able to verify every conclusion by following the evidence chain to the raw data.

**Trade-off:** Some synthesis may be less fluent or comprehensive. Grounded correctness always beats fluent hallucination.

### Principle 4: Test the Contract, Not the Implementation

Tests validate behavior (inputs → outputs), not internal implementation. Module boundaries are tested via their public interfaces. Internal refactoring never breaks tests.

**Why:** Tests that depend on implementation details break during refactoring, creating maintenance burden and reducing confidence.

**Trade-off:** Contract testing may miss edge cases in internal logic. Use internal unit tests sparingly for complex algorithms.

### Principle 5: Fail Explicitly

When something goes wrong, the system produces a clear, actionable error — never a silent failure or a misleading success. Every error has a code, a message, and a suggestion.

**Why:** Silent failures erode trust. Users need to know what went wrong and what to do about it.

**Trade-off:** More error handling code. More branches to test. Better user experience.

### Principle 6: Prefer Composition Over Inheritance

Modules, components, and data structures use composition to combine behaviors. Inheritance is limited to framework-specific requirements.

**Why:** Composition produces smaller, testable, reusable units. Inheritance creates deep hierarchies that are hard to change.

**Trade-off:** More small files, more wiring code. Clearer boundaries.

### Principle 7: Write Code for Humans

Code is read more often than it is written. Prioritize readability, clarity, and simple solutions over clever or optimized ones. Optimization decisions include a comment explaining the performance rationale.

**Why:** The codebase will outlive any single contributor. Future engineers (including your future self) must understand why code exists and how it works.

**Trade-off:** Sometimes a more verbose solution is slower. Optimize only when profiling proves the bottleneck.

### Principle 8: Small Modules, Clear Boundaries

Every module does one thing and has one reason to change. Modules communicate through well-defined interfaces. Circular dependencies are not allowed.

**Why:** Small modules are independently testable, replaceable, and understandable. Clear boundaries prevent the system from becoming a monolith.

**Trade-off:** More module boundaries, more interfaces. Requires discipline to maintain.

### Principle 9: Progress Over Perfection

Ship working software early, iterate based on feedback, and improve continuously. V1 features are designed to be good enough — they are refined in V2 and V3 based on real usage.

**Why:** Perfecting a feature that users don't need is wasted effort. Real usage reveals what matters.

**Trade-off:** V1 may have rough edges. The architecture must support refactoring without rewriting.

### Principle 10: Everything as Code

Configuration, documentation, infrastructure, and pipelines are defined as code — versioned, reviewed, and tested alongside application code.

**Why:** Manual processes are error-prone, unrepeatable, and invisible. Code-defined processes are auditable, reproducible, and improvable.

**Trade-off:** More files to maintain. Higher setup cost. Lower operational risk.

---

## Decision Framework

When facing a trade-off between principles:

```
1. Does one principle clearly apply while others do not?
   → Follow the applicable principle.

2. Do multiple principles conflict?
   → Prioritize: 1 (Deterministic) > 2 (Local) > 3 (Evidence) > 4 (Test Contract)
     > 5 (Fail Explicit) > 6 (Composition) > 7 (Human Code) > 8 (Small Modules)
     > 9 (Progress) > 10 (Everything as Code)

3. Is the decision still unclear?
   → Write a brief ADR (Architecture Decision Record) explaining the trade-off
     and the chosen resolution.
```

---

## Principle Enforcement

| Mechanism | How Principles Are Applied |
|---|---|
| **Code review** | Reviewers check for principle violations. Deterministic-first and evidence-bound are highest priority. |
| **Architecture review** | Significant design decisions are reviewed against principles before implementation. |
| **Automated checks** | Linting enforces module boundaries (circular dependency detection). |
| **Documentation** | ADRs document principle-based decisions for future reference. |
