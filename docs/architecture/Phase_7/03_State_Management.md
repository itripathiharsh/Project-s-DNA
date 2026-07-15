================================================================================
# 03 State Management
================================================================================

# State Management

## Purpose

The frontend manages two categories of state: server state (SCM data, insights, evidence — fetched from the API) and client state (UI preferences, active selections, search input). This document defines how each category is managed, how they interact, and the caching, synchronization, and optimistic update strategies that keep the UI responsive and consistent.

---

## Scope

### In Scope

- Server state management with React Query (TanStack Query)
- Client state management with Zustand
- Store architecture and boundaries
- Cache invalidation strategy
- Optimistic updates
- WebSocket-driven cache synchronization
- Offline state handling

### Out of Scope

- Component-level local state (useState, useReducer)
- Form state management
- Routing state (React Router)

---

## Background

Phase 2 (Decision 9) established the state management architecture:
- **Zustand** for global UI state (lightweight, minimal boilerplate).
- **React Query (TanStack Query)** for server state (caching, synchronization, background updates).

Phase 6 defined the REST API that React Query fetches from and the WebSocket API that pushes real-time updates.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     State Architecture                            │
│                                                                   │
│  ┌──────────────────────────────────────┐  ┌──────────────────┐  │
│  │         Server State (React Query)     │  │  Client State     │  │
│  │                                        │  │  (Zustand)        │  │
│  │  - Entities                           │  │                   │  │
│  │  - Evidence                           │  │  - Sidebar open   │  │
│  │  - Insights                           │  │  - Theme          │  │
│  │  - Analysis status                    │  │  - Search input   │  │
│  │  - Search results                     │  │  - Active repo    │  │
│  │                                        │  │  - Filters        │  │
│  │  Cached, auto-refreshed,              │  │  - Preferences    │  │
│  │  invalidated by WS events             │  │                   │  │
│  └──────────────────┬───────────────────┘  │  Persisted to     │  │
│                     │                       │  localStorage     │  │
│                     │ Uses                  └──────────────────┘  │
│                     ▼                                              │
│  ┌──────────────────────────────────────┐                         │
│  │         API Client (Axios)            │                         │
│  │  - REST calls                         │                         │
│  │  - WebSocket connection               │                         │
│  └──────────────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Server State (React Query)

### Query Key Convention

```typescript
// [resource, ...params]
['entities']
['entities', id]
['evidence', { entityId, engine, page }]
['insights', { entityId, severity, status }]
['insights', id]
['analysis', jobId]
['search', { query, types }]
```

### Query Configuration

```typescript
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 30_000,           // 30s — data is fresh
            gcTime: 5 * 60_000,          // 5min — keep in cache
            retry: 2,                    // Retry twice on failure
            refetchOnWindowFocus: true,  // Refresh when user returns
        },
    },
})
```

### Pre-Built Query Hooks

```typescript
// src/api/queries.ts

export function useEntities(filter?: EntityFilter) {
    return useQuery({
        queryKey: ['entities', filter],
        queryFn: () => api.entities.list(filter),
        placeholderData: keepPreviousData,  // Keep old data while fetching next page
    })
}

export function useEntity(id: string) {
    return useQuery({
        queryKey: ['entities', id],
        queryFn: () => api.entities.get(id),
        enabled: !!id,                     // Don't fetch if id is empty
    })
}

export function useInsights(filter?: InsightFilter) {
    return useQuery({
        queryKey: ['insights', filter],
        queryFn: () => api.insights.list(filter),
    })
}

export function useEvidenceChain(insightId: string) {
    return useQuery({
        queryKey: ['insights', insightId, 'evidence-chain'],
        queryFn: () => api.insights.getEvidenceChain(insightId),
        staleTime: 60_000,  // Evidence chains are immutable — longer cache
    })
}
```

### Mutations

```typescript
export function useUpdateInsightStatus() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: ({ id, status }: { id: string; status: InsightStatus }) =>
            api.insights.updateStatus(id, status),
        onSuccess: (_, { id }) => {
            // Invalidate the individual insight and the list
            queryClient.invalidateQueries({ queryKey: ['insights', id] })
            queryClient.invalidateQueries({ queryKey: ['insights'] })
        },
    })
}
```

---

## Client State (Zustand)

### Store Definitions

```typescript
// stores/uiStore.ts
interface UIState {
    sidebarOpen: boolean
    theme: 'light' | 'dark' | 'system'
    notifications: Notification[]
    
    toggleSidebar: () => void
    setTheme: (theme: 'light' | 'dark' | 'system') => void
    addNotification: (n: Notification) => void
    dismissNotification: (id: string) => void
}

export const useUIStore = create<UIState>()(
    persist(
        (set) => ({
            sidebarOpen: true,
            theme: 'system',
            notifications: [],
            toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
            setTheme: (theme) => set({ theme }),
            addNotification: (n) => set((s) => ({ notifications: [...s.notifications, n] })),
            dismissNotification: (id) => set((s) => ({ notifications: s.notifications.filter((n) => n.id !== id) })),
        }),
        { name: 'dna-ui-store', partialize: (state) => ({ theme: state.theme }) }
    )
)
```

