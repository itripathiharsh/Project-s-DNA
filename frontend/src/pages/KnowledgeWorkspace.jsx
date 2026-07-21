import { useAnalysis } from '../store/analysis';
import PageHeader from '../components/PageHeader';

export default function KnowledgeWorkspace() {
  const { data, loading, error } = useAnalysis();
  const k = data?.knowledge;

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 py-20">
        <div className="w-10 h-10 border-4 border-surface-container-high border-t-primary rounded-full animate-spin" />
        <p className="text-on-surface-variant font-body-md">Analyzing knowledge maps...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 p-6">
        <div className="text-signal-rose card-base p-5 border border-signal-rose/30 bg-signal-rose/5 text-xs font-semibold">{error}</div>
      </div>
    );
  }

  if (!k) {
    return (
      <>
        <PageHeader title="Knowledge Mapping" subtitle="Contributor knowledge concentration and expertise shares" />
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 py-20 max-w-md mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-surface-container-high flex items-center justify-center border border-border-subtle shadow-md">
            <span className="material-symbols-outlined text-[36px] text-primary">menu_book</span>
          </div>
          <p className="text-on-surface-variant text-xs leading-relaxed">
            Run an analysis to inspect codebase ownership, expert concentration ratios, and bus factor warnings.
          </p>
        </div>
      </>
    );
  }

  const contributions = k.contributions || [];
  const totalCommits = contributions.reduce((s, c) => s + (c.commit_count || 0), 0) || 1;
  const riskBadge = k.bus_factor_risk === 'high' ? 'badge-high' : k.bus_factor_risk === 'medium' ? 'badge-warn' : 'badge-ok';

  // Helper to generate initials and custom avatar color
  const getAvatarColor = (name) => {
    const colors = [
      'bg-primary/20 text-primary border-primary/30',
      'bg-signal-cyan/20 text-signal-cyan border-signal-cyan/30',
      'bg-signal-emerald/20 text-signal-emerald border-signal-emerald/30',
      'bg-signal-amber/20 text-signal-amber border-signal-amber/30',
      'bg-purple-500/20 text-purple-300 border-purple-500/30'
    ];
    let sum = 0;
    for (let i = 0; i < name.length; i++) {
      sum += name.charCodeAt(i);
    }
    return colors[sum % colors.length];
  };

  const getInitials = (name) => {
    return name.split(/[\s_-]/).map(p => p[0]).join('').substring(0, 2).toUpperCase();
  };

  return (
    <>
      <PageHeader title="Knowledge Mapping" subtitle="Contributor knowledge concentration and expertise shares" />
      
      <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto w-full">
        {/* KPI Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card-base flex items-center gap-4 relative overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-[#161625] border border-border-subtle flex items-center justify-center text-signal-rose">
              <span className="material-symbols-outlined text-[24px]">gavel</span>
            </div>
            <div>
              <div className="text-[10px] font-bold text-text-muted uppercase tracking-widest">Bus Factor Level</div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-extrabold text-on-surface tracking-tight">{k.bus_factor ?? '—'}</span>
                <span className={`badge ${riskBadge}`}>{k.bus_factor_risk ?? '—'} risk</span>
              </div>
            </div>
          </div>

          <div className="card-base flex items-center gap-4 relative overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-[#161625] border border-border-subtle flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-[24px]">person</span>
            </div>
            <div>
              <div className="text-[10px] font-bold text-text-muted uppercase tracking-widest">Key Knowledge Owner</div>
              <div className="flex flex-col mt-0.5">
                <span className="text-sm font-extrabold text-on-surface truncate max-w-[180px]">{k.top_contributor || '—'}</span>
                <span className="text-[11px] text-text-muted">{Math.round((k.top_contributor_share ?? 0) * 100)}% commit share</span>
              </div>
            </div>
          </div>

          <div className="card-base flex items-center gap-4 relative overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-[#161625] border border-border-subtle flex items-center justify-center text-signal-emerald">
              <span className="material-symbols-outlined text-[24px]">group</span>
            </div>
            <div>
              <div className="text-[10px] font-bold text-text-muted uppercase tracking-widest">Active Contributors</div>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-2xl font-extrabold text-on-surface tracking-tight">{k.total_authors ?? contributions.length}</span>
                <span className="text-[10px] text-text-muted">committers</span>
              </div>
            </div>
          </div>
        </div>

        {/* Section block: Contributor List & file ownership distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Contributor commit weights */}
          <div className="card-base lg:col-span-1 flex flex-col justify-between">
            <div>
              <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">group</span>
                <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Expertise Allocation</h3>
              </div>
              
              {contributions.length ? (
                <div className="space-y-4">
                  {contributions.map((c, i) => {
                    const pct = Math.round(((c.commit_count || 0) / totalCommits) * 100);
                    return (
                      <div key={i} className="flex flex-col gap-1.5 p-2 rounded-lg bg-surface-container-low/20 border border-transparent hover:border-border-subtle transition-all duration-200">
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-2.5 min-w-0">
                            <div className={`w-7 h-7 rounded-lg border flex items-center justify-center font-extrabold text-[10px] ${getAvatarColor(c.name)} flex-shrink-0`}>
                              {getInitials(c.name)}
                            </div>
                            <span className="text-xs font-semibold text-on-surface truncate">{c.name}</span>
                          </div>
                          <span className="font-code-sm text-[10px] text-text-muted">{c.commit_count} commits</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="flex-1 h-1.5 bg-surface-container rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-primary to-signal-cyan" style={{ width: `${pct}%` }} />
                          </div>
                          <span className="font-code-sm text-[10px] font-bold text-primary w-8 text-right">{pct}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-text-muted font-body-sm py-4 text-center">No contributor data present in Git logs.</p>
              )}
            </div>
          </div>

          {/* Detailed file ownership */}
          {k.ownership_scores && Object.keys(k.ownership_scores).length > 0 && (
            <div className="card-base lg:col-span-2 flex flex-col justify-between">
              <div>
                <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center gap-2">
                  <span className="material-symbols-outlined text-signal-cyan text-[18px]">key</span>
                  <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">File-Level Ownership & Experts</h3>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-border-subtle/60 text-text-muted font-bold text-[10px] uppercase tracking-wider">
                        <th className="py-2.5">File Path</th>
                        <th className="py-2.5">Primary Owner</th>
                        <th className="py-2.5 text-right">Ownership Share</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border-subtle/30 font-code-sm">
                      {Object.entries(k.ownership_scores).slice(0, 10).map(([file, info]) => (
                        <tr key={file} className="hover:bg-surface-container-high/10 transition-colors">
                          <td className="py-3 pr-4 font-mono text-[11px] text-primary truncate max-w-[280px]" title={file}>
                            {file}
                          </td>
                          <td className="py-3 text-on-surface-variant font-sans font-medium">{info.primary_owner}</td>
                          <td className="py-3 text-right">
                            <span className="inline-flex items-center gap-2">
                              <div className="w-12 h-1 bg-surface-container rounded-full overflow-hidden hidden sm:block">
                                <div className="h-full bg-signal-cyan" style={{ width: `${Math.round((info.ownership_score ?? 0) * 100)}%` }} />
                              </div>
                              <span className="text-[11px] font-bold text-on-surface">
                                {Math.round((info.ownership_score ?? 0) * 100)}%
                              </span>
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
