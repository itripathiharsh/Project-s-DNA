================================================================================
# 01 Frontend Overview
================================================================================

# Frontend Overview

## Purpose

The frontend is the primary interface through which users interact with Project DNA — asking questions, exploring evidence, visualizing software structure, and acting on insights. This document defines the frontend architecture, technology stack, application shells, and how the frontend connects to the API Gateway (Phase 6) to deliver the experiences defined in Phase 1 (UX Design).

---

## Scope

### In Scope

- Frontend architecture overview
- Technology stack (React 18, Vite, Zustand, React Query, D3.js, Recharts, React Flow)
- Application shells (Web SPA, Desktop via Tauri, CLI)
- Key feature areas and their components
- API integration patterns
- Build pipeline and distribution
- Performance and accessibility targets

### Out of Scope

- Detailed component hierarchy (Phase 7/04)
- State management internals (Phase 7/03)
- Graph visualization engine (Phase 7/05)
- Search UI implementation (Phase 7/06)
- Evidence Explorer (Phase 7/07)
- Dashboard architecture (Phase 7/08)

---

## Background

Phase 1 (Product Design UX) defined six user journeys (Developer, Tech Lead, Engineering Manager, New Engineer, Architect, Investor) and the information architecture: Search/Ask, Dashboard, Repository View, Insights Feed, Reports, Settings. The UX specification detailed 12 screens with loading, empty, and error states for each.

Phase 2 (System Architecture) established the technology stack:
- **Framework:** React 18 + Vite + TypeScript
- **State management:** Zustand (global UI state) + React Query (server state)
- **Visualization:** D3.js (custom) + Recharts (charts) + React Flow (graphs)
- **Packaging:** Docker (server), Tauri (desktop), npm (CLI)

Phase 6 (API & Integration Layer) defined the REST, WebSocket, and GraphQL APIs that the frontend consumes.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Application Shells                              │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐   │
│  │  Web SPA (Vite)  │  │  Desktop (Tauri) │  │  CLI (Node.js) │   │
│  │  - Browser app   │  │  - Native window │  │  - Terminal    │   │
│  │  - Hot reload    │  │  - File system   │  │  - Scriptable  │   │
│  │  - PWA ready     │  │  - System tray   │  │  - Pipeable    │   │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬───────┘   │
│           │                     │                      │           │
└───────────┼─────────────────────┼──────────────────────┼───────────┘
            │                     │                      │
            └──────────┬──────────┘                      │
                       │                                 │
              ┌────────▼────────┐                        │
              │   API Client     │                        │
              │  (Axios + WS)   │                        │
              │  - REST calls   │                        │
              │  - WebSocket    │                        │
              │  - Auth tokens  │                        │
              └────────┬────────┘                        │
                       │ HTTP / WebSocket                │
                       ▼                                 │
              ┌──────────────────┐                       │
              │  API Gateway     │◄──────────────────────┘
              │  (localhost:8000)│   Direct IPC (CLI)
              └──────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Framework** | React 18 + TypeScript | Component model, type safety |
| **Build** | Vite 5 | Fast dev server, optimized builds |
| **Global state** | Zustand | Lightweight global UI state |
| **Server state** | TanStack React Query | API caching, sync, background updates |
| **Routing** | React Router v6 | Client-side navigation |
| **HTTP client** | Axios | REST API calls |
| **WebSocket** | Native WebSocket + reconnection | Real-time events, token streaming |
| **Charts** | Recharts + D3.js | Metric visualization, custom viz |
| **Graphs** | React Flow | Interactive entity relationship graphs |
| **Styling** | Tailwind CSS | Utility-first, consistent design |
| **Desktop** | Tauri (Rust + web view) | Native desktop packaging |
| **Testing** | Vitest + React Testing Library | Unit and component tests |
| **Linting** | ESLint + Prettier | Code quality |

---

## Application Shells

### Web SPA (V1)

The primary delivery mechanism. A single-page application served by Vite:

```
dna-ui/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Route-level page components
│   ├── hooks/          # Custom React hooks
│   ├── stores/         # Zustand stores
│   ├── api/            # API client + React Query hooks
│   ├── visualization/  # D3, Recharts, React Flow components
│   └── lib/            # Utility functions
├── index.html
├── vite.config.ts
└── package.json
```

**Start:** `npm run dev` → `http://localhost:5173`

### Desktop App (V1 — Tauri)

For users who prefer a native experience. Tauri wraps the web frontend in a native window with additional capabilities:

| Capability | Web SPA | Desktop |
|---|---|---|
| Local API connection | `localhost:8000` | `localhost:8000` |
| File system access | None | Open local repos, config files |
| System tray | No | Yes — background analysis |
| Auto-start | No | Yes — on login |
| Native notifications | Browser API | OS-native notifications |
| Menu bar | None | Native menus |

### CLI (V1 — npm package)

