================================================================================
# 07 AI Agent Handbook
================================================================================

# AI Agent Handbook

## Purpose

This handbook defines how AI coding agents (LLM-based tools) should operate within the Project DNA codebase. It establishes rules for prompt construction, output validation, context management, and the human-in-the-loop verification process that ensures AI-generated code meets the same quality standards as human-written code.

---

## Scope

### In Scope

- When AI agents may be used
- Prompt construction rules
- Output validation requirements
- Context management for long-running tasks
- Human review and approval gates
- Prohibited behaviors

### Out of Scope

- General coding standards (Phase 8/02)
- Code review process (Phase 8/06)
- Documentation standards (Phase 8/08)

---

## Permitted Use Cases

AI agents may be used for:

| Task | Approval | Review Requirements |
|---|---|---|
| Documentation generation | No approval needed | Human reviews for accuracy |
| Boilerplate code | No approval needed | Standard code review |
| Test generation | No approval needed | Tests must pass |
| Bug fixes (isolated) | No approval needed | Standard code review |
| Refactoring | Architecture review | In-depth code review |
| Feature implementation | Feature spec required | Full code review |
| Architecture decisions | Never — human only | N/A |

---

## Prompt Construction Rules

### Context Budget

When constructing prompts for AI agents:

| Task Type | Max Context Size | Notes |
|---|---|---|
| Simple edit | 4K tokens | Single function or file |
| Documentation | 8K tokens | Reference 2-3 source files |
| Feature implementation | 16K tokens | Include interface contracts |
| Architecture analysis | 32K tokens | Include relevant phase docs |

### Required Context

Every prompt must include:

1. **Task description**: What to do, in one paragraph.
2. **Constraints**: Any must-follow rules (language, framework, patterns).
3. **Reference files**: File paths and relevant excerpts.
4. **Output format**: Where to write the output, what format.
5. **Verification criteria**: How to check the output is correct.

### Prohibited Prompts

- "Rewrite this entire module" without a specific goal.
- "Make it better" — vague, unverifiable.
- "Ignore the tests" — tests must pass.

---

## Output Validation

Before submitting AI-generated code, validate:

### Automated Checks

- [ ] Code compiles / type-checks.
- [ ] Linting passes (Ruff, ESLint, clippy).
- [ ] Existing tests pass.
- [ ] No secrets or credentials in output.
- [ ] No placeholder values (e.g., `change_me`, `TODO` without ticket).

### Human Review Gates

| Gate | Required For | Reviewer |
|---|---|---|
| Format check | All output | Automated (CI) |
| Logic review | Feature implementation | Engineer |
| Security review | Auth, data access | Engineer |
| Architecture review | New modules, significant refactors | Architect |

---

## Prohibited Behaviors

| Behavior | Why |
|---|---|
| Generating secrets, keys, or credentials | Security risk — never commit |
| Modifying CI/CD configuration without explicit instructions | Safety — could break deployments |
| Rewriting tests without running them | Tests might fail silently |
| Adding dependencies without justification | Dependency bloat, security surface |
| Removing error handling | Degrades robustness |
| Outputting code that references non-existent APIs | Will fail at runtime |

---

## Agent Guidelines

1. **Ask before acting** — if the task is ambiguous, ask for clarification rather than guessing.
2. **Minimize changes** — change only what is necessary to fulfill the task.
3. **Follow existing patterns** — match the style, structure, and conventions of surrounding code.
4. **Explain reasoning** — when the approach is non-obvious, explain why in a comment.
5. **Respect module boundaries** — do not import across layers unless the architecture permits it.
6. **Test your output** — verify correctness before presenting it for review.
