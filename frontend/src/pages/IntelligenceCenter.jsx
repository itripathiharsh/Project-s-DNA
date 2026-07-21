import { useState } from 'react';
import { useAnalysis } from '../store/analysis';
import PageHeader from '../components/PageHeader';

const INSIGHT_METADATA = {
  hotspot_risk: {
    title: "High-Risk Hotspot Analysis",
    what: "Combines high change frequency (churn) with high complexity. Hotspots are the most fragile files in the codebase, where changes are highly likely to introduce bugs.",
    remedy: "Break down this file into smaller, less coupled modules, and add automated tests to guard future changes."
  },
  bus_factor: {
    title: "Knowledge Concentration (Bus Factor)",
    what: "Measures developer redundancy by calculating how many team members possess critical knowledge of this codebase. A bus factor of 0 or 1 indicates extreme reliance on a single author, presenting a project continuity risk.",
    remedy: "Distribute tasks related to this module, introduce pair programming, and conduct peer code reviews to share ownership."
  },
  test_debt: {
    title: "Test Coverage / Debt",
    what: "Measures the presence of unit/integration tests relative to functional source code files. A low ratio suggests that the codebase lacks validation frameworks, leaving it prone to regressions.",
    remedy: "Create unit and integration tests under the tests directory to cover core routines in this file."
  },
  dependency_risk: {
    title: "Circular Dependency Cycle",
    what: "Detects cyclic import paths (e.g., A -> B -> A). Tight coupling makes testing and modifying code very difficult, causing side-effects.",
    remedy: "Refactor the import chain by introducing a shared base utility, or use dependency injection/interfaces."
  },
  growth_trend: {
    title: "Codebase Growth Dynamics",
    what: "Measures code growth speed (lines of code and class count) over time to flag runaway complexity.",
    remedy: "Track the growth to make sure the structure scales cleanly without accumulating excessive file sizes."
  },
  refactoring_needed: {
    title: "Complexity Refactoring Alert",
    what: "Flags files with high nested logic depth or high code complexity that are difficult to read and maintain.",
    remedy: "Deconstruct nested loops/conditionals into helper functions or early return patterns."
  },
  large_files: {
    title: "Large File Warning",
    what: "Identifies 'God files' that contain too many function or class definitions, violating the single-responsibility principle.",
    remedy: "Extract helper functions and group cohesive functions into separate specialized service classes."
  },
  author_contribution_risk: {
    title: "High Contributor Concentration",
    what: "Shows that a single author has contributed the vast majority of the code changes, creating key-person dependency.",
    remedy: "Encourage other squad members to submit patches and take over issues in this repository domain."
  },
  module_structure_complexity: {
    title: "Complex Module Structure",
    what: "Detects a deep directory hierarchy, making the project hard to navigate and import paths verbose.",
    remedy: "Flatten the folder tree structure by combining small nested subfolders."
  },
  hotspot_active: {
    title: "Highly Active Hotspot",
    what: "Identifies files that receive the highest volume of recent modifications, which are focal points for potential regression bugs.",
    remedy: "Keep commits to these active spots small, and write strict automated integration tests."
  },
  commit_distribution_balance: {
    title: "Commit Distribution Balance",
    what: "Analyzes the diversity of commit types to see if energy is split healthily between new features, bug fixes, and documentation.",
    remedy: "Ensure quality processes balance feature work with refactoring and cleanup."
  },
  refactoring_opportunities: {
    title: "High Refactoring Activity",
    what: "Files that have been historically refactored frequently, indicating either a highly unstable API or active cleanups.",
    remedy: "Lock down the interface once it matures to avoid API churn."
  },
  temporal_coupling_coupling: {
    title: "Temporal Coupling Link",
    what: "Identifies files that are consistently changed together in the same commits, signifying implicit coupling.",
    remedy: "Encourage combining them or extracting the tightly coupled parts into a single module to ensure single-responsibility."
  },
  expertise_risk: {
    title: "Low Team Expertise",
    what: "Identifies files modified by authors who lack deep familiarity with that specific codebase area.",
    remedy: "Require code reviews from subject matter experts before merging changes to these modules."
  },
  dependency_graph_risk: {
    title: "Complex Dependency Graph Structure",
    what: "Shows high density of imports and connections between files, suggesting spaghetti structure.",
    remedy: "Decouple modules by introducing cleaner event-driven communication or facade modules."
  },
  bus_factor_direct: {
    title: "Bus Factor Risk (Direct)",
    what: "Direct contributor statistics point to high key-person dependency in this module.",
    remedy: "Share knowledge and rotate tasks among team members."
  },
  commit_metadata_activity: {
    title: "Repository Commit Activity Status",
    what: "Summarizes the overall pace of work and commit patterns of the repository.",
    remedy: "Maintain healthy release cadences and clean commit message standards."
  }
};

const fallbackMeta = {
  title: "Codebase Analytical Insight",
  what: "An analytical finding generated by applying rules to codebase evidence indicators.",
  remedy: "Review the target files to align them with codebase standards."
};

function severityClass(s) {
  if (s === 'critical' || s === 'high') return 'badge-high';
  if (s === 'medium') return 'badge-warn';
  if (s === 'low') return 'badge-low';
  return 'badge-info';
}

