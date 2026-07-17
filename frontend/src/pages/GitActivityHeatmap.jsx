import { useState, useEffect, useMemo } from 'react';
import { getChangeHeatmap } from '../services/api';
import PageHeader from '../components/PageHeader';

export default function GitIntelligence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        // We use the change heatmap endpoint because it returns the full commit history and file hotspots
        const result = await getChangeHeatmap('all');
        setData(result);
      } catch (err) {
        console.error('Error fetching git intelligence:', err);
        setError(err.message || 'Failed to fetch git intelligence metrics.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const { commits = [], file_changes = [] } = data || {};

  const metrics = useMemo(() => {
    if (!commits.length) return null;

    // 1. Hot Files & Unstable Files
    const hotFiles = [...file_changes].sort((a, b) => b.churn - a.churn).slice(0, 5);
    const unstableFiles = [...file_changes].sort((a, b) => (b.commits_count * b.churn) - (a.commits_count * a.churn)).slice(0, 5);

    // 2. Abandoned Files & Forgotten Modules
    const abandonedFiles = [...file_changes]
      .filter(f => f.last_modified)
      .sort((a, b) => new Date(a.last_modified) - new Date(b.last_modified))
      .slice(0, 5);

    // 3. Knowledge Evolution & Churn Analysis
    let totalInsertions = 0;
    let totalDeletions = 0;
    
    // 4. Commit Timeline & Frequency
    const months = {};
    const authors = {};
    const authorNetwork = {}; // { file: Set(authors) }
    
    commits.forEach(c => {
      const dt = c.date ? c.date.substring(0, 7) : 'Unknown';
      if (!months[dt]) months[dt] = { commits: 0, insertions: 0, deletions: 0 };
      months[dt].commits++;
      
      const author = c.author || 'Unknown';
      if (!authors[author]) authors[author] = { commits: 0, churn: 0, lastActive: c.date };
      authors[author].commits++;

      let cIns = 0;
      let cDel = 0;
      (c.files || []).forEach(f => {
        cIns += f.insertions || 0;
        cDel += f.deletions || 0;
        
        if (f.file_path) {
          if (!authorNetwork[f.file_path]) authorNetwork[f.file_path] = new Set();
          authorNetwork[f.file_path].add(author);
        }
      });
      
      months[dt].insertions += cIns;
      months[dt].deletions += cDel;
      authors[author].churn += cIns + cDel;
      totalInsertions += cIns;
      totalDeletions += cDel;
    });

    // 5. Team Collaboration Graph (simplified to pairs)
    const collabPairs = {};
    Object.values(authorNetwork).forEach(authorSet => {
      const arr = Array.from(authorSet);
      if (arr.length > 1) {
        for (let i = 0; i < arr.length; i++) {
          for (let j = i + 1; j < arr.length; j++) {
            const pair = [arr[i], arr[j]].sort().join(' & ');
            collabPairs[pair] = (collabPairs[pair] || 0) + 1;
          }
        }
      }
    });
    const topCollabs = Object.entries(collabPairs).sort((a, b) => b[1] - a[1]).slice(0, 5);

    const timeline = Object.entries(months).sort((a, b) => a[0].localeCompare(b[0]));
    const topAuthors = Object.entries(authors).sort((a, b) => b[1].commits - a[1].commits).slice(0, 5);

    return {
      hotFiles, unstableFiles, abandonedFiles, timeline, topAuthors, topCollabs, totalInsertions, totalDeletions, totalCommits: commits.length
    };
  }, [commits, file_changes]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-[36px] text-primary animate-spin">sync</span>
          <span className="text-xs text-text-muted">Aggregating chronological Git Intelligence...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 text-center max-w-md mx-auto">
        <span className="material-symbols-outlined text-[48px] text-signal-rose mb-3">error</span>
        <h3 className="font-bold text-base text-on-surface">Analysis Error</h3>
        <p className="text-xs text-text-muted mt-2">{error}</p>
      </div>
    );
  }

  if (!metrics) return null;

  return (
    <>
      <PageHeader 
        title="Git Intelligence Center" 
        subtitle="Deep chronological and social analysis of repository evolution, team collaboration, and codebase churn" 
      />
      <div className="p-6 max-w-[1600px] mx-auto w-full flex-1 overflow-y-auto">
        
        {/* Top KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="card-base p-4 border-l-4 border-l-primary flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-text-muted tracking-wider">Total Commits</span>
            <span className="text-2xl font-black text-on-surface">{metrics.totalCommits.toLocaleString()}</span>
          </div>
          <div className="card-base p-4 border-l-4 border-l-signal-emerald flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-text-muted tracking-wider">Lines Added (Knowledge Evolution)</span>
            <span className="text-2xl font-black text-signal-emerald">+{metrics.totalInsertions.toLocaleString()}</span>
          </div>
          <div className="card-base p-4 border-l-4 border-l-signal-rose flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-text-muted tracking-wider">Lines Removed (Churn)</span>
            <span className="text-2xl font-black text-signal-rose">-{metrics.totalDeletions.toLocaleString()}</span>
          </div>
          <div className="card-base p-4 border-l-4 border-l-signal-amber flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-text-muted tracking-wider">Active Contributors</span>
            <span className="text-2xl font-black text-signal-amber">{metrics.topAuthors.length}</span>
          </div>
        </div>

        {/* Bento Box Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Commit Timeline & Frequency */}
          <div className="card-base p-5 lg:col-span-2 flex flex-col">
            <div className="border-b border-border-subtle/50 pb-2 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px] text-primary">monitoring</span>
              <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Commit Timeline & Churn Analysis</h3>
            </div>
            <div className="flex-1 flex items-end gap-2 h-48 mt-4 overflow-hidden">
              {metrics.timeline.slice(-24).map(([month, stats], i) => {
                const maxCommits = Math.max(...metrics.timeline.map(t => t[1].commits), 1);
                const heightPct = Math.max(5, (stats.commits / maxCommits) * 100);
                return (
                  <div key={i} className="flex-1 flex flex-col justify-end items-center group relative h-full">
                    <div 
                      className="w-full bg-primary/20 hover:bg-primary border border-primary/40 rounded-t transition-colors" 
                      style={{ height: `${heightPct}%` }}
                    />
                    <div className="mt-2 text-[9px] text-text-muted -rotate-45 origin-top-left translate-y-2 translate-x-1 whitespace-nowrap">
                      {month}
                    </div>
                    {/* Tooltip */}
                    <div className="absolute bottom-full mb-2 bg-[#09090e] border border-border-subtle text-xs px-3 py-2 rounded shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 whitespace-nowrap">
                      <p className="font-bold text-on-surface border-b border-border-subtle pb-1 mb-1">{month}</p>
                      <p className="text-primary">{stats.commits} Commits</p>
                      <p className="text-signal-emerald">+{stats.insertions} Insertions</p>
                      <p className="text-signal-rose">-{stats.deletions} Deletions</p>
                    </div>
                  </div>
                )
              })}
            </div>
            <div className="h-6" /> {/* spacer for labels */}
          </div>

          {/* Team Collaboration Graph / Author Network */}
          <div className="card-base p-5 flex flex-col">
            <div className="border-b border-border-subtle/50 pb-2 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px] text-signal-amber">hub</span>
              <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Team Collaboration Network</h3>
            </div>
            <p className="text-[10px] text-text-muted mb-3 leading-relaxed">Authors frequently editing the same files, indicating shared knowledge domains.</p>
            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
              {metrics.topCollabs.map(([pair, count], i) => (
                <div key={i} className="flex items-center justify-between bg-surface-container-low p-2 rounded border border-border-subtle">
                  <div className="flex items-center gap-2 truncate">
                    <span className="material-symbols-outlined text-[16px] text-on-surface-variant">group</span>
                    <span className="text-xs text-on-surface font-semibold truncate">{pair}</span>
                  </div>
                  <span className="badge badge-warn text-[10px] shrink-0">{count} Shared Edits</span>
                </div>
              ))}
              {metrics.topCollabs.length === 0 && <span className="text-xs text-text-muted block text-center py-4">No collaboration overlaps found.</span>}
            </div>
          </div>

          {/* Hot Files */}
          <div className="card-base p-5 flex flex-col">
            <div className="border-b border-border-subtle/50 pb-2 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px] text-signal-rose">local_fire_department</span>
              <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Hot Files (Highest Churn)</h3>
            </div>
            <div className="flex flex-col gap-2.5">
              {metrics.hotFiles.map((f, i) => (
                <div key={i} className="flex flex-col gap-1 p-2 bg-signal-rose/5 border border-signal-rose/20 rounded">
                  <span className="text-xs font-mono font-bold text-on-surface truncate" title={f.file_path}>{f.file_path.split('/').pop()}</span>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-text-muted break-all pr-2 truncate">{f.file_path}</span>
                    <span className="font-bold text-signal-rose shrink-0">{f.churn.toLocaleString()} churn</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Unstable Files */}
          <div className="card-base p-5 flex flex-col">
            <div className="border-b border-border-subtle/50 pb-2 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px] text-primary">moving</span>
              <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Unstable Files</h3>
            </div>
            <div className="flex flex-col gap-2.5">
              {metrics.unstableFiles.map((f, i) => (
                <div key={i} className="flex flex-col gap-1 p-2 bg-primary/5 border border-primary/20 rounded">
                  <span className="text-xs font-mono font-bold text-on-surface truncate" title={f.file_path}>{f.file_path.split('/').pop()}</span>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-text-muted">Freq: {f.commits_count} commits</span>
                    <span className="font-bold text-primary shrink-0">{f.churn.toLocaleString()} churn</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Abandoned Files */}
          <div className="card-base p-5 flex flex-col">
            <div className="border-b border-border-subtle/50 pb-2 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px] text-text-muted">inventory_2</span>
              <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Abandoned & Forgotten Modules</h3>
            </div>
            <div className="flex flex-col gap-2.5">
              {metrics.abandonedFiles.map((f, i) => (
                <div key={i} className="flex flex-col gap-1 p-2 bg-surface-container border border-border-subtle rounded">
                  <span className="text-xs font-mono font-bold text-on-surface truncate" title={f.file_path}>{f.file_path.split('/').pop()}</span>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-text-muted break-all pr-2 truncate">{f.file_path}</span>
                    <span className="font-bold text-on-surface-variant shrink-0">{f.last_modified ? f.last_modified.substring(0, 10) : 'Unknown'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </>
  );
}
