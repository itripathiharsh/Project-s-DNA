================================================================================
# 01 Deployment Overview
================================================================================

# Deployment Overview

## Purpose

Project DNA is designed to run on the user's machine with zero infrastructure dependencies. Deployment is synonymous with installation — there is no server to provision, no database to configure, no cloud to connect. This document defines the deployment model, distribution channels, and the transition from local to team deployment.

---

## Deployment Models

| Model | V1 | V2+ |
|---|---|---|
| **Local** | ✅ Default | ✅ Supported |
| **Team (LAN)** | ❌ | ✅ |
| **Team (WAN)** | ❌ | ✅ (with auth) |

### Local (V1)

```
User Machine
├── dna serve         # API Gateway + SCM + Engines + Reasoning
├── dna ui            # Frontend (browser or Tauri window)
└── ollama serve      # Local LLM (separate process)
```

### Team (V2+)

```
Server Machine (LAN/WAN)
├── dna serve --host 0.0.0.0  # API Gateway + all services
├── ollama serve               # Shared LLM
└── PostgreSQL (optional)      # Shared SCM storage

Client Machines
├── dna ui --remote http://server:8000  # Browser access
└── dna config set server http://server:8000
```

## Distribution Channels

| Channel | Artifact | Users |
|---|---|---|
| npm | `dna` CLI | Developers, CI/CD |
| Tauri | `.msi` / `.dmg` / `.AppImage` | Desktop users |
| Docker | `dna-server` image | Server deployments |
| Homebrew (V2) | `brew install dna` | macOS users |

## Installation Requirements

| Component | Requirement |
|---|---|
| Operating System | macOS 12+, Windows 10+, Linux (glibc 2.28+) |
| RAM | 8 GB minimum, 16 GB recommended |
| Disk | 500 MB (app) + 4 GB (LLM models) |
| Ollama | Required for AI reasoning |
| Python | Not required (distributed as binary or container) |
| Node.js | 18+ (CLI only) |
