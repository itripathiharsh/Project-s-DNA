import { useState, useEffect } from 'react';
import { getGitActivityHeatmap } from '../services/api';
import PageHeader from '../components/PageHeader';

export default function GitActivityHeatmap() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await getGitActivityHeatmap();
        setData(result);
      } catch (err) {
        console.error('Error fetching git activity heatmap:', err);
        setError(err.message || 'Failed to fetch git activity metrics.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getActivityColor = (count) => {
    if (count >= 10) return '#00bbf9'; // High activity (cyan)
    if (count >= 5) return '#0ea5e9';  // Medium activity
    if (count >= 1) return '#38bdf8';  // Low activity
    return '#12121e'; // No activity (dark background)
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-[36px] text-primary animate-spin">sync</span>
          <span className="text-xs text-text-muted">Analyzing commit history timeline...</span>
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

  const activity = data?.activity || [];
  const totalCommits = data?.total_commits || 0;

  return (
    <>
      <PageHeader 
        title="Git Activity Heatmap" 
        subtitle="Chronological commit frequency and contribution hotspots" 
      />
      <div className="p-6 flex flex-col gap-6 max-w-[1600px] mx-auto w-full flex-1">
        
        <div className="card-base flex flex-col min-h-[450px]">
          <div className="border-b border-border-subtle/50 pb-3 mb-4 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-xs uppercase text-text-muted tracking-wider">Activity Timeline</h3>
              <p className="text-[10px] text-text-muted mt-0.5">Colors indicate volume of commits per day.</p>
            </div>
            <div className="text-right">
              <span className="text-xs text-text-muted mr-2">Total Commits:</span>
              <span className="font-bold text-primary">{totalCommits}</span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 overflow-y-auto max-h-[600px]">
            {activity.length > 0 ? activity.map((act, i) => {
              const bg = getActivityColor(act.count);
              return (
                <div
                  key={i}
                  className="w-12 h-12 flex flex-col items-center justify-center rounded-sm border border-border-subtle hover:scale-110 transition-transform cursor-pointer relative group"
                  style={{ backgroundColor: bg }}
                >
                  <span className={`text-[10px] font-bold ${act.count > 0 ? 'text-surface-base' : 'text-text-muted'}`}>{act.count > 0 ? act.count : ''}</span>
                  
                  {/* Tooltip */}
                  <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-[#09090e] border border-border-subtle text-on-surface text-[10px] px-2 py-1 rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                    {act.date}: {act.count} commits
                  </div>
                </div>
              );
            }) : (
              <div className="w-full py-16 text-center text-text-muted text-xs">No activity found.</div>
            )}
          </div>
          
          <div className="mt-8 flex items-center gap-2 text-[10px] text-text-muted border-t border-border-subtle/50 pt-4">
            <span>Less</span>
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#12121e' }} />
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#38bdf8' }} />
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#0ea5e9' }} />
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#00bbf9' }} />
            <span>More</span>
          </div>
        </div>

      </div>
    </>
  );
}
