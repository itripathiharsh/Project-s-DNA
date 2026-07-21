import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../store/analysis';
import PageHeader from '../components/PageHeader';
import { 
  getAdvancedScores,
  getAdvancedGithubMetrics,
  getAdvancedCodeSmells,
  getAdvancedSecurityReport,
  getAdvancedPerformanceHotpaths,
  postAdvancedAction,
  postAdvancedChat
} from '../services/api';
import Heatmaps from '../components/Heatmaps';
import Benchmarking from '../components/Benchmarking';
import BranchDiff from '../components/BranchDiff';

export default function Dashboard() {
  const { data: analysisData, repoPath, loading: analysisLoading, reset, activeBranch, setActiveBranch, selectedBranches } = useAnalysis();
  const navigate = useNavigate();

  // Tabs state
  const [activeTab, setActiveTab] = useState('scores'); // scores, ai, github, audits, heatmaps

  // API states
  const [scoresData, setScoresData] = useState(null);
  const [githubData, setGithubData] = useState(null);
  const [smellsData, setSmellsData] = useState(null);
  const [securityData, setSecurityData] = useState(null);
  const [perfData, setPerfData] = useState(null);

  // Loading/Error states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Drill-down Modal State
  const [selectedScore, setSelectedScore] = useState(null);

  // Chat State
  const [chatPrompt, setChatPrompt] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', text: 'Hello! I am your AI repository assistant. Ask me about refactoring strategies, structural risks, or code smells.' }
  ]);
  const [chatLoading, setChatLoading] = useState(false);

  // AI Action Console state
  const [actionConsole, setActionConsole] = useState(null); // { type, message, details }
  const [actionLoading, setActionLoading] = useState(false);

  // Fetch all advanced data
  const fetchAdvancedData = async () => {
    if (!analysisData) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const timeout = (ms) => new Promise((_, r) => setTimeout(() => r(new Error("timeout")), ms));
      const [scores, github, smells, security, perf] = await Promise.all([
        Promise.race([getAdvancedScores(), timeout(15000)]),
        Promise.race([getAdvancedGithubMetrics(), timeout(15000)]),
        Promise.race([getAdvancedCodeSmells(), timeout(15000)]),
        Promise.race([getAdvancedSecurityReport(), timeout(15000)]),
        Promise.race([getAdvancedPerformanceHotpaths(), timeout(15000)])
      ]);
      setScoresData(scores);
      setGithubData(github);
      setSmellsData(smells);
      setSecurityData(security);
      setPerfData(perf);
    } catch (err) {
      console.error("Error fetching advanced dashboard metrics:", err);
      setError("Failed to compile advanced repository insights. Please ensure onboarding analysis was fully completed.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdvancedData();
  }, [analysisData, activeBranch]);

  // Execute AI action
  const handleAiAction = async (actionType) => {
    setActionLoading(true);
    setActionConsole(null);
    try {
      const res = await postAdvancedAction(actionType);
      setActionConsole({
        type: actionType,
        message: res.message,
        details: res.findings || res.patch || res
      });
    } catch (err) {
      setActionConsole({
        type: actionType,
        message: 'Action failed',
        details: String(err)
      });
    } finally {
      setActionLoading(false);
    }
  };

  // Submit AI chat
  const handleChatSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!chatPrompt.trim()) return;

    const userMsg = chatPrompt;
    setChatHistory(prev => [...prev, { role: 'user', text: userMsg }]);
    setChatPrompt('');
    setChatLoading(true);

    try {
      const res = await postAdvancedChat(userMsg);
      setChatHistory(prev => [...prev, { role: 'assistant', text: res.reply }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', text: `Failed to receive grounded reasoning: ${err.message}` }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Render score badge classes
  const getTrendBadge = (trend) => {
    if (trend === 'improving') return { label: 'Improving', class: 'bg-signal-emerald/10 text-signal-emerald border border-signal-emerald/20', icon: 'trending_up' };
    if (trend === 'declining') return { label: 'Declining', class: 'bg-signal-rose/10 text-signal-rose border border-signal-rose/20', icon: 'trending_down' };
    return { label: 'Stable', class: 'bg-signal-amber/10 text-signal-amber border border-signal-amber/20', icon: 'trending_flat' };
  };

  const getScoreColorClass = (score) => {
    if (score >= 85) return 'text-signal-emerald';
    if (score >= 70) return 'text-signal-cyan';
    if (score >= 50) return 'text-signal-amber';
    return 'text-signal-rose';
  };

  if (analysisLoading) {
    return (
      <>
        <PageHeader title="Executive Dashboard" subtitle="Running analytical pipelines..." />
        <div className="flex-1 flex flex-col items-center justify-center gap-6 p-12">
          <div className="relative">
            <div className="w-16 h-16 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
            <div className="absolute inset-0 w-16 h-16 border border-transparent border-b-signal-cyan rounded-full animate-pulse" />
          </div>
          <div className="flex flex-col items-center gap-1.5 text-center">
            <p className="text-sm font-semibold text-on-surface">Extracting AST & Git history</p>
            <p className="text-xs text-text-muted">Analyzing structural dependency graph...</p>
          </div>
        </div>
      </>
    );
  }

  if (!analysisData) {
    return (
      <>
        <PageHeader title="Executive Dashboard" />
        <div className="flex-1 flex flex-col items-center justify-center gap-6 px-6 py-12 text-center max-w-2xl mx-auto">
          <div className="relative">
            <div className="absolute inset-0 bg-primary/10 blur-2xl rounded-full scale-150 animate-pulse" />
            <div className="relative w-16 h-16 rounded-2xl bg-surface-container-high border border-border-subtle flex items-center justify-center shadow-lg">
              <span className="material-symbols-outlined text-[32px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>analytics</span>
            </div>
          </div>
          <div className="space-y-2">
            <h2 className="font-extrabold text-xl text-on-surface tracking-tight">No codebase analysis found</h2>
            <p className="text-on-surface-variant text-xs max-w-md mx-auto leading-relaxed">
              Connect and scan a repository path to generate comprehensive architectural maps, identify structural risks, and extract developer expertise metadata.
            </p>
          </div>
          <button onClick={() => { reset(); navigate('/onboarding'); }} className="btn-primary py-2.5 px-6 rounded-lg font-bold flex items-center gap-2 shadow-[0_0_20px_rgba(157,78,221,0.25)] hover:scale-[1.02] active:scale-[0.98] transition-all">
            <span className="material-symbols-outlined text-[16px]">add</span> New Analysis
          </button>
        </div>
      </>
    );
  }

  const overallDnaScore = scoresData?.dna_score ?? 82.5;

  return (
    <>
      <PageHeader
        title="Executive Intelligence Center"
        subtitle={repoPath || "No active repo"}
        actions={
          <div className="flex items-center gap-3">
            {selectedBranches && selectedBranches.length > 1 && (
              <div className="flex items-center bg-surface-container-high rounded px-3 py-1.5 border border-border-subtle">
                <span className="material-symbols-outlined text-[16px] text-text-muted mr-2">call_split</span>
                <select 
                  value={activeBranch}
                  onChange={(e) => setActiveBranch(e.target.value)}
                  className="bg-transparent text-sm text-on-surface font-semibold outline-none cursor-pointer"
                >
                  {selectedBranches.map(b => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>
            )}
            <button onClick={() => navigate('/graph')} className="btn-secondary px-4 py-2 flex items-center gap-1.5 hover:scale-[1.02] transition-all text-xs font-semibold">
              <span className="material-symbols-outlined text-[15px]">account_tree</span> Workspace Graph
            </button>
            <button onClick={() => navigate('/onboarding')} className="btn-primary px-4 py-2 flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all text-xs font-semibold">
              <span className="material-symbols-outlined text-[15px]">add</span> New Scan
            </button>
          </div>
        }
      />

      <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto w-full flex-1 overflow-hidden">
        {/* Tab Headers */}
        <div className="flex border-b border-border-subtle/50 pb-px">
          {[
            { id: 'scores', label: 'Repository Analysis Center', icon: 'dashboard' },
            { id: 'ai', label: 'AI Repository Assistant', icon: 'smart_toy' },
            { id: 'github', label: 'GitHub Intelligence', icon: 'query_stats' },
            { id: 'audits', label: 'Code & Security Audits', icon: 'security' },
            { id: 'heatmaps', label: 'Intelligence Heatmaps', icon: 'grid_view' },
            { id: 'benchmarking', label: 'Branch Benchmarks', icon: 'bar_chart' },
            { id: 'diff', label: 'Branch Compare', icon: 'difference' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-5 py-3 border-b-2 font-semibold text-xs transition-all -mb-px ${
                activeTab === tab.id
                  ? 'border-primary text-primary font-bold bg-primary/5 rounded-t-lg'
                  : 'border-transparent text-on-surface-variant hover:text-on-surface hover:bg-surface-container/20'
              }`}
            >
              <span className="material-symbols-outlined text-[17px]">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content Panels */}
        {loading && activeTab !== 'ai' ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-3 py-24">
            <div className="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
            <span className="text-xs text-text-muted">Loading repository analytics...</span>
          </div>
        ) : (
          <div className="flex-1 flex flex-col gap-6">
            
            {/* 1. Scores Center Tab */}
            {activeTab === 'scores' && scoresData && (
              <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 items-start">
                
                {/* Left DNA Summary Card */}
                <div className="card-base xl:col-span-1 flex flex-col gap-5 p-5 bg-gradient-to-b from-surface-container-high/60 to-surface-container/30 border border-border-subtle">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>science</span>
                    <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">DNA Intelligence</h3>
                  </div>

                  <div className="flex flex-col items-center py-4 relative">
                    {/* Ring score */}
                    <div className="relative w-36 h-36 flex items-center justify-center">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle cx="72" cy="72" r="62" stroke="rgba(255,255,255,0.03)" strokeWidth="8" fill="transparent" />
                        <circle 
                          cx="72" 
                          cy="72" 
                          r="62" 
                          stroke="url(#dashboardGlow)" 
                          strokeWidth="8" 
                          fill="transparent" 
                          strokeDasharray="389.5" 
                          strokeDashoffset={389.5 - (389.5 * overallDnaScore) / 100}
                          strokeLinecap="round"
                        />
                        <defs>
                          <linearGradient id="dashboardGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#9d4edd" />
                            <stop offset="50%" stopColor="#00bbf9" />
                            <stop offset="100%" stopColor="#00f5d4" />
                          </linearGradient>
                        </defs>
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-3xl font-extrabold text-on-surface tracking-tighter">{overallDnaScore}%</span>
                        <span className="text-[9px] text-text-muted uppercase tracking-widest font-bold mt-0.5">DNA score</span>
                      </div>
                    </div>
                  </div>

                  <div className="text-left space-y-3 border-t border-border-subtle/50 pt-4">
                    <h4 className="text-xs font-bold text-on-surface">Executive Summary</h4>
                    <p className="text-xs text-on-surface-variant leading-relaxed">
                      {scoresData.ai_summary}
                    </p>
                  </div>
                </div>

                {/* 12 Detailed Scores Grid */}
                <div className="xl:col-span-3 flex flex-col gap-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(scoresData.scores || {}).map(([key, item]) => {
                      const trend = getTrendBadge(item.trend);
                      const scoreColor = getScoreColorClass(item.score);
                      return (
                        <div 
                          key={key}
                          onClick={() => setSelectedScore({ key, ...item })}
                          className="card-base group hover:border-primary/40 hover:bg-surface-container-high/40 cursor-pointer p-4 flex flex-col justify-between transition-all duration-300 relative overflow-hidden"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex flex-col min-w-0">
                              <span className="font-bold text-xs text-on-surface truncate group-hover:text-primary transition-colors">
                                {item.name.replace(" Score", "")}
                              </span>
                              <span className="text-[10px] text-text-muted mt-0.5 truncate">{item.why}</span>
                            </div>
                            <span className={`text-lg font-black font-code-sm ${scoreColor}`}>
                              {item.score}%
                            </span>
                          </div>

                          <div className="flex items-center justify-between mt-3 pt-3 border-t border-border-subtle/30">
                            <span className={`badge text-[9px] flex items-center gap-1 font-semibold ${trend.class}`}>
                              <span className="material-symbols-outlined text-[11px]">{trend.icon}</span>
                              {trend.label}
                            </span>
                            <span className="text-[9px] text-primary hover:underline font-bold flex items-center gap-0.5">
                              Details <span className="material-symbols-outlined text-[10px]">open_in_new</span>
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

              </div>
            )}

            {/* 2. AI Assistant Tab */}
            {activeTab === 'ai' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start flex-1 min-h-[500px]">
                
                {/* Prompt Panel */}
                <div className="card-base p-5 flex flex-col gap-4 text-left">
                  <h3 className="font-label-caps text-label-caps text-text-muted border-b border-border-subtle pb-2 flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[16px] text-primary">terminal</span> Quick AI Actions
                  </h3>
                  <div className="flex flex-col gap-2">
                    <button 
                      onClick={() => handleAiAction('audit')}
                      disabled={actionLoading}
                      className="w-full btn-secondary text-left text-xs py-2 px-3 justify-start flex items-center gap-2 hover:bg-surface-container-high"
                    >
                      <span className="material-symbols-outlined text-[15px] text-signal-cyan">find_in_page</span>
                      One-Click Codebase Audit
                    </button>
                    <button 
                      onClick={() => handleAiAction('security')}
                      disabled={actionLoading}
                      className="w-full btn-secondary text-left text-xs py-2 px-3 justify-start flex items-center gap-2 hover:bg-surface-container-high"
                    >
                      <span className="material-symbols-outlined text-[15px] text-signal-rose">gavel</span>
                      Security Flaw Audit
                    </button>
                    <button 
                      onClick={() => handleAiAction('refactor')}
                      disabled={actionLoading}
                      className="w-full btn-secondary text-left text-xs py-2 px-3 justify-start flex items-center gap-2 hover:bg-surface-container-high"
                    >
                      <span className="material-symbols-outlined text-[15px] text-signal-emerald">construction</span>
                      Generate Refactor Patch
                    </button>
                  </div>

                  <h3 className="font-label-caps text-label-caps text-text-muted border-b border-border-subtle pb-2 flex items-center gap-1.5 mt-4">
                    <span className="material-symbols-outlined text-[16px] text-primary">psychology</span> Suggested Prompts
                  </h3>
                  <div className="flex flex-col gap-2">
                    {[
                      "Find cyclomatic complexity hotspots in backend modules.",
                      "List class coupling risks.",
                      "How can I resolve circular cycles?",
                      "Audit memory limits in SQLite store."
                    ].map((p, idx) => (
                      <button
                        key={p}
                        onClick={() => { setChatPrompt(p); }}
                        className="text-left text-xs text-on-surface-variant hover:text-on-surface hover:bg-surface-container/60 p-2 rounded border border-border-subtle transition-all"
                      >
                        "{p}"
                      </button>
                    ))}
                  </div>
                </div>

                {/* Chat Panel */}
                <div className="card-base lg:col-span-2 flex flex-col bg-[#0b0b10] min-h-[500px] border border-border-subtle relative overflow-hidden">
                  
                  {/* Chat messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[360px] min-h-[300px]">
                    {chatHistory.map((msg, i) => (
                      <div 
                        key={i} 
                        className={`flex gap-3 text-left ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        {msg.role !== 'user' && (
                          <div className="w-8 h-8 rounded-lg bg-primary/15 border border-primary/30 flex items-center justify-center flex-shrink-0">
                            <span className="material-symbols-outlined text-[16px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
                          </div>
                        )}
                        <div 
                          className={`p-3 rounded-lg max-w-[85%] text-xs leading-relaxed ${
                            msg.role === 'user' 
                              ? 'bg-primary text-on-primary font-medium' 
                              : 'bg-surface-container border border-border-subtle text-on-surface-variant'
                          }`}
                        >
                          {/* Markdown simple parser */}
                          <div className="whitespace-pre-wrap font-body-sm">
                            {msg.text}
                          </div>
                        </div>
                      </div>
                    ))}
                    {chatLoading && (
                      <div className="flex gap-3 text-left">
                        <div className="w-8 h-8 rounded-lg bg-primary/15 border border-primary/30 flex items-center justify-center flex-shrink-0 animate-pulse">
                          <span className="material-symbols-outlined text-[16px] text-primary">psychology</span>
                        </div>
                        <div className="p-3 bg-surface-container border border-border-subtle rounded-lg text-xs flex items-center gap-2">
                          <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" />
                          <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.2s]" />
                          <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.4s]" />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Input Form */}
                  <form onSubmit={handleChatSubmit} className="p-4 border-t border-border-subtle/50 flex gap-2.5 bg-surface-container-low/40">
                    <input
                      type="text"
                      placeholder="Ask the AI repository assistant..."
                      value={chatPrompt}
                      onChange={(e) => setChatPrompt(e.target.value)}
                      className="input-base flex-1 text-xs py-2 pr-3 pl-3"
                    />
                    <button 
                      type="submit" 
                      disabled={chatLoading}
                      className="btn-primary py-2 px-4 rounded-lg flex items-center gap-1 text-xs font-bold"
                    >
                      Send <span className="material-symbols-outlined text-[14px]">send</span>
                    </button>
                  </form>

                  {/* Dynamic Action Console Output */}
                  {actionConsole && (
                    <div className="absolute inset-0 bg-[#08080c]/98 backdrop-blur z-20 p-5 flex flex-col text-left">
                      <div className="flex items-center justify-between border-b border-border-subtle pb-2 mb-4">
                        <h4 className="font-bold text-xs text-signal-cyan flex items-center gap-1.5 uppercase">
                          <span className="material-symbols-outlined text-[16px]">terminal</span>
                          AI Action Output: {actionConsole.type}
                        </h4>
                        <button 
                          onClick={() => setActionConsole(null)}
                          className="text-text-muted hover:text-on-surface text-xs font-bold"
                        >
                          Close Console
                        </button>
                      </div>
                      <div className="flex-1 bg-[#050508] border border-border-subtle rounded p-3 font-code-sm text-xs overflow-y-auto space-y-2 text-on-surface">
                        <p className="text-signal-emerald font-semibold">{actionConsole.message}</p>
                        <pre className="text-text-muted text-[11px] leading-relaxed whitespace-pre-wrap">
                          {typeof actionConsole.details === 'object' 
                            ? JSON.stringify(actionConsole.details, null, 2) 
                            : actionConsole.details
                          }</pre>
                      </div>
                    </div>
                  )}

                  {actionLoading && (
                    <div className="absolute inset-0 bg-[#08080c]/80 backdrop-blur z-20 flex flex-col items-center justify-center gap-3">
                      <div className="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
                      <span className="text-xs text-on-surface-variant font-bold uppercase tracking-wider">AI Agent Auditing Repository...</span>
                    </div>
                  )}
                </div>

              </div>
            )}

            {/* 3. GitHub Intelligence Tab */}
            {activeTab === 'github' && githubData && (
              <>
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
                  {/* Contributor contributions bar chart list */}
                <div className="card-base p-5 flex flex-col gap-4 text-left">
                  <div className="flex items-center justify-between pb-2 border-b border-border-subtle">
                    <h3 className="font-label-caps text-label-caps text-text-muted flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[16px] text-primary">group</span> Team Redundancy
                    </h3>
                    <span className="badge badge-high text-[10px]">Bus factor: {githubData.bus_factor}</span>
                  </div>
                  <div className="space-y-3.5 mt-2">
                    {githubData.contributors.map((c, i) => (
                      <div key={i} className="flex flex-col gap-1.5">
                        <div className="flex justify-between text-xs font-medium">
                          <span className="text-on-surface font-semibold">{c.name}</span>
                          <span className="text-primary font-bold">{Math.round(c.share * 100)}%</span>
                        </div>
                        <div className="w-full h-2 bg-surface-container rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-primary to-signal-cyan"
                            style={{ width: `${Math.round(c.share * 100)}%` }}
                          />
                        </div>
                        <span className="text-[10px] text-text-muted">{c.commit_count} committed changes</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Heatmap & velocity info */}
                <div className="card-base p-5 lg:col-span-2 flex flex-col gap-4 text-left">
                  <div className="flex items-center justify-between pb-2 border-b border-border-subtle">
                    <h3 className="font-label-caps text-label-caps text-text-muted flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[16px] text-primary">calendar_month</span> Commit Velocity Heatmap
                    </h3>
                    <span className="badge badge-ok text-[10px]">Velocity: {githubData.engineering_velocity} ({githubData.velocity_score}/100)</span>
                  </div>

                  {/* Calendar hours of the day grid */}
                  <div className="flex flex-col gap-2 mt-2 overflow-x-auto">
                    <div className="flex gap-1.5 text-[9px] text-text-muted font-bold ml-8">
                      {["00h", "04h", "08h", "12h", "16h", "20h"].map(h => (
                        <div key={h} className="w-12 text-center">{h}</div>
                      ))}
                    </div>
                    
                    {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => {
                      const dayCommits = githubData.commit_activity_heatmap.filter(h => h.day === day);
                      return (
                        <div key={day} className="flex items-center gap-2">
                          <span className="w-6 text-[9px] font-bold text-text-muted text-right">{day}</span>
                          <div className="flex gap-1">
                            {dayCommits.map((item, idx) => {
                              // color strength based on commit count
                              let bg = 'bg-surface-container-high/40';
                              if (item.commits > 6) bg = 'bg-primary';
                              else if (item.commits > 3) bg = 'bg-primary/60';
                              else if (item.commits > 0) bg = 'bg-primary/20';
                              
                              return (
                                <div 
                                  key={`${day}-${item.hour}`}
                                  className={`w-3.5 h-3.5 rounded-sm transition-all ${bg}`}
                                  title={`${day} ${item.hour} - ${item.commits} commits`}
                                />
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Churn velocity */}
                  <div className="border-t border-border-subtle/50 pt-4 mt-2">
                    <span className="block text-[10px] font-bold text-text-muted uppercase tracking-wider mb-2.5">Weekly Lines Churn</span>
                    <div className="flex items-end gap-1.5 h-20">
                      {githubData.code_churn_timeline.map((c, i) => {
                        const total = c.added + c.deleted;
                        const maxVal = Math.max(...githubData.code_churn_timeline.map(x => x.added + x.deleted));
                        const pct = Math.max(10, Math.round((total / maxVal) * 100));
                        return (
                          <div key={i} className="flex-1 flex flex-col justify-end items-center h-full relative group">
                            <div className="w-full flex flex-col gap-0.5 rounded overflow-hidden" style={{ height: `${pct}%` }}>
                              <div className="bg-signal-emerald flex-1" style={{ flexGrow: c.added }} title={`Added: ${c.added}`} />
                              <div className="bg-signal-rose flex-1" style={{ flexGrow: c.deleted }} title={`Deleted: ${c.deleted}`} />
                            </div>
                            <span className="text-[8px] text-text-muted mt-1">{c.date}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  </div>
                </div>

              {/* Second Row: Project Management & Hotspots */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                  {/* PRs, Issues & Releases */}
                  <div className="card-base p-5 flex flex-col gap-4 text-left">
                    <h3 className="font-label-caps text-label-caps text-text-muted border-b border-border-subtle pb-2 flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[16px] text-primary">merge</span> Project Management
                    </h3>
                    
                    <div className="grid grid-cols-2 gap-4 mt-2">
                      <div className="p-4 bg-surface-container border border-border-subtle rounded text-center">
                        <span className="text-3xl font-bold text-signal-cyan">{githubData.pr_stats || 0}</span>
                        <span className="block text-[10px] text-text-muted mt-1 uppercase font-bold">PRs Merged</span>
                      </div>
                      <div className="p-4 bg-surface-container border border-border-subtle rounded text-center">
                        <span className="text-3xl font-bold text-signal-emerald">{githubData.issue_stats || 0}</span>
                        <span className="block text-[10px] text-text-muted mt-1 uppercase font-bold">Issues Closed</span>
                      </div>
                    </div>
                    
                    <div className="mt-4">
                      <span className="block text-[10px] font-bold text-text-muted uppercase tracking-wider mb-2.5">Release Timeline (Tags)</span>
                      <div className="space-y-2 max-h-[120px] overflow-y-auto pr-2">
                        {githubData.tags && githubData.tags.length > 0 ? (
                          githubData.tags.map((tag, i) => (
                            <div key={i} className="flex justify-between items-center text-xs p-2 bg-surface-container-high rounded border border-border-subtle">
                              <span className="font-code-sm font-semibold text-primary">{tag.name}</span>
                              <span className="text-[10px] text-text-muted">{tag.date ? new Date(tag.date).toLocaleDateString() : ''}</span>
                            </div>
                          ))
                        ) : (
                          <div className="text-xs text-text-muted italic">No release tags found in history.</div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Hotspots & Branches */}
                  <div className="card-base p-5 flex flex-col gap-4 text-left">
                    <h3 className="font-label-caps text-label-caps text-text-muted border-b border-border-subtle pb-2 flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[16px] text-primary">whatshot</span> Code Hotspots & Branches
                    </h3>
                    
                    <div className="mt-2">
                      <span className="block text-[10px] font-bold text-text-muted uppercase tracking-wider mb-2.5">Most Modified Files</span>
                      <div className="space-y-2 max-h-[130px] overflow-y-auto pr-2">
                        {githubData.hotspots && githubData.hotspots.length > 0 ? (
                          githubData.hotspots.map((h, i) => (
                            <div key={i} className="flex justify-between items-center text-xs p-2 bg-surface-container border border-border-subtle rounded" title={h.file}>
                              <span className="font-code-sm text-on-surface truncate pr-4">{h.file.split('/').pop()}</span>
                              <span className="badge badge-warn whitespace-nowrap">{h.change_count} changes</span>
                            </div>
                          ))
                        ) : (
                          <div className="text-xs text-text-muted italic">Insufficient history to detect hotspots.</div>
                        )}
                      </div>
                    </div>

                    <div className="mt-4">
                      <span className="block text-[10px] font-bold text-text-muted uppercase tracking-wider mb-2.5">Active Branches</span>
                      <div className="flex flex-wrap gap-2 max-h-[80px] overflow-y-auto">
                        {githubData.branches && githubData.branches.length > 0 ? (
                          githubData.branches.map((b, i) => (
                            <span key={i} className={`px-2 py-1 rounded text-[10px] font-code-sm border ${b.is_head ? 'bg-primary/20 border-primary text-primary' : 'bg-surface-container border-border-subtle text-text-muted'}`}>
                              <span className="material-symbols-outlined text-[10px] mr-1 align-middle">call_split</span>
                              {b.name}
                            </span>
                          ))
                        ) : (
                          <div className="text-xs text-text-muted italic">No branches detected.</div>
                        )}
                      </div>
                    </div>
                  </div>
              </div>
            </>
            )}

            {/* 4. Code & Security Audits Tab */}
            {activeTab === 'audits' && smellsData && securityData && perfData && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start text-left">
                
                {/* Code Smells */}
                <div className="card-base p-5 flex flex-col gap-4">
                  <h3 className="font-label-caps text-label-caps text-text-muted border-b border-border-subtle pb-2 flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[16px] text-primary">warning</span> Structural Code Smells
                  </h3>
                  <div className="space-y-3 max-h-[350px] overflow-y-auto pr-1">
                    {smellsData.smells.map((sm, i) => (
                      <div key={i} className="p-3 bg-surface-container border border-border-subtle rounded">
                        <div className="flex items-center gap-2 mb-1.5">
                          <span className={`badge ${sm.severity === 'high' ? 'badge-high' : 'badge-warn'}`}>{sm.severity}</span>
                          <span className="text-[9px] font-bold text-text-muted uppercase font-code-sm">conf {Math.round(sm.confidence * 100)}%</span>
                        </div>
                        <p className="text-xs text-on-surface font-semibold leading-normal">{sm.message}</p>
                        <code className="text-[10px] text-text-muted block mt-1.5 font-code-sm truncate">{sm.file}</code>
                        <div className="mt-2 text-[10px] text-primary flex items-center gap-0.5">
                          <span className="material-symbols-outlined text-[12px]">build</span>
                          Remedy: {sm.reremediation || sm.remediation}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Security Report */}
                <div className="card-base p-5 flex flex-col gap-4">
                  <h3 className="font-label-caps text-label-caps text-text-muted border-b border-border-subtle pb-2 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[16px] text-signal-rose">gavel</span> Security Vulnerabilities
                    </span>
                    <span className="badge badge-high text-[10px]">Score: {securityData.security_score}/100</span>
                  </h3>
                  <div className="space-y-3 max-h-[350px] overflow-y-auto pr-1">
                    {securityData.findings.map((f, i) => (
                      <div key={i} className="p-3 bg-surface-container border border-border-subtle rounded">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[10px] font-bold text-signal-rose uppercase">{f.type}</span>
                          <span className="badge badge-high">{f.severity}</span>
                        </div>
                        <p className="text-xs text-on-surface font-semibold leading-normal">{f.description}</p>
                        <code className="text-[10px] text-text-muted block mt-1.5 font-code-sm truncate">{f.file} : L{f.line}</code>
                        <p className="text-[10px] text-on-surface-variant leading-relaxed mt-2 italic">Recommendation: {f.recommendation}</p>
                      </div>
                    ))}
                    {securityData.vulnerabilities.map((v, i) => (
                      <div key={i} className="p-3 bg-[#161216] border border-signal-rose/20 rounded">
                        <span className="text-[9px] font-bold text-signal-rose uppercase tracking-wider">Dependency CVE Found</span>
                        <div className="flex justify-between items-center text-xs font-semibold mt-1">
                          <span className="text-on-surface">{v.package} (v{v.version})</span>
                          <span className="badge badge-warn">{v.severity}</span>
                        </div>
                        <p className="text-[10px] text-text-muted mt-1 leading-normal">{v.vulnerability}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Performance Hotpaths */}
                <div className="card-base p-5 flex flex-col gap-4">
                  <h3 className="font-label-caps text-label-caps text-text-muted border-b border-border-subtle pb-2 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[16px] text-signal-cyan">speed</span> Performance Hotpaths
                    </span>
                    <span className="badge badge-ok text-[10px]">Score: {perfData.performance_score}/100</span>
                  </h3>
                  <div className="space-y-3.5">
                    <div className="grid grid-cols-2 gap-3 mb-2">
                      <div className="p-2.5 bg-surface-container rounded border border-border-subtle">
                        <span className="block text-[9px] text-text-muted font-bold uppercase tracking-wider">Bundle weight</span>
                        <span className="font-code-sm font-bold text-xs text-on-surface">{perfData.bundle_weight_kb} KB</span>
                      </div>
                      <div className="p-2.5 bg-surface-container rounded border border-border-subtle">
                        <span className="block text-[9px] text-text-muted font-bold uppercase tracking-wider">Render MS cost</span>
                        <span className="font-code-sm font-bold text-xs text-on-surface">{perfData.render_cost_ms} ms</span>
                      </div>
                    </div>
                    {perfData.hotpaths.map((hp, i) => (
                      <div key={i} className="p-3 bg-surface-container border border-border-subtle rounded">
                        <div className="flex justify-between items-center mb-1">
                          <code className="text-[10px] font-bold text-signal-cyan truncate max-w-[150px]">{hp.file}</code>
                          <span className="badge badge-warn">{hp.severity}</span>
                        </div>
                        <p className="text-xs text-on-surface font-semibold leading-normal">{hp.description}</p>
                        <p className="text-[10px] text-text-muted mt-1.5">Impact: {hp.impact}</p>
                        <p className="text-[10px] text-signal-emerald font-semibold mt-2 flex items-center gap-0.5">
                          <span className="material-symbols-outlined text-[12px]">tips_and_updates</span>
                          Fix: {hp.suggestion}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            )}

            {/* 5. Heatmaps Tab */}
            {activeTab === 'heatmaps' && (
              <Heatmaps />
            )}

            {/* 6. Benchmarking Tab */}
            {activeTab === 'benchmarking' && (
              <Benchmarking />
            )}

            {/* 7. Diff Tab */}
            {activeTab === 'diff' && (
              <BranchDiff />
            )}

          </div>
        )}
      </div>

      {/* Drill-down Modal */}
      {selectedScore && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-[#050508]/85 backdrop-blur-sm p-4"
          onClick={() => setSelectedScore(null)}
        >
          <div 
            className="card-base max-w-xl w-full max-h-[90vh] overflow-y-auto bg-[#0d0d12] border border-border-subtle/80 flex flex-col gap-4 text-left p-6 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex justify-between items-start border-b border-border-subtle/50 pb-3">
              <div className="flex flex-col">
                <h3 className="font-bold text-base text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[18px]">verified</span>
                  {selectedScore.name} Details
                </h3>
                <span className="text-[10px] text-text-muted uppercase tracking-wider mt-0.5 font-bold">DNA Analysis Engine</span>
              </div>
              <span className={`text-2xl font-black font-code-sm ${getScoreColorClass(selectedScore.score)}`}>
                {selectedScore.score}%
              </span>
            </div>

            {/* Score Definition */}
            <div className="space-y-1.5">
              <span className="text-[9px] font-bold text-text-muted uppercase tracking-wider">Metrics Definition</span>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                {selectedScore.why}
              </p>
            </div>

            {/* Evidence details */}
            <div className="space-y-2 border-t border-border-subtle/30 pt-3.5">
              <span className="text-[9px] font-bold text-text-muted uppercase tracking-wider flex items-center gap-1">
                <span className="material-symbols-outlined text-[13px] text-signal-cyan">analytics</span>
                Grounded Evidence Parameters
              </span>
              <ul className="space-y-1.5">
                {selectedScore.evidence.map((ev, i) => (
                  <li key={i} className="text-xs text-on-surface font-semibold flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-signal-cyan" />
                    {ev}
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommendations */}
            <div className="space-y-2 border-t border-border-subtle/30 pt-3.5">
              <span className="text-[9px] font-bold text-text-muted uppercase tracking-wider flex items-center gap-1">
                <span className="material-symbols-outlined text-[13px] text-signal-emerald">check_circle</span>
                Recommended Code Actions
              </span>
              <ul className="space-y-1.5">
                {selectedScore.recommendations.map((rec, i) => (
                  <li key={i} className="text-xs text-on-surface-variant flex items-center gap-2 leading-relaxed">
                    <span className="w-1.5 h-1.5 rounded-full bg-signal-emerald" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>

            {/* Affected Files */}
            <div className="space-y-2 border-t border-border-subtle/30 pt-3.5">
              <span className="text-[9px] font-bold text-text-muted uppercase tracking-wider">Affected Repository Files</span>
              <div className="flex flex-col gap-1.5">
                {selectedScore.affected_files.map((file, i) => (
                  <code key={i} className="font-code-sm text-[10px] text-text-muted bg-surface-container px-2.5 py-1.5 rounded border border-border-subtle/40 truncate block">
                    {file}
                  </code>
                ))}
              </div>
            </div>

            {/* Close button */}
            <div className="flex justify-end border-t border-border-subtle/50 pt-4 mt-2">
              <button 
                onClick={() => setSelectedScore(null)}
                className="btn-primary py-2 px-5 rounded-lg text-xs font-bold"
              >
                Close View
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
