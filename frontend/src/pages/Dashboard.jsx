import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../store/analysis';
import PageHeader from '../components/PageHeader';

export default function Dashboard() {
  const { data, repoPath, loading, reset } = useAnalysis();
  const navigate = useNavigate();

  if (loading) {
    return (
      <>
        <PageHeader title="System Dashboard" subtitle="Running analytical pipeline..." />
        <div className="flex-1 flex flex-col items-center justify-center gap-6 p-12">
          <div className="relative">
            <div className="w-16 h-16 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
            <div className="absolute inset-0 w-16 h-16 border border-transparent border-b-signal-cyan rounded-full animate-pulse" />
          </div>
          <div className="flex flex-col items-center gap-1.5 text-center">
            <p className="text-sm font-semibold text-on-surface">Extracting AST & Git history</p>
            <p className="text-xs text-text-muted">Analyzing structural dependency graph...</p>
          </div>
        </div>
      </>
    );
  }

  if (!data) {
    return (
      <>
        <PageHeader title="System Dashboard" />
        <div className="flex-1 flex flex-col items-center justify-center gap-6 px-6 py-12 text-center max-w-2xl mx-auto">
          <div className="relative">
            <div className="absolute inset-0 bg-primary/10 blur-2xl rounded-full scale-150 animate-pulse" />
            <div className="relative w-16 h-16 rounded-2xl bg-surface-container-high border border-border-subtle flex items-center justify-center shadow-lg">
              <span className="material-symbols-outlined text-[32px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>analytics</span>
            </div>
          </div>
          <div className="space-y-2">
            <h2 className="font-extrabold text-xl text-on-surface tracking-tight">No analysis indexed yet</h2>
            <p className="text-on-surface-variant text-xs max-w-md mx-auto leading-relaxed">
              Connect and scan a repository path to generate comprehensive architectural maps, identify structural risks, and extract developer expertise metadata.
            </p>
          </div>
          <button onClick={() => { reset(); navigate('/onboarding'); }} className="btn-primary py-2.5 px-6 rounded-lg font-bold flex items-center gap-2 shadow-[0_0_20px_rgba(157,78,221,0.25)] hover:scale-[1.02] active:scale-[0.98] transition-all">
            <span className="material-symbols-outlined text-[16px]">add</span> New Analysis
          </button>
        </div>
      </>
    );
  }

  const { summary, structural, risk, knowledge } = data;
  const overallRisk = risk?.overall_risk_score ?? 0;
  const healthScore = Math.max(0, 100 - (overallRisk * 10));

  const KPIS = [
    { 
      label: 'Total Files', 
      value: summary?.total_files ?? 0, 
      sub: 'tracked repository files', 
      icon: 'folder_zip',
      spark: 'M0,35 Q20,10 40,25 T80,15 T120,30 T160,5',
      color: 'text-primary',
      bgGlow: 'rgba(157, 78, 221, 0.05)'
    },
    { 
      label: 'Source Files', 
      value: summary?.source_files ?? 0, 
      sub: 'excluding tests & vendor', 
      icon: 'code',
      spark: 'M0,35 Q20,15 40,28 T80,20 T120,10 T160,12',
      color: 'text-signal-cyan',
      bgGlow: 'rgba(0, 187, 249, 0.05)'
    },
    { 
      label: 'Total Commits', 
      value: summary?.total_commits ?? 0, 
      sub: 'mined git operations', 
      icon: 'history',
      spark: 'M0,25 Q20,35 40,15 T80,30 T120,5 T160,18',
      color: 'text-signal-emerald',
      bgGlow: 'rgba(0, 245, 212, 0.05)'
    },
    { 
      label: 'Risk Score', 
      value: `${overallRisk}/10`, 
      sub: 'aggregate health risk', 
      icon: 'gavel',
      spark: 'M0,15 Q20,25 40,8 T80,22 T120,18 T160,32',
      color: overallRisk > 6 ? 'text-signal-rose' : overallRisk > 3 ? 'text-signal-amber' : 'text-signal-emerald',
      bgGlow: overallRisk > 6 ? 'rgba(255, 0, 127, 0.05)' : 'rgba(0, 245, 212, 0.05)'
    },
  ];

  return (
    <>
      <PageHeader
        title="System Dashboard"
        subtitle={repoPath}
        actions={
          <button onClick={() => navigate('/onboarding')} className="btn-primary px-4 py-2 flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
            <span className="material-symbols-outlined text-[16px]">add</span> New Analysis
          </button>
        }
      />

      <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto w-full">
        {/* KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {KPIS.map((k) => (
            <div 
              key={k.label} 
              className="card-base group relative overflow-hidden flex flex-col justify-between hover:border-primary/40 hover:shadow-[0_8px_32px_rgba(157,78,221,0.08)] transition-all duration-300 cursor-pointer"
              style={{
                backgroundImage: `radial-gradient(circle at 100% 0%, ${k.bgGlow} 0%, transparent 60%)`
              }}
            >
              <div className="flex items-center justify-between text-on-surface-variant font-semibold text-[10px] uppercase tracking-widest mb-3">
                {k.label}
                <div className={`p-1.5 rounded-lg bg-surface-container-high/60 border border-border-subtle group-hover:border-primary/30 transition-all ${k.color}`}>
                  <span className="material-symbols-outlined text-[14px]" style={{ fontVariationSettings: "'FILL' 1" }}>{k.icon}</span>
                </div>
              </div>
              <div className="flex items-end justify-between gap-2 mt-1">
                <div className="flex flex-col">
                  <span className="font-extrabold text-2xl text-on-surface tracking-tight leading-none">{k.value}</span>
                  <span className="text-[10px] text-text-muted mt-1.5">{k.sub}</span>
                </div>
                {/* Simulated Sparkline Trend */}
                <svg className="w-20 h-10 overflow-visible text-text-muted/20 group-hover:text-primary/40 transition-colors duration-300" viewBox="0 0 160 40">
                  <defs>
                    <linearGradient id={`grad-${k.label}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="rgba(157, 78, 221, 0.2)" />
                      <stop offset="100%" stopColor="rgba(157, 78, 221, 0)" />
                    </linearGradient>
                  </defs>
                  <path d={`${k.spark} L160,40 L0,40 Z`} fill={`url(#grad-${k.label})`} className="opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <path d={k.spark} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </div>
            </div>
          ))}
        </div>

        {/* Middle row: Health & summary panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Health Score & AI Recommendation card */}
          <div className="card-base lg:col-span-2 flex flex-col justify-between bg-gradient-to-br from-[#0c0c16] via-surface-container/60 to-[#0e0c16]">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-primary text-[18px]">gpp_good</span>
                <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Architectural Health & AI Summary</h3>
              </div>
              <div className="flex flex-col md:flex-row items-center gap-6 py-2">
                {/* Health progress ring */}
                <div className="relative w-24 h-24 flex items-center justify-center flex-shrink-0">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="48" cy="48" r="40" stroke="rgba(255,255,255,0.03)" strokeWidth="6" fill="transparent" />
                    <circle 
                      cx="48" 
                      cy="48" 
                      r="40" 
                      stroke="url(#purpleGlow)" 
                      strokeWidth="6" 
                      fill="transparent" 
                      strokeDasharray="251.2" 
                      strokeDashoffset={251.2 - (251.2 * healthScore) / 100}
                      strokeLinecap="round"
                    />
                    <defs>
                      <linearGradient id="purpleGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#9d4edd" />
                        <stop offset="100%" stopColor="#00bbf9" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-xl font-extrabold text-on-surface tracking-tighter">{healthScore}%</span>
                    <span className="text-[8px] text-text-muted uppercase tracking-widest font-bold">score</span>
                  </div>
                </div>
                {/* AI generated summary text */}
                <div className="flex-1 space-y-2.5">
                  <p className="text-xs text-on-surface font-semibold">
                    The reasoning engines parsed {summary?.total_files} files and generated an architectural health index of {healthScore}%.
                  </p>
                  <p className="text-xs text-on-surface-variant leading-relaxed">
                    {overallRisk > 6 
                      ? "ALERT: High risk indicators detected. Low test coverage combined with dense structural dependency loops are creating complex architectural cycles. Remediate direct cyclic imports immediately."
                      : overallRisk > 3 
                      ? "NOTICE: Moderate structural risks identified. The codebase shows manageable complexity, but contributor concentration (bus factor) suggests high reliance on single authors for core storage operations."
                      : "EXCELLENT: Low overall architectural risk. Modularity boundaries conform to rules, and developer contributions are distributed evenly."
                    }
                  </p>
                  <div className="flex items-center gap-2 pt-1 flex-wrap">
                    <span onClick={() => navigate('/intelligence')} className="text-[10px] text-primary hover:text-primary-fixed font-bold cursor-pointer flex items-center gap-1">
                      Inspect generated insights <span className="material-symbols-outlined text-[12px]">arrow_forward</span>
                    </span>
                    <span className="h-3 w-px bg-border-subtle" />
                    <span onClick={() => navigate('/risk')} className="text-[10px] text-signal-cyan hover:text-signal-cyan/80 font-bold cursor-pointer flex items-center gap-1">
                      Check Risk Center <span className="material-symbols-outlined text-[12px]">security</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bus Factor details */}
          <div className="card-base flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-border-subtle/50 mb-4">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-signal-cyan text-[18px]">group</span>
                  <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Bus Factor Map</h3>
                </div>
                <span className={`badge ${knowledge?.bus_factor_risk === 'high' ? 'badge-high' : 'badge-ok'}`}>
                  {knowledge?.bus_factor ?? '—'} ({knowledge?.bus_factor_risk || 'low'} risk)
                </span>
              </div>
              <div className="space-y-2">
                {(knowledge?.contributions || []).slice(0, 4).map((c, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-surface-container-low/40 border border-border-subtle/40 hover:border-primary/20 hover:bg-surface-container-high/30 transition-all duration-200">
                    <div className="flex flex-col min-w-0">
                      <span className="font-code-sm text-xs font-semibold text-on-surface truncate">{c.name}</span>
                      <span className="text-[10px] text-text-muted">{c.commit_count} contributions</span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <div className="w-16 h-1.5 bg-surface-container rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-primary to-signal-cyan" 
                          style={{ width: `${Math.round((c.share ?? 0) * 100)}%` }} 
                        />
                      </div>
                      <span className="text-[10px] font-semibold text-primary font-code-sm w-8 text-right">
                        {Math.round((c.share ?? 0) * 100)}%
                      </span>
                    </div>
                  </div>
                ))}
                {!knowledge?.contributions?.length && (
                  <div className="py-8 text-center text-text-muted text-xs">No contributor data available.</div>
                )}
              </div>
            </div>
            {knowledge?.contributions?.length > 0 && (
              <button onClick={() => navigate('/knowledge')} className="text-[10px] text-text-muted hover:text-on-surface font-bold text-center mt-3 flex items-center justify-center gap-1">
                View knowledge concentration map <span className="material-symbols-outlined text-[12px]">arrow_right</span>
              </button>
            )}
          </div>
        </div>

        {/* Lower Row: Risk Indicators & Structure Summary */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Risk indicators list */}
          <div className="card-base lg:col-span-2 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-border-subtle/50 mb-4">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-signal-rose text-[18px]">warning</span>
                  <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Top Risk Indicators</h3>
                </div>
                <span className="badge badge-info">{risk?.risk_indicators?.length ?? 0} active</span>
              </div>
              <div className="space-y-2">
                {(risk?.risk_indicators || []).slice(0, 4).map((r, i) => (
                  <div key={i} className="flex items-start md:items-center justify-between gap-4 p-3 rounded-lg bg-surface-container-low/40 border border-border-subtle/40 hover:bg-surface-container-high/20 transition-all duration-200">
                    <div className="flex flex-col min-w-0">
                      <span className="font-semibold text-xs text-on-surface flex items-center gap-1.5">
                        <span className={`w-1.5 h-1.5 rounded-full ${r.severity === 'high' ? 'bg-signal-rose' : r.severity === 'medium' ? 'bg-signal-amber' : 'bg-signal-emerald'}`} />
                        {r.type.replace(/_/g, ' ')}
                      </span>
                      <span className="text-[10px] text-on-surface-variant leading-relaxed mt-0.5">{r.description}</span>
                    </div>
                    <span className={`badge flex-shrink-0 ${r.severity === 'high' ? 'badge-high' : r.severity === 'medium' ? 'badge-warn' : 'badge-low'}`}>
                      {r.severity}
                    </span>
                  </div>
                ))}
                {!risk?.risk_indicators?.length && (
                  <div className="py-12 text-center text-text-muted text-xs">No active risk constraints identified.</div>
                )}
              </div>
            </div>
            {risk?.risk_indicators?.length > 0 && (
              <button onClick={() => navigate('/risk')} className="text-[10px] text-text-muted hover:text-on-surface font-bold text-center mt-4 flex items-center justify-center gap-1">
                Open Risk Assessment Center <span className="material-symbols-outlined text-[12px]">arrow_right</span>
              </button>
            )}
          </div>

          {/* Structure summary counts */}
          <div className="card-base flex flex-col justify-between">
            <div>
              <div className="flex items-center pb-3 border-b border-border-subtle/50 mb-4">
                <span className="material-symbols-outlined text-primary text-[18px] mr-2">database</span>
                <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Codebase Architecture</h3>
              </div>
              <div className="grid grid-cols-2 gap-4 py-2">
                <div className="p-3.5 rounded-lg bg-surface-container-low/40 border border-border-subtle/40">
                  <div className="text-[9px] font-bold text-text-muted uppercase tracking-wider">Total Files</div>
                  <div className="font-extrabold text-xl text-on-surface tracking-tight mt-1">{structural?.total_files ?? 0}</div>
                </div>
                <div className="p-3.5 rounded-lg bg-surface-container-low/40 border border-border-subtle/40">
                  <div className="text-[9px] font-bold text-text-muted uppercase tracking-wider">Total Functions</div>
                  <div className="font-extrabold text-xl text-on-surface tracking-tight mt-1">{structural?.total_functions ?? 0}</div>
                </div>
                <div className="p-3.5 rounded-lg bg-surface-container-low/40 border border-border-subtle/40">
                  <div className="text-[9px] font-bold text-text-muted uppercase tracking-wider">Total Classes</div>
                  <div className="font-extrabold text-xl text-on-surface tracking-tight mt-1">{structural?.total_classes ?? 0}</div>
                </div>
                <div className="p-3.5 rounded-lg bg-surface-container-low/40 border border-border-subtle/40">
                  <div className="text-[9px] font-bold text-text-muted uppercase tracking-wider">Avg Complexity</div>
                  <div className="font-extrabold text-xl text-on-surface tracking-tight mt-1 text-signal-cyan">{structural?.avg_complexity ?? '—'}</div>
                </div>
              </div>
            </div>
            <button onClick={() => navigate('/explorer')} className="text-[10px] text-text-muted hover:text-on-surface font-bold text-center mt-4 flex items-center justify-center gap-1">
              Explore codebase symbol index <span className="material-symbols-outlined text-[12px]">arrow_right</span>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
