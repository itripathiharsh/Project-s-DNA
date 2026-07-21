import { useState, useEffect, useRef } from 'react';

const SCREENS = [
  {
    id: 'home',
    label: 'Home',
    color: 'from-blue-600 to-blue-700',
    description: 'Repository Dashboard',
    mockupContent: () => (
      <div className="space-y-4 p-6">
        <div className="h-8 bg-blue-400/30 rounded w-1/3"></div>
        <div className="space-y-2">
          <div className="h-3 bg-blue-400/20 rounded w-full"></div>
          <div className="h-3 bg-blue-400/20 rounded w-5/6"></div>
        </div>
        <div className="grid grid-cols-2 gap-4 pt-4">
          <div className="h-16 bg-blue-500/30 rounded"></div>
          <div className="h-16 bg-blue-500/30 rounded"></div>
        </div>
      </div>
    ),
  },
  {
    id: 'search',
    label: 'Search',
    color: 'from-purple-600 to-purple-700',
    description: 'Intelligent Code Search',
    mockupContent: () => (
      <div className="space-y-4 p-6">
        <div className="h-10 bg-purple-400/30 rounded-full"></div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-12 bg-purple-500/20 rounded"></div>
          ))}
        </div>
      </div>
    ),
  },
  {
    id: 'repository',
    label: 'Repository',
    color: 'from-pink-600 to-pink-700',
    description: 'File Structure',
    mockupContent: () => (
      <div className="space-y-3 p-6">
        {['src/', 'components/', 'pages/'].map((item, i) => (
          <div key={i} className="flex gap-2 items-center">
            <div className="h-4 w-4 bg-pink-400/40 rounded"></div>
            <div className="h-3 bg-pink-400/30 rounded w-32"></div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'analysis',
    label: 'Analysis',
    color: 'from-cyan-600 to-cyan-700',
    description: 'Code Metrics',
    mockupContent: () => (
      <div className="space-y-4 p-6">
        <div className="h-20 bg-cyan-500/20 rounded-lg"></div>
        <div className="grid grid-cols-3 gap-2">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-8 bg-cyan-400/20 rounded"></div>
          ))}
        </div>
      </div>
    ),
  },
  {
    id: 'insights',
    label: 'Insights',
    color: 'from-green-600 to-green-700',
    description: 'AI Recommendations',
    mockupContent: () => (
      <div className="space-y-4 p-6">
        <div className="h-6 bg-green-400/30 rounded w-3/4"></div>
        <div className="space-y-2">
          <div className="h-2 bg-green-400/20 rounded w-full"></div>
          <div className="h-2 bg-green-400/20 rounded w-4/5"></div>
        </div>
      </div>
    ),
  },
  {
    id: 'export',
    label: 'Export',
    color: 'from-orange-600 to-orange-700',
    description: 'Download Reports',
    mockupContent: () => (
      <div className="space-y-4 p-6">
        <div className="h-10 bg-orange-400/30 rounded-lg text-center pt-2 text-orange-200 font-semibold">
          Export
        </div>
        <div className="space-y-2">
          <div className="h-3 bg-orange-400/20 rounded w-full"></div>
          <div className="h-3 bg-orange-400/20 rounded w-3/4"></div>
        </div>
      </div>
    ),
  },
];

