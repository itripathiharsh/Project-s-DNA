================================================================================
# 04 Configuration
================================================================================

# Configuration

## Purpose

Project DNA is configured through a combination of config files, environment variables, and CLI flags. Configuration follows the principle of sensible defaults — most users need zero configuration.

---

## Configuration Sources

| Priority | Source | Format | Example |
|---|---|---|---|
| 1 (highest) | CLI flags | `--flag value` | `dna serve --port 9000` |
| 2 | Environment variables | `DNA_*` | `DNA_PORT=9000` |
| 3 | Config file | `dna.json` / `dna.yaml` | See below |
| 4 (lowest) | Defaults | Hardcoded | `port: 8000` |

## Config File

Location: `~/.config/dna/dna.json` (Linux/macOS) or `%APPDATA%/dna/dna.json` (Windows)

```jsonc
{
    "server": {
        "host": "127.0.0.1",
        "port": 8000,
        "workers": 4
    },
    "auth": {
        "mode": "local",
        "jwt_secret": "",  // Auto-generated if empty
        "api_keys": []
    },
    "scm": {
        "storage": {
            "type": "sqlite",          // sqlite | postgresql
            "path": "~/.dna/scm.db"    // SQLite only
        }
    },
    "llm": {
        "model": "llama3.1:8b-q4_K_M",
        "fallback_model": "llama3.2:3b-q4_K_M",
        "ollama_host": "http://localhost:11434",
        "temperature": 0.2
    },
    "logging": {
        "level": "info",
        "file": "~/.dna/logs/dna.log"
    }
}
```

## Environment Variables

| Variable | Maps To | Default |
|---|---|---|
| `DNA_HOST` | server.host | `127.0.0.1` |
| `DNA_PORT` | server.port | `8000` |
| `DNA_AUTH_MODE` | auth.mode | `local` |
| `DNA_SCM_TYPE` | scm.storage.type | `sqlite` |
| `DNA_LLM_MODEL` | llm.model | `llama3.1:8b-q4_K_M` |
| `DNA_LLM_OLLAMA_HOST` | llm.ollama_host | `http://localhost:11434` |
| `DNA_LOG_LEVEL` | logging.level | `info` |
