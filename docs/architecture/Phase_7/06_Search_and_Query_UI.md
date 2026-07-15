================================================================================
# 06 Search and Query UI
================================================================================

# Search and Query UI

## Purpose

The search bar is the primary entry point for user interaction with Project DNA. Users type questions, get answers, and explore results. This document defines the search UI architecture — autocomplete, question submission, answer streaming, result exploration, and the transition from search to deep investigation.

---

## Scope

### In Scope

- Search bar component and autocomplete
- Question submission flow (REST + WebSocket)
- Answer view with token streaming
- Search result exploration (entities, evidence, insights)
- Transition from answer to detailed investigation
- Search history and saved queries
- Empty, loading, and error states

### Out of Scope

- Graph visualization within search results (Phase 7/05)
- Evidence Explorer full page (Phase 7/07)
- Dashboard search integration (Phase 7/08)

---

## Background

Phase 1 (Information Architecture) defined Search/Ask as the universal entry point — the primary interface where users ask questions and receive answers. Phase 1 (UI/UX Specification, Screen 4) detailed the Search Results / Answer View.

Phase 6 defined the REST endpoint `POST /v1/reason/question` and the WebSocket streaming protocol for real-time token delivery.

---

## Flow

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  User    │   │  Search  │   │  Answer  │   │  Explore │
│  types   │──▶│  Bar +   │──▶│  View    │──▶│  Results │
│  query   │   │  Suggest │   │  Stream  │   │  Detail  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

---

## Search Bar

### Location and Behavior

The search bar appears in two contexts:

| Context | Location | Behavior |
|---|---|---|
| **Global** | Header (always visible) | Searches across all entities, navigates to `/search?q=...` |
| **Contextual** | Repository detail page | Scoped to the active repository |

### Autocomplete

As the user types, the search bar shows an autocomplete dropdown with:

```
┌──────────────────────────────────────────────┐
│  [🔍] What is causing the auth               │
├──────────────────────────────────────────────┤
│  Entities                                     │
│  ┌─ src/auth (module)                        │
│  ├─ validateToken (function)                 │
│  ├─ AuthProvider (class)                     │
│  └─ Alice (author)                          │
│                                               │
│  Previous Questions                           │
│  ┌─ "What is the error rate of auth?"       │
│  └─ "Who owns the auth module?"            │
│                                               │
│  Suggestions                                  │
│  └─ "What is causing the auth failures?"    │
└──────────────────────────────────────────────┘
```

| Section | Source | Max Items |
|---|---|---|
| Entities | `GET /v1/entities?q=auth` | 5 |
| Previous questions | Local storage | 5 |
| Suggestions | `POST /v1/reason/suggest` | 3 |

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `/` | Focus search bar (from anywhere) |
| `Escape` | Clear search / close dropdown |
| `↑` `↓` | Navigate autocomplete items |
| `Enter` | Submit query / select autocomplete item |
| `Tab` | Select entity filter and continue typing |

---

## Answer View

### Layout

```
┌──────────────────────────────────────────────────────────┐
│  Question: "What is causing the authentication failures?" │
│  [Ask again] [Share] [Save]                              │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Summary (streamed tokens)                           │ │
│  │  Authentication failures are caused by a recent      │ │
│  │  deployment to src/auth/validate.ts that...          │ │
│  │  └─ Confidence: MEDIUM (0.71) · 12 evidence items   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  Key Findings                                             │
│  • Error rate spike from 5% to 36.8% correlates with      │
│    deployment at 07:00 UTC                                │
│  • All 312 errors trace to validate.ts:88                 │
│                                                           │
│  Evidence Overview                                        │
│  Trace: 36.8% error rate (trace_cognition)                │
│  Exception: TypeError at validate.ts:88 (trace_cognition) │
│  Metric: error rate avg 0.368 (metric_cognition)          │
│  [View all 12 evidence items →]                           │
│                                                           │
│  Recommendations                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Roll back src/auth/validate.ts to version 2.1.3     │ │
│  │ 30 minutes · LOW risk · Confidence: 0.85            │ │
│  │ [Dismiss] [Acknowledge]                             │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  [View Full Insight] [View Evidence Chain] [Export]      │
└──────────────────────────────────────────────────────────┘
```

### Streaming Token Display

Tokens are displayed character-by-character as they arrive via WebSocket. The component uses a blinking cursor animation during active streaming:

```
Authentication failures are caused by a recent deployment▌
```

| State | Behavior |
|---|---|
| Streaming | Blinking cursor, tokens append in real time |
| Complete | Cursor removed, "Generated in 3.4s" shown |
| Error | Partial text shown with error banner |
| Cancelled | "Cancelled. Partial results shown." |

### Follow-Up Questions

After an answer is displayed, the search bar shows: "Ask a follow-up..." which sends the follow-up with the previous context:

```
Follow-up: "How do we fix it?"
→ Sends: { question: "How do we fix it?", context: { previous_insight_id: "insight_synth_001" } }
```

---

## Search Results Page

When the user submits a query without waiting for streaming, or navigates to `/search?q=...`:

```
┌────────────────────────────────────────────────────────────┐
│  Results for "auth"                                         │
│  [All] [Entities] [Evidence] [Insights]                    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Answer (if available)                                     │
│  ┌─ "What is causing the authentication failures?"       │
│  │  Confidence: MEDIUM · 12 evidence items                │
│  └─ [View Full Answer]                                    │
│                                                            │
│  Entities (12 results)                                     │
│  ┌─ src/auth (module) · 47 evidence · 12 insights        │
│  ├─ validateToken (function) · Insights available         │
│  ├─ AuthProvider (class) · Needs analysis                 │
│  └─ [Show all 12 →]                                       │
│                                                            │
│  Insights (5 results)                                      │
│  ┌─ Auth module error rate degradation · HIGH             │
│  │  New insight · 10 minutes ago                          │
│  └─ [View]                                                 │
│                                                            │
│  Evidence (24 results)                                     │
│  ┌─ validateToken: 312 errors (36.8%) · LOW              │
│  │  trace_cognition · 10 minutes ago                      │
│  └─ [View]                                                 │
└────────────────────────────────────────────────────────────┘
```

### Tab Behavior

| Tab | Content | Sort |
|---|---|---|
| All | Mixed results (best answer + top entities + top insights) | Relevance |
| Entities | Entity list matching query | Name |
| Evidence | Evidence nodes matching query | Recency |
| Insights | Insights matching query | Recency |

---

## Search History

Search history is stored in Zustand with localStorage persistence:

```typescript
interface SearchHistoryEntry {
    query: string
    timestamp: string
    resultCount: number
    insightId?: string  // If the user drilled into a result
}
```

| Feature | Behavior |
|---|---|
| Recent searches | Last 20 queries, shown in autocomplete |
| Clear history | Button in search bar dropdown |
| Re-run | Click a history item to re-submit |
| Save | Star a query to pin it to favorites (persisted) |

---

## Edge Cases

### Empty Query

If the user submits an empty query, the search bar shows a validation shake animation. No API call is made.

### Very Long Query

Queries over 500 characters are rejected client-side before submission:

```
"Question is too long (612 characters). Maximum length is 500."
```

### No Results

```
[Search results page — empty state]
No results found for "xyz".
Suggestions:
• Check spelling
• Try a broader term
• Run an analysis first: [Run Analysis]
```

### Question Parsing Failure

If the intent recognition stage cannot parse the question:

```
The system couldn't understand your question.
Try rephrasing. For example:
• "What is the error rate of the auth module?"
• "Who wrote the PaymentService class?"
• "Show me all recent insights about dependencies"
```
