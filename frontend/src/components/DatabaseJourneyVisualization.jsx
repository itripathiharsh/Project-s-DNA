import { useState, useEffect, useRef } from 'react';

// We will dynamically compute schema and trains inside the component now

function StationNode({ station, isHovered, onHover, selectedConnections }) {
  const activityColor =
    station.activity > 0.8
      ? 'from-green-400 to-green-500'
      : station.activity > 0.6
      ? 'from-yellow-400 to-yellow-500'
      : 'from-orange-400 to-orange-500';

  return (
    <g
      key={station.id}
      onMouseEnter={() => onHover(station.id)}
      onMouseLeave={() => onHover(null)}
      className="cursor-pointer"
    >
      {/* Station glow based on activity */}
      <circle
        cx={station.position.x}
        cy={station.position.y}
        r={isHovered ? 60 : 45}
        className={`transition-all duration-300 ${isHovered ? 'fill-white/10' : 'fill-white/5'}`}
      />

      {/* Outer ring - activity indicator */}
      <circle
        cx={station.position.x}
        cy={station.position.y}
        r={40}
        fill="none"
        strokeWidth="2"
        className={`stroke-${station.activity > 0.8 ? 'green' : station.activity > 0.6 ? 'yellow' : 'orange'}-400`}
        opacity={station.activity}
        style={{
          filter: `drop-shadow(0 0 ${station.activity * 15}px ${
            station.activity > 0.8
              ? 'rgb(74, 222, 128)'
              : station.activity > 0.6
              ? 'rgb(250, 204, 21)'
              : 'rgb(249, 115, 22)'
          })`,
        }}
      />

      {/* Station circle */}
      <circle
        cx={station.position.x}
        cy={station.position.y}
        r={30}
        fill="url(#stationGradient)"
        stroke={isHovered ? 'rgb(168, 85, 247)' : 'rgb(147, 112, 221)'}
        strokeWidth={isHovered ? 3 : 2}
        className="transition-all duration-300"
      />

      {/* Icon */}
      <text
        x={station.position.x}
        y={station.position.y + 5}
        textAnchor="middle"
        fontSize="24"
        dominantBaseline="middle"
      >
        {station.icon}
      </text>

      {/* Label */}
      <text
        x={station.position.x}
        y={station.position.y + 50}
        textAnchor="middle"
        fontSize="12"
        fontWeight="600"
        fill="rgb(240, 240, 240)"
        className="pointer-events-none"
      >
        {station.label}
      </text>

      {/* Hover tooltip with metrics */}
      {isHovered && (() => {
        const displayConnections = station.connections.slice(0, 4);
        const hasMore = station.connections.length > 4;
        const tooltipHeight = 100 + (displayConnections.length + (hasMore ? 1 : 0)) * 14;
        
        return (
        <>
          {/* Tooltip background */}
          <rect
            x={station.position.x + 45}
            y={station.position.y - 80}
            width="220"
            height={tooltipHeight}
            rx="8"
            fill="rgb(30, 27, 50)"
            stroke="rgb(147, 112, 221)"
            strokeWidth="1"
            opacity="0.95"
            className="drop-shadow-lg"
          />

          {/* Tooltip content */}
          <text
            x={station.position.x + 55}
            y={station.position.y - 65}
            fontSize="11"
            fontWeight="700"
            fill="rgb(168, 85, 247)"
          >
            {station.label}
          </text>

          {/* Rows metric */}
          <text x={station.position.x + 55} y={station.position.y - 48} fontSize="10" fill="rgb(200, 200, 200)">
            Rows
          </text>
          <text x={station.position.x + 150} y={station.position.y - 48} fontSize="10" fontWeight="700" fill="rgb(74, 222, 128)" textAnchor="end">
            {station.metrics.rows.toLocaleString()}
          </text>

          {/* Indexes metric */}
          <text x={station.position.x + 55} y={station.position.y - 32} fontSize="10" fill="rgb(200, 200, 200)">
            Indexes
          </text>
          <text x={station.position.x + 150} y={station.position.y - 32} fontSize="10" fontWeight="700" fill="rgb(250, 204, 21)" textAnchor="end">
            {station.metrics.indexes}
          </text>

          {/* Query count metric */}
          <text x={station.position.x + 55} y={station.position.y - 16} fontSize="10" fill="rgb(200, 200, 200)">
            Queries
          </text>
          <text x={station.position.x + 150} y={station.position.y - 16} fontSize="10" fontWeight="700" fill="rgb(249, 115, 22)" textAnchor="end">
            {station.metrics.queryCount.toLocaleString()}
          </text>

          {/* Activity metric */}
          <text x={station.position.x + 55} y={station.position.y} fontSize="10" fill="rgb(200, 200, 200)">
            Activity
          </text>
          <text x={station.position.x + 150} y={station.position.y} fontSize="10" fontWeight="700" fill="rgb(148, 163, 184)" textAnchor="end">
            {Math.round(station.activity * 100)}%
          </text>

          {/* Connections */}
          <text x={station.position.x + 55} y={station.position.y + 16} fontSize="10" fill="rgb(200, 200, 200)">
            Connections
          </text>
          <text x={station.position.x + 55} y={station.position.y + 30} fontSize="9" fill="rgb(168, 85, 247)">
            {displayConnections.map((c, i) => (
              <tspan key={i} x={station.position.x + 55} dy={i > 0 ? '1.2em' : '0'}>
                → {c.name}
              </tspan>
            ))}
            {hasMore && (
              <tspan x={station.position.x + 55} dy="1.2em">
                → +{station.connections.length - 4} more
              </tspan>
            )}
          </text>
        </>
        );
      })()}
    </g>
  );
}

