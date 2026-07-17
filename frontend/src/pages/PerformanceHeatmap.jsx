import { useState, useEffect } from 'react';
import { getPerformanceHeatmap } from '../services/api';
import PageHeader from '../components/PageHeader';

export default function PerformanceHeatmap() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await getPerformanceHeatmap();
        setData(result);
        if (result.files && result.files.length > 0) {
          setSelectedFile(result.files[0]);
        }
      } catch (err) {
        console.error('Error fetching performance heatmap:', err);
        setError(err.message || 'Failed to fetch performance metrics.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getScoreColor = (score) => {
    if (score >= 50) return '#ff007f'; // Critical (rose)
    if (score >= 20) return '#ffaa00'; // High (amber)
    if (score >= 5) return '#00bbf9';  // Moderate (cyan)
    return '#10b981'; // Low (emerald)
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-[36px] text-primary animate-spin">sync</span>
          <span className="text-xs text-text-muted">Analyzing AST for performance hotpaths...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 text-center max-w-md mx-auto">
        <span className="material-symbols-outlined text-[48px] text-signal-rose mb-3">error</span>
        <h3 className="font-bold text-base text-on-surface">Analysis Error</h3>
        <p className="text-xs text-text-muted mt-2">{error}</p>
      </div>
    );
  }

  const files = data?.files || [];

  return (
    <>
      <PageHeader 
        title="Performance Hotpaths Heatmap" 
        subtitle="Static analysis of time complexity, blocking calls, and expensive loops" 
      />
      <div className="p-6 flex flex-col lg:flex-row gap-6 max-w-[1600px] mx-auto w-full flex-1">
        
        {/* Main Grid */}
        <div className="flex-1 flex flex-col gap-6 min-w-0">
          <div className="card-base flex-1 flex flex-col min-h-[450px]">
            <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">File Performance Matrix</h3>
                <p className="text-[10px] text-text-muted mt-0.5">Colors indicate estimated time complexity severity.</p>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-3 overflow-y-auto max-h-[600px] pr-1">
              {files.map((file, i) => {
                const active = selectedFile?.file_path === file.file_path;
                const scoreColor = getScoreColor(file.time_complexity_score);
                return (
                  <div
                    key={i}
                    onClick={() => setSelectedFile(file)}
                    style={{ 
                      backgroundColor: `${scoreColor}15`,
                      borderColor: scoreColor,
                      color: scoreColor
                    }}
                    className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:scale-[1.02] flex flex-col justify-between h-20 relative overflow-hidden ${active ? 'ring-2 ring-primary ring-offset-2 ring-offset-[#09090e] border-transparent' : ''}`}
                  >
                    <div className="absolute left-0 top-0 bottom-0 w-1" style={{ backgroundColor: scoreColor }} />
                    <div className="text-[10px] font-mono truncate leading-none pl-1 text-on-surface font-semibold" title={file.file_path}>
                      {file.file_path.split('/').pop()}
                    </div>
                    <div className="flex justify-between items-end mt-2 pl-1">
                      <span className="text-[9px] uppercase font-bold tracking-widest text-text-muted">Score</span>
                      <span className="font-extrabold text-[13px] text-on-surface">
                        {file.time_complexity_score}
                      </span>
                    </div>
                  </div>
                );
              })}
              {files.length === 0 && (
                <div className="col-span-full py-16 text-center text-text-muted text-xs">No files analyzed.</div>
              )}
            </div>
          </div>
        </div>

        {/* Drill-down Panel */}
        <div className="w-full lg:w-[400px] shrink-0">
          <div className="card-base sticky top-24 flex flex-col gap-5">
            <div className="border-b border-border-subtle/50 pb-3 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">speed</span>
              <div>
                <h3 className="font-bold text-xs uppercase tracking-wider text-on-surface">Performance Detail</h3>
                <p className="text-[10px] text-text-muted">Estimated time complexity metrics</p>
              </div>
            </div>

            {selectedFile ? (
              <div className="flex flex-col gap-4 text-xs">
                <div className="bg-[#12121e] border border-border-subtle rounded-lg p-3">
                  <span className="text-[9px] font-bold text-primary uppercase tracking-widest block mb-1">Target File</span>
                  <div className="font-mono text-xs text-on-surface break-all font-semibold leading-normal">
                    {selectedFile.file_path}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg text-center">
                    <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-0.5">Expensive Loops</span>
                    <span className="text-lg font-extrabold text-signal-amber">{selectedFile.expensive_loops}</span>
                  </div>
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg text-center">
                    <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-0.5">Blocking Calls</span>
                    <span className="text-lg font-extrabold text-signal-rose">{selectedFile.blocking_calls}</span>
                  </div>
                </div>

                <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                  <div className="flex justify-between font-semibold mb-1.5">
                    <span>Est. Time Complexity Score</span>
                    <span className="font-bold text-primary">{selectedFile.time_complexity_score}</span>
                  </div>
                  <p className="text-[9px] text-text-muted leading-relaxed mt-1">
                    A combination of deep nesting depth and cyclomatic complexity denoting potentially slow execution paths.
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-xs text-text-muted text-center py-10">Select a file cell to review performance metrics.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
