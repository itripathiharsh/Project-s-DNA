================================================================================
# 02 Local Installation
================================================================================

# Local Installation

## Purpose

Local installation is the primary way users get started with Project DNA. The process must be fast, reliable, and require no external dependencies beyond what the installation method provides.

---

## Install Methods

### npm (Recommended)

```bash
# Install globally
npm install -g @project-dna/cli

# Verify installation
dna --version

# Start the server
dna serve

# Open the UI (in another terminal)
dna ui
```

### Tauri Desktop App

```bash
# Download the latest release
# https://github.com/project-dna/dna/releases

# macOS
open ProjectDNA-x64.dmg

# Windows
ProjectDNA-Setup-x64.msi

# Linux
chmod +x ProjectDNA-x86_64.AppImage
./ProjectDNA-x86_64.AppImage
```

### Docker

```bash
# Pull and run
docker run -d \
    --name dna-server \
    -p 8000:8000 \
    -v dna-data:/data \
    -v /path/to/repos:/repos \
    project-dna/dna-server:latest
```

## Post-Install

### First Run

1. Start the server: `dna serve`
2. Open the UI: `http://localhost:8000`
3. Import a repository: Provide a local path or clone URL
4. Run analysis: The system begins analyzing the repository
5. Download LLM model (prompted): `ollama pull llama3.1:8b-q4_K_M`

### Verify Installation

```bash
dna health
# → { "status": "healthy", "version": "1.0.0", "services": { ... } }

# Run a test query
dna query "What modules are in this repository?"
```

## Troubleshooting

| Problem | Likely Cause | Solution |
|---|---|---|
| `dna: command not found` | npm global path not in PATH | `export PATH=$(npm bin -g):$PATH` |
| Server won't start | Port 8000 in use | `dna serve --port 8001` |
| Ollama not found | Not installed | `brew install ollama` or download from ollama.ai |
| Model not found | Not pulled | Run `ollama pull llama3.1:8b-q4_K_M` |
