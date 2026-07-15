================================================================================
# 05 Graph Visualization
================================================================================

# Graph Visualization

## Purpose

Graph visualization is the visual heart of Project DNA. Users explore software structure through interactive node-edge diagrams, track trends through charts, and navigate evidence chains through linked graphs. This document defines the visualization architecture, graph types, interaction patterns, rendering strategy, and performance considerations.

---

## Scope

### In Scope

- Visualization stack (React Flow, Recharts, D3.js)
- Graph types (dependency, entity, timeline, evidence chain)
- Interaction patterns (pan, zoom, click, hover, drag)
- Rendering strategy (SVG vs Canvas, progressive loading)
- Large graph performance
- Animation and transitions

### Out of Scope

- Specific component API (Phase 7/04)
- State management for visualization (Phase 7/03)
- Search UI integration (Phase 7/06)
- Dashboard layout (Phase 7/08)

---

## Background

Phase 2 (Decision 10) established the visualization technology stack:
- **React Flow** — Interactive node-edge graphs for dependency and entity visualizations.
- **Recharts** — Standard charts for metrics, trends, and distributions.
- **D3.js** — Custom visualizations (timeline, heatmap, custom layouts) when React Flow or Recharts don't suffice.

Phase 3 defined the SCM graph structure — entities as nodes, relationships as edges. The visualization layer brings this graph to life.

---

## Visualization Stack

```
┌─────────────────────────────────────────────────────────────┐
│                  Visualization Layer                           │
│                                                               │
│  ┌──────────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   React Flow      │  │   Recharts    │  │   D3.js       │  │
│  │   - Dependency   │  │   - Line      │  │   - Timeline  │  │
│  │   - Entity graph │  │   - Bar       │  │   - Heatmap   │  │
│  │   - Evidence     │  │   - Area      │  │   - Force     │  │
│  │     chain        │  │   - Radar     │  │   - Custom    │  │
│  └────────┬─────────┘  └──────┬───────┘  └──────┬─────────┘  │
│           │                   │                  │            │
│           └────────┬──────────┴──────────────────┘            │
│                    │                                          │
│  ┌─────────────────▼──────────────────────────────────────┐  │
│  │              Visualization Utilities                    │  │
│  │  - Color scales (severity, engine, confidence)         │  │
│  │  - Layout algorithms (dagre, force, radial)            │  │
│  │  - Zoom/pan controls                                   │  │
│  │  - Responsive containers                               │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## Graph Types

### Dependency Graph (React Flow)

Nodes represent modules or packages. Edges represent dependencies.

```
┌──────────────┐     ┌──────────────┐
│  src/auth    │────▶│  lodash      │
└──────────────┘     └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  src/payment │────▶│  stripe-sdk  │
└──────────────┘     └──────────────┘
```

| Feature | Behavior |
|---|---|
| Node color | By module tier / risk level |
| Edge thickness | By dependency weight (call count, import count) |
| Edge color | Green (healthy), yellow (outdated), red (vulnerable) |
| Click node | Open module detail |
| Hover edge | Show dependency metadata (version, calls) |
| Layout | Dagre (directed, hierarchical) |

### Entity Graph (React Flow)

Nodes represent any SCM entity type. Edges represent relationships.

```
┌────────────┐    contains    ┌────────────┐
│  src/auth  │───────────────▶│ validate.ts│
└────────────┘                └────────────┘
      │                             │
      │ depends_on                  │ contains
      ▼                             ▼
┌────────────┐              ┌──────────────┐
│  lodash    │              │ validateToken│
└────────────┘              └──────────────┘
```

| Feature | Behavior |
|---|---|
| Node shape | By entity type (rect=module, circle=function, diamond=person) |
| Filter | Show/hide by entity type |
| Expand | Double-click node to expand its sub-graph |
| Collapse | Right-click → collapse children |

### Timeline Graph (D3.js custom)

Time-based visualization of metrics, events, and trends.

```
Error Rate (%)
40 ║                                    ●
30 ║                           ●
20 ║                  ●
10 ║    ●    ●    ●
 0 ╚══════════════════════════════════════
    Jul 7  Jul 8  Jul 9  Jul 10 Jul 11 Jul 12 Jul 13 Jul 14
```

| Feature | Behavior |
|---|---|
| Multi-series | Overlay multiple metrics (error rate, latency, call count) |
| Event markers | Vertical lines for deployments, config changes |
| Brush | Select time range to zoom |
| Hover | Crosshair with value readout |
| Trend line | Dashed linear regression overlay |

### Evidence Chain Graph (React Flow)

The directed graph from insight through evidence to raw data.

```
┌──────────────────┐
│  Insight          │
│  "Auth degrading" │
└────────┬─────────┘
         │ supported_by
         ▼
