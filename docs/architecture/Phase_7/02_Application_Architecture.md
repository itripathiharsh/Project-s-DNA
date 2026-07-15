================================================================================
# 02 Application Architecture
================================================================================

# Application Architecture

## Purpose

The frontend application architecture defines how code is organized, how pages relate to each other, how routing works, and how the component tree is structured. This document provides the blueprint for the entire frontend codebase — the skeleton upon which all features are built.

---

## Scope

### In Scope

- Directory and module structure
- Routing hierarchy and route definitions
- Page layout and shell components
- Component tree (top-level)
- Module dependency rules
- Code-splitting strategy
- Navigation architecture

### Out of Scope

- Individual component specifications (Phase 7/04)
- State management (Phase 7/03)
- Graph visualization engine (Phase 7/05)
- Build configuration and tooling

---

## Background

Phase 7/01 defined the overall frontend architecture: React 18 + TypeScript + Vite, with multiple application shells (Web SPA, Desktop, CLI). This document details the internal structure of the web/desktop application.

Phase 1 (Information Architecture) defined the navigation structure: Search/Ask, Dashboard, Repository View, Insights Feed, Reports, Settings. This routing structure implements that information architecture.

---

## Directory Structure

```
src/
├── main.tsx                    # Application entry point
├── App.tsx                     # Root component with router
├── routes.tsx                  # Route definitions
├──
├── components/                 # Shared UI components
│   ├── ui/                     # Primitive UI (Button, Input, Card, Badge)
│   ├── layout/                 # Shell layout (Sidebar, Header, Main)
│   ├── evidence/               # Evidence display components
│   ├── insights/               # Insight card, detail components
│   ├── entities/               # Entity display components
│   ├── search/                 # Search bar, autocomplete
│   ├── visualization/          # Graph, chart, timeline components
│   └── common/                 # Loading, empty, error states
│
├── pages/                      # Route-level page components
│   ├── Landing.tsx
│   ├── Dashboard.tsx
│   ├── SearchResults.tsx
│   ├── RepositoryDetail.tsx
│   ├── InsightsFeed.tsx
│   ├── Reports.tsx
│   ├── EvidenceExplorer.tsx
│   └── Settings.tsx
│
├── hooks/                      # Custom React hooks
│   ├── useWebSocket.ts
│   ├── useTokenStream.ts
│   ├── useEntitySearch.ts
│   ├── useInsights.ts
│   └── useAnalysis.ts
│
├── stores/                     # Zustand state stores
│   ├── uiStore.ts              # Sidebar, theme, preferences
│   ├── searchStore.ts          # Current query, results
│   └── workspaceStore.ts       # Active repository, filters
│
├── api/                        # API client layer
│   ├── client.ts               # Axios instance, interceptors
│   ├── entities.ts             # Entity API calls
│   ├── evidence.ts             # Evidence API calls
│   ├── insights.ts             # Insight API calls
│   ├── reasoning.ts            # Question/reasoning API calls
│   ├── analysis.ts             # Analysis API calls
│   └── queries.ts              # React Query hooks (composed from above)
│
├── visualization/              # D3, Recharts, React Flow modules
│   ├── graphs/                 # React Flow graph components
│   ├── charts/                 # Recharts chart components
│   └── custom/                 # Custom D3 visualizations
│
├── lib/                        # Utility functions
│   ├── formatters.ts           # Date, number, token formatters
│   ├── validators.ts           # Client-side validation
│   └── constants.ts            # App-wide constants
│
└── types/                      # TypeScript type definitions
    ├── api.ts                  # API response types
    ├── domain.ts               # Domain model types
    └── events.ts               # WebSocket event types
```

---

## Routing Structure

### Route Definitions

```typescript
const routes = [
    { path: '/',                   element: <Landing /> },
    { path: '/dashboard',          element: <Dashboard /> },
    { path: '/search',             element: <SearchResults /> },
    { path: '/repo/:id',           element: <RepositoryDetail /> },
    { path: '/repo/:id/:tab',      element: <RepositoryDetail /> },
    { path: '/insights',           element: <InsightsFeed /> },
    { path: '/insights/:id',       element: <InsightDetail /> },
    { path: '/evidence',           element: <EvidenceExplorer /> },
    { path: '/evidence/:id',       element: <EvidenceDetail /> },
    { path: '/reports',            element: <Reports /> },
    { path: '/reports/:id',        element: <ReportViewer /> },
    { path: '/settings',           element: <Settings /> },
    { path: '/settings/:tab',      element: <Settings /> },
]
```

### Navigation Map

```
/                       → Landing (repository import, or redirect to dashboard)
/dashboard              → Main dashboard with alerts, health, recent insights
/search?q=...           → Search results and answer view
/repo/:id               → Repository detail with tab navigation
/repo/:id/overview      → Overview tab
/repo/:id/structure     → Structure tab
/repo/:id/evolution     → Evolution tab
/repo/:id/knowledge     → Knowledge tab
/repo/:id/risks         → Risks tab
/insights               → Insights feed (sorted by recency)
/insights/:id           → Single insight with full evidence chain
/evidence               → Evidence explorer (filterable grid)
/evidence/:id           → Single evidence node with raw data
/reports                → Reports gallery
/reports/:id            → Generated report viewer
/settings               → Settings (general, model, API keys, about)
```

