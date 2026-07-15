================================================================================
# 07 Evidence Explorer
================================================================================

# Evidence Explorer

## Purpose

The Evidence Explorer is the dedicated interface for browsing, filtering, and inspecting evidence nodes produced by the Cognitive Engines. It surfaces the raw perceptual data of Project DNA — the facts from which all insights are derived. Users filter by engine, entity, severity, and time range; drill into individual evidence detail; and navigate from evidence to the insights it supports.

---

## Scope

### In Scope

- Evidence list view with filtering and sorting
- Evidence detail view with raw data access
- Cross-linking between evidence and insights
- Evidence comparison side-by-side
- Filter persistence and sharing

### Out of Scope

- Evidence chain visualization (Phase 7/05)
- Insight display (Phase 7/06)
- Dashboard integration (Phase 7/08)

---

## Background

Phase 3 defined the EvidenceNode structure (id, type, category, value, confidence, source, raw_data_ref, affected_entities). Phase 4 defined how Cognitive Engines produce evidence. Phase 6 defined the REST endpoints for evidence retrieval. This document defines the UI that presents that evidence.

---

## Evidence List View

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Evidence Explorer                                           │
│                                                               │
│  Filters Bar                                                 │
│  [Entity ▼] [Engine ▼] [Severity ▼] [Type ▼] [Time ▼] [Q]  │
│                                                               │
│  Active Filters: [engine: trace_cognition ✕]                 │
│                  [severity: high, critical ✕]                │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ◉ trace_001 · FUNCTION_CALL                             │ │
│  │   validateToken: 312 errors (36.8%) · LOW · 10 min ago │ │
│  │   trace_cognition · mod_auth_001                        │ │
│  │   [View] [Linked Insights: 2]                           │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ ◉ trace_002 · EXCEPTION                                 │ │
│  │   TypeError at validate.ts:88 · HIGH · 10 min ago      │ │
│  │   trace_cognition · mod_auth_001, func_validatetoken   │ │
│  │   [View] [Linked Insights: 2]                           │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ ... more items                                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  [← Prev] Page 1 of 16 [Next →]                              │
└──────────────────────────────────────────────────────────────┘
```

### Filter Controls

| Filter | Control Type | Options |
|---|---|---|
| Entity | Autocomplete combo | All entities (searchable) |
| Engine | Multi-select dropdown | structural, evolution, knowledge, dependency, risk, etc. |
| Severity | Button group | ALL, LOW, MEDIUM, HIGH, CRITICAL |
| Type | Multi-select dropdown | Evidence type taxonomy |
| Time range | Date range picker | Presets: 1h, 24h, 7d, 30d, Custom |
| Search | Text input | Full-text search across evidence values |

### Sort Options

| Option | Default Direction |
|---|---|
| Recency (newest first) | Default |
| Severity (highest first) | Toggle |
| Confidence (highest first) | Toggle |
| Engine (alphabetical) | Toggle |

---

## Evidence Detail View

Clicking an evidence row opens the detail panel (slide-over or full page):

```
┌────────────────────────────────────────────────────────────┐
│  Evidence Detail                                    [Close] │
├────────────────────────────────────────────────────────────┤
│  ID: trace_001                                             │
│  Type: FUNCTION_CALL                                       │
│  Engine: trace_cognition v1.3.0                            │
│  Severity: LOW                                             │
│  Confidence: 0.95                                          │
│  Timestamp: 2026-07-14T10:23:00Z                           │
│                                                             │
│  Value                                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ validateToken() called 847 times, 312 returning      │  │
│  │ errors (36.8%)                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Source                                                     │
│  File: src/auth/validate.ts                                │
│  Line: 42                                                   │
│                                                             │
│  Affected Entities                                          │
│  ┌─ func_auth_validatetoken_001 — validateToken (function) │
│  └─ mod_auth_001 — src/auth (module)                      │
│                                                             │
│  Raw Data Reference                                         │
│  File: logs/auth_20260714.json                              │
│  Content hash: abc123def456                                │
│  [View Raw Data]                                            │
│                                                             │
│  Linked Insights                                            │
│  ┌─ Auth module error rate degradation · HIGH              │
│  │  "Directly supports: error rate data shows degradation" │
│  │  [View Insight]                                         │
│  └─ Auth module risk assessment · MEDIUM                   │
│                                                             │
│  [View Evidence Chain Graph] [Export Evidence]             │
└────────────────────────────────────────────────────────────┘
```

### Raw Data View

When the user clicks "View Raw Data", the raw data panel opens within the detail view:

```
┌────────────────────────────────────────────────────────────┐
│  Raw Data: logs/auth_20260714.json                  [Close] │
├────────────────────────────────────────────────────────────┤
│  Lines 847-850                                             │
│                                                             │
│  847  2026-07-14 10:23:00 [TRACE] validateToken called     │
│  848  from authenticate() caller_id=req_847                │
│  849  2026-07-14 10:23:00 [ERROR] TypeError: Cannot read   │
│  850  property 'config' of undefined at validate.ts:88     │
└────────────────────────────────────────────────────────────┘
```

---

## Evidence Comparison

Users can select two or more evidence items and view them side-by-side:

```
┌──────────────────────┬──────────────────────────────────────┐
│  trace_001           │  metric_003                           │
├──────────────────────┼──────────────────────────────────────┤
│  FUNCTION_CALL       │  COUNTER                              │
│  trace_cognition     │  metric_cognition                     │
│  0.95                │  0.85                                 │
│                      │                                       │
│  36.8% error rate    │  avg 0.368, trend increasing          │
│                      │                                       │
│  resolved: CONFLICT  │  resolved: CONFLICT                   │
│  36.8% ↔ 42.1%      │  36.8% ↔ 42.1%                        │
└──────────────────────┴──────────────────────────────────────┘
```

The comparison view highlights differences (conflicting values, different engines, different timestamps) with color-coded indicators.

---

## Cross-Linking

Every evidence detail view links to:

| Link | Destination | Action |
|---|---|---|
| Affected entities | Entity detail page | `navigate(/repo/{entity_id})` |
| Linked insights | Insight detail page | `navigate(/insights/{insight_id})` |
| Raw data | Raw data panel | Opens in-slide panel |
| Evidence chain graph | Visualization | Opens evidence chain graph |

---

## Edge Cases

### No Evidence Found

When filters return zero results:

```
No evidence matches your filters.
[Clear Filters] [Run Analysis]
```

### Evidence with Conflicting Values

Conflicting evidence (same metric, different values from different engines) is tagged with a conflict badge. The list view shows a `⚡ Conflict` indicator on the affected row.

### Very Large Evidence Values

Evidence values containing large JSON blobs or code snippets are truncated at 500 characters in the list view. The detail view shows the full value with syntax highlighting and scroll.

### Stale Evidence

Evidence older than the configured staleness threshold (default: 30 days) is visually dimmed and tagged with a `[Stale]` badge in both list and detail views.
