================================================================================
# 04 Task Breakdown
================================================================================

# Task Breakdown

## Purpose

Tasks are the smallest unit of work — a single PR-sized chunk that can be completed by one developer (human or AI) in 1–3 days. This document defines the task structure and provides examples for each epic.

---

## Task Template

Each task must specify:

| Field | Description |
|---|---|
| **ID** | `T-NNN` |
| **Title** | Short action-oriented description |
| **Epic** | Parent epic ID |
| **Effort** | 1–3 days |
| **Dependencies** | Task IDs that must be done first |
| **Acceptance Criteria** | Measurable completion conditions |
| **Files** | Likely files to create/modify |

## Example: E-01 Core SCM

| ID | Title | Effort | Dependencies |
|---|---|---|---|
| T-001 | Define SCM data model (CodeEntity, Relationship, Evidence) | 2d | None |
| T-002 | Implement repository scanner (file tree parser) | 2d | T-001 |
| T-003 | Implement dependency graph builder | 3d | T-001 |
| T-004 | Implement identifier resolver (import/require scanning) | 3d | T-001 |
| T-005 | Implement SCM query interface (by path, type, relationship) | 2d | T-002, T-003, T-004 |
| T-006 | Write SCM unit tests | 1d | T-005 |

## Example: E-09 Reasoning Pipeline

| ID | Title | Effort | Dependencies |
|---|---|---|---|
| T-030 | Design reasoning pipeline stages | 1d | E-06, E-07, E-08 |
| T-031 | Implement simple_qa reasoning stage | 2d | T-030 |
| T-032 | Implement synthesis reasoning stage | 3d | T-030 |
| T-033 | Implement decision_support reasoning stage | 3d | T-030 |
| T-034 | Implement chain-of-thought prompt builder | 2d | E-07 |
| T-035 | Write reasoning integration tests | 2d | T-031, T-032, T-033 |

## Task ID Registry

| Range | Epic |
|---|---|
| T-001 to T-020 | E-01 Core SCM |
| T-021 to T-030 | E-02/E-03/E-04/E-05 |
| T-031 to T-050 | E-06 through E-09 |
| T-051 to T-070 | E-10 through E-14 |
| T-071 to T-090 | E-15 through E-19 |
