import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import { getFlowJourney } from '../services/api';
import PageHeader from '../components/PageHeader';
import UserJourneyVisualization from '../components/UserJourneyVisualization';
import DatabaseJourneyVisualization from '../components/DatabaseJourneyVisualization';
import EventTimelineVisualization from '../components/EventTimelineVisualization';
import ObjectLifetimeVisualization from '../components/ObjectLifetimeVisualization';
import DependencyGalaxyVisualization from '../components/DependencyGalaxyVisualization';
const JOURNEYS = [
  { key: 'code_understanding', label: 'Code Understanding', icon: 'location_city', desc: 'Cityscape: height=LOC, color=complexity' },
  { key: 'execution_flow', label: 'Execution Flow', icon: 'electric_bolt', desc: 'Tron-style light beams tracing execution' },
  { key: 'data_flow', label: 'Data Flow', icon: 'water_drop', desc: 'Flowing rivers of data transformation' },
  { key: 'variable_flow', label: 'Variable Flow', icon: 'psychology', desc: 'Neural network of variable mutations' },
  { key: 'state_flow', label: 'State Flow', icon: 'schema', desc: 'State machine transitions' },
  { key: 'api_journey', label: 'API Journey', icon: 'flight_takeoff', desc: 'Airport flight paths for requests' },
  { key: 'database_journey', label: 'Database Journey', icon: 'train', desc: 'Metro map of queries' },
  { key: 'event_timeline', label: 'Event Timeline', icon: 'timeline', desc: 'Horizontal chronological events' },
  { key: 'object_lifetime', label: 'Object Lifetime', icon: 'park', desc: 'Growing and dying trees (GC)' },
  { key: 'dependency_galaxy', label: 'Dependency Galaxy', icon: 'public', desc: 'Solar systems of imports' },
  { key: 'runtime_simulation', label: 'Runtime Simulation', icon: 'play_circle', desc: 'Live execution playback' },
  { key: 'repository_dna', label: 'Repository DNA', icon: 'biotech', desc: 'Living genetic helix of the codebase' },
];

