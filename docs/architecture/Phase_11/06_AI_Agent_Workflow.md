================================================================================
# 06 AI Agent Workflow
================================================================================

# AI Agent Workflow

## Purpose

Project DNA is itself developed with the assistance of AI agents. This document defines the workflow for an AI agent (like the one reading this) to execute development tasks effectively within the project structure.

---

## Workflow Steps

### 1. Read the Context

Before starting any task, the agent reads:

- `LOOP.md` — Current phase, document index, and instructions
- `docs/Phase_1/` through current phase — Architecture and design decisions
- Relevant source files (if any exist) — Current implementation state

### 2. Understand the Task

From the TODO.md, identify the current task. If the task is to write a document:

- Check the Phase index file (if applicable) for the document list
- Read adjacent documents for consistency
- Determine the document category (architecture, specification, guide)

### 3. Execute

- Write the document according to Documentation Standards (Phase 8/08)
- Use the Phase template: # Title, ## Purpose, then structured content
- Cross-reference existing documents where relevant
- Prefer tables, code blocks, and structured lists over prose

### 4. Validate

After writing, verify:

- TODO.md is updated
- Document references existing phases correctly
- No duplicate or contradictory definitions across phases
- Document has a clear Purpose section and self-contained content

### 5. Repeat

Return to step 1 for the next task. Never generate more than one markdown file per execution unless explicitly instructed.

## Agent Conventions

| Convention | Rule |
|---|---|
| File creation | Write one document per call |
| TODO updates | Update TODO.md after each document |
| Cross-references | Use `Phase X/Y — Title` format |
| Consistency | Check adjacent documents before writing |
| Self-correction | If a contradiction is found, flag it |
