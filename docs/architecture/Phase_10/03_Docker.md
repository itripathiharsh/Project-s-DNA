================================================================================
# 03 Docker
================================================================================

# Docker

## Purpose

Docker provides a consistent, isolated environment for running the Project DNA server, suitable for team deployments, CI/CD pipelines, and users who prefer containerized applications.

---

## Images

| Image | Base | Contents | Size |
|---|---|---|---|
| `project-dna/dna-server:latest` | python:3.11-slim | API Gateway + SCM + Engines + Reasoning | ~500 MB |
| `project-dna/dna-server:full` | python:3.11 + cuda | Includes CUDA runtime for GPU inference | ~3 GB |
| `project-dna/dna-server:minimal` | alpine:3.19 | API Gateway only (no engines — remote SCM) | ~200 MB |

## Usage

```bash
# Basic — local-only mode
docker run -d \
    --name dna \
    -p 8000:8000 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    project-dna/dna-server:latest

# With GPU support
docker run -d \
    --name dna \
    --gpus all \
    -p 8000:8000 \
    -v dna-data:/data \
    project-dna/dna-server:full

# With external Ollama
docker run -d \
    --name dna \
    -p 8000:8000 \
    -e OLLAMA_HOST=http://host.docker.internal:11434 \
    project-dna/dna-server:latest
```

## Volumes

| Mount | Purpose |
|---|---|
| `/data` | SCM database, model cache, config |
| `/repos` | Repository access (bind mount) |
| `/var/run/docker.sock` | Docker socket for repo access |

## docker-compose

```yaml
version: '3.8'
services:
  dna-server:
    image: project-dna/dna-server:latest
    ports:
      - "8000:8000"
    volumes:
      - dna-data:/data
      - ./repos:/repos
    environment:
      - DNA_AUTH_MODE=local
      - DNA_LOG_LEVEL=info

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama-models:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  dna-data:
  ollama-models:
```