function Track({ from, to }) {
  return (
    <line
      x1={from.x}
      y1={from.y}
      x2={to.x}
      y2={to.y}
      stroke="rgb(147, 112, 221)"
      strokeWidth="2"
      opacity="0.4"
      strokeDasharray="5,5"
      className="pointer-events-none"
    />
  );
}

function Train({ fromStation, toStation, speed, duration, color, label, delay }) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let frame;
    let isActive = true;
    let startTime = Date.now() - delay * 1000;

    const animate = () => {
      if (!isActive) return;
      const elapsed = (Date.now() - startTime) / 1000;
      const cycleProgress = ((elapsed % duration) / duration) % 1;
      setProgress(cycleProgress);
      frame = requestAnimationFrame(animate);
    };

    frame = requestAnimationFrame(animate);
    return () => {
      isActive = false;
      if (frame) cancelAnimationFrame(frame);
    };
  }, [duration, delay]);

  const currentX = fromStation.x + (toStation.x - fromStation.x) * progress;
  const currentY = fromStation.y + (toStation.y - fromStation.y) * progress;

  const speedFactor = speed > 0.4 ? 1.5 : speed > 0.2 ? 1 : 0.5;

  return (
    <g key={`${fromStation.id}-${toStation.id}`}>
      {/* Train motion trail */}
      <circle
        cx={currentX}
        cy={currentY}
        r={speedFactor > 1 ? 8 : 6}
        className={`bg-gradient-to-r ${color}`}
        fill={`url(#train-${color})`}
        opacity={0.8}
        style={{
          filter: `drop-shadow(0 0 ${12 * speedFactor}px ${
            speed > 0.4
              ? 'rgb(74, 222, 128)'
              : speed > 0.2
              ? 'rgb(250, 204, 21)'
              : 'rgb(249, 115, 22)'
          })`,
        }}
      />

      {/* Motion trail for faster queries */}
      {speed > 0.3 && (
        <>
          {[0.3, 0.6, 0.9].map((offset, i) => {
            const trailX =
              fromStation.x + (toStation.x - fromStation.x) * Math.max(0, progress - offset * 0.2);
            const trailY =
              fromStation.y + (toStation.y - fromStation.y) * Math.max(0, progress - offset * 0.2);
            return (
              <circle
                key={i}
                cx={trailX}
                cy={trailY}
                r={4}
                fill={speed > 0.4 ? 'rgb(74, 222, 128)' : 'rgb(250, 204, 21)'}
                opacity={0.3 - i * 0.1}
              />
            );
          })}
        </>
      )}

      {/* Label - shown near train */}
      {progress < 0.1 && (
        <text
          x={fromStation.x}
          y={fromStation.y - 15}
          fontSize="10"
          fontWeight="600"
          fill={speed > 0.4 ? 'rgb(74, 222, 128)' : speed > 0.2 ? 'rgb(250, 204, 21)' : 'rgb(249, 115, 22)'}
          textAnchor="middle"
          opacity={1 - progress * 10}
        >
          {label}
        </text>
      )}
    </g>
  );
}

