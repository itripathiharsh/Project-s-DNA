================================================================================
# 02 Coding Standards
================================================================================

# Coding Standards

## Purpose

Consistent code style across the Project DNA codebase reduces cognitive overhead during code review, makes code predictable to read, and prevents entire categories of bugs through disciplined patterns. This document defines the mandatory coding standards for all Python, TypeScript, and Rust code in the project.

---

## Scope

### In Scope

- Language-specific standards (Python, TypeScript, Rust)
- Naming conventions
- File and module organization
- Error handling patterns
- Type annotations and documentation
- Code formatting rules
- Linting and static analysis configuration

### Out of Scope

- Architecture patterns (Phase 8/01)
- Git workflow (Phase 8/04)
- Code review process (Phase 8/06)

---

## General Standards (All Languages)

| Rule | Standard |
|---|---|
| Line length | 100 characters max |
| Indentation | 4 spaces (no tabs) |
| Encoding | UTF-8 |
| Newlines | LF (Unix) — `.gitattributes` handles conversion |
| Trailing whitespace | None — trimmed by formatter |
| Final newline | Always — one blank line at end of file |

### Comment Policy

- Comments explain *why*, not *what*. The code itself documents *what*.
- No commented-out code. Delete it. Git history preserves it.
- TODO comments must include a ticket reference: `// TODO(PROJ-123): handle edge case`
- No block comments for license headers (single-line is sufficient).

---

## Python Standards

### Version and Tooling

| Tool | Standard |
|---|---|
| Python version | 3.11+ |
| Formatter | Ruff (format) |
| Linter | Ruff (lint) — all rules enabled |
| Type checker | mypy — strict mode |
| Import sorting | Ruff (isort rules) |

### Naming

| Element | Convention | Example |
|---|---|---|
| Modules | `snake_case` | `evidence_store.py` |
| Classes | `PascalCase` | `EvidenceNode` |
| Functions | `snake_case` | `get_evidence_by_entity()` |
| Variables | `snake_case` | `evidence_count` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_EVIDENCE_ITEMS` |
| Private | `_prefix` | `_validate_schema()` |
| Type vars | `PascalCase` | `T`, `EngineResult` |

### Typing

```python
# All functions must have type annotations
def get_evidence(entity_id: str, limit: int = 20) -> list[EvidenceNode]:
    ...

# Use Optional explicitly, not default None without type
def find_entity(name: str, type_filter: str | None = None) -> Entity | None:
    ...

# Prefer explicit union over Optional
# Good
def get_insight(id: str) -> Insight | None: ...
# Avoid
def get_insight(id: str) -> Optional[Insight]: ...
```

### Error Handling

```python
# Use custom exception types for domain errors
class EvidenceNotFoundError(DomainError):
    def __init__(self, entity_id: str) -> None:
        super().__init__(f"Evidence not found for entity: {entity_id}")
        self.entity_id = entity_id

# Raise early, catch at boundaries
def get_evidence(entity_id: str) -> list[EvidenceNode]:
    if not entity_id:
        raise ValueError("entity_id must not be empty")
    ...

# No bare except clauses
try:
    result = engine.run(repository)
except TimeoutError:
    logger.warning("Engine timed out, falling back to cached data")
    result = get_cached_result(repository)
```

### Imports

```python
# Standard library
import json
from collections.abc import Sequence

# Third-party
import click
from pydantic import BaseModel

# First-party
from dna.engines.base import CognitiveEngine
from dna.scm.models import EvidenceNode

# Conditional imports (inside function, with comment)
def get_visualization():
    import matplotlib.pyplot as plt  # Only for visualization
    ...
```

---

## TypeScript Standards

### Version and Tooling

| Tool | Standard |
|---|---|
| TypeScript version | 5.4+ |
| Formatter | Prettier (default config) |
| Linter | ESLint (flat config, strict rules) |
| Strict mode | `strict: true` in tsconfig |

### Naming

| Element | Convention | Example |
|---|---|---|
| Files | `PascalCase` (components), `camelCase` (hooks/utils) | `InsightCard.tsx`, `useWebSocket.ts` |
| Components | `PascalCase` | `InsightCard` |
| Hooks | `camelCase` with `use` prefix | `useInsights` |
| Functions | `camelCase` | `formatEvidenceValue` |
| Variables | `camelCase` | `evidenceCount` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Types/Interfaces | `PascalCase` | `InsightCardProps` |
| Enums | `PascalCase` | `SeverityLevel` |

### Typing

```typescript
// Prefer interfaces for objects
interface InsightCardProps {
    insight: Insight
    onStatusChange?: (status: InsightStatus) => void
    className?: string
}

