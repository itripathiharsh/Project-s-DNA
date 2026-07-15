================================================================================
# 03 Project Structure
================================================================================

# Project Structure

## Purpose

A consistent, predictable directory structure across all Project DNA repositories enables engineers to find code, understand module boundaries, and navigate the codebase without ceremony.

---

## Monorepo Structure

```
dna/                          # Root
├── docs/                     # Phase documentation
├── prompts/                  # AI agent prompts, generation rules
├── roadmap/                  # PHASE_PLAN.md
├── TODO.md
├── README.md
│
├── engine/                   # Language-dependent runtime
├── scm/                      # SCM storage implementation
├── reasoning/                # Reasoning layer implementation
├── api/                      # API Gateway
├── ui/                       # Frontend application
├── cli/                      # CLI tool
│
├── tests/                    # Cross-module integration tests
├── scripts/                  # Build, release, utility scripts
├── docker/                   # Docker configurations
│
├── .github/                  # CI/CD workflows
├── .vscode/                  # Editor settings
├── .gitignore
├── .pre-commit-config.yaml
├── ruff.toml
├── tsconfig.json
├── package.json
└── Cargo.toml
```

## Module Layout

| Directory | Language | Purpose |
|---|---|---|
| `engine/` | Python / Rust | Cognitive Engine implementations |
| `scm/` | Python | SCM storage, query interface |
| `reasoning/` | Python | Reasoning pipeline, prompt management |
| `api/` | Python (FastAPI) | API Gateway |
| `ui/` | TypeScript (React) | Frontend SPA |
| `cli/` | TypeScript (Node.js) | CLI tool |
| `tests/` | Mixed | Integration and e2e tests |
