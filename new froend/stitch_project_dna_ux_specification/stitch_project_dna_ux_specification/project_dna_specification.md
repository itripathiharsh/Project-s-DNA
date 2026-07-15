# Project DNA: UX & Product Specification
**Software Cognition Platform**

Project DNA is a production-grade engineering tool designed to transform source code into a navigable knowledge graph. It provides deep visibility into repository structure, evolution, and risks, serving as a "Control Plane" for software architecture.

---

## 1. Product Vision
### The Core Problem
Modern software systems are too complex to keep in a single human head. Knowledge is fragmented across Git history, dependency trees, and tribal knowledge. 

### User Goals
*   **Architects:** Understand structural integrity and technical debt.
*   **Tech Leads:** Manage "Bus Factor" and knowledge distribution.
*   **Engineering Managers:** Identify hotspots, risk areas, and team velocity blockers.
*   **CTOs:** Get a high-level view of portfolio health and strategic technical risk.

### Primary Personas
*   **The Explorer:** Digging into a new codebase to understand dependencies.
*   **The Auditor:** Identifying security risks, license compliance, or architectural drift.
*   **The Optimizer:** Looking for refactoring candidates and dead code.

---

## 2. Navigation Architecture
The navigation is designed for speed, density, and keyboard-first interaction, mirroring the efficiency of **VS Code** or **Linear**.

### Global Sidebar (Left)
*   **Project Switcher:** Top-level dropdown for multi-repo or workspace selection.
*   **Primary Workspaces:** 
    *   `Dashboard` (Cmd+1)
    *   `Explorer` (Cmd+2)
    *   `Graph` (Cmd+3)
    *   `Intelligence` (Cmd+4)
    *   `Risk Center` (Cmd+5)
*   **Secondary Workspaces:**
    *   `Knowledge`
    *   `Evolution`
*   **Bottom Utility:**
    *   `Search` (/)
    *   `Settings` (Cmd+,)
    *   `Profile/Status`

### Contextual Navigation
*   **Breadcrumbs:** Global header showing `Project > Branch > Folder > File`.
*   **Tabs:** Persistent workspace tabs for multi-tasking (e.g., comparing two branches).
*   **Command Palette:** (Cmd+K) The "brain" of the app. Universal access to any file, symbol, or action.

---

## 3. Workspace Architecture
Every workspace follows a standard **Layout Pattern**:
`[Sidebar/Tree] + [Main Canvas/Stage] + [Inspector Panel (Right)]`

### Workspace States
*   **Loading:** High-fidelity skeletons (not spinners) matching component geometry.
*   **Empty:** Actionable prompts (e.g., "Select a folder to begin analysis").
*   **Error:** Specific technical logs with a "Retry" or "Re-scan" action.
*   **Success:** Subtle toast notifications for background scan completions.

---

## 4. Detailed Screen Inventory
1.  **Dashboard (Overview):** Strategic KPIs and health signals.
2.  **Repo Explorer:** High-density file/symbol tree with metadata overlays.
3.  **Graph Stage:** Infinite-canvas visualization of the project's knowledge graph.
4.  **Intelligence Center:** Feed of automated insights and architectural recommendations.
5.  **Risk Center:** Categorized alerts for technical debt, security, and complexity.
6.  **Knowledge Map:** Ownership heatmaps and contribution distribution.
7.  **Evolution Timeline:** Visual history of code growth and structural changes.
8.  **Search Overlay:** Full-screen modal for deep symbol and semantic search.

---

## 5. Component Inventory
### Core UI
*   **High-Density Tables:** Support for sorting, filtering, and column pinning.
*   **Monospace Text Components:** For file paths and code snippets.
*   **Status Badges:** `Critical`, `High`, `Neutral`, `Healthy` with consistent color mapping.

### Specialized Components
*   **Graph Node:** Visual representation of a file/module/class with health indicators.
*   **Metric Sparklines:** Small inline charts for 7-day evolution trends.
*   **Knowledge Heatmap:** A grid-based visualization for author expertise.
*   **Bus Factor Widget:** A circular chart showing "Knowledge Silos."

