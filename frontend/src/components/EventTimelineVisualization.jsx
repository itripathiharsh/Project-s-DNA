import { useState, useMemo } from 'react';

const EVENT_TYPES = [
  { type: 'Commit', icon: '🔗', color: 'from-blue-500 to-cyan-500', bg: 'bg-blue-500/10', border: 'border-blue-500/30' },
  { type: 'Build', icon: '🔨', color: 'from-purple-500 to-pink-500', bg: 'bg-purple-500/10', border: 'border-purple-500/30' },
  { type: 'Deploy', icon: '🚀', color: 'from-yellow-500 to-orange-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' },
  { type: 'Bug', icon: '🐛', color: 'from-red-500 to-orange-500', bg: 'bg-red-500/10', border: 'border-red-500/30' },
  { type: 'Fix', icon: '✅', color: 'from-green-500 to-emerald-500', bg: 'bg-green-500/10', border: 'border-green-500/30' },
  { type: 'Release', icon: '🎉', color: 'from-violet-500 to-purple-500', bg: 'bg-violet-500/10', border: 'border-violet-500/30' },
];

export default function EventTimelineVisualization({ data }) {
  const [hoveredEvent, setHoveredEvent] = useState(null);

  const EVENTS = useMemo(() => {
    return (data?.nodes || []).map((node, i) => {
      const m = node.metrics || {};
      const baseTime = i; 
      
      let type = 'Commit';
      let icon = '🔗';
      let color = 'from-blue-500 to-cyan-500';
      let bg = 'bg-blue-500/10';
      let border = 'border-blue-500/30';

      const msg = (m.message || '').toLowerCase();
      
      if (msg.includes('fix') || msg.includes('bug')) {
        type = 'Fix'; icon = '✅'; color = 'from-green-500 to-emerald-500'; bg = 'bg-green-500/10'; border = 'border-green-500/30';
      } else if (msg.includes('release') || msg.includes('version')) {
        type = 'Release'; icon = '🎉'; color = 'from-violet-500 to-purple-500'; bg = 'bg-violet-500/10'; border = 'border-violet-500/30';
      } else if (msg.includes('build') || msg.includes('ci')) {
        type = 'Build'; icon = '🔨'; color = 'from-purple-500 to-pink-500'; bg = 'bg-purple-500/10'; border = 'border-purple-500/30';
      } else if (msg.includes('deploy')) {
        type = 'Deploy'; icon = '🚀'; color = 'from-yellow-500 to-orange-500'; bg = 'bg-yellow-500/10'; border = 'border-yellow-500/30';
      }

      return {
        id: node.id,
        type,
        icon,
        timestamp: baseTime,
        title: node.name || 'Unknown Commit',
        description: m.message || 'No description available',
        color, bg, border,
        metadata: {
          author: m.author || 'Unknown',
          hash: m.hash || node.id,
          date: m.timestamp ? new Date(m.timestamp * 1000).toLocaleString() : 'N/A'
        },
      };
    }).reverse(); 
  }, [data]);

  return (
    <div className="w-full h-full flex flex-col bg-slate-950 overflow-hidden font-sans">
      {/* Header */}
      <div className="p-6 border-b border-white/5 bg-slate-900/60 backdrop-blur-xl z-20 shadow-xl flex justify-between items-center shrink-0">
        <div>
          <h2 className="text-2xl font-black text-white tracking-wide">Repository Timeline</h2>
          <p className="text-sm font-semibold text-slate-400 mt-1">Vertical Chronological Git Evolution</p>
        </div>
        
        {/* Event Type Legend */}
        <div className="flex gap-4 flex-wrap bg-black/40 p-3 rounded-xl border border-white/5">
          {EVENT_TYPES.map(({ type, icon }) => (
            <div key={type} className="flex items-center gap-2 text-xs font-bold tracking-wider uppercase text-slate-300">
              <span className="text-base drop-shadow-md">{icon}</span>
              <span>{type}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Vertical Timeline Container */}
      <div className="flex-1 overflow-y-auto relative p-12 scroll-smooth">
        {/* Central Glowing Line */}
        <div className="absolute left-1/2 top-0 bottom-0 w-[3px] bg-gradient-to-b from-transparent via-violet-500/40 to-transparent -translate-x-1/2 shadow-[0_0_20px_rgba(139,92,246,0.3)] pointer-events-none" />

        <div className="max-w-5xl mx-auto space-y-24 relative pb-20">
          {EVENTS.length === 0 && (
            <div className="text-center text-slate-500 font-bold mt-20">No history available</div>
          )}

          {EVENTS.map((event, index) => {
            const isLeft = index % 2 === 0;
            const isHovered = hoveredEvent === event.id;

            return (
              <div 
                key={event.id} 
                className={`relative flex items-center w-full justify-between group transition-all duration-500 ${isHovered ? 'scale-[1.02]' : 'scale-100'}`}
                onMouseEnter={() => setHoveredEvent(event.id)}
                onMouseLeave={() => setHoveredEvent(null)}
              >
                {/* Connector Dot */}
                <div 
                  className={`absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-5 rounded-full border-4 border-slate-950 bg-gradient-to-r ${event.color} z-10 transition-all duration-300 ${isHovered ? 'scale-150 shadow-[0_0_30px_rgba(255,255,255,0.4)]' : 'scale-100 shadow-md'}`}
                />

                {/* Left Side Content */}
                <div className={`w-[45%] flex ${isLeft ? 'justify-end' : 'justify-start'}`}>
                  {isLeft && (
                    <TimelineCard event={event} isHovered={isHovered} />
                  )}
                  {!isLeft && (
                     <div className={`text-sm font-bold tracking-widest uppercase transition-colors duration-300 ${isHovered ? 'text-white' : 'text-slate-500'}`}>
                       {event.metadata.date}
                     </div>
                  )}
                </div>

                {/* Right Side Content */}
                <div className={`w-[45%] flex ${!isLeft ? 'justify-start' : 'justify-end'}`}>
                  {!isLeft && (
                    <TimelineCard event={event} isHovered={isHovered} />
                  )}
                  {isLeft && (
                    <div className={`text-sm font-bold tracking-widest uppercase transition-colors duration-300 ${isHovered ? 'text-white' : 'text-slate-500'}`}>
                      {event.metadata.date}
                    </div>
                  )}
                </div>

              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function TimelineCard({ event, isHovered }) {
  return (
    <div className={`relative w-full max-w-md p-6 rounded-2xl border backdrop-blur-md transition-all duration-500 ${event.bg} ${event.border} ${isHovered ? 'shadow-[0_0_40px_rgba(255,255,255,0.05)] bg-slate-800/80' : 'shadow-xl bg-slate-900/60'}`}>
      
      {/* Glow highlight */}
      <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${event.color} opacity-0 transition-opacity duration-500 ${isHovered ? 'opacity-10' : ''}`} pointerEvents="none" />

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${event.color} flex items-center justify-center text-xl shadow-lg`}>
              {event.icon}
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-wide truncate max-w-[200px]">{event.title}</h3>
              <p className={`text-xs font-semibold mt-0.5 uppercase tracking-widest bg-clip-text text-transparent bg-gradient-to-r ${event.color}`}>{event.type}</p>
            </div>
          </div>
        </div>

        <p className={`text-sm leading-relaxed font-medium transition-colors duration-300 mb-5 ${isHovered ? 'text-slate-200' : 'text-slate-400'}`}>
          {event.description}
        </p>

        <div className="grid grid-cols-2 gap-3 mt-4">
          <div className="bg-black/30 rounded-lg p-2.5 border border-white/5">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">Author</div>
            <div className="text-xs font-semibold text-slate-200 truncate">{event.metadata.author}</div>
          </div>
          <div className="bg-black/30 rounded-lg p-2.5 border border-white/5">
            <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">Commit Hash</div>
            <div className="text-xs font-mono text-slate-300 truncate">{event.metadata.hash}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