// Prefer type for unions and primitives
type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'

// No `any` — use `unknown` and narrow
function parseResponse(data: unknown): ParsedInsight {
    if (typeof data !== 'object' || data === null) {
        throw new Error('Invalid response')
    }
    // ... narrow and validate
}

// Strict null checks enabled — no implicit `any`
function getEntityName(entity: Entity | null): string {
    return entity?.name ?? 'Unknown'
}
```

### Error Handling

```typescript
// Use result pattern for expected failures
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E }

function fetchEvidence(id: string): Promise<Result<EvidenceNode>> {
    try {
        const response = await api.get(`/v1/evidence/${id}`)
        return { ok: true, value: parseEvidence(response) }
    } catch (error) {
        return { ok: false, error: error as Error }
    }
}

// Use custom error classes for domain errors
class EntityNotFoundError extends Error {
    constructor(entityId: string) {
        super(`Entity not found: ${entityId}`)
        this.name = 'EntityNotFoundError'
    }
}
```

### React Component Standards

```typescript
// Functional components only
// Props interface defined above the component
interface ButtonProps {
    variant: 'primary' | 'secondary'
    children: ReactNode
    onClick?: () => void
}

// Default export for page components, named export for everything else
export function Button({ variant, children, onClick }: ButtonProps) {
    return (
        <button
            className={`btn btn-${variant}`}
            onClick={onClick}
        >
            {children}
        </button>
    )
}
```

---

## Rust Standards

### Version and Tooling

| Tool | Standard |
|---|---|
| Rust version | 1.75+ (latest stable) |
| Formatter | `rustfmt` (default config) |
| Linter | `clippy` — all warnings as errors |
| Documentation | `rustdoc` — all public items documented |

### Naming

| Element | Convention | Example |
|---|---|---|
| Files | `snake_case` | `evidence_store.rs` |
| Types | `PascalCase` | `EvidenceStore` |
| Traits | `PascalCase` | `CognitiveEngine` |
| Functions | `snake_case` | `get_evidence()` |
| Variables | `snake_case` | `evidence_count` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_BATCH_SIZE` |
| Macros | `snake_case` | `engine_impl!` |

### Error Handling

```rust
// Use thiserror for library errors
#[derive(Debug, thiserror::Error)]
pub enum EngineError {
    #[error("Evidence not found: {0}")]
    NotFound(String),
    #[error("Engine timed out after {0}s")]
    Timeout(u64),
    #[error(transparent)]
    Internal(#[from] anyhow::Error),
}

// Return Result, never panic
pub fn run_engine(repo: &Repository) -> Result<EngineResult, EngineError> {
    // ...
}

// Use anyhow for application-level errors
pub fn main() -> anyhow::Result<()> {
    let result = run_engine(&repo)?;
    Ok(())
}
```

---

## File Structure

### Python Module

```
engine/
├── __init__.py          # Public API re-exports
├── base.py              # Abstract base class
├── structural.py        # Implementation
└── tests/
    ├── __init__.py
    └── test_structural.py
```

### TypeScript Component

```
components/
├── InsightCard.tsx
├── InsightCard.test.tsx
└── InsightCard.stories.tsx (if using Storybook)
```

---

## Enforcement

| Check | Tool | Runs On |
|---|---|---|
| Format | Ruff / Prettier / rustfmt | Pre-commit, CI |
| Lint | Ruff / ESLint / clippy | Pre-commit, CI |
| Type check | mypy / tsc / cargo check | CI |
| Import sort | Ruff / Prettier | Pre-commit, CI |
| Line length | All formatters | Pre-commit, CI |
| Dead code | `vulture` (Python) / `ts-prune` (TS) | CI (weekly) |
