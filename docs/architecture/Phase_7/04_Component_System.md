================================================================================
# 04 Component System
================================================================================

# Component System

## Purpose

The component system defines how UI components are structured, named, composed, and reused across the frontend. It establishes a consistent hierarchy from primitive UI elements to composite feature components, ensuring maintainability, testability, and visual consistency.

---

## Scope

### In Scope

- Component classification (primitive → domain → feature → page)
- Naming conventions
- UI primitive catalog
- Composition patterns
- Slot-based component design
- Styling approach (Tailwind CSS)
- Accessibility requirements per component type

### Out of Scope

- State management integration (Phase 7/03)
- Graph visualization components (Phase 7/05)
- Search UI components (Phase 7/06)
- Evidence Explorer components (Phase 7/07)
- Dashboard components (Phase 7/08)

---

## Background

Phase 2 established React 18 + TypeScript + Tailwind CSS as the frontend technology stack. Phase 7/02 defined the directory structure with `components/ui/` (primitives), `components/` (domain), and `pages/` (route-level).

---

## Component Classification

| Level | Category | Examples | Can Import From |
|---|---|---|---|
| 1 | **Primitive** | Button, Input, Card, Badge, Tooltip | Nothing UI-related |
| 2 | **Domain** | InsightCard, EvidenceRow, EntityBadge, SearchResult | Primitives |
| 3 | **Feature** | InsightList, EvidenceExplorer, DependencyGraph | Domain + Primitives |
| 4 | **Page** | Dashboard, RepositoryDetail, SearchResults | Features + Domain |
| 5 | **Shell** | Header, Sidebar, StatusBar, Layout | Primitives |

### Dependency Flow

```
Page → Feature → Domain → Primitive
  │        │        │        │
  └────────┴────────┴────────┴──→ lib/, types/
```

A primitive never imports a domain component. A page never imports another page.

---

## Naming Conventions

| Convention | Example | Applies To |
|---|---|---|
| `PascalCase` | `InsightCard.tsx` | All components |
| `.tsx` extension | `Button.tsx` | All components |
| `index.ts` barrel | `components/ui/index.ts` | Module exports |
| Suffix by type | `Button.tsx`, `SearchBar.tsx`, `EntityList.tsx` | Reflects purpose |
| No `Component` suffix | ~~`ButtonComponent.tsx`~~ | Redundant |

### Prop Naming

```typescript
// boolean props: is/has/shows prefix
interface CardProps {
    isSelected: boolean
    hasError: boolean
    showsDetail: boolean
}

// event handlers: on prefix
interface ButtonProps {
    onClick: () => void
    onHover?: (isHovered: boolean) => void
}

// data props: noun or noun phrase
interface InsightCardProps {
    insight: Insight
    showEvidenceCount?: boolean
}
```

---

## UI Primitive Catalog

### Visual Primitives

| Component | Props | Description |
|---|---|---|
| `Button` | variant, size, isLoading, disabled, icon, children | Primary, secondary, ghost, danger variants |
| `Input` | type, value, onChange, placeholder, error, icon | Text input with icon and error state |
| `Select` | options, value, onChange, placeholder | Dropdown select |
| `Badge` | variant, size, children | Severity/status badge (red for CRITICAL, yellow for HIGH, etc.) |
| `Card` | variant, padding, isSelected, onClick, children | Container with shadow and border |
| `Modal` | isOpen, onClose, title, size, children | Overlay dialog with backdrop |
| `Tooltip` | content, position, children | Hover tooltip |
| `Spinner` | size, label | Loading indicator with optional text |
| `Skeleton` | width, height, variant | Content placeholder during loading |
| `EmptyState` | icon, title, description, action | Empty state with illustration and CTA |
| `ErrorState` | error, onRetry | Error state with message and retry button |

### Layout Primitives

| Component | Props | Description |
|---|---|---|
| `Stack` | direction, gap, align, wrap | Flex layout container |
| `Grid` | columns, gap, minChildWidth | CSS grid layout |
| `Divider` | orientation, label | Horizontal or vertical divider |
| `Tabs` | tabs, activeTab, onChange | Tab navigation |
| `Breadcrumbs` | items, separator | Breadcrumb navigation |
| `Pagination` | page, totalPages, onChange | Page navigation |

---

## Domain Components

Domain components combine primitives to represent specific data types:

| Component | Props | Composes |
|---|---|---|
| `InsightCard` | insight, onStatusChange | Card, Badge, Button, Stack |
| `EvidenceRow` | evidence, isExpanded | Card, Badge, Text |
| `EntityBadge` | entity, onClick | Badge, Tooltip |
| `SeverityIndicator` | severity | Badge (color-coded) |
| `ConfidenceBar` | confidence | Progress bar with label |
| `EvidenceChain` | chain | Stack, EvidenceRow, Arrow |
| `RecommendationCard` | recommendation, onApply | Card, Badge, Button, Stack |
| `TokenStream` | tokens, isStreaming | Animated text display |

---

## Slot-Based Composition

Components use React's `children` prop for flexible composition:

```typescript
// Card with header, body, footer slots
interface CardProps {
    header?: ReactNode
    children: ReactNode
    footer?: ReactNode
    isSelected?: boolean
    onClick?: () => void
}

// Usage
<Card
    header={<CardHeader insight={insight} />}
    footer={<CardFooter onAction={handleAction} />}
>
    <InsightSummary insight={insight} />
</Card>
```

---

## Styling Approach

All styling uses Tailwind CSS utility classes. No CSS modules or styled-components.

```typescript
// Primitive components accept className for customization
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
    size?: 'sm' | 'md' | 'lg'
}

function Button({ variant = 'primary', size = 'md', className, ...props }: ButtonProps) {
    const base = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2'
    const variants = {
        primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
        secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500',
        ghost: 'hover:bg-gray-100 focus:ring-gray-500',
        danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    }
    const sizes = {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
    }
    
    return (
        <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...props} />
    )
}
```

---

## Accessibility

| Requirement | Implementation |
|---|---|
| Keyboard navigation | All interactive elements reachable and activatable via keyboard |
| Focus management | Focus trap in modals. Focus restoration on close. |
| ARIA labels | `aria-label` on icon-only buttons. `aria-describedby` on error messages. |
| Color contrast | WCAG AAA for text (7:1), AA for large text (4.5:1) |
| Screen reader | Live regions for streaming tokens. Status announcements for loading. |
| Reduced motion | `prefers-reduced-motion` disables animations |

---

## Edge Cases

### Empty List

When a list has no items, render `EmptyState` with contextual message:

```
No insights found for this entity.
[Run Analysis] [Adjust Filters]
```

### Loading State

Every data-dependent component shows a skeleton matching its layout:

```
<InsightCard />
→ <Skeleton variant="card" width={400} height={120} />
```

### Error State

When a query fails, show `ErrorState` with retry option:

```
Failed to load insights.
[Retry]
```

### Extremely Long Text

Evidence values or insight summaries may be very long:

| Strategy | Implementation |
|---|---|
| Truncation | CSS `line-clamp-3` for cards. Full text on detail page. |
| Expand | "Show more" / "Show less" toggle for long text. |
| Scroll | Fixed-height container with overflow scroll for code blocks. |
