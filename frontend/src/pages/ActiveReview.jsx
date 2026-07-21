import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { getReview, addReviewComment, updateReviewStatus } from '../services/api';
import { useNotification } from '../components/NotificationContext';

export default function ActiveReview() {
  const [searchParams] = useSearchParams();
  const rid = searchParams.get('id');
  const [review, setReview] = useState(null);
  const [commentText, setCommentText] = useState('');
  const [commentAuthor, setCommentAuthor] = useState('Alice Johnson');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { toast } = useNotification();

  useEffect(() => {
    if (!rid) {
      setError('No review ID provided in parameters.');
      setLoading(false);
      return;
    }

    async function loadReview() {
      try {
        const res = await getReview(rid);
        setReview(res);
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    loadReview();
  }, [rid]);

  const handlePostComment = async (e) => {
    e.preventDefault();
    if (!commentText) return;
    try {
      await addReviewComment(rid, {
        author: commentAuthor,
        text: commentText
      });
      setCommentText('');
      const updated = await getReview(rid);
      setReview(updated);
      toast('Comment posted successfully', 'success');
    } catch (err) {
      toast('Failed to post comment: ' + err.message, 'error');
    }
  };

  const handleStatusChange = async (status) => {
    try {
      await updateReviewStatus(rid, status);
      const updated = await getReview(rid);
      setReview(updated);
      toast('Status changed to ' + status, 'success');
    } catch (err) {
      toast('Failed to change status: ' + err.message, 'error');
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
        title={review ? `Active Review: ${review.title}` : 'Active Review'}
        subtitle={review ? `Status: ${review.status.toUpperCase()} | Created ${new Date(review.created_at).toLocaleString()}` : ''}
        actions={
          <div className="flex gap-2.5">
            <button onClick={() => navigate('/reviews')} className="btn-secondary px-4 py-2 text-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
              <span className="material-symbols-outlined text-[15px]">arrow_back</span> All Reviews
            </button>
            {review && review.status === 'open' && (
              <>
                <button onClick={() => handleStatusChange('merged')} className="btn-primary px-4 py-2 text-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
                  <span className="material-symbols-outlined text-[15px]">check</span> Merge
                </button>
                <button onClick={() => handleStatusChange('closed')} className="btn-secondary !text-signal-rose border-signal-rose/30 hover:bg-signal-rose/10 px-4 py-2 text-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all">
                  <span className="material-symbols-outlined text-[15px]">close</span> Close
                </button>
              </>
            )}
          </div>
        }
      />
      
      <div className="p-6 flex-1 flex flex-col lg:flex-row gap-6 overflow-hidden max-h-[calc(100vh-140px)] max-w-[1600px] mx-auto w-full">
        {loading ? (
          <div className="flex-1 flex justify-center items-center py-20">
            <div className="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-signal-rose card-base flex-1 p-5 border border-signal-rose/30 bg-signal-rose/5 text-xs font-semibold">{error}</div>
        ) : review ? (
          <>
            {/* Left Column: Comments Feed & Post form */}
            <div className="flex-1 card-base flex flex-col overflow-hidden bg-surface-container/30 border border-border-subtle p-0 shadow-2xl">
              <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider p-4 border-b border-border-subtle/50 flex items-center gap-1.5 bg-surface-container/20">
                <span className="material-symbols-outlined text-primary text-[18px]">chat_bubble</span> 
                <span>Comment Thread</span>
              </h3>
              
              {/* Messages list */}
              <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4 scrollbar-hide">
                {review.comments.map((comment) => (
                  <div key={comment.id} className="p-4 bg-surface-container-low/40 border border-border-subtle/80 rounded-xl flex flex-col gap-2 hover:border-outline/25 transition-all">
                    <div className="flex justify-between items-center text-xs">
                      <div className="flex items-center gap-2">
                        <div className={`w-6 h-6 rounded-lg font-extrabold text-[8px] flex items-center justify-center border ${getAvatarColor(comment.author)}`}>
                          {getInitials(comment.author)}
                        </div>
                        <span className="font-bold text-primary">{comment.author}</span>
                      </div>
                      <span className="text-[10px] text-text-muted">{new Date(comment.timestamp).toLocaleTimeString()}</span>
                    </div>
                    
                    <p className="text-xs text-on-surface-variant whitespace-pre-line leading-relaxed pl-8">{comment.text}</p>
                    
                    {comment.file_path && (
                      <div className="mt-1 pl-8 flex items-center gap-1.5 text-[10px] text-text-muted">
                        <span className="material-symbols-outlined text-[12px] text-primary/80">code</span>
                        <span className="font-code-sm truncate" title={comment.file_path}>
                          {comment.file_path} (Line {comment.line})
                        </span>
                      </div>
                    )}
                  </div>
                ))}
                {review.comments.length === 0 && (
                  <p className="text-text-muted text-xs text-center py-12">No comments yet. Start the review conversation below.</p>
                )}
              </div>

              {/* Form */}
              <form onSubmit={handlePostComment} className="border-t border-border-subtle/50 p-4 bg-[#0d0d14]/80 backdrop-blur-xl flex flex-col sm:flex-row gap-3 items-center">
                <div className="flex flex-col gap-1 w-full sm:w-1/4">
                  <input
                    type="text"
                    required
                    value={commentAuthor}
                    onChange={(e) => setCommentAuthor(e.target.value)}
                    placeholder="Author"
                    className="input-base text-xs bg-surface-container-lowest/50 border border-border-subtle"
                  />
                </div>
                <div className="flex flex-col gap-1 flex-1 w-full">
                  <input
                    type="text"
                    required
                    placeholder="Add review comment or architectural suggestion..."
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    className="input-base text-xs bg-surface-container-lowest/50 border border-border-subtle"
                  />
                </div>
                <button type="submit" className="btn-primary h-[38px] px-6 py-2 text-xs hover:scale-[1.02] active:scale-[0.98] transition-all w-full sm:w-auto shrink-0">
                  Post
                </button>
              </form>
            </div>

            {/* Right Column: Files under review & details */}
            <div className="w-full lg:w-80 card-base flex flex-col gap-4 overflow-y-auto bg-surface-container/30 border border-border-subtle shadow-xl flex-shrink-0">
              <h3 className="font-bold text-xs text-on-surface uppercase tracking-wider pb-2 border-b border-border-subtle/50 flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[18px]">description</span> 
                <span>Metadata Details</span>
              </h3>
              
              <div className="flex flex-col gap-3 text-xs">
                <div className="bg-surface-container-low/40 border border-border-subtle/60 p-3 rounded-xl">
                  <span className="block text-text-muted text-[9px] font-bold uppercase tracking-wider mb-1">Description</span>
                  <p className="text-on-surface-variant leading-relaxed text-[11px]">{review.description}</p>
                </div>
                <div className="bg-surface-container-low/40 border border-border-subtle/60 p-3 rounded-xl">
                  <span className="block text-text-muted text-[9px] font-bold uppercase tracking-wider mb-1">Repository Path</span>
                  <span className="font-code-sm text-[10px] truncate block text-primary" title={review.repo_path}>{review.repo_path}</span>
                </div>
                <div className="bg-surface-container-low/40 border border-border-subtle/60 p-3 rounded-xl">
                  <span className="block text-text-muted text-[9px] font-bold uppercase tracking-wider mb-1">Assignees</span>
                  <span className="text-on-surface font-semibold text-[11px]">{review.assignees.join(', ') || 'No assignees'}</span>
                </div>
              </div>

              <div className="flex flex-col gap-2 mt-2">
                <span className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Files Under Audit</span>
                {review.files.map((file, i) => (
                  <div
                    key={i}
                    onClick={() => navigate(`/diff?path=${encodeURIComponent(file)}`)}
                    className="p-2.5 rounded-lg bg-surface-container-low/40 hover:bg-surface-container-high/30 border border-border-subtle/70 cursor-pointer hover:border-primary/30 transition-all flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center gap-2 truncate pr-2">
                      <span className="material-symbols-outlined text-[15px] text-primary/80">code</span>
                      <span className="text-on-surface truncate font-code-sm text-[11px]">{file}</span>
                    </div>
                    <span className="material-symbols-outlined text-[14px] text-text-muted">chevron_right</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          <div className="text-center text-text-muted text-xs py-8">Session index not resolved.</div>
        )}
      </div>
    </>
  );
}
