================================================================================
# 10 Glossary
================================================================================

# Glossary

## Purpose

This glossary defines key terms introduced across Phase 10 (Deployment & Operations).

---

## B

### Backup

A point-in-time snapshot of the SCM database, configuration, and model cache. Created with `dna backup create` and restored with `dna backup restore`. Retention: 30 daily, 12 weekly, 12 monthly. Defined in Phase 10/08.

---

## C

### CI/CD

Automated pipeline that runs linting, type checking, unit tests, integration tests, and builds on every push. Tagged releases trigger publication to npm, Docker Hub, and GitHub Releases. Defined in Phase 10/05.

### Configuration

Sourced from CLI flags (highest priority), environment variables, config file, and defaults (lowest). Config file at `~/.config/dna/dna.json` or `%APPDATA%/dna/dna.json`. Defined in Phase 10/04.

---

## D

### Deployment Model

How DNA is deployed. Local (default, single machine) or Team (V2+, LAN/WAN with shared server). Defined in Phase 10/01.

### Docker

Container images for running the DNA server. Three variants: `latest` (CPU), `full` (GPU/CUDA), `minimal` (API gateway only). Defined in Phase 10/03.

---

## H

### Health Endpoint

`GET /health` — Returns JSON with service status (healthy/degraded/unhealthy), uptime, version, and per-service latency. Used by monitoring and orchestrators. Defined in Phase 10/06.

---

## L

### Logging

Structured JSON lines written by `dna.api`, `dna.scm`, `dna.engine`, `dna.reasoning`, `dna.auth` loggers. Levels: ERROR, WARNING, INFO, DEBUG. Defined in Phase 10/07.

---

## R

### Runbook

Reference document for operational procedures: startup, shutdown, troubleshooting, reset. Defined in Phase 10/09.
