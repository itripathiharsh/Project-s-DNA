================================================================================
# 08 Documentation Standards
================================================================================

# Documentation Standards

## Purpose

Consistent documentation enables engineers to find, understand, and trust the information they need. This document defines the standards for all Project DNA documentation.

---

## Document Types

| Type | Location | Format | Purpose |
|---|---|---|---|
| Phase docs | `docs/Phase_*/` | Markdown | Architecture, design, specification |
| Code docs | In-source | Docstrings | API reference, module purpose |
| README | Root, per-module | Markdown | Getting started, overview |
| ADRs | `docs/adr/` | Markdown | Architecture decisions |
| Runbooks | `docs/operations/` | Markdown | Operational procedures |
| AI prompts | `prompts/` | Markdown | Agent instructions |

## Markdown Standards

| Element | Standard |
|---|---|
| Heading 1 | Document title only |
| Heading 2 | Major sections |
| Heading 3 | Sub-sections |
| Code blocks | Language-annotated triple backticks |
| Tables | GitHub-flavored markdown |
| Line breaks | Single newline between paragraphs |
| File names | `Snake_Case.md` for phase docs |

## Docstrings

### Python (Google style)

```python
def get_evidence(entity_id: str, limit: int = 20) -> list[EvidenceNode]:
    """Retrieve evidence nodes for a given entity.

    Args:
        entity_id: The SCM entity ID to fetch evidence for.
        limit: Maximum number of evidence nodes to return.

    Returns:
        A list of EvidenceNode objects, ordered by recency.

    Raises:
        ValueError: If entity_id is empty.
    """
```

### TypeScript (JSDoc)

```typescript
/** Retrieves evidence nodes for a given entity.
 * @param entityId - The SCM entity ID to fetch evidence for.
 * @param limit - Maximum number of evidence nodes to return.
 * @returns A list of EvidenceNode objects, ordered by recency.
 */
export async function getEvidence(entityId: string, limit = 20): Promise<EvidenceNode[]> {
```

### Rust (rustdoc)

```rust
/// Retrieves evidence nodes for a given entity.
///
/// # Arguments
/// * `entity_id` - The SCM entity ID to fetch evidence for.
/// * `limit` - Maximum number of evidence nodes to return.
///
/// # Returns
/// A vector of EvidenceNode objects, ordered by recency.
///
/// # Errors
/// Returns `EngineError::NotFound` if the entity has no evidence.
pub fn get_evidence(entity_id: &str, limit: usize) -> Result<Vec<EvidenceNode>, EngineError> {
```
