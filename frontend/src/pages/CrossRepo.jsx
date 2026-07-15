import { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { getCrossRepoCompare } from '../services/api';

export default function CrossRepo() {
  const [comparison, setComparison] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadComparison() {
      try {
        const res = await getCrossRepoCompare();
        setComparison(res.comparison || []);
        if (res.message) {
          setMessage(res.message);
        }
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    loadComparison();
  }, []);

  return (
    <>
      <PageHeader title="Cross-Repository Comparison" subtitle="Compare complexity, commits, and risk score across analyzed codebases" />
      
      <div className="p-6 flex flex-col gap-6 max-w-[1200px] mx-auto w-full">
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-signal-rose card-base p-5 border border-signal-rose/30 bg-signal-rose/5 text-xs font-semibold">{error}</div>
        ) : (
          <>
            {message && (
              <div className="card-base flex items-center gap-3 bg-[#1d1b18] border border-signal-amber/30 p-4 rounded-xl">
                <span className="material-symbols-outlined text-signal-amber animate-pulse">warning</span>
                <p className="text-xs text-on-surface-variant leading-relaxed">{message}</p>
              </div>
            )}

            {comparison.length > 0 && (
              <div className="space-y-6">
                {/* Benchmarking Matrix Table */}
                <div className="card-base overflow-x-auto bg-surface-container/30 border border-border-subtle p-5 shadow-xl">
                  <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider mb-4 flex items-center gap-1.5 pb-2 border-b border-border-subtle/50">
                    <span className="material-symbols-outlined text-primary text-[18px]">analytics</span> 
                    <span>Benchmarking Matrix</span>
                  </h3>
                  
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-border-subtle/60 text-text-muted font-bold text-[10px] uppercase tracking-wider">
                        <th className="py-2.5 px-3">Repository</th>
                        <th className="py-2.5 px-3">Last Analyzed</th>
                        <th className="py-2.5 px-3 text-right">Total Files</th>
                        <th className="py-2.5 px-3 text-right">Source Files</th>
                        <th className="py-2.5 px-3 text-right">Commits</th>
                        <th className="py-2.5 px-3 text-right">Risk Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border-subtle/30 font-code-sm">
                      {comparison.map((repo, idx) => (
                        <tr key={idx} className="hover:bg-surface-container-high/15 transition-colors">
                          <td className="py-3 px-3 font-sans font-bold text-on-surface">{repo.name}</td>
                          <td className="py-3 px-3 text-on-surface-variant opacity-80">{new Date(repo.analyzed_at).toLocaleString()}</td>
                          <td className="py-3 px-3 text-right font-semibold">{repo.metrics.total_files}</td>
                          <td className="py-3 px-3 text-right font-semibold text-primary">{repo.metrics.source_files}</td>
                          <td className="py-3 px-3 text-right font-semibold text-signal-cyan">{repo.metrics.commits}</td>
                          <td className="py-3 px-3 text-right">
                            <span className={`badge ${repo.metrics.risk_score >= 7 ? 'badge-high' : repo.metrics.risk_score >= 4 ? 'badge-warn' : 'badge-ok'}`}>
                              {repo.metrics.risk_score.toFixed(1)} / 10
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Grid comparing individual metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {comparison.map((repo, idx) => {
                    const ratio = Math.round((repo.metrics.source_files / (repo.metrics.total_files || 1)) * 100);
                    return (
                      <div key={idx} className="card-base flex flex-col justify-between p-5 bg-[#09090e]/60 border border-border-subtle hover:border-primary/30 relative overflow-hidden group">
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary/70" />
                        <div>
                          <div className="flex items-center justify-between border-b border-border-subtle/50 pb-2 mb-3 gap-2">
                            <span className="font-extrabold text-sm text-primary uppercase tracking-wider">{repo.name}</span>
                            <span className={`badge ${repo.metrics.risk_score >= 7 ? 'badge-high' : 'badge-warn'}`}>
                              {repo.metrics.risk_score >= 7 ? 'Critical Risk' : 'Moderate'}
                            </span>
                          </div>
                          
                          <div className="space-y-3 mt-4">
                            <div>
                              <div className="flex justify-between items-center text-[10px] text-text-muted font-bold uppercase tracking-wider mb-1">
                                <span>Code Weight Ratio</span>
                                <span>{ratio}% source files</span>
                              </div>
                              <div className="h-1.5 bg-surface-container rounded-full overflow-hidden">
                                <div className="h-full bg-gradient-to-r from-primary to-signal-cyan" style={{ width: `${ratio}%` }} />
                              </div>
                            </div>
                            
                            <div className="pt-2">
                              <span className="block text-[9px] text-text-muted font-bold uppercase tracking-wider mb-0.5">Physical Directory Location</span>
                              <code className="font-code-sm text-[10px] text-on-surface-variant bg-surface-container-low/55 px-2 py-1 rounded border border-border-subtle block truncate" title={repo.path}>
                                {repo.path}
                              </code>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
}
