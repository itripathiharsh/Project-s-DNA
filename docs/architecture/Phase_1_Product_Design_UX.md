

================================================================================
# 01 User Journeys
================================================================================

# User Journeys

## How Users Experience Project DNA

This document maps the complete user journeys for Project DNA's primary personas. Every journey is grounded in the Jobs To Be Done (Phase 0) and the Product Principles (Phase 0). No implementation details. Only product behavior.

---

## Journey 1: Developer — Understanding Code Before Modifying It

**Persona:** Developer (Sarah)
**Job:** Understand code I did not write
**Trigger:** Assigned a bug in PaymentService

### Stage 1: Discovery (0-2 minutes)

Sarah opens Project DNA. She sees the main dashboard with a search bar at the top.

She types: "PaymentService"

The system responds immediately with:
- A summary card: "PaymentService — High complexity, frequently modified, single owner."
- A quick-actions row: [Overview] [Dependencies] [History] [Ownership] [Tests] [Risks]
- A visual preview: Mini dependency graph showing 3 downstream services.

### Stage 2: Orientation (2-5 minutes)

Sarah clicks [Overview].

She sees:
- **Purpose:** "PaymentService handles payment processing, retries, and webhook notifications."
- **Health indicators:** Complexity trend (upward), test coverage (42%, flat), change frequency (high).
- **Key insight:** "This module has grown 300% in 18 months while test coverage remained flat."
- **Warning:** "Bus factor: 1. Primary owner: Alex (73% of commits)."

She clicks [Show Evidence] on the complexity insight.

The evidence panel slides in from the right:
- Complexity graph: 12 → 28 over 18 months.
- Commit timeline: Major features added without corresponding tests.
- Ownership chart: Alex's contribution dominance.

### Stage 3: Deep Understanding (5-15 minutes)

Sarah clicks [Dependencies].

She sees an interactive graph:
- PaymentService at the center.
- 3 services connected: OrderService, NotificationService, AnalyticsService.
- Each connection shows: dependency type, change frequency, stability score.
- She hovers over OrderService: "OrderService calls PaymentService.processPayment() 47 times per day. Last change: 3 days ago."

She clicks [History].

A timeline appears:
- 18 months ago: Module created (complexity: 12).
- 14 months ago: Retry logic added (+8 complexity).
- 10 months ago: Webhook support added (+5 complexity).
- 6 months ago: Refactoring attempted but reverted.
- 2 months ago: Bug fix surge (+3 complexity, no tests).

She clicks [Risks].

Risk cards appear:
- **High:** "Complexity accelerating. No tests for retry logic."
- **Medium:** "Bus factor of 1. Alex on vacation next week."
- **Low:** "Dependency on AnalyticsService is stable."

### Stage 4: Decision (15-20 minutes)

Sarah clicks [What Should I Know Before Changing?]

Project DNA responds:
- "Before modifying PaymentService, understand the retry logic (lines 145-287). It is the most complex and least tested area."
- "Check with Alex before making structural changes. He designed the retry mechanism."
- "Run tests for OrderService and NotificationService after changes — they are the primary consumers."
- "Estimated understanding time: 2 hours with Project DNA. 2 days without."

Sarah feels confident. She bookmarks the analysis. She starts her bug fix.

### Emotional Arc
- **Start:** Anxious (unfamiliar code, high-stakes module).
- **Middle:** Curious (discovering history, understanding context).
- **End:** Confident (knows what to do, who to ask, what to test).

---

## Journey 2: Tech Lead — Making an Architecture Decision

**Persona:** Tech Lead (Marcus)
**Job:** Make confident architecture decisions
**Trigger:** Quarterly planning — should we split the payment service?

### Stage 1: Framing the Question (0-5 minutes)

Marcus opens Project DNA. He navigates to the Decision Cognition section.

He asks: "Should we split PaymentService into separate services?"

Project DNA presents a decision frame:
- **Context:** "PaymentService currently handles 4 domains: processing, retries, webhooks, and reconciliation."
- **Current State:** Complexity 28, 3 dependent services, bus factor 1.
- **Trend:** "Complexity has increased 133% in 18 months."

### Stage 2: Option Evaluation (5-20 minutes)

Project DNA presents 3 options:

**Option A: Split by Domain**
- **Pros:** Reduced complexity per service, independent deployability, parallel development.
- **Cons:** Network overhead, data consistency challenges, migration effort.
- **Evidence:** "Microservices pattern detected in 2 other services. They show 40% faster feature velocity post-split."
- **Confidence:** 82%
- **Effort:** 45 developer-days.
- **Risk:** Medium.

**Option B: Modularize Within Monolith**
- **Pros:** Lower operational overhead, no network latency, faster to implement.
- **Cons:** Does not solve deployment coupling, limited scalability.
- **Evidence:** "Clean Architecture pattern detected. Module extraction would align with existing conventions."
- **Confidence:** 76%
- **Effort:** 18 developer-days.
- **Risk:** Low.

**Option C: Leave As Is**
- **Pros:** No immediate effort, no disruption.
- **Cons:** Complexity will likely reach 40+ in 6 months. Feature velocity will decline further.
- **Evidence:** "Trend extrapolation: if current growth continues, complexity will be 42 in 6 months. 2 other services at this threshold became maintenance bottlenecks."
- **Confidence:** 91% (for prediction), 34% (for recommendation).
- **Effort:** 0 days.
- **Risk:** High (deferred).

Marcus clicks [Show Evidence] on Option A.

He sees:
- The 2 services that successfully split, with before/after metrics.
- The specific domain boundaries detected in PaymentService.
- The dependency graph showing how splits would reduce coupling.

### Stage 3: Stakeholder Communication (20-30 minutes)

Marcus clicks [Generate Report for Leadership].

Project DNA generates a one-page summary:
- **Problem:** PaymentService is becoming a bottleneck.
- **Options:** A, B, C with effort, risk, and confidence.
- **Recommendation:** Option B (modularize) as a pragmatic first step. Option A as a future phase.
- **Evidence:** 3 charts, 2 dependency graphs, 1 trend projection.
- **Next Steps:** Schedule 2-week spike to validate module boundaries.

Marcus exports the report as PDF. He presents it at the quarterly planning meeting.

### Emotional Arc
- **Start:** Uncertain (intuition says split, but no data to justify it).
- **Middle:** Analytical (evaluating options with evidence, comparing trade-offs).
- **End:** Confident (has evidence-backed recommendation, leadership-ready report).

---

## Journey 3: Engineering Manager — Identifying Team Risks

**Persona:** Engineering Manager (Priya)
**Job:** Identify and mitigate risks before they become critical
**Trigger:** Monthly engineering health review

### Stage 1: Overview (0-5 minutes)

Priya opens Project DNA. She navigates to the Team Health view.

She sees:
- **Team Velocity Trend:** Declining 15% over 3 months.
- **Knowledge Distribution:** 3 modules with bus factor 1.
- **Risk Forecast:** 2 modules will become critical bottlenecks within 4 months.
- **Alert:** "PaymentService owner (Alex) has no backup. Vacation scheduled next week."

### Stage 2: Investigation (5-15 minutes)

Priya clicks on the velocity decline.

Project DNA shows:
- **Root Cause:** "Architectural coupling in checkout flow increased 40%. Parallel development is now difficult."
- **Evidence:** Co-change analysis showing checkout modules are modified together 80% of the time.
- **Impact:** "Features touching checkout take 2.3x longer than average."

Priya clicks on Knowledge Distribution.

A team map appears:
- Each engineer is a node.
- Each module is a node.
- Connections show expertise (commit count, review participation, documentation authorship).
- **Alert:** Alex → PaymentService (thick line). No other engineer has significant connection.

### Stage 3: Action Planning (15-25 minutes)

Priya clicks [Generate Action Plan].

Project DNA suggests:
- **Immediate:** Pair Alex with Sarah on PaymentService for 2 weeks. Target: increase bus factor to 2.
- **Short-term:** Schedule architecture review for checkout flow. Target: reduce coupling.
- **Medium-term:** Documentation sprint for knowledge-concentrated modules. Target: 5 days.
- **Tracking:** "I will monitor bus factor and coupling metrics weekly. Alert me if they worsen."

Priya assigns the pair-programming task. She schedules the architecture review. She sets up weekly alerts.

### Emotional Arc
- **Start:** Concerned (velocity down, risks unknown).
- **Middle:** Informed (understands root causes, sees knowledge gaps).
- **End:** Proactive (has specific, evidence-backed action plan).

---

## Journey 4: New Engineer — Onboarding to a Repository

**Persona:** New Engineer (Jamie)
**Job:** Understand the codebase quickly
**Trigger:** First day on the job

### Stage 1: Repository Orientation (0-10 minutes)

Jamie opens Project DNA. She sees the Onboarding Guide.

Project DNA has automatically generated:
- **Repository Overview:** "This is a microservices e-commerce platform. 12 services. 3 languages. 2 frameworks."
- **Architecture Map:** Interactive graph showing services and their relationships.
- **Key Modules:** "Start here: API Gateway (entry point), OrderService (core business), PaymentService (critical, complex)."
- **Team Map:** "You will work with Marcus (Tech Lead), Sarah (Senior Engineer), and Alex (Payment expert)."

### Stage 2: Guided Exploration (10-30 minutes)

Jamie clicks [Start Guided Tour].

Project DNA walks her through:
- **Step 1:** The API Gateway. "All requests enter here. It routes to 8 services."
- **Step 2:** The OrderService. "Core business logic. Handles cart, checkout, and order lifecycle."
- **Step 3:** The PaymentService. "Critical and complex. See the detailed analysis."

At each step, Jamie sees:
- Purpose and responsibility.
- Key files and their roles.
- Recent changes and why they were made.
- Who to ask questions.
- Tests to run.

### Stage 3: First Task (30-60 minutes)

Jamie's first task is to add a field to the order response.

She asks Project DNA: "What will break if I add a field to OrderResponse?"

Project DNA shows:
- **Consumers:** 3 services deserialize OrderResponse.
- **Tests:** 12 test files reference OrderResponse.
- **Risk:** Low — additive change, no breaking contracts.
- **Recommendation:** "Add the field. Update the 3 consumer tests. No downstream impact."

Jamie makes the change confidently.

### Emotional Arc
- **Start:** Overwhelmed (new codebase, new team, new domain).
- **Middle:** Guided (structured exploration, clear explanations).
- **End:** Productive (completed first task on day 1).

---

## Journey 5: Architect — Reviewing Architecture Erosion

**Persona:** Architect (Jordan)
**Job:** Ensure architecture vision is maintained
**Trigger:** Quarterly architecture review

### Stage 1: Architecture Overview (0-10 minutes)

Jordan opens Project DNA. He navigates to the Architecture Cognition view.

He sees:
- **Original Design:** Microservices with domain boundaries.
- **Current State:** 3 boundary violations detected.
- **Erosion Timeline:** When each violation began and which commits caused it.
- **Drift Score:** 72/100 (100 = perfect alignment with original design).

### Stage 2: Deep Dive (10-30 minutes)

Jordan clicks on Boundary Violation #1: "PaymentService directly accesses Order database."

Project DNA shows:
- **When:** 8 months ago.
- **Which Commit:** "feat: add order status check in payment flow" (commit abc123).
- **Why:** "The payment flow needed order status. Instead of calling OrderService API, the developer queried the database directly for performance."
- **Impact:** "This creates a hidden coupling. Changes to Order database schema now risk breaking PaymentService."
- **Frequency:** "This query is executed 12,000 times per day."

Jordan clicks [Show Fix Options].

Project DNA suggests:
- **Option A:** Add an API endpoint in OrderService for status checks. Effort: 3 days. Risk: Low.
- **Option B:** Create a shared read model. Effort: 8 days. Risk: Medium. Benefit: Reusable.

### Stage 3: Planning Remediation (30-45 minutes)

Jordan adds the boundary violation to the architecture backlog.

He clicks [Generate Architecture Health Report].

Project DNA generates:
- **Current drift:** 72/100.
- **Target:** 85/100 by end of quarter.
- **Required actions:** Fix 3 boundary violations, review 2 new service proposals.
- **Effort:** 18 developer-days.
- **Confidence:** 78%.

Jordan presents the report at the architecture review meeting.

### Emotional Arc
- **Start:** Concerned (architecture drift is invisible without tools).
- **Middle:** Analytical (understanding exactly when, why, and how erosion occurred).
- **End:** Strategic (has a concrete, evidence-backed remediation plan).

---

## Journey 6: Investor — Technical Due Diligence

**Persona:** Investor (David)
**Job:** Evaluate software asset health before investment
**Trigger:** Series B due diligence

### Stage 1: Repository Import (0-5 minutes)

David receives repository access from the startup. He imports it into Project DNA.

Project DNA analyzes the repository. A progress bar shows:
- "Analyzing structure..."
- "Mining Git history..."
- "Building dependency graph..."
- "Evaluating architecture..."
- "Assessing risks..."

### Stage 2: Executive Summary (5-10 minutes)

Analysis complete. David sees the Due Diligence Dashboard:

- **Overall Health:** 64/100 (Caution).
- **Key Risks:**
  - 2 modules with bus factor 1.
  - Complexity accelerating in payment module.
  - Test coverage declining (58% → 42% over 12 months).
- **Positive Indicators:**
  - Clean architecture patterns detected.
  - Active refactoring culture (15% of commits are refactorings).
  - Good documentation coverage (78%).
- **Hidden Costs:**
  - Estimated 4 months of refactoring to stabilize.
  - Payment module knowledge silo creates acquisition risk.

### Stage 3: Deep Investigation (10-30 minutes)

David clicks on each risk for evidence.

He sees:
- **Bus factor:** Names, commit counts, tenure.
- **Complexity trend:** Graph with annotations for major events.
- **Coverage decline:** Correlation with feature growth (features +60%, coverage -16%).

