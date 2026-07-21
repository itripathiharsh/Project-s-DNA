import { useState, useEffect } from 'react';
import { useAnalysis } from '../store/analysis';
import { postBenchmarkingDiff } from '../services/api';

export default function BranchDiff() {
  const { selectedBranches } = useAnalysis();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [baseBranch, setBaseBranch] = useState('');
  const [compareBranch, setCompareBranch] = useState('');

  useEffect(() => {
    if (selectedBranches && selectedBranches.length >= 2) {
      if (!baseBranch) setBaseBranch(selectedBranches[0]);
      if (!compareBranch) setCompareBranch(selectedBranches[1]);
    }
  }, [selectedBranches, baseBranch, compareBranch]);

  useEffect(() => {
    async function load() {
      if (!baseBranch || !compareBranch || baseBranch === compareBranch) {
        setLoading(false);
        setData(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const res = await postBenchmarkingDiff(baseBranch, compareBranch);
        setData(res);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [baseBranch, compareBranch]);

  if (!selectedBranches || selectedBranches.length < 2) {
    return (
      <div className="p-8 text-center text-on-surface-variant flex flex-col items-center justify-center min-h-[300px]">
        <span className="material-symbols-outlined text-[48px] text-primary mb-4 opacity-50">difference</span>
        <h3 className="font-headline-md mb-2">Insufficient Branches</h3>
        <p>You need to select and analyze at least two branches to view diffs.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="card-base p-6 border border-border-subtle">
        <div className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4">
          <h3 className="font-headline-md text-headline-md flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">difference</span>
            Branch Comparison
          </h3>
          <div className="flex items-center gap-4 bg-surface-container p-2 rounded border border-border-subtle">
            <select 
              value={baseBranch} 
              onChange={e => setBaseBranch(e.target.value)}
              className="bg-surface-container-high text-on-surface border border-border-subtle p-2 rounded text-sm outline-none focus:border-primary"
            >
              {selectedBranches.map(b => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
            <span className="material-symbols-outlined text-text-muted">arrow_right_alt</span>
            <select 
              value={compareBranch} 
              onChange={e => setCompareBranch(e.target.value)}
              className="bg-surface-container-high text-on-surface border border-border-subtle p-2 rounded text-sm outline-none focus:border-primary"
            >
              {selectedBranches.map(b => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="py-12 text-center text-text-muted">Calculating diff...</div>
        ) : error ? (
          <div className="py-12 text-center text-signal-rose">Error: {error}</div>
        ) : !data ? (
          <div className="py-12 text-center text-on-surface-variant">Please select different branches to compare.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Overview Stats */}
            <div className="flex flex-col gap-4">
              <h4 className="font-label-caps text-text-muted">Changes Overview</h4>
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-surface-container border border-border-subtle p-4 rounded text-center">
                  <span className="text-3xl font-bold text-signal-emerald">+{data.files_added}</span>
                  <span className="block text-[10px] text-text-muted mt-1 uppercase font-bold">Files Added</span>
                </div>
                <div className="bg-surface-container border border-border-subtle p-4 rounded text-center">
                  <span className="text-3xl font-bold text-signal-rose">-{data.files_removed}</span>
                  <span className="block text-[10px] text-text-muted mt-1 uppercase font-bold">Files Removed</span>
                </div>
                <div className="bg-surface-container border border-border-subtle p-4 rounded text-center">
                  <span className="text-3xl font-bold text-signal-cyan">~{data.files_modified}</span>
                  <span className="block text-[10px] text-text-muted mt-1 uppercase font-bold">Files Modified</span>
                </div>
              </div>
              
              <h4 className="font-label-caps text-text-muted mt-4">Structural Impact</h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-surface-container border border-border-subtle p-4 rounded text-center">
                  <span className={`text-2xl font-bold ${data.complexity_difference > 0 ? 'text-signal-rose' : 'text-signal-emerald'}`}>
                    {data.complexity_difference > 0 ? '+' : ''}{data.complexity_difference}
                  </span>
                  <span className="block text-[10px] text-text-muted mt-1 uppercase font-bold">Complexity Delta</span>
                </div>
                <div className="bg-surface-container border border-border-subtle p-4 rounded text-center">
                  <span className={`text-2xl font-bold ${data.risk_difference > 0 ? 'text-signal-rose' : 'text-signal-emerald'}`}>
                    {data.risk_difference > 0 ? '+' : ''}{data.risk_difference}
                  </span>
                  <span className="block text-[10px] text-text-muted mt-1 uppercase font-bold">Risk Score Delta</span>
                </div>
              </div>
            </div>

            {/* AI Summary */}
            <div className="flex flex-col gap-4">
              <h4 className="font-label-caps text-text-muted flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px] text-primary">auto_awesome</span>
                AI Architectural Summary
              </h4>
              <div className="bg-surface-container-low border border-border-subtle p-5 rounded h-full">
                <ul className="space-y-4">
                  {data.ai_summary.map((summary, idx) => (
                    <li key={idx} className="flex gap-3">
                      <span className="material-symbols-outlined text-primary text-[20px] shrink-0">check_circle</span>
                      <span className="text-on-surface text-sm leading-relaxed">{summary}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
