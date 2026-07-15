You are creating the permanent Engineering Decision Record (EDR) template for Project DNA.

Your task is NOT to write implementation.

Your task is to generate:

prompts/08_DECISION_TEMPLATE.md

This document defines the standard template for recording every important engineering decision made during the implementation of Project DNA.

It must become the single format used whenever architecture, implementation, technology, algorithms, APIs, schemas, deployment strategies, or engineering processes change.

The purpose is to preserve engineering knowledge and explain WHY decisions were made.

--------------------------------------------------
Purpose
--------------------------------------------------

Every significant engineering decision must be documented.

Future engineers should understand:

What changed

Why it changed

What alternatives were considered

What trade-offs were accepted

What future impact is expected

Never lose engineering context.

--------------------------------------------------
When To Create A Decision Record
--------------------------------------------------

Examples include:

Architecture changes

Technology selection

Database schema changes

API contract changes

Algorithm changes

Security decisions

Performance optimizations

Infrastructure decisions

Deployment strategy changes

Breaking changes

Dependency additions/removals

Coding standard changes

--------------------------------------------------
Decision Record Structure
--------------------------------------------------

Every decision record must contain:

Decision ID

Title

Status

Date

Author

Sprint

Phase

Related Issue

Related Specification

Related Architecture Document

Summary

--------------------------------------------------
Problem Statement
--------------------------------------------------

Clearly describe:

Current problem

Context

Constraints

Business impact

Technical impact

Why the decision is required

--------------------------------------------------
Decision
--------------------------------------------------

Describe exactly what was decided.

Be explicit.

Avoid ambiguity.

Explain implementation boundaries.

--------------------------------------------------
Alternatives Considered
--------------------------------------------------

For every decision document:

List all realistic alternatives.

Describe:

Advantages

Disadvantages

Complexity

Risk

Reason for rejection

--------------------------------------------------
Trade-Off Analysis
--------------------------------------------------

Discuss:

Performance

Maintainability

Scalability

Security

Complexity

Developer Experience

Operational Cost

Future Flexibility

--------------------------------------------------
Consequences
--------------------------------------------------

Explain:

Positive outcomes

Negative outcomes

Known limitations

Future work created

Migration impact

Compatibility impact

--------------------------------------------------
Implementation Notes
--------------------------------------------------

Reference:

Implementation Specs

Affected Modules

Affected APIs

Affected Tests

Affected Documentation

Affected Configurations

--------------------------------------------------
Validation
--------------------------------------------------

Describe how the decision will be validated.

Examples:

Tests

Benchmarks

Reviews

Monitoring

Performance Metrics

User Validation

--------------------------------------------------
Rollback Plan
--------------------------------------------------

Every major decision should explain:

Can it be reverted?

How?

What risks exist?

Migration requirements

--------------------------------------------------
References
--------------------------------------------------

Link to:

Architecture Documents

Implementation Specifications

API Specifications

GitHub Issues

Pull Requests

Previous Decisions

External Standards (if applicable)

--------------------------------------------------
Decision Lifecycle
--------------------------------------------------

Every decision must include a status.

Examples:

Proposed

Accepted

Implemented

Validated

Deprecated

Superseded

Rejected

Archived

--------------------------------------------------
Naming Convention
--------------------------------------------------

Define filename format.

Example:

EDR-0001-SCM-Writer-Protocol.md

EDR-0002-Reasoning-Pipeline.md

EDR-0003-Evidence-Confidence.md

--------------------------------------------------
Quality Checklist
--------------------------------------------------

Before accepting a decision verify:

Problem understood

Alternatives evaluated

Trade-offs explained

References linked

Implementation identified

Validation planned

Rollback documented

--------------------------------------------------
Example Decision Record
--------------------------------------------------

Provide a fully worked example using a realistic Project DNA engineering decision.

Example:

Choosing Tree-sitter as the universal parser.

OR

Choosing SQLite for V1 SCM storage.

--------------------------------------------------
Output Requirements
--------------------------------------------------

Return ONLY the completed markdown document.

No explanations.

No commentary.

Produce a production-grade engineering decision template.

Target approximately 250–450 well-structured lines.

Use headings, tables, checklists, lifecycle diagrams, examples, and reusable markdown templates.

This file should become the permanent engineering decision standard for Project DNA.