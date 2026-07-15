You are creating the permanent implementation rules for Project DNA.

Your task is NOT to write production code.

Your task is to generate:

prompts/04_IMPLEMENTATION_RULES.md

This document defines the mandatory engineering rules that every implementation must follow throughout the lifetime of Project DNA.

It is the implementation contract between the architecture and the codebase.

This file is loaded before every coding session.

It must prevent inconsistent implementations, duplicate logic, architecture drift, and poor engineering practices.

--------------------------------------------------
Purpose
--------------------------------------------------

Define how production code is written.

This is NOT a coding style guide.

This is NOT language-specific.

This is NOT an architecture document.

It defines universal implementation rules.

--------------------------------------------------
Implementation Order
--------------------------------------------------

Every feature must follow this sequence.

1.
Read Architecture

↓

2.
Read Existing Implementation

↓

3.
Read Current Sprint

↓

4.
Read Implementation Specification

↓

5.
Implement

↓

6.
Write Tests

↓

7.
Validate

↓

8.
Update Documentation

↓

9.
Update TODO

Never change this order.

--------------------------------------------------
Engineering Rules
--------------------------------------------------

Define mandatory rules such as

Never invent architecture.

Never ignore architecture documents.

Never implement undocumented behaviour.

Never duplicate existing functionality.

Prefer extension over rewriting.

Keep modules small.

Single responsibility.

Explicit dependencies.

No hidden behaviour.

No global mutable state.

Pure business logic where possible.

Prefer composition over inheritance.

Never optimize prematurely.

--------------------------------------------------
Implementation Standards
--------------------------------------------------

Describe expectations for

Modularity

Maintainability

Readability

Observability

Configurability

Extensibility

Determinism

Error handling

Logging

Documentation

Consistency

--------------------------------------------------
Dependencies
--------------------------------------------------

Define dependency rules.

Every dependency must have a reason.

Avoid unnecessary libraries.

Prefer standard library.

Prefer existing project utilities.

Never introduce framework lock-in without justification.

--------------------------------------------------
Interfaces
--------------------------------------------------

Implementation must expose clear interfaces.

Stable contracts.

Versioned APIs.

Explicit inputs.

Explicit outputs.

Documented failures.

No hidden side effects.

--------------------------------------------------
Error Handling
--------------------------------------------------

Every implementation must define

Expected failures

Unexpected failures

Recovery behaviour

Retry policy

Logging strategy

User-visible errors

Developer-visible errors

Never swallow exceptions silently.

--------------------------------------------------
Configuration
--------------------------------------------------

Configuration must be

Centralized

Documented

Environment-independent

Typed

Validated

No hardcoded secrets.

No hardcoded paths.

--------------------------------------------------
Testing Requirements
--------------------------------------------------

Every implementation must include

Unit tests

Integration tests where appropriate

Edge cases

Failure cases

Performance checks if required

Regression tests

No implementation is complete without tests.

--------------------------------------------------
Documentation Rules
--------------------------------------------------

Every public component must explain

Purpose

Responsibilities

Inputs

Outputs

Dependencies

Limitations

Examples where useful

--------------------------------------------------
Performance Rules
--------------------------------------------------

Do not optimize blindly.

Measure first.

Profile first.

Optimize bottlenecks only.

Keep deterministic operations predictable.

Avoid unnecessary allocations.

Avoid unnecessary database access.

--------------------------------------------------
Security Rules
--------------------------------------------------

Input validation.

Output sanitization.

Least privilege.

Secure defaults.

No secrets in source.

Safe logging.

Safe error messages.

--------------------------------------------------
Maintainability
--------------------------------------------------

Future engineers should understand every implementation.

Code should be obvious.

Avoid clever code.

Prefer explicit behaviour.

Small reusable modules.

Minimal coupling.

--------------------------------------------------
Definition of Done
--------------------------------------------------

Implementation is complete only if

Architecture respected

Specification satisfied

Code written

Tests pass

Validation complete

Documentation updated

TODO updated

Decision log updated if needed

--------------------------------------------------
Output Requirements
--------------------------------------------------

Return ONLY the completed markdown document.

No explanations.

No commentary.

Write a production-quality engineering standard.

Target approximately 400–700 well-structured lines.

Use headings, tables, engineering checklists, implementation flow diagrams, and best practices.

This file should become the permanent implementation standard for the Project DNA repository.