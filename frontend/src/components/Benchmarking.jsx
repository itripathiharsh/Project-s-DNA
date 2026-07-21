import { useState, useEffect } from 'react';
import { useAnalysis } from '../store/analysis';
import { postBenchmarkingCompare } from '../services/api';

export default function Benchmarking() {
  const { selectedBranches } = useAnalysis();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      if (!selectedBranches || selectedBranches.length < 2) {
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const res = await postBenchmarkingCompare(selectedBranches);
        setData(res.benchmarks);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [selectedBranches]);

  if (loading) {
    return <div className="p-8 text-center text-text-muted">Loading benchmarks...</div>;
  }

  if (error) {
    return <div className="p-8 text-center text-signal-rose">Error: {error}</div>;
  }

  if (!selectedBranches || selectedBranches.length < 2) {
    return (
      <div className="p-8 text-center text-on-surface-variant flex flex-col items-center justify-center min-h-[300px]">
        <span className="material-symbols-outlined text-[48px] text-primary mb-4 opacity-50">compare</span>
        <h3 className="font-headline-md mb-2">Insufficient Branches</h3>
        <p>You need to select and analyze at least two branches to view benchmarking data.</p>
      </div>
    );
  }

  const metrics = [
    { key: 'health', label: 'Health Score' },
    { key: 'complexity', label: 'Complexity Risks' },
    { key: 'maintainability', label: 'Maintainability' },
    { key: 'technical_debt', label: 'Technical Debt Score' },
    { key: 'production_readiness', label: 'Production Readiness' },
    { key: 'risk_score', label: 'Overall Risk Score' },
    { key: 'bus_factor', label: 'Bus Factor' },
    { key: 'total_files', label: 'Total Files' }
  ];

  return (
    <div className="flex flex-col gap-6">
      <div className="card-base p-6 border border-border-subtle">
        <h3 className="font-headline-md text-headline-md mb-6 flex items-center gap-2">
          <span className="material-symbols-outlined text-primary">bar_chart</span>
          Branch Benchmarking
        </h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr>
                <th className="p-4 border-b border-border-subtle font-label-caps text-text-muted">Metric</th>
                {selectedBranches.map(b => (
                  <th key={b} className="p-4 border-b border-border-subtle font-headline-sm text-on-surface text-center">
                    <span className="bg-surface-container-highest px-3 py-1 rounded-full text-primary font-code-sm">{b}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {metrics.map(metric => (
                <tr key={metric.key} className="border-b border-border-subtle/50 hover:bg-surface-container-low transition-colors">
                  <td className="p-4 font-bold text-on-surface-variant">{metric.label}</td>
                  {selectedBranches.map(b => {
                    const val = data?.[b]?.[metric.key];
                    let color = 'text-on-surface';
                    if (metric.key.includes('score') || metric.key === 'health') {
                      if (val >= 80) color = 'text-signal-emerald';
                      else if (val >= 60) color = 'text-signal-amber';
                      else color = 'text-signal-rose';
                    }
                    if (metric.key === 'risk_score') {
                      if (val <= 20) color = 'text-signal-emerald';
                      else if (val <= 50) color = 'text-signal-amber';
                      else color = 'text-signal-rose';
                    }
                    return (
                      <td key={`${metric.key}-${b}`} className={`p-4 text-center font-code-md ${color}`}>
                        {val !== undefined ? val : 'N/A'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
