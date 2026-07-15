import { useAnalysis } from '../store/analysis';
import PageHeader from '../components/PageHeader';

export default function Structural() {
  const { data } = useAnalysis();
  const s = data?.structural;

  if (!s) {
    return (
      <>
        <PageHeader title="Structure" subtitle="Codebase structure metrics" />
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-4">
          <span className="material-symbols-outlined text-[48px] text-on-surface-variant">account_tree</span>
          <p className="text-on-surface-variant">Run an analysis to view structure metrics.</p>
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader title="Structure" subtitle="Codebase structure metrics" />
      <div className="p-6 flex flex-col gap-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card-base"><div className="font-label-caps text-label-caps text-text-muted">Files</div><div className="text-[24px] font-bold">{s.total_files ?? 0}</div></div>
          <div className="card-base"><div className="font-label-caps text-label-caps text-text-muted">Functions</div><div className="text-[24px] font-bold">{s.total_functions ?? 0}</div></div>
          <div className="card-base"><div className="font-label-caps text-label-caps text-text-muted">Classes</div><div className="text-[24px] font-bold">{s.total_classes ?? 0}</div></div>
          <div className="card-base"><div className="font-label-caps text-label-caps text-text-muted">Imports</div><div className="text-[24px] font-bold">{s.total_imports ?? 0}</div></div>
          <div className="card-base"><div className="font-label-caps text-label-caps text-text-muted">Avg Complexity</div><div className="font-code-md text-code-md">{s.avg_complexity ?? '—'}</div></div>
          <div className="card-base"><div className="font-label-caps text-label-caps text-text-muted">Max Complexity</div><div className="font-code-md text-code-md text-signal-amber">{s.max_complexity ?? '—'}</div></div>
          <div className="card-base"><div className="font-label-caps text-label-caps text-text-muted">Avg Dir Depth</div><div className="font-code-md text-code-md">{s.avg_directory_depth ?? '—'}</div></div>
          <div className="card-base"><div className="font-label-caps text-label-caps text-text-muted">Structural Coupling</div><div className="font-code-md text-code-md">{s.structural_coupling ?? 0}</div></div>
        </div>

        <div className="card-base">
          <div className="border-b border-border-subtle pb-3 mb-4"><h2 className="font-headline-md text-headline-md">Top Directories</h2></div>
          <div className="flex flex-col gap-2">
            {(s.top_directories || []).map(([dir, count], i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded bg-surface-container border border-border-subtle">
                <code className="font-code-sm text-code-sm text-primary">{dir}</code>
                <span className="font-code-sm text-code-sm text-text-muted">{count} files</span>
              </div>
            ))}
            {!s.top_directories?.length && <p className="text-text-muted font-body-sm">No data.</p>}
          </div>
        </div>
      </div>
    </>
  );
}
