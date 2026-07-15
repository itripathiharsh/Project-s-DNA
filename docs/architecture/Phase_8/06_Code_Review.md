================================================================================
# 06 Code Review
================================================================================

# Code Review

## Purpose

Code review is the primary quality gate for all changes to Project DNA. It ensures correctness, consistency, and knowledge sharing. This document defines the review process, expectations, and checklist.

---

## Process

```
Author creates PR → Assigns reviewers → Reviewers review → Author addresses feedback → Approve → Merge
```

### PR Requirements

| Requirement | Standard |
|---|---|
| Title | Follows commit convention: `type(scope): description` |
| Description | What, why, how, testing notes, screenshots (if UI) |
| Size | Max 400 lines changed (exclude generated files) |
| Tests | Tests included or rationale for omission |
| CI | All checks pass |
| Draft | Use draft PR for work-in-progress |

### Reviewer Assignment

| PR Type | Required Reviewers | Time to Review |
|---|---|---|
| Feature | 2 engineers | < 24 hours |
| Bug fix | 1 engineer | < 4 hours (if blocking) |
| Documentation | 1 engineer | < 48 hours |
| Hotfix | 1 engineer | < 1 hour |

## Review Checklist

- [ ] Does the code follow the coding standards (Phase 8/02)?
- [ ] Does the code follow engineering principles (Phase 8/01)?
- [ ] Are there tests for new functionality?
- [ ] Do existing tests still pass?
- [ ] Is error handling explicit?
- [ ] Are there no security concerns (hardcoded secrets, injection)?
- [ ] Is the API backward-compatible (if applicable)?
- [ ] Are there no TODO/FIXME without a ticket reference?
- [ ] Is documentation updated (if applicable)?

## Review Culture

| Do | Don't |
|---|---|
| Be specific: "Line 42: handle null entity_id" | "Fix this" |
| Explain the why behind suggestions | Nitpick style (formatter handles it) |
| Approve if the code is correct, even if you'd write it differently | Block for subjective preferences |
| Ask questions if unclear: "What does this branch handle?" | Assume intent |
| Thank authors for good solutions | Review when tired or distracted |
