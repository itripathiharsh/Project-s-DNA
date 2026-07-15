You are creating the permanent Project Context document for Project DNA.

Your task is NOT to write code.

Your task is to generate

prompts/03_PROJECT_CONTEXT.md

This document is loaded before every engineering session.

Its purpose is to give every AI model a complete understanding of Project DNA without reading hundreds of architecture documents first.

This is NOT an architecture document.

This is a concise engineering context file.

It must summarize the entire project in one place while treating the architecture documents as the ultimate source of truth.

--------------------------------------------------
Purpose
--------------------------------------------------

The AI engineer must understand:

• What Project DNA is
• Why it exists
• What problem it solves
• The engineering philosophy
• Current implementation status
• Overall architecture
• Technology stack
• Repository structure
• Development roadmap

without reading every phase document.

--------------------------------------------------
Project Overview
--------------------------------------------------

Describe Project DNA as

A Local-first AI Software Cognition Platform.

Explain Software Cognition.

Explain why the project exists.

Explain what differentiates it from GitHub, SonarQube, CodeQL, static analysis tools and code assistants.

Keep this concise.

--------------------------------------------------
Current Status
--------------------------------------------------

Architecture Documentation

Completed

Critical audits resolved

Architecture frozen

Implementation starting

Current development stage

Engineering Sprint implementation

--------------------------------------------------
Project Principles
--------------------------------------------------

Summarize only.

Do not copy architecture documents.

Include ideas such as

Evidence First

Deterministic Before Probabilistic

Local First

Explainability

Privacy

No hallucinated insights

Architecture is law

--------------------------------------------------
Architecture Summary
--------------------------------------------------

Summarize the major layers.

Repository Input

↓

Repository Processing

↓

Software Cognition Model

↓

Cognitive Engines

↓

Reasoning Layer

↓

API

↓

Frontend

Do not explain implementation details.

--------------------------------------------------
Major Components
--------------------------------------------------

Summarize every major subsystem.

Repository Scanner

Git Analyzer

Tree-sitter Parser

Dependency Analysis

Entity Extraction

SCM

Evidence Store

Graph Engine

Structural Engine

Evolution Engine

Knowledge Engine

Risk Engine

Decision Engine

Prediction Engine

Reasoning Pipeline

REST API

WebSocket

Frontend

Authentication

Testing

Deployment

Only describe responsibilities.

--------------------------------------------------
Technology Stack
--------------------------------------------------

Summarize the approved technologies.

Python

FastAPI

SQLite

Tree-sitter

Ollama

React

TypeScript

Cytoscape

Docker

Pytest

etc.

Only approved technologies.

--------------------------------------------------
Repository Structure
--------------------------------------------------

Summarize the repository layout.

docs/

implementation/

backend/

frontend/

tests/

roadmap/

prompts/

configs/

scripts/

docker/

Briefly explain the responsibility of each directory.

--------------------------------------------------
Engineering Roadmap
--------------------------------------------------

Summarize engineering sprints.

Do NOT repeat detailed sprint planning.

Simply explain that development proceeds sprint-by-sprint using SPRINTS.md and TODO.md.

--------------------------------------------------
Source of Truth
--------------------------------------------------

Clearly define document priority.

Architecture Documents

↓

Implementation Specs

↓

Engineering Decisions

↓

Existing Code

↓

Tests

↓

Roadmap

↓

Model Reasoning

Never allow assumptions to override documented architecture.

--------------------------------------------------
Working Rules
--------------------------------------------------

The AI should always

Read before changing

Understand before implementing

Prefer reuse

Respect previous decisions

Implement incrementally

Validate continuously

--------------------------------------------------
Out of Scope
--------------------------------------------------

Clearly state what this document is NOT.

Not architecture

Not implementation

Not API documentation

Not coding standards

Not sprint planning

It is only project context.

--------------------------------------------------
Output Requirements
--------------------------------------------------

Return ONLY the completed markdown file.

No explanations.

No additional commentary.

Write a professional engineering reference document.

Target 250–500 well-structured lines.

Use tables, summaries, diagrams, and concise engineering language.