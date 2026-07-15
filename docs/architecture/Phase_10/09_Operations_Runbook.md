================================================================================
# 09 Operations Runbook
================================================================================

# Operations Runbook

## Purpose

The runbook documents common operational procedures. It is the go-to reference for startup, shutdown, troubleshooting, and recovery.

---

## Startup

```bash
# 1. Start Ollama (if using local LLM)
ollama serve

# 2. Start DNA server
dna serve

# 3. Verify health
dna health
# Expected: { "status": "healthy", ... }

# 4. Open UI (optional)
dna ui
```

## Shutdown

```bash
# Graceful shutdown
kill -SIGTERM $(pidof dna)
# or Ctrl+C if running in foreground

# Verify shutdown
dna health  # → Error: connection refused
```

## Common Procedures

### Restart ALL Services

```bash
dna stop
dna start
```

### Reset Everything

```bash
dna backup create --output ./pre-reset-backup.tar.gz
dna reset --all
dna start
```

---

## Troubleshooting

### Problem: Server Won't Start

```
Error: Address already in use
```
→ Port 8000 is occupied. Use `dna serve --port 8001` or `netstat -ano | findstr :8000` to find the process.

```
Error: Ollama connection refused
```
→ Ollama is not running. Start with `ollama serve`. Verify with `curl http://localhost:11434`.

### Problem: Slow Queries

```
Query took 30s (expected < 5s)
```
→ Check system resources (CPU, RAM). Restart Ollama. Verify no other LLM is consuming resources.

### Problem: Insight Quality Degraded

→ Check which model is loaded: `dna config get llm.model`
→ Verify model is not being throttled: `dna health` (check Ollama latency)
→ Fallback to smaller model if resource constrained: `dna config set llm.model llama3.2:3b-q4_K_M`

### Problem: Disk Space Low

```bash
# Check data size
du -sh ~/.dna

# Clear analysis cache
dna cache clear --analysis

# Clear all cache (except database)
dna cache clear --all

# List backups to remove
ls ~/.dna/backups/
```
