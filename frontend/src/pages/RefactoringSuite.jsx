import { useState, useEffect } from 'react';
import { getRefactoringAnalysis, simulateRefactoring } from '../services/api';
import PageHeader from '../components/PageHeader';

const TABS = [
  { key: 'one_click_plan',        label: 'One-Click Plan',       icon: 'bolt' },
  { key: 'dead_code',             label: 'Dead Code',            icon: 'delete_sweep' },
  { key: 'duplicate_removal',     label: 'Duplicates',           icon: 'content_copy' },
  { key: 'class_splits',          label: 'Class Splits',         icon: 'call_split' },
  { key: 'package_splits',        label: 'Package Splits',       icon: 'folder_open' },
  { key: 'dependency_breaks',     label: 'Dep Breaks',           icon: 'link_off' },
  { key: 'modularization',        label: 'Modularization',       icon: 'view_module' },
  { key: 'microservices',         label: 'Microservices',        icon: 'cloud' },
  { key: 'architecture_migration',label: 'Architecture',         icon: 'account_tree' },
  { key: 'simulator',             label: 'Simulator',            icon: 'science' },
];

const PRIORITY_COLOR = { critical:'text-red-400', high:'text-orange-400', medium:'text-yellow-400', low:'text-slate-400' };
const Badge = ({ p }) => <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${PRIORITY_COLOR[p] || 'text-slate-400'} bg-white/5`}>{p}</span>;
const Card = ({ children, className = '' }) => <div className={`rounded-xl border border-white/8 bg-white/3 p-4 ${className}`}>{children}</div>;
const FileTag = ({ path }) => <code className="text-[10px] text-violet-300 bg-violet-900/20 px-1.5 py-0.5 rounded break-all">{path}</code>;
const SummaryBadge = ({ text }) => <p className="text-[11px] text-slate-400 mt-1">{text}</p>;

function OneClickPlan({ data }) {
  if (!data) return null;
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Actions', val: data.total_actions, color: 'text-violet-400' },
          { label: 'Est. Hours', val: data.estimated_effort_hours, color: 'text-amber-400' },
          { label: 'Est. Days', val: data.estimated_effort_days, color: 'text-emerald-400' },
        ].map(c => (
          <Card key={c.label} className="text-center">
            <div className={`text-2xl font-black ${c.color}`}>{c.val}</div>
            <div className="text-[10px] text-slate-400 uppercase tracking-widest mt-1">{c.label}</div>
          </Card>
        ))}
      </div>
      <SummaryBadge text={data.summary} />
      <div className="space-y-2">
        {data.actions?.map((a, i) => (
          <Card key={i} className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <span className="text-[10px] font-black text-slate-500 w-5 mt-0.5">{i+1}</span>
              <div>
                <FileTag path={a.file} />
                <p className="text-xs text-slate-200 mt-1">{a.action}</p>
                <span className="text-[10px] text-slate-500">{a.effort_hours}h · {a.type}</span>
              </div>
            </div>
            <Badge p={a.priority === 1 ? 'critical' : a.priority === 2 ? 'high' : 'medium'} />
          </Card>
        ))}
      </div>
    </div>
  );
}

function DeadCode({ data }) {
  return (
    <div className="space-y-4">
      <SummaryBadge text={data.summary} />
      <div className="grid grid-cols-2 gap-3">
        <Card>
          <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Unreferenced Files ({data.dead_files?.length})</p>
          <div className="space-y-2">{data.dead_files?.map((f, i) => (
            <div key={i}><FileTag path={f.file_path} /><p className="text-[10px] text-slate-500 mt-1">{f.reason}</p></div>
          ))}</div>
        </Card>
        <Card>
          <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Dead Functions ({data.dead_functions?.length})</p>
          <div className="space-y-2 max-h-80 overflow-y-auto">{data.dead_functions?.map((f, i) => (
            <div key={i} className="flex items-center justify-between">
              <div><FileTag path={`${f.file_path}:${f.line}`} /><p className="text-[10px] text-slate-500 mt-0.5">{f.function} · {f.loc} LOC</p></div>
              <Badge p={f.priority} />
            </div>
          ))}</div>
        </Card>
      </div>
      <Card className="flex items-center gap-3">
        <span className="material-symbols-outlined text-emerald-400 text-[20px]">savings</span>
        <span className="text-sm text-emerald-300 font-semibold">{data.total_savings_loc} LOC removable</span>
      </Card>
    </div>
  );
}

function DuplicateRemoval({ data }) {
  return (
    <div className="space-y-4">
      <SummaryBadge text={data.summary} />
      <Card>
        <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Duplicate Function Bodies ({data.total_duplicate_functions})</p>
        <div className="space-y-2 max-h-64 overflow-y-auto">{data.duplicate_functions?.map((f, i) => (
          <div key={i} className="flex items-center gap-3 p-2 bg-white/3 rounded-lg">
            <span className="material-symbols-outlined text-amber-400 text-[14px]">content_copy</span>
            <div className="min-w-0"><FileTag path={f.file_path} /><p className="text-[10px] text-slate-500 mt-0.5">{f.name} · {f.lines_of_code} LOC</p></div>
          </div>
        ))}</div>
      </Card>
      <Card>
        <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Duplicate Filenames ({data.duplicate_filenames?.length})</p>
        <div className="space-y-3">{data.duplicate_filenames?.map((g, i) => (
          <div key={i}>
            <p className="text-xs font-bold text-slate-300 mb-1">{g.filename}</p>
            <div className="space-y-1 pl-3">{g.occurrences.map((p, j) => <FileTag key={j} path={p} />)}</div>
            <p className="text-[10px] text-slate-500 mt-1">{g.action} · {g.effort_hours}h</p>
          </div>
        ))}</div>
      </Card>
    </div>
  );
}

function ClassSplits({ data }) {
  return (
    <div className="space-y-3">
      <SummaryBadge text={data.summary} />
      {data.suggestions?.map((s, i) => (
        <Card key={i}>
          <div className="flex items-start justify-between mb-2">
            <FileTag path={s.file_path} />
            <Badge p={s.priority} />
          </div>
          <p className="text-[10px] text-slate-400 mb-2">{s.reason} · {s.function_count} funcs · complexity {s.total_complexity} · {s.effort_hours}h</p>
          <div className="grid grid-cols-2 gap-2">
            {s.proposed_splits?.map((sp, j) => (
              <div key={j} className="bg-violet-900/20 border border-violet-800/30 rounded-lg p-2">
                <p className="text-[10px] font-bold text-violet-300">{sp.name}</p>
                <p className="text-[9px] text-slate-500 mt-0.5">{sp.functions?.join(', ')}</p>
                <p className="text-[9px] text-slate-600 mt-0.5">{sp.estimated_loc} LOC</p>
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}

function PackageSplits({ data }) {
  return (
    <div className="space-y-3">
      <SummaryBadge text={data.summary} />
      {data.suggestions?.map((s, i) => (
        <Card key={i}>
          <div className="flex items-start justify-between mb-2">
            <code className="text-[10px] text-amber-300 bg-amber-900/20 px-1.5 py-0.5 rounded">{s.directory}/</code>
            <Badge p={s.priority} />
          </div>
          <p className="text-[10px] text-slate-400 mb-2">{s.file_count} files · {s.total_functions} funcs · {s.effort_hours}h</p>
          <div className="flex flex-wrap gap-1">
            {s.proposed_sub_packages?.map((sp, j) => (
              <span key={j} className="text-[9px] bg-white/5 border border-white/10 px-2 py-0.5 rounded text-slate-300">
                {sp.sub_package}/ ({sp.files?.length} files)
              </span>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}

function DependencyBreaks({ data }) {
  return (
    <div className="space-y-4">
      <SummaryBadge text={data.summary} />
      {data.cycles?.length > 0 && (
        <div>
          <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Dependency Cycles ({data.total_cycles})</p>
          {data.cycles?.map((c, i) => (
            <Card key={i} className="mb-2">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-red-400 font-bold">{c.length}-node cycle</span>
                <Badge p="critical" />
              </div>
              <div className="flex flex-wrap gap-1 mb-2">{c.cycle?.map((p, j) => <FileTag key={j} path={p} />)}</div>
              <p className="text-[10px] text-slate-400">{c.action} · {c.effort_hours}h</p>
            </Card>
          ))}
        </div>
      )}
      <div>
        <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Bottleneck Files</p>
        {data.bottlenecks?.map((b, i) => (
          <Card key={i} className="mb-2 flex items-start justify-between">
            <div><FileTag path={b.file_path} /><p className="text-[10px] text-slate-400 mt-1">{b.action}</p></div>
            <Badge p={b.priority} />
          </Card>
        ))}
      </div>
    </div>
  );
}

function Modularization({ data }) {
  return (
    <div className="space-y-3">
      <SummaryBadge text={data.summary} />
      {data.suggestions?.map((s, i) => (
        <Card key={i}>
          <div className="flex items-start justify-between mb-1">
            <code className="text-[10px] text-cyan-300 bg-cyan-900/20 px-1.5 py-0.5 rounded">{s.directory}/</code>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black text-cyan-400">{s.cohesion_score}</span>
              <Badge p={s.priority} />
            </div>
          </div>
          <p className="text-[10px] text-slate-500">{s.file_count} files · {s.total_functions} funcs · {s.external_deps} ext deps · {s.effort_hours}h</p>
          <p className="text-[10px] text-slate-300 mt-1">{s.action}</p>
        </Card>
      ))}
    </div>
  );
}

function Microservices({ data }) {
  return (
    <div className="space-y-3">
      <SummaryBadge text={data.summary} />
      {data.candidates?.map((c, i) => (
        <Card key={i}>
          <div className="flex items-start justify-between mb-2">
            <div>
              <p className="text-xs font-bold text-slate-200">{c.proposed_service_name}</p>
              <code className="text-[9px] text-slate-500">{c.directory}/</code>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black text-emerald-400">{c.isolation_score}%</span>
              <Badge p={c.priority} />
            </div>
          </div>
          <p className="text-[10px] text-slate-400 mb-2">{c.total_functions} funcs · {c.transport} · {c.effort_hours}h · ext-in:{c.external_incoming} ext-out:{c.external_outgoing}</p>
          <p className="text-[10px] text-slate-300">{c.action}</p>
        </Card>
      ))}
    </div>
  );
}

function Architecture({ data }) {
  return (
    <div className="space-y-4">
      <SummaryBadge text={data.summary} />
      <div className="grid grid-cols-2 gap-3">
        <Card>
          <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Current Layers</p>
          {Object.entries(data.current_layers || {}).map(([layer, info]) => (
            <div key={layer} className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-slate-300 capitalize">{layer}</span>
              <span className="text-[10px] text-slate-500">{info.count} files</span>
            </div>
          ))}
        </Card>
        <Card>
          <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Target Architecture</p>
          {data.target_architecture?.map((t, i) => (
            <div key={i} className="mb-1">
              <p className="text-[10px] font-bold text-violet-300">{t.layer} → {t.pattern}</p>
              <p className="text-[9px] text-slate-500">{t.description}</p>
            </div>
          ))}
        </Card>
      </div>
      <p className="text-[10px] font-bold text-slate-400 uppercase">Migration Steps ({data.total_effort_hours}h total)</p>
      {data.migration_steps?.map((s, i) => (
        <Card key={i} className="flex items-start gap-3">
          <span className="text-xs font-black text-slate-600 w-5">S{s.step}</span>
          <div className="flex-1">
            <p className="text-xs font-bold text-slate-200">{s.action}</p>
            <p className="text-[10px] text-slate-500 mt-0.5">{s.detail} · {s.effort_hours}h</p>
          </div>
          <Badge p={s.priority} />
        </Card>
      ))}
    </div>
  );
}

function Simulator() {
  const [filePath, setFilePath] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  const run = async () => {
    if (!filePath.trim()) return;
    setLoading(true); setErr(null); setResult(null);
    try { setResult(await simulateRefactoring(filePath.trim())); }
    catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div className="space-y-4">
      <p className="text-[11px] text-slate-400">Enter a file path from your analyzed repository to simulate refactoring impact.</p>
      <div className="flex gap-2">
        <input
          value={filePath} onChange={e => setFilePath(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && run()}
          placeholder="e.g. dna/reasoning/scores_engine.py"
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-slate-200 outline-none focus:border-violet-500/50 transition-all"
        />
        <button onClick={run} disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-bold transition-all disabled:opacity-50">
          {loading ? '...' : 'Simulate'}
        </button>
      </div>
      {err && <p className="text-xs text-red-400 bg-red-900/20 px-3 py-2 rounded-lg">{err}</p>}
      {result && (
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Risk Score', val: result.simulation.risk_score, color: result.simulation.risk_score > 60 ? 'text-red-400' : 'text-emerald-400' },
              { label: 'Benefit Score', val: result.simulation.benefit_score, color: 'text-violet-400' },
              { label: 'Effort Hours', val: result.simulation.effort_hours, color: 'text-amber-400' },
            ].map(c => (
              <Card key={c.label} className="text-center">
                <div className={`text-2xl font-black ${c.color}`}>{c.val}</div>
                <div className="text-[10px] text-slate-400 uppercase tracking-widest mt-1">{c.label}</div>
              </Card>
            ))}
          </div>
          <Card>
            <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Metrics</p>
            <div className="grid grid-cols-3 gap-2 text-[11px]">
              {Object.entries(result.metrics).map(([k, v]) => (
                <div key={k}><span className="text-slate-500 capitalize">{k.replace(/_/g,' ')}: </span><span className="text-slate-200 font-bold">{v}</span></div>
              ))}
            </div>
          </Card>
          <Card className="border-violet-800/40 bg-violet-900/10">
            <span className="material-symbols-outlined text-violet-400 text-[16px] mr-2 align-middle">info</span>
            <span className="text-xs text-violet-200">{result.simulation.recommendation}</span>
          </Card>
          {result.simulation.affected_files?.length > 0 && (
            <Card>
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Files Requiring Update ({result.simulation.files_requiring_update})</p>
              <div className="flex flex-wrap gap-1">{result.simulation.affected_files.map((f, i) => <FileTag key={i} path={f} />)}</div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}

export default function RefactoringSuite() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('one_click_plan');

  useEffect(() => {
    getRefactoringAnalysis()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <>
      <PageHeader title="Refactoring Suite" subtitle="AI-driven refactoring analysis — 10 real-world strategies" />
      <div className="flex-1 flex items-center justify-center py-40">
        <div className="w-12 h-12 rounded-full border-4 border-violet-500/20 border-t-violet-500 animate-spin" />
      </div>
    </>
  );

  if (error || !data) return (
    <>
      <PageHeader title="Refactoring Suite" subtitle="AI-driven refactoring analysis — 10 real-world strategies" />
      <div className="flex-1 flex flex-col items-center justify-center gap-4 py-20">
        <span className="material-symbols-outlined text-red-400 text-[40px]">error</span>
        <p className="text-sm text-slate-400 max-w-md text-center">{error || 'Run an analysis first.'}</p>
      </div>
    </>
  );

  const panels = {
    one_click_plan: <OneClickPlan data={data.one_click_plan} />,
    dead_code: <DeadCode data={data.dead_code} />,
    duplicate_removal: <DuplicateRemoval data={data.duplicate_removal} />,
    class_splits: <ClassSplits data={data.class_splits} />,
    package_splits: <PackageSplits data={data.package_splits} />,
    dependency_breaks: <DependencyBreaks data={data.dependency_breaks} />,
    modularization: <Modularization data={data.modularization} />,
    microservices: <Microservices data={data.microservices} />,
    architecture_migration: <Architecture data={data.architecture_migration} />,
    simulator: <Simulator />,
  };

  return (
    <>
      <PageHeader title="Refactoring Suite" subtitle="AI-driven refactoring analysis — 10 real-world strategies" />
      <div className="p-6 max-w-[1400px] mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar nav */}
          <div className="flex flex-col gap-1.5">
            {TABS.map(t => (
              <button key={t.key} onClick={() => setActiveTab(t.key)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-200 text-xs font-semibold ${
                  activeTab === t.key
                    ? 'bg-violet-600/20 border border-violet-500/40 text-violet-200'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
                }`}>
                <span className="material-symbols-outlined text-[16px]">{t.icon}</span>
                {t.label}
              </button>
            ))}
            <div className="mt-3 p-3 rounded-xl bg-white/3 border border-white/8 text-center">
              <p className="text-[9px] text-slate-500 uppercase tracking-widest">Analyzed</p>
              <p className="text-lg font-black text-violet-400">{data.total_source_files}</p>
              <p className="text-[9px] text-slate-500">source files</p>
              <p className="text-lg font-black text-amber-400 mt-1">{data.total_functions}</p>
              <p className="text-[9px] text-slate-500">functions</p>
            </div>
          </div>

          {/* Main panel */}
          <div className="lg:col-span-3 min-h-[600px]">
            <div className="mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-violet-400 text-[20px]">
                {TABS.find(t => t.key === activeTab)?.icon}
              </span>
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                {TABS.find(t => t.key === activeTab)?.label}
              </h2>
            </div>
            {panels[activeTab]}
          </div>
        </div>
      </div>
    </>
  );
}