function severityColor(s) {
  if (s === 'critical') return '#F43F5E';
  if (s === 'high') return '#F0883E';
  if (s === 'medium') return '#F59E0B';
  return '#3FB950';
}

function getSeverityExplanation(severity) {
  const sev = (severity || '').toLowerCase();
  if (sev === 'critical') {
    return "Critical severity indicates an immediate operational or architectural bottleneck that risks breaking builds, blocking releases, or causing major regression errors.";
  }
  if (sev === 'high') {
    return "High severity indicates a major architectural risk (like severe dependency cycles or single-maintainer concentration) that will hurt project quality and developer productivity if left unaddressed.";
  }
  if (sev === 'medium') {
    return "Medium severity represents warning flags and moderate technical debt (e.g., lack of tests, large modules) that should be scheduled for refactoring during normal sprint cycles.";
  }
  if (sev === 'low') {
    return "Low severity represents minor code hygiene concerns or stylistic opportunities that present negligible risk to overall system stability.";
  }
  return "Info severity contains diagnostic metadata and baseline metrics describing the repository structure, commit frequency, or general growth trends.";
}

function getConfidenceExplanation(confidence) {
  const confVal = confidence ?? 0.5;
  const percent = Math.round(confVal * 100);
  let rationale = "";
  if (confVal >= 0.85) {
    rationale = "This is backed by direct, high-quality evidence parsed from the AST (Abstract Syntax Tree) database, verifying explicit class/function definitions and import paths.";
  } else if (confVal >= 0.65) {
    rationale = "This is derived from statistical commit history and repository metadata heuristics. Some data might be partially simulated or simplified due to local folder analysis.";
  } else {
    rationale = "This is an informational signal based on general heuristics. Use this as a guide for further investigation rather than an absolute rule.";
  }
  return `Confidence level is ${percent}%. ${rationale}`;
}

export default function IntelligenceCenter() {
  const { data, loading, error } = useAnalysis();
  const insights = data?.insights || [];
  const [filter, setFilter] = useState('all');
  const [expandedIndex, setExpandedIndex] = useState(null);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 py-20">
        <div className="w-10 h-10 border-4 border-surface-container-high border-t-primary rounded-full animate-spin" />
        <p className="text-on-surface-variant font-body-md">Gathering intelligence...</p>
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

  const filtered = filter === 'all' ? insights : insights.filter((i) => i.severity === filter);

  return (
    <>
      <PageHeader
        title="Intelligence Center"
        subtitle={`${insights.length} insights generated`}
        actions={['all', 'high', 'medium', 'low'].map((f) => (
          <button
            key={f}
            onClick={() => {
              setFilter(f);
              setExpandedIndex(null);
            }}
            className={`px-3 py-1.5 rounded font-label-caps text-label-caps transition-colors ${filter === f ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high'}`}
          >
            {f}
          </button>
        ))}
      />
      <div className="p-6 flex flex-col gap-3">
        {filtered.length ? (
          filtered.map((ins, i) => {
            const meta = INSIGHT_METADATA[ins.category] || fallbackMeta;
            const isExpanded = expandedIndex === i;
            return (
              <div
                key={i}
                onClick={() => setExpandedIndex(isExpanded ? null : i)}
                className="flex flex-col p-4 rounded bg-surface-container border border-border-subtle hover:border-primary/30 cursor-pointer transition-all duration-200"
              >
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full mt-2 shrink-0" style={{ background: severityColor(ins.severity) }} />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-body-md font-bold">{ins.label ?? ins.category}</span>
                      <span className={`badge ${severityClass(ins.severity)}`}>{ins.severity}</span>
                      <span className="font-code-sm text-code-sm text-text-muted">conf {Math.round((ins.confidence ?? 0.5) * 100)}%</span>
                    </div>
                    <div className="text-body-sm text-on-surface-variant">{ins.detail}</div>
                    {ins.file_path && (
                      <code className="font-code-sm text-code-sm text-text-muted block mt-2 bg-surface-container-high px-2 py-1 rounded inline-block">{ins.file_path}</code>
                    )}
                  </div>
                  <span className="material-symbols-outlined text-text-muted select-none mt-1">
                    {isExpanded ? 'expand_less' : 'expand_more'}
                  </span>
                </div>
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-border-subtle/50 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs transition-all duration-300">
                    <div className="flex flex-col gap-1.5">
                      <span className="font-bold text-primary flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px]">info</span> What is this?
                      </span>
                      <p className="text-on-surface-variant leading-relaxed">
                        {meta.what}
                      </p>
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <span className="font-bold text-primary flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px]">psychology</span> Severity & Confidence
                      </span>
                      <p className="text-on-surface-variant leading-relaxed">
                        <strong>{ins.severity.toUpperCase()} Severity:</strong> {getSeverityExplanation(ins.severity)}
                        <span className="block mt-2 font-semibold text-primary">{getConfidenceExplanation(ins.confidence)}</span>
                      </p>
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <span className="font-bold text-primary flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px]">construction</span> How to fix?
                      </span>
                      <p className="text-on-surface-variant leading-relaxed">
                        {meta.remedy}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 py-16">
            <span className="material-symbols-outlined text-[48px] text-on-surface-variant">psychology</span>
            <p className="text-on-surface-variant">{data ? 'No insights for this filter.' : 'Run an analysis to generate insights.'}</p>
          </div>
        )}
      </div>
    </>
  );
}
