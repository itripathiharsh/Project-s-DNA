import PageHeader from '../components/PageHeader';
import NotAvailable from '../components/NotAvailable';

function Stub({ title, subtitle, icon, description }) {
  return (
    <>
      <PageHeader title={title} subtitle={subtitle} />
      <NotAvailable title={title} icon={icon} description={description} />
    </>
  );
}

export const RepositoryExplorer = () => (
  <Stub
    title="Repository Explorer" icon="folder_open"
    subtitle="Browse files & symbols"
    description="The explorer navigation is live. Per-file symbol browsing requires the /v1/entities backend listing to be wired into a tree view."
  />
);
export const GraphWorkspace = () => (
  <Stub
    title="Graph Workspace" icon="account_tree"
    subtitle="Dependency graph visualization"
    description="An interactive node-link graph view is part of the unified UX. Wiring it to the dependency graph data requires a graph rendering backend / visualization library."
  />
);
export const CrossRepo = () => (
  <Stub
    title="Cross-Repository Analysis" icon="compare"
    subtitle="Compare multiple repositories"
    description="Cross-repo analysis is part of the product UX roadmap. It needs a multi-repo backend workflow that is not yet implemented."
  />
);
export const TeamReview = () => (
  <Stub
    title="Team Review" icon="rate_review"
    subtitle="Review sessions"
    description="Team review sessions are part of the unified experience and require a collaboration backend."
  />
);
export const ActiveReview = () => (
  <Stub
    title="Active Review Session" icon="rate_review"
    subtitle="Live review"
    description="Live review sessions require a sessions backend and are therefore shown disabled."
  />
);
export const RefactoringRoadmap = () => (
  <Stub
    title="Refactoring Roadmap" icon="construction"
    subtitle="Plan refactors"
    description="Refactoring planning requires a backend that maps insights to actionable tasks."
  />
);
export const RefactoringPipeline = () => (
  <Stub
    title="Refactoring Execution Pipeline" icon="construction"
    subtitle="Execute refactors"
    description="Refactor execution requires a change-management backend."
  />
);
export const RefactoringVerification = () => (
  <Stub
    title="Refactoring Verification & Impact" icon="fact_check"
    subtitle="Verify refactors"
    description="Impact verification needs a diff/impact backend."
  />
);
export const AiAssistant = () => (
  <Stub
    title="DNA AI Assistant" icon="smart_toy"
    subtitle="Conversational codebase queries"
    description="The AI assistant requires an LLM backend. No AI/LLM calls exist in the current backend, so this is shown disabled without fabricated responses."
  />
);
export const CommandPalette = () => (
  <Stub
    title="Command Palette" icon="keyboard_command_key"
    subtitle="Quick navigation"
    description="A global command palette is part of the UX. It will index routes and actions once wired to a backend search index."
  />
);
export const SearchPalette = () => (
  <Stub
    title="Search" icon="search"
    subtitle="Full-text & symbol search"
    description="Full-text/symbol search requires a search index backend."
  />
);
export const TaskMonitor = () => (
  <Stub
    title="Task Monitor & Notifications" icon="notifications"
    subtitle="Background jobs"
    description="A task monitor needs a background-job backend. The current analysis runs synchronously."
  />
);
export const OrganizationAdmin = () => (
  <Stub
    title="Organization Admin" icon="corporate_fare"
    subtitle="Teams & members"
    description="Organization administration requires an auth/teams backend."
  />
);
export const ApiDocs = () => (
  <Stub
    title="API Documentation" icon="description"
    subtitle="REST API reference"
    description="The interactive API docs portal is part of the UX. The live OpenAPI spec is available at /docs on the backend."
  />
);
export const WindowOrchestration = () => (
  <Stub
    title="Window Orchestration" icon="grid_view"
    subtitle="Multi-pane layouts"
    description="Multi-pane window orchestration is a workspace layout feature requiring a persisted-layout backend."
  />
);
export const SideBySideDiff = () => (
  <Stub
    title="Side-by-Side Diff Verification" icon="difference"
    subtitle="Compare changes"
    description="Diff verification requires a source-diff backend."
  />
);

export default Stub;
