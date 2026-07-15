================================================================================
# 08 Dashboard Architecture
================================================================================

# Dashboard Architecture

## Purpose

The dashboard is the default landing page after repository import. It provides a personalized overview of system health, active alerts, recent insights, and quick actions — enabling users to understand the state of their software at a glance and navigate to deeper investigation.

---

## Scope

### In Scope

- Dashboard layout and section breakdown
- Health scorecard computation and display
- Active alerts panel
- Recent insights feed
- Quick actions
- Context header
- Dashboard customization (V2)
- Empty and error states

### Out of Scope

- Search and query UI (Phase 7/06)
- Evidence Explorer (Phase 7/07)
- Graph visualization components (Phase 7/05)

---

## Background

Phase 1 (Information Architecture) defined the Dashboard as the second major section after Search/Ask. Phase 1 (UI/UX Specification, Screen 3) detailed the Main Dashboard layout: Context Header, Search Bar, Alert Cards, Health Scorecard, Recent Insights, Quick Actions.

---

## Dashboard Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Context Header                                               │
│  Good morning, Alex · payment-system · Last analyzed: 10m ago │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Alert Cards (horizontal scroll)                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐               │
│  │ 🔴 HIGH    │ │ 🟡 MEDIUM │ │ 🔴 HIGH    │               │
│  │ Auth error │ │ Lodash CVE │ │ Bus factor │               │
│  │ rate 36.8% │ │ v4.17      │ │ Alice only │               │
│  └────────────┘ └────────────┘ └────────────┘               │
│                                                               │
│  ┌─────────────────────────┬─────────────────────────────────┐│
│  │  Health Scorecard       │  Recent Insights                ││
│  │                         │                                 ││
│  │  Overall: 72/100      │  ┌─ Auth module degrading · 10m ││
│  │  [▼ 5 pts this week]   │  ├─ Payment latency · 2h      ││
│  │                         │  └─ Notification coverage · 1d ││
│  │  Structure  ████████░░ 78│  [View All →]                 ││
│  │  Evolution  ██████░░░░ 62│                                 ││
│  │  Knowledge  ███████░░░ 70│  Quick Actions                 ││
│  │  Dependency █████████░ 88│  [Run Analysis] [New Report]  ││
│  │  Risk       █████░░░░░ 55│  [Ask Question]              ││
│  └─────────────────────────┴─────────────────────────────────┘│
│                                                               │
│  Insights Feed (expandable)                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 🔴 HIGH  Auth module error rate degradation             │ │
│  │          Roll back validate.ts to v2.1.3               │ │
│  │          Confidence: MEDIUM · 12 evidence items         │ │
│  │          [Acknowledge] [View] [Dismiss]                │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ 🟡 MEDIUM Lodash vulnerability CVE-2026-1234           │ │
│  │          Update to v4.18+ to patch                     │ │
│  │          Confidence: HIGH · 3 evidence items            │ │
│  │          [Acknowledge] [View] [Dismiss]                │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## Context Header

The header provides contextual awareness:

| Element | Source | Example |
|---|---|---|
| Greeting | Time-based | "Good morning, Alex" |
| Active repository | Workspace state | "payment-system" |
| Last analysis | `GET /v1/analysis/status` | "Last analyzed: 10m ago" |
| Server status | WebSocket connection | "Connected · llama3.1" |
| Insight count | `GET /v1/insights` | "12 active insights" |

---

## Alert Cards

Alert cards show the highest-severity active insights in a horizontally scrollable row.

### Card Design

```typescript
interface AlertCardProps {
    severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
    title: string
    summary: string
    entityName: string
    timestamp: string
    onView: () => void
    onDismiss: () => void
}
```

| Severity | Icon Color | Background | Border |
|---|---|---|---|
| CRITICAL | Red pulse | Red/50 | Red/500 |
| HIGH | Orange | Orange/50 | Orange/500 |
| MEDIUM | Yellow | Yellow/50 | Yellow/500 |
| LOW | Blue | Blue/50 | Blue/500 |

### Card Count

| State | Max Cards | Behavior |
|---|---|---|
| Default | 5 | Highest severity, most recent |
| Expanded | 10 | Click "Show all alerts" |
| None | 0 | Empty state: "No active alerts" |
| CRITICAL | Unlimited | CRITICAL alerts always shown |

---

## Health Scorecard

The health scorecard provides a composite view of system health across five dimensions.

### Score Computation

Each dimension is scored 0–100 by aggregating evidence from the corresponding engine:

| Dimension | Engine Source | Factors |
|---|---|---|
| Structure | structural_cognition | Cyclomatic complexity, file count, coupling |
| Evolution | evolution_cognition | Commit frequency, change size, refactoring ratio |
| Knowledge | knowledge_cognition | Bus factor, ownership concentration |
| Dependency | dependency_cognition | Outdated packages, vulnerability count |
| Risk | risk_cognition | Combined risk score from all engines |

### Overall Score

```
overall = weighted_average(structure, evolution, knowledge, dependency, risk)
Weights: [0.20, 0.20, 0.20, 0.20, 0.20] (configurable)
```

### Score Display

```
Overall: 72/100      [▼ 5 pts this week]

Structure  ████████░░ 78  +2
Evolution  ██████░░░░ 62  -8
Knowledge  ███████░░░ 70  +0
Dependency █████████░ 88  +1
Risk       █████░░░░░ 55  -12  ← needs attention
```

| Score Range | Color | Label |
|---|---|---|
| 80–100 | Green | Healthy |
| 60–79 | Yellow | Fair |
| 40–59 | Orange | At Risk |
| 0–39 | Red | Critical |

---

## Recent Insights

A compact list of the most recent insights across all entities.

| Property | Behavior |
|---|---|
| Count | 5 most recent (default), expandable to 20 |
| Sort | `-created_at` |
| Filter | Click severity badge to filter by level |
| Click | Navigate to `/insights/{id}` |
| Acknowledge | Inline acknowledge button (optimistic update) |

---

## Quick Actions

| Action | Endpoint | Navigation |
|---|---|---|
| Run Analysis | `POST /v1/analysis/run` | Opens progress modal |
| New Report | — | Navigates to `/reports/new` |
| Ask Question | — | Focuses search bar |
| Import Repository | — | Opens import dialog |
| View All Insights | `GET /v1/insights` | Navigates to `/insights` |

---

## Empty State (No Repositories)

When no repositories have been imported:

```
┌──────────────────────────────────────────────────────────────┐
│                                                               │
│                    Welcome to Project DNA                     │
│                                                               │
│     Understand your software. Completely.                     │
│                                                               │
│     [Import Repository]  [Open Sample Project]                │
│                                                               │
│     Project DNA analyzes your code to reveal structure,       │
│     risks, dependencies, and insights — all locally.          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Edge Cases

### No Insights Yet

When the repository is imported but no analysis has been run:

```
Alerts: No insights yet. Run an analysis to get started.
Health: Not yet scored.
Recent Insights: Run an analysis to generate insights.
[Run Analysis]
```

### All Alerts Acknowledged

When the user has acknowledged all insights, the alert row shows:

```
All caught up! No active alerts.
```

### Analysis In Progress

While analysis is running, the dashboard shows live progress:

```
Analysis in progress: 65% · 142 evidence items found
[View Progress]
```

Progress is updated via WebSocket events.