He clicks [Generate Investment Risk Report].

Project DNA generates a PDF:
- **Technical Risk Score:** 6.2/10.
- **Stabilization Cost:** $240K (4 months × 3 engineers).
- **Key Personnel Risk:** High (payment expert is sole owner).
- **Recommendation:** "Require key-person retention clause. Budget $240K for technical debt remediation post-investment."

David uses this report in investment committee negotiations.

### Emotional Arc
- **Start:** Uncertain (no systematic way to evaluate code health).
- **Middle:** Informed (quantified risks, hidden costs revealed).
- **End:** Confident (has objective evidence for investment decision).

---

## Journey Design Principles

Every journey follows these principles:

1. **Start with a question, not a dashboard.** Users arrive with intent. The system responds to intent.
2. **Progressive disclosure.** Start with summary. Reveal detail on demand.
3. **Evidence is always available.** Every insight has a [Show Evidence] action.
4. **Temporal context is default.** Trends, not snapshots. History, not just state.
5. **Action-oriented.** Every journey ends with a decision or action, not just information.
6. **Emotional awareness.** The system acknowledges user anxiety and builds confidence.

---

## The Journey Doctrine

> **Project DNA is not a destination. It is a guide. Every journey starts with confusion and ends with understanding. The path between is paved with evidence, context, and clarity.**


---



================================================================================
# 02 Information Architecture
================================================================================

# Information Architecture

## How Project DNA is Organized

This document defines the information architecture of Project DNA — the hierarchy, navigation, and organization of information. It ensures users can find what they need without hunting.

---

## Architecture Principles

1. **Question-first, not browse-first.** Users arrive with questions. The architecture supports asking, not browsing.
2. **Progressive disclosure.** Surface summaries. Hide detail until requested.
3. **Context preservation.** Users never lose their place. Navigation is contextual, not hierarchical.
4. **Evidence proximity.** Evidence is always adjacent to the insight it supports.

---

## The Top-Level Structure

```
Project DNA
├── Search / Ask (Universal Entry Point)
├── Dashboard (Personalized Overview)
├── Repository View (Single Repository Understanding)
│   ├── Overview
│   ├── Structure
│   ├── Evolution
│   ├── Knowledge
│   ├── Dependencies
│   ├── Risks
│   └── Decisions
├── Organization View (Multi-Repository) [V2]
├── Insights Feed (Continuous Updates)
├── Reports (Generated Documents)
├── Settings
└── Help
```

---

## 1. Search / Ask (Universal Entry Point)

**Purpose:** The primary interface. Users ask questions. Project DNA answers.

**Behavior:**
- Omnipresent search bar at the top of every screen.
- Natural language input: "Why is velocity declining?"
- Structured query support: "complexity > 20 AND change_frequency > weekly"
- Auto-suggest: As user types, suggestions appear from history, common questions, and repository context.
- Recent questions: Last 10 questions are saved locally.

**Results Presentation:**
- Direct answer with summary.
- Supporting evidence cards.
- Related questions.
- Drill-down links.

**Navigation:** Search is always accessible via keyboard shortcut (Cmd+K / Ctrl+K).

---

## 2. Dashboard (Personalized Overview)

**Purpose:** A personalized landing page showing what matters to this user right now.

**Sections:**

### 2.1 Good Morning / Context Header
- "Good morning, Sarah. PaymentService has 2 new alerts since yesterday."
- Context-aware: shows different info based on user's role and recent activity.

### 2.2 Active Alerts
- Cards showing urgent insights requiring attention.
- Ordered by urgency (time to critical + impact).
- Each card: Title, severity, one-line summary, [View Details].

### 2.3 My Focus Areas
- Modules, services, or domains the user has bookmarked or recently interacted with.
- Quick health indicators for each.

### 2.4 Recent Insights
- New insights generated since user's last visit.
- Filterable by type (risk, opportunity, change, prediction).

### 2.5 Quick Actions
- [Ask a Question] [Generate Report] [View Architecture] [Check Team Health]

---

## 3. Repository View (Single Repository Understanding)

**Purpose:** Complete understanding of one repository.

**Navigation:** Tab-based, persistent across sessions.

### 3.1 Overview Tab
- **Repository Summary:** Languages, frameworks, size, maturity.
- **Health Scorecard:** Key dimensions with trend indicators.
- **Top Insights:** 3-5 most important insights right now.
- **Recent Activity:** Commits, changes, new insights.

### 3.2 Structure Tab
- **Module Map:** Interactive graph of modules and dependencies.
- **Layer View:** Architectural layers (if detected).
- **Complexity Heatmap:** Files/modules colored by complexity.
- **Coupling Matrix:** Which modules change together.

### 3.3 Evolution Tab
- **Timeline:** Repository history with major events annotated.
- **Growth Curves:** Code size, feature count, complexity over time.
- **Velocity Trends:** Commits, PRs, releases over time.
- **Refactoring History:** Detected refactoring events.

### 3.4 Knowledge Tab
- **Ownership Map:** Who owns what.
- **Expertise Distribution:** Knowledge concentration and gaps.
- **Bus Factor Alerts:** Modules at risk.
- **Onboarding Difficulty:** How hard is each module to learn.

### 3.5 Dependencies Tab
- **Internal Dependency Graph:** Module-to-module dependencies.
- **External Dependency List:** Packages with age, health, and risk.
- **Vulnerability Context:** CVEs with usage analysis and blast radius.
- **Dependency Evolution:** How dependency structure has changed.

### 3.6 Risks Tab
- **Risk Landscape:** All identified risks, filterable by severity and type.
- **Risk Forecast:** Which risks will become critical and when.
- **Risk Trends:** Risk levels over time.
- **Mitigation Tracking:** Which risks are being addressed.

### 3.7 Decisions Tab
- **Open Decisions:** Questions the system has identified but not answered.
- **Decision History:** Past decisions with outcomes (if tracked).
- **Decision Support:** Active evaluations (e.g., "Should we split PaymentService?").

---

## 4. Organization View [V2]

**Purpose:** Understanding across multiple repositories.

**Sections:**
- **Repository Map:** All repos with health indicators.
- **Cross-Repository Dependencies:** How services interact across repos.
- **Organization Knowledge:** Expertise distribution across teams.
- **Shared Components:** Libraries and services used by multiple repos.

---

## 5. Insights Feed (Continuous Updates)

**Purpose:** A chronological feed of all new insights, changes, and alerts.

**Behavior:**
- Like a social feed but for software understanding.
- Each entry: Insight type, repository, severity, timestamp, [View Details].
- Filterable by type, repository, severity, time range.
- Groupable by day, week, month.

**Entry Types:**
- **Risk Alert:** "PaymentService complexity increased 5% this week."
- **Opportunity:** "OrderService test coverage improved 12%."
- **Change:** "New module added: InventoryService."
- **Prediction:** "AnalyticsService will become high-risk in 3 months if trends continue."
- **Decision Support:** "New decision evaluation available: Should we migrate to TypeScript?"

---

## 6. Reports (Generated Documents)

**Purpose:** Exportable, shareable documents for meetings, reviews, and due diligence.

**Report Types:**
- **Engineering Health Report:** Monthly/quarterly summary.
- **Architecture Review Report:** Current state, drift, recommendations.
- **Due Diligence Report:** Investment-focused technical assessment.
- **Onboarding Guide:** New engineer repository introduction.
- **Risk Assessment:** Current risks with mitigation plans.
- **Custom Report:** User-defined queries and visualizations.

**Export Formats:**
- Interactive HTML (shareable link).
- PDF (for presentations).
- Markdown (for documentation).
- JSON (for programmatic use).

---

## 7. Settings

**Purpose:** User and system configuration.

**Sections:**
- **Profile:** Name, role, notification preferences.
- **Repositories:** Add, remove, configure analysis settings.
- **Notifications:** Alert types, frequency, channels.
- **Privacy:** Data handling, export, deletion.
- **Models:** Local model selection, update preferences.
- **Integrations:** GitHub, Jira, Slack (V2+).
- **Appearance:** Theme, density, language.

---

## 8. Help

**Purpose:** User assistance and learning.

**Sections:**
- **Getting Started:** Guided tutorial for first-time users.
- **How to Ask Questions:** Tips for effective queries.
- **Understanding Evidence:** How to read evidence chains.
- **FAQ:** Common questions.
- **Keyboard Shortcuts:** Reference card.
- **Feedback:** Report issues, suggest features.

---

## Navigation Patterns

### Global Navigation
- **Top Bar:** Search, notifications, user menu, help.
- **Left Sidebar:** Repository list, organization view, insights feed, reports, settings.
- **Breadcrumbs:** Always show current location: Repository > PaymentService > Risks.
- **Back Button:** Contextual — returns to previous view, not just previous page.

### Contextual Navigation
- **In-Content Links:** Every module name, author name, and insight is a link to its detail view.
- **Evidence Drill-Down:** Every insight has a [Show Evidence] button that opens a side panel or modal.
- **Related Content:** "You might also want to see..." suggestions at the bottom of each view.

### Keyboard Navigation
- **Cmd+K / Ctrl+K:** Universal search.
- **Esc:** Close modals, side panels, or return to previous view.
- **Arrow Keys:** Navigate lists and graphs.
- **Enter:** Select focused item.
- **?:** Show keyboard shortcuts.

---

## Mobile Architecture [V2]

For mobile (responsive web or native app):
- **Bottom Navigation:** 5 tabs: Dashboard, Search, Insights, Reports, Settings.
- **Cards:** All information presented as swipeable cards.
- **Search-first:** Mobile is primarily search-driven.
- **Notifications:** Push notifications for critical alerts.

---

## The Information Architecture Doctrine

> **Project DNA's architecture is designed around questions, not categories. Users do not browse folders. They ask questions and receive answers. The structure serves understanding, not organization.**


---



================================================================================
# 03 UI UX Specification
================================================================================

# UI/UX Specification

## Screen-by-Screen Behavior

This document specifies the behavior of every major screen in Project DNA. It is the blueprint for the frontend implementation. Every interaction, state, and transition is documented.

---

## Screen 1: Landing / Welcome

**Purpose:** First impression. Introduce Project DNA. Guide to first analysis.

**Layout:**
- Full-screen with centered content.
- Background: Subtle animated graph visualization (nodes and edges slowly moving).
- Logo and tagline: "Understand Software. Completely."
- Primary CTA: [Analyze Your First Repository]
- Secondary CTA: [Watch Demo] [Learn More]
- Footer: Version, links to docs, GitHub, privacy policy.

**States:**
- **First visit:** Shows welcome message and setup guide.
- **Returning visit:** Shows recent repositories and quick access.
- **Offline:** Shows cached data with "Last updated" timestamp.

**Transitions:**
- [Analyze Your First Repository] → Repository Import Screen.
- [Watch Demo] → Demo video modal.

---

## Screen 2: Repository Import

**Purpose:** Add a repository to Project DNA.

**Layout:**
- Two-column: Left (form), Right (preview/info).
- Left: Path input, language detection, analysis settings.
- Right: "What will be analyzed" checklist with icons.

**Form Fields:**
- **Repository Path:** Local path or Git URL.
- **Name:** Auto-detected from path. Editable.
- **Analysis Depth:** [Quick] [Standard] [Deep]
  - Quick: Structure + Dependencies (5 min).
  - Standard: + History + Metrics (15 min).
  - Deep: + Full cognitive analysis (30+ min).
- **Exclude Patterns:** Glob patterns for files to ignore.

**Behavior:**
- As user types path, system validates existence and detects language.
- [Start Analysis] becomes active when path is valid.
- Progress bar appears during analysis with stage labels.
- Cancel button available at all times.
- On completion: "Analysis complete. View your repository."

**States:**
- **Idle:** Form ready for input.
- **Validating:** Checking path, detecting language.
- **Analyzing:** Progress bar with stage names.
- **Complete:** Success message + [View Repository].
- **Error:** Clear error message with retry option.

---

## Screen 3: Main Dashboard

**Purpose:** Personalized overview and entry point.

**Layout:**
- Top: Fixed header with search bar, notifications, user menu.
- Left: Collapsible sidebar (repository list, navigation).
- Center: Scrollable dashboard content.
- Right: Collapsible detail panel (for evidence, side views).

**Content Sections (top to bottom):**

### 3.1 Context Header
- "Good morning, [Name]. [Repository Name] has [N] new insights."
- Date, last analysis timestamp.

### 3.2 Search Bar
- Full-width, prominent.
- Placeholder: "Ask anything about your software..."
- Auto-suggest dropdown.
- Voice input icon (V2).

### 3.3 Alert Cards (Horizontal Scroll)
- Up to 5 cards, ordered by urgency.
- Each card: Icon, title, one-line summary, severity badge.
- Swipe/scroll on mobile.
- Click expands to detail view.

### 3.4 Health Scorecard (Grid)
- 4-6 cards in a grid.
- Each card: Dimension name, score, trend arrow, sparkline.
- Dimensions: Structure, Evolution, Knowledge, Dependencies, Risks, Architecture.
- Click card navigates to that dimension's detail view.

### 3.5 Recent Insights (List)
- Last 10 insights with timestamps.
- Each row: Type icon, title, repository, time, [View].
- Filter: All / Risks / Opportunities / Changes / Predictions.

### 3.6 Quick Actions (Button Row)
- [Ask Question] [Generate Report] [View Architecture] [Check Team Health]

**States:**
- **Loading:** Skeleton placeholders for all sections.
- **Empty (no repositories):** CTA to import first repository.
- **Empty (no insights):** "Analysis is running. Check back soon."
- **Error:** "Unable to load dashboard. [Retry]"

---

## Screen 4: Search Results / Answer View

**Purpose:** Display answers to user questions.

