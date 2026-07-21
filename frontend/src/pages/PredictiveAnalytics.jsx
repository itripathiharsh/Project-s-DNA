import { useState, useEffect } from 'react';
import { getPredictiveForecast } from '../services/api';
import PageHeader from '../components/PageHeader';

export default function PredictiveAnalytics() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [activeTab, setActiveTab] = useState('bugs');
  const [forecastMetric, setForecastMetric] = useState('future_technical_debt');
  const [activeMonthIdx, setActiveMonthIdx] = useState(0);

  useEffect(() => {
    async function loadForecast() {
      try {
        setLoading(true);
        const data = await getPredictiveForecast();
        setForecast(data);
        setError(null);
      } catch (err) {
        console.error('Failed to load predictive analytics', err);
        setError(err.message || 'Failed to retrieve predictive data from the analysis repository.');
      } finally {
        setLoading(false);
      }
    }
    loadForecast();
  }, []);

  if (loading) {
    return (
      <>
        <PageHeader title="Predictive Intelligence" subtitle="Dynamic regression modeling, bug vectors, and future-state trajectories" />
        <div className="flex-1 flex flex-col items-center justify-center py-40">
          <div className="w-12 h-12 rounded-full border-4 border-primary/20 border-t-primary animate-spin mb-4" />
          <p className="text-on-surface-variant text-xs font-semibold animate-pulse">
            Calculating forward-looking vectors & repository telemetry...
          </p>
        </div>
      </>
    );
  }

  if (error || !forecast) {
    return (
      <>
        <PageHeader title="Predictive Intelligence" subtitle="Dynamic regression modeling, bug vectors, and future-state trajectories" />
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 py-20 max-w-md mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-surface-container-high flex items-center justify-center border border-border-subtle shadow-md">
            <span className="material-symbols-outlined text-[36px] text-signal-rose">troubleshoot</span>
          </div>
          <h3 className="font-extrabold text-sm text-on-surface">Data Stream Unavailable</h3>
          <p className="text-on-surface-variant text-xs leading-relaxed">
            {error || "An onboarding analysis must be fully completed to persist repository history in the databases before predictions can be projected."}
          </p>
        </div>
      </>
    );
  }

  const {
    summary,
    bug_prediction,
    regression_prediction,
    crash_probability,
    scalability_prediction,
  } = forecast;

  // Active sub-tab stats
  let activeTabTitle = '';
  let activeTabIcon = '';
  let activeTabScoreLabel = '';
  let activeTabScoreVal = 0;
  let activeTabColor = '';
  let activeTabFilesList = [];

  if (activeTab === 'bugs') {
    activeTabTitle = 'Future Bug Vectors';
    activeTabIcon = 'bug_report';
    activeTabScoreLabel = 'Mean Bug Probability';
    activeTabScoreVal = bug_prediction.score;
    activeTabColor = 'text-signal-rose';
    activeTabFilesList = bug_prediction.top_affected;
  } else if (activeTab === 'regression') {
    activeTabTitle = 'Regression Probability Index';
    activeTabIcon = 'history';
    activeTabScoreLabel = 'Change Regression Risk';
    activeTabScoreVal = regression_prediction.score;
    activeTabColor = 'text-signal-amber';
    activeTabFilesList = regression_prediction.top_affected;
  } else if (activeTab === 'crash') {
    activeTabTitle = 'Crash Probability';
    activeTabIcon = 'error';
    activeTabScoreLabel = 'Runtime Exception Threat';
    activeTabScoreVal = crash_probability.score;
    activeTabColor = 'text-signal-rose';
    activeTabFilesList = crash_probability.top_affected;
  } else if (activeTab === 'scalability') {
    activeTabTitle = 'Scalability Telemetry';
    activeTabIcon = 'speed';
    activeTabScoreLabel = 'Average Scalability Index';
    activeTabScoreVal = scalability_prediction.score;
    activeTabColor = 'text-signal-cyan';
    activeTabFilesList = scalability_prediction.top_affected;
  }

  // Calculate SVG line/area projection points
  const timeline = forecast[forecastMetric]?.timeline || [];
  const activeMonthData = timeline[activeMonthIdx] || {};

  const values = timeline.map(t => t.value);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const valRange = maxVal - minVal || 1;

  const width = 640;
  const height = 240;
  const padding = { top: 20, right: 30, bottom: 40, left: 50 };

  const svgPoints = timeline.map((t, i) => {
    const x = padding.left + (i / 12) * (width - padding.left - padding.right);
    const y = height - padding.bottom - ((t.value - minVal) / valRange) * (height - padding.top - padding.bottom);
    return { x, y, ...t };
  });

  const pathD = svgPoints.reduce((acc, p, i) => {
    return i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`;
  }, '');

  const areaD = svgPoints.length
    ? `${pathD} L ${svgPoints[svgPoints.length - 1].x} ${height - padding.bottom} L ${svgPoints[0].x} ${height - padding.bottom} Z`
    : '';

  // Projections selector definition
  const FORECASTS = [
    { key: 'future_technical_debt', label: 'Technical Debt', unit: 'effort units', icon: 'engineering' },
    { key: 'future_complexity', label: 'AST Complexity', unit: 'index', icon: 'account_tree' },
    { key: 'future_coupling', label: 'Coupling Density', unit: '%', icon: 'hub' },
    { key: 'future_risk', label: 'Aggregate Risk', unit: 'score', icon: 'warning' },
    { key: 'future_architecture_drift', label: 'Architecture Drift', unit: '% probability', icon: 'change_history' },
    { key: 'future_maintenance_cost', label: 'Maintenance Cost', unit: 'dev hours', icon: 'payments' },
  ];

  return (
    <>
      <PageHeader title="Predictive Intelligence" subtitle="Dynamic regression modeling, bug vectors, and future-state trajectories" />

      <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto w-full">
        
        {/* Summary Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card-base flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest block">Current Health</span>
              <div className="text-xl font-extrabold text-signal-emerald mt-1">{summary.overall_health}%</div>
            </div>
            <span className="material-symbols-outlined text-[24px] text-signal-emerald">verified_user</span>
          </div>

          <div className="card-base flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest block">Git Commit Count</span>
              <div className="text-xl font-extrabold text-primary mt-1">{summary.total_commits}</div>
            </div>
            <span className="material-symbols-outlined text-[24px] text-primary">history</span>
          </div>

          <div className="card-base flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest block">Commit Velocity</span>
              <div className="text-xl font-extrabold text-signal-amber mt-1">{summary.monthly_commit_velocity} / mo</div>
            </div>
            <span className="material-symbols-outlined text-[24px] text-signal-amber">show_chart</span>
          </div>

          <div className="card-base flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest block">Analyzed Structures</span>
              <div className="text-xl font-extrabold text-signal-cyan mt-1">
                {summary.total_files} <span className="text-xs text-text-muted font-normal">files</span> / {summary.total_functions} <span className="text-xs text-text-muted font-normal font-sans">funcs</span>
              </div>
            </div>
            <span className="material-symbols-outlined text-[24px] text-signal-cyan">analytics</span>
          </div>
        </div>

        {/* 12-Month Timeline Forecast Charts (SVG based) */}
        <div className="card-base p-6">
          <div className="border-b border-border-subtle/50 pb-3 mb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="font-bold text-sm text-on-surface uppercase tracking-wider">12-Month Projections Timeline</h2>
              <p className="text-[11px] text-text-muted mt-0.5">
                Simulated progression using commit frequency and regression coefficients.
              </p>
            </div>
            <div className="flex flex-wrap gap-1">
              {FORECASTS.map((f) => (
                <button
                  key={f.key}
                  onClick={() => {
                    setForecastMetric(f.key);
                    setActiveMonthIdx(0);
                  }}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase transition-all duration-200 ${
                    forecastMetric === f.key
                      ? 'bg-primary/20 text-primary border border-primary/40'
                      : 'text-on-surface-variant bg-surface-container-high/40 hover:bg-surface-container-high border border-border-subtle/30'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Interactive SVG Chart */}
            <div className="lg:col-span-2 flex flex-col items-center justify-center p-4 bg-surface-container-low/20 rounded-xl border border-border-subtle/40">
              <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible select-none">
                <defs>
                  <linearGradient id="chartGlow" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-primary, #9d4edd)" stopOpacity="0.25" />
                    <stop offset="100%" stopColor="var(--color-primary, #9d4edd)" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Grid Lines */}
                {Array.from({ length: 5 }).map((_, i) => {
                  const y = padding.top + (i / 4) * (height - padding.top - padding.bottom);
                  const gridVal = maxVal - (i / 4) * valRange;
                  return (
                    <g key={i} className="opacity-30">
                      <line
                        x1={padding.left}
                        y1={y}
                        x2={width - padding.right}
                        y2={y}
                        stroke="rgba(255,255,255,0.08)"
                        strokeDasharray="4,4"
                      />
                      <text
                        x={padding.left - 8}
                        y={y + 4}
                        textAnchor="end"
                        className="fill-text-muted text-[10px] font-mono"
                      >
                        {forecastMetric === 'future_coupling' ? `${gridVal.toFixed(1)}%` : Math.round(gridVal)}
                      </text>
                    </g>
                  );
                })}

                {/* X Axis Labels */}
                {timeline.map((t, i) => {
                  const x = padding.left + (i / 12) * (width - padding.left - padding.right);
                  return (
                    <text
                      key={i}
                      x={x}
                      y={height - padding.bottom + 16}
                      textAnchor="middle"
                      className="fill-text-muted text-[9px] font-mono opacity-80"
                    >
                      M{i}
                    </text>
                  );
                })}

                {/* Area under curve */}
                {areaD && (
                  <path
                    d={areaD}
                    fill="url(#chartGlow)"
                    className="transition-all duration-300"
                  />
                )}

                {/* Main line */}
                {pathD && (
                  <path
                    d={pathD}
                    fill="transparent"
                    stroke="var(--color-primary, #9d4edd)"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    className="transition-all duration-300"
                  />
                )}

                {/* Interaction Dots */}
                {timeline.map((t, i) => {
                  const p = svgPoints[i];
                  if (!p) return null;
                  const isActive = activeMonthIdx === i;
                  return (
                    <g key={i}>
                      {isActive && (
                        <circle
                          cx={p.x}
                          cy={p.y}
                          r="8"
                          fill="var(--color-primary, #9d4edd)"
                          className="opacity-35 animate-ping"
                          style={{ transformOrigin: `${p.x}px ${p.y}px` }}
                        />
                      )}
                      <circle
                        cx={p.x}
                        cy={p.y}
                        r={isActive ? 5.5 : 3.5}
                        fill={isActive ? 'var(--color-primary, #9d4edd)' : '#161622'}
                        stroke="var(--color-primary, #9d4edd)"
                        strokeWidth="2"
                        className="cursor-pointer transition-all duration-150 hover:scale-125 origin-center"
                        style={{ transformOrigin: `${p.x}px ${p.y}px` }}
                        onClick={() => setActiveMonthIdx(i)}
                      />
                      {/* Transparent overlay hitbox for much easier hover/click target */}
                      <circle
                        cx={p.x}
                        cy={p.y}
                        r="14"
                        fill="transparent"
                        className="cursor-pointer"
                        style={{ transformOrigin: `${p.x}px ${p.y}px` }}
                        onClick={() => setActiveMonthIdx(i)}
                      />
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Selected Month Forecast Card */}
            <div className="card-base bg-surface-container-high/40 flex flex-col justify-between border-border-subtle/50">
              <div className="pb-3 border-b border-border-subtle/50">
                <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest">
                  Forecast Breakdown
                </span>
                <h3 className="font-extrabold text-sm text-on-surface mt-1">
                  {FORECASTS.find(f => f.key === forecastMetric)?.label} ({activeMonthData.label || 'M0'})
                </h3>
              </div>

              <div className="py-6 flex flex-col items-center justify-center text-center">
                <div className="text-3xl font-extrabold text-primary">
                  {activeMonthData.value}{' '}
                  <span className="text-xs text-text-muted font-normal font-sans">
                    {FORECASTS.find(f => f.key === forecastMetric)?.unit}
                  </span>
                </div>
                
                {activeMonthIdx > 0 && (
                  <div className="text-[10px] text-signal-amber font-semibold mt-2 flex items-center gap-1">
                    <span className="material-symbols-outlined text-[12px]">trending_up</span>
                    +{Math.round(((activeMonthData.value - timeline[0].value) / (timeline[0].value || 1)) * 100)}% accumulated growth
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-border-subtle/50 text-[11px] text-text-muted leading-relaxed">
                {forecastMetric === 'future_technical_debt' && (
                  <span>
                    Forecasts the expected effort required to fix structural issues. Highly related to code change churn rates.
                  </span>
                )}
                {forecastMetric === 'future_complexity' && (
                  <span>
                    Accumulated Cyclomatic complexity across all nodes. Unresolved cognitive spikes compound logic complexity.
                  </span>
                )}
                {forecastMetric === 'future_coupling' && (
                  <span>
                    Measures the percentage density of inter-file imports. Lack of modular boundaries causes coupling creep.
                  </span>
                )}
                {forecastMetric === 'future_risk' && (
                  <span>
                    Projected score of overall code risk indices. Rising values suggest knowledge dilution and critical security debts.
                  </span>
                )}
                {forecastMetric === 'future_architecture_drift' && (
                  <span>
                    Probability of layer constraint violations based on existing cycle growth velocities.
                  </span>
                )}
                {forecastMetric === 'future_maintenance_cost' && (
                  <span>
                    Projected developer hours needed per month for bug fixes and chore items.
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Actionable Risk Tab Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Navigation Panel for predictions tabs */}
          <div className="flex flex-col gap-2.5">
            <button
              onClick={() => setActiveTab('bugs')}
              className={`card-base text-left flex items-center gap-3 transition-all duration-200 ${
                activeTab === 'bugs' ? 'border-primary bg-primary/5 shadow-md' : 'hover:border-border-subtle'
              }`}
            >
              <div className="w-9 h-9 rounded-lg bg-signal-rose/10 border border-signal-rose/20 flex items-center justify-center text-signal-rose flex-shrink-0">
                <span className="material-symbols-outlined text-[18px]">bug_report</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-xs text-on-surface">Bug Probability Predictor</div>
                <div className="text-[10px] text-text-muted truncate mt-0.5">Files susceptible to future defect insertion</div>
              </div>
            </button>

            <button
              onClick={() => setActiveTab('regression')}
              className={`card-base text-left flex items-center gap-3 transition-all duration-200 ${
                activeTab === 'regression' ? 'border-primary bg-primary/5 shadow-md' : 'hover:border-border-subtle'
              }`}
            >
              <div className="w-9 h-9 rounded-lg bg-signal-amber/10 border border-signal-amber/20 flex items-center justify-center text-signal-amber flex-shrink-0">
                <span className="material-symbols-outlined text-[18px]">history</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-xs text-on-surface">Regression Modeler</div>
                <div className="text-[10px] text-text-muted truncate mt-0.5">Highly coupled modules susceptible to change impact</div>
              </div>
            </button>

            <button
              onClick={() => setActiveTab('crash')}
              className={`card-base text-left flex items-center gap-3 transition-all duration-200 ${
                activeTab === 'crash' ? 'border-primary bg-primary/5 shadow-md' : 'hover:border-border-subtle'
              }`}
            >
              <div className="w-9 h-9 rounded-lg bg-signal-rose/10 border border-signal-rose/20 flex items-center justify-center text-signal-rose flex-shrink-0">
                <span className="material-symbols-outlined text-[18px]">error</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-xs text-on-surface">Crash Probability Scan</div>
                <div className="text-[10px] text-text-muted truncate mt-0.5">Lack of exception guards and risky API triggers</div>
              </div>
            </button>

            <button
              onClick={() => setActiveTab('scalability')}
              className={`card-base text-left flex items-center gap-3 transition-all duration-200 ${
                activeTab === 'scalability' ? 'border-primary bg-primary/5 shadow-md' : 'hover:border-border-subtle'
              }`}
            >
              <div className="w-9 h-9 rounded-lg bg-signal-cyan/10 border border-signal-cyan/20 flex items-center justify-center text-signal-cyan flex-shrink-0">
                <span className="material-symbols-outlined text-[18px]">speed</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-xs text-on-surface">Scalability Constraints</div>
                <div className="text-[10px] text-text-muted truncate mt-0.5">Ast deep structures & God module bottleneck alerts</div>
              </div>
            </button>
          </div>

          {/* Detailed predictions sub-panel */}
          <div className="lg:col-span-2 card-base flex flex-col gap-4">
            <div className="border-b border-border-subtle/50 pb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">{activeTabIcon}</span>
                <h2 className="font-bold text-sm text-on-surface uppercase tracking-wider">{activeTabTitle}</h2>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-text-muted block uppercase font-bold">{activeTabScoreLabel}</span>
                <span className={`text-base font-extrabold ${activeTabColor}`}>{activeTabScoreVal}%</span>
              </div>
            </div>

            {/* List of files */}
            <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
              {activeTabFilesList.map((f, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-surface-container-low/40 border border-border-subtle/30 rounded-xl hover:border-primary/20 transition-all duration-200"
                >
                  <div className="flex items-center justify-between gap-4 mb-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="material-symbols-outlined text-text-muted text-[15px] flex-shrink-0">description</span>
                      <code className="font-code-sm text-xs text-primary truncate" title={f.file_path}>
                        {f.file_path}
                      </code>
                    </div>
                    <div className="flex items-center gap-1 flex-shrink-0 text-xs font-extrabold">
                      <span className={activeTabColor}>
                        {f.probability ?? f.score}%
                      </span>
                      <span className="text-[10px] text-text-muted font-normal">
                        {activeTab === 'scalability' ? 'scaling capability' : 'probability'}
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-col gap-1 pl-6">
                    {f.reasons?.map((r, rIdx) => (
                      <div key={rIdx} className="text-[10px] text-on-surface-variant flex items-center gap-1.5">
                        <span className="w-1 h-1 rounded-full bg-primary/60" />
                        {r}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </>
  );
}
