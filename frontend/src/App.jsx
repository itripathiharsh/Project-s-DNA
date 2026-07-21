import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AnalysisProvider } from './store/analysis';
import { NotificationProvider } from './components/NotificationContext';
import Layout from './components/Layout';

// Lazily load route components for code splitting
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const RiskCenter = React.lazy(() => import('./pages/RiskCenter'));
const EvolutionTimeline = React.lazy(() => import('./pages/EvolutionTimeline'));
const KnowledgeWorkspace = React.lazy(() => import('./pages/KnowledgeWorkspace'));
const IntelligenceCenter = React.lazy(() => import('./pages/IntelligenceCenter'));
const Structural = React.lazy(() => import('./pages/Structural'));
const Settings = React.lazy(() => import('./pages/Settings'));
const ComplexityHeatmap = React.lazy(() => import('./pages/ComplexityHeatmap'));
const ChangeHeatmap = React.lazy(() => import('./pages/ChangeHeatmap'));
const OwnershipHeatmap = React.lazy(() => import('./pages/OwnershipHeatmap'));
const SecurityHeatmap = React.lazy(() => import('./pages/SecurityHeatmap'));
const PerformanceHeatmap = React.lazy(() => import('./pages/PerformanceHeatmap'));
const CouplingHeatmap = React.lazy(() => import('./pages/CouplingHeatmap'));
const DependencyHeatmap = React.lazy(() => import('./pages/DependencyHeatmap'));
const FolderHeatmap = React.lazy(() => import('./pages/FolderHeatmap'));
const RiskHeatmap = React.lazy(() => import('./pages/RiskHeatmap'));
const GitActivityHeatmap = React.lazy(() => import('./pages/GitActivityHeatmap'));
const PredictiveAnalytics = React.lazy(() => import('./pages/PredictiveAnalytics'));
const RefactoringSuite = React.lazy(() => import('./pages/RefactoringSuite'));
const FlowJourneys = React.lazy(() => import('./pages/FlowJourneys'));
const DocumentationHub = React.lazy(() => import('./pages/DocumentationHub'));
const Landing = React.lazy(() => import('./pages/Landing'));

const SelectRepository = React.lazy(() => import('./pages/onboarding/SelectRepository'));
const ConfigureAnalysis = React.lazy(() => import('./pages/onboarding/ConfigureAnalysis'));
const AnalysisProgress = React.lazy(() => import('./pages/onboarding/AnalysisProgress'));
const AnalysisComplete = React.lazy(() => import('./pages/onboarding/AnalysisComplete'));

const RepositoryExplorer = React.lazy(() => import('./pages/RepositoryExplorer'));
const GraphWorkspace = React.lazy(() => import('./pages/GraphWorkspace'));
const CrossRepo = React.lazy(() => import('./pages/CrossRepo'));
const TeamReview = React.lazy(() => import('./pages/TeamReview'));
const ActiveReview = React.lazy(() => import('./pages/ActiveReview'));
const RefactoringRoadmap = React.lazy(() => import('./pages/RefactoringRoadmap'));
const RefactoringPipeline = React.lazy(() => import('./pages/RefactoringPipeline'));
const RefactoringVerification = React.lazy(() => import('./pages/RefactoringVerification'));
const AiAssistant = React.lazy(() => import('./pages/AiAssistant'));
const CommandPalette = React.lazy(() => import('./pages/CommandPalette'));
const SearchPalette = React.lazy(() => import('./pages/SearchPalette'));
const TaskMonitor = React.lazy(() => import('./pages/TaskMonitor'));
const OrganizationAdmin = React.lazy(() => import('./pages/OrganizationAdmin'));
const ApiDocs = React.lazy(() => import('./pages/ApiDocs'));
const WindowOrchestration = React.lazy(() => import('./pages/WindowOrchestration'));
const SideBySideDiff = React.lazy(() => import('./pages/SideBySideDiff'));
const NotFound = React.lazy(() => import('./pages/NotFound'));

const LoadingFallback = () => (
  <div className="flex h-screen w-full items-center justify-center bg-gray-50 dark:bg-gray-900">
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-t-2 border-blue-600 dark:border-blue-400"></div>
      <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Loading module...</p>
    </div>
  </div>
);

import ErrorBoundary from './components/ErrorBoundary';

export default function App() {
  return (
    <ErrorBoundary>
    <AnalysisProvider>
      <NotificationProvider>
        <BrowserRouter>
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/onboarding" element={<SelectRepository />} />
              <Route path="/onboarding/configure" element={<ConfigureAnalysis />} />
              <Route path="/onboarding/analyze" element={<AnalysisProgress />} />
              <Route path="/onboarding/complete" element={<AnalysisComplete />} />

              <Route element={<Layout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/explorer" element={<RepositoryExplorer />} />
                <Route path="/graph" element={<GraphWorkspace />} />
                <Route path="/intelligence" element={<IntelligenceCenter />} />
                <Route path="/risk" element={<RiskCenter />} />
                <Route path="/predictive" element={<PredictiveAnalytics />} />
                <Route path="/knowledge" element={<KnowledgeWorkspace />} />
                <Route path="/evolution" element={<EvolutionTimeline />} />
                <Route path="/structural" element={<Structural />} />
                <Route path="/settings" element={<Settings />} />

                <Route path="/heatmaps/complexity" element={<ComplexityHeatmap />} />
                <Route path="/heatmaps/change" element={<ChangeHeatmap />} />
                <Route path="/heatmaps/ownership" element={<OwnershipHeatmap />} />
                <Route path="/heatmaps/security" element={<SecurityHeatmap />} />
                <Route path="/heatmaps/performance" element={<PerformanceHeatmap />} />
                <Route path="/heatmaps/coupling" element={<CouplingHeatmap />} />
                <Route path="/heatmaps/dependency" element={<DependencyHeatmap />} />
                <Route path="/heatmaps/folder" element={<FolderHeatmap />} />
                <Route path="/heatmaps/risk" element={<RiskHeatmap />} />
                <Route path="/heatmaps/git-activity" element={<GitActivityHeatmap />} />

                <Route path="/cross-repo" element={<CrossRepo />} />
                <Route path="/reviews" element={<TeamReview />} />
                <Route path="/reviews/active" element={<ActiveReview />} />
                <Route path="/refactoring" element={<RefactoringRoadmap />} />
                <Route path="/refactoring/pipeline" element={<RefactoringPipeline />} />
                <Route path="/refactoring/verify" element={<RefactoringVerification />} />
                <Route path="/refactoring-suite" element={<RefactoringSuite />} />
                <Route path="/flow-journeys" element={<FlowJourneys />} />
                <Route path="/documentation" element={<DocumentationHub />} />
                <Route path="/ai-assistant" element={<AiAssistant />} />
                <Route path="/command-palette" element={<CommandPalette />} />
                <Route path="/search" element={<SearchPalette />} />
                <Route path="/notifications" element={<TaskMonitor />} />
                <Route path="/admin" element={<OrganizationAdmin />} />
                <Route path="/api-docs" element={<ApiDocs />} />
                <Route path="/orchestration" element={<WindowOrchestration />} />
                <Route path="/diff" element={<SideBySideDiff />} />
                <Route path="*" element={<NotFound />} />
              </Route>
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </NotificationProvider>
    </AnalysisProvider>
    </ErrorBoundary>
  );
}
