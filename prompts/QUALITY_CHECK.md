You are creating the permanent quality assurance and self-review framework for Project DNA.

Your task is NOT to generate implementation.

Your task is to create:

prompts/06_QUALITY_CHECK.md

This document defines the mandatory quality validation process that the AI engineer must execute before considering any task complete.

The goal is to ensure every artifact produced during Project DNA implementation meets production engineering standards.

This file is loaded before every engineering session.

--------------------------------------------------
Purpose
--------------------------------------------------

This document defines HOW every engineering artifact is reviewed.

It is the final gate before work is considered complete.

Every implementation must pass these checks.

--------------------------------------------------
Review Philosophy
--------------------------------------------------

Quality is not optional.

Correctness is more important than speed.

Architecture compliance is more important than clever code.

Evidence is more important than assumptions.

Never approve work because it "looks right."

Every claim must be verifiable.

--------------------------------------------------
Review Pipeline
--------------------------------------------------

Every task must pass through this pipeline.

Implementation Complete

↓

Architecture Review

↓

Specification Review

↓

Code Review

↓

Testing Review

↓

Documentation Review

↓

Cross-Reference Validation

↓

Performance Review

↓

Security Review

↓

Final Acceptance

If any stage fails:

Return to implementation.

Repeat until all checks pass.

--------------------------------------------------
Architecture Validation
--------------------------------------------------

Verify:

Implementation follows architecture.

No architecture drift.

Correct module placement.

Correct dependencies.

No duplicated components.

No invented systems.

--------------------------------------------------
Specification Validation
--------------------------------------------------

Verify:

Specification fully implemented.

Nothing missing.

Nothing extra.

Acceptance criteria satisfied.

Inputs match specification.

Outputs match specification.

--------------------------------------------------
Code Review
--------------------------------------------------

Verify:

Readable.

Maintainable.

Modular.

Deterministic.

No dead code.

No duplicated logic.

Clear naming.

Minimal complexity.

Proper error handling.

--------------------------------------------------
Testing Validation
--------------------------------------------------

Verify:

Unit tests exist.

Integration tests exist where required.

Failure cases covered.

Edge cases covered.

Regression tests updated.

All tests pass.

--------------------------------------------------
Documentation Validation
--------------------------------------------------

Verify:

Documentation updated.

Examples correct.

No stale references.

Cross-links valid.

Terminology consistent.

--------------------------------------------------
Cross-Reference Validation
--------------------------------------------------

Verify:

Referenced files exist.

Referenced APIs exist.

Referenced schemas exist.

Referenced decisions exist.

Referenced modules exist.

No broken documentation links.

--------------------------------------------------
Performance Review
--------------------------------------------------

Verify:

No obvious bottlenecks.

No unnecessary allocations.

No repeated expensive operations.

No redundant database work.

Performance matches specification.

--------------------------------------------------
Security Review
--------------------------------------------------

Verify:

Input validation.

Output sanitization.

Secrets protected.

Safe logging.

Proper authentication checks.

Least privilege respected.

--------------------------------------------------
Consistency Review
--------------------------------------------------

Verify:

Terminology consistent.

Naming conventions followed.

Folder structure respected.

Implementation matches existing project patterns.

No conflicting approaches introduced.

--------------------------------------------------
Definition of Done
--------------------------------------------------

A task is complete only if:

Architecture validated.

Specification satisfied.

Code reviewed.

Tests passing.

Documentation updated.

Quality checklist passed.

TODO updated.

Decision log updated if required.

--------------------------------------------------
Failure Handling
--------------------------------------------------

If validation fails:

Clearly identify every issue.

Categorize by severity:

Critical

Major

Minor

Provide exact remediation steps.

Never silently ignore failures.

Never approve partially complete work.

--------------------------------------------------
Review Report
--------------------------------------------------

Every completed review should produce a summary containing:

Scope reviewed.

Files reviewed.

Checks performed.

Issues found.

Issues fixed.

Remaining risks.

Final verdict.

Confidence score.

--------------------------------------------------
Output Requirements
--------------------------------------------------

Return ONLY the completed markdown document.

No explanations.

No commentary.

Write a production-grade engineering quality manual.

Target approximately 300–600 well-structured lines.

Use tables, validation matrices, review checklists, severity classifications, flow diagrams, and acceptance gates.

This document should become the permanent quality assurance framework for Project DNA.