import { useState, useEffect } from 'react';
import { 
  getComplexityHeatmap, 
  getChangeHeatmap, 
  getOwnershipHeatmap, 
  getSecurityHeatmap 
} from '../services/api';

export default function Heatmaps() {
  const [activeSubTab, setActiveSubTab] = useState('complexity');
  
  const [complexityData, setComplexityData] = useState(null);
  const [changeData, setChangeData] = useState(null);
  const [ownershipData, setOwnershipData] = useState(null);
  const [securityData, setSecurityData] = useState(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [selectedCell, setSelectedCell] = useState(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const [comp, chg, own, sec] = await Promise.all([
          getComplexityHeatmap().catch(() => null),
          getChangeHeatmap().catch(() => null),
          getOwnershipHeatmap().catch(() => null),
          getSecurityHeatmap().catch(() => null)
        ]);
        setComplexityData(comp);
        setChangeData(chg);
        setOwnershipData(own);
        setSecurityData(sec);
      } catch (err) {
        setError('Failed to load heatmap data.');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const renderColor = (val, max, colorStart, colorEnd) => {
    // Simple interpolation for tailwind bg opacity or specific classes could be used.
    // For simplicity, we'll return inline styles using an HSL interpolation or just standard classes
    const intensity = Math.min(1, Math.max(0.1, val / (max || 1)));
    return `rgba(${colorEnd}, ${intensity})`;
  };

  const SubTabs = () => (
    <div className="flex border-b border-border-subtle/50 pb-px mb-4">
      {['complexity', 'change', 'ownership', 'security'].map(tab => (
        <button
          key={tab}
          onClick={() => { setActiveSubTab(tab); setSelectedCell(null); }}
          className={`px-4 py-2 text-xs font-bold capitalize transition-all ${
            activeSubTab === tab 
              ? 'border-b-2 border-primary text-primary bg-primary/5' 
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container/20'
          }`}
        >
          {tab} Heatmap
        </button>
      ))}
    </div>
  );

  const CellModal = () => {
    if (!selectedCell) return null;
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#050508]/85 backdrop-blur-sm p-4" onClick={() => setSelectedCell(null)}>
        <div className="card-base max-w-xl w-full bg-[#0d0d12] border border-border-subtle/80 flex flex-col gap-4 p-6 shadow-2xl relative" onClick={e => e.stopPropagation()}>
          <h3 className="font-bold text-base text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[18px]">verified</span>
            {selectedCell.title}
          </h3>
          <div className="text-xs text-on-surface-variant mt-2 whitespace-pre-wrap font-code-sm bg-surface-container p-3 rounded border border-border-subtle">
            {JSON.stringify(selectedCell.details, null, 2)}
          </div>
          <button className="btn-primary mt-4 self-end" onClick={() => setSelectedCell(null)}>Close</button>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
         <div className="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
         <p className="text-xs text-text-muted">Computing heatmaps from real repository analysis...</p>
      </div>
    );
  }

  if (error) {
    return <div className="text-signal-rose text-center p-4 text-xs font-bold">{error}</div>;
  }

  const renderComplexity = () => {
    if (!complexityData || !complexityData.files) return <div className="text-xs text-text-muted">No complexity data available.</div>;
    const files = complexityData.files;
    const maxComp = Math.max(1, ...files.map(f => f.metrics.cyclomatic));
    return (
      <div className="flex flex-col gap-4">
        <p className="text-xs text-text-muted">Tree-sitter AST Cyclomatic & Cognitive Complexity</p>
        <div className="flex flex-wrap gap-2">
          {files.map((f, i) => (
            <div 
              key={i} 
              onClick={() => setSelectedCell({ title: f.file_path, details: f.metrics })}
              className="w-12 h-12 rounded cursor-pointer hover:ring-2 ring-primary transition-all flex items-center justify-center relative group"
              style={{ backgroundColor: renderColor(f.metrics.cyclomatic, maxComp, '0,0,0', '157,78,221') }}
            >
              <div className="hidden group-hover:block absolute bottom-full mb-1 bg-black text-white text-[10px] p-1 rounded z-10 whitespace-nowrap">
                {f.file_path.split('/').pop()}<br/>Comp: {f.metrics.cyclomatic}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderChange = () => {
    if (!changeData || !changeData.file_changes) return <div className="text-xs text-text-muted">No change data available.</div>;
    const files = changeData.file_changes;
    const maxChange = Math.max(1, ...files.map(f => f.change_count));
    return (
      <div className="flex flex-col gap-4">
        <p className="text-xs text-text-muted">Git History Code Churn & Hotspots</p>
        <div className="flex flex-wrap gap-2">
          {files.map((f, i) => (
            <div 
              key={i} 
              onClick={() => setSelectedCell({ title: f.file_path, details: f })}
              className="w-12 h-12 rounded cursor-pointer hover:ring-2 ring-signal-cyan transition-all flex items-center justify-center relative group"
              style={{ backgroundColor: renderColor(f.change_count, maxChange, '0,0,0', '0,187,249') }}
            >
              <div className="hidden group-hover:block absolute bottom-full mb-1 bg-black text-white text-[10px] p-1 rounded z-10 whitespace-nowrap">
                {f.file_path.split('/').pop()}<br/>Changes: {f.change_count}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderOwnership = () => {
    if (!ownershipData || !ownershipData.contributors) return <div className="text-xs text-text-muted">No ownership data available.</div>;
    const contributors = ownershipData.contributors;
    return (
      <div className="flex flex-col gap-4">
        <p className="text-xs text-text-muted">Git Blame Ownership & Bus Factor (Bus Factor: {ownershipData.bus_factor})</p>
        <div className="flex flex-col gap-3">
          {contributors.map((c, i) => (
            <div key={i} className="flex flex-col gap-1.5 p-3 bg-surface-container rounded cursor-pointer hover:border-primary border border-transparent" onClick={() => setSelectedCell({ title: c.name, details: c })}>
               <div className="flex justify-between text-xs font-bold text-on-surface">
                 <span>{c.name}</span>
                 <span>{Math.round(c.share * 100)}%</span>
               </div>
               <div className="w-full h-2 bg-surface-container-high rounded-full overflow-hidden">
                 <div className="h-full bg-primary" style={{ width: `${c.share * 100}%` }} />
               </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderSecurity = () => {
    if (!securityData || !securityData.findings) return <div className="text-xs text-text-muted">No security data available.</div>;
    const findings = securityData.findings;
    if (findings.length === 0) return <div className="text-xs text-signal-emerald">No security risks detected!</div>;
    
    return (
      <div className="flex flex-col gap-4">
        <p className="text-xs text-text-muted">Real Secrets, Dangerous APIs, Vulnerabilities</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {findings.map((f, i) => (
            <div key={i} onClick={() => setSelectedCell({ title: f.finding_type, details: f })} className="p-3 bg-surface-container border border-signal-rose/30 rounded cursor-pointer hover:border-signal-rose transition-all">
              <div className="flex justify-between items-center text-xs font-bold text-on-surface mb-1">
                 <span className="uppercase text-signal-rose flex items-center gap-1"><span className="material-symbols-outlined text-[14px]">warning</span> {f.finding_type}</span>
                 <span className="badge badge-high">{f.severity}</span>
              </div>
              <code className="text-[10px] text-text-muted">{f.file_path}:{f.line}</code>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="card-base p-6 bg-surface-container-low min-h-[400px]">
      <SubTabs />
      {activeSubTab === 'complexity' && renderComplexity()}
      {activeSubTab === 'change' && renderChange()}
      {activeSubTab === 'ownership' && renderOwnership()}
      {activeSubTab === 'security' && renderSecurity()}
      <CellModal />
    </div>
  );
}
