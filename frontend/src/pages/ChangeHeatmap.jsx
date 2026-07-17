import { useState, useEffect } from 'react';
import { getChangeHeatmap } from '../services/api';
import PageHeader from '../components/PageHeader';

export default function ChangeHeatmap() {
  const [timeFilter, setTimeFilter] = useState('all');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedCommit, setSelectedCommit] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await getChangeHeatmap(timeFilter);
        setData(result);
        if (result.file_changes && result.file_changes.length > 0) {
          setSelectedFile(result.file_changes[0]);
        }
        if (result.commits && result.commits.length > 0) {
          setSelectedCommit(result.commits[0]);
        }
      } catch (err) {
        console.error('Error fetching change heatmap:', err);
        setError(err.message || 'Failed to fetch change metrics.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [timeFilter]);

  const getChurnColor = (churn) => {
    if (churn >= 500) return 'bg-signal-rose/20 border-signal-rose text-signal-rose shadow-[0_0_15px_rgba(255,0,127,0.1)]';
    if (churn >= 150) return 'bg-signal-amber/20 border-signal-amber text-signal-amber';
    if (churn >= 50) return 'bg-primary/20 border-primary text-primary';
    return 'bg-signal-emerald/10 border-signal-emerald/40 text-signal-emerald';
  };

  const getRelativeDate = (isoString) => {
    if (!isoString) return 'never';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return isoString;
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-[36px] text-primary animate-spin">sync</span>
          <span className="text-xs text-text-muted">Reconstructing Git evolution history...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 text-center max-w-md mx-auto">
        <span className="material-symbols-outlined text-[48px] text-signal-rose mb-3">error</span>
        <h3 className="font-bold text-base text-on-surface">Analysis Error</h3>
        <p className="text-xs text-text-muted mt-2">{error}</p>
      </div>
    );
  }

  const fileChanges = data?.file_changes || [];
  const commits = data?.commits || [];

  return (
    <>
      <PageHeader 
        title="Evolution & Change Heatmap" 
        subtitle="Git code churn, change frequency, and active evolution hotspots" 
      />
      <div className="p-6 flex flex-col xl:flex-row gap-6 max-w-[1600px] mx-auto w-full flex-1">
        {/* Main Panel with Filter & Heatmap Grid */}
        <div className="flex-1 flex flex-col gap-6 min-w-0">
          
          {/* Controls / Filter */}
          <div className="card-base flex items-center justify-between">
            <span className="text-xs uppercase font-bold text-text-muted">History Horizon:</span>
            <div className="flex items-center gap-1.5 bg-[#12121e] border border-border-subtle rounded-lg p-1">
              {[
                { id: '7d', label: '7 Days' },
                { id: '30d', label: '30 Days' },
                { id: '90d', label: '90 Days' },
                { id: 'all', label: 'All History' },
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTimeFilter(t.id)}
                  className={`px-3 py-1 rounded-md text-[11px] font-bold uppercase transition-all duration-200 ${timeFilter === t.id ? 'bg-primary text-white shadow-md' : 'text-text-muted hover:text-on-surface'}`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          {/* Grid Panel */}
          <div className="card-base flex-1 flex flex-col min-h-[350px]">
            <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Evolution Hotspots Matrix</h3>
                <p className="text-[10px] text-text-muted mt-0.5">Sized by change count, color-coded by absolute line churn.</p>
              </div>
              <div className="flex items-center gap-3 text-[9px] text-text-muted">
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-signal-emerald/20 border border-signal-emerald/40 inline-block"/> &lt;50 lines</span>
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-primary/20 border border-primary/40 inline-block"/> &lt;150 lines</span>
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-signal-amber/20 border border-signal-amber/40 inline-block"/> &lt;500 lines</span>
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-signal-rose/20 border border-signal-rose/40 inline-block"/> 500+ lines</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 overflow-y-auto max-h-[400px] pr-1">
              {fileChanges.map((f, i) => {
                const active = selectedFile?.file_path === f.file_path;
                return (
                  <div
                    key={i}
                    onClick={() => setSelectedFile(f)}
                    className={`p-3.5 rounded-lg border cursor-pointer transition-all duration-300 hover:scale-[1.02] flex flex-col justify-between ${getChurnColor(f.churn)} ${active ? 'ring-2 ring-primary ring-offset-2 ring-offset-[#09090e] border-transparent' : ''}`}
                  >
                    <div className="min-w-0">
                      <div className="font-mono text-xs font-semibold truncate text-on-surface" title={f.file_path}>
                        {f.file_path.split('/').pop()}
                      </div>
                      <div className="text-[10px] opacity-75 truncate mt-0.5" title={f.file_path}>
                        {f.file_path}
                      </div>
                    </div>

                    <div className="flex justify-between items-end mt-4 pt-2 border-t border-white/5">
                      <div className="flex flex-col gap-0.5 text-[9px] opacity-75">
                        <span>Commits: <strong className="text-on-surface font-extrabold">{f.commits_count}</strong></span>
                        <span className="flex items-center gap-1">
                          Churn: 
                          <strong className="text-on-surface font-extrabold flex items-center gap-0.5">
                            <span className="text-signal-emerald">+{f.insertions}</span>
                            <span className="text-signal-rose">-{f.deletions}</span>
                          </strong>
                        </span>
                      </div>
                      <div className="text-right text-[9px] opacity-60">
                        Modified: {getRelativeDate(f.last_modified)}
                      </div>
                    </div>
                  </div>
                );
              })}
              {fileChanges.length === 0 && (
                <div className="col-span-full py-16 text-center text-text-muted text-xs">No files modified in the selected timeframe.</div>
              )}
            </div>
          </div>

          {/* Commits Timeline Panel */}
          <div className="card-base flex-1 flex flex-col min-h-[300px]">
            <div className="border-b border-border-subtle/50 pb-3 mb-4">
              <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Commit Log Activity</h3>
              <p className="text-[10px] text-text-muted mt-0.5">Chronological record of commits affecting the repository in this window.</p>
            </div>
            
            <div className="space-y-2 overflow-y-auto max-h-[300px] pr-1">
              {commits.map((c, i) => {
                const active = selectedCommit?.hash === c.hash;
                return (
                  <div
                    key={i}
                    onClick={() => setSelectedCommit(c)}
                    className={`p-3 rounded-lg border transition-all duration-200 cursor-pointer flex items-center justify-between ${active ? 'bg-primary/10 border-primary/30' : 'bg-surface-container-low/40 border-border-subtle/40 hover:bg-surface-container-high/20'}`}
                  >
                    <div className="min-w-0 pr-4 flex-1">
                      <div className="flex items-center gap-2">
                        <code className="font-code-sm text-[10px] text-primary bg-[#12121e] px-1.5 py-0.5 rounded font-extrabold">{c.hash?.slice(0, 7)}</code>
                        <span className="text-xs font-semibold truncate text-on-surface">{c.message}</span>
                      </div>
                      <div className="text-[10px] text-text-muted mt-1.5 flex items-center gap-2">
                        <span className="font-medium text-on-surface-variant flex items-center gap-0.5">
                          <span className="material-symbols-outlined text-[12px]">person</span> {c.author}
                        </span>
                        <span>•</span>
                        <span>{getRelativeDate(c.date)}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2.5 flex-shrink-0">
                      <span className="badge badge-info">{c.files?.length ?? 0} files</span>
                      <span className="material-symbols-outlined text-text-muted text-[15px] select-none">
                        {active ? 'keyboard_arrow_right' : 'chevron_right'}
                      </span>
                    </div>
                  </div>
                );
              })}
              {commits.length === 0 && (
                <div className="py-12 text-center text-text-muted text-xs">No commits found in the selected timeframe.</div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar Info/Detail Panel */}
        <div className="w-full xl:w-[400px] shrink-0 flex flex-col gap-6">
          
          {/* File Evolution Details */}
          <div className="card-base">
            <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">history</span>
              <div>
                <h3 className="font-bold text-xs uppercase tracking-wider text-on-surface">Hotspot Details</h3>
                <p className="text-[10px] text-text-muted">Per-file git metadata drill-down</p>
              </div>
            </div>

            {selectedFile ? (
              <div className="flex flex-col gap-4 text-xs">
                <div className="bg-[#12121e] border border-border-subtle rounded-lg p-3">
                  <span className="text-[9px] font-bold text-primary uppercase tracking-widest block mb-1">Target File</span>
                  <div className="font-mono text-xs text-on-surface break-all font-semibold leading-normal">
                    {selectedFile.file_path}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg text-center">
                    <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-0.5">Commit Frequency</span>
                    <span className="text-lg font-extrabold text-on-surface">{selectedFile.commits_count}</span>
                  </div>
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg text-center">
                    <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-0.5">Line Churn</span>
                    <span className="text-lg font-extrabold text-primary">{selectedFile.churn}</span>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <div className="flex justify-between items-center py-1.5 border-b border-border-subtle/40">
                    <span className="text-text-muted">Added Lines</span>
                    <span className="font-bold text-signal-emerald">+{selectedFile.insertions}</span>
                  </div>
                  <div className="flex justify-between items-center py-1.5 border-b border-border-subtle/40">
                    <span className="text-text-muted">Deleted Lines</span>
                    <span className="font-bold text-signal-rose">-{selectedFile.deletions}</span>
                  </div>
                  <div className="flex justify-between items-center py-1.5 border-b border-border-subtle/40">
                    <span className="text-text-muted">Last Modification</span>
                    <span className="font-semibold text-on-surface">{getRelativeDate(selectedFile.last_modified)}</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-text-muted text-center py-10">Select a hotspot block to review details.</p>
            )}
          </div>

          {/* Commit Drift Files list */}
          <div className="card-base">
            <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">commit</span>
              <div>
                <h3 className="font-bold text-xs uppercase tracking-wider text-on-surface">Commit Details</h3>
                <p className="text-[10px] text-text-muted">Files affected in active commit selection</p>
              </div>
            </div>

            {selectedCommit ? (
              <div className="flex flex-col gap-4 text-xs">
                <div className="bg-[#12121e] border border-border-subtle rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[9px] font-bold text-primary uppercase tracking-widest">Commit SHA</span>
                    <code className="text-[9px] text-text-muted">{selectedCommit.hash}</code>
                  </div>
                  <div className="font-semibold text-xs text-on-surface leading-snug">
                    {selectedCommit.message}
                  </div>
                </div>

                <div>
                  <span className="text-[9px] font-bold text-text-muted uppercase tracking-widest block mb-2">Affected Files ({selectedCommit.files?.length ?? 0})</span>
                  <div className="flex flex-col gap-2 max-h-[220px] overflow-y-auto pr-1">
                    {selectedCommit.files?.map((f, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                        <div className="min-w-0 pr-4 flex-1">
                          <code className="font-code-sm text-[10px] text-on-surface truncate block" title={f.file_path}>{f.file_path}</code>
                        </div>
                        <div className="flex items-center gap-1.5 text-[9px] font-extrabold flex-shrink-0">
                          <span className="text-signal-emerald">+{f.insertions}</span>
                          <span className="text-signal-rose">-{f.deletions}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-text-muted text-center py-10">Select a commit log item to inspect files.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
