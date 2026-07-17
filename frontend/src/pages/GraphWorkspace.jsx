import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import PageHeader from '../components/PageHeader';
import { getAdvancedArchitecture } from '../services/api';
import ForceGraph3D from 'react-force-graph-3d';

const KIND_COLORS = {
  class: '#6366F1',      // Indigo
  function: '#10B981',   // Emerald
  method: '#3B82F6',     // Blue
  file: '#F59E0B',       // Amber
  import: '#EC4899',     // Pink
  table: '#14B8A6',      // Teal
  module: '#8B5CF6',      // Violet
  default: '#A1A1AA',    // Zinc
};

export default function GraphWorkspace() {
  const [viewType, setViewType] = useState('dependency'); // dependency, circular, er, hierarchy, imports
  const [rawData, setRawData] = useState({ nodes: [], links: [], violations: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Active filters by entity kind
  const [kindFilters, setKindFilters] = useState({});
  // Highlighted path (for cycle tracing)
  const [highlightedPath, setHighlightedPath] = useState(null);

  const containerRef = useRef();
  const fgRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    if (!containerRef.current) return;
    const updateDim = () => {
      setDimensions({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight
      });
    };
    updateDim();
    const observer = new ResizeObserver(updateDim);
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const fetchGraph = async () => {
    setLoading(true);
    setError(null);
    setHighlightedPath(null);
    try {
      const data = await getAdvancedArchitecture(viewType);
      
      const kinds = new Set();
      const initializedNodes = (data.nodes || []).map((node) => {
        kinds.add(node.kind);
        return {
          ...node,
          // 3D graph adds x, y, z automatically, we don't need to manually init them
        };
      });

      const filters = {};
      kinds.forEach(k => {
        filters[k] = true;
      });
      setKindFilters(prev => ({ ...filters, ...prev }));

      setRawData({
        nodes: initializedNodes,
        links: data.links || [],
        violations: data.violations || []
      });

      if (initializedNodes.length > 0) {
        setSelectedNode(initializedNodes[0]);
      }
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, [viewType]);

  // Removed the custom d3Force override that caused NaN physics crash

  const toggleKindFilter = (kind) => {
    setKindFilters(prev => ({
      ...prev,
      [kind]: prev[kind] === false ? true : false
    }));
  };

  const getKindColor = (kind) => KIND_COLORS[kind] || KIND_COLORS.default;

  // Compute filtered graph data
  const { nodes, links } = useMemo(() => {
    const filteredNodes = rawData.nodes.filter(n => kindFilters[n.kind] !== false);
    const activeNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredLinks = rawData.links.filter(l => 
      activeNodeIds.has(l.source?.id || l.source) && activeNodeIds.has(l.target?.id || l.target)
    );
    return { nodes: filteredNodes, links: filteredLinks };
  }, [rawData, kindFilters]);

  const searchResults = nodes.filter((n) =>
    n.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (n.file || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const isLinkHighlighted = useCallback((link) => {
    if (!highlightedPath) return false;
    const sourceId = link.source?.id || link.source;
    const targetId = link.target?.id || link.target;
    for (let i = 0; i < highlightedPath.length - 1; i++) {
      const src = highlightedPath[i];
      const tgt = highlightedPath[i + 1];
      if (
        (sourceId === src && targetId === tgt) ||
        (sourceId === tgt && targetId === src)
      ) {
        return true;
      }
    }
    return false;
  }, [highlightedPath]);

  const isNodeHighlighted = useCallback((nodeId) => {
    if (!highlightedPath) return false;
    return highlightedPath.includes(nodeId);
  }, [highlightedPath]);

  const focusOnNode = (node) => {
    setSelectedNode(node);
    if (fgRef.current && node) {
      // Aim at node from outside it
      const distance = 40;
      const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
      fgRef.current.cameraPosition(
        { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
        node, // lookAt ({ x, y, z })
        3000  // ms transition duration
      );
    }
  };

  return (
    <>
      <PageHeader 
        title="Architecture Intelligence 3D" 
        subtitle="Mined codebase coupling, class hierarchies, structural cycles, and violations rendered as a 3D globe"
        actions={
          <div className="flex gap-1.5 bg-surface-container p-1 rounded-lg border border-border-subtle">
            {[
              { id: 'dependency', label: 'All Code Graph', icon: 'account_tree' },
              { id: 'circular', label: 'Circular Cycles', icon: 'sync_problem' },
              { id: 'er', label: 'Database Models (ER)', icon: 'database' },
              { id: 'hierarchy', label: 'Inheritance Tree', icon: 'schema' },
              { id: 'imports', label: 'Imports Map', icon: 'input' }
            ].map((v) => (
              <button
                key={v.id}
                onClick={() => setViewType(v.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-semibold transition-all ${
                  viewType === v.id 
                    ? 'bg-primary text-on-primary shadow-md' 
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
                }`}
              >
                <span className="material-symbols-outlined text-[15px]">{v.icon}</span>
                {v.label}
              </button>
            ))}
          </div>
        }
      />

      <div className="p-6 flex-1 flex gap-6 overflow-hidden max-h-[calc(100vh-140px)]">
        {/* Left Side: Filter checkmarks & violations list */}
        <div className="w-80 flex flex-col gap-5 overflow-y-auto">
          <div className="card-base p-4 flex flex-col gap-3">
            <h3 className="font-label-caps text-label-caps text-text-muted border-b border-border-subtle pb-2 flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px] text-primary">filter_list</span> Filter Symbols
            </h3>
            <div className="flex flex-col gap-2">
              {Object.keys(kindFilters).map((kind) => (
                <label 
                  key={kind} 
                  className="flex items-center justify-between text-xs font-medium text-on-surface cursor-pointer hover:bg-surface-container/40 p-1.5 rounded transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span 
                      className="w-2.5 h-2.5 rounded-full" 
                      style={{ backgroundColor: getKindColor(kind) }} 
                    />
                    <span className="capitalize">{kind}s</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={kindFilters[kind] !== false}
                    onChange={() => toggleKindFilter(kind)}
                    className="accent-primary w-4 h-4 cursor-pointer"
                  />
                </label>
              ))}
              {Object.keys(kindFilters).length === 0 && (
                <span className="text-text-muted text-xs text-center py-4">No categories found in this view.</span>
              )}
            </div>
          </div>

          <div className="card-base p-4 flex-1 flex flex-col gap-3 overflow-hidden">
            <h3 className="font-label-caps text-label-caps text-text-muted border-b border-border-subtle pb-2 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px] text-signal-rose">warning</span> 
                Violations Checklist
              </span>
              <span className="badge badge-info">{rawData.violations.length}</span>
            </h3>
            <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
              {rawData.violations.map((v, i) => (
                <div 
                  key={i}
                  onClick={() => v.path && setHighlightedPath(v.path)}
                  className={`p-3 rounded border text-left cursor-pointer transition-all ${
                    highlightedPath === v.path
                      ? 'bg-signal-rose/10 border-signal-rose shadow-md shadow-signal-rose/5' 
                      : 'bg-surface-container border-border-subtle hover:border-outline/40'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className={`w-1.5 h-1.5 rounded-full ${v.severity === 'critical' ? 'bg-signal-rose' : 'bg-signal-amber'}`} />
                    <span className="font-bold text-[10px] uppercase tracking-wider text-text-muted">
                      {v.type.replace(/_/g, ' ')}
                    </span>
                    <span className={`ml-auto badge ${v.severity === 'critical' ? 'badge-high' : 'badge-warn'}`}>
                      {v.severity}
                    </span>
                  </div>
                  <p className="text-xs text-on-surface leading-normal">{v.description}</p>
                  {v.path && (
                    <div className="mt-2 text-[10px] text-primary flex items-center gap-1 font-semibold">
                      <span className="material-symbols-outlined text-[12px]">gesture</span>
                      Click to highlight circular path
                    </div>
                  )}
                </div>
              ))}
              {rawData.violations.length === 0 && (
                <div className="flex-1 flex flex-col items-center justify-center text-center gap-3 py-16 text-text-muted">
                  <span className="material-symbols-outlined text-[32px] text-signal-emerald">gpp_good</span>
                  <span className="text-xs">No layer violations or circular reference cycles found in this workspace view.</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Center main graph area */}
        <div ref={containerRef} className="flex-1 card-base relative flex flex-col overflow-hidden bg-[#0a0a0f] border border-border-subtle rounded-xl">
          
          <div className="absolute top-4 left-4 z-10 flex gap-1.5 bg-surface-container/80 backdrop-blur px-2 py-1.5 rounded-lg border border-border-subtle shadow-xl">
            <button onClick={() => { if(fgRef.current) fgRef.current.zoomToFit(600, 50); }} className="p-1 text-on-surface hover:text-primary transition-colors flex items-center gap-1" title="Reset Camera">
              <span className="material-symbols-outlined text-[18px]">center_focus_strong</span>
              <span className="text-[10px] font-bold uppercase tracking-widest hidden lg:block">Center</span>
            </button>
          </div>

          <div className="absolute top-4 right-4 z-10 w-64 shadow-xl">
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-2.5 text-on-surface-variant text-[15px]">search</span>
              <input
                type="text"
                placeholder="Search symbol..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-base pl-9 pr-3 py-1.5 text-xs bg-surface-container/90 backdrop-blur"
              />
            </div>
            {searchTerm && (
              <div className="absolute top-full left-0 right-0 mt-1 max-h-48 overflow-y-auto bg-surface-container border border-border-subtle rounded shadow-2xl z-20">
                {searchResults.slice(0, 5).map((node) => (
                  <div
                    key={node.id}
                    onClick={() => { focusOnNode(node); setSearchTerm(''); }}
                    className="p-2 text-xs hover:bg-surface-container-high cursor-pointer flex items-center justify-between"
                  >
                    <span className="truncate text-on-surface font-semibold">{node.name}</span>
                    <span className="badge badge-info text-[9px]">{node.kind}</span>
                  </div>
                ))}
                {searchResults.length === 0 && (
                  <div className="p-2.5 text-xs text-text-muted text-center">No symbols found.</div>
                )}
              </div>
            )}
          </div>

          {highlightedPath && (
            <div className="absolute bottom-4 left-4 z-10 bg-surface-container/90 backdrop-blur border border-signal-rose/30 px-3 py-1.5 rounded-lg flex items-center gap-2 shadow-2xl">
              <span className="w-2 h-2 rounded-full bg-signal-rose animate-ping" />
              <span className="text-[10px] text-on-surface font-bold tracking-tight">CYCLE TRACE PATH ACTIVE</span>
              <button 
                onClick={() => setHighlightedPath(null)}
                className="text-[9px] text-text-muted hover:text-signal-rose uppercase font-bold ml-2 transition-colors"
              >
                Clear
              </button>
            </div>
          )}

          {loading ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-3">
              <div className="w-12 h-12 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
              <span className="text-xs text-on-surface-variant font-medium">Rendering 3D Space...</span>
            </div>
          ) : error ? (
            <div className="flex-1 flex items-center justify-center text-signal-rose font-semibold text-sm">{error}</div>
          ) : (
            <ForceGraph3D
              ref={fgRef}
              width={dimensions.width}
              height={dimensions.height}
              graphData={{ nodes, links }}
              nodeLabel="name"
              nodeColor={node => {
                if (isNodeHighlighted(node.id)) return '#F43F5E';
                if (selectedNode?.id === node.id) return '#FFFFFF';
                return getKindColor(node.kind);
              }}
              nodeVal={node => (selectedNode?.id === node.id || isNodeHighlighted(node.id)) ? 15 : 8}
              nodeOpacity={0.9}
              nodeResolution={16}
              linkColor={link => isLinkHighlighted(link) ? '#F43F5E' : (selectedNode?.id === link.source?.id || selectedNode?.id === link.target?.id) ? '#9d4edd' : '#33333e'}
              linkWidth={link => isLinkHighlighted(link) ? 3 : (selectedNode?.id === link.source?.id || selectedNode?.id === link.target?.id) ? 2 : 1.5}
              linkOpacity={0.6}
              linkDirectionalParticles={link => isLinkHighlighted(link) ? 4 : 0}
              linkDirectionalParticleWidth={4}
              onNodeClick={focusOnNode}
              backgroundColor="#0a0a0f"
              enableNodeDrag={false}
            />
          )}
        </div>

        {/* Right Side: Symbol Details panel */}
        <div className="w-80 card-base flex flex-col gap-4 overflow-y-auto">
          <h3 className="font-label-caps text-label-caps text-text-muted border-b border-border-subtle pb-2 flex items-center gap-1.5">
            <span className="material-symbols-outlined text-[16px] text-primary">analytics</span> Node Analysis
          </h3>
          
          {selectedNode ? (
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-on-surface truncate">{selectedNode.name}</span>
                <span 
                  className="badge" 
                  style={{ backgroundColor: `${getKindColor(selectedNode.kind)}15`, color: getKindColor(selectedNode.kind) }}
                >
                  {selectedNode.kind}
                </span>
              </div>

              <div className="flex flex-col gap-2.5">
                <div className="bg-surface-container p-2.5 border border-border-subtle rounded text-left">
                  <span className="block text-[9px] text-text-muted font-bold uppercase tracking-wider mb-0.5">UID</span>
                  <span className="font-code-sm text-xs text-on-surface truncate block">{selectedNode.id}</span>
                </div>
                <div className="bg-surface-container p-2.5 border border-border-subtle rounded text-left">
                  <span className="block text-[9px] text-text-muted font-bold uppercase tracking-wider mb-0.5">File Path</span>
                  <span className="font-code-sm text-xs text-on-surface break-all block">{selectedNode.file || 'N/A'}</span>
                </div>
                {selectedNode.line > 0 && (
                  <div className="bg-surface-container p-2.5 border border-border-subtle rounded text-left">
                    <span className="block text-[9px] text-text-muted font-bold uppercase tracking-wider mb-0.5">Definition Line</span>
                    <span className="font-code-sm text-xs text-on-surface block font-bold">{selectedNode.line}</span>
                  </div>
                )}

                {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                  <div className="bg-surface-container p-2.5 border border-border-subtle rounded flex flex-col gap-1.5 text-left">
                    <span className="block text-[9px] text-text-muted font-bold uppercase tracking-wider">Symbol Properties</span>
                    {Object.entries(selectedNode.properties).map(([k, v]) => (
                      <div key={k} className="flex justify-between items-center text-xs border-b border-border-subtle/30 pb-1 last:border-0 last:pb-0">
                        <span className="text-text-muted font-code-sm">{k}</span>
                        <span className="text-on-surface font-semibold font-code-sm truncate max-w-[150px]">
                          {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Connections listing */}
              <div className="flex flex-col gap-2.5 mt-2">
                <span className="font-label-caps text-[10px] text-text-muted font-bold uppercase tracking-wider border-b border-border-subtle/50 pb-1">
                  Coupling Relations
                </span>
                <div className="space-y-1.5">
                  {links.filter((l) => (l.source?.id || l.source) === selectedNode.id || (l.target?.id || l.target) === selectedNode.id).map((l, i) => {
                    const srcId = l.source?.id || l.source;
                    const tgtId = l.target?.id || l.target;
                    const isSource = srcId === selectedNode.id;
                    const partnerId = isSource ? tgtId : srcId;
                    const partnerNode = nodes.find(n => n.id === partnerId);
                    return (
                      <div
                        key={i}
                        onClick={() => partnerNode && focusOnNode(partnerNode)}
                        className="p-2 rounded bg-surface-container hover:bg-surface-container-high border border-border-subtle hover:border-outline/30 cursor-pointer transition-all flex items-center justify-between text-xs text-left"
                      >
                        <div className="flex items-center gap-2 truncate">
                          <span className="material-symbols-outlined text-[13px] text-text-muted flex-shrink-0">
                            {isSource ? 'arrow_forward' : 'arrow_back'}
                          </span>
                          <span className="text-primary truncate font-semibold font-code-sm">{partnerNode?.name || partnerId.split(':').pop()}</span>
                        </div>
                        <span className="badge badge-info text-[9px] capitalize flex-shrink-0">{l.kind}</span>
                      </div>
                    );
                  })}
                  {links.filter((l) => (l.source?.id || l.source) === selectedNode.id || (l.target?.id || l.target) === selectedNode.id).length === 0 && (
                    <span className="text-text-muted text-xs italic text-center block py-4">No coupling relationships identified.</span>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center text-text-muted gap-3 py-16">
              <span className="material-symbols-outlined text-[36px]">touch_app</span>
              <p className="text-xs">Click or search a symbol node in the 3D graph workspace to analyze its dependencies.</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
