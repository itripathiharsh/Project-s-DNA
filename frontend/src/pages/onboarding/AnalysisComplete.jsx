import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../../store/analysis';

export default function AnalysisComplete() {
  const navigate = useNavigate();
  const { data, repoPath } = useAnalysis();
  const summary = data?.summary ?? {};

  return (
    <div className="min-h-screen bg-background text-on-surface font-body-md flex flex-col">
      <header className="fixed top-0 left-0 right-0 h-row-height-standard flex justify-between items-center px-gutter bg-background/60 backdrop-blur-sm z-20">
        <span className="font-headline-md text-headline-md font-bold text-on-surface">Project DNA</span>
        <div className="flex items-center gap-6">
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => <div key={i} className="w-2 h-2 rounded-full bg-primary/20" />)}
            <div className="w-2 h-2 rounded-full bg-primary ring-4 ring-primary/20" />
          </div>
          <span className="font-label-caps text-label-caps text-primary uppercase">Exploration Ready</span>
        </div>
      </header>

      <main className="relative z-10 flex flex-col items-center justify-center min-h-screen px-gutter pt-16">
        <div className="max-w-4xl w-full flex flex-col items-center gap-8">
          <div className="relative">
            <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full scale-150 animate-pulse" />
            <div className="relative w-24 h-24 rounded-full bg-surface-container-highest border-2 border-primary flex items-center justify-center">
              <span className="material-symbols-outlined text-primary text-[48px]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
            </div>
          </div>

          <div className="text-center space-y-2">
            <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">Analysis Complete</h1>
            <p className="text-on-surface-variant font-body-md max-w-lg mx-auto">
              The analysis for <span className="font-code-md text-code-md text-primary">{repoPath || 'your repository'}</span> has finalized. Your insights are ready for deep inspection.
            </p>
          </div>

          <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
            <div className="card-glass p-6 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <span className="font-label-caps text-label-caps text-text-muted uppercase">Files Indexed</span>
                <span className="material-symbols-outlined text-primary">hub</span>
              </div>
              <div className="text-[32px] font-bold text-on-surface leading-none">{summary.total_files ?? '—'}</div>
              <div className="font-body-sm text-body-sm text-on-surface-variant">{summary.source_files ?? 0} source · {summary.test_files ?? 0} test</div>
            </div>
            <div className="card-glass p-6 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <span className="font-label-caps text-label-caps text-text-muted uppercase">Commits</span>
                <span className="material-symbols-outlined text-signal-cyan">history</span>
              </div>
              <div className="text-[32px] font-bold text-on-surface leading-none">{summary.total_commits ?? '—'}</div>
              <div className="font-body-sm text-body-sm text-on-surface-variant">{summary.total_authors ?? 0} authors</div>
            </div>
            <div className="card-glass p-6 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <span className="font-label-caps text-label-caps text-text-muted uppercase">Insights</span>
                <span className="material-symbols-outlined text-signal-emerald">psychology</span>
              </div>
              <div className="text-[32px] font-bold text-on-surface leading-none">{data?.insights?.length ?? '—'}</div>
              <div className="font-body-sm text-body-sm text-on-surface-variant">reasoning-generated</div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 w-full justify-center pt-6">
            <button onClick={() => navigate('/graph')} className="btn-primary-lg">
              <span className="material-symbols-outlined">rocket_launch</span>
              Enter Graph Workspace
            </button>
            <button onClick={() => navigate('/dashboard')} className="btn-secondary">
              <span className="material-symbols-outlined">dashboard</span>
              View Dashboard
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
