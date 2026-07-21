import React, { useState, useEffect, useMemo } from 'react';

export default function DependencyGalaxyVisualization({ data }) {
  const [hoverNode, setHoverNode] = useState(null);
  
  // Categorize nodes by dependency weight (simulating rings)
  const rings = useMemo(() => {
    const nodes = data?.nodes || [];
    const core = [];
    const internal = [];
    const edge = [];
    
    nodes.forEach((n) => {
      const linksCount = (data.links || []).filter(l => l.source === n.id || l.target === n.id).length;
      if (linksCount > 5 || n.group === 1) core.push(n);
      else if (linksCount > 2) internal.push(n);
      else edge.push(n);
    });
    
    return { core, internal, edge };
  }, [data]);

  const mapNodesToOrbit = (nodes, radius) => {
    return nodes.map((n, i) => {
      const angle = (i / nodes.length) * Math.PI * 2;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      return { ...n, x, y, angle };
    });
  };

  const coreNodes = mapNodesToOrbit(rings.core, 60);
  const internalNodes = mapNodesToOrbit(rings.internal, 160);
  const edgeNodes = mapNodesToOrbit(rings.edge, 280);

  const allMappedNodes = [...coreNodes, ...internalNodes, ...edgeNodes];

  return (
    <div className="w-full h-full bg-slate-950 flex relative overflow-hidden font-sans">
      {/* Sidebar Stats */}
      <div className="w-80 bg-slate-900/80 border-r border-sky-900/50 backdrop-blur-xl flex flex-col p-6 z-20">
        <div className="flex items-center gap-3 mb-8">
          <span className="material-symbols-outlined text-4xl text-sky-400">radar</span>
          <div>
            <h2 className="text-xl font-black text-white">Dependency Sonar</h2>
            <p className="text-xs text-sky-400 font-bold uppercase tracking-widest">Active Scan</p>
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="bg-slate-950/50 p-4 rounded-xl border border-sky-500/20 shadow-[0_0_20px_rgba(14,165,233,0.1)]">
            <h3 className="text-[10px] text-slate-400 uppercase tracking-widest mb-4">Sector Density</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-sky-200 font-semibold">Core (Ring 0)</span>
                  <span className="text-white font-mono">{rings.core.length}</span>
                </div>
                <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-sky-400 rounded-full" style={{ width: `${(rings.core.length / Math.max(1, allMappedNodes.length)) * 100}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-blue-200 font-semibold">Internal (Ring 1)</span>
                  <span className="text-white font-mono">{rings.internal.length}</span>
                </div>
                <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(rings.internal.length / Math.max(1, allMappedNodes.length)) * 100}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-indigo-200 font-semibold">Edge (Ring 2)</span>
                  <span className="text-white font-mono">{rings.edge.length}</span>
                </div>
                <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${(rings.edge.length / Math.max(1, allMappedNodes.length)) * 100}%` }}></div>
                </div>
              </div>
            </div>
          </div>

          {hoverNode && (
            <div className="bg-sky-950/40 p-4 rounded-xl border border-sky-400/40 shadow-[0_0_30px_rgba(14,165,233,0.2)] animate-in fade-in zoom-in-95 duration-200">
              <h3 className="text-[10px] text-sky-400 uppercase tracking-widest mb-2 flex items-center gap-1">
                <span className="material-symbols-outlined text-[12px] animate-ping">my_location</span>
                Target Acquired
              </h3>
              <div className="text-sm font-bold text-white break-all mb-3 pb-3 border-b border-sky-500/20">{hoverNode.name}</div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Classification</span>
                  <span className="text-sky-300 font-mono font-bold">Module</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Sector</span>
                  <span className="text-sky-300 font-mono font-bold">
                    {rings.core.find(n => n.id === hoverNode.id) ? 'Core' : rings.internal.find(n => n.id === hoverNode.id) ? 'Internal' : 'Edge'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Radar Canvas */}
      <div className="flex-1 flex items-center justify-center relative bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black">
        
        {/* Radar Rings Grid */}
        <div className="absolute inset-0 flex items-center justify-center opacity-40 pointer-events-none">
          <div className="w-[120px] h-[120px] rounded-full border border-sky-400/60 absolute shadow-[0_0_15px_rgba(56,189,248,0.2)_inset]"></div>
          <div className="w-[320px] h-[320px] rounded-full border border-sky-500/40 absolute border-dashed shadow-[0_0_20px_rgba(56,189,248,0.1)_inset]"></div>
          <div className="w-[560px] h-[560px] rounded-full border border-sky-600/30 absolute"></div>
          {/* Crosshairs */}
          <div className="w-full h-px bg-sky-500/20 absolute"></div>
          <div className="h-full w-px bg-sky-500/20 absolute"></div>
        </div>

        {/* Sweeping Scanner */}
        <div className="absolute w-[560px] h-[560px] rounded-full pointer-events-none origin-center animate-spin" style={{ animationDuration: '4s', animationTimingFunction: 'linear' }}>
          <div className="absolute top-0 right-1/2 w-1/2 h-1/2 rounded-tl-full bg-[conic-gradient(from_270deg_at_bottom_right,_transparent_0deg,_rgba(56,189,248,0.5)_90deg)]"></div>
          <div className="absolute top-0 right-1/2 w-px h-1/2 bg-sky-300 shadow-[0_0_15px_#7dd3fc]"></div>
        </div>

        {/* Nodes */}
        <div className="relative w-[560px] h-[560px]">
          {allMappedNodes.map((node) => {
            const isHovered = hoverNode?.id === node.id;
            const isCore = rings.core.find(n => n.id === node.id);
            const isInternal = rings.internal.find(n => n.id === node.id);
            
            let colorClass = 'bg-indigo-400 shadow-[0_0_10px_#818cf8]';
            if (isCore) colorClass = 'bg-sky-300 shadow-[0_0_15px_#7dd3fc]';
            if (isInternal) colorClass = 'bg-blue-400 shadow-[0_0_10px_#60a5fa]';

            return (
              <div 
                key={node.id}
                className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-crosshair group z-10"
                style={{ 
                  left: `${280 + node.x}px`, 
                  top: `${280 + node.y}px` 
                }}
                onMouseEnter={() => setHoverNode(node)}
                onMouseLeave={() => setHoverNode(null)}
              >
                <div className={`${isCore ? 'w-4 h-4' : 'w-2 h-2'} rounded-full ${colorClass} ${isHovered ? 'scale-150 bg-white shadow-[0_0_20px_#fff]' : 'transition-transform duration-300'}`}></div>
                
                {isHovered && (
                  <div className="absolute left-6 top-1/2 -translate-y-1/2 bg-sky-950/90 border border-sky-500/50 text-white text-[10px] px-2 py-1 rounded backdrop-blur whitespace-nowrap z-50 pointer-events-none">
                    {node.name}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