For scripting and automation. A Node.js CLI that wraps the REST API:

```
dna query "What is causing auth failures?"
dna insights list --entity auth --severity high
dna analysis run --full
dna watch --subscribe insights
```

The CLI uses the same API client library as the web frontend.

---

## Key Feature Areas

| Feature | Phase 7 Doc | Primary Components |
|---|---|---|
| **Search / Ask** | 06 | SearchBar, AnswerView, InsightCard, TokenStream |
| **Dashboard** | 08 | ContextHeader, AlertCards, HealthScorecard, RecentInsights, QuickActions |
| **Repository View** | 04 | TabBar, OverviewTab, StructureTab, EvolutionTab, KnowledgeTab, RisksTab |
| **Graph Visualization** | 05 | DependencyGraph, EntityGraph, TimelineGraph |
| **Evidence Explorer** | 07 | EvidenceList, EvidenceDetail, EvidenceChainView, RawDataView |
| **Insights Feed** | 08 | InsightFeed, InsightCard, FilterBar |
| **Reports** | 04 | ReportList, ReportViewer, ExportButton |
| **Settings** | 04 | SettingsForm, ModelConfig, KeyManager |

---

## API Integration Patterns

### REST (React Query)

```typescript
// Auto-cached, background-refreshed data
const { data, isLoading, error } = useQuery({
    queryKey: ['insights', { entityId: 'mod_auth_001' }],
    queryFn: () => api.getInsights({ entityId: 'mod_auth_001' }),
    staleTime: 30_000,  // 30s before refetch
})

// Mutations with optimistic updates
const mutation = useMutation({
    mutationFn: (id: string) => api.updateInsightStatus(id, 'acknowledged'),
    onMutate: async (id) => {
        // Optimistically update cache
    },
})
```

### WebSocket (Real-Time)

```typescript
const ws = useWebSocket({
    url: 'ws://localhost:8000/v1/ws',
    onEvent: (event) => {
        switch (event.channel) {
            case 'insights:mod_auth_001':
                queryClient.invalidateQueries({ queryKey: ['insights'] })
                break
            case 'analysis:job_046':
                setProgress(event.data.progress)
                break
        }
    },
    onToken: (token) => {
        appendToStream(token)
    },
})
```

### Streaming (LLM Tokens)

When the user asks a question, the frontend opens a WebSocket and streams tokens into the AnswerView component in real time. The user sees the answer being written word by word.

---

## Build and Distribution

| Artifact | Command | Output |
|---|---|---|
| Web SPA (dev) | `npm run dev` | `localhost:5173` |
| Web SPA (build) | `npm run build` | `dist/` (static files) |
| Desktop | `npm run tauri build` | `.msi` / `.dmg` / `.AppImage` |
| CLI | `npm run build:cli` | `dna` (Node.js script) |
| Docker | `docker build -t dna-ui .` | Container with Nginx + static build |

---

## Performance and Accessibility

### Performance Targets

| Metric | Target | Measurement |
|---|---|---|
| First Contentful Paint (FCP) | < 1.5s | Lighthouse |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| Interaction to Next Paint (INP) | < 200ms | Web Vitals |
| Bundle size (initial) | < 200 KB gzipped | Vite analyze |
| Time to interactive | < 3s | Lighthouse |

### Accessibility Targets

- WCAG 2.1 AA compliance (minimum).
- WCAG 2.1 AAA for color contrast.
- Full keyboard navigation.
- Screen reader support (ARIA labels on all interactive elements).
- Focus management for single-page app navigation.

---

## Edge Cases

### API Gateway Not Running

When the frontend starts and cannot reach `localhost:8000`:

1. Show a "Connecting to Project DNA..." screen with animation.
2. Retry connection every 3 seconds.
3. If no connection after 30 seconds, show setup instructions: "Start the Project DNA server with `dna serve`."
4. Provide a one-click "Start Server" button (desktop app only — spawns the server process).

### Slow LLM Inference

When the LLM takes longer than expected (no tokens received for 10 seconds):

1. Show a "Still thinking..." indicator with elapsed time.
2. If no response after 60 seconds, show "Taking longer than expected. You can wait or cancel."
3. Cancel button sends a WebSocket cancel message.
4. On cancel, show partial results if any were streamed.

### Offline Mode

The frontend always works in offline mode by design:
- No external CDN dependencies (all assets bundled).
- No external API calls (all to localhost).
- Service worker caches the SPA for instant reloads.

---

## The Frontend Doctrine

> **The frontend is the face of Project DNA. It is where understanding becomes visible, where evidence becomes explainable, and where users act on insights. It is fast, accessible, and local-first. It communicates with the API Gateway through REST for queries and WebSocket for real-time events. It renders graphs, charts, evidence chains, and insight narratives — always grounded in the data, always responsive to the user. The frontend does not hide complexity. It makes complexity understandable.**
