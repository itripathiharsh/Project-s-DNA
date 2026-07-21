import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../../store/analysis';

export default function AnalysisProgress() {
  const navigate = useNavigate();
  const { repoPath, selectedBranches, runAnalysisStreamBranch, setActiveBranch } = useAnalysis();
  const [currentBranchIndex, setCurrentBranchIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const [overallError, setOverallError] = useState(null);

  useEffect(() => {
    if (!selectedBranches || selectedBranches.length === 0) {
      navigate('/onboarding');
      return;
    }

    const branch = selectedBranches[currentBranchIndex];
    if (!branch) return;

    setProgress(0);

    const stream = runAnalysisStreamBranch(repoPath, branch, (data) => {
      if (data.type === 'connected') {
        setLogs((prev) => [...prev, { type: '[INFO]', msg: `[${data.branch}] Connection established...`, color: 'text-signal-emerald' }].slice(-20));
      } else if (data.type === 'log') {
        setLogs((prev) => [...prev, { type: '[INFO]', msg: `[${data.branch}] ${data.message}`, color: 'text-signal-emerald' }].slice(-20));
      } else if (data.type === 'progress') {
        if (data.percent !== undefined) setProgress(data.percent);
        const stepLabel = data.step_id ? data.step_id.replace('_', ' ').toUpperCase() : 'STEP';
        const color = data.status === 'success' ? 'text-signal-emerald' : data.status === 'failed' ? 'text-signal-rose' : 'text-signal-cyan';
        setLogs((prev) => [...prev, { type: `[${stepLabel}]`, msg: `[${data.branch}] ${data.message || ''} (${data.status})`, color }].slice(-20));
      } else if (data.type === 'complete') {
        setProgress(100);
        setLogs((prev) => [...prev, { type: '[SUCCESS]', msg: `[${data.branch}] Analysis completed!`, color: 'text-signal-emerald' }].slice(-20));
        
        if (currentBranchIndex < selectedBranches.length - 1) {
          setTimeout(() => setCurrentBranchIndex(prev => prev + 1), 1500);
        } else {
          setTimeout(() => {
            if (selectedBranches.length > 0) {
              setActiveBranch(selectedBranches[0]);
            }
            navigate('/onboarding/complete');
          }, 1500);
        }
      } else if (data.type === 'error') {
        const errMsg = data.message || 'Unknown error occurred.';
        setOverallError(`Error on branch ${data.branch}: ${errMsg}`);
        setLogs((prev) => [...prev, { type: '[ERROR]', msg: `[${data.branch}] ${errMsg}`, color: 'text-signal-rose' }].slice(-20));
      }
    });

    return () => {
      if (stream) stream.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentBranchIndex, repoPath, selectedBranches, runAnalysisStreamBranch, navigate]);

  const circumference = 2 * Math.PI * 44;
  const offset = circumference - (progress / 100) * circumference;
  const overallProgress = ((currentBranchIndex + (progress / 100)) / selectedBranches.length) * 100;

  return (
    <div className="min-h-screen bg-background text-on-surface font-body-md selection:bg-primary/30">
      <header className="fixed top-0 left-0 w-full h-row-height-standard px-gutter flex justify-between items-center bg-background border-b border-border-subtle z-50">
        <div className="flex items-center gap-4">
          <span className="font-headline-md text-headline-md font-bold text-on-surface">Project DNA</span>
          <div className="h-4 w-px bg-border-subtle" />
          <span className="text-primary font-bold border-b-2 border-primary pb-1 font-body-md">Analysis</span>
        </div>
      </header>

      <main className="relative z-10 pt-24 pb-8 flex flex-col items-center justify-center min-h-screen px-gutter">
        <div className="w-full max-w-4xl flex flex-col items-center">
          <div className="relative mb-12 flex flex-col items-center">
            <div className="relative w-48 h-48">
              <svg className="w-full h-full" viewBox="0 0 100 100">
                <circle className="text-surface-container-highest stroke-current" cx="50" cy="50" fill="transparent" r="44" strokeWidth="4" />
                <circle
                  className="text-primary stroke-current progress-ring-circle"
                  cx="50" cy="50" fill="transparent" r="44"
                  strokeDasharray={circumference}
                  strokeDashoffset={offset}
                  strokeLinecap="round" strokeWidth="4"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-[42px] leading-none text-primary font-bold">{Math.floor(progress)}%</span>
                <span className="font-label-caps text-label-caps text-on-surface-variant mt-1">BRANCH</span>
              </div>
            </div>
            
            <div className="w-64 bg-surface-container h-2 rounded-full mt-4 overflow-hidden">
              <div 
                className="bg-primary h-full transition-all duration-300"
                style={{ width: `${overallProgress}%` }}
              />
            </div>
            <div className="text-on-surface-variant text-sm mt-2">
              Overall Progress: {Math.floor(overallProgress)}% ({currentBranchIndex + 1}/{selectedBranches.length} branches)
            </div>

            <div className="mt-6 text-center">
              <h1 className="font-headline-lg text-headline-lg mb-2">
                {overallError ? 'Analysis Failed' : `Analyzing ${selectedBranches[currentBranchIndex]}`}
              </h1>
              <p className="text-on-surface-variant font-body-md max-w-md">
                {overallError ? overallError : 'Project DNA is mapping dependencies and identifying risk patterns.'}
              </p>
            </div>
          </div>

          <div className="w-full bg-[#0D0D0D] border border-border-subtle rounded-lg overflow-hidden shadow-2xl">
            <div className="bg-surface-container px-4 py-2 border-b border-border-subtle flex justify-between items-center">
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-signal-rose/40" />
                <div className="w-2.5 h-2.5 rounded-full bg-signal-amber/40" />
                <div className="w-2.5 h-2.5 rounded-full bg-signal-emerald/40" />
              </div>
              <div className="font-code-sm text-code-sm text-on-surface-variant/60">dna_analysis_engine.log</div>
              <div className="w-12" />
            </div>
            <div className="p-4 h-64 overflow-y-auto font-code-md text-code-md bg-black/40">
              <div className="space-y-1">
                {logs.map((l, i) => (
                  <div key={i} className="flex gap-4">
                    <span className="text-text-muted select-none">{new Date().toLocaleTimeString()}</span>
                    <span className={l.color}>{l.type}</span>
                    <span className="text-on-surface">{l.msg}</span>
                  </div>
                ))}
                {!overallError && (
                  <div className="flex gap-4 items-center">
                    <span className="text-text-muted select-none">{new Date().toLocaleTimeString()}</span>
                    <span className="text-signal-rose animate-pulse-dna">[BUSY]</span>
                    <span className="text-on-surface">Awaiting response from backend…</span>
                    <span className="w-1.5 h-4 bg-primary animate-pulse" />
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex gap-4 mt-8">
            <button onClick={() => navigate('/onboarding')} className="btn-secondary">
              <span className="material-symbols-outlined">arrow_back</span> Cancel
            </button>
            {overallError && (
              <button onClick={() => navigate('/onboarding')} className="btn-primary-lg">
                <span className="material-symbols-outlined">refresh</span> Try Again
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
