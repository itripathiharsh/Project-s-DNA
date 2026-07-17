import { useState, useEffect } from 'react';
import { getFolderHeatmap } from '../services/api';
import PageHeader from '../components/PageHeader';

export default function FolderHeatmap() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFolder, setSelectedFolder] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await getFolderHeatmap();
        setData(result);
        if (result.folders && result.folders.length > 0) {
          setSelectedFolder(result.folders[0]);
        }
      } catch (err) {
        console.error('Error fetching folder heatmap:', err);
        setError(err.message || 'Failed to fetch folder metrics.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getFolderColor = (fileCount) => {
    if (fileCount >= 20) return '#ff007f'; // Critical (rose)
    if (fileCount >= 10) return '#ffaa00'; // High (amber)
    if (fileCount >= 3) return '#00bbf9';  // Moderate (cyan)
    return '#10b981'; // Low (emerald)
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-[36px] text-primary animate-spin">sync</span>
          <span className="text-xs text-text-muted">Aggregating directory-level metrics...</span>
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

  const folders = data?.folders || [];

  return (
    <>
      <PageHeader 
        title="Folder Heatmap" 
        subtitle="Directory-level aggregation of size, count, and complexity" 
      />
      <div className="p-6 flex flex-col lg:flex-row gap-6 max-w-[1600px] mx-auto w-full flex-1">
        
        {/* Main Grid */}
        <div className="flex-1 flex flex-col gap-6 min-w-0">
          <div className="card-base flex-1 flex flex-col min-h-[450px]">
            <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Directory Matrix</h3>
                <p className="text-[10px] text-text-muted mt-0.5">Colors indicate volume of files within the directory.</p>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-3 overflow-y-auto max-h-[600px] pr-1">
              {folders.map((folder, i) => {
                const active = selectedFolder?.folder === folder.folder;
                const scoreColor = getFolderColor(folder.file_count);
                return (
                  <div
                    key={i}
                    onClick={() => setSelectedFolder(folder)}
                    style={{ 
                      backgroundColor: `${scoreColor}15`,
                      borderColor: scoreColor,
                      color: scoreColor
                    }}
                    className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:scale-[1.02] flex flex-col justify-between h-20 relative overflow-hidden ${active ? 'ring-2 ring-primary ring-offset-2 ring-offset-[#09090e] border-transparent' : ''}`}
                  >
                    <div className="absolute left-0 top-0 bottom-0 w-1" style={{ backgroundColor: scoreColor }} />
                    <div className="text-[10px] font-mono truncate leading-none pl-1 text-on-surface font-semibold" title={folder.folder}>
                      {folder.folder}
                    </div>
                    <div className="flex justify-between items-end mt-2 pl-1">
                      <span className="text-[9px] uppercase font-bold tracking-widest text-text-muted">Files</span>
                      <span className="font-extrabold text-[13px] text-on-surface">
                        {folder.file_count}
                      </span>
                    </div>
                  </div>
                );
              })}
              {folders.length === 0 && (
                <div className="col-span-full py-16 text-center text-text-muted text-xs">No directories found.</div>
              )}
            </div>
          </div>
        </div>

        {/* Drill-down Panel */}
        <div className="w-full lg:w-[400px] shrink-0">
          <div className="card-base sticky top-24 flex flex-col gap-5">
            <div className="border-b border-border-subtle/50 pb-3 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">folder_open</span>
              <div>
                <h3 className="font-bold text-xs uppercase tracking-wider text-on-surface">Directory Details</h3>
                <p className="text-[10px] text-text-muted">Aggregated statistics</p>
              </div>
            </div>

            {selectedFolder ? (
              <div className="flex flex-col gap-4 text-xs">
                <div className="bg-[#12121e] border border-border-subtle rounded-lg p-3">
                  <span className="text-[9px] font-bold text-primary uppercase tracking-widest block mb-1">Target Directory</span>
                  <div className="font-mono text-xs text-on-surface break-all font-semibold leading-normal">
                    {selectedFolder.folder}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg text-center">
                    <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-0.5">Total Files</span>
                    <span className="text-lg font-extrabold text-signal-emerald">{selectedFolder.file_count}</span>
                  </div>
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg text-center">
                    <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-0.5">Total LOC</span>
                    <span className="text-lg font-extrabold text-signal-cyan">{selectedFolder.loc}</span>
                  </div>
                </div>

                <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                  <div className="flex justify-between font-semibold mb-1.5">
                    <span>Aggregated Complexity</span>
                    <span className="font-bold text-primary">{selectedFolder.complexity}</span>
                  </div>
                  <p className="text-[9px] text-text-muted leading-relaxed mt-2">
                    Sum of cyclomatic complexity across all analyzed functions inside this directory.
                  </p>
                </div>

                {/* Insight Interpretation Box */}
                <div className="mt-2 p-3 bg-primary/5 border border-primary/20 rounded-lg relative overflow-hidden">
                  <div className="absolute top-0 left-0 bottom-0 w-1 bg-primary" style={{ backgroundColor: getFolderColor(selectedFolder.file_count) }} />
                  <span className="flex items-center gap-1.5 font-bold text-[10px] uppercase tracking-wider mb-2" style={{ color: getFolderColor(selectedFolder.file_count) }}>
                    <span className="material-symbols-outlined text-[14px]">psychology</span>
                    Insight Interpretation
                  </span>
                  <p className="text-xs text-on-surface/80 leading-relaxed">
                    {selectedFolder.file_count >= 20 ? 
                      "This directory is extremely dense and contains a high volume of files. " : 
                     selectedFolder.file_count >= 10 ? 
                      "This directory is moderately large. " : 
                      "This directory is small and focused. "}
                    
                    {selectedFolder.loc > 5000 && "It holds a massive amount of code (over 5k LOC), which can be an indicator of a monolithic structure. "}
                    {selectedFolder.complexity > 500 && "The aggregated complexity here is very high, suggesting deeply nested logic or many interdependent functions. "}
                    
                    {selectedFolder.file_count >= 20 ? 
                      "Consider splitting this folder into smaller, more modular sub-packages to improve maintainability." : 
                      "The folder structure appears healthy and manageable."}
                  </p>
                </div>

              </div>
            ) : (
              <p className="text-xs text-text-muted text-center py-10">Select a directory cell to review folder metrics.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