export default function FlowJourneys() {
  const [activeTab, setActiveTab] = useState(JOURNEYS[0].key);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [simulationState, setSimulationState] = useState(0);
  
  const fgRef = useRef();
  const containerRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  
  // Cyberpunk City Hover State
  const [hoverNode, setHoverNode] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  
  // Flow Tracking States
  const [activeStateNode, setActiveStateNode] = useState(null);
  const [activeRequestNode, setActiveRequestNode] = useState(null);
  const [activeResponseNode, setActiveResponseNode] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getFlowJourney(activeTab)
      .then(res => {
        setData(res);
        if (res.nodes.length > 0) {
          if (activeTab === 'state_flow') setActiveStateNode(res.nodes[0].id);
          // For linear flows like request/response, try to find a root node or just pick the first
          if (activeTab === 'request_journey') setActiveRequestNode(res.nodes[0].id);
          if (activeTab === 'response_journey') setActiveResponseNode(res.nodes[res.nodes.length-1].id);
        }
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [activeTab]);

  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(entries => {
      if (entries.length > 0) {
        const { width, height } = entries[0].contentRect;
        setDimensions({ width, height });
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  // Animate runtime simulation and execution flow
  useEffect(() => {
    let frame;
    let isActive = true;
    if (['runtime_simulation', 'execution_flow', 'state_flow', 'request_journey', 'response_journey'].includes(activeTab)) {
      const update = () => {
        if (!isActive) return;
        setSimulationState(s => {
          const isFlowingTab = ['state_flow', 'request_journey', 'response_journey'].includes(activeTab);
          const next = (hoverNode && !isFlowingTab) ? s : (s + 1) % 400;
          
          if (next % 60 === 0 && data && data.links) {
            // Advance active nodes for step-by-step simulations
            const transitionNode = (currentActiveId, isReverse = false) => {
              if (!currentActiveId) return null;
              const nextLinks = data.links.filter(l => 
                (isReverse ? (l.target.id || l.target) : (l.source.id || l.source)) === currentActiveId
              );
              if (nextLinks.length > 0) {
                const nextLink = nextLinks[Math.floor(Math.random() * nextLinks.length)];
                return isReverse ? (nextLink.source.id || nextLink.source) : (nextLink.target.id || nextLink.target);
              }
              // If terminal node, restart from root
              return data.nodes.length > 0 ? data.nodes[isReverse ? data.nodes.length-1 : 0].id : null;
            };

            if (activeTab === 'state_flow') setActiveStateNode(prev => transitionNode(prev));
            if (activeTab === 'request_journey') setActiveRequestNode(prev => transitionNode(prev));
            if (activeTab === 'response_journey') setActiveResponseNode(prev => transitionNode(prev, true)); // Responses flow backwards visually
          }
          return next;
        });
        frame = requestAnimationFrame(update);
      };
      frame = requestAnimationFrame(update);
    }
    return () => {
      isActive = false;
      if (frame) cancelAnimationFrame(frame);
    };
  }, [activeTab, hoverNode, data]);

  // Handle post-load camera positioning and graph layouts
  useEffect(() => {
    if (!fgRef.current || !data) return;
    const fg = fgRef.current;
    const scene = fg.scene();
    
    // Reset forces and environment
    fg.d3Force('charge').strength(-150);
    fg.d3Force('link').distance(40);
    scene.fog = null;
    
    if (activeTab === 'repository_dna') {
      const nodes = data.nodes;
      nodes.forEach((node, i) => {
        const angle = i * 0.5;
        const radius = 60;
        const strand = i % 2 === 0 ? 1 : -1;
        node.fx = Math.cos(angle) * radius * strand;
        node.fy = i * 4 - (nodes.length * 2);
        node.fz = Math.sin(angle) * radius * strand;
      });
      fg.cameraPosition({ x: 0, y: 0, z: 400 });
    } else if (activeTab === 'code_understanding') {
      scene.fog = new THREE.FogExp2(0x02020a, 0.002);
      const nodes = data.nodes;
      const gridSize = Math.ceil(Math.sqrt(nodes.length));
      const spacing = 40;
      
      nodes.forEach((node, i) => {
        const row = Math.floor(i / gridSize);
        const col = i % gridSize;
        const groupOffset = (node.group || 1) * 10;
        
        node.fx = (col - gridSize/2) * spacing + groupOffset;
        node.fz = (row - gridSize/2) * spacing + groupOffset;
        node.fy = 0; 
      });
      
      fg.cameraPosition({ x: 200, y: 150, z: 200 }, { x: 0, y: 0, z: 0 });
    } else if (activeTab === 'execution_flow') {
      scene.fog = new THREE.FogExp2(0x020617, 0.001);
      fg.d3Force('charge').strength(-250);
      const nodes = data.nodes;
      nodes.forEach(n => { n.fx = undefined; n.fy = undefined; n.fz = undefined; });
      fg.zoomToFit(400);
    } else if (activeTab === 'data_flow') {
      scene.fog = new THREE.FogExp2(0x000814, 0.001);
      fg.d3Force('charge').strength(-200);
      
      const nodes = data.nodes;
      nodes.forEach((node, i) => {
        // Flat layout to simulate lakes/rivers on a terrain
        if (node.group === 3) node.fy = 0; // Databases stay low
        else if (node.group === 1) node.fy = 40; // APIs sit higher
        else node.fy = 20 + Math.sin(i)*10; // Others roll in between
      });
    } else if (activeTab === 'api_journey') {
      scene.fog = new THREE.FogExp2(0x000000, 0.0015);
      fg.d3Force('charge').strength(-400);
      const nodes = data.nodes;
      nodes.forEach((node) => {
        node.fy = 0; // Flat airline map
      });
      fg.cameraPosition({ x: 0, y: 300, z: 0 }, { x: 0, y: 0, z: 0 });
    } else if (activeTab === 'state_flow') {
      scene.fog = new THREE.FogExp2(0x050011, 0.002);
      fg.d3Force('charge').strength(-600);
      const nodes = data.nodes;
      nodes.forEach(n => { n.fx = undefined; n.fy = undefined; n.fz = undefined; });
      fg.zoomToFit(400);
    } else if (activeTab === 'request_journey') {
      scene.fog = new THREE.FogExp2(0x020617, 0.002);
      fg.d3Force('charge').strength(-400);
      const nodes = data.nodes;
      nodes.forEach((n, i) => {
        n.fx = 0; // Lock to center vertical column
        n.fy = i * -40; // Step down vertically
        n.fz = 0;
      });
      fg.cameraPosition({ x: 0, y: 0, z: 300 }, { x: 0, y: -100, z: 0 });
    } else if (activeTab === 'response_journey') {
      scene.fog = new THREE.FogExp2(0x0a0a0a, 0.001);
      fg.d3Force('charge').strength(-300);
      const nodes = data.nodes;
      nodes.forEach((n, i) => {
        n.fx = i * 60; // Step right horizontally
        n.fy = 0;
        n.fz = 0;
      });
      fg.cameraPosition({ x: 100, y: 0, z: 250 }, { x: 100, y: 0, z: 0 });
    } else if (activeTab === 'database_journey') {
      fg.d3Force('charge').strength(-200);
      const nodes = data.nodes;
      nodes.forEach(n => { n.fx = undefined; n.fy = undefined; n.fz = undefined; });
      fg.zoomToFit(400);
    } else {
      const nodes = data.nodes;
      nodes.forEach(n => { n.fx = undefined; n.fy = undefined; n.fz = undefined; });
      fg.zoomToFit(400);
    }
  }, [data, activeTab]);

  const handleZoom = useCallback((direction) => {
    if (!fgRef.current) return;
    if (direction === 'fit') {
      if (activeTab === 'code_understanding') {
        fgRef.current.cameraPosition({ x: 200, y: 150, z: 200 }, { x: 0, y: 0, z: 0 }, 400);
      } else if (activeTab === 'api_journey') {
        fgRef.current.cameraPosition({ x: 0, y: 300, z: 0 }, { x: 0, y: 0, z: 0 }, 400);
      } else {
        fgRef.current.zoomToFit(400);
      }
      return;
    }
    const pos = fgRef.current.cameraPosition();
    const factor = direction === 'in' ? 0.7 : 1.4;
    fgRef.current.cameraPosition(
      { x: pos.x * factor, y: pos.y * factor, z: pos.z * factor },
      null, // keep looking at current target
      400
    );
  }, [activeTab]);

  // Node visualization generator
  const renderNode = useCallback((node) => {
    const isHovered = hoverNode === node.id;
    
    if (activeTab === 'code_understanding') {
      const height = Math.max(10, (node.val || 1) * 4);
      const geometry = new THREE.BoxGeometry(10, height, 10);
      
      let colorHex = 0x00ffcc; 
      if (node.group === 2) colorHex = 0xffe600; 
      if (node.group >= 3) colorHex = 0xff003c; 
      
      const material = new THREE.MeshStandardMaterial({ 
        color: colorHex, emissive: colorHex, emissiveIntensity: isHovered ? 0.8 : 0.4,
        roughness: 0.2, metalness: 0.8
      });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.y = (height / 2) + (isHovered ? 20 : 0);
      return mesh;
    } 
    else if (activeTab === 'execution_flow') {
      // Tron Circuit Nodes
      const phase = (simulationState * 4 - (node.x || 0)) % 600;
      const isActive = phase > 0 && phase < 80 && !isHovered && !hoverNode;
      
      const geometry = new THREE.TorusGeometry(isHovered ? 7 : 5, 1.5, 16, 32);
      const colorHex = isActive || isHovered ? 0xff00ff : 0x0088cc;
      
      const material = new THREE.MeshStandardMaterial({
        color: colorHex, emissive: colorHex,
        emissiveIntensity: isActive || isHovered ? 1.5 : 0.1,
        roughness: 0.1, metalness: 0.9
      });
      return new THREE.Mesh(geometry, material);
    }
    else if (activeTab === 'data_flow') {
      // Fluid Data Mechanics
      const isHovered = hoverNode === node.id;
      let geo, mat;
      
      if (node.group === 3) {
        // Database = Lake
        geo = new THREE.CylinderGeometry(20, 20, 3, 32);
        mat = new THREE.MeshPhongMaterial({ 
          color: 0x0066ff, emissive: 0x0033ff, emissiveIntensity: 0.8,
          shininess: 100, flatShading: false
        });
      } else if (node.group === 1) {
        // API = Bridge
        geo = new THREE.BoxGeometry(24, 6, 12);
        mat = new THREE.MeshPhongMaterial({ 
          color: 0x94a3b8, emissive: 0x475569, emissiveIntensity: 0.5,
          shininess: 50 
        });
      } else {
        // Services/Caches = Pools/Reservoirs
        geo = new THREE.CylinderGeometry(12, 12, 5, 16);
        mat = new THREE.MeshPhongMaterial({ 
          color: 0x00ccff, emissive: 0x0088ff, emissiveIntensity: 0.7,
          shininess: 100
        });
      }
      
      if (isHovered) {
        mat.emissive.setHex(0x00ffff);
        mat.emissiveIntensity = 2.5;
      }
      
      const mesh = new THREE.Mesh(geo, mat);
      // Keep lakes flat on the plane
      mesh.rotation.x = node.group === 1 ? 0 : Math.PI / 2;
      return mesh;
    }
    else if (activeTab === 'state_flow') {
      // Large State Nodes
      const isActiveState = node.id === activeStateNode;
      const scale = isActiveState ? 1.5 : (isHovered ? 1.2 : 1.0);
      const geo = new THREE.SphereGeometry(12 * scale, 32, 32);
      
      const mat = new THREE.MeshPhongMaterial({
        color: isActiveState ? 0xcc00ff : 0x4c0099,
        emissive: isActiveState ? 0xcc00ff : 0x220044,
        emissiveIntensity: isActiveState ? 1.5 : 0.5,
        shininess: 100
      });
      return new THREE.Mesh(geo, mat);
    }
    else if (activeTab === 'api_journey') {
      // Airport Pins
      const geo = new THREE.CylinderGeometry(isHovered ? 4 : 2, isHovered ? 4 : 2, 2, 16);
      const mat = new THREE.MeshPhongMaterial({
        color: 0xffffff, emissive: 0xffffff,
        emissiveIntensity: isHovered ? 2 : 0.5
      });
      return new THREE.Mesh(geo, mat);
    }
    else if (activeTab === 'request_journey') {
      // Waterfall timeline bars
      const isCurrent = node.id === activeRequestNode;
      // We assume nodes are ordered in the data list to determine past/future
      const nodeIndex = data.nodes.findIndex(n => n.id === node.id);
      const activeIndex = data.nodes.findIndex(n => n.id === activeRequestNode);
      const isPast = nodeIndex < activeIndex;
      
      const geo = new THREE.BoxGeometry(20, 2, 5);
      const mat = new THREE.MeshPhongMaterial({
        color: isCurrent ? 0x00ffff : (isPast ? 0x0ea5e9 : 0x334155),
        emissive: isCurrent ? 0x00ffff : (isPast ? 0x0284c7 : 0x000000),
        emissiveIntensity: isCurrent ? (1.5 + Math.sin(simulationState * 0.2) * 0.5) : (isPast ? 0.4 : 0),
        transparent: true, opacity: isCurrent || isPast ? 1 : 0.4,
        shininess: 100
      });
      return new THREE.Mesh(geo, mat);
    }
    else if (activeTab === 'response_journey') {
      // Payload Bubble Mutations
      const isCurrent = node.id === activeResponseNode;
      const nodeIndex = data.nodes.findIndex(n => n.id === node.id);
      
      // Stage transformations based on depth/index
      // 0: Raw (Large, Blue), 1: Compressed (Small, Blue), 2: Serialized (Small, Purple), 3: Encrypted (Small, Purple, Shell)
      const size = isHovered ? 12 : (nodeIndex > 0 ? 6 : 10);
      const color = nodeIndex > 1 ? 0xcc00ff : 0x00aaff;
      
      const group = new THREE.Group();
      
      const geo = new THREE.SphereGeometry(size, 32, 32);
      const mat = new THREE.MeshPhongMaterial({
        color: color, emissive: color,
        emissiveIntensity: isCurrent ? 1.5 : 0.4,
        transparent: true, opacity: isCurrent ? 1 : 0.5,
        shininess: 100
      });
      group.add(new THREE.Mesh(geo, mat));
      
      if (nodeIndex > 2) {
        // Encrypted shell
        const shellGeo = new THREE.SphereGeometry(size + 2, 16, 16);
        const shellMat = new THREE.MeshBasicMaterial({
          color: 0x00ffcc, wireframe: true, transparent: true, opacity: 0.3
        });
        group.add(new THREE.Mesh(shellGeo, shellMat));
      }
      return group;
    }
    else if (activeTab === 'object_lifetime') {
      const isCurrent = node.id === hoverNode;
      const age = (node.val || 1); // Mock age
      
      const group = new THREE.Group();
      
      // Tree trunk
      const trunkGeo = new THREE.CylinderGeometry(0.5 + age * 0.1, 1 + age * 0.2, 4 + age, 8);
      const trunkMat = new THREE.MeshPhongMaterial({ color: 0x4a3728, emissive: 0x2d1a11 });
      const trunk = new THREE.Mesh(trunkGeo, trunkMat);
      trunk.position.y = (4 + age) / 2;
      group.add(trunk);
      
      // Tree leaves
      const leavesSize = 3 + age * 1.5;
      const leavesGeo = new THREE.DodecahedronGeometry(leavesSize);
      const leavesColor = age > 5 ? 0xccff00 : (age > 2 ? 0x00ffaa : 0x00ff00);
      const leavesMat = new THREE.MeshPhongMaterial({ 
        color: leavesColor, emissive: leavesColor, emissiveIntensity: isCurrent ? 1.5 : 0.4,
        transparent: true, opacity: 0.8, shininess: 100 
      });
      const leaves = new THREE.Mesh(leavesGeo, leavesMat);
      leaves.position.y = (4 + age) + leavesSize * 0.5;
      group.add(leaves);
      
      return group;
    }
    else if (activeTab === 'dependency_galaxy') {
      const isCurrent = node.id === hoverNode;
      const size = Math.max(2, (node.val || 1) * 2); // Central nodes are bigger
      const isStar = node.group === 1 || size > 6;
      
      const group = new THREE.Group();
      
      // Core body (Star or Planet)
      const coreGeo = new THREE.SphereGeometry(size, 32, 32);
      const colorHex = isStar ? 0xffea00 : 0x00d4ff;
      const coreMat = new THREE.MeshPhongMaterial({ 
        color: colorHex, emissive: colorHex, 
        emissiveIntensity: isCurrent ? 2 : (isStar ? 1.5 : 0.4),
        shininess: 100 
      });
      group.add(new THREE.Mesh(coreGeo, coreMat));
      
      // Star Halo / Orbit Ring
      if (isStar) {
        const haloGeo = new THREE.SphereGeometry(size + (isCurrent ? 4 : 2), 32, 32);
        const haloMat = new THREE.MeshBasicMaterial({
          color: 0xffaa00, transparent: true, opacity: 0.15, blending: THREE.AdditiveBlending
        });
        group.add(new THREE.Mesh(haloGeo, haloMat));
      } else if (isCurrent) {
        const ringGeo = new THREE.RingGeometry(size + 2, size + 2.5, 32);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0x00ffff, side: THREE.DoubleSide });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = Math.PI / 2;
        group.add(ring);
      }
      
      return group;
    }
    else if (activeTab === 'repository_dna') {
      const geo = new THREE.SphereGeometry(4, 16, 16);
      const mat = new THREE.MeshStandardMaterial({ 
        color: node.group === 1 ? 0xff0066 : 0x00ffcc,
        emissive: node.group === 1 ? 0xff0066 : 0x00ffcc, emissiveIntensity: 0.5
      });
      return new THREE.Mesh(geo, mat);
    }
    return null; 
  }, [activeTab, hoverNode, simulationState]);

  // Graph styling options based on journey type
  const config = useMemo(() => {
    switch(activeTab) {
      case 'execution_flow': 
        return { 
          linkDirectionalParticles: hoverNode ? 0 : 5, 
          linkDirectionalParticleSpeed: hoverNode ? 0 : 0.02, 
          linkDirectionalParticleWidth: 3.5,
          linkColor: () => '#00e5ff55', linkWidth: 2, bg: '#020617', dag: 'lr' 
        };
      case 'api_journey': 
        return { 
          linkDirectionalParticles: hoverNode ? 0 : 3, 
          linkDirectionalParticleSpeed: hoverNode ? 0 : 0.02, 
          linkDirectionalParticleWidth: 4,
          linkCurvature: 0.3, 
          linkColor: (link) => {
            const val = link.value || 1;
            if (val > 3) return '#ef444499'; // Slow (Red)
            if (val > 1) return '#f59e0b99'; // Medium (Yellow)
            return '#10b98199'; // Fast (Green)
          }, 
          linkWidth: 2,
          bg: '#000000', dag: null 
        };
      case 'state_flow':
        return {
          linkDirectionalArrowLength: 8,
          linkDirectionalArrowRelPos: 1,
          linkDirectionalParticles: 0,
          linkCurvature: (link) => (link.source === link.target || (link.source.id && link.source.id === link.target.id)) ? 1 : 0.2,
          linkColor: (link) => {
            if (link.value === 0) return '#ff0033'; // Invalid flash
            if ((link.source.id || link.source) === activeStateNode) return '#cc00ff';
            return '#555555';
          },
          linkWidth: (link) => ((link.source.id || link.source) === activeStateNode) ? 3 : 1,
          bg: '#050011', dag: null
        };
      case 'data_flow': 
        return { 
          linkDirectionalParticles: hoverNode ? 0 : 4, 
          linkDirectionalParticleSpeed: hoverNode ? 0 : 0.008, 
          linkDirectionalParticleWidth: 3.5,
          linkColor: () => '#00e5ff', 
          linkCurvature: 0.5, 
          linkWidth: 4, 
          linkOpacity: 0.9,
          bg: '#000814', dag: null 
        };
      case 'database_journey': 
        return { 
          linkDirectionalParticles: 0, linkWidth: 4, linkColor: () => '#ef4444', 
          bg: '#111', dag: 'td' 
        };
      case 'request_journey': 
        return { 
          linkDirectionalParticles: hoverNode ? 0 : 3, 
          linkDirectionalParticleSpeed: hoverNode ? 0 : 0.015,
          linkDirectionalParticleWidth: 2.5,
          linkColor: () => '#0ea5e988', 
          linkWidth: 1.5,
          bg: '#020617', dag: 'td' 
        };
      case 'response_journey':
        return {
          linkDirectionalParticles: hoverNode ? 0 : 4,
          linkDirectionalParticleSpeed: hoverNode ? 0 : 0.02,
          linkDirectionalParticleWidth: 3,
          linkColor: () => '#cc00ff66',
          linkWidth: 2,
          bg: '#0a0a0a', dag: 'lr'
        };
      case 'dependency_galaxy':
        return {
          linkDirectionalParticles: 0, linkColor: () => '#ffffff33', 
          linkWidth: 0.5, bg: '#000010', dag: null
        };
      case 'repository_dna':
        return {
          linkDirectionalParticles: 0, linkColor: () => '#444', linkWidth: 1, bg: '#000', dag: null
        };
      case 'runtime_simulation':
        return {
          linkDirectionalParticles: 8, linkDirectionalParticleSpeed: 0.03, 
          linkColor: () => '#f59e0b', linkWidth: 2, bg: '#0a0a0a', dag: null
        };
      case 'code_understanding':
        return {
          linkDirectionalParticles: 2, linkDirectionalParticleSpeed: 0.015, 
          linkColor: () => '#00ffcc22', linkWidth: 2, bg: '#02020a', dag: null
        };
      default: 
        return { 
          linkDirectionalParticles: 3, linkDirectionalParticleSpeed: 0.01, 
          linkColor: () => '#9d4edd', linkWidth: 1, bg: '#060608', dag: null 
        };
    }
  }, [activeTab, hoverNode]);

  return (
    <div className="flex flex-col h-full relative overflow-hidden">
      <PageHeader title="Flow & Journeys" subtitle="Cinematic visualizations of architecture, logic, and flow" />
      
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-72 bg-surface-container-low border-r border-border-subtle flex flex-col gap-1 overflow-y-auto z-20 shadow-xl">
          <div className="p-4 pb-2 text-xs font-bold text-slate-400 uppercase tracking-widest sticky top-0 bg-surface-container-low/95 backdrop-blur z-10 border-b border-border-subtle">
            22 Journey Modes
          </div>
          <div className="p-2 space-y-1">
            {JOURNEYS.map(j => (
              <button
                key={j.key}
                onClick={() => setActiveTab(j.key)}
                className={`w-full flex items-start gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 text-left group ${
                  activeTab === j.key
                    ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30 shadow-[0_0_15px_rgba(157,78,221,0.1)]'
                    : 'text-slate-400 hover:bg-white/5 border border-transparent hover:text-slate-200'
                }`}
              >
                <span className={`material-symbols-outlined text-[20px] mt-0.5 ${activeTab === j.key ? 'text-violet-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
                  {j.icon}
                </span>
                <div>
                  <div className="leading-tight">{j.label}</div>
                  <div className={`text-[9px] font-normal mt-1 ${activeTab === j.key ? 'text-violet-400/80' : 'text-slate-500'}`}>
                    {j.desc}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* 3D Viewport or Specialized Visualization */}
        <div className="flex-1 relative min-w-0" ref={containerRef} style={{ backgroundColor: config.bg }}>
          {/* Special visualizations for specific journey types */}
          {activeTab === 'user_journey' ? (
            <UserJourneyVisualization data={data} />
          ) : activeTab === 'database_journey' ? (
            <DatabaseJourneyVisualization data={data} />
          ) : activeTab === 'event_timeline' ? (
            <EventTimelineVisualization data={data} />
          ) : activeTab === 'object_lifetime' ? (
            <ObjectLifetimeVisualization data={data} />
          ) : activeTab === 'dependency_galaxy' ? (
            <DependencyGalaxyVisualization data={data} />
          ) : null}

          {/* Generic 3D force graph for other journey types */}
          {!['user_journey', 'database_journey', 'event_timeline', 'object_lifetime', 'dependency_galaxy'].includes(activeTab) && (
            <>
              {loading && (
                <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/60 backdrop-blur-md">
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 rounded-full border-4 border-violet-500/20 border-t-violet-500 animate-spin shadow-[0_0_30px_rgba(157,78,221,0.5)]" />
                    <div className="text-violet-300 font-bold tracking-widest uppercase text-sm animate-pulse">Initializing Rendering Engine...</div>
                  </div>
                </div>
              )}
          
              {error && (
                <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-black/90">
                   <span className="material-symbols-outlined text-red-500 text-6xl mb-4">gpp_bad</span>
                   <p className="text-red-300 font-bold text-lg">{error}</p>
                   <button onClick={() => window.location.reload()} className="mt-4 px-6 py-2 bg-red-600/20 border border-red-500/50 rounded-lg text-red-200 hover:bg-red-600/40 transition-all">Retry</button>
                </div>
              )}

              {!error && data && (
                <div className="w-full h-full absolute inset-0">
              <ForceGraph3D
                ref={fgRef}
                width={dimensions.width}
                height={dimensions.height}
                graphData={data}
                dagMode={config.dag}
                nodeThreeObject={renderNode}
                nodeLabel={node => {
                  if (['code_understanding', 'execution_flow', 'data_flow', 'state_flow', 'api_journey', 'request_journey', 'response_journey', 'object_lifetime', 'dependency_galaxy'].includes(activeTab)) {
                    if (activeTab === 'code_understanding') {
                      const m = node.metrics || {};
                      if (m.loc || m.size) {
                        return `<div class="bg-slate-900/90 border border-violet-500/30 p-3 rounded-lg shadow-xl backdrop-blur-md w-48">
                          <div class="text-sm font-bold text-white mb-2 truncate">${node.name}</div>
                          <div class="flex justify-between text-[11px] mb-1">
                            <span class="text-slate-400">Lines of Code</span>
                            <span class="text-violet-400 font-mono">${m.loc || 0}</span>
                          </div>
                          <div class="flex justify-between text-[11px]">
                            <span class="text-slate-400">File Size</span>
                            <span class="text-emerald-400 font-mono">${m.size ? (m.size / 1024).toFixed(1) + ' KB' : '0 KB'}</span>
                          </div>
                        </div>`;
                      }
                    }
                    return null;
                  }
                  return `<div class="bg-surface-container-high/90 border border-border-subtle p-2 rounded shadow-xl backdrop-blur">
                    <div class="text-xs font-bold text-on-surface">${node.name}</div>
                    <div class="text-[10px] text-text-muted mt-1 break-all max-w-[200px]">${node.desc || ''}</div>
                  </div>`;
                }}
                nodeAutoColorBy="group"
                nodeRelSize={6}
                linkDirectionalArrowLength={config.linkDirectionalArrowLength}
                linkDirectionalArrowRelPos={config.linkDirectionalArrowRelPos}
                linkDirectionalParticles={config.linkDirectionalParticles}
                linkDirectionalParticleWidth={config.linkDirectionalParticleWidth || 2.5}
                linkDirectionalParticleSpeed={config.linkDirectionalParticleSpeed}
                linkCurvature={config.linkCurvature || 0}
                linkOpacity={config.linkOpacity || 0.6}
                linkWidth={config.linkWidth}
                linkColor={config.linkColor}
                backgroundColor={config.bg}
                onNodeHover={(node) => {
                  if (['code_understanding', 'execution_flow', 'data_flow', 'state_flow', 'api_journey', 'request_journey', 'response_journey', 'object_lifetime', 'dependency_galaxy'].includes(activeTab)) {
                    setHoverNode(node ? node.id : null);
                  }
                }}
                onNodeClick={node => {
                  let distance = 80;
                  if (activeTab === 'code_understanding') distance = 120;
                  if (activeTab === 'execution_flow' || activeTab === 'data_flow') distance = 60;
                  if (activeTab === 'state_flow') distance = 150;
                  if (activeTab === 'api_journey') distance = 40;
                  if (activeTab === 'request_journey') distance = 100;
                  if (activeTab === 'response_journey') distance = 80;
                  
                  const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
                  fgRef.current.cameraPosition(
                    { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
                    node,
                    1200
                  );
                }}
              />


              {/* Custom Glass Card Overlay for Code City */}
              {activeTab === 'code_understanding' && hoverNode && data.nodes.find(n => n.id === hoverNode) && (() => {
                const node = data.nodes.find(n => n.id === hoverNode);
                return (
                  <div 
                    className="absolute z-50 p-4 bg-black/70 backdrop-blur-xl border border-white/20 rounded-xl shadow-[0_0_40px_rgba(0,255,204,0.15)] w-64 transition-opacity pointer-events-none"
                    style={{ left: '50%', top: '50%', transform: 'translate(20px, -50%)' }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="material-symbols-outlined text-white/50 text-sm">insert_drive_file</span>
                      <h3 className="text-white font-bold text-sm truncate">{node.name}</h3>
                    </div>
                    <div className="space-y-1.5 mt-3">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-white/50">District</span>
                        <span className="text-white/90 font-mono">/src/module_{node.group}</span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-white/50">Lines of Code</span>
                        <span className="text-emerald-400 font-mono font-bold">{Math.max(10, (node.val || 1)*4)}</span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-white/50">Complexity</span>
                        <span className={`${node.group === 1 ? 'text-emerald-400' : node.group === 2 ? 'text-amber-400' : 'text-rose-400'} font-bold`}>
                          {node.group === 1 ? 'Healthy' : node.group === 2 ? 'Moderate' : 'High'}
                        </span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-white/50">Authors</span>
                        <span className="text-white/90 font-mono">{Math.max(1, Math.floor((node.val||1)/2))}</span>
                      </div>
                    </div>
                  </div>
                );
              })()}

              {/* Custom Glass Card Overlay for Execution Flow (Tron) */}
              {activeTab === 'execution_flow' && hoverNode && data.nodes.find(n => n.id === hoverNode) && (() => {
                const node = data.nodes.find(n => n.id === hoverNode);
                const execTime = Math.max(5, (node.val||1) * 3 + Math.floor(Math.random()*10));
                return (
                  <div 
                    className="absolute z-50 p-4 bg-slate-950/80 backdrop-blur-xl border border-cyan-500/30 rounded-xl shadow-[0_0_40px_rgba(0,229,255,0.2)] w-72 transition-opacity pointer-events-none"
                    style={{ left: '50%', top: '50%', transform: 'translate(20px, -50%)' }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="material-symbols-outlined text-cyan-400 text-sm">memory</span>
                      <h3 className="text-white font-bold text-sm truncate">{node.name}</h3>
                    </div>
                    <div className="space-y-1.5 mt-3">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-cyan-200/50">Execution Time</span>
                        <span className="text-cyan-400 font-mono font-bold">{execTime}ms</span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-cyan-200/50">Parameters</span>
                        <span className="text-white/90 font-mono text-[9px] bg-white/10 px-1 rounded">({node.group > 1 ? 'req, res' : 'data, opts'})</span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-cyan-200/50">Return Value</span>
                        <span className="text-white/90 font-mono text-[9px] bg-white/10 px-1 rounded">Promise&lt;Result&gt;</span>
                      </div>
                      <div className="mt-3 pt-3 border-t border-cyan-500/20">
                        <span className="text-[10px] text-cyan-200/50 mb-1 block">Source Code Preview</span>
                        <pre className="text-[9px] text-cyan-100/70 font-mono bg-black/50 p-2 rounded border border-white/5 overflow-hidden">
{`async function ${node.name}(...) {
  const start = performance.now();
  await processData();
  return { status: "OK" };
}`}
                        </pre>
                      </div>
                    </div>
                  </div>
                );
              })()}

              {/* Custom Glass Card Overlay for Data Flow (Liquid) */}
              {activeTab === 'data_flow' && hoverNode && data.nodes.find(n => n.id === hoverNode) && (() => {
                const node = data.nodes.find(n => n.id === hoverNode);
                return (
                  <div 
                    className="absolute z-50 p-4 bg-slate-900/80 backdrop-blur-xl border border-blue-500/30 rounded-xl shadow-[0_0_40px_rgba(59,130,246,0.3)] w-72 transition-opacity pointer-events-none"
                    style={{ left: '50%', top: '50%', transform: 'translate(20px, -50%)' }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="material-symbols-outlined text-blue-400 text-sm">water_drop</span>
                      <h3 className="text-white font-bold text-sm truncate">{node.name}</h3>
                    </div>
                    <div className="space-y-1.5 mt-3">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-blue-200/50">Node Type</span>
                        <span className="text-blue-400 font-bold">{node.group === 3 ? 'Database Lake' : node.group === 1 ? 'API Bridge' : 'Cache Reservoir'}</span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-blue-200/50">Throughput</span>
                        <span className="text-white/90 font-mono font-bold">{Math.max(1, (node.val||1)*12)} req/s</span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-blue-200/50">Avg Payload Size</span>
                        <span className="text-white/90 font-mono font-bold">{Math.max(128, (node.val||1)*512)} B</span>
                      </div>
                      <div className="mt-3 pt-3 border-t border-blue-500/20">
                        <span className="text-[10px] text-blue-200/50 mb-1 block">Object Structure Preview</span>
                        <pre className="text-[9px] text-blue-100/80 font-mono bg-black/60 p-2 rounded border border-white/5 overflow-hidden">
{`{
  "id": "uuid",
  "type": "${node.name.toLowerCase()}_payload",
  "data": {
    "status": "active",
    "timestamp": ${Date.now()}
  }
}`}
                        </pre>
                      </div>
                    </div>
                  </div>
                );
              })()}
              
              {/* Custom Glass Card Overlay for State Flow */}
              {activeTab === 'state_flow' && hoverNode && data.nodes.find(n => n.id === hoverNode) && (() => {
                const node = data.nodes.find(n => n.id === hoverNode);
                const isActive = activeStateNode === node.id;
                return (
                  <div 
                    className="absolute z-50 p-4 bg-indigo-950/80 backdrop-blur-xl border border-indigo-500/30 rounded-xl shadow-[0_0_40px_rgba(204,0,255,0.2)] w-56 transition-opacity pointer-events-none"
                    style={{ left: '50%', top: '50%', transform: 'translate(20px, -50%)' }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="material-symbols-outlined text-fuchsia-400 text-sm">schema</span>
                      <h3 className="text-white font-bold text-sm truncate">{node.name}</h3>
                    </div>
                    {isActive && (
                      <div className="mt-2 text-[10px] font-bold text-fuchsia-300 bg-fuchsia-900/50 border border-fuchsia-500/30 rounded px-2 py-1 text-center animate-pulse">
                        CURRENT ACTIVE STATE
                      </div>
                    )}
                  </div>
                );
              })()}

              {/* Custom Glass Card Overlay for API Journey (Airports) */}
              {activeTab === 'api_journey' && hoverNode && data.nodes.find(n => n.id === hoverNode) && (() => {
                const node = data.nodes.find(n => n.id === hoverNode);
                const latency = Math.max(10, Math.floor((node.val||1) * 45));
                return (
                  <div 
                    className="absolute z-50 p-4 bg-slate-900/90 backdrop-blur-xl border border-slate-500/30 rounded-xl shadow-[0_0_40px_rgba(255,255,255,0.1)] w-64 transition-opacity pointer-events-none"
                    style={{ left: '50%', top: '50%', transform: 'translate(20px, -50%)' }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="material-symbols-outlined text-emerald-400 text-sm">flight_land</span>
                      <h3 className="text-white font-bold text-sm truncate">{node.name}</h3>
                    </div>
                    <div className="space-y-1.5 mt-3">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-400">Endpoint</span>
                        <span className="text-white/90 font-mono">/api/v1/{node.name.toLowerCase()}</span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-400">Latency</span>
                        <span className={`${latency > 200 ? 'text-rose-400' : latency > 80 ? 'text-amber-400' : 'text-emerald-400'} font-mono font-bold`}>{latency}ms</span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-400">Payload</span>
                        <span className="text-white/90 font-mono">{(node.val||1)*12} KB</span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-400">Status</span>
                        <span className="text-emerald-400 font-mono">200 OK</span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-400">Success Rate</span>
                        <span className="text-white/90 font-mono">99.8%</span>
                      </div>
                    </div>
                  </div>
                );
              })()}
              
              <div className="absolute top-6 left-6 pointer-events-none z-10">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-4xl text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]">
                    {JOURNEYS.find(j => j.key === activeTab)?.icon}
                  </span>
                  <div>
                    <h2 className="text-3xl font-black text-white drop-shadow-xl">{JOURNEYS.find(j => j.key === activeTab)?.label}</h2>
                    <p className="text-sm font-semibold text-white/70 mt-0.5 drop-shadow-md">
                      {data.nodes.length} entities • {data.links.length} flows
                    </p>
                  </div>
                </div>
                <div className="mt-6 px-4 py-3 bg-black/60 border border-white/10 rounded-xl backdrop-blur-md shadow-2xl max-w-sm">
                  <p className="text-[11px] font-bold text-white/90 uppercase tracking-widest mb-1 text-primary">Director's Notes</p>
                  <p className="text-xs text-white/70 leading-relaxed">{JOURNEYS.find(j => j.key === activeTab)?.desc}</p>
                  <div className="h-px bg-white/10 my-3 w-full" />
                  <p className="text-[10px] text-white/50 flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[14px]">360</span>
                    Drag to rotate • Scroll to zoom • Click to focus
                  </p>
                </div>
              </div>

              {/* Custom Glass Card Overlay for Request Journey (Waterfall) */}
              {activeTab === 'request_journey' && hoverNode && data.nodes.find(n => n.id === hoverNode) && (() => {
                const node = data.nodes.find(n => n.id === hoverNode);
                return (
                  <div 
                    className="absolute z-50 p-4 bg-slate-900/90 backdrop-blur-xl border border-sky-500/30 rounded-xl shadow-[0_0_40px_rgba(14,165,233,0.15)] w-72 transition-opacity pointer-events-none"
                    style={{ left: '50%', top: '50%', transform: 'translate(20px, -50%)' }}
                  >
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-white/10">
                      <span className="material-symbols-outlined text-sky-400 text-sm">waterfall_chart</span>
                      <h3 className="text-white font-bold text-sm truncate uppercase tracking-widest">{node.name} STAGE</h3>
                    </div>
                    <div className="space-y-3 mt-2">
                      <div>
                        <div className="text-[10px] text-sky-200/60 uppercase tracking-wider mb-1">Network Timing</div>
                        <div className="flex justify-between items-center text-xs">
                          <span className="text-slate-300">Queuing</span>
                          <span className="text-white font-mono">1.2ms</span>
                        </div>
                        <div className="flex justify-between items-center text-xs">
                          <span className="text-slate-300">Processing</span>
                          <span className="text-white font-mono">{Math.floor(Math.random() * 40 + 5)}ms</span>
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-sky-200/60 uppercase tracking-wider mb-1">Headers</div>
                        <div className="bg-black/50 p-1.5 rounded border border-white/5 font-mono text-[9px] text-sky-100/80">
                          <div>Content-Type: application/json</div>
                          <div>X-Trace-Id: req_{node.id.substring(0,6)}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })()}

              {/* Custom Glass Card Overlay for Response Journey (Mutating Bubble) */}
              {activeTab === 'response_journey' && hoverNode && data.nodes.find(n => n.id === hoverNode) && (() => {
                const node = data.nodes.find(n => n.id === hoverNode);
                const nodeIndex = data.nodes.findIndex(n => n.id === hoverNode);
                // Simulate mutations based on depth
                const isCompressed = nodeIndex > 0;
                const isSerialized = nodeIndex > 1;
                const isEncrypted = nodeIndex > 2;
                
                return (
                  <div 
                    className="absolute z-50 p-4 bg-fuchsia-950/90 backdrop-blur-xl border border-fuchsia-500/30 rounded-xl shadow-[0_0_50px_rgba(204,0,255,0.2)] w-64 transition-opacity pointer-events-none"
                    style={{ left: '50%', top: '50%', transform: 'translate(20px, -50%)' }}
                  >
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-fuchsia-500/20">
                      <span className="material-symbols-outlined text-fuchsia-400 text-sm">bubble_chart</span>
                      <h3 className="text-white font-bold text-sm truncate">Response Payload</h3>
                    </div>
                    <div className="space-y-2 mt-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-fuchsia-200/60">Current Stage</span>
                        <span className="text-white font-bold">{node.name}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-fuchsia-200/60">Size</span>
                        <span className="text-white font-mono">{isCompressed ? '4.2 KB' : '18.5 KB'}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-fuchsia-200/60">Compression</span>
                        <span className={isCompressed ? "text-emerald-400 font-mono" : "text-slate-500 font-mono"}>{isCompressed ? '77% (GZIP)' : 'None'}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-fuchsia-200/60">Format</span>
                        <span className="text-fuchsia-300 font-mono">{isSerialized ? 'Binary / Encrypted' : 'JSON Object'}</span>
                      </div>
                      <div className="mt-2 pt-2 border-t border-fuchsia-500/20">
                        <div className="text-[10px] text-fuchsia-200/60 uppercase tracking-wider mb-1">State Flags</div>
                        <div className="flex gap-1">
                          <span className={`px-1.5 py-0.5 rounded text-[9px] ${isCompressed ? 'bg-fuchsia-500/20 text-fuchsia-300' : 'bg-white/5 text-white/30'}`}>COMPRESSED</span>
                          <span className={`px-1.5 py-0.5 rounded text-[9px] ${isSerialized ? 'bg-fuchsia-500/20 text-fuchsia-300' : 'bg-white/5 text-white/30'}`}>SERIALIZED</span>
                          <span className={`px-1.5 py-0.5 rounded text-[9px] ${isEncrypted ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/5 text-white/30'}`}>SECURE</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })()}
              {/* Custom Glass Card Overlay for Object Lifetime */}
              {activeTab === 'object_lifetime' && hoverNode && data.nodes.find(n => n.id === hoverNode) && (() => {
                const node = data.nodes.find(n => n.id === hoverNode);
                const age = node.val || 1;
                const status = age > 5 ? 'Mature' : (age > 2 ? 'Active' : 'Newborn');
                return (
                  <div 
                    className="absolute z-50 p-4 bg-emerald-950/90 backdrop-blur-xl border border-emerald-500/30 rounded-xl shadow-[0_0_40px_rgba(16,185,129,0.15)] w-64 transition-opacity pointer-events-none"
                    style={{ left: '50%', top: '50%', transform: 'translate(20px, -50%)' }}
                  >
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-emerald-500/20">
                      <span className="material-symbols-outlined text-emerald-400 text-sm">park</span>
                      <h3 className="text-white font-bold text-sm truncate">{node.name}</h3>
                    </div>
                    <div className="space-y-2 mt-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-emerald-200/60">Status</span>
                        <span className="text-white font-bold">{status}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-emerald-200/60">Memory Size</span>
                        <span className="text-white font-mono">{Math.max(12, age * 34)} KB</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-emerald-200/60">References</span>
                        <span className="text-emerald-300 font-mono">{Math.floor(age / 2) + 1}</span>
                      </div>
                    </div>
                  </div>
                );
              })()}

              {/* Custom Glass Card Overlay for Dependency Galaxy */}
              {activeTab === 'dependency_galaxy' && hoverNode && data.nodes.find(n => n.id === hoverNode) && (() => {
                const node = data.nodes.find(n => n.id === hoverNode);
                const isStar = node.group === 1 || (node.val || 1) * 2 > 6;
                return (
                  <div 
                    className="absolute z-50 p-4 bg-blue-950/90 backdrop-blur-xl border border-blue-500/30 rounded-xl shadow-[0_0_50px_rgba(0,212,255,0.2)] w-72 transition-opacity pointer-events-none"
                    style={{ left: '50%', top: '50%', transform: 'translate(20px, -50%)' }}
                  >
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-blue-500/20">
                      <span className="material-symbols-outlined text-blue-400 text-sm">public</span>
                      <h3 className="text-white font-bold text-sm truncate">{node.name}</h3>
                    </div>
                    <div className="space-y-2 mt-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-blue-200/60">Classification</span>
                        <span className="text-white font-bold">{isStar ? 'Core Module (Star)' : 'Dependent Module (Planet)'}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-blue-200/60">Orbit Radius</span>
                        <span className="text-white font-mono">{isStar ? 'Center' : Math.floor(Math.random() * 50 + 10) + ' AU'}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-blue-200/60">Gravitational Pull</span>
                        <span className="text-blue-300 font-mono">{node.val || 1} M☉</span>
                      </div>
                      <div className="mt-2 pt-2 border-t border-blue-500/20">
                         <span className="text-[10px] text-blue-200/60 uppercase tracking-wider block">Path</span>
                         <span className="text-xs text-white/80 font-mono truncate block mt-1">{node.desc || node.file_path || '/src/unknown'}</span>
                      </div>
                    </div>
                  </div>
                );
              })()}
              
              {/* Camera Controls */}
              <div className="absolute bottom-6 right-6 z-20 flex flex-col gap-2">
                <button 
                  onClick={() => handleZoom('in')}
                  className="w-10 h-10 bg-surface-container-high/90 hover:bg-surface-container-highest text-slate-300 rounded-full flex items-center justify-center backdrop-blur shadow-lg border border-white/10 transition-colors"
                  title="Zoom In"
                >
                  <span className="material-symbols-outlined text-lg">add</span>
                </button>
                <button 
                  onClick={() => handleZoom('fit')}
                  className="w-10 h-10 bg-surface-container-high/90 hover:bg-surface-container-highest text-slate-300 rounded-full flex items-center justify-center backdrop-blur shadow-lg border border-white/10 transition-colors"
                  title="Fit to View"
                >
                  <span className="material-symbols-outlined text-lg">center_focus_strong</span>
                </button>
                <button 
                  onClick={() => handleZoom('out')}
                  className="w-10 h-10 bg-surface-container-high/90 hover:bg-surface-container-highest text-slate-300 rounded-full flex items-center justify-center backdrop-blur shadow-lg border border-white/10 transition-colors"
                  title="Zoom Out"
                >
                  <span className="material-symbols-outlined text-lg">remove</span>
                </button>
              </div>

              {activeTab === 'runtime_simulation' && (
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 flex items-center gap-3 px-6 py-3 bg-black/80 border border-amber-500/30 rounded-full backdrop-blur-md shadow-[0_0_30px_rgba(245,158,11,0.2)]">
                  <span className="material-symbols-outlined text-amber-500 animate-pulse">play_circle</span>
                  <span className="text-sm font-bold text-amber-400">Simulation Running... (Tick: {simulationState})</span>
                </div>
              )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