export default function DatabaseJourneyVisualization({ data }) {
  const [hoveredStation, setHoveredStation] = useState(null);
  const svgRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // Generate database stations from actual code modules
  const MOCK_DATABASE_SCHEMA = (data?.nodes || []).slice(0, 15).map((node, i) => {
    // Generate a nice circular layout
    const total = Math.min((data?.nodes || []).length, 15);
    const angle = (i / total) * Math.PI * 2;
    const radius = 200 + (i % 2 === 0 ? 50 : -50);
    const x = dimensions.width / 2 + Math.cos(angle) * radius;
    const y = dimensions.height / 2 + Math.sin(angle) * radius;

    // Use links to determine connections
    const connections = (data?.links || [])
      .filter(l => (typeof l.source === 'object' ? l.source.id : l.source) === node.id)
      .map(l => {
        const targetId = typeof l.target === 'object' ? l.target.id : l.target;
        const targetNode = data?.nodes?.find(n => n.id === targetId);
        const name = (targetNode?.name || targetId.split(':').pop() || targetId).replace('.py', '').replace('.js', '');
        return { id: targetId, name: name.length > 20 ? name.substring(0, 17) + '...' : name };
      });

    // Derive deterministic metrics from node id or name
    const hash = node.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const rows = 1000 + (hash % 49000);
    const indexes = 1 + (hash % 5);
    const queryCount = 100 + ((hash * 7) % 9900);
    const activity = 0.2 + ((hash % 100) / 100) * 0.8;

    return {
      id: node.id,
      label: (node.name || 'Unknown').replace('.py', '').replace('.js', ''),
      icon: node.group === 1 ? '🖥️' : node.group === 2 ? '⚙️' : '💾',
      position: { x: Number.isFinite(x) ? x : 400, y: Number.isFinite(y) ? y : 300 },
      metrics: { rows, indexes, queryCount },
      connections: connections,
      activity: activity,
    };
  });

  // Generate trains from actual connections that exist in our schema
  const QUERY_TRAINS = (data?.links || [])
    .filter(link => {
      const fromId = typeof link.source === 'object' ? link.source.id : link.source;
      const toId = typeof link.target === 'object' ? link.target.id : link.target;
      return MOCK_DATABASE_SCHEMA.some(s => s.id === fromId) && MOCK_DATABASE_SCHEMA.some(s => s.id === toId);
    })
    .slice(0, 20)
    .map((link, i) => {
      const fromId = typeof link.source === 'object' ? link.source.id : link.source;
      const toId = typeof link.target === 'object' ? link.target.id : link.target;
      
      // Deterministic speed based on connection ids
      const hash = (fromId + toId).split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) + i;
      const speed = 0.1 + ((hash % 40) / 100);
      const duration = speed > 0.4 ? 3 : speed > 0.2 ? 5 : 8;
      const color = speed > 0.4 ? 'from-green-400 to-green-500' : speed > 0.2 ? 'from-yellow-400 to-yellow-500' : 'from-red-400 to-red-500';
      const label = link.label || 'QUERY';
      
      return { id: i, from: fromId, to: toId, speed, duration, color, label };
    });

  useEffect(() => {
    const handleResize = () => {
      if (svgRef.current) {
        setDimensions({
          width: svgRef.current.parentElement.offsetWidth,
          height: svgRef.current.parentElement.offsetHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize();
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="w-full h-full flex flex-col bg-slate-950">
      {/* SVG Visualization */}
      <div className="flex-1 overflow-hidden bg-gradient-to-br from-slate-900 via-slate-950 to-black relative">
        <svg
          ref={svgRef}
          width={dimensions.width}
          height={dimensions.height}
          className="w-full h-full"
          style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(30, 27, 50, 0.5) 0%, transparent 70%)' }}
        >
          <defs>
            {/* Station gradient */}
            <radialGradient id="stationGradient" cx="30%" cy="30%">
              <stop offset="0%" stopColor="rgba(168, 85, 247, 0.6)" />
              <stop offset="100%" stopColor="rgba(147, 112, 221, 0.3)" />
            </radialGradient>

            {/* Train gradients */}
            {[
              { id: 'train-from-green-400 to-green-500', colors: ['rgb(74, 222, 128)', 'rgb(34, 197, 94)'] },
              { id: 'train-from-yellow-400 to-yellow-500', colors: ['rgb(250, 204, 21)', 'rgb(202, 138, 4)'] },
              { id: 'train-from-red-400 to-red-500', colors: ['rgb(249, 115, 22)', 'rgb(220, 38, 38)'] },
            ].map(gradient => (
              <linearGradient key={gradient.id} id={gradient.id} x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor={gradient.colors[0]} />
                <stop offset="100%" stopColor={gradient.colors[1]} />
              </linearGradient>
            ))}
          </defs>

          {/* Background grid */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(147, 112, 221, 0.05)" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width={dimensions.width} height={dimensions.height} fill="url(#grid)" />

          {/* Tracks (foreign keys) */}
          {MOCK_DATABASE_SCHEMA.map(station =>
            station.connections.map(conn => {
              const targetStation = MOCK_DATABASE_SCHEMA.find(s => s.id === conn.id);
              if (!targetStation) return null;
              return <Track key={`${station.id}-${conn.id}`} from={station.position} to={targetStation.position} />;
            })
          )}

          {/* Trains (queries) */}
          {QUERY_TRAINS.map((query, idx) => {
            const fromStation = MOCK_DATABASE_SCHEMA.find(s => s.id === query.from);
            const toStation = MOCK_DATABASE_SCHEMA.find(s => s.id === query.to);
            if (!fromStation || !toStation) return null;
            return (
              <Train
                key={query.id}
                fromStation={fromStation.position}
                toStation={toStation.position}
                speed={query.speed}
                duration={query.duration}
                color={query.color}
                label={query.label}
                delay={idx * 0.5}
              />
            );
          })}

          {/* Stations */}
          {MOCK_DATABASE_SCHEMA.map(station => (
            <StationNode
              key={station.id}
              station={station}
              isHovered={hoveredStation === station.id}
              onHover={setHoveredStation}
            />
          ))}
        </svg>
      </div>

      {/* Legend and Info Panel */}
      <div className="p-6 border-t border-slate-700/50 bg-slate-900/50 backdrop-blur">
        <div className="flex items-center justify-between gap-8">
          {/* Legend */}
          <div className="flex-1">
            <h3 className="text-sm font-bold text-white mb-3">Query Performance</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-400 shadow-lg shadow-green-400/50"></div>
                <span className="text-xs text-slate-300">Fast (&gt;0.4s)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-yellow-400 shadow-lg shadow-yellow-400/50"></div>
                <span className="text-xs text-slate-300">Medium (0.2-0.4s)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-orange-400 shadow-lg shadow-orange-400/50"></div>
                <span className="text-xs text-slate-300">Slow (&lt;0.2s)</span>
              </div>
            </div>
          </div>

          {/* Activity Indicator */}
          <div className="flex-1">
            <h3 className="text-sm font-bold text-white mb-3">Station Activity</h3>
            <div className="space-y-2">
              {MOCK_DATABASE_SCHEMA.filter(s => hoveredStation === s.id).map(s => (
                <div key={s.id} className="text-xs">
                  <div className="flex justify-between mb-1">
                    <span className="text-slate-300">{s.label}</span>
                    <span className="text-violet-400 font-semibold">{Math.round(s.activity * 100)}% active</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-gradient-to-r ${
                        s.activity > 0.8
                          ? 'from-green-400 to-green-500'
                          : s.activity > 0.6
                          ? 'from-yellow-400 to-yellow-500'
                          : 'from-orange-400 to-orange-500'
                      }`}
                      style={{ width: `${s.activity * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Summary */}
          <div className="text-right text-xs text-slate-400">
            <div className="text-white font-semibold mb-1">{MOCK_DATABASE_SCHEMA.length} Stations</div>
            <div className="text-violet-400">{QUERY_TRAINS.length} Active Trains</div>
            <div className="text-slate-500 mt-1">Metro Transit System</div>
          </div>
        </div>
      </div>
    </div>
  );
}
