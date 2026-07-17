import { useState, useEffect } from 'react';
import { getComplexityHeatmap } from '../services/api';
import PageHeader from '../components/PageHeader';

export default function ComplexityHeatmap() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMetric, setSelectedMetric] = useState('cyclomatic'); // cyclomatic, cognitive, nesting_depth, halstead_effort, loc
  const [activeTab, setActiveTab] = useState('files'); // files, functions
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await getComplexityHeatmap();
        setData(result);
        if (result.files && result.files.length > 0) {
          setSelectedItem({ type: 'file', ...result.files[0] });
        }
      } catch (err) {
        console.error('Error fetching complexity heatmap:', err);
        setError(err.message || 'Failed to fetch complexity metrics.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getMetricValue = (item, metric, type) => {
    if (type === 'file') {
      return item.metrics?.[metric] ?? 0;
    } else {
      if (metric === 'cyclomatic') return item.cyclomatic ?? 0;
      if (metric === 'cognitive') return item.cognitive ?? 0;
      if (metric === 'nesting_depth') return item.nesting_depth ?? 0;
      if (metric === 'halstead_effort') return item.halstead_effort ?? 0;
      if (metric === 'loc') return item.loc ?? 0;
      return 0;
    }
  };

  const getColorClass = (value, metric) => {
    if (metric === 'cyclomatic' || metric === 'cognitive') {
      if (value >= 15) return 'bg-signal-rose border-signal-rose/40 text-white';
      if (value >= 8) return 'bg-signal-amber border-signal-amber/40 text-black';
      if (value >= 4) return 'bg-primary/50 border-primary/40 text-white';
      return 'bg-signal-emerald/20 border-signal-emerald/30 text-signal-emerald';
    }
    if (metric === 'nesting_depth') {
      if (value >= 5) return 'bg-signal-rose border-signal-rose/40 text-white';
      if (value >= 3) return 'bg-signal-amber border-signal-amber/40 text-black';
      if (value >= 2) return 'bg-primary/50 border-primary/40 text-white';
      return 'bg-signal-emerald/20 border-signal-emerald/30 text-signal-emerald';
    }
    if (metric === 'halstead_effort') {
      if (value >= 10000) return 'bg-signal-rose border-signal-rose/40 text-white';
      if (value >= 3000) return 'bg-signal-amber border-signal-amber/40 text-black';
      if (value >= 1000) return 'bg-primary/50 border-primary/40 text-white';
      return 'bg-signal-emerald/20 border-signal-emerald/30 text-signal-emerald';
    }
    // loc
    if (value >= 500) return 'bg-signal-rose border-signal-rose/40 text-white';
    if (value >= 200) return 'bg-signal-amber border-signal-amber/40 text-black';
    if (value >= 50) return 'bg-primary/50 border-primary/40 text-white';
    return 'bg-signal-emerald/20 border-signal-emerald/30 text-signal-emerald';
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-[36px] text-primary animate-spin">sync</span>
          <span className="text-xs text-text-muted">Analyzing AST complexity profiles...</span>
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
  const functions = data?.functions || [];

  const filteredFiles = files.filter(f => 
    f.file_path.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredFunctions = functions.filter(f => 
    f.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    f.file_path.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <PageHeader 
        title="Complexity Heatmap" 
        subtitle="AST-based static code analysis & structural complexity matrix" 
      />
      <div className="p-6 flex flex-col lg:flex-row gap-6 max-w-[1600px] mx-auto w-full flex-1">
        {/* Heatmap Control & Grid Panel */}
        <div className="flex-1 flex flex-col gap-4 min-w-0">
          {/* Controls Bar */}
          <div className="card-base flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-2 bg-[#12121e] border border-border-subtle rounded-lg p-1 w-max">
              <button 
                onClick={() => { setActiveTab('files'); if(files.length) setSelectedItem({ type: 'file', ...files[0] }); }}
                className={`px-3 py-1.5 rounded-md text-[11px] font-bold tracking-wide uppercase transition-all duration-200 ${activeTab === 'files' ? 'bg-primary text-white shadow-md' : 'text-text-muted hover:text-on-surface'}`}
              >
                Files Grid
              </button>
              <button 
                onClick={() => { setActiveTab('functions'); if(functions.length) setSelectedItem({ type: 'function', ...functions[0] }); }}
                className={`px-3 py-1.5 rounded-md text-[11px] font-bold tracking-wide uppercase transition-all duration-200 ${activeTab === 'functions' ? 'bg-primary text-white shadow-md' : 'text-text-muted hover:text-on-surface'}`}
              >
                Functions List
              </button>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {/* Metric Select Dropdown */}
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase font-bold text-text-muted">Target Metric:</span>
                <select 
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value)}
                  className="bg-[#12121e] border border-border-subtle text-xs text-on-surface rounded-lg px-2.5 py-1.5 focus:border-primary focus:outline-none"
                >
                  <option value="cyclomatic">Cyclomatic Complexity</option>
                  <option value="cognitive">Cognitive Complexity</option>
                  <option value="nesting_depth">AST Nesting Depth</option>
                  <option value="halstead_effort">Halstead Effort</option>
                  <option value="loc">Lines of Code (LOC)</option>
                </select>
              </div>

              {/* Search input */}
              <div className="relative">
                <span className="material-symbols-outlined absolute left-2.5 top-1/2 -translate-y-1/2 text-[16px] text-text-muted">search</span>
                <input 
                  type="text"
                  placeholder="Filter name or path..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-[#12121e] border border-border-subtle text-xs text-on-surface rounded-lg pl-8 pr-3 py-1.5 w-[200px] focus:border-primary focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Visual Heatmap Grid */}
          <div className="card-base flex-1 flex flex-col justify-between min-h-[450px]">
            <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center justify-between">
              <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">
                {activeTab === 'files' ? `Repository Files (${filteredFiles.length})` : `Analyzed Functions (${filteredFunctions.length})`}
              </h3>
              <div className="flex items-center gap-4 text-[10px] text-text-muted">
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-signal-emerald/20 border border-signal-emerald/30 inline-block"/> Low</span>
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-primary/50 border border-primary/40 inline-block"/> Mod</span>
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-signal-amber border border-signal-amber/40 inline-block"/> High</span>
                <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-signal-rose border border-signal-rose/40 inline-block"/> Crit</span>
              </div>
            </div>

            {activeTab === 'files' ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-3 overflow-y-auto max-h-[550px] pr-1">
                {filteredFiles.map((file, i) => {
                  const val = getMetricValue(file, selectedMetric, 'file');
                  const active = selectedItem?.type === 'file' && selectedItem?.file_path === file.file_path;
                  return (
                    <div
                      key={i}
                      onClick={() => setSelectedItem({ type: 'file', ...file })}
                      className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:scale-[1.02] flex flex-col justify-between h-20 ${getColorClass(val, selectedMetric)} ${active ? 'ring-2 ring-primary ring-offset-2 ring-offset-[#09090e]' : ''}`}
                    >
                      <div className="text-[10px] font-mono truncate leading-none" title={file.file_path}>
                        {file.file_path.split('/').pop()}
                      </div>
                      <div className="flex justify-between items-end mt-2">
                        <span className="text-[9px] uppercase tracking-widest font-bold opacity-60">
                          {selectedMetric.replace('_', ' ')}
                        </span>
                        <span className="font-extrabold text-sm leading-none">
                          {selectedMetric === 'halstead_effort' ? Math.round(val) : val}
                        </span>
                      </div>
                    </div>
                  );
                })}
                {filteredFiles.length === 0 && (
                  <div className="col-span-full py-16 text-center text-text-muted text-xs">No files matched your filter.</div>
                )}
              </div>
            ) : (
              <div className="space-y-2 overflow-y-auto max-h-[550px] pr-1">
                {filteredFunctions.map((fn, i) => {
                  const val = getMetricValue(fn, selectedMetric, 'function');
                  const active = selectedItem?.type === 'function' && selectedItem?.name === fn.name && selectedItem?.file_path === fn.file_path;
                  return (
                    <div
                      key={i}
                      onClick={() => setSelectedItem({ type: 'function', ...fn })}
                      className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 flex items-center justify-between hover:bg-surface-container-high/20 ${getColorClass(val, selectedMetric)} ${active ? 'ring-2 ring-primary' : ''}`}
                    >
                      <div className="min-w-0 pr-4">
                        <div className="font-semibold text-xs truncate flex items-center gap-1.5">
                          <span className="material-symbols-outlined text-[13px]">code</span>
                          {fn.name}
                        </div>
                        <div className="text-[9px] opacity-75 mt-0.5 truncate">{fn.file_path}:{fn.line}</div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[9px] uppercase font-bold tracking-widest opacity-60">{selectedMetric.replace('_', ' ')}</span>
                        <span className="font-extrabold text-sm">{selectedMetric === 'halstead_effort' ? Math.round(val) : val}</span>
                      </div>
                    </div>
                  );
                })}
                {filteredFunctions.length === 0 && (
                  <div className="py-16 text-center text-text-muted text-xs">No functions matched your filter.</div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Selected Item Detail Panel */}
        <div className="w-full lg:w-[400px] shrink-0">
          <div className="card-base sticky top-24 flex flex-col gap-5">
            <div className="border-b border-border-subtle/50 pb-3 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">
                {selectedItem?.type === 'file' ? 'description' : 'code'}
              </span>
              <div>
                <h3 className="font-bold text-xs uppercase tracking-wider text-on-surface">Drill-Down Metrics</h3>
                <p className="text-[10px] text-text-muted">Granular AST parse summary</p>
              </div>
            </div>

            {selectedItem ? (
              <div className="flex flex-col gap-4 text-xs">
                {/* Title information */}
                <div className="bg-[#12121e] border border-border-subtle rounded-lg p-3">
                  <span className="text-[9px] font-bold text-primary uppercase tracking-widest block mb-1">
                    {selectedItem.type === 'file' ? 'File Path' : 'Function Name'}
                  </span>
                  <div className="font-mono text-xs text-on-surface break-all font-semibold leading-normal">
                    {selectedItem.type === 'file' ? selectedItem.file_path : selectedItem.name}
                  </div>
                  {selectedItem.type === 'function' && (
                    <div className="text-[10px] text-text-muted mt-1 truncate">
                      in: <span className="font-mono text-primary/80">{selectedItem.file_path}:{selectedItem.line}</span>
                    </div>
                  )}
                </div>

                {/* Metrics detail checklist */}
                <div className="flex flex-col gap-3">
                  <span className="text-[9px] font-bold text-text-muted uppercase tracking-widest block">Structural Breakdown</span>
                  
                  {/* Cyclomatic Complexity */}
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                    <div className="flex justify-between font-semibold mb-1.5">
                      <span>Cyclomatic Complexity</span>
                      <span className="text-primary font-bold">
                        {selectedItem.type === 'file' ? selectedItem.metrics?.cyclomatic : selectedItem.cyclomatic}
                      </span>
                    </div>
                    <div className="h-1.5 bg-[#12121e] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary" 
                        style={{ width: `${Math.min(100, ((selectedItem.type === 'file' ? selectedItem.metrics?.cyclomatic : selectedItem.cyclomatic) || 1) * 5)}%` }} 
                      />
                    </div>
                    <p className="text-[9px] text-text-muted leading-relaxed mt-1">
                      Independent logical paths through execution flow. Higher counts require more tests.
                    </p>
                  </div>

                  {/* Cognitive Complexity */}
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                    <div className="flex justify-between font-semibold mb-1.5">
                      <span>Cognitive Complexity</span>
                      <span className="text-signal-amber font-bold">
                        {selectedItem.type === 'file' ? selectedItem.metrics?.cognitive : selectedItem.cognitive}
                      </span>
                    </div>
                    <div className="h-1.5 bg-[#12121e] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-signal-amber" 
                        style={{ width: `${Math.min(100, ((selectedItem.type === 'file' ? selectedItem.metrics?.cognitive : selectedItem.cognitive) || 0) * 5)}%` }} 
                      />
                    </div>
                    <p className="text-[9px] text-text-muted leading-relaxed mt-1">
                      Measures cognitive load & readability based on nested control flows.
                    </p>
                  </div>

                  {/* Nesting Depth */}
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                    <div className="flex justify-between font-semibold mb-1.5">
                      <span>AST Nesting Depth</span>
                      <span className="text-signal-rose font-bold">
                        {selectedItem.type === 'file' ? selectedItem.metrics?.nesting_depth : selectedItem.nesting_depth}
                      </span>
                    </div>
                    <div className="h-1.5 bg-[#12121e] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-signal-rose" 
                        style={{ width: `${Math.min(100, ((selectedItem.type === 'file' ? selectedItem.metrics?.nesting_depth : selectedItem.nesting_depth) || 0) * 15)}%` }} 
                      />
                    </div>
                    <p className="text-[9px] text-text-muted leading-relaxed mt-1">
                      Maximum block/control statement nesting. High nesting is a major code smell.
                    </p>
                  </div>

                  {/* LOC */}
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                    <div className="flex justify-between font-semibold mb-1.5">
                      <span>Lines of Code (LOC)</span>
                      <span className="text-signal-cyan font-bold">
                        {selectedItem.type === 'file' ? selectedItem.metrics?.loc : selectedItem.loc}
                      </span>
                    </div>
                    <div className="h-1.5 bg-[#12121e] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-signal-cyan" 
                        style={{ width: `${Math.min(100, ((selectedItem.type === 'file' ? selectedItem.metrics?.loc : selectedItem.loc) || 0) / 10)}%` }} 
                      />
                    </div>
                    <p className="text-[9px] text-text-muted leading-relaxed mt-1">
                      Physical count of code lines. Large source files violate Single Responsibility.
                    </p>
                  </div>

                  {/* Halstead Effort */}
                  <div className="p-3 bg-surface-container-low/40 border border-border-subtle rounded-lg">
                    <div className="flex justify-between font-semibold mb-1.5">
                      <span>Halstead Effort</span>
                      <span className="text-text-muted font-bold">
                        {Math.round(selectedItem.type === 'file' ? selectedItem.metrics?.halstead_effort : selectedItem.halstead_effort)}
                      </span>
                    </div>
                    <div className="h-1.5 bg-[#12121e] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-[#aaa]" 
                        style={{ width: `${Math.min(100, ((selectedItem.type === 'file' ? selectedItem.metrics?.halstead_effort : selectedItem.halstead_effort) || 0) / 250)}%` }} 
                      />
                    </div>
                    <p className="text-[9px] text-text-muted leading-relaxed mt-1">
                      Software science metric for time and mental effort to build/modify.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-text-muted text-center py-10">Select a cell/block to review metrics drill-down.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
