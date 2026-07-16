import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../../store/analysis';

const FAKE_LOGS = [
  { type: '[INFO]', msg: 'Initializing AST extraction...', color: 'text-signal-emerald' },
  { type: '[TASK]', msg: 'Parsing module boundaries...', color: 'text-signal-cyan' },
  { type: '[INFO]', msg: 'Analyzing call-graphs...', color: 'text-signal-emerald' },
  { type: '[WARN]', msg: 'Checking circular dependencies...', color: 'text-signal-amber' },
  { type: '[TASK]', msg: 'Generating knowledge graph metadata...', color: 'text-signal-cyan' },
  { type: '[INFO]', msg: 'Running engines: structural, evolution, knowledge, risk...', color: 'text-signal-emerald' },
  { type: '[TASK]', msg: 'Generating insights from evidence...', color: 'text-signal-cyan' },
];

export default function AnalysisProgress() {
  const navigate = useNavigate();
  const { repoPath, runAnalysisStream, error } = useAnalysis();
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  useEffect(() => {
    // Reset local state
    setProgress(0);
    setLogs([]);

    const stream = runAnalysisStream(repoPath, (data) => {
      if (data.type === 'connected') {
        setLogs((prev) => [
          ...prev,
          { type: '[INFO]', msg: 'Connection established with analysis stream.', color: 'text-signal-emerald' }
        ].slice(-20));
      } else if (data.type === 'log') {
        setLogs((prev) => [
          ...prev,
          { type: '[INFO]', msg: data.message, color: 'text-signal-emerald' }
        ].slice(-20));
      } else if (data.type === 'progress') {
        if (data.percent !== undefined) {
          setProgress(data.percent);
        }
        const stepLabel = data.step_id ? data.step_id.replace('_', ' ').toUpperCase() : 'STEP';
        const color = data.status === 'success' ? 'text-signal-emerald' : data.status === 'failed' ? 'text-signal-rose' : 'text-signal-cyan';
        setLogs((prev) => [
          ...prev,
          { type: `[${stepLabel}]`, msg: `${data.message || ''} (${data.status})`, color }
        ].slice(-20));
      } else if (data.type === 'complete') {
        setProgress(100);
        setLogs((prev) => [
          ...prev,
          { type: '[SUCCESS]', msg: 'Analysis completed successfully!', color: 'text-signal-emerald' }
        ].slice(-20));
        setTimeout(() => navigate('/onboarding/complete'), 1000);
      } else if (data.type === 'error') {
        const errMsg = data.message || 'An unknown error occurred during analysis.';
        setLogs((prev) => [
          ...prev,
          { type: '[ERROR]', msg: errMsg, color: 'text-signal-rose' }
        ].slice(-20));
      }
    });

    return () => {
      if (stream) {
        stream.close();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repoPath, navigate, runAnalysisStream]);

  const circumference = 2 * Math.PI * 44;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className="min-h-screen bg-background text-on-surface font-body-md selection:bg-primary/30">
      <header className="fixed top-0 left-0 w-full h-row-height-standard px-gutter flex justify-between items-center bg-background border-b border-border-subtle z-50">
        <div className="flex items-center gap-4">
          <span className="font-headline-md text-headline-md font-bold text-on-surface">Project DNA</span>
          <div className="h-4 w-px bg-border-subtle" />
          <span className="text-primary font-bold border-b-2 border-primary pb-1 font-body-md">Analysis</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-on-surface">settings</span>
          <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-on-surface">help</span>
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
                <span className="font-label-caps text-label-caps text-on-surface-variant mt-1">PROCESSED</span>
              </div>
            </div>
            <div className="mt-6 text-center">
              <h1 className="font-headline-lg text-headline-lg mb-2">
                {error ? 'Analysis Failed' : 'Building Knowledge Graph'}
              </h1>
              <p className="text-on-surface-variant font-body-md max-w-md">
                {error ? error : 'Project DNA is mapping dependencies and identifying risk patterns for ' + (repoPath || 'your repository') + '.'}
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
                <div className="flex gap-4">
                  <span className="text-text-muted select-none">{new Date().toLocaleTimeString()}</span>
                  <span className="text-signal-emerald">[INFO]</span>
                  <span className="text-on-surface">POST /v1/analyze — repo_path={repoPath || '…'}</span>
                </div>
                {logs.map((l, i) => (
                  <div key={i} className="flex gap-4">
                    <span className="text-text-muted select-none">{new Date().toLocaleTimeString()}</span>
                    <span className={l.color}>{l.type}</span>
                    <span className="text-on-surface">{l.msg}</span>
                  </div>
                ))}
                {!error && (
                  <div className="flex gap-4 items-center">
                    <span className="text-text-muted select-none">{new Date().toLocaleTimeString()}</span>
                    <span className="text-signal-rose animate-pulse-dna">[BUSY]</span>
                    <span className="text-on-surface">Awaiting response from backend…</span>
                    <span className="w-1.5 h-4 bg-primary animate-pulse" />
                  </div>
                )}
                {error && (
                  <div className="flex gap-4">
                    <span className="text-text-muted select-none">{new Date().toLocaleTimeString()}</span>
                    <span className="text-signal-rose">[ERROR]</span>
                    <span className="text-signal-rose">{error}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex gap-4 mt-8">
            <button onClick={() => navigate('/onboarding')} className="btn-secondary">
              <span className="material-symbols-outlined">arrow_back</span> Back
            </button>
            {error && (
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
