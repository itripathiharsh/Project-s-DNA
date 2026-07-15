You are designing the permanent engineering execution loop for Project DNA.

Your task is NOT to write code.

Your task is to create:

prompts/02_LOOP.md

This file defines the complete execution loop followed by the AI engineer during every engineering session.

The goal is to make the engineering workflow deterministic, repeatable, and autonomous.

This document must define exactly how every engineering session begins, executes, validates work, updates project state, and ends.

--------------------------------------------------
Purpose
--------------------------------------------------

This is NOT a project plan.

This is NOT a coding guideline.

This is the operating loop executed every time the AI engineer receives instructions such as:

"Continue engineering"

"Start next sprint"

"Resume work"

"Continue implementation"

--------------------------------------------------
Overall Engineering Loop
--------------------------------------------------

The document must describe the complete lifecycle.

Example flow:

Start Session

↓

Read Engineering Control Files

↓

Read Current Sprint

↓

Read TODO

↓

Read Relevant Architecture Documents

↓

Inspect Existing Code

↓

Determine Next Task

↓

Generate Missing Implementation Specification (if required)

↓

Implement

↓

Generate Tests

↓

Run Validation

↓

Fix Failures

↓

Update TODO

↓

Update Decision Log

↓

Stop

This should be described in detail.

--------------------------------------------------
Session Startup
--------------------------------------------------

The AI must always begin by reading:

prompts/

roadmap/TODO.md

roadmap/SPRINTS.md

implementation/decisions/

implementation/specs/

Relevant docs/architecture/

Existing backend/

Existing frontend/

Existing tests/

Never begin implementation without understanding current project state.

--------------------------------------------------
Task Selection Rules
--------------------------------------------------

Describe how the AI selects work.

Highest priority:

Current TODO item

↓

Current Sprint

↓

Missing implementation specification

↓

Implementation

↓

Testing

↓

Documentation updates

Never skip unfinished work.

Never jump to another sprint.

Never start multiple sprints simultaneously.

--------------------------------------------------
Specification Generation
--------------------------------------------------

If implementation requires information that does not yet exist:

Generate ONLY the specification needed for the current sprint.

Never generate specifications for future sprints.

Store them under:

implementation/specs/

The specification becomes the implementation contract.

--------------------------------------------------
Implementation Rules
--------------------------------------------------

Implementation must always follow:

Architecture

↓

Implementation Spec

↓

Code

↓

Tests

Never reverse this order.

--------------------------------------------------
Validation Loop
--------------------------------------------------

Every completed implementation must go through:

Static review

↓

Compile

↓

Run tests

↓

Fix failures

↓

Repeat

The loop continues until the sprint satisfies completion rules.

--------------------------------------------------
Decision Recording
--------------------------------------------------

Whenever an architectural or engineering decision is made:

Record it in:

implementation/decisions/

Include:

Decision ID

Context

Decision

Reason

Alternatives

Impact

Date

Future engineers must understand why decisions were made.

--------------------------------------------------
Failure Handling
--------------------------------------------------

Describe behavior for:

Compilation failures

Test failures

Architecture conflicts

Missing specifications

Missing files

Unexpected project state

Infinite implementation loops

Repeated failures

The AI should retry intelligently.

If still blocked:

Stop.

Explain.

Never fabricate progress.

--------------------------------------------------
Progress Tracking
--------------------------------------------------

The AI must continuously update:

roadmap/TODO.md

when tasks begin,

when tasks finish,

when blocked,

and when a sprint completes.

--------------------------------------------------
Sprint Completion
--------------------------------------------------

Define exactly when a sprint is complete.

Examples:

Implementation specification exists.

Production code completed.

Tests pass.

No unresolved errors.

Documentation updated if required.

Decision log updated.

TODO updated.

Sprint marked complete.

Next sprint activated.

--------------------------------------------------
Session Shutdown
--------------------------------------------------

Before ending:

Summarize work.

List files changed.

List decisions made.

List remaining work.

Update roadmap.

Stop cleanly.

--------------------------------------------------
Engineering Principles
--------------------------------------------------

The loop must reinforce:

Small iterations

No skipped validation

No speculative coding

No duplicate implementations

No architecture drift

Evidence-first engineering

Continuous review

Deterministic execution

--------------------------------------------------
Output Requirements
--------------------------------------------------

Return ONLY the completed markdown file.

No explanations.

No additional commentary.

Produce a professional engineering operations manual suitable for running autonomous software development throughout the lifetime of Project DNA.

Target approximately 400–700 well-structured lines with clear sections, checklists, flow diagrams, decision tables, and operational procedures.