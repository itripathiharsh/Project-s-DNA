import { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';

// Repository evolution data across years
const TIMELINE_DATA = {
  2020: {
    year: 2020,
    name: 'v0.1 - Initial Prototype',
    description: 'Basic folder structure',
    folders: [
      { id: 'src', name: 'src', x: -3, y: 2, color: 0x6366f1, files: 3, complexity: 0.2 },
      { id: 'tests', name: 'tests', x: 0, y: 2, color: 0x8b5cf6, files: 2, complexity: 0.1 },
      { id: 'docs', name: 'docs', x: 3, y: 2, color: 0x06b6d4, files: 1, complexity: 0 },
    ],
    dependencies: 5,
    totalFiles: 6,
    codeMetrics: { complexity: 2.1, maintainability: 78, testCoverage: 42 },
  },
  2021: {
    year: 2021,
    name: 'v1.0 - Feature Complete',
    description: 'Core features implemented',
    folders: [
      { id: 'src', name: 'src', x: -4, y: 2, color: 0x6366f1, files: 12, complexity: 0.35 },
      { id: 'backend', name: 'backend', x: -1, y: 2, color: 0xf59e0b, files: 8, complexity: 0.4 },
      { id: 'tests', name: 'tests', x: 2, y: 2, color: 0x8b5cf6, files: 15, complexity: 0.2 },
      { id: 'docs', name: 'docs', x: 5, y: 2, color: 0x06b6d4, files: 8, complexity: 0 },
      { id: 'config', name: 'config', x: 8, y: 2, color: 0x10b981, files: 4, complexity: 0.15 },
    ],
    dependencies: 18,
    totalFiles: 47,
    codeMetrics: { complexity: 4.2, maintainability: 72, testCoverage: 65 },
  },
  2022: {
    year: 2022,
    name: 'v2.0 - Scaled Architecture',
    description: 'Microservices & modularization',
    folders: [
      { id: 'frontend', name: 'frontend', x: -5, y: 3, color: 0xec4899, files: 24, complexity: 0.3 },
      { id: 'backend', name: 'backend', x: -2, y: 3, color: 0xf59e0b, files: 32, complexity: 0.5 },
      { id: 'api', name: 'api', x: 1, y: 3, color: 0x14b8a6, files: 16, complexity: 0.45 },
      { id: 'services', name: 'services', x: 4, y: 3, color: 0x06b6d4, files: 28, complexity: 0.55 },
      { id: 'tests', name: 'tests', x: 7, y: 3, color: 0x8b5cf6, files: 38, complexity: 0.25 },
      { id: 'infra', name: 'infra', x: 10, y: 3, color: 0x6b7280, files: 12, complexity: 0.4 },
    ],
    dependencies: 45,
    totalFiles: 150,
    codeMetrics: { complexity: 6.8, maintainability: 68, testCoverage: 78 },
  },
  2023: {
    year: 2023,
    name: 'v3.0 - Enterprise Ready',
    description: 'Advanced features & optimization',
    folders: [
      { id: 'frontend', name: 'frontend', x: -6, y: 2, color: 0xec4899, files: 45, complexity: 0.35 },
      { id: 'backend', name: 'backend', x: -3, y: 2, color: 0xf59e0b, files: 58, complexity: 0.55 },
      { id: 'api', name: 'api', x: 0, y: 2, color: 0x14b8a6, files: 32, complexity: 0.48 },
      { id: 'services', name: 'services', x: 3, y: 2, color: 0x06b6d4, files: 52, complexity: 0.60 },
      { id: 'workers', name: 'workers', x: 6, y: 2, color: 0xf97316, files: 18, complexity: 0.42 },
      { id: 'tests', name: 'tests', x: 9, y: 2, color: 0x8b5cf6, files: 68, complexity: 0.28 },
      { id: 'infra', name: 'infra', x: 12, y: 2, color: 0x6b7280, files: 24, complexity: 0.45 },
    ],
    dependencies: 78,
    totalFiles: 297,
    codeMetrics: { complexity: 8.9, maintainability: 65, testCoverage: 85 },
  },
  2024: {
    year: 2024,
    name: 'v4.0 - Intelligence Layer',
    description: 'AI-powered analysis & insights',
    folders: [
      { id: 'frontend', name: 'frontend', x: -7, y: 2, color: 0xec4899, files: 62, complexity: 0.38 },
      { id: 'backend', name: 'backend', x: -4, y: 2, color: 0xf59e0b, files: 85, complexity: 0.58 },
      { id: 'api', name: 'api', x: -1, y: 2, color: 0x14b8a6, files: 48, complexity: 0.50 },
      { id: 'services', name: 'services', x: 2, y: 2, color: 0x06b6d4, files: 74, complexity: 0.63 },
      { id: 'workers', name: 'workers', x: 5, y: 2, color: 0xf97316, files: 32, complexity: 0.45 },
      { id: 'ml', name: 'ml', x: 8, y: 2, color: 0xa855f7, files: 28, complexity: 0.70 },
      { id: 'tests', name: 'tests', x: 11, y: 2, color: 0x8b5cf6, files: 95, complexity: 0.30 },
      { id: 'infra', name: 'infra', x: 14, y: 2, color: 0x6b7280, files: 36, complexity: 0.48 },
    ],
    dependencies: 125,
    totalFiles: 460,
    codeMetrics: { complexity: 11.2, maintainability: 62, testCoverage: 88 },
  },
  2025: {
    year: 2025,
    name: 'v5.0 - Intelligence DNA',
    description: 'Full repository analysis platform',
    folders: [
      { id: 'frontend', name: 'frontend', x: -8, y: 2, color: 0xec4899, files: 78, complexity: 0.40 },
      { id: 'backend', name: 'backend', x: -5, y: 2, color: 0xf59e0b, files: 112, complexity: 0.62 },
      { id: 'api', name: 'api', x: -2, y: 2, color: 0x14b8a6, files: 64, complexity: 0.53 },
      { id: 'services', name: 'services', x: 1, y: 2, color: 0x06b6d4, files: 98, complexity: 0.67 },
      { id: 'workers', name: 'workers', x: 4, y: 2, color: 0xf97316, files: 45, complexity: 0.48 },
      { id: 'ml', name: 'ml', x: 7, y: 2, color: 0xa855f7, files: 52, complexity: 0.75 },
      { id: 'graph', name: 'graph', x: 10, y: 2, color: 0x8b4513, files: 38, complexity: 0.71 },
      { id: 'tests', name: 'tests', x: 13, y: 2, color: 0x8b5cf6, files: 128, complexity: 0.32 },
      { id: 'infra', name: 'infra', x: 16, y: 2, color: 0x6b7280, files: 48, complexity: 0.52 },
    ],
    dependencies: 185,
    totalFiles: 663,
    codeMetrics: { complexity: 13.8, maintainability: 58, testCoverage: 91 },
  },
};

const YEARS = Object.keys(TIMELINE_DATA).map(Number).sort();

function FolderNode({ folder, progress, isActive }) {
  const scale = 0.8 + folder.complexity * 0.6;
  const opacity = 0.3 + progress * 0.7;

  return (
    <div
      key={folder.id}
      className="absolute w-16 h-16 rounded-lg flex flex-col items-center justify-center cursor-pointer group transition-all duration-300 ease-out"
      style={{
        transform: isActive ? `translate(${folder.x * 30}px, ${folder.y * 30}px) scale(${scale * 1.1})` : `translate(${folder.x * 30}px, ${folder.y * 30}px) scale(${scale})`,
        opacity: isActive ? 1 : opacity,
        background: `linear-gradient(135deg, rgba(${(folder.color >> 16) & 255}, ${(folder.color >> 8) & 255}, ${folder.color & 255}, 0.3), rgba(${(folder.color >> 16) & 255}, ${(folder.color >> 8) & 255}, ${folder.color & 255}, 0.05))`,
        border: `2px solid rgba(${(folder.color >> 16) & 255}, ${(folder.color >> 8) & 255}, ${folder.color & 255}, ${opacity})`,
        boxShadow: `0 0 ${20 * opacity}px rgba(${(folder.color >> 16) & 255}, ${(folder.color >> 8) & 255}, ${folder.color & 255}, ${opacity * 0.5})`,
      }}
    >
      <span className="material-symbols-outlined text-xl" style={{ color: `rgb(${(folder.color >> 16) & 255}, ${(folder.color >> 8) & 255}, ${folder.color & 255})` }}>
        folder
      </span>
      <div className="text-xs font-bold text-white mt-1 text-center truncate w-full px-1">
        {folder.name}
      </div>

      {/* Hover tooltip */}
      <div className="absolute -bottom-12 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
        <div className="bg-slate-900/95 border border-slate-700 rounded px-2 py-1 text-xs">
          <div className="text-white font-bold">{folder.files} files</div>
          <div className="text-slate-400">Complexity: {(folder.complexity * 100).toFixed(0)}%</div>
        </div>
      </div>
    </div>
  );
}

function DependencyLine({ from, to, progress }) {
  const x1 = from.x * 30;
  const y1 = from.y * 30;
  const x2 = to.x * 30;
  const y2 = to.y * 30;

  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke="url(#dependencyGradient)"
      strokeWidth={2}
      opacity={progress * 0.6}
      strokeDasharray="5,5"
      className="pointer-events-none transition-opacity duration-300"
    />
  );
}

