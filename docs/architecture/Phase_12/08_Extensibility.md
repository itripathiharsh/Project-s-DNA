================================================================================
# 08 Extensibility
================================================================================

# Extensibility

## Purpose

Project DNA is designed to be extended at every layer — custom engines, new evidence sources, third-party integrations, and plugin-based UI components.

---

## Extension Points

| Layer | Extension Point | What It Enables |
|---|---|---|
| SCM | Custom data source | Index non-Git codebases, databases, documentation |
| Engine | Custom engine | Domain-specific analysis (security, compliance) |
| Reasoning | Custom prompt template | Tailored reasoning for specific domains |
| API | Webhook receiver | Trigger analysis from external tools |
| UI | Dashboard plugin | Custom visualizations and metrics |
| CLI | Custom command | Team-specific automation workflows |

## Plugin Architecture

```python
# A custom engine plugin
from dna.plugins import EnginePlugin

class SecurityAuditEngine(EnginePlugin):
    name = "security_audit"
    version = "1.0.0"
    
    def analyze(self, scm: SCMClient) -> List[Evidence]:
        """Find security-relevant evidence."""
        evidence = []
        for file in scm.files("*.py"):
            # Detect use of dangerous functions
            if "eval(" in file.content:
                evidence.append(Evidence(
                    type="security_issue",
                    severity="high",
                    location=file.path,
                    snippet="eval() usage detected"
                ))
        return evidence
```

## Plugin Registration

```python
# In dna_plugins.toml
[plugins.security_audit]
path = "security_audit.py"
enabled = true
engines = ["security"]
```

## Extensibility Principles

| Principle | Rationale |
|---|---|
| Stable ABI | Plugins compiled against stable API don't break on DNA updates |
| Sandboxed | Plugins run in isolated context (WebAssembly or subprocess) |
| Versioned | Plugin manifest declares compatible DNA version range |
| Discoverable | Plugin registry for community-contributed plugins (V3) |