---

## 6. Design System
### Typography
*   **UI:** Inter (San-Serif) - Clean, legible at small sizes.
*   **Code/Data:** JetBrains Mono - Monospaced for high-density data.

### Color Palette (The "DNA" Palette)
*   **Surface:** Deep charcoal (`#0D0D0D`) and matte grays.
*   **Accent:** "DNA Purple" (`#8B5CF6`) for primary actions.
*   **Signals:** Emerald (Healthy), Amber (Warning), Rose (Critical), Cyan (Info).

### Motion
*   **Spring-based:** Fast, snappy transitions (0.2s duration).
*   **Spatial Consistency:** New panels slide from the right; overlays scale from center.

---

## 7. Dashboard Design
The Dashboard is the **Executive Summary**.
*   **Total Cognitive Load:** A calculated score of project complexity.
*   **Structure Health:** Percentage of components adhering to architectural rules.
*   **Bus Factor Alert:** A card highlighting the most at-risk modules (low ownership).
*   **Recent Hotspots:** A "Heatmap" chart showing files with high churn and high complexity.

---

## 8. Repository Explorer
A professional tree view that goes beyond the file system.
*   **Metadata Columns:** Show "Coverage," "Complexity," and "Last Modified" inline.
*   **Virtual Scrolling:** Supports 100k+ nodes without lag.
*   **Quick Actions:** Hover-based icons for "View in Graph" or "Run Analysis."

---

## 9. Graph Workspace (Flagship)
An infinite canvas built for exploration.
*   **Rendering:** WebGL-based for 10k+ nodes.
*   **Force-Directed Layout:** Automatically clusters related modules.
*   **Clustering:** Collapse folders into single nodes to view high-level architecture.
*   **Inspector:** Click a node to see its dependency depth, callers, and callees.

---

## 10. Intelligence Workspace
Automated reasoning based on the knowledge graph.
*   **Insight Cards:** e.g., "Circular Dependency Detected between A and B."
*   **Evidence:** Click to see the exact lines of code or Git history proving the insight.
*   **Confidence Score:** Percentage reflecting the system's certainty.

---

## 11. Risk Center
Focused strictly on what is **breaking**.
*   **Risk Score:** Aggregated from technical debt, security, and low bus factor.
*   **Prioritization:** Filter by "Impact on Release" or "Fix Difficulty."

---

## 12. Knowledge Workspace
Visualizing the **Human** side of the code.
*   **Ownership Map:** Color-coded by team/author.
*   **Silos:** Identifying code areas where only one developer has contributed in 12 months.

---

## 13. Evolution Workspace
The **Time Machine**.
*   **Timeline Slider:** Drag to see how the architecture grew over the last 2 years.
*   **Churn vs Complexity:** A scatter plot identifying the most dangerous "Debt" files.

---

## 14. Search Experience
*   **Semantic Search:** "Show me all modules related to authentication."
*   **Fuzzy Finding:** Instant results for filenames and symbols.

---

## 15. Settings
*   **Analysis Config:** Define "Ignore" patterns (node_modules, etc.).
*   **Rulesets:** Configure architectural rules (e.g., "Layer A cannot call Layer C").

---

## 16. User Journey
1.  **Ingest:** Connect GitHub/GitLab repo.
2.  **Analysis:** System builds the graph (background process).
3.  **Discovery:** User opens Dashboard, sees a "High Risk" alert on a core module.
4.  **Drill-down:** User clicks to Explorer, then "View in Graph" to see impact.
5.  **Action:** User exports a "Refactoring Plan" for the team.

---

## 17. Future Expansion
*   **DNA AI:** A sidebar assistant for natural language queries ("Where is the memory leak?").
*   **Cross-Repo Analysis:** Compare architecture across a whole microservices fleet.
*   **Live Sync:** Real-time updates as developers push code.
