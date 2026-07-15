import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { getFileDiff } from '../services/api';

export default function SideBySideDiff() {
  const [searchParams] = useSearchParams();
  const filePath = searchParams.get('path') || 'backend/dna/api/app.py';
  const [diffData, setDiffData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadDiff() {
      try {
        const res = await getFileDiff(filePath);
        setDiffData(res);
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    loadDiff();
  }, [filePath]);

  return (
    <>
      <PageHeader
        title={`Side-by-Side Diff Verification: ${filePath}`}
        subtitle="Verify structure modifications and AST refactoring correctness"
        actions={
          <button onClick={() => navigate(-1)} className="btn-secondary">
            <span className="material-symbols-outlined text-[16px]">arrow_back</span> Back
          </button>
        }
      />
      <div className="p-6 flex-1 flex gap-6 overflow-hidden max-h-[calc(100vh-140px)] font-body-sm">
        {loading ? (
          <div className="flex-1 flex justify-center items-center">
            <div className="w-10 h-10 border-4 border-surface-container-high border-t-primary rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-signal-rose card-base flex-1">{error}</div>
        ) : diffData ? (
          <div className="flex-1 flex gap-4 overflow-hidden">
            {/* Left Side: Original Code */}
            <div className="flex-1 card-base flex flex-col overflow-hidden bg-[#0d0d0d]">
              <div className="p-2 border-b border-border-subtle bg-surface-container-high font-bold text-xs text-text-muted flex justify-between">
                <span>ORIGINAL CODE</span>
                <span className="badge badge-high">Before</span>
              </div>
              <div className="flex-1 overflow-auto p-4 font-code-sm text-code-sm">
                <pre className="text-on-surface whitespace-pre">
                  {diffData.original.split('\n').map((line, idx) => {
                    const isChanged = line.trim().startsWith('import ') || line.trim().startsWith('from ') || line.includes('def ');
                    return (
                      <div key={idx} className={`flex ${isChanged ? 'bg-signal-rose/10 text-signal-rose' : ''} py-[1px]`}>
                        <span className="w-8 text-right select-none text-text-muted pr-2 border-r border-border-subtle mr-2">{idx + 1}</span>
                        <span>{line || ' '}</span>
                      </div>
                    );
                  })}
                </pre>
              </div>
            </div>

            {/* Right Side: Refactored Code */}
            <div className="flex-1 card-base flex flex-col overflow-hidden bg-[#0d0d0d]">
              <div className="p-2 border-b border-border-subtle bg-surface-container-high font-bold text-xs text-text-muted flex justify-between">
                <span>REFACTORED CODE</span>
                <span className="badge badge-ok">After</span>
              </div>
              <div className="flex-1 overflow-auto p-4 font-code-sm text-code-sm">
                <pre className="text-on-surface whitespace-pre">
                  {diffData.refactored.split('\n').map((line, idx) => {
                    const isChanged = line.includes('# Organized import') || line.includes('# Documented definition');
                    return (
                      <div key={idx} className={`flex ${isChanged ? 'bg-signal-emerald/15 text-signal-emerald' : ''} py-[1px]`}>
                        <span className="w-8 text-right select-none text-text-muted pr-2 border-r border-border-subtle mr-2">{idx + 1}</span>
                        <span>{line || ' '}</span>
                      </div>
                    );
                  })}
                </pre>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </>
  );
}