┌──────────────────┐     ┌──────────────────┐
│  trace_001        │────▶│  raw_data         │
│  36.8% error rate │     │  auth.log:847     │
└──────────────────┘     └──────────────────┘
         │ supported_by
         ▼
┌──────────────────┐     ┌──────────────────┐
│  trace_002        │────▶│  raw_data         │
│  TypeError:88     │     │  auth.log:849     │
└──────────────────┘     └──────────────────┘
```

| Feature | Behavior |
|---|---|
| Node color | By evidence engine or confidence |
| Edge label | Relationship type (`supported_by`, `derived_from`) |
| Click evidence | Open evidence detail panel |
| Click raw data | Open file at line in source view |
| Collapse | Group evidence by engine |

---

## Interaction Patterns

| Gesture | Behavior | Components |
|---|---|---|
| Pan | Click and drag background | All graphs |
| Zoom | Scroll wheel, pinch | All graphs |
| Click node | Select / open detail | All graphs |
| Double-click | Expand sub-graph (entity graph) | EntityGraph |
| Hover node | Tooltip with summary | All graphs |
| Hover edge | Tooltip with relationship detail | DependencyGraph, EvidenceChain |
| Drag node | Reposition (local only) | All graphs |
| Lasso select | Draw selection area to select multiple nodes | EntityGraph |
| Right-click | Context menu | All graphs |

---

## Rendering Strategy

### SVG (Default)

React Flow and Recharts use SVG by default. Suitable for:
- Up to 500 nodes / 2000 edges.
- Interactive elements (hover, click, drag).
- Crisp rendering at any zoom level.

### Canvas (Large Graphs)

For graphs exceeding SVG performance limits, switch to Canvas rendering:

```
if (nodeCount > 500 || edgeCount > 2000):
    renderMode = 'canvas'
else:
    renderMode = 'svg'
```

| Mode | Max Recommended | Technology |
|---|---|---|
| SVG | 500 nodes, 2000 edges | React Flow default |
| Canvas | 5000 nodes, 20000 edges | React Flow canvas mode or D3 canvas |

### Progressive Loading

For very large graphs:

1. Load top-level nodes first (modules).
2. Show loading indicator: "Loading 1,200 nodes..."
3. Expand children on demand (click to load sub-nodes).
4. Cache loaded sub-graphs in React Query cache.

---

## Performance

| Optimization | Technique | Impact |
|---|---|---|
| Node memoization | `React.memo` on all graph node components | Prevents re-render of static nodes |
| Viewport culling | Only render nodes visible in viewport | 2–5x FPS improvement for large graphs |
| Debounced layout | Debounce layout recalculation during drag | Smooth interaction |
| WebGL | Canvas mode for 1000+ node graphs | Maintains 30+ FPS |
| Lazy loading | Load graph data only when tab is active | Reduces initial bundle |

---

## Color System

Colors are semantic and consistent across all visualization types:

| Severity | Color | Hex |
|---|---|---|
| CRITICAL | Red | `#DC2626` |
| HIGH | Orange | `#EA580C` |
| MEDIUM | Yellow | `#CA8A04` |
| LOW | Blue | `#2563EB` |
| INFO | Gray | `#6B7280` |

| Evidence Engine | Color |
|---|---|
| structural_cognition | `#7C3AED` (purple) |
| evolution_cognition | `#059669` (green) |
| knowledge_cognition | `#0284C7` (blue) |
| dependency_cognition | `#D97706` (amber) |
| risk_cognition | `#DC2626` (red) |

---

## Edge Cases

### Empty Graph

When no data exists for the selected entity:

```
[EmptyState]
No dependencies found for this module.
This module has no external dependencies.
```

### Single-Node Graph

A module with no dependencies or a function with no callers renders as a single centered node with appropriate messaging.

### Circular Dependencies

Detected and rendered with a warning indicator on the affected edges. A badge shows: "Circular dependency detected" on hover.

### Graph Too Large

If the graph exceeds 5000 nodes:

```
[Warning banner]
"This graph contains 12,000 nodes. Showing module-level view only.
[Show full graph] [Zoom to module]"
```

User options: show zoomed view, filter by entity type, or search for a specific node.

---

## Future Work

### 3D Force-Directed Layout (V3)

For very large dependency graphs, use a 3D force-directed layout with WebGL rendering. Users orbit and zoom through the graph.

### Graph Diff View (V2)

Overlay two snapshots of the same graph to show what changed: new nodes highlighted green, removed nodes faded red, changed edges animated.

### Export Graph as Image (V2)

Export the current graph view as PNG or SVG for documentation and sharing.
