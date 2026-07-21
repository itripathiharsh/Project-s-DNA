import { useState } from 'react';
import { useAnalysis } from '../store/analysis';
import PageHeader from '../components/PageHeader';

const INSIGHT_EXPLANATIONS = {
  hotspot_risk: {
    what: "A file that has been changed frequently AND has high complexity. This is the highest-priority refactoring candidate.",
    why: "Frequent changes + high complexity means every bug fix or feature addition in this file is error-prone and takes longer than it should. These files are the #1 source of production defects.",
    action: "Break this file into smaller, single-responsibility modules. Write tests covering the hot paths before refactoring. Consider extracting the most-frequently changed logic into a dedicated service."
  },
  bus_factor: {
    what: "The minimum number of team members who would need to be hit by a bus (or leave) before the project becomes unmaintainable. A bus factor of 1 means only one person knows the code.",
    why: "If the sole knowledgeable person leaves or is unavailable, the team cannot ship features or fix bugs in that area. This is a critical talent-risk blind spot.",
    action: "Pair-program on the high-risk module. Assign a second reviewer to every change. Document architecture decisions and deployment steps."
  },
  test_debt: {
    what: "The ratio of test files to source files is very low, meaning the codebase has minimal automated test coverage.",
    why: "Without tests, every refactor or dependency upgrade is a gamble. Regression bugs slip through because there's no safety net catching them.",
    action: "Add tests for the most-changed files first (hotspot files). Aim for at least one test file per source package. Use property-based testing for core business logic."
  },
  dependency_risk: {
    what: "Circular dependencies exist in the codebase's import graph (e.g., module A imports B imports C imports A).",
    why: "Circular dependencies break clean architectural layering, make isolated testing impossible, and can cause runtime import errors that are hard to debug.",
    action: "Extract the shared dependency into a new common module. Use dependency inversion: make both modules depend on an interface instead of each other."
  },
  growth_trend: {
    what: "Indicates how the total codebase size has changed over time — growing, stable, or shrinking.",
    why: "Rapid uncontrolled growth often signals duplicated code and lack of architectural oversight. Shrinking without refactoring could mean dead code removal or team attrition.",
    action: "Review growth direction against team velocity. If growing too fast, run duplication detectors. If shrinking, check if features are being deleted without replacement."
  },
  refactoring_needed: {
    what: "Files whose internal complexity (function count, nesting depth) significantly exceeds the codebase average.",
    why: "High-complexity files are hard to read, debug, and modify safely. They accumulate technical debt faster and discourage new contributors.",
    action: "Extract large functions into smaller helpers. Split the file into domain-specific modules. Increase unit test coverage before touching complex code."
  },
  author_contribution_risk: {
    what: "A single author has contributed a disproportionately large share of the commits in the codebase.",
    why: "Knowledge concentration in one person creates a bus-factor risk. If that person leaves, large parts of the codebase become unmaintainable.",
    action: "Encourage code review by other team members. Rotate ownership of key modules. Schedule knowledge-transfer sessions for critical subsystems."
  },
  hotspot_active: {
    what: "A file that appears in the repository's list of most-frequently changed files (hotspot list).",
    why: "Frequently changed files are where most bugs surface. Every change carries risk of regression, so these files need disproportionate testing effort.",
    action: "Review recent commits to this file for patterns. If it keeps being changed for the same reason, consider extracting that concern into its own module."
  },
  large_files: {
    what: "A source file that contains an unusually large number of function or method declarations.",
    why: "Files with many functions tend to violate the Single Responsibility Principle. They become 'god objects' that are hard to navigate, test, and reuse.",
    action: "Split the file by domain concern. Each exported function should have a clear, single purpose. Move related helpers into a dedicated utility module."
  },
  commit_distribution_balance: {
    what: "How evenly commits are distributed across different areas of the codebase.",
    why: "Uneven distribution may indicate that some modules are neglected (high risk of hidden bugs) while others are over-rotated (high maintenance burden).",
    action: "Check if neglected modules have known issues. If over-rotated modules are stable, reduce change frequency by investing in design improvements."
  },
  bus_factor_direct: {
    what: "Direct bus-factor evidence from contributor analysis — the absolute number of people who own critical areas.",
    why: "A bus factor of 1 or 2 means knowledge is dangerously concentrated. The project is one person away from being stuck.",
    action: "Ensure at least two people understand every critical module. Use pair programming and shared code ownership practices."
  },
  dependency_graph_risk: {
    what: "The dependency graph coupling coefficient — a measure of how interconnected and tangled the codebase is.",
    why: "High coupling means changing one module often forces changes in many others. This makes the system rigid and hard to evolve.",
    action: "Identify the most-coupled modules and apply the Interface Segregation Principle. Reduce cross-module dependencies by introducing abstraction layers."
  },
  expert_risk: {
    what: "Files that are modified by authors with low historical expertise in that area of the codebase.",
    why: "Changes made by authors unfamiliar with a module are more likely to introduce bugs or violate established patterns.",
    action: "Assign experienced reviewers for changes to unfamiliar modules. Route complex changes through the domain expert before merge."
  },
  temporal_coupling_coupling: {
    what: "Two or more files that are frequently changed together in the same commit, suggesting a hidden dependency.",
    why: "Temporal coupling means a logical relationship exists between modules that isn't captured in the code (imports, interfaces). This makes independent refactoring dangerous.",
    action: "Examine why these files change together. Either extract a shared dependency or merge the coupled modules into one cohesive unit."
  },
  refactoring_opportunities: {
    what: "Files that show a history of frequent refactoring (rename, restructure, move) in commit history.",
    why: "Frequent refactoring signals instability — the design keeps getting revised because the initial architecture wasn't a good fit.",
    action: "Stabilize the module's interface before making further changes. Consider a broader architectural redesign rather than incremental fixes."
  },
  module_structure_complexity: {
    what: "The directory tree has unusually deep nesting, with many subdirectories beyond typical project conventions.",
    why: "Deep directory structures make it hard to discover files, increase import path complexity, and often indicate over-organization.",
    action: "Flatten the structure. Keep directory depth to a maximum of 3-4 levels. Use meaningful module names instead of nested folders."
  },
  commit_metadata_activity: {
    what: "General activity levels derived from commit metadata — frequency, recency, and distribution of commits.",
    why: "Very low activity may indicate an abandoned project. Very high activity concentrated in short bursts could indicate code churn or crisis-mode development.",
    action: "Assess activity trends. Low activity: plan maintenance sprints. High burst activity: review for quality regression and technical debt."
  }
};