export default function UserJourneyVisualization() {
  const [currentScreenIdx, setCurrentScreenIdx] = useState(0);
  const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 });
  const [clicks, setClicks] = useState([]);
  const [isAnimating, setIsAnimating] = useState(true);
  const containerRef = useRef();

  // Animate through screens
  useEffect(() => {
    if (!isAnimating) return;
    const timer = setInterval(() => {
      setCurrentScreenIdx(prev => (prev + 1) % SCREENS.length);
    }, 3000);
    return () => clearInterval(timer);
  }, [isAnimating]);

  const cursorPosRef = useRef({ x: 0, y: 0 });

  // Animate cursor position
  useEffect(() => {
    if (!isAnimating || !containerRef.current) return;
    
    let frame;
    let isActive = true;
    const animate = () => {
      if (!isActive) return;
      const container = containerRef.current;
      if (!container) return;
      
      const centerX = container.offsetWidth / 2;
      const centerY = container.offsetHeight / 2;
      
      // Follow a smooth path around the screen
      const time = Date.now() / 3000;
      const screen = SCREENS[currentScreenIdx];
      const screenContainer = container.querySelector(`[data-screen="${screen.id}"]`);
      
      if (screenContainer) {
        const rect = screenContainer.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        
        // Random movement within screen
        const offsetX = Math.sin(time * 2) * (rect.width * 0.3);
        const offsetY = Math.cos(time * 2.3) * (rect.height * 0.3);
        
        const newX = rect.left - containerRect.left + rect.width / 2 + offsetX;
        const newY = rect.top - containerRect.top + rect.height / 2 + offsetY;
        
        cursorPosRef.current = { x: newX, y: newY };
        setCursorPos({ x: newX, y: newY });
      }
      
      frame = requestAnimationFrame(animate);
    };
    
    frame = requestAnimationFrame(animate);
    return () => {
      isActive = false;
      cancelAnimationFrame(frame);
    };
  }, [currentScreenIdx, isAnimating]);

  // Create ripple effect on click
  useEffect(() => {
    if (!isAnimating) return;
    
    const timer = setInterval(() => {
      setClicks(prev => [
        ...prev,
        {
          id: Date.now(),
          x: cursorPosRef.current.x,
          y: cursorPosRef.current.y,
        }
      ]);
    }, 2000);
    
    return () => clearInterval(timer);
  }, [isAnimating]);

  // Clean up old ripples
  useEffect(() => {
    const timer = setInterval(() => {
      setClicks(prev => prev.filter(click => Date.now() - click.id < 1000));
    }, 100);
    return () => clearInterval(timer);
  }, []);

  const currentScreen = SCREENS[currentScreenIdx];

  return (
    <div className="w-full h-full flex flex-col bg-slate-950">
      <div className="flex-1 p-8 flex gap-8 overflow-hidden">
        {/* Flow Diagram */}
        <div className="flex flex-col justify-center items-center w-32 gap-6 flex-shrink-0">
          {SCREENS.map((screen, idx) => (
            <div key={screen.id} className="flex flex-col items-center gap-2">
              <button
                onClick={() => {
                  setCurrentScreenIdx(idx);
                  setIsAnimating(false);
                }}
                className={`w-16 h-16 rounded-lg transition-all duration-300 ${
                  idx === currentScreenIdx
                    ? 'bg-gradient-to-br ' + screen.color + ' shadow-lg scale-110'
                    : 'bg-slate-700/50 hover:bg-slate-600/50'
                }`}
              >
                <div className="flex items-center justify-center h-full text-sm font-bold text-white">
                  {screen.label.charAt(0)}
                </div>
              </button>
              {idx < SCREENS.length - 1 && (
                <div className="h-6 w-0.5 bg-gradient-to-b from-violet-500 to-transparent"></div>
              )}
            </div>
          ))}
        </div>

        {/* Main Mockup Area */}
        <div
          ref={containerRef}
          className="flex-1 relative bg-slate-900 rounded-2xl shadow-2xl overflow-hidden border border-slate-700/50"
        >
          {/* Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-slate-800 via-slate-900 to-black"></div>

          {/* Screen Content */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              key={currentScreen.id}
              data-screen={currentScreen.id}
              className="w-full h-full animate-in fade-in slide-in-from-right-10 duration-500"
            >
              <div className={`w-full h-full bg-gradient-to-br ${currentScreen.color} relative overflow-hidden`}>
                {/* Top bar */}
                <div className="absolute top-0 left-0 right-0 h-12 bg-black/20 border-b border-white/10 flex items-center px-4">
                  <div className="text-white font-semibold text-sm">{currentScreen.label}</div>
                  <div className="ml-auto text-white/50 text-xs">{currentScreen.description}</div>
                </div>

                {/* Content */}
                <div className="absolute top-12 left-0 right-0 bottom-0 overflow-hidden">
                  {currentScreen.mockupContent()}
                </div>

                {/* Animated background elements */}
                <div className="absolute inset-0 opacity-10">
                  <div className="absolute w-96 h-96 rounded-full bg-white blur-3xl top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Animated Cursor */}
          <div
            className="absolute w-2 h-2 bg-white rounded-full shadow-lg z-50 pointer-events-none"
            style={{
              left: `${cursorPos.x}px`,
              top: `${cursorPos.y}px`,
              transform: 'translate(-50%, -50%)',
              transition: 'all 0.15s ease-out',
              boxShadow: '0 0 12px rgba(255,255,255,0.8), 0 0 24px rgba(147,112,221,0.4)',
            }}
          >
            {/* Cursor glow */}
            <div className="absolute inset-0 w-2 h-2 rounded-full bg-white/30 blur-sm animate-pulse"></div>
          </div>

          {/* Cursor trail */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 40 }}>
            <defs>
              <linearGradient id="trail-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgba(147, 112, 221, 0.5)" />
                <stop offset="100%" stopColor="rgba(147, 112, 221, 0)" />
              </linearGradient>
            </defs>
          </svg>

          {/* Ripple Effects */}
          {clicks.map(click => {
            const progress = ((Date.now() - click.id) / 1000);
            const radius = progress * 100;
            const opacity = Math.max(0, 1 - progress);
            
            return (
              <div
                key={click.id}
                className="absolute rounded-full border-2 border-white pointer-events-none"
                style={{
                  left: `${click.x}px`,
                  top: `${click.y}px`,
                  width: `${radius * 2}px`,
                  height: `${radius * 2}px`,
                  transform: 'translate(-50%, -50%)',
                  opacity: opacity,
                  zIndex: 30,
                  boxShadow: `0 0 12px rgba(255,255,255,${opacity * 0.5})`,
                }}
              ></div>
            );
          })}
        </div>
      </div>

      {/* Controls and Info */}
      <div className="p-6 border-t border-slate-700/50 bg-slate-900/50 backdrop-blur">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h3 className="text-lg font-bold text-white">{currentScreen.label}</h3>
            <p className="text-sm text-slate-400">{currentScreen.description}</p>
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => setIsAnimating(!isAnimating)}
              className="px-4 py-2 rounded-lg bg-violet-600/20 border border-violet-500/50 text-violet-300 hover:bg-violet-600/30 transition-all text-sm font-semibold"
            >
              {isAnimating ? 'Pause' : 'Play'}
            </button>
            
            <div className="flex gap-2">
              {SCREENS.map((screen, idx) => (
                <button
                  key={screen.id}
                  onClick={() => {
                    setCurrentScreenIdx(idx);
                    setIsAnimating(false);
                  }}
                  className={`w-2 h-2 rounded-full transition-all ${
                    idx === currentScreenIdx ? 'bg-violet-400 w-6' : 'bg-slate-600 hover:bg-slate-500'
                  }`}
                ></button>
              ))}
            </div>
          </div>
        </div>

        {/* Journey Path Indicator */}
        <div className="mt-4 flex items-center gap-2">
          {SCREENS.map((screen, idx) => (
            <div key={screen.id} className="flex items-center gap-2">
              <div className={`text-xs font-semibold px-2 py-1 rounded ${
                idx === currentScreenIdx
                  ? 'bg-violet-600/30 text-violet-300 border border-violet-500/50'
                  : 'bg-slate-700/50 text-slate-400'
              }`}>
                {screen.label}
              </div>
              {idx < SCREENS.length - 1 && (
                <div className="text-slate-600">→</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
