import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AnalysisProvider } from './store/analysis';
import Layout from './components/Layout';

import Dashboard from './pages/Dashboard';
import RiskCenter from './pages/RiskCenter';
import EvolutionTimeline from './pages/EvolutionTimeline';
import KnowledgeWorkspace from './pages/KnowledgeWorkspace';
import IntelligenceCenter from './pages/IntelligenceCenter';
import Structural from './pages/Structural';
import Settings from './pages/Settings';

import SelectRepository from './pages/onboarding/SelectRepository';
import ConfigureAnalysis from './pages/onboarding/ConfigureAnalysis';
import AnalysisProgress from './pages/onboarding/AnalysisProgress';
import AnalysisComplete from './pages/onboarding/AnalysisComplete';

import RepositoryExplorer from './pages/RepositoryExplorer';
import GraphWorkspace from './pages/GraphWorkspace';
import CrossRepo from './pages/CrossRepo';
import TeamReview from './pages/TeamReview';
import ActiveReview from './pages/ActiveReview';
import RefactoringRoadmap from './pages/RefactoringRoadmap';
import RefactoringPipeline from './pages/RefactoringPipeline';
import RefactoringVerification from './pages/RefactoringVerification';
import AiAssistant from './pages/AiAssistant';
import CommandPalette from './pages/CommandPalette';
import SearchPalette from './pages/SearchPalette';
import TaskMonitor from './pages/TaskMonitor';
import OrganizationAdmin from './pages/OrganizationAdmin';
import ApiDocs from './pages/ApiDocs';
import WindowOrchestration from './pages/WindowOrchestration';
import SideBySideDiff from './pages/SideBySideDiff';

export default function App() {
  return (
    <AnalysisProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/onboarding" replace />} />
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
            <Route path="/knowledge" element={<KnowledgeWorkspace />} />
            <Route path="/evolution" element={<EvolutionTimeline />} />
            <Route path="/structural" element={<Structural />} />
            <Route path="/settings" element={<Settings />} />

            <Route path="/cross-repo" element={<CrossRepo />} />
            <Route path="/reviews" element={<TeamReview />} />
            <Route path="/reviews/active" element={<ActiveReview />} />
            <Route path="/refactoring" element={<RefactoringRoadmap />} />
            <Route path="/refactoring/pipeline" element={<RefactoringPipeline />} />
            <Route path="/refactoring/verify" element={<RefactoringVerification />} />
            <Route path="/ai-assistant" element={<AiAssistant />} />
            <Route path="/command-palette" element={<CommandPalette />} />
            <Route path="/search" element={<SearchPalette />} />
            <Route path="/notifications" element={<TaskMonitor />} />
            <Route path="/admin" element={<OrganizationAdmin />} />
            <Route path="/api-docs" element={<ApiDocs />} />
            <Route path="/orchestration" element={<WindowOrchestration />} />
            <Route path="/diff" element={<SideBySideDiff />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AnalysisProvider>
  );
}
