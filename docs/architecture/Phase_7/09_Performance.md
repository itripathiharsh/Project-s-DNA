================================================================================
# 09 Performance
================================================================================

# Performance

## Purpose

The frontend must feel instant — even when rendering thousands of evidence nodes, navigating complex graphs, or streaming LLM tokens. This document defines the performance targets, optimization strategies, measurement methodology, and build-time optimizations that ensure the frontend meets its speed and responsiveness goals.

---

## Scope

### In Scope

- Performance targets and measurement
- Bundle size optimization
- Rendering optimization (memoization, virtualization)
- Graph rendering performance (SVG vs Canvas, culling)
- Network optimization (caching, prefetching, compression)
- Build-time optimizations (code splitting, tree shaking)
- Performance monitoring in production

### Out of Scope

- API Gateway performance (Phase 6)
- LLM inference speed (Phase 5)
- Cognitive Engine performance (Phase 4)

---

## Background

Phase 2 established the technology stack with performance implications: Vite (fast builds), React 18 (concurrent features), TanStack Query (caching). Phase 7/05 introduced graph rendering with SVG/Canvas selection criteria.

---

## Performance Targets

| Metric | Target | Source |
|---|---|---|
| First Contentful Paint (FCP) | < 1.5s | Lighthouse |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| Interaction to Next Paint (INP) | < 200ms | Web Vitals |
| Total Blocking Time (TBT) | < 300ms | Lighthouse |
| Bundle size (initial JS) | < 200 KB gzipped | Vite |
| Time to Interactive (TTI) | < 3s | Lighthouse |
| Graph render (500 nodes) | < 500ms | Custom benchmark |
| Search autocomplete | < 100ms (after keydown) | Custom benchmark |
| Token stream latency | < 200ms (first token) | Custom benchmark |

---

## Bundle Size Optimization

### Code Splitting Routes

All page-level components are lazy-loaded via `React.lazy` + dynamic `import()`:

```typescript
const Dashboard = lazy(() => import('./pages/Dashboard'))
const RepositoryDetail = lazy(() => import('./pages/RepositoryDetail'))
const EvidenceExplorer = lazy(() => import('./pages/EvidenceExplorer'))
const Reports = lazy(() => import('./pages/Reports'))
const Settings = lazy(() => import('./pages/Settings'))
```

### Code Splitting Visualization Modules

Heavy visualization libraries are loaded only when the corresponding tab is activated:

```typescript
// Load D3 only when the user visits the graph tab
const DependencyGraph = lazy(() => import('./visualization/graphs/DependencyGraph'))

// Load Recharts only when charts are visible
const MetricChart = lazy(() => import('./visualization/charts/MetricChart'))
```

### Tree Shaking

Import only what's needed from large libraries:

```typescript
// Good — only imports the specific module
import { scaleLinear } from 'd3-scale'
import { schemeCategory10 } from 'd3-scale-chromatic'

// Avoid — imports the entire D3 library
import * as d3 from 'd3'
```

### Bundle Size Budget

| Bundle | Max Size (gzipped) | Contents |
|---|---|---|
| `main.js` | 80 KB | React, React Router, app shell |
| `vendor.js` | 60 KB | React Query, Zustand, Axios |
| `ui.js` | 30 KB | UI primitives, common components |
| `pages-dashboard.js` | 15 KB | Dashboard components |
| `pages-repo.js` | 25 KB | Repository detail components |
| `viz-graph.js` | 40 KB | React Flow, D3 graph modules |
| `viz-chart.js` | 20 KB | Recharts, chart components |

---

## Rendering Optimization

### Memoization

```typescript
// Prevent re-render of unchanged evidence items
const EvidenceRow = memo(function EvidenceRow({ evidence }: EvidenceRowProps) {
    return (
        <div className="flex items-center p-3 border-b">
            <SeverityBadge severity={evidence.severity} />
            <span className="ml-2">{evidence.value}</span>
        </div>
    )
})
```

| Component | Memoized | Reason |
|---|---|---|
| `EvidenceRow` | Yes | Many items in list, frequent filter changes |
| `InsightCard` | Yes | Renders in feeds and search results |
| `GraphNode` | Yes | Hundreds of nodes, frequent pan/zoom |
| `Chart` | Yes | Expensive Recharts renders |
| `Header` | Yes | Never changes after mount |
| `SearchBar` | No | Needs re-render on input |