const INDICATOR_EXPLANATIONS = {
  orphaned_modules: {
    what: "Orphaned modules are files that have no registered incoming or outgoing import dependencies within the analyzed codebase.",
    why: "They often represent obsolete scripts, dead code, or isolated entry points (such as manual cron jobs, database seeders, or standalone workers) that aren't integrated into the main application flow.",
    action: "Review these files to verify if they are still in use. If they are obsolete, remove them to reduce code clutter. If they are active workers or entry points, document their use cases."
  },
  low_test_file_ratio: {
    what: "Measures the ratio of test files relative to the count of source code files.",
    why: "A low or zero ratio indicates that the codebase lacks automated test safety nets. Without tests, any structural refactoring carries a high regression risk.",
    action: "Create automated unit tests matching standard naming conventions (e.g. test_*.py or tests/) to validate the core classes and utility functions."
  },
  high_complexity: {
    what: "Identifies files that contain an excessive number of function or method declarations.",
    why: "Files with too many functions often become bloated 'God Objects' that violate the single-responsibility principle and are hard to read and modify.",
    action: "Split the bloated files into smaller, single-responsibility files or domain-specific helper modules."
  },
  dependency_cycles: {
    what: "Tightly coupled loops in the codebase's import graphs (e.g., Module A imports Module B, which imports Module A).",
    why: "Dependency cycles break architectural boundaries, block clean modular testing, and can lead to unexpected runtime import failures.",
    action: "Extract the shared imports into a common leaf module or apply dependency inversion principles."
  }
};

