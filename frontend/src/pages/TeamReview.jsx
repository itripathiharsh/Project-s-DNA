import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { getReviews, createReview } from '../services/api';

export default function TeamReview() {
  const [reviews, setReviews] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [repoPath, setRepoPath] = useState('');
  const [assignees, setAssignees] = useState('');
  const [files, setFiles] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadReviews() {
      try {
        const res = await getReviews();
        setReviews(res.reviews || []);
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    loadReviews();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !description) return;
    try {
      const payload = {
        title,
        description,
        repo_path: repoPath || 'F:\\code\\project DNA',
        assignees: assignees.split(',').map((s) => s.trim()).filter(Boolean),
        files: files.split(',').map((s) => s.trim()).filter(Boolean),
      };
      const res = await createReview(payload);
      setShowModal(false);
      setTitle('');
      setDescription('');
      setAssignees('');
      setFiles('');
      const updated = await getReviews();
      setReviews(updated.reviews || []);
      navigate(`/reviews/active?id=${res.id}`);
    } catch (err) {
      alert('Failed to create review: ' + err.message);
    }
  };

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
      <PageHeader
        title="Team Code Reviews"
        subtitle="Manage collaborative review sessions and architectural audits"
        actions={
          <button onClick={() => setShowModal(true)} className="btn-primary px-4 py-2 text-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
            <span className="material-symbols-outlined text-[15px]">add</span> Create Review
          </button>
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {reviews.map((rev) => (
              <div
                key={rev.id}
                onClick={() => navigate(`/reviews/active?id=${rev.id}`)}
                className="card-base card-hover flex flex-col justify-between p-5 bg-[#09090e]/60 border border-border-subtle hover:border-primary/45 hover:shadow-[0_8px_32px_rgba(157,78,221,0.06)] relative overflow-hidden group"
              >
                <div>
                  <div className="flex items-center justify-between gap-3 mb-2">
                    <span className="font-extrabold text-sm text-on-surface group-hover:text-primary transition-colors cursor-pointer truncate max-w-[70%]">{rev.title}</span>
                    <span className={`badge ${rev.status === 'open' ? 'badge-info' : rev.status === 'merged' ? 'badge-ok' : 'badge-warn'}`}>
                      {rev.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-on-surface-variant line-clamp-2 leading-relaxed mb-4">{rev.description}</p>
                </div>
                
                <div className="flex flex-col gap-3 border-t border-border-subtle/50 pt-4 mt-1">
                  <div className="flex justify-between items-center text-xs">
                    {/* Avatars Stack */}
                    <div className="flex items-center">
                      <div className="flex -space-x-2 overflow-hidden mr-2">
                        {rev.assignees.map((name, i) => (
                          <div
                            key={i}
                            className={`inline-flex items-center justify-center w-6 h-6 rounded-full border border-[#070709] font-extrabold text-[8px] ${getAvatarColor(name)}`}
                            title={name}
                          >
                            {getInitials(name)}
                          </div>
                        ))}
                      </div>
                      <span className="text-[10px] text-text-muted truncate max-w-[120px]">
                        {rev.assignees.length ? rev.assignees.join(', ') : 'No assignees'}
                      </span>
                    </div>
                    
                    <span className="font-code-sm text-[10px] text-primary bg-surface-container-low px-2 py-0.5 border border-border-subtle rounded-md">
                      {rev.files.length} targets
                    </span>
                  </div>
                  <div className="text-[9px] text-text-muted font-semibold uppercase tracking-wider">
                    Created {new Date(rev.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
            {reviews.length === 0 && (
              <div className="col-span-2 py-16 text-center text-text-muted text-xs">
                No active code review sessions. Click Create Review to begin a new audit.
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
                <span className="material-symbols-outlined text-primary">rate_review</span>
                <h3 className="font-extrabold text-sm text-on-surface uppercase tracking-wider">New Review Session</h3>
              </div>
              <button onClick={() => setShowModal(false)} className="text-on-surface-variant hover:text-on-surface p-1 rounded-lg hover:bg-surface-container-high/40 transition-all">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-4 font-sans text-xs">
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Review Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Verify connection pool robustness"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="input-base"
                />
              </div>
              
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Description</label>
                <textarea
                  required
                  rows="3"
                  placeholder="Explain what to audit and verify during the session."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="input-base resize-none"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Repository Path</label>
                <input
                  type="text"
                  placeholder="e.g. F:\code\project DNA"
                  value={repoPath}
                  onChange={(e) => setRepoPath(e.target.value)}
                  className="input-base"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Assignees (comma separated)</label>
                <input
                  type="text"
                  placeholder="e.g. Alice Johnson, Bob Smith"
                  value={assignees}
                  onChange={(e) => setAssignees(e.target.value)}
                  className="input-base"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Files (comma separated)</label>
                <input
                  type="text"
                  placeholder="e.g. backend/dna/api/app.py"
                  value={files}
                  onChange={(e) => setFiles(e.target.value)}
                  className="input-base"
                />
              </div>
              
              <div className="flex justify-end gap-3 mt-3 pt-3 border-t border-border-subtle/50">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary px-5 py-2 text-xs">
                  Cancel
                </button>
                <button type="submit" className="btn-primary px-5 py-2 text-xs hover:scale-[1.02] active:scale-[0.98] transition-all">
                  Start Session
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
