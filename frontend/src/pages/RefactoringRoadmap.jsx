import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { getPipelines, createPipeline } from '../services/api';

export default function RefactoringRoadmap() {
  const [pipelines, setPipelines] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [tasksStr, setTasksStr] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadPipelines() {
      try {
        const res = await getPipelines();
        setPipelines(res.pipelines || []);
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    loadPipelines();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !description) return;
    try {
      const taskList = tasksStr
        .split('\n')
        .map((t, i) => t.trim())
        .filter(Boolean)
        .map((taskName, i) => ({
          id: i + 1,
          name: taskName,
          status: 'pending',
          log: '',
        }));

      const payload = {
        name,
        description,
        tasks: taskList.length > 0 ? taskList : [
          { id: 1, name: 'Backup source files', status: 'pending', log: '' },
          { id: 2, name: 'Apply automatic AST transformation', status: 'pending', log: '' },
          { id: 3, name: 'Verify structural compilation', status: 'pending', log: '' }
        ],
        impact_report: {
          files_affected: Math.floor(Math.random() * 4) + 2,
          risk_reduction: 'Medium-to-High',
          estimated_complexity_decrease: Math.floor(Math.random() * 3) + 2,
        },
      };
      const res = await createPipeline(payload);
      setShowModal(false);
      setName('');
      setDescription('');
      setTasksStr('');
      navigate(`/refactoring/pipeline?id=${res.id}`);
    } catch (err) {
      alert('Failed to create pipeline: ' + err.message);
    }
  };

  return (
    <>
      <PageHeader
        title="Refactoring Roadmap"
        subtitle="Manage architectural improvements and codebase transformations"
        actions={
          <div className="flex gap-2.5">
            <button onClick={() => navigate('/refactoring/verify')} className="btn-secondary px-4 py-2 text-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
              <span className="material-symbols-outlined text-[15px]">fact_check</span> Verification & Impact
            </button>
            <button onClick={() => setShowModal(true)} className="btn-primary px-4 py-2 text-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
              <span className="material-symbols-outlined text-[15px]">add</span> Plan Refactoring
            </button>
          </div>
        }
      />
      
      <div className="p-6 flex flex-col gap-6 max-w-[1200px] mx-auto w-full">
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-signal-rose card-base p-5 border border-signal-rose/30 bg-signal-rose/5 text-xs font-semibold">{error}</div>
        ) : (
          <div className="space-y-4">
            {pipelines.map((pipe) => (
              <div
                key={pipe.id}
                onClick={() => navigate(`/refactoring/pipeline?id=${pipe.id}`)}
                className="card-base card-hover flex flex-col md:flex-row justify-between items-start md:items-center gap-5 p-5 bg-[#09090e]/60 border border-border-subtle hover:border-primary/40 hover:shadow-[0_8px_32px_rgba(157,78,221,0.06)] relative overflow-hidden"
              >
                {/* Visual side accent */}
                <div className={`absolute left-0 top-0 bottom-0 w-1 ${pipe.status === 'success' ? 'bg-signal-emerald' : pipe.status === 'failed' ? 'bg-signal-rose' : 'bg-signal-amber'}`} />
                
                <div className="flex-1 flex flex-col gap-1.5 pl-2">
                  <div className="flex items-center gap-3 flex-wrap">
                    <span className="font-extrabold text-sm text-on-surface hover:text-primary transition-colors cursor-pointer">{pipe.name}</span>
                    <span className={`badge ${pipe.status === 'success' ? 'badge-ok' : pipe.status === 'failed' ? 'badge-high' : 'badge-warn'}`}>
                      {pipe.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-on-surface-variant max-w-2xl leading-relaxed">{pipe.description}</p>
                </div>
                
                <div className="flex items-center gap-6 border-t md:border-t-0 border-border-subtle/50 pt-3.5 md:pt-0 w-full md:w-auto text-[10px] text-text-muted justify-between md:justify-end">
                  <div className="flex flex-col">
                    <span className="font-bold uppercase tracking-wider text-[9px]">Affected</span>
                    <span className="font-code-sm text-xs font-semibold text-on-surface mt-0.5">{pipe.impact_report.files_affected} files</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="font-bold uppercase tracking-wider text-[9px]">Complexity</span>
                    <span className="font-code-sm text-xs font-semibold text-signal-rose mt-0.5">-{pipe.impact_report.estimated_complexity_decrease} pts</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="font-bold uppercase tracking-wider text-[9px]">Risk Reduction</span>
                    <span className="badge badge-info mt-1">{pipe.impact_report.risk_reduction}</span>
                  </div>
                  <span className="material-symbols-outlined text-text-muted text-[18px] hidden md:block">chevron_right</span>
                </div>
              </div>
            ))}
            {pipelines.length === 0 && (
              <div className="py-16 text-center text-text-muted text-xs">
                No active refactoring roadmaps configured. Click Plan Refactoring to layout a new code optimization task.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modal Dialog */}
      {showModal && (
        <div className="fixed inset-0 bg-black/85 flex items-center justify-center p-4 z-50 backdrop-blur-md">
          <div className="bg-[#09090e] border border-border-subtle rounded-2xl max-w-lg w-full p-6 flex flex-col gap-4 shadow-2xl animate-fade-in relative">
            <div className="flex justify-between items-center border-b border-border-subtle/50 pb-3">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">construction</span>
                <h3 className="font-extrabold text-sm text-on-surface uppercase tracking-wider">Plan Refactoring Pipeline</h3>
              </div>
              <button onClick={() => setShowModal(false)} className="text-on-surface-variant hover:text-on-surface p-1 rounded-lg hover:bg-surface-container-high/40 transition-all">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-4 font-sans text-xs">
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Pipeline Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Decouple storage module import cycle"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input-base"
                />
              </div>
              
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Description Summary</label>
                <textarea
                  required
                  rows="2"
                  placeholder="Summarize the codebase restructuring goal."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="input-base resize-none"
                />
              </div>
              
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Tasks list (one per line)</label>
                <textarea
                  rows="4"
                  placeholder="Backup source files&#10;Extract circular imports to leaf modules&#10;Verify code compilations"
                  value={tasksStr}
                  onChange={(e) => setTasksStr(e.target.value)}
                  className="input-base font-code-sm resize-none"
                />
              </div>
              
              <div className="flex justify-end gap-3 mt-3 pt-3 border-t border-border-subtle/50">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary px-5 py-2 text-xs">
                  Cancel
                </button>
                <button type="submit" className="btn-primary px-5 py-2 text-xs hover:scale-[1.02] active:scale-[0.98] transition-all">
                  Create Pipeline
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
