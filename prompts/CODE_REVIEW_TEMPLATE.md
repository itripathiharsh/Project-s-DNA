You are creating the permanent Code Review Standard for Project DNA.

Your task is NOT to write implementation.

Your task is to generate:

prompts/09_CODE_REVIEW_TEMPLATE.md

This document defines the standard process for reviewing every code change made during the implementation of Project DNA.

It must become the mandatory review framework used before any implementation is considered complete.

The objective is to ensure every change is technically correct, architecturally compliant, maintainable, secure, performant, and production-ready.

--------------------------------------------------
Purpose
--------------------------------------------------

This document defines HOW code is reviewed.

It is not a coding guideline.

It is not an implementation guide.

It is the final engineering review before accepting any change.

--------------------------------------------------
Review Philosophy
--------------------------------------------------

Every review should answer:

Is the implementation correct?

Does it follow architecture?

Does it satisfy the specification?

Is it maintainable?

Is it testable?

Is it secure?

Can another engineer understand it?

Would this survive production?

--------------------------------------------------
Review Workflow
--------------------------------------------------

Describe the complete review lifecycle.

Implementation Completed

↓

Read Related Architecture Documents

↓

Read Implementation Specification

↓

Review Changed Files

↓

Verify Tests

↓

Check Documentation

↓

Validate Dependencies

↓

Review Security

↓

Review Performance

↓

Approve or Request Changes

Every stage must be described.

--------------------------------------------------
Architecture Review
--------------------------------------------------

Verify:

Architecture documents followed

Correct module boundaries

Correct dependencies

No architecture drift

No duplicate functionality

Correct layer placement

--------------------------------------------------
Specification Review
--------------------------------------------------

Verify:

Feature matches specification

Acceptance criteria satisfied

Nothing missing

Nothing extra

Interfaces respected

Data flow matches specification

--------------------------------------------------
Code Quality Review
--------------------------------------------------

Check:

Readability

Maintainability

Naming

Modularity

Complexity

Coupling

Cohesion

Reusability

Code duplication

Dead code

Magic values

Comments

Documentation

--------------------------------------------------
Error Handling Review
--------------------------------------------------

Verify:

Exceptions handled

Errors propagated correctly

Recovery strategy

Logging

Meaningful messages

No silent failures

--------------------------------------------------
Testing Review
--------------------------------------------------

Verify:

Unit tests

Integration tests

Edge cases

Failure cases

Regression tests

Coverage

Test quality

Deterministic behaviour

--------------------------------------------------
Security Review
--------------------------------------------------

Review:

Authentication

Authorization

Input validation

Output sanitization

Secrets

Logging safety

Injection risks

Dependency risks

--------------------------------------------------
Performance Review
--------------------------------------------------

Check:

Algorithms

Memory usage

Database access

Caching

Repeated work

Concurrency

Latency

Scalability

--------------------------------------------------
Documentation Review
--------------------------------------------------

Verify:

Public APIs documented

Specifications updated

Examples correct

Cross references valid

Decision records updated if required

--------------------------------------------------
Review Severity
--------------------------------------------------

Define categories.

Critical

Major

Minor

Suggestion

For each severity define:

Meaning

Impact

Must Fix?

Blocks Merge?

--------------------------------------------------
Approval Rules
--------------------------------------------------

A change may be approved only if:

Architecture respected

Specification complete

Tests pass

Documentation updated

No Critical issues

No unresolved Major issues

--------------------------------------------------
Review Report Template
--------------------------------------------------

Every review should produce:

Summary

Files Reviewed

Architecture Compliance

Specification Compliance

Strengths

Issues

Recommendations

Approval Status

Reviewer Notes

Confidence Score

--------------------------------------------------
Example Review
--------------------------------------------------

Provide a realistic review example using a Project DNA feature.

Example:

Repository Scanner

Reasoning Pipeline

REST Endpoint

SCM Query Engine

--------------------------------------------------
Quality Checklist
--------------------------------------------------

The reviewer must verify:

✓ Correct

✓ Complete

✓ Tested

✓ Secure

✓ Performant

✓ Maintainable

✓ Documented

✓ Consistent

✓ Production Ready

--------------------------------------------------
Output Requirements
--------------------------------------------------

Return ONLY the completed markdown document.

No explanations.

No commentary.

Produce a production-grade engineering code review standard.

Target approximately 250–450 well-structured lines.

Use tables, review matrices, severity definitions, checklists, approval gates, and reusable review templates.

This document should become the permanent code review framework for Project DNA.