# 📖 Project DNA - User & Feature Navigation Guide

This guide details how to launch Project DNA, configure your workspace, and utilize every screen to audit your codebase's architecture.

---

## 🛠️ Step-by-Step Installation & Launch

### 1. Backend Server Setup
The backend utilizes FastAPI to serve REST endpoints and manage local database persistence.

1. Navigate to the project root directory.
2. Install python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Spin up the FastAPI server on port `8000`:
   ```bash
   python -m uvicorn dna.api.app:app --host 0.0.0.0 --port 8000 --reload
   ```
   *Note: Interactive Swagger API reference will be served at `http://localhost:8000/docs`.*

### 2. Frontend Development Setup
The frontend is a Vite-based React SPA built around a premium obsidian carbon theme.

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install node dependencies:
   ```bash
   npm install
   ```
3. Run the hot-reloading dev server:
   ```bash
   npm run dev
   ```
4. Access the web interface at `http://localhost:5173`.

---

## 🖥️ Screen-by-Screen Navigation

### 1. Onboarding & Analysis Configuration
* **Select Repository**: Input an absolute local path (e.g. `F:\code\my-project`) or a remote GitHub URL.
* **Configure Ruleset**: Choose your target engineering standard:
  * *Clean Architecture*: Strict layer isolation.
  * *Microservices*: Service-to-service decoupled boundaries.
  * *Modular Monolith*: Component encapsulation.
* **Filter Setup**: View glob include/exclude filters (e.g. ignoring `node_modules/` or test suites).
* **Launch**: Click **Start Analysis** to kick off AST parsing and history mining in real time.

### 2. Main Dashboard
* Shows aggregated project metrics: **Total Files**, **Source Files**, **Mined Git Commits**, and **Overall Risk Score**.
* Displays a codebase health graph and automated recommendations from the reasoning engines.

### 3. Risk Center (Complexity Hotspots)
* Renders the **Complexity Hotspots list**, identifying source files containing high functional densities or high change velocity.
* **Explainability Drilldown**: Click on any hotspot file to expand AI-generated breakdowns showing *Architectural Problems* (e.g. circular dependency risk) and *Remediation Paths* (decoupling methods).

### 4. Dependency Graph Workspace
* A force-directed 2D node-link diagram showing importing relations between files.
* Nodes are colored by kind (files, classes, modules), helping you spot cycles, god classes, and tight coupling instantly.

### 5. Repository Explorer
* Browse files and directories in your codebase.
* Select any source file to inspect its parsed Abstract Syntax Tree symbols, declarations, lines, and metadata.

### 6. Team Audits & Code Reviews
* Create collaborative reviews for structural patterns.
* Assign team members and list target files.
* **Active Review Dashboard**: Open any review to comment on structural targets and change status (`open`, `merged`, `closed`).
* Audits are stored in SQLite and persist after server reloads.

### 7. Refactoring Executions
* **Roadmap**: Displays planned refactoring tasks.
* **Pipeline**: Execute change steps sequentially, tracking status logs (running, success, failed) in real time.
* **Verification (Diffs)**: Inspect side-by-side versions of files before/after refactoring to measure complexity reduction score changes.

### 8. DNA AI Assistant
* Input queries like:
  * *"What structural risks exist in this codebase?"*
  * *"Show me the most complex files."*
  * *"Who are the top contributors?"*
* Responses are resolved deterministically against the databases without sending code payloads to external LLM servers.

### 9. Organization Admin
* Manage your team rosters.
* Add, edit, or delete engineering groups (e.g. Platform Engineering, Security team) and assign roles.

---

## 💾 Storage & Persistence Mechanisms

Project DNA uses 3 separate storage targets in your project workspace:
1. `dna_system.db` (SQLite): Configs, teams, reviews, notification logs, settings.
2. `sc_store.db` (SQLite): Parsed AST entities, import relations, files.
3. `ev_store.db` (SQLite): Metrics evidence facts, logic reasoning insights.
4. `latest_analysis.json`: Cached copy of the last generated analysis response data.
