================================================================================
# 10 Glossary
================================================================================

# Glossary

## Purpose

This glossary defines every key term introduced across Phase 7 (Frontend), with cross-references to related concepts in other phases.

---

## A

### Application Shell

The top-level layout wrapper rendered by the router. Contains Header (logo, search bar, notifications, user menu), Sidebar (collapsible navigation), Main Content Area (route-dependent), and Status Bar (server connection, model info). Defined in Phase 7/02.

*See also:* Routing Hierarchy, Page Component.

---

## D

### Dashboard

The default landing page. Provides a personalized overview: context header, health scorecard, active alert cards, recent insights feed, and quick actions. Defined in Phase 7/08.

*See also:* Health Scorecard, Alert Card.

### Domain Component

A Level 2 component that combines UI primitives to represent specific Project DNA data types (InsightCard, EvidenceRow, EntityBadge, ConfidenceBar, EvidenceChain). Domain components are reusable across features.

*See:* Phase 7/04.
*See also:* Primitive Component, Feature Component.

---

## E

### Evidence Explorer

The dedicated interface for browsing, filtering, and inspecting evidence nodes. Features filterable list view, detail panel with raw data access, evidence comparison, and cross-linking to insights and entities. Defined in Phase 7/07.

*See also:* Evidence Node, Evidence Chain.

---

## F

### Feature Component

A Level 3 component that implements a complete feature (InsightList, EvidenceExplorer, DependencyGraph). Composes domain components and integrates with state management hooks. Used by page components.

*See:* Phase 7/04.

---

## G

### Graph Visualization

The interactive node-edge diagram system built on React Flow, Recharts, and D3.js. Supports dependency graphs, entity relationship graphs, timeline charts, and evidence chain visualizations. Defined in Phase 7/05.

*See also:* Dependency Graph, Entity Graph, Evidence Chain.

---

## H

### Health Scorecard

A dashboard widget showing composite health scores across five dimensions (Structure, Evolution, Knowledge, Dependency, Risk). Each dimension is scored 0–100 from Cognitive Engine evidence. Overall score is a weighted average. Defined in Phase 7/08.

---

## P

### Page Component

A Level 4 component that corresponds to a route. Renders within the Application Shell. Composes feature and domain components. Lazy-loaded via React.lazy. Defined in Phase 7/02.

*See also:* Application Shell, Routing Hierarchy.

### Primitive Component

A Level 1 component — the smallest reusable UI element (Button, Input, Card, Badge, Tooltip, Spinner, Skeleton). Does not import any domain or feature components. Styled entirely with Tailwind CSS utility classes. Defined in Phase 7/04.

*See also:* Domain Component, Feature Component.

---

## R

### React Query (TanStack Query)

Server state management library. Manages API data caching, background refetching, optimistic updates, and cache invalidation for all data fetched from the Project DNA API Gateway. Data is fetched via hooks like `useInsights()` and `useEntity()`.

*See:* Phase 7/03.
*See also:* Zustand.

### Routing Hierarchy

The route structure connecting paths to page components: `/` (Landing), `/dashboard`, `/search`, `/repo/:id`, `/insights`, `/evidence`, `/reports`, `/settings`. Supports deep linking and breadcrumb navigation. Defined in Phase 7/02.

*See also:* Application Shell, Page Component.

---

## S

### Search Bar / Search UI

The primary entry point for user interaction. A global search bar in the header with autocomplete (entities, previous questions, suggestions), question submission via WebSocket, token streaming answer view, and follow-up question support. Defined in Phase 7/06.

*See also:* Token Streaming, Answer View.

---

## T

### Token Streaming

Real-time display of LLM-generated tokens as they arrive via WebSocket. Each token is appended to the Answer View component with a blinking cursor animation during active streaming. Defined in Phase 7/06.

*See also:* Search Bar, WebSocket API.

---

## Z

### Zustand

Client state management library. Handles global UI state that does not come from the API: sidebar open state, theme preference, search input, active repository, UI filters. Some stores are persisted to localStorage. Defined in Phase 7/03.

*See also:* React Query.