**Layout:**
- Full-width, clean, reading-focused.
- Question at top (editable).
- Answer body in the center.
- Evidence panel on the right (collapsible).

**Answer Structure:**
1. **Executive Summary:** One-paragraph answer.
2. **Detailed Explanation:** Sections with headers, paragraphs, lists.
3. **Visual Evidence:** Charts, graphs, timelines embedded in the answer.
4. **Related Questions:** "You might also ask..."
5. **Confidence Footer:** "Confidence: 87%. Based on [N] evidence items. [Show Evidence]"

**Evidence Panel (Right Side):**
- Collapsible. Opens when user clicks [Show Evidence].
- Tabbed: [Evidence Chain] [Raw Data] [Sources]
- Evidence Chain: Visual tree from conclusion to raw data.
- Each node expandable to show details.

**States:**
- **Loading:** Skeleton text with pulsing animation.
- **Answer Ready:** Full content with evidence available.
- **Insufficient Evidence:** "I don't have enough evidence to answer this confidently. Here's what I know: [partial answer]. [Suggest how to get more evidence]"
- **Error:** "Unable to generate answer. [Retry] [Report Issue]"

---

## Screen 5: Repository Detail — Overview Tab

**Purpose:** Complete understanding of one repository.

**Layout:**
- Header: Repository name, path, last analysis time, [Re-analyze] button.
- Tab bar: Overview | Structure | Evolution | Knowledge | Dependencies | Risks | Decisions
- Content below tabs.

**Overview Content:**
- **Summary Card:** Language, framework, size (LOC, files), maturity, architecture pattern detected.
- **Health Radar:** Radar chart showing 6 dimensions (0-100).
- **Top Insights:** 3-5 insight cards with severity.
- **Activity Timeline:** Last 30 days of significant events.
- **Quick Stats:** Row of metric cards (complexity avg, coverage, bus factor avg, dependency count).

**States:**
- **Analyzing:** Progress overlay with "Analysis in progress..."
- **Up-to-date:** Full content.
- **Stale:** "Analysis is 7 days old. [Re-analyze]"
- **Error:** "Analysis failed. [View Logs] [Retry]"

---

## Screen 6: Repository Detail — Structure Tab

**Purpose:** Visualize and explore the physical and logical structure.

**Layout:**
- Left: Controls (zoom, filter, layout selector).
- Center: Interactive graph visualization.
- Right: Selected node details (collapsible).

**Graph Views:**
- **Dependency Graph:** Nodes = modules. Edges = dependencies. Node size = complexity. Color = health.
- **Layer View:** Architectural layers stacked vertically. Modules placed in their layer.
- **Heatmap:** Grid view. Color = complexity or other metric.

**Interactions:**
- **Click node:** Selects it. Right panel shows details.
- **Double-click node:** Navigates to module detail.
- **Hover node:** Tooltip with name, complexity, owner.
- **Drag node:** Reposition (physics-based layout).
- **Zoom:** Mouse wheel or pinch. Zoom limits prevent getting lost.
- **Filter:** By language, layer, complexity range, owner.
- **Search in graph:** Highlight matching nodes.

**Right Panel (Node Details):**
- Name, type, path.
- Complexity score with trend.
- Owner(s).
- Dependencies (in/out).
- Recent changes.
- [View Code] [View History] [View Risks]

---

## Screen 7: Repository Detail — Evolution Tab

**Purpose:** Understand how the repository has changed over time.

**Layout:**
- Top: Timeline scrubber (date range selector).
- Center: Main visualization.
- Bottom: Event annotations.

**Visualizations:**
- **Growth Chart:** LOC, files, modules over time. Multi-line chart.
- **Complexity Trend:** Average complexity over time. Annotated with major events.
- **Velocity Chart:** Commits, PRs, releases per week/month.
- **Refactoring Timeline:** Detected refactoring events as markers on the timeline.
- **Author Evolution:** Stacked area chart showing contributor mix over time.

**Timeline Scrubber:**
- Drag to select date range.
- Zoom in/out (1 week to 5 years).
- Play button: Animate evolution over time.
- Event markers: Click to see what happened on that date.

**Interactions:**
- **Hover chart:** Tooltip with exact values and date.
- **Click event marker:** Popup with event details (commit, author, impact).
- **Brush select:** Select a time range to zoom.
- **Compare:** Select two time points to compare differences.

---

## Screen 8: Repository Detail — Knowledge Tab

**Purpose:** Understand who knows what.

**Layout:**
- Toggle: [Team View] [Module View]
- Main: Network visualization or matrix.

**Team View:**
- Nodes = engineers.
- Size = number of modules they know.
- Color = tenure or activity level.
- Click engineer: See their module expertise map.

**Module View:**
- Nodes = modules.
- Size = complexity or criticality.
- Color = bus factor (green = many know it, red = few know it).
- Click module: See who knows it, how well, and onboarding difficulty.

**Details Panel:**
- **For Engineer:** Name, tenure, modules known, expertise depth, recent activity, risk if they leave.
- **For Module:** Name, bus factor, primary owner, backup owners, onboarding difficulty score, knowledge transfer recommendations.

---

## Screen 9: Repository Detail — Risks Tab

**Purpose:** See all risks and their trajectories.

**Layout:**
- Top: Risk summary (total risks, critical, high, medium, low).
- Filter bar: By type, severity, time horizon, status.
- Main: Risk cards in a list or grid.

**Risk Card:**
- **Header:** Severity badge, title, module name.
- **Body:** One-line description, trend indicator (improving/stable/worsening).
- **Footer:** Time to critical (if applicable), [View Details], [Dismiss], [Track Mitigation].

**Risk Detail View (Modal or Side Panel):**
- **Description:** Full explanation.
- **Evidence:** Charts, graphs, commit lists.
- **Impact:** Who and what is affected.
- **Forecast:** What happens if nothing changes.
- **Recommendation:** Suggested action with effort and confidence.
- **History:** How this risk has changed over time.

---

## Screen 10: Decision Support View

**Purpose:** Evaluate engineering options with evidence.

**Layout:**
- Top: Question input (e.g., "Should we split PaymentService?").
- Center: Options comparison table or cards.
- Bottom: Recommendation with confidence.

**Option Card:**
- **Title:** Option name.
- **Pros/Cons:** Bulleted list with evidence links.
- **Effort:** Estimated developer-days.
- **Risk:** Low / Medium / High with explanation.
- **Confidence:** Percentage with evidence summary.
- **Evidence:** Expandable section with supporting data.

**Comparison Table:**
- Rows: Criteria (cost, risk, effort, confidence, strategic alignment).
- Columns: Options.
- Cells: Scores with visual indicators (bars, colors).

**Recommendation Section:**
- "Recommended: [Option X]"
- "Confidence: [Y]%"
- "Reason: [Evidence-backed explanation]"
- "Next Steps: [Actionable items]"
- [Generate Report] [Save Decision] [Share]

---

## Screen 11: Reports Gallery

**Purpose:** Browse, generate, and export reports.

**Layout:**
- Grid of report templates.
- Each card: Template name, description, preview thumbnail, [Generate].
- Search/filter by type, audience, frequency.

**Report Templates:**
- Engineering Health Report (monthly).
- Architecture Review Report (quarterly).
- Due Diligence Report (on-demand).
- Onboarding Guide (on-demand).
- Risk Assessment (on-demand).
- Custom Report (user-defined).

**Report Generation Flow:**
1. Select template.
2. Configure parameters (repositories, date range, audience).
3. Preview (live generation with progress).
4. Export (PDF, HTML, Markdown, JSON).

---

## Screen 12: Settings

**Purpose:** Configure Project DNA.

**Layout:**
- Left: Settings categories (vertical tabs).
- Right: Settings form.

**Categories:**
- **Profile:** Name, role, avatar, timezone.
- **Repositories:** List, add, remove, configure analysis.
- **Notifications:** Alert types, frequency, quiet hours.
- **Privacy:** Data export, deletion, telemetry consent.
- **Models:** Local LLM selection, update preferences.
- **Integrations:** GitHub, Jira, Slack (V2+).
- **Appearance:** Theme, density, font size, language.
- **Keyboard:** Shortcut customization.
- **Advanced:** Debug mode, logs, cache management.

---

## Global UI Behaviors

### Loading States
- **Skeleton screens:** For content-heavy pages. Never show spinners on blank pages.
- **Progress bars:** For long operations (analysis, report generation). Show stage names.
- **Inline spinners:** For button actions and small requests.
- **Optimistic updates:** For user actions (dismiss alert, bookmark). Update UI immediately, sync in background.

### Empty States
- **No repositories:** Illustration + "Import your first repository" CTA.
- **No insights:** "Analysis is running. Check back soon." with progress.
- **No results:** "No results found. Try a different query." with suggestions.
- **No evidence:** "Insufficient data to support this conclusion."

### Error States
- **Recoverable:** Inline error message with retry button.
- **Non-recoverable:** Full-page error with contact/support link.
- **Network:** "You appear to be offline. Some features are unavailable."
- **Analysis failure:** Clear error log with export option for debugging.

### Notifications
- **Toast:** Brief, auto-dismissing (3-5 seconds). For success, info, warnings.
- **Banner:** Persistent until dismissed. For critical alerts, updates.
- **Badge:** On icons (notifications, alerts). Red dot with count.
- **In-app:** Within the relevant context (e.g., "New insight available" in the insights feed).

---

## The UX Specification Doctrine

> **Every screen serves understanding. Every interaction reduces friction. Every state is handled gracefully. Project DNA feels like a conversation with a brilliant engineer who has perfect memory, not like a dashboard or a tool.**


---



================================================================================
# 04 Dashboard Design
================================================================================

# Dashboard Design

## The Main Dashboard

This document specifies the design of the main dashboard — the personalized landing page that users see when they open Project DNA. It is the most important screen. It must communicate health, urgency, and opportunity at a glance.

---

## Design Philosophy

The dashboard is not a control panel. It is a **briefing**.

When a user opens Project DNA, they should immediately know:
1. What requires attention right now.
2. How their system is trending.
3. Where to go next.

The dashboard is **glanceable, actionable, and contextual**.

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Header (Fixed)                                             │
│  [Logo] [Search Bar]              [Notifications] [User]    │
├─────────────────────────────────────────────────────────────┤
│  Sidebar (Collapsible)        │  Main Content Area          │
│  ─────────────────────────    │  ─────────────────────────  │
│  Repositories                 │  Context Header             │
│  ├── repo-a                   │  ─────────────────────────  │
│  ├── repo-b                   │  Alert Cards (Horizontal)   │
│  └── repo-c                   │  ─────────────────────────  │
│                               │  Health Scorecard (Grid)  │
│  Navigation                   │  ─────────────────────────  │
│  ├── Dashboard                │  Recent Insights (List)     │
│  ├── Insights Feed            │  ─────────────────────────  │
│  ├── Reports                  │  Quick Actions              │
│  └── Settings                 │                             │
│                               │                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Section 1: Header

**Height:** 64px
**Background:** Surface color (slightly elevated from background).
**Position:** Fixed at top. Always visible.

**Elements (left to right):**

### Logo
- Icon + "Project DNA" wordmark.
- Click: Return to dashboard.
- Size: 32px icon + text.

### Search Bar
- Width: 480px (expandable on focus).
- Placeholder: "Ask anything about your software..."
- Icon: Magnifying glass (left), microphone (right, V2).
- Behavior: Click expands to full search experience. Typing triggers auto-suggest.
- Keyboard shortcut: Cmd+K highlights search bar.

### Notifications
- Bell icon with badge (red dot + count if > 0).
- Click: Dropdown with recent alerts and insights.
- Max 10 items. [View All] links to Insights Feed.
- Each item: Icon, title, time, [Dismiss].

### User Menu
- Avatar with dropdown.
- Items: Profile, Settings, Help, Log Out.
- Role badge shown (Developer, Manager, etc.).

---

## Section 2: Sidebar

**Width:** 240px (collapsible to 64px icons-only).
**Background:** Slightly darker than main content.
**Position:** Fixed left. Scrollable if content exceeds height.

### Repositories List
- Section header: "Repositories" with [+] button.
- Each repository: Favicon/icon + name + health indicator (small dot: green/yellow/red).
- Click: Navigate to that repository's overview.
- Right-click: Context menu (Re-analyze, Settings, Remove).
- Active repository: Highlighted background.

### Navigation Links
- Dashboard (home icon)
- Insights Feed (pulse icon)
- Reports (document icon)
- Settings (gear icon)

Each link has:
- Icon (24px).
- Label.
- Badge (if applicable).
- Hover: Slight background highlight.
- Active: Bold text + left border accent.

### Collapse Behavior
- Collapse button at bottom of sidebar.
- Collapsed: Icons only (64px width). Labels in tooltips.
- Expanded: Full width (240px).
- State persisted in user preferences.

---

## Section 3: Context Header

**Height:** ~80px
**Background:** Transparent (part of main content).
**Padding:** 24px horizontal, 16px vertical.

**Content:**
- **Greeting:** "Good morning, Sarah." (Time-aware: morning/afternoon/evening).
- **Context line:** "PaymentService has 2 new alerts since yesterday. OrderService coverage improved 8%."
- **Date / Last update:** "Last analyzed: 2 hours ago."

**Behavior:**
- Context line updates dynamically based on recent insights.
- If no new insights: "All systems stable. No new alerts."
- If first visit: "Welcome to Project DNA. Start by importing a repository."

---

## Section 4: Alert Cards (Horizontal Scroll)

**Height:** 160px
**Background:** Transparent.
**Padding:** 24px horizontal.

**Layout:**
- Horizontal scroll container.
- 3-5 cards visible at once (desktop).
- 1 card visible (mobile).
- Scroll indicators: Left/right arrows if scrollable.

