import React, { useState, useEffect, useMemo } from 'react';

export default function ObjectLifetimeVisualization({ data }) {
  const [hoverNode, setHoverNode] = useState(null);
  const [gcCycle, setGcCycle] = useState(0);

  // Group nodes by pseudo-generations
  const generations = useMemo(() => {
    const nodes = data?.nodes || [];
    const eden = [];
    const survivor = [];
    const tenured = [];

    nodes.forEach((n) => {
      // Use metrics or hash to simulate memory placement
      const hashVal = n.id.length + (n.val || 1);
      if (hashVal % 3 === 0) tenured.push(n);
      else if (hashVal % 2 === 0) survivor.push(n);
      else eden.push(n);
    });

    return { eden, survivor, tenured };
  }, [data]);

  // Simulate GC sweeps
  useEffect(() => {
    const interval = setInterval(() => {
      setGcCycle(prev => (prev + 1) % 4);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const renderMemoryBlocks = (nodes, genName, isActiveGC) => (
    <div className={`flex-1 flex flex-col bg-slate-950 rounded-xl overflow-hidden border ${isActiveGC ? 'border-emerald-500/50 shadow-[0_0_30px_rgba(16,185,129,0.2)]' : 'border-emerald-900/30'} transition-all duration-500 relative`}>
      <div className={`p-3 text-xs font-bold uppercase tracking-widest border-b ${isActiveGC ? 'bg-emerald-900/40 text-emerald-300 border-emerald-500/30' : 'bg-slate-900/50 text-slate-500 border-emerald-900/20'}`}>
        <div className="flex justify-between items-center">
          <span className="flex items-center gap-2">
            {isActiveGC && <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>}
            {genName} Space
          </span>
          <span className="font-mono bg-black/50 px-2 py-0.5 rounded">{nodes.length} Objects</span>
        </div>
      </div>
      
      {/* Grid of memory blocks */}
      <div className="flex-1 p-4 overflow-y-auto">
        <div className="flex flex-wrap gap-1.5 content-start">
          {nodes.map((node, i) => {
            const isHovered = hoverNode?.id === node.id;
            // Simulate memory fragmentation and allocations
            const isCollected = isActiveGC && (i % 7 === 0);
            
            let colorClass = 'bg-emerald-800/40 border-emerald-700/50';
            if (isCollected) colorClass = 'bg-red-500/80 border-red-400 shadow-[0_0_10px_#ef4444] animate-pulse';
            else if (isHovered) colorClass = 'bg-emerald-400 border-emerald-300 shadow-[0_0_15px_#34d399] z-10 scale-125';
            else if (isActiveGC) colorClass = 'bg-emerald-600 border-emerald-400';

            return (
              <div
                key={node.id}
                onMouseEnter={() => setHoverNode(node)}
                onMouseLeave={() => setHoverNode(null)}
                className={`w-4 h-4 border rounded-[2px] cursor-pointer transition-all duration-300 ${colorClass}`}
                title={node.name}
              />
            );
          })}
        </div>
      </div>

      {isActiveGC && (
        <div className="absolute inset-0 bg-emerald-500/5 pointer-events-none animate-pulse"></div>
      )}
    </div>
  );

  return (
    <div className="w-full h-full bg-slate-950 flex flex-col relative overflow-hidden font-sans">
      
      {/* Header Stats */}
      <div className="h-20 bg-slate-900/80 border-b border-emerald-900/50 backdrop-blur-xl flex items-center justify-between px-8 z-20 shadow-xl">
        <div className="flex items-center gap-4">
          <span className="material-symbols-outlined text-4xl text-emerald-500">memory</span>
          <div>
            <h2 className="text-xl font-black text-white">Heap Inspector</h2>
            <p className="text-xs text-emerald-500 font-bold uppercase tracking-widest flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Live Memory Tracking
            </p>
          </div>
        </div>
        
        <div className="flex gap-8">
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Total Objects</span>
            <span className="text-xl font-mono text-white font-bold">{data?.nodes?.length || 0}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Allocated Memory</span>
            <span className="text-xl font-mono text-emerald-400 font-bold">{Math.floor((data?.nodes?.length || 0) * 1.4)} MB</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">GC Status</span>
            <span className={`text-xl font-mono font-bold ${gcCycle !== 0 ? 'text-amber-400' : 'text-emerald-500'}`}>
              {gcCycle === 1 ? 'Minor GC (Scavenge)' : gcCycle === 3 ? 'Major GC (Mark-Sweep)' : 'Idle'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid Area */}
      <div className="flex-1 flex gap-6 p-8 bg-[radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-emerald-950/20 via-slate-950 to-black overflow-hidden">
        
        {renderMemoryBlocks(generations.eden, 'Eden', gcCycle === 1)}
        {renderMemoryBlocks(generations.survivor, 'Survivor', gcCycle === 1 || gcCycle === 2)}
        {renderMemoryBlocks(generations.tenured, 'Tenured', gcCycle === 3)}

      </div>

      {/* Hover Panel Overlay */}
      {hoverNode && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 bg-slate-900/95 border border-emerald-500/50 backdrop-blur-xl p-5 rounded-2xl shadow-[0_0_50px_rgba(16,185,129,0.2)] flex items-center gap-6 z-50 animate-in slide-in-from-bottom-5">
          <div className="p-3 bg-emerald-950/50 rounded-xl border border-emerald-500/30">
             <span className="material-symbols-outlined text-emerald-400 text-3xl">data_object</span>
          </div>
          <div>
            <h3 className="text-sm font-bold text-white mb-1 break-all max-w-md">{hoverNode.name}</h3>
            <div className="flex gap-6 mt-2">
              <div>
                <div className="text-[9px] text-emerald-500 uppercase tracking-widest mb-0.5">Size</div>
                <div className="text-xs text-white font-mono">{hoverNode.val || 12} KB</div>
              </div>
              <div>
                <div className="text-[9px] text-emerald-500 uppercase tracking-widest mb-0.5">Generation</div>
                <div className="text-xs text-white font-mono">
                  {generations.tenured.find(n => n.id === hoverNode.id) ? 'Tenured' : generations.survivor.find(n => n.id === hoverNode.id) ? 'Survivor' : 'Eden'}
                </div>
              </div>
              <div>
                <div className="text-[9px] text-emerald-500 uppercase tracking-widest mb-0.5">Retained</div>
                <div className="text-xs text-emerald-400 font-mono font-bold">Yes</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