export default function RiskCenter() {
  const { data, loading, error } = useAnalysis();
  const risk = data?.risk;
  const insights = (data?.insights || []).filter((i) => ['high', 'critical', 'medium'].includes(i.severity));

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 py-20">
        <div className="w-10 h-10 border-4 border-surface-container-high border-t-primary rounded-full animate-spin" />
        <p className="text-on-surface-variant font-body-md">Analyzing risk indicators...</p>
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
  const [expandedIndicator, setExpandedIndicator] = useState(null);
  const [expandedInsight, setExpandedInsight] = useState(null);
  const [expandedHotspot, setExpandedHotspot] = useState(null);

  if (!risk) {
    return (
      <>
        <PageHeader title="Risk Assessment" subtitle="Dependency boundaries, cycles and structural anomalies" />
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 py-20 max-w-md mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-surface-container-high flex items-center justify-center border border-border-subtle shadow-md">
            <span className="material-symbols-outlined text-[36px] text-primary">security</span>
          </div>
          <p className="text-on-surface-variant text-xs leading-relaxed">
            Please select and analyze a repository to access architectural constraint audits and security hotspots.
          </p>
        </div>
      </>
    );
  }

  const score = risk.overall_risk_score ?? 0;
  const scoreColor = score >= 7 ? 'text-signal-rose' : score >= 4 ? 'text-signal-amber' : 'text-signal-emerald';
  const glowColor = score >= 7 ? 'rgba(255, 0, 127, 0.15)' : score >= 4 ? 'rgba(234, 179, 8, 0.15)' : 'rgba(0, 245, 212, 0.15)';
  const totalFiles = (risk.source_files ?? 0) + (risk.test_files ?? 0);
  const testPct = totalFiles > 0 ? Math.round(((risk.test_files ?? 0) / totalFiles) * 100) : 0;
  const sourcePct = 100 - testPct;

  return (
    <>
      <PageHeader title="Risk Assessment" subtitle="Dependency boundaries, cycles and structural anomalies" />
      
      <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto w-full">
        {/* Risk Level summary card row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Circular Threat Indicator */}
          <div 
            className="card-base flex flex-col items-center justify-center py-6 text-center"
            style={{ backgroundImage: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)` }}
          >
            <div className="relative w-28 h-28 flex items-center justify-center mb-2">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="56" cy="56" r="46" stroke="rgba(255,255,255,0.03)" strokeWidth="6" fill="transparent" />
                <circle 
                  cx="56" 
                  cy="56" 
                  r="46" 
                  stroke="currentColor" 
                  strokeWidth="6" 
                  fill="transparent" 
                  strokeDasharray="289" 
                  strokeDashoffset={289 - (289 * score) / 10}
                  className={`${scoreColor} transition-all duration-500`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-[34px] font-extrabold tracking-tighter leading-none">{score}</span>
                <span className="text-[8px] text-text-muted uppercase tracking-widest font-bold mt-1">out of 10</span>
              </div>
            </div>
            <h4 className="text-[10px] font-bold text-text-muted uppercase tracking-widest mt-1">aggregate risk score</h4>
          </div>

          {/* Test Coverage Ratio & Details */}
          <div className="card-base md:col-span-2 flex flex-col justify-between">
            <div className="pb-3 border-b border-border-subtle/50">
              <h4 className="text-[10px] font-bold text-text-muted uppercase tracking-widest">Test Coverage Ratio</h4>
            </div>
            <div className="py-4">
              <div className="flex justify-between items-center text-xs mb-2">
                <span className="text-on-surface-variant font-medium">Source files ({risk.source_files ?? 0})</span>
                <span className="text-signal-cyan font-bold">Test files ({risk.test_files ?? 0})</span>
              </div>
              <div className="h-2.5 bg-surface-container rounded-full overflow-hidden flex">
                <div className="h-full bg-primary" style={{ width: `${sourcePct}%` }} title={`Source Code: ${sourcePct}%`} />
                <div className="h-full bg-signal-cyan shadow-[0_0_10px_rgba(0,187,249,0.3)]" style={{ width: `${testPct}%` }} title={`Test Coverage: ${testPct}%`} />
              </div>
              <div className="flex items-center justify-between text-[10px] text-text-muted mt-2">
                <span>{sourcePct}% functional logic</span>
                <span>{testPct}% test validation</span>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 pt-3 border-t border-border-subtle/50 text-xs">
              <div>
                <span className="text-text-muted block text-[10px] uppercase">Test File Ratio</span>
                <span className="font-extrabold text-on-surface text-sm mt-0.5 block">{risk.test_file_ratio ?? 0}</span>
              </div>
              <div>
                <span className="text-text-muted block text-[10px] uppercase">Dependency Cycles</span>
                <span className={`font-extrabold text-sm mt-0.5 block ${risk.dependency_cycles > 0 ? 'text-signal-rose' : 'text-signal-emerald'}`}>
                  {risk.dependency_cycles ?? 0} cycles
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Risk Indicators alerts block */}
        <div className="card-base">
          <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center justify-between">
            <div>
              <h2 className="font-bold text-sm text-on-surface uppercase tracking-wider">Identified Risk Indicators</h2>
              <p className="text-[11px] text-text-muted mt-0.5">Architectural boundaries that fail validation parameters.</p>
            </div>
            <span className="badge badge-info">{risk.risk_indicators?.length ?? 0} warnings</span>
          </div>
          <div className="space-y-3">
            {(risk.risk_indicators || []).map((r, i) => {
              const isExpanded = expandedIndicator === i;
              const expl = INDICATOR_EXPLANATIONS[r.type] || {
                what: "An identified risk indicator in the codebase structures.",
                why: "Heuristics detect that this property deviates from software engineering best practices.",
                action: "Review code segments related to this indicator to enforce quality standards."
              };
              const severityBorder = r.severity === 'high' ? 'border-l-signal-rose' : r.severity === 'medium' ? 'border-l-signal-amber' : 'border-l-signal-emerald';
              return (
                <div
                  key={i}
                  onClick={() => setExpandedIndicator(isExpanded ? null : i)}
                  className={`flex flex-col p-4 rounded-lg bg-surface-container-low/40 border border-border-subtle border-l-4 ${severityBorder} hover:bg-surface-container-high/20 cursor-pointer transition-all duration-200`}
                >
                  <div className="flex items-center justify-between">
                    <div className="min-w-0 pr-4">
                      <div className="font-semibold text-xs capitalize text-on-surface flex items-center gap-2">
                        {r.type.replace(/_/g, ' ')}
                      </div>
                      <div className="text-[11px] text-on-surface-variant mt-0.5 truncate">{r.description}</div>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <span className={`badge ${r.severity === 'high' ? 'badge-high' : r.severity === 'medium' ? 'badge-warn' : 'badge-low'}`}>{r.severity}</span>
                      <span className="material-symbols-outlined text-text-muted select-none text-[16px]">
                        {isExpanded ? 'keyboard_arrow_up' : 'keyboard_arrow_down'}
                      </span>
                    </div>
                  </div>
                  {isExpanded && (
                    <div className="mt-4 pt-3 border-t border-border-subtle/50 grid grid-cols-1 md:grid-cols-3 gap-6 text-xs transition-all duration-200">
                      <div className="space-y-1">
                        <span className="font-bold text-primary block text-[10px] uppercase">Description</span>
                        <p className="text-on-surface-variant leading-relaxed text-[11px]">{expl.what}</p>
                      </div>
                      <div className="space-y-1">
                        <span className="font-bold text-primary block text-[10px] uppercase">Architectural Impact</span>
                        <p className="text-on-surface-variant leading-relaxed text-[11px]">{expl.why}</p>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <span className="font-bold text-primary block text-[10px] uppercase">Remediation Blueprint</span>
                          <p className="text-on-surface-variant leading-relaxed text-[11px]">{expl.action}</p>
                        </div>
                        {r.type === 'orphaned_modules' && risk.orphaned_modules && risk.orphaned_modules.length > 0 && (
                          <div className="p-2 rounded bg-[#161625] border border-border-subtle mt-2">
                            <span className="font-bold text-primary block text-[9px] uppercase mb-1">Files List ({risk.orphaned_modules.length}):</span>
                            <div className="flex flex-col gap-1 max-h-[120px] overflow-y-auto pr-1">
                              {risk.orphaned_modules.map((path, idx) => (
                                <code key={idx} className="font-code-sm text-[9px] text-primary bg-surface-container px-1.5 py-0.5 rounded truncate" title={path}>
                                  {path}
                                </code>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
            {!risk.risk_indicators?.length && <p className="text-text-muted font-body-sm py-4">No validation failures identified.</p>}
          </div>
        </div>

        {/* Complexity hotspots & reasoning alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* High Complexity Files List */}
          <div className="card-base">
            <div className="border-b border-border-subtle/50 pb-3 mb-4">
              <h2 className="font-bold text-sm text-on-surface uppercase tracking-wider">Complexity Hotspots</h2>
              <p className="text-[11px] text-text-muted mt-0.5">Source files containing excessive functional densities.</p>
            </div>
            <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
              {(risk.high_complexity_files || []).map((f, i) => {
                const isExpanded = expandedHotspot === i;
                return (
                  <div
                    key={i}
                    onClick={() => setExpandedHotspot(isExpanded ? null : i)}
                    className="flex flex-col p-3 rounded-lg bg-surface-container-low/40 border border-border-subtle/40 hover:border-primary/30 cursor-pointer transition-all duration-200"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 min-w-0 pr-2">
                        <span className="material-symbols-outlined text-[15px] text-primary flex-shrink-0">description</span>
                        <code className="font-code-sm text-xs text-on-surface truncate" title={f.file}>{f.file}</code>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className="badge badge-warn">{f.function_count} declarations</span>
                        <span className="material-symbols-outlined text-text-muted select-none text-[15px]">
                          {isExpanded ? 'keyboard_arrow_up' : 'keyboard_arrow_down'}
                        </span>
                      </div>
                    </div>
                    {isExpanded && (
                      <div className="mt-3 pt-2.5 border-t border-border-subtle/50 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs transition-all">
                        <div className="space-y-1">
                          <span className="font-bold text-primary block text-[10px] uppercase">Architectural Problem</span>
                          <p className="text-on-surface-variant leading-relaxed text-[11px]">
                            This file contains {f.function_count} declarations. High functional density makes modules difficult to understand, test in isolation, and maintain safely.
                          </p>
                        </div>
                        <div className="space-y-1">
                          <span className="font-bold text-primary block text-[10px] uppercase">Remediation Path</span>
                          <p className="text-on-surface-variant leading-relaxed text-[11px]">
                            Extract independent helper functions into distinct utility modules. Apply single-responsibility principles to break large code constructs down into cohesive, smaller components.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
              {!risk.high_complexity_files?.length && (
                <div className="py-12 text-center text-text-muted text-xs">No complexity anomalies detected.</div>
              )}
            </div>
          </div>

          {/* High Severity Insights list */}
          <div className="card-base">
            <div className="border-b border-border-subtle/50 pb-3 mb-4">
              <h2 className="font-bold text-sm text-on-surface uppercase tracking-wider">Reasoning Insights</h2>
              <p className="text-[11px] text-text-muted mt-0.5">AI assistant findings demanding immediate attention.</p>
            </div>
            <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
              {insights.map((ins, i) => {
                const isExpanded = expandedInsight === i;
                const expl = INSIGHT_EXPLANATIONS[ins.category] || {
                  what: "A detected pattern inferred from the repository's structure, history, and code metrics.",
                  why: "The reasoning engine identified a deviation from software quality baselines that warrants a closer look.",
                  action: "Review the highlighted area with your team and decide if immediate remediation or long-term tracking is appropriate."
                };
                return (
                  <div
                    key={i}
                    onClick={() => setExpandedInsight(isExpanded ? null : i)}
                    className="flex flex-col p-3 rounded-lg bg-surface-container-low/40 border border-border-subtle/40 hover:border-primary/30 cursor-pointer transition-all duration-200"
                  >
                    <div className="flex items-start gap-3">
                      <span className={`badge mt-0.5 ${ins.severity === 'high' || ins.severity === 'critical' ? 'badge-high' : 'badge-warn'}`}>{ins.severity}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <div className="font-bold text-xs truncate text-on-surface">{ins.label ?? ins.category}</div>
                          <span className="material-symbols-outlined text-text-muted select-none text-[15px] shrink-0">
                            {isExpanded ? 'keyboard_arrow_up' : 'keyboard_arrow_down'}
                          </span>
                        </div>
                        <div className="text-[11px] text-on-surface-variant leading-relaxed mt-0.5">{ins.detail}</div>
                        {ins.file_path && <code className="font-code-sm text-[10px] text-primary/80 block mt-1.5 truncate" title={ins.file_path}>{ins.file_path}</code>}
                      </div>
                    </div>
                    {isExpanded && (
                      <div className="mt-4 pt-3 border-t border-border-subtle/50 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs transition-all duration-200">
                        <div className="space-y-1">
                          <span className="font-bold text-primary block text-[10px] uppercase">Reasoning</span>
                          <p className="text-on-surface-variant leading-relaxed text-[10px]">{expl.what}</p>
                        </div>
                        <div className="space-y-1">
                          <span className="font-bold text-primary block text-[10px] uppercase">Risk Vector</span>
                          <p className="text-on-surface-variant leading-relaxed text-[10px]">{expl.why}</p>
                        </div>
                        <div className="space-y-1">
                          <span className="font-bold text-primary block text-[10px] uppercase">Next Step</span>
                          <p className="text-on-surface-variant leading-relaxed text-[10px]">{expl.action}</p>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
              {!insights.length && (
                <div className="py-12 text-center text-text-muted text-xs">No active reasoning insights generated.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