```typescript
// stores/searchStore.ts
interface SearchState {
    query: string
    selectedEntities: string[]
    isSearching: boolean
    
    setQuery: (q: string) => void
    addEntity: (id: string) => void
    removeEntity: (id: string) => void
    setIsSearching: (v: boolean) => void
    clearSearch: () => void
}

export const useSearchStore = create<SearchState>()((set) => ({
    query: '',
    selectedEntities: [],
    isSearching: false,
    setQuery: (query) => set({ query }),
    addEntity: (id) => set((s) => ({ selectedEntities: [...s.selectedEntities, id] })),
    removeEntity: (id) => set((s) => ({ selectedEntities: s.selectedEntities.filter((e) => e !== id) })),
    setIsSearching: (isSearching) => set({ isSearching }),
    clearSearch: () => set({ query: '', selectedEntities: [], isSearching: false }),
}))
```

```typescript
// stores/workspaceStore.ts
interface WorkspaceState {
    activeRepoId: string | null
    activeTab: string
    filters: {
        severity: string[]
        engine: string[]
        timeRange: [string, string] | null
    }
    
    setActiveRepo: (id: string | null) => void
    setActiveTab: (tab: string) => void
    setFilter: (key: string, value: any) => void
    resetFilters: () => void
}

export const useWorkspaceStore = create<WorkspaceState>()((set) => ({
    activeRepoId: null,
    activeTab: 'overview',
    filters: { severity: [], engine: [], timeRange: null },
    setActiveRepo: (activeRepoId) => set({ activeRepoId }),
    setActiveTab: (activeTab) => set({ activeTab }),
    setFilter: (key, value) => set((s) => ({ filters: { ...s.filters, [key]: value } })),
    resetFilters: () => set({ filters: { severity: [], engine: [], timeRange: null } }),
}))
```

### Persistence

| Store | Persisted | Medium | Fields Persisted |
|---|---|---|---|
| `uiStore` | Yes | localStorage | theme, sidebarOpen |
| `searchStore` | Yes | localStorage | query, selectedEntities |
| `workspaceStore` | No | — | — |

---

## WebSocket-Driven Cache Invalidation

When WebSocket events arrive, the frontend invalidates the relevant React Query cache to trigger refetches:

```typescript
// hooks/useWebSocketEvents.ts
export function useWebSocketEvents() {
    const queryClient = useQueryClient()

    useEffect(() => {
        const ws = connectWebSocket()

        ws.onEvent((event) => {
            switch (event.channel) {
                case 'insights:mod_auth_001':
                    // New insight for this entity — refresh insight list
                    queryClient.invalidateQueries({ queryKey: ['insights'] })
                    break
                case 'evidence:mod_auth_001':
                    // New evidence — refresh evidence queries
                    queryClient.invalidateQueries({ queryKey: ['evidence'] })
                    break
                case 'analysis:job_046':
                    // Analysis progress — update cached status
                    queryClient.setQueryData(['analysis', event.data.jobId], event.data)
                    break
            }
        })

        return () => ws.disconnect()
    }, [])
}
```

---

## Optimistic Updates

For user actions that should feel instant (dismiss insight, acknowledge alert), the UI updates the cache optimistically:

```typescript
const mutation = useMutation({
    mutationFn: (id: string) => api.insights.updateStatus(id, 'dismissed'),
    onMutate: async (id) => {
        // Cancel outgoing refetches
        await queryClient.cancelQueries({ queryKey: ['insights', id] })
        
        // Snapshot previous value
        const previous = queryClient.getQueryData(['insights', id])
        
        // Optimistically update
        queryClient.setQueryData(['insights', id], (old: Insight) => ({
            ...old,
            status: 'dismissed',
        }))
        
        return { previous }
    },
    onError: (err, id, context) => {
        // Rollback on error
        queryClient.setQueryData(['insights', id], context?.previous)
    },
    onSettled: () => {
        // Refetch to ensure consistency
        queryClient.invalidateQueries({ queryKey: ['insights'] })
    },
})
```

---

## Offline State

When the API Gateway becomes unreachable:

1. React Query queries enter `error` state.
2. Components show cached data (if available) with a "offline" indicator.
3. Mutations are paused (React Query default).
4. When connection restores, React Query refetches stale queries and replays paused mutations.
5. WebSocket automatically reconnects (Phase 6/04 reconnection protocol).
6. Zustand stores remain fully functional (client state only).

---

## Edge Cases

### Stale Data After Long Inactivity

If the user leaves the tab open overnight, all React Query data is stale. On return:
1. `refetchOnWindowFocus` triggers refetches for all active queries.
2. UI shows cached data with a subtle "refreshing..." indicator.
3. As new data arrives, components update seamlessly.

### Concurrent Tab Edits

In V2+ (team mode), two users might update the same insight status. The last write wins. React Query's `invalidateQueries` on WebSocket event ensures both tabs converge to the latest state.

### Rapid Filter Changes

When a user rapidly changes filters (e.g., clicking severities), the previous query is cancelled:

```typescript
useInsights({ severity: ['high', 'critical'] })
// User immediately switches filter →
useInsights({ severity: ['low'] })
// Previous query is automatically cancelled by React Query
```