---

## Application Shell (Layout)

Every page is rendered inside a consistent shell layout:

```
┌─────────────────────────────────────────────────────┐
│  Header                                               │
│  [Logo] [Search Bar (global)] [Notifications] [User] │
├────────┬────────────────────────────────────────────┤
│        │                                              │
│ Sidebar│  Main Content Area                           │
│        │                                              │
│  Nav    │  {page content rendered here}               │
│  Links  │                                              │
│        │                                              │
│ [Coll.]│                                              │
│        │                                              │
├────────┴────────────────────────────────────────────┤
│  Status Bar   [Server: Connected] [Model: llama3.1] │
└─────────────────────────────────────────────────────┘
```

| Shell Component | Behavior |
|---|---|
| **Header** | Fixed top bar. Logo, global search bar, notification bell, user menu. Collapses on scroll. |
| **Sidebar** | Collapsible left nav. Links to Dashboard, Repositories, Insights, Evidence, Reports, Settings. Shows active repository name when in repo context. |
| **Main Content** | Route-dependent page content. Scrollable. Max-width container for readability. |
| **Status Bar** | Bottom bar showing server connection status, active model, last analysis time. Dismissable. |

---

## Component Tree (Top Level)

```
<App>
    <QueryClientProvider>          ← React Query
        <Router>
            <Shell>
                <Header>
                    <Logo />
                    <GlobalSearch />
                    <NotificationBell />
                    <UserMenu />
                </Header>
                <Sidebar>
                    <NavLinks />
                    <ActiveRepoContext />
                </Sidebar>
                <Main>
                    <Routes>
                        <Landing />
                        <Dashboard />
                        <SearchResults />
                        <RepositoryDetail />
                        <InsightsFeed />
                        <EvidenceExplorer />
                        <Reports />
                        <Settings />
                    </Routes>
                </Main>
                <StatusBar />
            </Shell>
            <WebSocketProvider />   ← Global WS connection
        </Router>
    </QueryClientProvider>
</App>
```

---

## Code-Splitting

Pages and heavy visualization components are lazy-loaded for performance:

```typescript
const Dashboard = lazy(() => import('./pages/Dashboard'))
const RepositoryDetail = lazy(() => import('./pages/RepositoryDetail'))
const EvidenceExplorer = lazy(() => import('./pages/EvidenceExplorer'))

// Visualization modules are loaded on demand
const DependencyGraph = lazy(() => import('./visualization/graphs/DependencyGraph'))
```

| Route | Split Point | Estimated Size |
|---|---|---|
| `/dashboard` | `pages/Dashboard.tsx` | 15 KB |
| `/repo/:id` | `pages/RepositoryDetail.tsx` | 25 KB |
| `/evidence` | `pages/EvidenceExplorer.tsx` | 20 KB |
| Visualization | `visualization/graphs/*` | 40 KB (D3) |
| Reports | `pages/Reports.tsx` | 10 KB |

---

## Module Dependency Rules

```
pages/         → components/, hooks/, stores/, api/,
                 visualization/, lib/, types/
components/    → lib/, types/                           (no stores, no hooks)
hooks/         → api/, stores/, types/                  (no components)
stores/        → lib/, types/                           (no components, no hooks)
api/           → types/                                 (no components, no hooks)
visualization/ → components/ui/, lib/, types/           (no pages)
lib/           → types/                                 (no other modules)
types/         → nothing                                (pure types)
```

---

## Navigation Architecture

### Programmatic Navigation

```typescript
// From any component
const navigate = useNavigate()
navigate('/repo/mod_auth_001/risks')

// From a Zustand store (outside React)
import { navigate } from './lib/navigation'
navigate('/insights/insight_synth_001')
```

### Deep Linking

Every page supports deep linking via URL parameters:
- `/repo/:id?tab=risks` → Opens repository at Risks tab.
- `/search?q=auth+failures&entity=auth` → Pre-filled search.
- `/insights?severity=high&entity=mod_auth_001` → Filtered insight list.

### Breadcrumbs

Repository and insight pages show breadcrumb navigation:

```
Dashboard > Repositories > src/auth > Risks > Auth module error rate
```

---

## Edge Cases

### Unknown Route

Any unknown path renders the NotFound page with suggested navigation:

```
/unknown-route → <NotFound>
    "Page not found. Try the Dashboard or search for what you need."
    [Go to Dashboard] [Search]
```

### Repository Not Found

If a repository ID is invalid or not yet analyzed:

```
/repo/nonexistent → <RepositoryNotFound>
    "Repository 'nonexistent' was not found."
    [Import Repository] [Go to Dashboard]
```

### Deep Link Before Data Ready

When navigating directly to a deep link (e.g., `/evidence/trace_001`) before the evidence data has loaded:

```
1. Route matches → render page shell immediately
2. Page shows <LoadingState /> while data fetches
3. Data arrives → render content
4. If data is 404 → render <NotFound />
```
