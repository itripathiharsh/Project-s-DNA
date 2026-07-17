import { useState, useEffect, useRef } from 'react';
import PageHeader from '../components/PageHeader';
import { getAdvancedArchitecture } from '../services/api';

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
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Active filters by entity kind
  const [kindFilters, setKindFilters] = useState({});
  // Highlighted path (for cycle tracing)
  const [highlightedPath, setHighlightedPath] = useState(null);

  // Viewport zoom & pan state
  const [pan, setPan] = useState({ x: 450, y: 320 });
  const [zoom, setZoom] = useState(0.85);
  const isDraggingViewport = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });

  // Node drag state
  const draggedNodeId = useRef(null);

  // Physics simulation loop
  const simulationRef = useRef(null);
  const stateRef = useRef({ nodes: [], links: [] });

  const fetchGraph = async () => {
    setLoading(true);
    setError(null);
    setHighlightedPath(null);
    try {
      const data = await getAdvancedArchitecture(viewType);
      
      // Keep track of all kinds to build dynamic filter checkboxes
      const kinds = new Set();
      const initializedNodes = (data.nodes || []).map((node) => {
        kinds.add(node.kind);
        return {
          ...node,
          x: (Math.random() - 0.5) * 400,
          y: (Math.random() - 0.5) * 400,
          vx: 0,
          vy: 0,
        };
      });

      // Set initial checkbox states if not set
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

  // Re-fetch when view type changes
  useEffect(() => {
    fetchGraph();
  }, [viewType]);

  // Apply filters to nodes and links
  useEffect(() => {
    if (loading) return;

    const filteredNodes = rawData.nodes.filter(n => {
      // Kind filter
      if (kindFilters[n.kind] === false) return false;
      return true;
    });

    const activeNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredLinks = rawData.links.filter(l => 
      activeNodeIds.has(l.source) && activeNodeIds.has(l.target)
    );

    setNodes(filteredNodes);
    setLinks(filteredLinks);

    stateRef.current = {
      nodes: filteredNodes,
      links: filteredLinks
    };

    // Restart simulation
    if (simulationRef.current) cancelAnimationFrame(simulationRef.current);
    startSimulation();

  }, [rawData, kindFilters]);

  // Physics force directed simulation
  const startSimulation = () => {
    let alpha = 1.0;
    const tick = () => {
      if (alpha < 0.005) {
        return;
      }

      const { nodes: currentNodes, links: currentLinks } = stateRef.current;
      const nodeMap = {};
      currentNodes.forEach(n => { nodeMap[n.id] = n; });

      // 1. Repulsion force between nodes
      for (let i = 0; i < currentNodes.length; i++) {
        const u = currentNodes[i];
        if (u.id === draggedNodeId.current) continue;
        for (let j = i + 1; j < currentNodes.length; j++) {
          const v = currentNodes[j];
          let dx = v.x - u.x;
          let dy = v.y - u.y;
          if (dx === 0) dx = 0.1;
          let dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 1) dist = 1;
          
          let force = (6000 / (dist * dist)) * alpha;
          if (force > 15) force = 15;
          
          let fx = (dx / dist) * force;
          let fy = (dy / dist) * force;
          
          if (u.id !== draggedNodeId.current) {
            u.vx -= fx;
            u.vy -= fy;
          }
          if (v.id !== draggedNodeId.current) {
            v.vx += fx;
            v.vy += fy;
          }
        }
      }

      // 2. Attraction along links
      currentLinks.forEach(link => {
        const source = nodeMap[link.source];
        const target = nodeMap[link.target];
        if (source && target) {
          let dx = target.x - source.x;
          let dy = target.y - source.y;
          if (dx === 0) dx = 0.1;
          let dist = Math.sqrt(dx * dx + dy * dy);
          
          let targetDist = 130;
          let force = (dist - targetDist) * 0.05 * alpha;
          let fx = (dx / dist) * force;
          let fy = (dy / dist) * force;
          
          if (source.id !== draggedNodeId.current) {
            source.vx += fx;
            source.vy += fy;
          }
          if (target.id !== draggedNodeId.current) {
            target.vx -= fx;
            target.vy -= fy;
          }
        }
      });

      // 3. Central gravity and update
      currentNodes.forEach(node => {
        if (node.id === draggedNodeId.current) return;
        
        let dx = 0 - node.x;
        let dy = 0 - node.y;
        node.vx += dx * 0.02 * alpha;
        node.vy += dy * 0.02 * alpha;

        node.x += node.vx;
        node.y += node.vy;

        node.vx *= 0.8;
        node.vy *= 0.8;
      });

      alpha *= 0.98;
      setNodes([...currentNodes]);
      simulationRef.current = requestAnimationFrame(tick);
    };

    simulationRef.current = requestAnimationFrame(tick);
  };

  useEffect(() => {
    return () => {
      if (simulationRef.current) cancelAnimationFrame(simulationRef.current);
    };
  }, []);

  // Viewport interactions
  const handleMouseDown = (e) => {
    if (e.target.tagName === 'svg' || e.target.id === 'viewport-bg') {
      isDraggingViewport.current = true;
      dragStart.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
    }
  };

  const handleMouseMove = (e) => {
    if (isDraggingViewport.current) {
      setPan({
        x: e.clientX - dragStart.current.x,
        y: e.clientY - dragStart.current.y,
      });
    } else if (draggedNodeId.current) {
      // Update dragged node position
      const { nodes: currentNodes } = stateRef.current;
      const node = currentNodes.find(n => n.id === draggedNodeId.current);
      if (node) {
        // Convert screen coordinates back to graph local coordinates
        const rect = e.currentTarget.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        node.x = (mouseX - pan.x) / zoom;
        node.y = (mouseY - pan.y) / zoom;
        node.vx = 0;
        node.vy = 0;
        setNodes([...currentNodes]);
      }
    }
  };

  const handleMouseUp = () => {
    isDraggingViewport.current = false;
    draggedNodeId.current = null;
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    setZoom((prev) => Math.min(Math.max(prev * factor, 0.15), 4));
  };

  const focusOnNode = (node) => {
    setSelectedNode(node);
    setPan({
      x: 450 - node.x * zoom,
      y: 320 - node.y * zoom,
    });
  };

  const handleNodeMouseDown = (e, node) => {
    e.stopPropagation();
    draggedNodeId.current = node.id;
    setSelectedNode(node);
  };

  const toggleKindFilter = (kind) => {
    setKindFilters(prev => ({
      ...prev,
      [kind]: prev[kind] === false ? true : false
    }));
  };

  const searchResults = nodes.filter((n) =>
    n.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (n.file || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getKindColor = (kind) => KIND_COLORS[kind] || KIND_COLORS.default;

  // Determine if a link is part of the highlighted path
  const isLinkHighlighted = (link) => {
    if (!highlightedPath) return false;
    for (let i = 0; i < highlightedPath.length - 1; i++) {
      const src = highlightedPath[i];
      const tgt = highlightedPath[i + 1];
      if (
        (link.source === src && link.target === tgt) ||
        (link.source === tgt && link.target === src)
      ) {
        return true;
      }
    }
    return false;
  };

  // Determine if a node is in the highlighted path
  const isNodeHighlighted = (nodeId) => {
    if (!highlightedPath) return false;
    return highlightedPath.includes(nodeId);
  };

  return (
    <>
      <PageHeader 
        title="Architecture Intelligence" 
        subtitle="Mined codebase coupling, class hierarchies, structural cycles, and violations"
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
          {/* Node Category Filters */}
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

          {/* Violations and Cycles alerts */}
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
        <div className="flex-1 card-base relative flex flex-col overflow-hidden bg-[#0a0a0f] border border-border-subtle">
          {/* Controls Overlay */}
          <div className="absolute top-4 left-4 z-10 flex gap-1.5 bg-surface-container/80 backdrop-blur px-2 py-1.5 rounded-lg border border-border-subtle">
            <button onClick={() => setZoom(prev => Math.min(prev * 1.2, 4))} className="p-1 text-on-surface hover:text-primary transition-colors" title="Zoom In">
              <span className="material-symbols-outlined text-[18px]">zoom_in</span>
            </button>
            <button onClick={() => setZoom(prev => Math.max(prev * 0.8, 0.15))} className="p-1 text-on-surface hover:text-primary transition-colors" title="Zoom Out">
              <span className="material-symbols-outlined text-[18px]">zoom_out</span>
            </button>
            <button onClick={() => { setPan({ x: 450, y: 320 }); setZoom(0.85); }} className="p-1 text-on-surface hover:text-primary transition-colors" title="Reset Camera">
              <span className="material-symbols-outlined text-[18px]">restart_alt</span>
            </button>
            <span className="w-px h-5 bg-border-subtle mx-1" />
            <button onClick={fetchGraph} className="p-1 text-on-surface hover:text-primary transition-colors" title="Re-Layout Simulation">
              <span className="material-symbols-outlined text-[18px]">refresh</span>
            </button>
          </div>

          {/* Search bar autocomplete */}
          <div className="absolute top-4 right-4 z-10 w-64">
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

          {/* Highlight indicator */}
          {highlightedPath && (
            <div className="absolute bottom-4 left-4 z-10 bg-surface-container/90 backdrop-blur border border-signal-rose/30 px-3 py-1.5 rounded-lg flex items-center gap-2">
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
              <span className="text-xs text-on-surface-variant font-medium">Assembling structural relationships...</span>
            </div>
          ) : error ? (
            <div className="flex-1 flex items-center justify-center text-signal-rose font-semibold text-sm">{error}</div>
          ) : (
            <svg
              className="w-full h-full cursor-grab active:cursor-grabbing"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              onWheel={handleWheel}
            >
              <rect id="viewport-bg" width="100%" height="100%" fill="transparent" />
              <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
                {/* 1. Draw Links */}
                {links.map((link, idx) => {
                  const sourceNode = nodes.find((n) => n.id === link.source);
                  const targetNode = nodes.find((n) => n.id === link.target);
                  if (!sourceNode || !targetNode) return null;
                  
                  const isHighlighted = isLinkHighlighted(link);
                  const isSelected = selectedNode?.id === sourceNode.id || selectedNode?.id === targetNode.id;
                  
                  let strokeColor = '#33333e';
                  let strokeWidth = 1;
                  
                  if (isHighlighted) {
                    strokeColor = '#F43F5E'; // Red
                    strokeWidth = 2.5;
                  } else if (isSelected) {
                    strokeColor = '#9d4edd'; // Purple glow
                    strokeWidth = 1.8;
                  }
                  
                  return (
                    <line
                      key={`link-${idx}`}
                      x1={sourceNode.x}
                      y1={sourceNode.y}
                      x2={targetNode.x}
                      y2={targetNode.y}
                      stroke={strokeColor}
                      strokeWidth={strokeWidth}
                      strokeDasharray={link.kind === 'import' ? '4,4' : '0'}
                      opacity={
                        highlightedPath
                          ? (isHighlighted ? 1.0 : 0.15)
                          : (selectedNode ? (isSelected ? 1.0 : 0.18) : 0.6)
                      }
                    />
                  );
                })}

                {/* 2. Draw Nodes */}
                {nodes.map((node) => {
                  const isSelected = selectedNode?.id === node.id;
                  const isHighlighted = isNodeHighlighted(node.id);
                  const isMatch = searchTerm && node.name.toLowerCase().includes(searchTerm.toLowerCase());
                  const nodeColor = getKindColor(node.kind);
                  
                  let r = isSelected ? 12 : isHighlighted ? 10 : isMatch ? 9 : 7;
                  let strokeColor = 'transparent';
                  let strokeWidth = 0;
                  
                  if (isHighlighted) {
                    strokeColor = '#F43F5E';
                    strokeWidth = 2.5;
                  } else if (isSelected) {
                    strokeColor = '#FFFFFF';
                    strokeWidth = 2;
                  } else if (isMatch) {
                    strokeColor = '#10B981';
                    strokeWidth = 1.5;
                  }

                  return (
                    <g
                      key={node.id}
                      transform={`translate(${node.x}, ${node.y})`}
                      onMouseDown={(e) => handleNodeMouseDown(e, node)}
                      className="cursor-pointer"
                    >
                      <circle
                        r={r}
                        fill={nodeColor}
                        stroke={strokeColor}
                        strokeWidth={strokeWidth}
                        style={{
                          filter: isSelected || isHighlighted 
                            ? `drop-shadow(0 0 8px ${isHighlighted ? '#F43F5E' : nodeColor})` 
                            : 'none'
                        }}
                      />
                      <text
                        y={isSelected ? -16 : -11}
                        textAnchor="middle"
                        fill={isSelected || isHighlighted ? '#FFFFFF' : '#A1A1AA'}
                        fontSize={isSelected || isHighlighted ? '11px' : '9px'}
                        fontWeight={isSelected || isHighlighted ? 'bold' : 'normal'}
                        className="select-none pointer-events-none font-code-sm"
                      >
                        {node.name}
                      </text>
                    </g>
                  );
                })}
              </g>
            </svg>
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
                  {links.filter((l) => l.source === selectedNode.id || l.target === selectedNode.id).map((l, i) => {
                    const isSource = l.source === selectedNode.id;
                    const partnerId = isSource ? l.target : l.source;
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
                  {links.filter((l) => l.source === selectedNode.id || l.target === selectedNode.id).length === 0 && (
                    <span className="text-text-muted text-xs italic text-center block py-4">No coupling relationships identified.</span>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center text-text-muted gap-3 py-16">
              <span className="material-symbols-outlined text-[36px]">touch_app</span>
              <p className="text-xs">Click or search a symbol node in the graph workspace to analyze its dependencies.</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