### Virtualization

For lists exceeding 100 items, use `@tanstack/react-virtual`:

```typescript
const virtualizer = useVirtualizer({
    count: evidence.length,
    getScrollElement: () => scrollRef.current,
    estimateSize: () => 64,  // 64px per row
})

return (
    <div ref={scrollRef} style={{ height: '600px', overflow: 'auto' }}>
        <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
            {virtualizer.getVirtualItems().map((item) => (
                <EvidenceRow
                    key={evidence[item.index].id}
                    evidence={evidence[item.index]}
                    style={{ transform: `translateY(${item.start}px)` }}
                />
            ))}
        </div>
    </div>
)
```

| Component | Virtualized | Threshold |
|---|---|---|
| Evidence list | Yes | > 100 items |
| Insight feed | Yes | > 50 items |
| Entity list | Yes | > 100 items |
| Search results | Yes | > 50 items |

### Graph Rendering Optimization

| Technique | When | Benefit |
|---|---|---|
| Viewport culling | > 300 nodes | Only render visible nodes |
| Canvas mode | > 500 nodes | Better FPS with many nodes |
| Debounced layout | During drag | Prevents layout thrash |
| Node clustering | > 1000 nodes | Group related nodes |
| Progressive load | > 500 nodes | Show skeleton first |

---

## Network Optimization

### React Query Caching

| Query | staleTime | gcTime | Refetch Behavior |
|---|---|---|---|
| Entity list | 60s | 5min | On focus, on mutation |
| Evidence list | 30s | 5min | On focus, on WS event |
| Insight list | 30s | 5min | On focus, on WS event |
| Evidence detail | 5min | 30min | Manual only (immutable) |
| Health | 10s | 60s | Polling every 10s |

### Prefetching

Prefetch data the user is likely to navigate to:

```typescript
// Prefetch entity detail on hover
const queryClient = useQueryClient()

const handleEntityHover = (id: string) => {
    queryClient.prefetchQuery({
        queryKey: ['entities', id],
        queryFn: () => api.entities.get(id),
        staleTime: 60_000,
    })
}
```

| Trigger | Prefetch Target |
|---|---|
| Hover on insight card | Insight detail, evidence chain |
| Hover on entity badge | Entity detail |
| Dashboard mount | Top 5 insights, health data |
| Search input (debounced) | Autocomplete results |

### Request Deduplication

React Query automatically deduplicates concurrent requests for the same query key. If two components mount simultaneously and both fetch `['entities']`, only one network request is made.

---

## Build-Time Optimizations

| Optimization | Tool | Impact |
|---|---|---|
| ESBuild minification | Vite (default) | Fast builds, small output |
| CSS purging | Tailwind (production) | Removes unused CSS classes |
| Image optimization | vite-plugin-imagemin | Compresses SVG/PNG assets |
| Module preload | Vite | Preloads critical chunks |
| Dynamic imports | React.lazy | Splits bundles by route |

---

## Performance Monitoring

### Development

```bash
# Analyze bundle composition
npx vite-bundle-analyzer

# React Profiler (in-browser)
React DevTools → Profiler tab

# Lighthouse report
npx lighthouse http://localhost:5173 --view
```

### Production

| Tool | What It Measures |
|---|---|
| Web Vitals (via API) | FCP, LCP, INP, CLS |
| React Profiler (dev build) | Component render times |
| Custom performance marks | Token stream latency, graph render time |

---

## Edge Cases

### Slow First Load

If the user has a slow machine or many background processes:

- Show skeleton screens immediately (no waiting for JS).
- Prioritize critical CSS inline in `<head>`.
- Defer non-critical JavaScript (graph visualization, charts).

### Low Memory Device

On devices with < 4 GB RAM:
- Limit evidence list to 500 items in view (virtualized).
- Unload graph data when tab is not visible.
- Reduce animation complexity (`prefers-reduced-motion`).
- Dispose WebGL contexts when navigating away from graph.

### Network Latency (Remote API)

In V2+ network mode with the API on a remote server:
- Increase `staleTime` to reduce requests.
- Enable React Query's `networkMode: 'offlineFirst'`.
- Show stale data immediately while refetching in background.
