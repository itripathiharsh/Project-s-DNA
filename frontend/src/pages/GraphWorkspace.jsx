import { useState, useEffect, useRef } from 'react';
import PageHeader from '../components/PageHeader';
import { getDependencyGraph } from '../services/api';

export default function GraphWorkspace() {
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Viewport zoom & pan state
  const [pan, setPan] = useState({ x: 400, y: 300 });
  const [zoom, setZoom] = useState(0.8);
  const isDragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });

  // Refs for the simulation loop
  const simulationRef = useRef(null);
  const stateRef = useRef({ nodes: [], links: [] });

  useEffect(() => {
    async function loadGraph() {
      try {
        const data = await getDependencyGraph();
        // Initialize positions randomly
        const initializedNodes = (data.nodes || []).map((node) => ({
          ...node,
          x: (Math.random() - 0.5) * 300,
          y: (Math.random() - 0.5) * 300,
          vx: 0,
          vy: 0,
        }));
        
        setNodes(initializedNodes);
        setLinks(data.links || []);
        
        stateRef.current = {
          nodes: initializedNodes,
          links: data.links || []
        };
        
        if (initializedNodes.length > 0) {
          setSelectedNode(initializedNodes[0]);
        }
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    loadGraph();

    return () => {
      if (simulationRef.current) cancelAnimationFrame(simulationRef.current);
    };
  }, []);

  // Run the force-directed simulation with cooling alpha
  useEffect(() => {
    if (loading || stateRef.current.nodes.length === 0) return;

    let alpha = 1.0;
    const runTick = () => {
      if (alpha < 0.02) {
        if (simulationRef.current) cancelAnimationFrame(simulationRef.current);
        return;
      }

      const { nodes: currentNodes, links: currentLinks } = stateRef.current;
      const nodeMap = {};
      currentNodes.forEach(n => { nodeMap[n.id] = n; });

      // 1. Repulsion between all node pairs
      for (let i = 0; i < currentNodes.length; i++) {
        for (let j = i + 1; j < currentNodes.length; j++) {
          let dx = currentNodes[j].x - currentNodes[i].x;
          let dy = currentNodes[j].y - currentNodes[i].y;
          if (dx === 0) dx = 0.1;
          let dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 1) dist = 1;
          
          // Repulsion force
          let force = (4000 / (dist * dist)) * alpha;
          if (force > 8) force = 8;
          
          let fx = (dx / dist) * force;
          let fy = (dy / dist) * force;
          currentNodes[i].vx -= fx;
          currentNodes[i].vy -= fy;
          currentNodes[j].vx += fx;
          currentNodes[j].vy += fy;
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
          
          // Spring force: rest length 120
          let force = (dist - 120) * 0.04 * alpha;
          let fx = (dx / dist) * force;
          let fy = (dy / dist) * force;
          
          source.vx += fx;
          source.vy += fy;
          target.vx -= fx;
          target.vy -= fy;
        }
      });

      // 3. Gravity towards center and apply velocities
      currentNodes.forEach(node => {
        let dx = 0 - node.x;
        let dy = 0 - node.y;
        node.vx += dx * 0.015 * alpha;
        node.vy += dy * 0.015 * alpha;

        node.x += node.vx;
        node.y += node.vy;

        // Friction
        node.vx *= 0.82;
        node.vy *= 0.82;
      });

      // Cool down the physics simulation
      alpha *= 0.97;

      // Force React state update
      setNodes([...currentNodes]);
      simulationRef.current = requestAnimationFrame(runTick);
    };

    simulationRef.current = requestAnimationFrame(runTick);

    return () => {
      if (simulationRef.current) cancelAnimationFrame(simulationRef.current);
    };
  }, [loading]);

  // Pan and Zoom actions
  const handleMouseDown = (e) => {
    if (e.target.tagName === 'svg' || e.target.tagName === 'g') {
      isDragging.current = true;
      dragStart.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging.current) {
      setPan({
        x: e.clientX - dragStart.current.x,
        y: e.clientY - dragStart.current.y,
      });
    }
  };

  const handleMouseUp = () => {
    isDragging.current = false;
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    setZoom((prev) => Math.min(Math.max(prev * factor, 0.2), 3));
  };

  const handleZoomIn = () => setZoom((prev) => Math.min(prev * 1.2, 3));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev * 0.8, 0.2));
  const handleReset = () => {
    setPan({ x: 400, y: 300 });
    setZoom(0.8);
  };

  // Node Selection & Highlight Search
  const handleNodeClick = (node) => {
    setSelectedNode(node);
  };

  const focusOnNode = (node) => {
    setSelectedNode(node);
    setPan({
      x: 400 - node.x * zoom,
      y: 300 - node.y * zoom,
    });
  };

  const filteredNodes = nodes.filter((n) =>
    n.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (n.file || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getKindColor = (kind) => {
    switch (kind) {
      case 'class': return '#6366F1';     // Indigo
      case 'function': return '#10B981';  // Emerald
      case 'method': return '#3B82F6';    // Blue
      case 'file': return '#F59E0B';      // Amber
      default: return '#8B5CF6';          // Purple
    }
  };

  return (
    <>
      <PageHeader title="Graph Workspace" subtitle="Explore module coupling, imports, and AST inheritance cycles" />
      <div className="p-6 flex-1 flex gap-6 overflow-hidden max-h-[calc(100vh-140px)]">
        {/* Left main graph area */}
        <div className="flex-1 card-base relative flex flex-col overflow-hidden bg-[#0d0d0d] select-none">
          {/* Controls Overlay */}
          <div className="absolute top-4 left-4 z-10 flex gap-2">
            <button onClick={handleZoomIn} className="btn-secondary px-3 py-1.5 rounded" title="Zoom In">
              <span className="material-symbols-outlined">zoom_in</span>
            </button>
            <button onClick={handleZoomOut} className="btn-secondary px-3 py-1.5 rounded" title="Zoom Out">
              <span className="material-symbols-outlined">zoom_out</span>
            </button>
            <button onClick={handleReset} className="btn-secondary px-3 py-1.5 rounded" title="Reset Camera">
              <span className="material-symbols-outlined">restart_alt</span>
            </button>
          </div>

          <div className="absolute top-4 right-4 z-10 w-64">
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-2 text-on-surface-variant text-[16px]">search</span>
              <input
                type="text"
                placeholder="Search nodes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-base pl-9 pr-3 py-1 text-sm bg-surface-container-high/90"
              />
            </div>
            {searchTerm && (
              <div className="absolute top-full left-0 right-0 mt-1 max-h-48 overflow-y-auto bg-surface-container border border-border-subtle rounded shadow-lg z-20">
                {filteredNodes.slice(0, 5).map((node) => (
                  <div
                    key={node.id}
                    onClick={() => focusOnNode(node)}
                    className="p-2 text-xs hover:bg-surface-container-high cursor-pointer flex items-center justify-between"
                  >
                    <span className="truncate text-on-surface font-bold">{node.name}</span>
                    <span className="badge badge-info text-[9px]">{node.kind}</span>
                  </div>
                ))}
                {filteredNodes.length === 0 && (
                  <div className="p-2 text-xs text-text-muted text-center">No nodes match search</div>
                )}
              </div>
            )}
          </div>

          {loading ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-2">
              <div className="w-12 h-12 border-4 border-surface-container-high border-t-primary rounded-full animate-spin" />
              <span className="text-on-surface-variant">Laying out dependency graph...</span>
            </div>
          ) : error ? (
            <div className="flex-1 flex items-center justify-center text-signal-rose font-body-sm">{error}</div>
          ) : (
            <svg
              className="w-full h-full cursor-grab active:cursor-grabbing"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              onWheel={handleWheel}
            >
              <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
                {/* 1. Connections / Links */}
                {links.map((link, idx) => {
                  const sourceNode = nodes.find((n) => n.id === link.source);
                  const targetNode = nodes.find((n) => n.id === link.target);
                  if (!sourceNode || !targetNode) return null;
                  return (
                    <line
                      key={`link-${idx}`}
                      x1={sourceNode.x}
                      y1={sourceNode.y}
                      x2={targetNode.x}
                      y2={targetNode.y}
                      stroke="#333"
                      strokeWidth={selectedNode?.id === sourceNode.id || selectedNode?.id === targetNode.id ? 2 : 1}
                      strokeDasharray={link.kind === 'import' ? '5,5' : '0'}
                      opacity={selectedNode ? (selectedNode.id === sourceNode.id || selectedNode.id === targetNode.id ? 0.9 : 0.2) : 0.5}
                    />
                  );
                })}

                {/* 2. Nodes */}
                {nodes.map((node) => {
                  const isSelected = selectedNode?.id === node.id;
                  const isMatch = searchTerm && node.name.toLowerCase().includes(searchTerm.toLowerCase());
                  const nodeColor = getKindColor(node.kind);
                  return (
                    <g
                      key={node.id}
                      transform={`translate(${node.x}, ${node.y})`}
                      onClick={() => handleNodeClick(node)}
                      className="cursor-pointer"
                    >
                      <circle
                        r={isSelected ? 10 : isMatch ? 8 : 6}
                        fill={nodeColor}
                        stroke={isSelected ? '#fff' : isMatch ? '#10B981' : 'transparent'}
                        strokeWidth={2}
                      />
                      <text
                        y={isSelected ? -14 : -10}
                        textAnchor="middle"
                        fill={isSelected ? '#fff' : '#888'}
                        fontSize={isSelected ? '12px' : '9px'}
                        fontWeight={isSelected ? 'bold' : 'normal'}
                        className="select-none pointer-events-none"
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

        {/* Right side Details Panel */}
        <div className="w-80 card-base flex flex-col gap-4 overflow-y-auto">
          <h3 className="font-headline-md text-headline-md border-b border-border-subtle pb-2 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">info</span> Node Details
          </h3>
          {selectedNode ? (
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <span className="font-headline-lg text-headline-lg text-on-surface truncate">{selectedNode.name}</span>
                <span className="badge badge-info" style={{ backgroundColor: `${getKindColor(selectedNode.kind)}25`, color: getKindColor(selectedNode.kind) }}>
                  {selectedNode.kind}
                </span>
              </div>
              <div className="flex flex-col gap-2">
                <div className="bg-surface-container p-2.5 border border-border-subtle rounded">
                  <span className="block text-[10px] text-text-muted">UID</span>
                  <span className="font-code-sm text-code-sm text-on-surface truncate block">{selectedNode.id}</span>
                </div>
                <div className="bg-surface-container p-2.5 border border-border-subtle rounded">
                  <span className="block text-[10px] text-text-muted">FILE PATH</span>
                  <span className="font-code-sm text-code-sm text-on-surface break-all block">{selectedNode.file || 'N/A'}</span>
                </div>
                {selectedNode.line > 0 && (
                  <div className="bg-surface-container p-2.5 border border-border-subtle rounded">
                    <span className="block text-[10px] text-text-muted">LINE NUMBER</span>
                    <span className="font-code-sm text-code-sm text-on-surface block">{selectedNode.line}</span>
                  </div>
                )}
                {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                  <div className="bg-surface-container p-2.5 border border-border-subtle rounded flex flex-col gap-1.5">
                    <span className="block text-[10px] text-text-muted">PROPERTIES</span>
                    {Object.entries(selectedNode.properties).map(([k, v]) => (
                      <div key={k} className="flex justify-between items-center text-xs">
                        <span className="text-text-muted font-code-sm">{k}</span>
                        <span className="text-on-surface font-bold font-code-sm truncate max-w-[150px]">{JSON.stringify(v)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Connections listing */}
              <div className="flex flex-col gap-2 mt-2">
                <span className="font-label-caps text-label-caps text-text-muted">Connected Relations</span>
                {links.filter((l) => l.source === selectedNode.id || l.target === selectedNode.id).map((l, i) => {
                  const isSource = l.source === selectedNode.id;
                  const partnerId = isSource ? l.target : l.source;
                  const partnerNode = nodes.find(n => n.id === partnerId);
                  return (
                    <div
                      key={i}
                      onClick={() => partnerNode && focusOnNode(partnerNode)}
                      className="p-2 rounded bg-surface-container-high hover:bg-surface-variant/30 border border-border-subtle cursor-pointer transition-colors flex items-center justify-between text-xs"
                    >
                      <div className="flex items-center gap-1.5 truncate">
                        <span className="material-symbols-outlined text-[14px]">
                          {isSource ? 'arrow_forward' : 'arrow_back'}
                        </span>
                        <span className="text-primary truncate font-code-sm">{partnerNode?.name || partnerId}</span>
                      </div>
                      <span className="badge badge-info text-[9px]">{l.kind}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <p className="text-text-muted font-body-sm text-center py-8">Select any node in the workspace graph to see its coupling relationships.</p>
          )}
        </div>
      </div>
    </>
  );
}
