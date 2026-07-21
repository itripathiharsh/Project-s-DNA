import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../../store/analysis';
import { useNotification } from '../../components/NotificationContext';

const STEPS = ['Connect', 'Select Branches', 'Analyze', 'Finalize'];

export default function SelectRepository() {
  const [path, setPath] = useState('');
  const [viaUrl, setViaUrl] = useState(false);
  const [loadingInfo, setLoadingInfo] = useState(false);
  const navigate = useNavigate();
  const { setRepoPath, setRepoInfo, data, loading, loadLatest } = useAnalysis();
  const { toast } = useNotification();

  useEffect(() => {
    if (!loading && data && localStorage.getItem('skip_onboarding') === 'true') {
      navigate('/dashboard');
    }
  }, [data, loading, navigate]);

  if (loading) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center gap-4 bg-surface-container-lowest text-on-surface">
        <div className="w-16 h-16 border-4 border-surface-container-high border-t-primary rounded-full animate-spin" />
        <p className="text-on-surface-variant font-body-md">Connecting to analysis server…</p>
      </div>
    );
  }

  async function next(e) {
    e.preventDefault();
    if (!path.trim()) return;
    setLoadingInfo(true);
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const res = await fetch(`${apiBase}/v1/intake/info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url_or_path: path.trim() })
      });
      if (!res.ok) throw new Error('Failed to fetch repository information');
      const info = await res.json();
      setRepoPath(path.trim());
      setRepoInfo(info);
      navigate('/onboarding/configure');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoadingInfo(false);
    }
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-surface-container-lowest">
      <header className="bg-background border-b border-border-subtle flex justify-between items-center px-gutter w-full h-row-height-standard sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <span className="font-headline-md text-headline-md font-bold text-on-surface">Project DNA</span>
          <div className="h-4 w-px bg-border-subtle mx-2" />
          <div className="flex items-center gap-2">
            <span className="text-on-surface-variant font-body-sm">Project DNA</span>
            <span className="material-symbols-outlined text-text-muted">chevron_right</span>
            <span className="text-primary font-bold">Onboarding</span>
          </div>
        </div>
      </header>

      <main className="flex-1 flex flex-col min-w-0">
        <div className="px-8 pt-8 pb-4 border-b border-border-subtle bg-surface-dim">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
              <div className="flex flex-col">
                <h1 className="font-headline-lg text-headline-lg text-on-surface">Connect a Repository</h1>
                <p className="text-text-muted font-body-sm mt-1">Select the source of truth for your architectural blueprint.</p>
              </div>
              <button onClick={() => setViaUrl((v) => !v)} className="bg-primary hover:bg-primary-container text-on-primary px-4 py-2 font-body-sm font-bold flex items-center gap-2 transition-all">
                <span className="material-symbols-outlined">link</span>
                {viaUrl ? 'Use Local Path' : 'Import from URL'}
              </button>
            </div>
            <div className="flex items-center gap-4 w-full">
              {STEPS.map((s, i) => (
                <div key={s} className="flex items-center gap-2 flex-1 last:flex-none">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${i === 0 ? 'bg-primary' : 'border-2 border-border-subtle'}`}>
                    {i === 0 ? (
                      <span className="material-symbols-outlined text-[14px] text-on-primary">check</span>
                    ) : (
                      <span className="text-[11px] font-bold text-text-muted">{i + 1}</span>
                    )}
                  </div>
                  <span className={`font-body-sm ${i === 0 ? 'text-primary font-bold' : 'text-text-muted'}`}>{s}</span>
                  {i < STEPS.length - 1 && <div className="h-[2px] flex-1 bg-border-subtle" />}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-surface-container-low border border-border-subtle p-6 rounded-lg">
              <h2 className="font-headline-md text-headline-md mb-1 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">folder_open</span>
                Repository Path or URL
              </h2>
              <p className="text-on-surface-variant font-body-sm mb-4">
                Enter the absolute path to a local repository or a GitHub HTTPS URL.
              </p>
              <form onSubmit={next} className="flex flex-col gap-4">
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">terminal</span>
                  <input
                    autoFocus
                    type="text"
                    value={path}
                    onChange={(e) => setPath(e.target.value)}
                    placeholder={viaUrl ? 'https://github.com/owner/repo' : 'C:\\projects\\my-repo'}
                    className="w-full bg-surface-container-lowest border border-border-subtle pl-10 pr-4 h-row-height-standard text-on-surface font-code-md focus:border-primary focus:ring-0 outline-none transition-colors rounded"
                  />
                </div>
              </form>
            </div>
          </div>
        </div>

        <div className="px-8 h-row-height-standard bg-surface-container-low border-t border-border-subtle flex items-center justify-between z-10">
          <div className="flex items-center gap-3 text-text-muted font-body-sm">
            <span className="material-symbols-outlined text-[16px]">info</span>
            <span>{path.trim() ? 'Ready to fetch information.' : 'No repository selected yet.'}</span>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={async () => {
                localStorage.setItem('skip_onboarding', 'true');
                if (loadLatest) {
                  await loadLatest();
                }
                navigate('/dashboard');
              }}
              className="text-on-surface-variant font-body-sm hover:text-on-surface transition-colors"
            >
              Skip
            </button>
            <button onClick={next} disabled={!path.trim() || loadingInfo} className="bg-primary hover:bg-primary-container text-on-primary px-6 h-8 font-body-sm font-bold transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
              {loadingInfo ? 'Fetching...' : 'Next: Branches'}
              <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
