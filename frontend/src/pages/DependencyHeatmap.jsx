import { useState, useEffect } from 'react';
import { getDependencyHeatmap } from '../services/api';
import PageHeader from '../components/PageHeader';

export default function DependencyHeatmap() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await getDependencyHeatmap();
        setData(result);
        if (result.files && result.files.length > 0) {
          setSelectedFile(result.files[0]);
        }
      } catch (err) {
        console.error('Error fetching dependency heatmap:', err);
        setError(err.message || 'Failed to fetch dependency metrics.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getDepColor = (extCount) => {
    if (extCount >= 10) return '#ff007f'; // Critical (rose)
    if (extCount >= 5) return '#ffaa00'; // High (amber)
    if (extCount >= 2) return '#00bbf9';  // Moderate (cyan)
    return '#10b981'; // Low (emerald)
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-[36px] text-primary animate-spin">sync</span>
          <span className="text-xs text-text-muted">Analyzing import graphs for dependencies...</span>
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
        title="Dependency Heatmap" 
        subtitle="Internal vs External dependencies and package surface area" 
      />
      <div className="p-6 flex flex-col lg:flex-row gap-6 max-w-[1600px] mx-auto w-full flex-1">
        
        {/* Main Grid */}
        <div className="flex-1 flex flex-col gap-6 min-w-0">
          <div className="card-base flex-1 flex flex-col min-h-[450px]">
            <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Dependency Matrix</h3>
                <p className="text-[10px] text-text-muted mt-0.5">Colors indicate volume of external third-party dependencies.</p>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-3 overflow-y-auto max-h-[600px] pr-1">
              {files.map((file, i) => {
                const active = selectedFile?.file_path === file.file_path;
                const scoreColor = getDepColor(file.external);
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
                      <span className="text-[9px] uppercase font-bold tracking-widest text-text-muted">Ext. Deps</span>
                      <span className="font-extrabold text-[13px] text-on-surface">
                        {file.external}
                      </span>
                    </div>
                  </div>
                );
              })}
              {files.length === 0 && (
                <div className="col-span-full py-16 text-center text-text-muted text-xs">No dependencies found.</div>
              )}
            </div>
          </div>
        </div>

        {/* Drill-down Panel */}
        <div className="w-full lg:w-[400px] shrink-0">
          <div className="card-base sticky top-24 flex flex-col gap-5">
            <div className="border-b border-border-subtle/50 pb-3 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">extension</span>
              <div>
                <h3 className="font-bold text-xs uppercase tracking-wider text-on-surface">Package Details</h3>
                <p className="text-[10px] text-text-muted">Import statistics</p>
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
                    <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-0.5">Internal Imports</span>
                    <span className="text-lg font-extrabold text-signal-emerald">{selectedFile.internal}</span>
                  </div>
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg text-center">
                    <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-0.5">External Imports</span>
                    <span className="text-lg font-extrabold text-signal-rose">{selectedFile.external}</span>
                  </div>
                </div>

                <div className="p-3 bg-[#12121e] border border-border-subtle rounded-lg text-center mt-2">
                  <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-1">External Dependency Ratio</span>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-surface-container-low rounded-full overflow-hidden flex">
                      <div className="h-full bg-signal-amber" style={{ width: `${Math.min(100, ((selectedFile.external_deps?.length || 0) / Math.max(1, (selectedFile.external_deps?.length || 0) + (selectedFile.internal_deps?.length || 0))) * 100)}%` }} />
                      <div className="h-full bg-signal-emerald" style={{ width: `${Math.min(100, ((selectedFile.internal_deps?.length || 0) / Math.max(1, (selectedFile.external_deps?.length || 0) + (selectedFile.internal_deps?.length || 0))) * 100)}%` }} />
                    </div>
                  </div>
                  <div className="flex justify-between mt-1 text-[9px] font-semibold text-text-muted">
                    <span className="text-signal-amber">External</span>
                    <span className="text-signal-emerald">Internal</span>
                  </div>
                </div>

                {/* Insight Interpretation Box */}
                <div className="mt-2 p-3 bg-primary/5 border border-primary/20 rounded-lg relative overflow-hidden">
                  <div className="absolute top-0 left-0 bottom-0 w-1 bg-primary" style={{ backgroundColor: getDependencyColor(selectedFile.total_deps) }} />
                  <span className="flex items-center gap-1.5 font-bold text-[10px] uppercase tracking-wider mb-2" style={{ color: getDependencyColor(selectedFile.total_deps) }}>
                    <span className="material-symbols-outlined text-[14px]">psychology</span>
                    Insight Interpretation
                  </span>
                  <p className="text-xs text-on-surface/80 leading-relaxed">
                    {selectedFile.total_deps >= 15 ? 
                      "This file has an extremely high volume of dependencies, meaning it relies heavily on external context to function. " : 
                     selectedFile.total_deps >= 8 ? 
                      "This file has a moderately high dependency load. " : 
                      "This file has a low dependency load and is fairly self-contained. "}
                    
                    {(selectedFile.external_deps?.length || 0) > (selectedFile.internal_deps?.length || 0) ? 
                      "It relies primarily on 3rd-party libraries, which increases supply-chain risk and makes mocking tests harder. " : 
                     (selectedFile.internal_deps?.length || 0) > (selectedFile.external_deps?.length || 0) ? 
                      "It primarily orchestrates internal project modules, indicating it acts as a local coordinator or service layer. " : ""}
                    
                    {selectedFile.total_deps >= 15 ? 
                      "Consider breaking out the logic into separate focused modules (Single Responsibility Principle)." : ""}
                  </p>
                </div>

                <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                  <div className="flex justify-between font-semibold mb-1.5">
                    <span>External Packages Used</span>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {selectedFile.packages && selectedFile.packages.length > 0 ? (
                      selectedFile.packages.map((pkg, idx) => (
                        <span key={idx} className="bg-[#12121e] text-on-surface font-mono text-[9px] px-2 py-1 rounded border border-border-subtle">
                          {pkg}
                        </span>
                      ))
                    ) : (
                      <span className="text-text-muted text-[10px]">None</span>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-text-muted text-center py-10">Select a file cell to review dependency metrics.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
