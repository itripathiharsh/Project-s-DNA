import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { getPipelines } from '../services/api';

export default function RefactoringVerification() {
  const [searchParams] = useSearchParams();
  const pid = searchParams.get('id');
  const [pipelines, setPipelines] = useState([]);
  const [selectedPipeline, setSelectedPipeline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadPipelines() {
      try {
        const res = await getPipelines();
        setPipelines(res.pipelines || []);
        if (pid) {
          const pipe = (res.pipelines || []).find((p) => p.id === pid);
          if (pipe) setSelectedPipeline(pipe);
        } else if (res.pipelines && res.pipelines.length > 0) {
          setSelectedPipeline(res.pipelines[0]);
        }
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    loadPipelines();
  }, [pid]);

  const handleSelectPipeline = (pipe) => {
    setSelectedPipeline(pipe);
  };

  const MOCK_AFFECTED_FILES = [
    'backend/dna/api/app.py',
    'backend/dna/storage/store.py',
    'backend/dna/storage/system.py',
  ];

  return (
    <>
      <PageHeader
        title="Verification & Impact"
        subtitle="Verify architectural constraints and measure reduction in complexity"
        actions={
          <button onClick={() => navigate('/refactoring')} className="btn-secondary px-4 py-2 text-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
            <span className="material-symbols-outlined text-[15px]">arrow_back</span> Back to Roadmap
          </button>
        }
      />
      
      <div className="p-6 flex-1 flex flex-col lg:flex-row gap-6 overflow-hidden max-h-[calc(100vh-140px)] max-w-[1600px] mx-auto w-full">
        {loading ? (
          <div className="flex-1 flex justify-center items-center py-20">
            <div className="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-signal-rose card-base flex-1 p-5 border border-signal-rose/30 bg-signal-rose/5 text-xs font-semibold">{error}</div>
        ) : (
          <>
            {/* Left Column: List of Pipelines */}
            <div className="w-full lg:w-80 card-base flex flex-col gap-4 overflow-y-auto bg-surface-container/30 border border-border-subtle shadow-xl flex-shrink-0">
              <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider pb-2 border-b border-border-subtle/50 flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[18px]">view_list</span> 
                <span>Pipelines</span>
              </h3>
              
              <div className="space-y-2">
                {pipelines.map((pipe) => (
                  <div
                    key={pipe.id}
                    onClick={() => handleSelectPipeline(pipe)}
                    className={`p-3.5 rounded-xl border cursor-pointer relative overflow-hidden transition-all duration-200 ${
                      selectedPipeline?.id === pipe.id
                        ? 'bg-primary/10 border-primary shadow-[0_0_15px_rgba(157,78,221,0.06)]'
                        : 'bg-surface-container-low/40 border-border-subtle hover:bg-surface-container-high/30 hover:border-outline/25'
                    }`}
                  >
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" style={{ display: selectedPipeline?.id === pipe.id ? 'block' : 'none' }} />
                    <div className="flex justify-between items-center mb-1.5 gap-2">
                      <span className="text-xs font-semibold text-on-surface truncate max-w-[70%]">{pipe.name}</span>
                      <span className={`badge ${pipe.status === 'success' ? 'badge-ok' : 'badge-warn'} text-[9px]`}>
                        {pipe.status}
                      </span>
                    </div>
                    <div className="text-[10px] text-text-muted">
                      Created {new Date(pipe.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
                {pipelines.length === 0 && (
                  <p className="text-text-muted text-xs text-center py-4">No pipelines available.</p>
                )}
              </div>
            </div>

            {/* Right Column: Impact Report & Diff triggers */}
            <div className="flex-1 card-base flex flex-col gap-4 overflow-y-auto bg-surface-container/30 border border-border-subtle shadow-xl">
              {selectedPipeline ? (
                <>
                  <div className="flex items-center justify-between border-b border-border-subtle/50 pb-3 gap-3">
                    <span className="font-extrabold text-sm text-primary uppercase tracking-wider">{selectedPipeline.name}</span>
                    <button
                      onClick={() => navigate(`/refactoring/pipeline?id=${selectedPipeline.id}`)}
                      className="btn-primary py-1.5 px-4 text-[11px] hover:scale-[1.02] active:scale-[0.98] transition-all"
                    >
                      View Pipeline Execution
                    </button>
                  </div>

                  <p className="text-xs text-on-surface-variant leading-relaxed">{selectedPipeline.description}</p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-2">
                    <div className="bg-surface-container-low/40 border border-border-subtle/70 p-4 rounded-xl shadow-inner">
                      <div className="text-text-muted font-bold text-[10px] uppercase tracking-wider mb-1">Files Affected</div>
                      <div className="font-code-md text-xl font-extrabold text-on-surface">{selectedPipeline.impact_report.files_affected}</div>
                    </div>
                    <div className="bg-surface-container-low/40 border border-border-subtle/70 p-4 rounded-xl shadow-inner">
                      <div className="text-text-muted font-bold text-[10px] uppercase tracking-wider mb-1">Complexity Reduction</div>
                      <div className="font-code-md text-xl font-extrabold text-signal-emerald">-{selectedPipeline.impact_report.estimated_complexity_decrease} points</div>
                    </div>
                    <div className="bg-surface-container-low/40 border border-border-subtle/70 p-4 rounded-xl shadow-inner">
                      <div className="text-text-muted font-bold text-[10px] uppercase tracking-wider mb-1">Risk Reduction Status</div>
                      <div className="badge badge-info mt-1.5 text-[10px] inline-block">{selectedPipeline.impact_report.risk_reduction}</div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 mt-3">
                    <h4 className="font-bold text-xs text-on-surface uppercase tracking-wider flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-primary text-[18px]">difference</span> 
                      <span>Verify Source Code Diffs</span>
                    </h4>
                    <p className="text-[11px] text-text-muted leading-relaxed">
                      Compare target transformation nodes. Click on any file path below to launch the side-by-side AST structural diff verification editor.
                    </p>
                    
                    <div className="space-y-2 mt-2">
                      {MOCK_AFFECTED_FILES.map((file, i) => (
                        <div
                          key={i}
                          onClick={() => navigate(`/diff?path=${encodeURIComponent(file)}`)}
                          className="p-3 bg-surface-container-low/40 hover:bg-surface-container-high/30 border border-border-subtle rounded-xl cursor-pointer hover:border-primary/30 transition-all duration-200 flex items-center justify-between"
                        >
                          <div className="flex items-center gap-2.5 min-w-0 pr-2">
                            <span className="material-symbols-outlined text-primary text-[16px]">code</span>
                            <span className="font-code-sm text-xs text-on-surface truncate">{file}</span>
                          </div>
                          <div className="flex items-center gap-3 flex-shrink-0">
                            <span className="badge badge-ok text-[9px]">Verified</span>
                            <span className="material-symbols-outlined text-text-muted text-[14px]">chevron_right</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 py-20 max-w-sm mx-auto">
                  <span className="material-symbols-outlined text-[48px] text-on-surface-variant">fact_check</span>
                  <div>
                    <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider mb-1">No pipeline selected</h3>
                    <p className="text-on-surface-variant text-[11px] leading-relaxed">Select a refactoring pipeline on the left to review its verification status and code diffs.</p>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </>
  );
}
