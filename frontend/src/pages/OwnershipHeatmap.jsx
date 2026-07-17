import { useState, useEffect } from 'react';
import { getOwnershipHeatmap } from '../services/api';
import PageHeader from '../components/PageHeader';

export default function OwnershipHeatmap() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await getOwnershipHeatmap();
        setData(result);
        if (result.files && result.files.length > 0) {
          setSelectedFile(result.files[0]);
        }
      } catch (err) {
        console.error('Error fetching ownership heatmap:', err);
        setError(err.message || 'Failed to fetch ownership metrics.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getOwnerColor = (owner) => {
    if (!owner || owner === 'unknown') return '#4a4a5a';
    
    // Hash name to get a consistent distinct pastel HSL color
    let hash = 0;
    for (let i = 0; i < owner.length; i++) {
      hash = owner.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    const hue = Math.abs(hash) % 360;
    return `hsl(${hue}, 60%, 45%)`;
  };

  const getRiskLabel = (score) => {
    if (score >= 0.8) return { text: 'Single Owner Risk', color: 'text-signal-rose border-signal-rose/30 bg-signal-rose/10' };
    if (score <= 0.2) return { text: 'Orphan File Risk', color: 'text-signal-amber border-signal-amber/30 bg-signal-amber/10' };
    return { text: 'Shared / Low Risk', color: 'text-signal-emerald border-signal-emerald/30 bg-signal-emerald/10' };
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-[36px] text-primary animate-spin">sync</span>
          <span className="text-xs text-text-muted">Analyzing git blame records and author shares...</span>
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

  const busFactor = data?.bus_factor ?? 1;
  const busFactorRisk = data?.bus_factor_risk ?? 'low';
  const contributors = data?.contributors || [];
  const files = data?.files || [];
  const orphanFiles = data?.orphan_files || [];
  const singleOwnerRiskFiles = data?.single_owner_risk_files || [];

  return (
    <>
      <PageHeader 
        title="Knowledge Ownership Heatmap" 
        subtitle="Git blame attribution, Bus Factor exposure, and knowledge sharing metrics" 
      />
      <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto w-full flex-1">
        
        {/* Top Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Bus Factor Card */}
          <div className="card-base flex items-center gap-4 py-5">
            <div className="w-12 h-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-[0_0_15px_rgba(157,78,221,0.15)]">
              <span className="material-symbols-outlined text-[24px]">groups</span>
            </div>
            <div>
              <span className="text-[10px] text-text-muted uppercase tracking-wider font-bold block">Bus Factor Score</span>
              <span className="text-2xl font-extrabold text-on-surface leading-none mt-1 block">{busFactor}</span>
              <span className={`text-[9px] uppercase tracking-widest font-extrabold mt-1.5 inline-block px-2 py-0.5 rounded border ${busFactorRisk === 'high' ? 'border-signal-rose/30 bg-signal-rose/10 text-signal-rose' : 'border-signal-emerald/30 bg-signal-emerald/10 text-signal-emerald'}`}>
                {busFactorRisk} Risk profile
              </span>
            </div>
          </div>

          {/* Single Owner Risk Card */}
          <div className="card-base flex items-center gap-4 py-5">
            <div className="w-12 h-12 rounded-xl bg-signal-rose/10 border border-signal-rose/20 flex items-center justify-center text-signal-rose shadow-[0_0_15px_rgba(255,0,127,0.1)]">
              <span className="material-symbols-outlined text-[24px]">person</span>
            </div>
            <div>
              <span className="text-[10px] text-text-muted uppercase tracking-wider font-bold block">Single-Owner Files</span>
              <span className="text-2xl font-extrabold text-on-surface leading-none mt-1 block">{singleOwnerRiskFiles.length}</span>
              <span className="text-[9px] text-text-muted mt-1.5 block">Files with &gt;80% ownership by one contributor.</span>
            </div>
          </div>

          {/* Orphan Files Card */}
          <div className="card-base flex items-center gap-4 py-5">
            <div className="w-12 h-12 rounded-xl bg-signal-amber/10 border border-signal-amber/20 flex items-center justify-center text-signal-amber shadow-[0_0_15px_rgba(234,179,8,0.1)]">
              <span className="material-symbols-outlined text-[24px]">question_mark</span>
            </div>
            <div>
              <span className="text-[10px] text-text-muted uppercase tracking-wider font-bold block">Orphaned Modules</span>
              <span className="text-2xl font-extrabold text-on-surface leading-none mt-1 block">{orphanFiles.length}</span>
              <span className="text-[9px] text-text-muted mt-1.5 block">Files with no dominant contributor context.</span>
            </div>
          </div>
        </div>

        {/* Lower Workspaces Layout */}
        <div className="flex flex-col lg:flex-row gap-6 w-full flex-1">
          {/* Main Visual Matrix & Contributor Shares */}
          <div className="flex-1 flex flex-col gap-6 min-w-0">
            {/* Heatmap Matrix */}
            <div className="card-base flex-1 flex flex-col min-h-[350px]">
              <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Repository Ownership Matrix</h3>
                  <p className="text-[10px] text-text-muted mt-0.5">Colors represent primary owners; opacity maps to ownership share.</p>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-3 overflow-y-auto max-h-[380px] pr-1">
                {files.map((file, i) => {
                  const active = selectedFile?.file_path === file.file_path;
                  const ownerColor = getOwnerColor(file.primary_owner);
                  const shareVal = file.ownership_score ?? 1.0;
                  return (
                    <div
                      key={i}
                      onClick={() => setSelectedFile(file)}
                      style={{ 
                        backgroundColor: `${ownerColor}22`,
                        borderColor: ownerColor,
                        color: ownerColor
                      }}
                      className={`p-3 rounded-lg border cursor-pointer transition-all duration-300 hover:scale-[1.02] flex flex-col justify-between h-20 relative overflow-hidden ${active ? 'ring-2 ring-primary ring-offset-2 ring-offset-[#09090e] border-transparent' : ''}`}
                    >
                      {/* Visual indicator bar on cell left */}
                      <div className="absolute left-0 top-0 bottom-0 w-1" style={{ backgroundColor: ownerColor }} />

                      <div className="text-[10px] font-mono truncate leading-none pl-1 text-on-surface font-semibold" title={file.file_path}>
                        {file.file_path.split('/').pop()}
                      </div>
                      <div className="flex justify-between items-end mt-2 pl-1">
                        <span className="text-[9px] truncate max-w-[80px] font-medium text-text-muted opacity-80" title={file.primary_owner}>
                          {file.primary_owner}
                        </span>
                        <span className="font-extrabold text-[13px] text-on-surface">
                          {Math.round(shareVal * 100)}%
                        </span>
                      </div>
                    </div>
                  );
                })}
                {files.length === 0 && (
                  <div className="col-span-full py-16 text-center text-text-muted text-xs">No files analyzed in repository.</div>
                )}
              </div>
            </div>

            {/* Contributor List / Distribution */}
            <div className="card-base flex-1 flex flex-col min-h-[300px]">
              <div className="border-b border-border-subtle/50 pb-3 mb-4">
                <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Contributor Distribution</h3>
                <p className="text-[10px] text-text-muted mt-0.5">Author shares and repository ownership percentage breakdown.</p>
              </div>

              <div className="space-y-3 overflow-y-auto max-h-[300px] pr-1">
                {contributors.map((c, i) => {
                  const ownerColor = getOwnerColor(c.name);
                  return (
                    <div key={i} className="flex items-center justify-between p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                      <div className="flex items-center gap-3 min-w-0 flex-1 pr-6">
                        {/* Dynamic color circle */}
                        <span className="w-3.5 h-3.5 rounded-full flex-shrink-0" style={{ backgroundColor: ownerColor }} />
                        <span className="text-xs font-bold truncate text-on-surface">{c.name}</span>
                        
                        {/* Bar meter representation */}
                        <div className="hidden sm:block flex-1 h-2 bg-[#12121e] rounded-full overflow-hidden ml-4">
                          <div className="h-full rounded-full" style={{ width: `${c.share * 100}%`, backgroundColor: ownerColor }} />
                        </div>
                      </div>

                      <div className="flex items-center gap-4 text-xs font-semibold flex-shrink-0">
                        <span className="text-text-muted">{c.commit_count} commits</span>
                        <span className="font-extrabold text-on-surface min-w-[40px] text-right">{Math.round(c.share * 100)}% share</span>
                      </div>
                    </div>
                  );
                })}
                {contributors.length === 0 && (
                  <div className="py-12 text-center text-text-muted text-xs">No contributors found in analysis.</div>
                )}
              </div>
            </div>
          </div>

          {/* Drill-down Right Sidebar Panel */}
          <div className="w-full lg:w-[400px] shrink-0">
            <div className="card-base sticky top-24 flex flex-col gap-5">
              <div className="border-b border-border-subtle/50 pb-3 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[20px]">badge</span>
                <div>
                  <h3 className="font-bold text-xs uppercase tracking-wider text-on-surface">Ownership Detail</h3>
                  <p className="text-[10px] text-text-muted">Blame drill-down metrics</p>
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

                  <div className="flex flex-col gap-4">
                    {/* Primary Owner details block */}
                    <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                      <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-1">Dominant Owner</span>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="w-3.5 h-3.5 rounded-full" style={{ backgroundColor: getOwnerColor(selectedFile.primary_owner) }} />
                        <span className="font-bold text-sm text-on-surface">{selectedFile.primary_owner}</span>
                      </div>
                    </div>

                    {/* Ownership share score progress bar */}
                    <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                      <div className="flex justify-between font-semibold mb-1.5">
                        <span>Attribution Percentage</span>
                        <span className="font-bold text-primary">{Math.round((selectedFile.ownership_score ?? 1.0) * 100)}%</span>
                      </div>
                      <div className="h-2 bg-[#12121e] rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full" 
                          style={{ 
                            width: `${(selectedFile.ownership_score ?? 1.0) * 100}%`,
                            backgroundColor: getOwnerColor(selectedFile.primary_owner)
                          }} 
                        />
                      </div>
                    </div>

                    {/* Risk indicator badge */}
                    <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                      <span className="text-[9px] text-text-muted uppercase tracking-widest block mb-1.5">Knowledge Concentration Risk</span>
                      {(() => {
                        const risk = getRiskLabel(selectedFile.ownership_score ?? 1.0);
                        return (
                          <div className={`p-2.5 rounded-md border text-center font-bold text-[11px] ${risk.color}`}>
                            {risk.text}
                          </div>
                        );
                      })()}
                      <p className="text-[9px] text-text-muted leading-relaxed mt-2">
                        Files with high attribution percentages denote knowledge silos. If the developer departs, the file becomes a maintenance vulnerability.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-text-muted text-center py-10">Select a file cell to review Blame drill-down details.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
