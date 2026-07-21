import { useAnalysis } from '../store/analysis';
import PageHeader from '../components/PageHeader';

const CAT_ICON = { 
  feat: 'add_circle', 
  fix: 'healing', 
  refactor: 'transform', 
  test: 'check_circle', 
  docs: 'article', 
  chore: 'settings_suggest', 
  other: 'commit' 
};

const CAT_COLOR = {
  feat: 'text-signal-emerald bg-signal-emerald/10 border-signal-emerald/20',
  fix: 'text-signal-rose bg-signal-rose/10 border-signal-rose/20',
  refactor: 'text-primary bg-primary/10 border-primary/20',
  test: 'text-signal-cyan bg-signal-cyan/10 border-signal-cyan/20',
  docs: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  chore: 'text-text-muted bg-surface-container border-border-subtle',
  other: 'text-text-muted bg-surface-container border-border-subtle'
};

export default function EvolutionTimeline() {
  const { data, loading, error } = useAnalysis();
  const ev = data?.evolution;

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 py-20">
        <div className="w-10 h-10 border-4 border-surface-container-high border-t-primary rounded-full animate-spin" />
        <p className="text-on-surface-variant font-body-md">Analyzing evolution data...</p>
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

  if (!ev) {
    return (
      <>
        <PageHeader title="Evolution & Hotspots" subtitle="Git commit activity distributions and hotspot analysis" />
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 py-20 max-w-md mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-surface-container-high flex items-center justify-center border border-border-subtle shadow-md">
            <span className="material-symbols-outlined text-[36px] text-primary">query_stats</span>
          </div>
          <p className="text-on-surface-variant text-xs leading-relaxed">
            Run an analysis on a git-supported directory to visualize commit history, code churn, and hotspot alerts.
          </p>
        </div>
      </>
    );
  }

  const cats = ev.commit_categories || {};
  const total = ev.total_commits || 0;
  const hotspots = ev.hotspots || ev.hotspot_list || [];

  const totalLines = (ev.total_insertions ?? 0) + (ev.total_deletions ?? 0);
  const insPct = totalLines > 0 ? Math.round(((ev.total_insertions ?? 0) / totalLines) * 100) : 0;
  const delPct = 100 - insPct;

  return (
    <>
      <PageHeader title="Evolution & Hotspots" subtitle={`${total} commits by ${ev.total_authors ?? 0} authors`} />
      
      <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto w-full">
        {/* KPI Stats cards row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card-base">
            <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest block">First Commit</span>
            <div className="text-sm font-extrabold text-on-surface mt-1.5 font-code-sm truncate" title={ev.first_commit}>
              {ev.first_commit || '—'}
            </div>
          </div>
          <div className="card-base">
            <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest block">Last Commit</span>
            <div className="text-sm font-extrabold text-on-surface mt-1.5 font-code-sm truncate" title={ev.last_commit}>
              {ev.last_commit || '—'}
            </div>
          </div>
          <div className="card-base">
            <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest block">Total Insertions</span>
            <div className="text-xl font-extrabold text-signal-emerald mt-1">{ev.total_insertions ?? 0}</div>
          </div>
          <div className="card-base">
            <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest block">Total Deletions</span>
            <div className="text-xl font-extrabold text-signal-rose mt-1">{ev.total_deletions ?? 0}</div>
          </div>
        </div>

        {/* Lines Changed Balance Card */}
        {totalLines > 0 && (
          <div className="card-base">
            <div className="flex justify-between items-center text-xs mb-2">
              <span className="text-signal-emerald font-semibold flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">add</span> {ev.total_insertions} insertions
              </span>
              <span className="text-signal-rose font-semibold flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">remove</span> {ev.total_deletions} deletions
              </span>
            </div>
            <div className="h-2 bg-surface-container rounded-full overflow-hidden flex">
              <div className="h-full bg-signal-emerald" style={{ width: `${insPct}%` }} />
              <div className="h-full bg-signal-rose" style={{ width: `${delPct}%` }} />
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Commit categorization list */}
          <div className="card-base">
            <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[18px]">category</span>
              <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Commit Classification</h3>
            </div>
            
            <div className="space-y-3.5">
              {Object.entries(cats).map(([cat, count]) => {
                const pct = total ? Math.round((count / total) * 100) : 0;
                return (
                  <div key={cat} className="flex items-center gap-4 p-2 rounded-lg bg-surface-container-low/40 border border-border-subtle/30 hover:bg-surface-container-high/20 transition-all duration-200">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${CAT_COLOR[cat] || CAT_COLOR.other} flex-shrink-0`}>
                      <span className="material-symbols-outlined text-[16px]">{CAT_ICON[cat] || 'commit'}</span>
                    </div>
                    <span className="font-bold text-xs capitalize w-20 text-on-surface truncate">{cat}</span>
                    <div className="flex-1 h-2 bg-surface-container rounded-full overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${pct}%` }} />
                    </div>
                    <span className="font-code-sm text-[10px] text-text-muted w-16 text-right">
                      {count} · {pct}%
                    </span>
                  </div>
                );
              })}
              {!Object.keys(cats).length && (
                <p className="text-text-muted font-body-sm text-center py-6">No categorized commit history available.</p>
              )}
            </div>
          </div>

          {/* Change hotspots list */}
          <div className="card-base">
            <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-signal-amber text-[18px]">local_fire_department</span>
              <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Most Active Change Hotspots</h3>
            </div>

            <div className="space-y-3.5 max-h-[390px] overflow-y-auto pr-1">
              {hotspots.length ? (
                hotspots.slice(0, 10).map((h, i) => {
                  const max = hotspots[0]?.changes || hotspots[0]?.change_count || 1;
                  const changes = h.changes ?? h.change_count ?? 0;
                  return (
                    <div key={i} className="flex flex-col gap-1.5 p-2 rounded-lg bg-surface-container-low/40 border border-border-subtle/30 hover:border-primary/20 transition-all duration-200">
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="material-symbols-outlined text-text-muted text-[15px] flex-shrink-0">description</span>
                          <code className="font-code-sm text-xs text-primary truncate" title={h.file}>{h.file}</code>
                        </div>
                        <span className="font-code-sm text-[11px] font-bold text-signal-amber w-16 text-right flex-shrink-0">
                          {changes} modifications
                        </span>
                      </div>
                      <div className="h-1.5 bg-surface-container rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-signal-amber to-signal-rose" 
                          style={{ width: `${Math.min(100, (changes / max) * 100)}%` }} 
                        />
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="text-text-muted font-body-sm py-12 text-center">No git-history hotspot indexes resolved.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