**Card Design:**
- Width: 320px.
- Height: 140px.
- Background: Elevated surface (card).
- Border-left: 4px colored by severity.
  - Critical: Red (#EF4444)
  - High: Orange (#F97316)
  - Medium: Yellow (#EAB308)
  - Low: Blue (#3B82F6)
  - Info: Gray (#6B7280)
- Padding: 16px.
- Border-radius: 12px.
- Shadow: Subtle (0 1px 3px rgba(0,0,0,0.1)).

**Card Content:**
- **Top row:** Severity badge + module name.
- **Title:** Bold, 16px, 2 lines max. Ellipsis if overflow.
- **Summary:** Regular, 14px, 2 lines max. Gray color.
- **Footer:** Time ("2 hours ago") + [View Details] link.

**Card Interactions:**
- **Hover:** Slight lift (shadow increase), cursor pointer.
- **Click:** Opens detail view (modal or side panel).
- **Dismiss:** X button in top-right. Confirmation for critical alerts.

**Empty State:**
- "No active alerts. Your systems are stable. 🎉"
- Icon: Checkmark in circle.

---

## Section 5: Health Scorecard (Grid)

**Height:** ~300px
**Background:** Transparent.
**Padding:** 24px horizontal.

**Layout:**
- Section header: "Repository Health" with [View All] link.
- Grid: 3 columns × 2 rows (desktop). 2 columns × 3 rows (tablet). 1 column (mobile).
- Gap: 16px.

**Card Design:**
- Background: Elevated surface.
- Border-radius: 12px.
- Padding: 20px.
- Height: 120px.

**Card Content:**
- **Top row:** Dimension icon (24px) + Dimension name.
- **Center:** Score (large, 32px, bold) + /100.
- **Bottom row:** Trend arrow (↑ ↓ →) + Sparkline (last 30 days).
- **Color coding:**
  - 80-100: Green
  - 60-79: Yellow
  - 40-59: Orange
  - 0-39: Red

**Dimensions (V1):**
1. **Structure:** Module health, coupling, cohesion.
2. **Evolution:** Growth velocity, refactoring health.
3. **Knowledge:** Expertise distribution, bus factor.
4. **Dependencies:** Internal/external dependency health.
5. **Risks:** Overall risk landscape.
6. **Architecture:** Pattern alignment, boundary health.

**Card Interactions:**
- **Hover:** Border color change to accent. Cursor pointer.
- **Click:** Navigate to that dimension's detail tab.
- **Sparkline hover:** Tooltip with exact values.

---

## Section 6: Recent Insights (List)

**Height:** Flexible (scrolls with page).
**Background:** Transparent.
**Padding:** 24px horizontal.

**Layout:**
- Section header: "Recent Insights" with filter tabs.
- Filter tabs: All | Risks | Opportunities | Changes | Predictions.
- List: Vertical stack of insight rows.
- Max 10 items visible. [Load More] button.

**Insight Row Design:**
- Height: 72px.
- Background: Elevated surface (subtle, lower than cards).
- Border-radius: 8px.
- Padding: 16px.
- Margin-bottom: 8px.

**Row Content:**
- **Left:** Type icon (24px, colored).
  - Risk: Red warning triangle.
  - Opportunity: Green upward arrow.
  - Change: Blue sync icon.
  - Prediction: Purple crystal ball.
- **Center:**
  - Title: Bold, 14px.
  - Subtitle: Repository name + time. 12px, gray.
- **Right:**
  - Severity badge (if applicable).
  - [View] button.

**Row Interactions:**
- **Hover:** Background lightens. Cursor pointer.
- **Click:** Opens insight detail (side panel or modal).
- **Swipe (mobile):** Dismiss or save.

**Empty State:**
- "No recent insights. Analysis may be running or the repository is stable."

---

## Section 7: Quick Actions

**Height:** ~100px
**Background:** Transparent.
**Padding:** 24px horizontal, 32px bottom.

**Layout:**
- Section header: "Quick Actions" (optional, can be implicit).
- Horizontal row of buttons.
- Gap: 12px.

**Buttons:**
- [Ask a Question] — Primary button (filled).
- [Generate Report] — Secondary button (outlined).
- [View Architecture] — Secondary button (outlined).
- [Check Team Health] — Secondary button (outlined).

**Button Design:**
- Height: 40px.
- Padding: 0 20px.
- Border-radius: 8px.
- Font: 14px, medium weight.
- Icon + label.

**Interactions:**
- **Hover:** Slight darken (filled) or border darken (outlined).
- **Active:** Scale down 0.98.
- **Focus:** Outline ring (accessibility).

---

## Responsive Behavior

### Desktop (≥1280px)
- Full layout as described.
- Sidebar expanded by default.
- 3-column scorecard grid.

### Tablet (768px – 1279px)
- Sidebar collapsed by default. Toggle to expand.
- 2-column scorecard grid.
- Alert cards: 2 visible.

### Mobile (<768px)
- Sidebar hidden. Hamburger menu to open.
- Search bar full-width, collapses to icon.
- 1-column scorecard grid.
- Alert cards: 1 visible, swipeable.
- Quick actions: 2×2 grid or horizontal scroll.
- Bottom navigation bar (V2).

---

## Dark Mode

All colors invert for dark mode:
- Background: Dark gray (#0F172A) instead of light gray (#F8FAFC).
- Surface: Slightly lighter dark (#1E293B).
- Text: Light gray (#F1F5F9) instead of dark.
- Accent colors remain similar but adjusted for contrast.
- Charts use dark-friendly color palettes.

Toggle: System preference or manual toggle in settings.

---

## The Dashboard Doctrine

> **The dashboard is not a destination. It is a starting point. It tells users what matters right now and where to go next. It never overwhelms. It always guides.**


---



================================================================================
# 05 Component Library
================================================================================

# Component Library

## Reusable UI Components

This document defines every reusable UI component in Project DNA. Each component includes its purpose, behavior, states, and usage guidelines. This ensures consistency across the product.

---

## Layout Components

### AppShell

**Purpose:** The outermost container that holds the entire application.

**Structure:**
- Header (fixed top).
- Sidebar (fixed left, collapsible).
- Main content area (scrollable).
- Right panel (collapsible, for evidence/details).
- Toast container (fixed bottom-right).

**Behavior:**
- Sidebar collapse state persisted.
- Right panel opens/closes based on context.
- Main content area resizes when sidebar/panel changes.

---

### PageHeader

**Purpose:** Page title with contextual actions.

**Structure:**
- Left: Breadcrumb + page title.
- Right: Action buttons (contextual).

**Example:**
- Title: "PaymentService"
- Breadcrumb: Repository > PaymentService > Risks
- Actions: [Re-analyze] [Bookmark] [Share]

---

### SectionHeader

**Purpose:** Label for a content section with optional actions.

**Structure:**
- Left: Section title + optional subtitle.
- Right: [View All], filter, or sort controls.

**Example:**
- Title: "Recent Insights"
- Subtitle: "Last 7 days"
- Action: [Filter ▼]

---

## Data Display Components

### InsightCard

**Purpose:** Display a single insight with summary and actions.

**Variants:**
- **Alert variant:** With severity border. Used in dashboard alert strip.
- **List variant:** Compact. Used in insights feed.
- **Detail variant:** Expanded. Used in detail views.

**Props:**
- `title` (string): Insight headline.
- `summary` (string): One-line description.
- `type` (enum): Risk | Opportunity | Change | Prediction.
- `severity` (enum): Critical | High | Medium | Low | Info.
- `module` (string): Related module name.
- `timestamp` (datetime): When insight was generated.
- `evidenceCount` (number): Number of supporting evidence items.
- `onView` (function): Click handler.
- `onDismiss` (function): Dismiss handler.

**States:**
- Default, Hover, Active, Dismissed (fade out).

**Usage:** Dashboard alerts, insights feed, risk lists.

---

### MetricCard

**Purpose:** Display a single metric with value, trend, and context.

**Props:**
- `label` (string): Metric name.
- `value` (number): Current value.
- `unit` (string): Optional unit (%, days, etc.).
- `trend` (enum): Up | Down | Stable.
- `trendValue` (number): Percentage change.
- `sparklineData` (array): Last 30 data points for sparkline.
- `threshold` (object): Color thresholds (green/yellow/red ranges).

**States:**
- Default, Loading (skeleton), Error ("--").

**Usage:** Health scorecard, quick stats, module details.

---

### EvidenceChain

**Purpose:** Visualize the chain of evidence from raw data to conclusion.

**Structure:**
- Vertical tree or horizontal flow.
- Nodes: Evidence items with type icons.
- Edges: "supports" or "derives from" relationships.
- Expandable nodes for detail.

**Props:**
- `chain` (array): Evidence nodes with metadata.
- `maxDepth` (number): How many levels to show initially.
- `interactive` (boolean): Whether nodes are clickable.

**States:**
- Collapsed (summary), Expanded (full chain), Loading.

**Usage:** Evidence panel, insight detail, report generation.

---

### Timeline

**Purpose:** Display chronological events with annotations.

**Props:**
- `events` (array): Event objects with date, type, title, description.
- `zoom` (enum): Day | Week | Month | Year.
- `selectable` (boolean): Whether events can be selected.
- `animate` (boolean): Whether to show animation on load.

**Event Types:**
- Commit, Release, Refactor, Incident, Decision, Milestone.

**States:**
- Default, Zoomed, Event Selected, Playing (animation).

**Usage:** Evolution tab, repository history, decision tracking.

---

### GraphVisualization

**Purpose:** Interactive node-edge graph for dependencies, architecture, and knowledge.

**Props:**
- `nodes` (array): Node objects with id, label, size, color, metadata.
- `edges` (array): Edge objects with source, target, weight, type.
- `layout` (enum): Force-directed | Hierarchical | Circular | Grid.
- `interactive` (boolean): Zoom, pan, drag, select.
- `nodeLabel` (function): Custom label renderer.

**Interactions:**
- Zoom (scroll/pinch).
- Pan (drag background).
- Drag nodes (reposition).
- Click node (select).
- Double-click (navigate to detail).
- Hover (tooltip).

**States:**
- Loading, Empty (no nodes), Error, Interactive.

**Usage:** Structure tab, dependency graph, knowledge map.

---

### RiskCard

**Purpose:** Display a risk with severity, trend, and actions.

**Props:**
- `title` (string): Risk name.
- `description` (string): Risk explanation.
- `severity` (enum): Critical | High | Medium | Low.
- `trend` (enum): Improving | Stable | Worsening.
- `timeToCritical` (string): Human-readable estimate.
- `module` (string): Affected module.
- `onTrack` (function): Start tracking mitigation.
- `onDismiss` (function): Dismiss risk.

**States:**
- Active, Tracking (mitigation in progress), Dismissed, Resolved.

**Usage:** Risks tab, alerts, reports.

---

### DecisionOption

**Purpose:** Display an option in a decision evaluation.

**Props:**
- `name` (string): Option name.
- `pros` (array): List of advantages with evidence links.
- `cons` (array): List of disadvantages with evidence links.
- `effort` (string): Estimated effort.
- `risk` (enum): Low | Medium | High.
- `confidence` (number): 0-100.
- `isRecommended` (boolean): Whether this is the recommended option.

**States:**
- Default, Expanded (showing full evidence), Selected.

**Usage:** Decision support view, reports.

---

## Input Components

### SearchBar

**Purpose:** Primary input for asking questions.

**Props:**
- `placeholder` (string): Default text.
- `value` (string): Current input.
- `suggestions` (array): Auto-suggest items.
- `loading` (boolean): Whether search is in progress.
- `onSearch` (function): Submit handler.
- `onChange` (function): Input change handler.

**States:**
- Idle, Focused (expanded), Typing (suggestions visible), Loading (results), Empty (no results).

**Behavior:**
- Cmd+K shortcut focuses.
- Escape clears.
- Enter submits.
- Arrow keys navigate suggestions.

---

### FilterBar

**Purpose:** Filter lists and views by multiple criteria.

**Props:**
- `filters` (array): Filter definitions with type, options, and current value.
- `onChange` (function): Filter change handler.
- `onClear` (function): Clear all filters.

**Filter Types:**
- Dropdown, Multi-select, Date range, Toggle, Slider.

**States:**
- Default, Active (filters applied), Collapsed.

---

### DateRangePicker

**Purpose:** Select a time range for temporal analysis.

**Props:**
- `start` (date): Start date.
- `end` (date): End date.
- `presets` (array): Quick presets (Last 7 days, Last 30 days, Last quarter, etc.).
- `onChange` (function): Range change handler.

**States:**
- Default, Open (calendar visible), Selected.

---

## Feedback Components

### Toast

**Purpose:** Brief, non-blocking notification.

**Props:**
- `message` (string): Notification text.
- `type` (enum): Success | Info | Warning | Error.
- `duration` (number): Auto-dismiss time in ms (default 3000).
- `action` (object): Optional action button (label + handler).

**States:**
- Entering, Visible, Exiting.

**Position:** Bottom-right stack. Max 3 visible.

---

### Banner

**Purpose:** Persistent notification for important information.

**Props:**
- `message` (string): Banner text.
- `type` (enum): Info | Warning | Error.
- `dismissible` (boolean): Whether user can close.
- `action` (object): Optional action button.

**States:**
- Visible, Dismissed (slide up).

**Position:** Below header, full width.

---

### Skeleton

**Purpose:** Placeholder for loading content.

**Variants:**
- **Text:** Single line or multi-line.
- **Card:** Rectangle with rounded corners.
- **Circle:** For avatars or icons.
- **Graph:** For chart placeholders.

**Animation:** Subtle pulse (opacity 0.5 → 1 → 0.5).

**Usage:** Dashboard loading, list loading, chart loading.

---

### EmptyState

**Purpose:** Friendly message when no content exists.

**Props:**
- `icon` (icon): Illustrative icon.
- `title` (string): Short headline.
- `description` (string): Explaining text.
- `action` (object): Optional CTA button.

**Variants:**
- No repositories, No insights, No results, No evidence, No data.

---

### LoadingOverlay

**Purpose:** Block interaction during long operations.

**Props:**
- `message` (string): Status message.
- `progress` (number): 0-100 for progress bar.
- `stage` (string): Current stage name.
- `cancelable` (boolean): Whether operation can be cancelled.

**States:**
- Visible, Updating (progress changes), Exiting.

**Usage:** Repository analysis, report generation, model loading.

---

## Navigation Components

### SidebarNav

**Purpose:** Primary navigation sidebar.

**Props:**
- `items` (array): Navigation items with icon, label, path, badge.
- `activePath` (string): Current active route.
- `collapsed` (boolean): Icon-only mode.
- `onToggle` (function): Collapse/expand handler.

**States:**
- Expanded, Collapsed, Hover (item).

---

### Breadcrumb

**Purpose:** Show current location in hierarchy.

**Props:**
- `items` (array): Path segments with label and path.
- `onClick` (function): Navigation handler.

**Behavior:**
- Each segment is clickable except the last.
- Home icon for root.
- Truncated with "..." if too long.

---

### TabBar

**Purpose:** Switch between views within a page.

**Props:**
- `tabs` (array): Tab items with label, icon, content, badge.
- `activeTab` (string): Currently active tab.
- `onChange` (function): Tab change handler.

**States:**
- Default, Active, Hover, Disabled.

**Variants:**
- Horizontal (default), Vertical (settings), Pill (compact).

---

## Modal Components

### Modal

**Purpose:** Overlay dialog for focused tasks.

**Props:**
- `title` (string): Modal header.
- `content` (component): Body content.
- `actions` (array): Footer buttons.
- `size` (enum): Small | Medium | Large | Fullscreen.
- `onClose` (function): Close handler.

**States:**
- Closed, Entering, Open, Exiting.

**Behavior:**
- Click outside closes.
- Escape closes.
- Focus trap inside modal.
- Body scroll locked when open.

---

### SidePanel

**Purpose:** Slide-in panel for detail views without leaving context.

**Props:**
- `title` (string): Panel header.
- `content` (component): Body content.
- `width` (number): Panel width in pixels.
- `onClose` (function): Close handler.

**States:**
- Closed, Entering (slide in), Open, Exiting (slide out).

**Behavior:**
- Swipe to close (mobile).
- Click outside closes.
- Content scrolls independently.

**Usage:** Evidence panel, insight detail, module detail.

---

### Tooltip

**Purpose:** Contextual information on hover.

**Props:**
- `content` (string or component): Tooltip content.
- `position` (enum): Top | Bottom | Left | Right.
- `delay` (number): Show delay in ms.

**States:**
- Hidden, Visible.

**Usage:** Graph nodes, metric labels, icon buttons.

---

## The Component Library Doctrine

> **Every component serves understanding. No component is decorative. Every component has a purpose, states, and behavior documented. Consistency is not about uniformity — it is about predictability.**


---



================================================================================
# 06 Design System
================================================================================

# Design System

## Visual Language of Project DNA

This document defines the complete visual language of Project DNA — colors, typography, spacing, icons, animations, and accessibility rules. It ensures visual consistency across every screen and component.

---

## Design Principles

1. **Clarity over decoration.** Every visual element serves understanding.
2. **Hierarchy through subtlety.** Use size, weight, and color — not borders and boxes — to create hierarchy.
3. **Motion with meaning.** Animations guide attention, not distract.
4. **Accessible by default.** WCAG 2.1 AA compliance is the baseline, not the goal.

---

## Color System

### Base Palette

| Token | Light Mode | Dark Mode | Usage |
|---|---|---|---|
| `--bg-primary` | `#F8FAFC` | `#0F172A` | Main background |
| `--bg-surface` | `#FFFFFF` | `#1E293B` | Cards, panels, elevated surfaces |
| `--bg-surface-hover` | `#F1F5F9` | `#334155` | Hover state for surfaces |
| `--bg-surface-active` | `#E2E8F0` | `#475569` | Active/selected state |
| `--text-primary` | `#0F172A` | `#F8FAFC` | Headlines, primary text |
| `--text-secondary` | `#475569` | `#94A3B8` | Body text, descriptions |
| `--text-tertiary` | `#94A3B8` | `#64748B` | Metadata, timestamps |
| `--text-inverse` | `#FFFFFF` | `#0F172A` | Text on colored backgrounds |
| `--border-subtle` | `#E2E8F0` | `#334155` | Dividers, borders |
| `--border-focus` | `#3B82F6` | `#60A5FA` | Focus rings |

### Accent Colors

| Token | Hex | Usage |
|---|---|---|
| `--accent-primary` | `#3B82F6` | Primary actions, links, active states |
| `--accent-primary-hover` | `#2563EB` | Primary button hover |
| `--accent-primary-subtle` | `#EFF6FF` | Primary tinted backgrounds |
| `--accent-success` | `#10B981` | Positive trends, success states |
| `--accent-success-subtle` | `#ECFDF5` | Success tinted backgrounds |
| `--accent-warning` | `#F59E0B` | Warnings, medium risks |
| `--accent-warning-subtle` | `#FFFBEB` | Warning tinted backgrounds |
| `--accent-danger` | `#EF4444` | Critical risks, errors |
| `--accent-danger-subtle` | `#FEF2F2` | Danger tinted backgrounds |
| `--accent-info` | `#6366F1` | Information, predictions |
| `--accent-info-subtle` | `#EEF2FF` | Info tinted backgrounds |

### Severity Colors

| Severity | Border | Background | Text |
|---|---|---|---|
| Critical | `#EF4444` | `#FEF2F2` / `#7F1D1D` | `#DC2626` |
| High | `#F97316` | `#FFF7ED` / `#7C2D12` | `#EA580C` |
| Medium | `#EAB308` | `#FEFCE8` / `#713F12` | `#CA8A04` |
| Low | `#3B82F6` | `#EFF6FF` / `#1E3A8A` | `#2563EB` |
| Info | `#6B7280` | `#F3F4F6` / `#374151` | `#4B5563` |

### Data Visualization Colors

| Index | Color | Usage |
|---|---|---|
| 1 | `#3B82F6` | Primary series |
| 2 | `#10B981` | Secondary / positive |
| 3 | `#F59E0B` | Tertiary / warning |
| 4 | `#EF4444` | Negative / danger |
| 5 | `#8B5CF6` | Quaternary |
| 6 | `#EC4899` | Additional series |
| 7 | `#06B6D4` | Additional series |
| 8 | `#84CC16` | Additional series |

---

## Typography

### Font Family

**Primary:** Inter (sans-serif)
- Weights: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold).
- Fallback: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto.

**Monospace:** JetBrains Mono (for code, metrics, raw data)
- Fallback: "Fira Code", "SF Mono", Consolas, monospace.

### Type Scale

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|---|---|---|---|---|---|
| `text-xs` | 12px | 400 | 16px | 0 | Timestamps, metadata, badges |
| `text-sm` | 14px | 400 | 20px | 0 | Body text, descriptions, buttons |
| `text-base` | 16px | 400 | 24px | 0 | Standard body, card titles |
| `text-lg` | 18px | 500 | 28px | -0.01em | Section headers, insight titles |
| `text-xl` | 20px | 600 | 30px | -0.02em | Page titles, major headings |
| `text-2xl` | 24px | 600 | 32px | -0.02em | Dashboard headers, modal titles |
| `text-3xl` | 30px | 700 | 36px | -0.02em | Hero text, landing page |
| `text-4xl` | 36px | 700 | 40px | -0.02em | Major headlines |

### Typography Rules

- **Headlines:** Use `text-primary`, semibold or bold, tight letter-spacing.
- **Body:** Use `text-secondary`, regular weight, comfortable line-height.
- **Metadata:** Use `text-tertiary`, small size, regular weight.
- **Code/Metrics:** Use monospace, `text-sm`, `text-secondary`.
- **Links:** `accent-primary`, underline on hover.
- **Emphasis:** Use weight (600) or color change, not italics.

---

## Spacing System

**Base unit:** 4px

| Token | Value | Usage |
|---|---|---|
| `space-1` | 4px | Tight gaps, icon padding |
| `space-2` | 8px | Inline spacing, small gaps |
| `space-3` | 12px | Button padding, list gaps |
| `space-4` | 16px | Card padding, section gaps |
| `space-5` | 20px | Medium padding |
| `space-6` | 24px | Page padding, large gaps |
| `space-8` | 32px | Section spacing |
| `space-10` | 40px | Major section breaks |
| `space-12` | 48px | Page-level spacing |
| `space-16` | 64px | Hero spacing |

### Layout Spacing

- **Page padding:** 24px horizontal, 16px vertical.
- **Card padding:** 16px or 20px.
- **Card gap:** 16px.
- **Section gap:** 24px.
- **Element gap within card:** 12px.

---

## Border Radius

| Token | Value | Usage |
|---|---|---|
| `radius-sm` | 6px | Small buttons, tags, badges |
| `radius-md` | 8px | Buttons, inputs, small cards |
| `radius-lg` | 12px | Cards, panels, modals |
| `radius-xl` | 16px | Large cards, feature sections |
| `radius-full` | 9999px | Pills, avatars, circular buttons |

---

## Shadows

| Token | Value | Usage |
|---|---|---|
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle elevation, hover states |
| `shadow-md` | `0 4px 6px -1px rgba(0,0,0,0.1)` | Cards, dropdowns |
| `shadow-lg` | `0 10px 15px -3px rgba(0,0,0,0.1)` | Modals, popovers |
| `shadow-xl` | `0 20px 25px -5px rgba(0,0,0,0.1)` | Fullscreen overlays |

---

## Icons

### Icon System

**Library:** Lucide React (or equivalent open-source icon set).
- Consistent stroke width (1.5px or 2px).
- Size variants: 16px (inline), 20px (buttons), 24px (navigation), 32px (feature icons).

### Icon Usage

| Icon | Meaning | Usage |
|---|---|---|
| 🔍 Search | Search, ask | Search bar, query actions |
| ⚠️ AlertTriangle | Warning, risk | Risk cards, alerts |
| ✓ CheckCircle | Success, resolved | Completed actions, healthy state |
| 📈 TrendingUp | Improvement, growth | Positive trends |
| 📉 TrendingDown | Decline, degradation | Negative trends |
| 🔄 RefreshCw | Update, re-analyze | Refresh buttons |
| 📄 FileText | Document, report | Reports, documentation |
| 👤 User | Person, owner | Ownership, team |
| 🔗 Link | Dependency, connection | Graphs, dependencies |
| 🧠 Brain | Cognition, understanding | Logo, AI features |
| 📊 BarChart | Metrics, data | Charts, analytics |
| 🏗️ GitBranch | Version control, history | Git-related features |
| ⚙️ Settings | Configuration | Settings menu |
| ❓ HelpCircle | Help, information | Help sections, tooltips |

---

## Animation

### Principles

1. **Purposeful:** Every animation guides attention or provides feedback.
2. **Fast:** Most animations complete in 200-300ms.
3. **Subtle:** Animations are noticed when absent, not when present.
4. **Respectful:** Reduced motion preference is honored.

### Standard Durations

| Duration | Usage |
|---|---|
| 100ms | Micro-interactions (button press, checkbox toggle) |
| 200ms | Hover states, small transitions |
| 300ms | Panel slides, modal open/close, page transitions |
| 500ms | Large transitions, complex animations |
| 1000ms+ | Loading animations, progress indicators |

### Easing Functions

| Name | Value | Usage |
|---|---|---|
| `ease-out` | `cubic-bezier(0,0,0.2,1)` | Elements entering (modals, panels) |
| `ease-in` | `cubic-bezier(0.4,0,1,1)` | Elements leaving |
| `ease-in-out` | `cubic-bezier(0.4,0,0.2,1)` | State changes, toggles |
| `spring` | `cubic-bezier(0.34,1.56,0.64,1)` | Playful bounces (badges, notifications) |

### Specific Animations

**Panel Slide:**
- Enter: Translate from right, 300ms, ease-out.
- Leave: Translate to right, 200ms, ease-in.

**Modal:**
- Backdrop: Fade in 200ms.
- Content: Scale from 0.95 + fade, 300ms, ease-out.

**Toast:**
- Enter: Slide up + fade, 300ms, spring.
- Leave: Slide right + fade, 200ms, ease-in.

**Skeleton:**
- Pulse: Opacity 0.5 → 1, 1.5s, infinite, ease-in-out.

**Graph Node:**
- Appear: Scale from 0 + fade, 400ms, ease-out.
- Hover: Scale 1.05, 200ms, ease-out.
- Select: Pulse ring, 2s, infinite.

**Page Transition:**
- Fade content, 150ms, ease-in-out.
- No slide (avoids motion sickness).

---

## Accessibility

### Color Contrast

- All text meets WCAG 2.1 AA (4.5:1 for normal text, 3:1 for large text).
- UI components meet WCAG 2.1 AA (3:1 for boundaries).
- Never rely on color alone to convey information. Always pair with icons, text, or patterns.

### Focus Management

- All interactive elements have visible focus rings (`border-focus` color, 2px offset).
- Focus order is logical and follows visual layout.
- Focus is trapped within modals and panels.
- Focus is returned to trigger element when modal closes.

### Reduced Motion

- When `prefers-reduced-motion: reduce` is active:
  - All transitions become instant (0ms).
  - Animations are disabled.
  - Skeleton pulse is replaced with static placeholder.
  - Graph physics are disabled (static layout).

### Screen Reader Support

- All images have alt text.
- All icons have aria-labels.
- All charts have data tables or aria descriptions.
- Live regions announce new insights and alerts.
- Skip links provided for keyboard navigation.

---

## Dark Mode

### Toggle

- Manual toggle in settings.
- Respects `prefers-color-scheme` by default.
- Transition between modes: 200ms ease-in-out for color properties.

### Color Inversion Rules

- Backgrounds become dark grays (not pure black).
- Surfaces are slightly lighter than background.
- Text inverts to light grays (not pure white).
- Accent colors remain similar but may shift slightly for contrast.
- Shadows become lighter (subtle glow instead of dark shadow).
- Borders become lighter grays.

### Chart Adaptation

- Background: Transparent (shows dark surface).
- Grid lines: Light gray with low opacity.
- Text: Light gray.
- Series colors: Slightly brighter for visibility on dark.

---

## The Design System Doctrine

> **Project DNA's visual language is calm, clear, and purposeful. It does not shout. It guides. It does not decorate. It clarifies. Every color, type size, and animation serves the goal of understanding software completely.**


---



================================================================================
# 07 User Workflows
================================================================================

# User Workflows

## Task Flows for Key Activities

This document defines the complete step-by-step workflows for the most important user activities in Project DNA. Each workflow is a sequence of screens, decisions, and actions that lead to a successful outcome.

---

## Workflow 1: Ask a Question and Get an Answer

**Goal:** User asks a natural language question and receives an evidence-backed answer.

**Trigger:** User has a question about their software system.

### Step 1: Initiate Question
- **Screen:** Any screen (search bar is omnipresent).
- **Action:** User clicks search bar or presses Cmd+K.
- **State:** Search bar expands/focuses. Cursor blinks. Auto-suggest dropdown appears with recent questions and popular queries.

### Step 2: Type Question
- **Action:** User types natural language question.
- **State:** Auto-suggest updates with matching questions from history and repository context.
- **Example:** "Why is PaymentService so complex?"

### Step 3: Submit Question
- **Action:** User presses Enter or clicks submit button.
- **State:** Search bar shows loading state. User is taken to Answer View.

### Step 4: Loading Answer
- **Screen:** Answer View with skeleton loading state.
- **State:**
  - Executive summary area shows skeleton text.
  - Evidence area shows skeleton cards.
  - Progress indicator: "Analyzing evidence..." → "Synthesizing understanding..." → "Generating explanation..."
- **Duration:** 2-10 seconds depending on question complexity.

### Step 5: Receive Answer
- **Screen:** Answer View populated with content.
- **Content:**
  1. **Executive Summary:** "PaymentService's complexity increased 133% over 18 months due to feature growth without corresponding refactoring."
  2. **Detailed Explanation:** Sections with headers, paragraphs, embedded charts.
  3. **Visual Evidence:** Complexity trend chart, commit timeline, ownership pie chart.
  4. **Related Questions:** "Who owns PaymentService?" "What depends on PaymentService?"
  5. **Confidence Footer:** "Confidence: 91%. Based on 12 evidence items. [Show Evidence]"

### Step 6: Explore Evidence
- **Action:** User clicks [Show Evidence].
- **State:** Evidence panel slides in from right.
- **Content:** Evidence chain tree. Each node expandable. Raw data accessible at leaf nodes.

### Step 7: Drill Down
- **Action:** User clicks on a chart, module name, or author name.
- **State:** Navigates to relevant detail view (module detail, author profile, timeline).

### Step 8: Follow-Up
- **Action:** User asks a follow-up question in the same view.
- **State:** New question appears above previous answer. Context is preserved (conversation thread).

### Step 9: Save or Share
- **Action:** User clicks [Save] or [Share].
- **Save:** Bookmarked to user's saved insights.
- **Share:** Generates shareable link or exports to PDF/Markdown.

### Alternative Paths
- **Insufficient Evidence:** System shows partial answer with explanation of what evidence is missing. User can suggest how to gather it.
- **Ambiguous Question:** System asks clarifying questions. "Do you mean complexity of the code or complexity of the dependencies?"
- **No Results:** System suggests related questions or broader queries.

---

## Workflow 2: Investigate a Risk

**Goal:** User investigates a identified risk, understands its evidence, and decides on mitigation.

**Trigger:** Alert card, risk notification, or proactive discovery.

### Step 1: Discover Risk
- **Source:** Dashboard alert card, email notification, or insights feed.
- **Content:** "PaymentService bus factor is 1. Alex is the sole expert. Vacation scheduled next week."

### Step 2: Open Risk Detail
- **Action:** User clicks alert card or notification.
- **Screen:** Risk Detail View (modal or side panel).
- **Content:**
  - Risk title and severity.
  - Full description with causal explanation.
  - Evidence: Ownership chart, commit history, knowledge distribution map.
  - Impact: "If Alex is unavailable, PaymentService bugs will take 3x longer to fix."
  - Forecast: "Bus factor will remain 1 unless knowledge transfer occurs."

### Step 3: Explore Evidence
- **Action:** User clicks through evidence items.
- **State:** Evidence panel shows:
  - Ownership chart: Alex 73%, others minimal.
  - Commit history: Alex's commits dominate for 18 months.
  - Knowledge map: Single thick line from Alex to PaymentService.

### Step 4: Evaluate Options
- **Action:** User clicks [What Should We Do?]
- **Screen:** Decision Support View with options.
- **Options:**
  - **Option A:** Pair Alex with Sarah for 2 weeks. Effort: 10 days. Risk: Low.
  - **Option B:** Document PaymentService architecture. Effort: 5 days. Risk: Medium (documentation may become outdated).
  - **Option C:** Accept risk. Effort: 0. Risk: High (if Alex leaves).

### Step 5: Select Action
- **Action:** User selects Option A and clicks [Schedule Knowledge Transfer].
- **State:** System creates a tracked mitigation item.

### Step 6: Track Mitigation
- **Screen:** Risks tab with mitigation tracking.
- **Content:**
  - Risk status: "Mitigation in progress."
  - Progress indicator: "Week 1 of 2. Sarah has made 4 commits to PaymentService."
  - Updated bus factor estimate: "Projected bus factor: 2 by end of week 2."

### Step 7: Resolution
- **Trigger:** After 2 weeks, system re-evaluates.
- **Content:** "Bus factor increased to 2. Sarah now has 15% of PaymentService commits. Risk reduced to Medium."
- **Action:** User clicks [Resolve]. Risk moved to resolved history.

---

## Workflow 3: Make an Architecture Decision

**Goal:** User evaluates whether to make a structural change to the software.

**Trigger:** Quarterly planning, technical review, or proactive identification.

### Step 1: Frame Decision
- **Screen:** Decision Support View.
- **Action:** User types decision question: "Should we split PaymentService into microservices?"
- **State:** System analyzes the question and frames the decision context.

### Step 2: Review Context
- **Content:**
  - Current state: "PaymentService handles 4 domains. Complexity: 28. 3 dependent services."
  - Trend: "Complexity increased 133% in 18 months."
  - Stakeholders: "This affects OrderService, NotificationService, and AnalyticsService teams."

### Step 3: Evaluate Options
- **Content:** System presents 2-4 options with full analysis.
- **User Action:** User clicks through each option, reading pros, cons, evidence, and confidence scores.
- **Interaction:** User can adjust parameters (e.g., "What if we had 6 engineers instead of 3?"). System recalculates in real-time.

### Step 4: Compare Options
- **Screen:** Comparison table or side-by-side cards.
- **Content:**
  - Criteria: Cost, Risk, Effort, Confidence, Strategic Alignment.
  - Scores for each option.
  - Visual indicators (bars, colors) for quick comparison.

### Step 5: Review Recommendation
- **Content:**
  - "Recommended: Modularize within monolith (Option B)."
  - "Confidence: 76%."
  - "Reason: Lower risk than full split, addresses immediate complexity, preserves operational simplicity."
  - "Next Steps: 1) Extract payment-retry module. 2) Add tests. 3) Evaluate split in 6 months."

### Step 6: Generate Report
- **Action:** User clicks [Generate Report for Leadership].
- **State:** System generates one-page summary with charts, evidence, and recommendation.
- **Formats:** PDF, HTML, Markdown.

### Step 7: Save Decision
- **Action:** User clicks [Save Decision].
- **State:** Decision stored in Decision History with:
  - Question, options, selected option, confidence, timestamp.
  - Outcome tracking: "Check back in 6 months to evaluate."

### Step 8: Track Outcome
- **Trigger:** 6 months later.
- **Content:** System prompts: "You decided to modularize PaymentService. How did it go?"
- **Action:** User provides feedback (success, partial, failure).
- **State:** System learns from outcome. Future recommendations improve.

---

## Workflow 4: Onboard to a New Repository

**Goal:** New engineer quickly understands a repository and completes their first task.

**Trigger:** New engineer joins team. First day.

### Step 1: Access Onboarding Guide
- **Screen:** Onboarding Guide (auto-generated or manually triggered).
- **Content:**
  - Repository overview: purpose, architecture, tech stack.
  - Team introduction: key people, their expertise.
  - Key modules: what to know first.
  - Architecture map: interactive graph.

### Step 2: Guided Tour
- **Action:** User clicks [Start Guided Tour].
- **State:** Step-by-step walkthrough with highlights and explanations.
- **Steps:**
  1. "This is the API Gateway. All requests enter here."
  2. "This is OrderService. Core business logic."
  3. "This is PaymentService. Critical and complex. Let's explore it."

### Step 3: Explore Module
- **Screen:** PaymentService detail view.
- **Content:**
  - Purpose and responsibility.
  - Key files and their roles.
  - Recent changes and why.
  - Who to ask: "Alex is the expert. Reach out on Slack."
  - Tests to run: "Run PaymentService tests with: npm test payment"

### Step 4: First Task Support
- **Action:** User receives first task: "Add a field to OrderResponse."
- **State:** User asks Project DNA: "What will break if I add a field to OrderResponse?"
- **Answer:**
  - Consumers: 3 services.
  - Tests: 12 files.
  - Risk: Low.
  - Recommendation: "Add field. Update consumer tests. No breaking changes."

### Step 5: Complete Task
- **Action:** User makes change, runs tests, submits PR.
- **State:** Project DNA detects the change and updates understanding.
- **Feedback:** "Great first contribution! OrderResponse now has the new field. 3 consumer tests updated."

### Step 6: Continue Learning
- **Screen:** Personalized learning path.
- **Content:** "Next: Understand the checkout flow. Estimated time: 1 hour."

---

## Workflow 5: Generate and Share a Report

**Goal:** User creates a shareable document for a meeting or review.

**Trigger:** Monthly review, quarterly planning, or due diligence.

### Step 1: Select Report Template
- **Screen:** Reports Gallery.
- **Action:** User browses templates and selects "Engineering Health Report."

### Step 2: Configure Parameters
- **Screen:** Report Configuration.
- **Fields:**
  - Repositories: Select 1 or more.
  - Date Range: Last 30 days (default), custom.
  - Audience: Engineering team (default), Leadership, External.
  - Depth: Summary (default), Detailed, Comprehensive.

### Step 3: Preview Report
- **Screen:** Live Report Preview.
- **State:** System generates report in real-time with progress bar.
- **Content:**
  - Title: "Engineering Health Report — June 2026"
  - Sections: Executive Summary, Health Metrics, Top Risks, Recommendations, Appendix.
  - Interactive charts embedded.

### Step 4: Edit and Customize
- **Action:** User clicks [Edit] on any section.
- **State:** Inline editing or section configuration panel.
- **Customization:** Add/remove sections, reorder, add custom notes.

### Step 5: Export
- **Action:** User clicks [Export].
- **Options:**
  - PDF (for presentations).
  - HTML (for sharing link).
  - Markdown (for documentation).
  - JSON (for programmatic use).

### Step 6: Share
- **Action:** User clicks [Share].
- **Options:**
  - Copy link (HTML version hosted locally or on shared server).
  - Email (opens email client with link).
  - Slack (integration, V2).

### Step 7: Schedule Recurring
- **Action:** User clicks [Schedule Monthly].
- **State:** Report is auto-generated on the first of each month.
- **Notification:** User receives "Your monthly report is ready" notification.

---

## Workflow 6: Respond to an Alert

**Goal:** User receives a critical alert and takes appropriate action.

**Trigger:** System detects critical condition.

### Step 1: Receive Alert
- **Channel:** In-app notification, dashboard alert card, email (optional), Slack (V2).
- **Content:** "CRITICAL: PaymentService complexity increased 15% this week. Trend is accelerating."

### Step 2: Acknowledge
- **Action:** User clicks notification or alert card.
- **Screen:** Alert Detail View.

### Step 3: Investigate
- **Content:**
  - What: Complexity jumped from 28 to 32.
  - When: This week, primarily from 3 commits.
  - Why: "Emergency bug fixes added without refactoring. Retry logic became more complex."
  - Evidence: Commit list, diff summary, complexity graph.
  - Impact: "If trend continues, complexity will reach 40 in 4 weeks. Maintenance cost will double."

### Step 4: Decide Action
- **Options:**
  - [Schedule Refactoring] — Adds to team's backlog.
  - [Dismiss] — Marks as acknowledged but not acted upon. System asks why.
  - [Snooze] — Reminds in 1 week.
  - [Escalate] — Sends to engineering manager.

### Step 5: Track
- **If Schedule Refactoring:**
  - System creates tracked item.
  - Monitors complexity trend weekly.
  - Alerts if trend continues despite scheduled work.

### Step 6: Resolve
- **Trigger:** Complexity stabilizes or decreases.
- **Content:** "PaymentService complexity stabilized at 32. Refactoring scheduled for next sprint. Risk reduced to Medium."

---

## Workflow Design Principles

1. **Never dead-end.** Every workflow ends with action or clear next step.
2. **Preserve context.** Users can always go back or see where they are.
3. **Progressive complexity.** Start simple. Reveal depth on demand.
4. **Evidence adjacent.** Evidence is always one click from any conclusion.
5. **Feedback loops.** Actions have visible consequences. System responds to user input.

---

## The Workflow Doctrine

> **A workflow is a conversation. The user asks. The system responds. The user explores. The system guides. The user decides. The system remembers. Every workflow in Project DNA is designed to feel like this conversation.**


---



================================================================================
# 08 Accessibility
================================================================================

# Accessibility

## Accessible by Design

This document defines the accessibility requirements and implementation guidelines for Project DNA. Accessibility is not a feature. It is a foundation. Every user — regardless of ability, device, or context — must be able to understand their software through Project DNA.

---

## Accessibility Principles

1. **Perceivable:** Information must be presentable in ways users can perceive.
2. **Operable:** Interface components must be operable by all users.
3. **Understandable:** Information and operation must be understandable.
4. **Robust:** Content must work with current and future assistive technologies.

These align with WCAG 2.1 AA standards, which are the minimum baseline for Project DNA.

---

## Visual Accessibility

### Color Contrast

All text and interactive elements must meet WCAG 2.1 AA contrast ratios:

| Element | Minimum Ratio | Target Ratio |
|---|---|---|
| Normal text (<18px) | 4.5:1 | 7:1 (AAA) |
| Large text (≥18px bold or ≥24px) | 3:1 | 4.5:1 |
| UI components (buttons, inputs) | 3:1 | 4.5:1 |
| Graphical objects (icons, charts) | 3:1 | 4.5:1 |

**Implementation:**
- Use the Design System color tokens. They are pre-validated for contrast.
- Never introduce new colors without contrast validation.
- Use tools like axe, WAVE, or Lighthouse for automated checking.

### Color Independence

Never rely on color alone to convey information:

- **Risk severity:** Use color + icon + text label. (Red triangle + "Critical" text.)
- **Trend direction:** Use color + arrow icon + text. (Green arrow up + "Improving".)
- **Graph data:** Use color + pattern + shape. (Blue solid line + circle markers.)

### Text Scaling

- All text must remain readable at 200% browser zoom.
- Layout must not break at 200% zoom (reflow acceptable, horizontal scroll not).
- Touch targets must remain at least 44×44px at 200% zoom.

---

## Motor Accessibility

### Keyboard Navigation

All functionality must be accessible via keyboard:

**Global Shortcuts:**
- `Tab`: Move focus forward.
- `Shift+Tab`: Move focus backward.
- `Enter` / `Space`: Activate focused element.
- `Escape`: Close modals, panels, dropdowns, return to previous context.
- `Cmd+K` / `Ctrl+K`: Focus search bar.
- `?`: Show keyboard shortcuts reference.
- `Arrow Keys`: Navigate within lists, menus, graphs, tabs.
- `Home` / `End`: Jump to start/end of lists.

**Focus Management:**
- All interactive elements have visible focus indicators (2px ring, `--border-focus` color, 2px offset).
- Focus order follows visual reading order (left-to-right, top-to-bottom).
- Focus is trapped within modals and panels while open.
- Focus returns to the trigger element when a modal/panel closes.
- No keyboard traps. Users can always Tab out of any component.

**Skip Links:**
- "Skip to main content" link at top of page (visible on focus).
- "Skip to search" link.
- "Skip to navigation" link.

### Touch and Pointer

- All interactive elements have minimum touch target of 44×44px.
- Buttons and links have adequate spacing (minimum 8px between targets).
- Hover states are not required for touch, but active states are.
- Drag operations (graph nodes) have keyboard alternatives (arrow keys to move, Enter to select).

---

## Cognitive Accessibility

### Clear Language

- Use plain language. Avoid jargon where possible.
- When technical terms are necessary, provide definitions or tooltips.
- Insight summaries are written at 8th-grade reading level (Flesch-Kincaid).
- Avoid abbreviations without explanation. ("Bus factor" is explained on first use.)

### Consistent Navigation

- Navigation structure is consistent across all pages.
- Same components behave the same way everywhere.
- Icons have consistent meanings (documented in Component Library).
- Predictable patterns reduce cognitive load.

### Error Prevention and Recovery

- Destructive actions (delete repository, dismiss critical alert) require confirmation.
- Forms validate in real-time with clear error messages.
- Users can undo major actions within 5 seconds (toast with undo).
- "Are you sure?" dialogs explain consequences, not just ask for confirmation.

### Reduced Distraction

- No auto-playing animations (except user-initiated play buttons).
- No flashing content (frequency < 3Hz to prevent seizures).
- Notifications are batched where possible. No notification spam.
- Users can configure notification frequency and types.

---

## Assistive Technology

### Screen Readers

Project DNA must work with:
- NVDA (Windows)
- JAWS (Windows)
- VoiceOver (macOS, iOS)
- TalkBack (Android)

**Requirements:**
- All images have descriptive `alt` text.
- All icons have `aria-label` or are hidden from screen readers (`aria-hidden="true"`) if decorative.
- All charts have:
  - `aria-label` describing the chart's conclusion.
  - Data table alternative or `aria-describedby` pointing to a text summary.
- All interactive elements have accessible names.
- Live regions announce:
  - New insights and alerts (`aria-live="polite"`).
  - Analysis completion (`aria-live="polite"`).
  - Critical errors (`aria-live="assertive"`).

**Landmarks:**
- `<header>` — Application header.
- `<nav>` — Sidebar navigation.
- `<main>` — Primary content area.
- `<aside>` — Evidence panel, side details.
- `<footer>` — Page footer.
- Search bar has `role="search"`.

### Screen Reader Specific Behaviors

**Graph Visualization:**
- Graphs are not read as visual elements.
- Screen reader users get:
  - A text summary: "PaymentService depends on 3 services: OrderService, NotificationService, and AnalyticsService."
  - A navigable list of nodes and edges.
  - Arrow keys navigate between connected nodes.
  - Enter opens node details.

**Evidence Chain:**
- Read as a nested list.
- Each evidence item is a list item with description.
- Users can expand/collapse levels.

**Timeline:**
- Read as a chronological list of events.
- Each event has date, type, and description.
- Users can jump to specific date ranges.

### Voice Control

- All interactive elements have visible text labels or `aria-label` for voice control compatibility.
- Common actions have clear, speakable names.
- No actions rely on precise mouse positioning.

---

## Responsive Accessibility

### Mobile Accessibility

- Touch targets are large (minimum 44×44px).
- Gestures have alternatives (tap instead of swipe, buttons instead of drag).
- Bottom navigation (V2) has clear labels and large touch areas.
- Screen reader order is logical on mobile (top-to-bottom, not left-to-right).

### Zoom and Reflow

- At 200% zoom: content reflows vertically. No horizontal scrolling except for tables and graphs.
- At 400% zoom: all content is still accessible. Navigation collapses to hamburger menu.
- Text spacing can be increased (line-height 1.5, paragraph spacing 2×, letter-spacing 0.12em, word-spacing 0.16em) without breaking layout.

---

## Motion and Animation

### Reduced Motion

Respect `prefers-reduced-motion`:

| Animation | Default | Reduced Motion |
|---|---|---|
| Page transitions | 150ms fade | Instant |
| Modal open | 300ms scale + fade | Instant |
| Panel slide | 300ms translate | Instant |
| Graph physics | Enabled | Disabled (static layout) |
| Skeleton pulse | 1.5s opacity cycle | Static gray placeholder |
| Toast enter | 300ms slide + fade | Instant |
| Chart animations | 500ms draw | Instant |

**Implementation:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Vestibular Disorders

- No parallax scrolling.
- No large-scale motion that simulates movement.
- Graph zoom is controlled, not continuous.
- No auto-rotating carousels.

---

## Accessibility Testing

### Automated Testing

Run on every build:
- **axe-core:** Automated accessibility testing.
- **Lighthouse:** Accessibility audit (target score: 100).
- **eslint-plugin-jsx-a11y:** Catch accessibility issues in JSX.

### Manual Testing

Performed monthly:
- Keyboard-only navigation test (no mouse).
- Screen reader test (VoiceOver or NVDA).
- Color contrast audit (all screens).
- Zoom test (200% and 400%).
- Reduced motion test.

### User Testing

Quarterly:
- Test with users who use assistive technology.
- Test with users who have cognitive disabilities.
- Test with users who use voice control.

---

## Accessibility Checklist

For every new feature or screen, verify:

- [ ] All images have alt text.
- [ ] All interactive elements have accessible names.
- [ ] Color is not the only means of conveying information.
- [ ] Focus is visible and logical.
- [ ] Keyboard navigation works completely.
- [ ] Screen reader can access all content.
- [ ] Charts have text alternatives.
- [ ] Touch targets are at least 44×44px.
- [ ] Animations respect reduced motion.
- [ ] Content is readable at 200% zoom.
- [ ] Forms have clear labels and error messages.
- [ ] Destructive actions require confirmation.

---

## The Accessibility Doctrine

> **Accessibility is not a checklist. It is a commitment. Every engineer, designer, and product manager at Project DNA is responsible for ensuring that every user can understand their software. We do not ship features that exclude people.**


---



================================================================================
# 09 Interaction Guidelines
================================================================================

# Interaction Guidelines

## How Project DNA Feels to Use

This document defines the micro-interactions, feedback patterns, and behavioral details that make Project DNA feel responsive, trustworthy, and delightful. These are the "polish" details that separate good products from great ones.

---

## Interaction Principles

1. **Immediate feedback.** Every user action receives immediate visual or haptic response. No action feels ignored.
2. **Meaningful motion.** Animations guide attention and explain state changes, not decorate.
3. **Forgiving.** Mistakes are easy to recover from. Destructive actions are hard to do accidentally.
4. **Predictable.** Same actions produce same results. No surprises.

---

## Micro-Interactions

### Button Interactions

**Default State:**
- Background: `--accent-primary` (filled) or transparent with border (outlined).
- Text: `--text-inverse` (filled) or `--accent-primary` (outlined).
- Border-radius: `radius-md` (8px).
- Padding: 0 20px, height 40px.

**Hover State:**
- Filled: Background darkens to `--accent-primary-hover`.
- Outlined: Border darkens, subtle background tint (`--accent-primary-subtle`).
- Cursor: pointer.
- Transition: 150ms ease-in-out.

**Active State (Press):**
- Scale: 0.98 (subtle press-down effect).
- Background: Slightly darker than hover.
- Transition: 100ms ease-out.

**Focus State:**
- Ring: 2px solid `--border-focus`, 2px offset.
- Visible for keyboard navigation. Slightly subdued for mouse (optional, based on browser).

**Disabled State:**
- Opacity: 0.5.
- Cursor: not-allowed.
- No hover or active effects.
- Tooltip on hover: "This action is unavailable because [reason]."

**Loading State:**
- Text replaced with inline spinner (16px).
- Button remains clickable but shows loading state.
- Spinner rotates 360° over 1s, linear, infinite.

---

### Card Interactions

**Default State:**
- Background: `--bg-surface`.
- Border-radius: `radius-lg` (12px).
- Shadow: `shadow-sm`.
- Padding: 16px or 20px.

**Hover State:**
- Shadow: `shadow-md` (lift effect).
- Border: 1px solid `--border-subtle` (if not already bordered).
- Cursor: pointer (if clickable).
- Transition: 200ms ease-out.

**Active State:**
- Scale: 0.99 (subtle press).
- Shadow: `shadow-sm` (return to default).
- Transition: 100ms ease-out.

**Selected State:**
- Border: 2px solid `--accent-primary`.
- Background: `--accent-primary-subtle`.

---

### Input Interactions

**Default State:**
- Background: `--bg-surface`.
- Border: 1px solid `--border-subtle`.
- Border-radius: `radius-md`.
- Padding: 10px 14px.

**Focus State:**
- Border: 2px solid `--accent-primary`.
- Shadow: 0 0 0 3px `rgba(59, 130, 246, 0.1)` (subtle glow).
- Transition: 150ms ease-in-out.

**Error State:**
- Border: 2px solid `--accent-danger`.
- Background: `--accent-danger-subtle`.
- Error message below: 12px, `--accent-danger`.
- Shake animation: translateX(-4px, 4px, -4px, 0) over 300ms.

**Success State:**
- Border: 2px solid `--accent-success`.
- Checkmark icon appears inside input (right side).

---

### Link Interactions

**Default State:**
- Color: `--accent-primary`.
- Text-decoration: none.

**Hover State:**
- Text-decoration: underline.
- Color: `--accent-primary-hover`.
- Transition: 150ms ease-in-out.

**Visited State:**
- Color: Slightly muted primary (optional, based on context).

**Focus State:**
- Outline: 2px solid `--border-focus`, 2px offset.

---

### Toggle / Switch Interactions

**Default State:**
- Track: Gray background.
- Thumb: White circle, left position.
- Shadow: `shadow-sm` on thumb.

**Checked State:**
- Track: `--accent-primary`.
- Thumb: White circle, right position.
- Transition: 200ms ease-in-out (thumb slides).

**Hover State:**
- Track: Slightly darker.

**Active State:**
- Thumb: Slight scale increase (1.1) during drag.

---

### Dropdown / Select Interactions

**Open Animation:**
- Origin: Top center of trigger.
- Scale: 0.95 → 1.
- Opacity: 0 → 1.
- Duration: 150ms ease-out.

**Close Animation:**
- Reverse of open.
- Duration: 100ms ease-in.

**Item Hover:**
- Background: `--bg-surface-hover`.
- Cursor: pointer.

**Item Selection:**
- Background: `--accent-primary-subtle`.
- Checkmark icon appears.

---

## Feedback Patterns

### Loading Feedback

**Inline Loading:**
- Spinner (16px) replaces content or appears next to action.
- Used for: button clicks, small data fetches.

**Skeleton Loading:**
- Gray placeholder shapes pulse.
- Used for: page content, cards, lists.
- Duration: Until content loads.

**Progress Loading:**
- Progress bar with percentage and stage label.
- Used for: repository analysis, report generation.
- Stage labels: "Analyzing structure..." → "Building graph..." → "Generating insights..."

**Staggered Loading:**
- Content appears sequentially, not all at once.
- Cards fade in one by one (50ms delay between each).
- Used for: dashboard cards, insight lists.

---

### Success Feedback

**Toast:**
- "Repository analysis complete. 47 insights generated."
- Icon: CheckCircle (green).
- Duration: 3 seconds.
- Action: [View Insights] (optional).

**Inline:**
- Checkmark icon next to completed action.
- Green text: "Saved successfully."
- Fades out after 2 seconds.

**Confetti (Optional):**
- Subtle confetti animation for major milestones (first repository, 100th insight).
- Respects reduced motion.

---

### Error Feedback

**Toast:**
- "Analysis failed. Unable to parse TypeScript configuration."
- Icon: AlertCircle (red).
- Duration: 5 seconds (persists longer than success).
- Action: [Retry] [View Logs].

**Inline:**
- Red border + error message.
- Shake animation for form inputs.

**Banner:**
- Persistent banner for critical errors.
- "Project DNA is unable to connect to the local model. Please check your Ollama installation."
- Action: [Troubleshoot] [Dismiss].

---

### Warning Feedback

**Toast:**
- "Analysis is taking longer than expected. Estimated time: 5 more minutes."
- Icon: AlertTriangle (yellow).
- Duration: 4 seconds.

**Inline:**
- Yellow border + warning message.
- "This module is large. Analysis may take several minutes."

---

### Information Feedback

**Tooltip:**
- Hover trigger: 300ms delay.
- Content: Brief explanation.
- Duration: Persists while hovering.
- Position: Auto-adjusts to stay on screen.

**Info Banner:**
- "New feature: Decision Cognition is now available. [Learn More]."
- Dismissible.
- Blue background.

---

## State Transitions

### Page Transition

**Enter:**
- Content fades in: opacity 0 → 1, 150ms ease-in-out.
- No slide (avoids motion sickness).

**Leave:**
- Content fades out: opacity 1 → 0, 100ms ease-in-out.

---

### Panel Slide

**Open (Right Panel):**
- Panel slides from right: translateX(100%) → translateX(0).
- Backdrop fades in: opacity 0 → 0.3.
- Duration: 300ms ease-out.

**Close:**
- Panel slides to right: translateX(0) → translateX(100%).
- Backdrop fades out: opacity 0.3 → 0.
- Duration: 200ms ease-in.

**Swipe to Close (Mobile):**
- Swipe right on panel edge.
- Velocity-based: Fast swipe closes immediately. Slow swipe snaps open or closed based on position.

---

### Modal Transition

**Open:**
- Backdrop: opacity 0 → 0.5, 200ms ease-out.
- Modal: scale 0.95 + opacity 0 → scale 1 + opacity 1, 300ms ease-out.
- Slight bounce at end (spring easing).

**Close:**
- Modal: scale 1 + opacity 1 → scale 0.95 + opacity 0, 200ms ease-in.
- Backdrop: opacity 0.5 → 0, 150ms ease-in.

---

### Graph Interactions

**Node Hover:**
- Scale: 1 → 1.1, 200ms ease-out.
- Shadow: Increases.
- Connected edges: Highlight (thicken, brighten).
- Unconnected nodes: Dim (opacity 0.3).

**Node Click:**
- Scale: 1.1 → 1.0 (quick bounce).
- Selection ring: Appears with pulse animation.
- Right panel: Slides in with node details.

**Node Drag:**
- Real-time position update.
- Physics simulation: Other nodes adjust smoothly.
- Release: Node settles with spring physics.

**Zoom:**
- Scroll wheel: Smooth zoom with 100ms inertia.
- Pinch: Smooth zoom with 100ms inertia.
- Zoom limits: Min 0.5x, Max 5x.
- Zoom indicator: Briefly shows current zoom level ("100%") on zoom change.

---

## Gesture Guidelines (Mobile / Touch)

### Tap
- Primary action: Select, open, activate.
- Double-tap: Zoom in on graphs. (Single tap + pinch preferred.)

### Long Press
- Context menu: Right-click equivalent.
- Duration: 500ms.
- Feedback: Haptic vibration (if available) + subtle scale increase.

### Swipe
- **Horizontal:**
  - Left: Dismiss card, delete item (with confirmation).
  - Right: Save, bookmark, quick action.
- **Vertical:**
  - Scroll lists, pages.
  - Pull to refresh (insights feed).

### Pinch
- Zoom in/out on graphs and visualizations.
- Two-finger rotate: Rotate graph view (optional).

### Pan
- Drag to pan graphs and large visualizations.
- One-finger pan on empty areas. Two-finger pan on nodes (to avoid conflict with drag).

---

## Sound and Haptics

### Sound (Optional, V2)

- **Success:** Subtle chime (pleasant, not jarring).
- **Error:** Low tone (distinct from success).
- **Notification:** Soft ping.
- **All sounds:** Optional, off by default. User can enable in settings.

### Haptics (Mobile)

- **Button press:** Light tap.
- **Long press:** Medium tap.
- **Error:** Double tap.
- **Success:** Light tap.
- **All haptics:** Optional, respect system settings.

---

## The Interaction Doctrine

> **Every interaction in Project DNA should feel like a conversation with a thoughtful partner. It responds immediately. It guides gently. It forgives mistakes. It never ignores the user. The product feels alive, attentive, and respectful.**


---



================================================================================
# 10 Future UI Ideas
================================================================================

# Future UI Ideas

## What Comes After V1

This document captures experimental and future UI concepts for Project DNA. These are not committed features. They are ideas to explore as the product matures. They ensure the UI evolves alongside the ambition of the product.

---

## V2 Ideas

### 1. 3D Architecture Visualization

**Concept:** A three-dimensional, explorable model of the software architecture.

**Visualization:**
- Services are 3D buildings in a cityscape.
- Height = complexity. Width = module count. Color = health.
- Dependencies are roads between buildings. Traffic = data flow.
- Zoom in: Enter a building to see floors (layers) and rooms (modules).
- Zoom out: See the entire organization as a city.

**Interactions:**
- Fly-through camera with WASD or drag.
- Click building: See details panel.
- Time slider: Watch the city grow and change over time.
- VR support: Walk through your architecture in virtual reality.

**Value:** Spatial understanding of large systems. Emotional connection to scale.

**Risk:** Performance. Accessibility. May be gimmicky if not useful.

---

### 2. Voice Interface

**Concept:** Ask questions and receive answers via voice.

**Interactions:**
- "Hey DNA, why is PaymentService complex?"
- System responds with spoken answer and visual summary on screen.
- Follow-up: "Who owns it?" — context preserved.
- Hands-free mode for engineers working in IDE.

**Value:** Faster querying. Accessibility for visually impaired users. Multi-tasking.

**Risk:** Accuracy of speech-to-text for technical terms. Privacy concerns (voice data). Local processing required.

---

### 3. Collaborative Annotations

**Concept:** Teams can annotate insights, evidence, and decisions with comments and discussions.

**Interactions:**
- Click any insight: Add a comment thread.
- @mention team members.
- Resolve discussions with decisions.
- Annotation history preserved in Engineering Memory.

**Value:** Team knowledge building. Decision rationale preservation. Async collaboration.

**Risk:** Scope creep toward project management. Notification complexity.

---

### 4. Mobile Companion App

**Concept:** A lightweight mobile app for checking insights on the go.

**Features:**
- Push notifications for critical alerts.
- Quick question asking (voice or text).
- Snapshot reports (view-only).
- Team health dashboard.
- Cannot perform full analysis (compute-intensive).

**Value:** Executive awareness. On-call engineer quick checks. Manager monitoring.

**Risk:** Feature parity expectations. Security of mobile data.

---

### 5. IDE Integration

**Concept:** Project DNA insights embedded in the developer's IDE.

**Features:**
- VS Code extension: Hover over function → see complexity, owner, last change.
- Inline risk warnings: "This module has bus factor 1. Be careful."
- Pre-commit analysis: "Your change affects 3 services. Review impact."
- Quick ask: Sidebar panel for asking questions without leaving IDE.

**Value:** Context at the point of work. No context switching.

**Risk:** IDE fragmentation (VS Code, JetBrains, Vim, etc.). Performance impact on IDE.

---

## V3 Ideas

### 6. Real-Time Runtime Overlay

**Concept:** Correlating runtime behavior (Grafana, Datadog) with code understanding.

**Visualization:**
- Code structure with live heatmaps showing which functions are called most.
- Error rate overlaid on module graph (red glow on failing modules).
- Latency indicators on dependency edges.
- "This module is slow AND complex AND frequently modified — triple risk."

**Value:** Connects code health with operational health. Prioritizes fixes that affect users.

**Risk:** Requires runtime data access. Complexity of real-time correlation.

---

### 7. AI-Powered Architecture Simulator

**Concept:** Simulate the impact of architectural changes before implementing them.

**Interactions:**
- "What if we split PaymentService?"
- System simulates: new dependency graph, estimated complexity per service, team impact, migration effort.
- Visual diff: Before vs. After architecture.
- Confidence score for simulation accuracy.

**Value:** Reduces risk of major changes. Enables experimentation without code.

**Risk:** Simulation accuracy. Computational cost. May encourage over-analysis.

---

### 8. Natural Language Report Generation

**Concept:** Generate custom reports by describing what you want in natural language.

**Interaction:**
- "Generate a report for my CTO showing the top 5 risks in the payment domain with estimated costs."
- System generates tailored report with appropriate visualizations and evidence.
- User can iterate: "Add a comparison to last quarter."

**Value:** Removes report configuration friction. Democratizes data access.

**Risk:** NL understanding accuracy. Report quality consistency.

---

## V4 Ideas

### 9. Cross-Organization Intelligence

**Concept:** Understand software ecosystems beyond a single organization.

**Visualization:**
- Industry-wide dependency graphs (open-source libraries as nodes, organizations as clusters).
- "Your organization and 340 others depend on this library. Here is its health."
- Benchmarking: "Your code health is in the 73rd percentile of similar organizations."
- Pattern propagation: "This architectural pattern is emerging across 12 organizations in your sector."

**Value:** Industry context. Competitive intelligence. Open-source health awareness.

**Risk:** Privacy (anonymization required). Data volume. Anti-trust concerns.

---

### 10. Predictive Engineering Calendar

**Concept:** A calendar view showing predicted future events based on trends.

**Visualization:**
- Calendar with predicted events:
  - "March 15: PaymentService likely to become critical bottleneck."
  - "April 1: Bus factor for AuthModule will drop to 1 if no action taken."
  - "May 10: Recommended time for quarterly architecture review."
- Events have confidence scores and evidence links.
- Users can accept, dismiss, or reschedule predictions.

**Value:** Proactive planning. Time-based risk management.

**Risk:** Prediction accuracy. User fatigue from too many predictions.

---

### 11. Software DNA Helix

**Concept:** A visual metaphor for the Software Cognition Model as a DNA double helix.

**Visualization:**
- One strand: Code structure (files, modules, dependencies).
- Other strand: Engineering dynamics (commits, people, decisions).
- Rungs: Connections between code and people (who wrote what, when, why).
- Time flows along the helix. Zoom in to see individual commits. Zoom out to see years.
- Interactive: Spin the helix, click rungs for details.

**Value:** Powerful brand metaphor. Intuitive representation of the "DNA" name. Memorable visualization.

**Risk:** May be too abstract for practical use. Performance. Accessibility.

---

## Experimental Concepts

### 12. Haptic Feedback for Code Health

**Concept:** Haptic patterns conveying code health through touch.

**For devices with haptic feedback:**
- Smooth vibration: Healthy code.
- Irregular, sharp vibrations: Unhealthy, risky code.
- Engineers "feel" code quality while exploring.

**Value:** Novel accessibility feature. Sensory understanding.

**Risk:** Niche use case. Device support limited.

---

### 13. Augmented Reality Code Exploration

**Concept:** Use AR glasses to project code understanding into physical space.

**Interaction:**
- Point phone at whiteboard architecture diagram.
- AR overlay shows live health metrics, recent changes, and risks for each service.
- Walk around office: See floating health indicators above team areas.

**Value:** Spatial computing. Physical-digital integration.

**Risk:** Very early technology. Hardware dependency. Gimmick potential.

---

### 14. Emotional Design — Software Vitality

**Concept:** The UI reflects the "mood" of the software.

**Visualization:**
- Healthy repository: Bright, vibrant colors, smooth animations, energetic feel.
- Unhealthy repository: Muted colors, slower animations, subtle visual tension.
- The UI itself becomes a health indicator.

**Value:** Intuitive emotional understanding. Immediate visual feedback on system health.

**Risk:** Subjectivity. May cause anxiety. Accessibility (color dependence).

---

## Evaluation Criteria for Future Ideas

Before implementing any future idea, evaluate against:

1. **Does it deepen understanding?** (North Star)
2. **Is it evidence-backed?** (First Principles)
3. **Does it work locally?** (Local-First)
4. **Is it explainable?** (Explainability)
5. **Is it accessible?** (Accessibility)
6. **Does it serve a real user need?** (Jobs To Be Done)
7. **Can it be built with zero budget?** (Zero Budget)
8. **Is it maintainable?** (Engineering Standards)

If an idea fails any of these, it is shelved or redesigned.

---

## The Future UI Doctrine

> **Project DNA's UI will evolve as software cognition evolves. Today's dashboard will become tomorrow's immersive experience. But the core principle never changes: every pixel, every animation, every interaction must serve understanding. We do not add features because they are cool. We add features because they help us understand software more completely.**