export default function TimeTravelVisualization() {
  const [currentYear, setCurrentYear] = useState(2025);
  const [isPlaying, setIsPlaying] = useState(false);
  const containerRef = useRef();
  const animationRef = useRef();

  const currentData = TIMELINE_DATA[currentYear];
  const progress = (currentYear - YEARS[0]) / (YEARS[YEARS.length - 1] - YEARS[0]);

  // Auto-play animation
  useEffect(() => {
    if (!isPlaying) return;

    let isActive = true;
    let frame = 0;
    const animate = () => {
      if (!isActive) return;
      frame += 1;
      const year = YEARS[Math.floor((frame / 120) % YEARS.length)];
      setCurrentYear(year);
      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);
    return () => {
      isActive = false;
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [isPlaying]);

  // Morphing effect: interpolate between years for smooth transitions
  const getPrevData = () => {
    const prevYearIdx = YEARS.indexOf(currentYear) - 1;
    return prevYearIdx >= 0 ? TIMELINE_DATA[YEARS[prevYearIdx]] : currentData;
  };

  const morphFolders = () => {
    const prev = getPrevData();
    const current = currentData;
    const t = 0.5; // interpolation factor (could be animated)

    return current.folders.map(folder => ({
      ...folder,
      opacity: Math.min(1, folder.files / (prev.totalFiles || 1)) * progress,
    }));
  };

  return (
    <div className="w-full h-full flex flex-col bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-slate-700/50 bg-slate-900/50 backdrop-blur space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">{currentData.name}</h2>
            <p className="text-sm text-slate-400 mt-1">{currentData.description} • {currentData.totalFiles} files</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="px-4 py-2 rounded-lg bg-violet-600/20 border border-violet-500/50 text-violet-300 hover:bg-violet-600/30 transition-all text-sm font-semibold"
            >
              {isPlaying ? 'Pause' : 'Play'} Evolution
            </button>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/30">
            <div className="text-xs text-slate-500 mb-1">Total Files</div>
            <div className="text-2xl font-bold text-emerald-400">{currentData.totalFiles}</div>
          </div>
          <div className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/30">
            <div className="text-xs text-slate-500 mb-1">Dependencies</div>
            <div className="text-2xl font-bold text-blue-400">{currentData.dependencies}</div>
          </div>
          <div className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/30">
            <div className="text-xs text-slate-500 mb-1">Avg Complexity</div>
            <div className="text-2xl font-bold text-orange-400">{currentData.codeMetrics.complexity.toFixed(1)}</div>
          </div>
          <div className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/30">
            <div className="text-xs text-slate-500 mb-1">Test Coverage</div>
            <div className="text-2xl font-bold text-purple-400">{currentData.codeMetrics.testCoverage}%</div>
          </div>
        </div>
      </div>

      {/* Main Visualization */}
      <div className="flex-1 relative overflow-hidden" ref={containerRef}>
        {/* Background grid */}
        <div className="absolute inset-0 opacity-5">
          <svg width="100%" height="100%" className="w-full h-full">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(147, 112, 221, 0.1)" strokeWidth="0.5" />
              </pattern>
              <linearGradient id="dependencyGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgba(147, 112, 221, 0.4)" />
                <stop offset="50%" stopColor="rgba(59, 130, 246, 0.6)" />
                <stop offset="100%" stopColor="rgba(168, 85, 247, 0.4)" />
              </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        {/* Folder Container */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="relative w-full h-full">
            {/* Dependency connections */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              <defs>
                <linearGradient id="dependencyGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="rgba(147, 112, 221, 0.3)" />
                  <stop offset="100%" stopColor="rgba(59, 130, 246, 0.3)" />
                </linearGradient>
              </defs>

              {/* Simple dependency lines */}
              {currentData.folders.length > 1 && (
                <>
                  {currentData.folders.slice(0, -1).map((folder, idx) => {
                    const nextFolder = currentData.folders[idx + 1];
                    return (
                      <DependencyLine
                        key={`dep-${idx}`}
                        from={folder}
                        to={nextFolder}
                        progress={progress}
                      />
                    );
                  })}
                </>
              )}
            </svg>

            {/* Folders */}
            <div className="relative w-full h-full">
              {morphFolders().map(folder => (
                <FolderNode
                  key={folder.id}
                  folder={folder}
                  progress={progress}
                  isActive={false}
                />
              ))}
            </div>

            {/* Center title */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center animate-pulse">
                <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-cyan-400 to-purple-400">
                  {currentYear}
                </div>
                <div className="text-sm text-slate-400 mt-2">Repository Evolution</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline Slider */}
      <div className="p-6 border-t border-slate-700/50 bg-slate-900/50 backdrop-blur space-y-6">
        {/* Year selector */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-bold text-white uppercase tracking-widest">Timeline</label>
            <div className="text-xs text-slate-400">
              {YEARS[0]} → {YEARS[YEARS.length - 1]}
            </div>
          </div>

          {/* Slider */}
          <input
            type="range"
            min={YEARS[0]}
            max={YEARS[YEARS.length - 1]}
            value={currentYear}
            onChange={(e) => {
              setIsPlaying(false);
              setCurrentYear(Number(e.target.value));
            }}
            className="w-full h-2 bg-gradient-to-r from-slate-700 to-slate-600 rounded-lg appearance-none cursor-pointer slider transition-all"
            style={{
              background: `linear-gradient(to right, 
                rgb(147, 112, 221) 0%, 
                rgb(59, 130, 246) 25%, 
                rgb(34, 197, 94) 50%, 
                rgb(249, 115, 22) 75%, 
                rgb(168, 85, 247) 100%)`,
            }}
          />

          {/* Year markers */}
          <div className="flex justify-between mt-2">
            {YEARS.map(year => (
              <button
                key={year}
                onClick={() => {
                  setIsPlaying(false);
                  setCurrentYear(year);
                }}
                className={`text-xs font-semibold px-3 py-1 rounded transition-all ${
                  currentYear === year
                    ? 'bg-violet-600/30 text-violet-300 border border-violet-500/50'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {year}
              </button>
            ))}
          </div>
        </div>

        {/* Evolution metrics */}
        <div className="space-y-2">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">Growth Metrics</div>
          <div className="grid grid-cols-2 gap-4">
            {/* Files growth */}
            <div className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/30">
              <div className="text-xs text-slate-500 mb-2">Files Growth</div>
              <div className="flex items-end gap-1 h-8">
                {YEARS.map(year => {
                  const data = TIMELINE_DATA[year];
                  const maxFiles = Math.max(...YEARS.map(y => TIMELINE_DATA[y].totalFiles));
                  const height = (data.totalFiles / maxFiles) * 100;
                  return (
                    <div
                      key={year}
                      className={`flex-1 rounded-t transition-all duration-300 ${
                        year === currentYear ? 'bg-emerald-500' : 'bg-emerald-500/30'
                      }`}
                      style={{ height: `${height}%`, minHeight: '2px' }}
                      title={`${year}: ${data.totalFiles} files`}
                    />
                  );
                })}
              </div>
            </div>

            {/* Complexity growth */}
            <div className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/30">
              <div className="text-xs text-slate-500 mb-2">Complexity Growth</div>
              <div className="flex items-end gap-1 h-8">
                {YEARS.map(year => {
                  const data = TIMELINE_DATA[year];
                  const maxComplexity = Math.max(...YEARS.map(y => TIMELINE_DATA[y].codeMetrics.complexity));
                  const height = (data.codeMetrics.complexity / maxComplexity) * 100;
                  return (
                    <div
                      key={year}
                      className={`flex-1 rounded-t transition-all duration-300 ${
                        year === currentYear ? 'bg-orange-500' : 'bg-orange-500/30'
                      }`}
                      style={{ height: `${height}%`, minHeight: '2px' }}
                      title={`${year}: ${data.codeMetrics.complexity.toFixed(1)} complexity`}
                    />
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Growth indicators */}
        <div className="grid grid-cols-3 gap-3 text-xs">
          <div className="bg-slate-800/30 rounded p-2 border border-slate-700/30 text-center">
            <div className="text-slate-400 mb-1">Files Added</div>
            <div className="text-emerald-400 font-bold">
              +{currentData.totalFiles - (getPrevData().totalFiles || 0)}
            </div>
          </div>
          <div className="bg-slate-800/30 rounded p-2 border border-slate-700/30 text-center">
            <div className="text-slate-400 mb-1">Dependencies</div>
            <div className="text-blue-400 font-bold">
              +{currentData.dependencies - (getPrevData().dependencies || 0)}
            </div>
          </div>
          <div className="bg-slate-800/30 rounded p-2 border border-slate-700/30 text-center">
            <div className="text-slate-400 mb-1">Test Coverage</div>
            <div className="text-purple-400 font-bold">
              +{currentData.codeMetrics.testCoverage - (getPrevData().codeMetrics.testCoverage || 0)}%
            </div>
          </div>
        </div>
      </div>

      {/* CSS for custom slider */}
      <style>{`
        input[type="range"]::-webkit-slider-thumb {
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: linear-gradient(135deg, rgb(147, 112, 221), rgb(168, 85, 247));
          cursor: pointer;
          box-shadow: 0 0 10px rgba(147, 112, 221, 0.8);
          border: 2px solid rgba(255, 255, 255, 0.3);
        }
        input[type="range"]::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: linear-gradient(135deg, rgb(147, 112, 221), rgb(168, 85, 247));
          cursor: pointer;
          box-shadow: 0 0 10px rgba(147, 112, 221, 0.8);
          border: 2px solid rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </div>
  );
}
