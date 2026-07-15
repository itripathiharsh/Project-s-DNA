You are creating the permanent Sprint Specification Template for Project DNA.

Your task is NOT to write implementation.

Your task is to generate:

prompts/10_SPRINT_TEMPLATE.md

This document defines the standard template that will be used for EVERY engineering sprint in Project DNA.

Every implementation sprint, regardless of feature, must follow this structure.

This template becomes the implementation contract between architecture and production code.

--------------------------------------------------
Purpose
--------------------------------------------------

The objective of a sprint specification is to describe ONE implementation unit completely enough that an AI engineer or human engineer can build it without ambiguity.

A sprint specification is implementation-focused.

It translates architecture into executable engineering work.

--------------------------------------------------
Scope
--------------------------------------------------

This template applies to every implementation sprint including:

Backend Services

Frontend Features

Database Schemas

API Development

Reasoning Engine

SCM Components

Infrastructure

CI/CD

Deployment

Testing

Monitoring

Security

Developer Tooling

--------------------------------------------------
Sprint Header
--------------------------------------------------

Every sprint must begin with:

Sprint Number

Sprint Name

Phase

Priority

Estimated Effort

Dependencies

Owner

Status

Version

Created Date

Last Updated

--------------------------------------------------
Sprint Goal
--------------------------------------------------

Clearly explain:

Why this sprint exists.

What business value it delivers.

What engineering problem it solves.

What will exist after completion.

--------------------------------------------------
Objectives
--------------------------------------------------

List measurable objectives.

Each objective must be independently verifiable.

--------------------------------------------------
Out of Scope
--------------------------------------------------

Clearly define what this sprint will NOT implement.

Avoid scope creep.

--------------------------------------------------
Architecture References
--------------------------------------------------

Reference all related architecture documents.

List:

Document

Section

Reason for dependency

Never duplicate architecture.

--------------------------------------------------
Prerequisites
--------------------------------------------------

List everything required before implementation begins.

Examples:

Completed Sprint IDs

Required APIs

Required Database Tables

Required Schemas

Required Decisions

Required Infrastructure

--------------------------------------------------
Requirements
--------------------------------------------------

Functional Requirements

Non-functional Requirements

Performance

Security

Reliability

Observability

Accessibility (when applicable)

--------------------------------------------------
Implementation Plan
--------------------------------------------------

Break implementation into logical tasks.

Each task should include:

Task ID

Description

Inputs

Outputs

Dependencies

Estimated Complexity

Acceptance Criteria

--------------------------------------------------
File Changes
--------------------------------------------------

For every sprint specify:

Files Created

Files Modified

Files Removed (if any)

Folder Locations

Purpose of each file

--------------------------------------------------
Interfaces
--------------------------------------------------

Describe all interfaces.

Public APIs

Internal APIs

Function Contracts

Component Contracts

Database Interfaces

Event Interfaces

--------------------------------------------------
Data Models
--------------------------------------------------

Define:

Entities

Schemas

Relationships

Validation Rules

Constraints

Indexes

Migration Strategy

--------------------------------------------------
Algorithms
--------------------------------------------------

When required describe:

Inputs

Outputs

Pseudo-code

Complexity

Edge Cases

Failure Behaviour

--------------------------------------------------
Error Handling
--------------------------------------------------

Expected Errors

Unexpected Errors

Retries

Recovery

Logging

Monitoring

--------------------------------------------------
Testing Plan
--------------------------------------------------

Unit Tests

Integration Tests

Performance Tests

Security Tests

Regression Tests

Test Data

Acceptance Tests

--------------------------------------------------
Validation Checklist
--------------------------------------------------

The sprint is complete only if:

Architecture followed

Requirements satisfied

Implementation finished

Tests passing

Documentation updated

Decision Records updated

Quality checks passed

--------------------------------------------------
Risks
--------------------------------------------------

Identify:

Technical Risks

Dependency Risks

Performance Risks

Security Risks

Mitigation Plans

--------------------------------------------------
Deliverables
--------------------------------------------------

List every artifact expected after sprint completion.

Examples:

Source Code

Tests

Specifications

Documentation

Configurations

Migration Files

Decision Records

--------------------------------------------------
Definition of Done
--------------------------------------------------

Clearly define objective completion criteria.

No ambiguity.

--------------------------------------------------
Future Sprints
--------------------------------------------------

Explain:

What this sprint enables.

Which future sprints depend on it.

Known follow-up work.

--------------------------------------------------
Sprint Review Template
--------------------------------------------------

End the document with a reusable review section.

Include:

Objectives Achieved

Files Changed

Tests Executed

Known Issues

Technical Debt

Lessons Learned

Recommendations

Approval Status

--------------------------------------------------
Formatting Standards
--------------------------------------------------

Use:

Markdown headings

Tables

Task checklists

Mermaid diagrams where useful

Callout blocks

Examples

Consistent formatting

--------------------------------------------------
Output Requirements
--------------------------------------------------

Return ONLY the completed markdown document.

No explanations.

No commentary.

Produce a production-grade engineering sprint template.

Target approximately 400–700 well-structured lines.

The resulting template should be reusable for every implementation sprint across the lifetime of Project DNA and should be detailed enough that an autonomous AI engineer can generate implementation-ready sprint specifications from it.