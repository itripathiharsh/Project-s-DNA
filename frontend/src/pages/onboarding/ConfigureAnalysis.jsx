import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../../store/analysis';

export default function ConfigureAnalysis() {
  const navigate = useNavigate();
  const { repoPath, repoInfo, selectedBranches, setSelectedBranches } = useAnalysis();
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!repoPath || !repoInfo) {
      navigate('/onboarding');
    }
  }, [repoPath, repoInfo, navigate]);

  if (!repoInfo) return null;

  const toggleBranch = (branchName) => {
    if (selectedBranches.includes(branchName)) {
      setSelectedBranches(selectedBranches.filter(b => b !== branchName));
    } else {
      setSelectedBranches([...selectedBranches, branchName]);
    }
  };

  const filteredBranches = repoInfo.branches.filter(b => 
    b.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-background text-on-surface font-body-md text-body-md flex flex-col">
      <header className="bg-background border-b border-border-subtle flex justify-between items-center px-gutter w-full h-row-height-standard fixed top-0 z-50">
        <div className="flex items-center gap-4">
          <span className="font-headline-md text-headline-md font-bold text-on-surface">Project DNA</span>
        </div>
      </header>

      <main className="pt-row-height-standard flex-grow flex flex-col items-center">
        <div className="max-w-5xl w-full p-8">
          <div className="mb-10 text-center">
            <h1 className="font-headline-lg text-headline-lg mb-2">Select Branches</h1>
            <p className="text-on-surface-variant max-w-2xl mx-auto">
              Choose the branches you want to analyze for <code className="bg-surface-container-highest px-1.5 py-0.5 rounded text-primary font-code-sm">{repoInfo.name}</code>.
            </p>
          </div>

          <div className="bg-surface-container-low border border-border-subtle p-6 rounded-lg mb-8">
            <h2 className="font-headline-md text-headline-md mb-4">Repository Overview</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="font-label-caps text-text-muted mb-1">Owner</div>
                <div className="font-code-md text-on-surface">{repoInfo.owner}</div>
              </div>
              <div>
                <div className="font-label-caps text-text-muted mb-1">Language</div>
                <div className="font-code-md text-on-surface">{repoInfo.language}</div>
              </div>
              <div>
                <div className="font-label-caps text-text-muted mb-1">Stars</div>
                <div className="font-code-md text-on-surface">{repoInfo.stars}</div>
              </div>
              <div>
                <div className="font-label-caps text-text-muted mb-1">Default Branch</div>
                <div className="font-code-md text-primary font-bold">{repoInfo.default_branch}</div>
              </div>
            </div>
          </div>

          <div className="bg-surface-container-low border border-border-subtle rounded-lg flex flex-col h-full overflow-hidden">
            <div className="p-4 border-b border-border-subtle flex justify-between items-center">
              <h3 className="font-headline-md text-headline-md">Available Branches ({filteredBranches.length})</h3>
              <input
                type="text"
                placeholder="Filter branches..."
                className="bg-surface-container border border-border-subtle p-2 text-sm rounded text-on-surface outline-none focus:border-primary"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="max-h-96 overflow-y-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-surface-container sticky top-0 z-10">
                  <tr>
                    <th className="p-3 border-b border-border-subtle font-label-caps text-text-muted w-10"></th>
                    <th className="p-3 border-b border-border-subtle font-label-caps text-text-muted">Branch Name</th>
                    <th className="p-3 border-b border-border-subtle font-label-caps text-text-muted">Last Commit</th>
                    <th className="p-3 border-b border-border-subtle font-label-caps text-text-muted hidden md:table-cell">Author</th>
                    <th className="p-3 border-b border-border-subtle font-label-caps text-text-muted hidden md:table-cell">Commits</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredBranches.map(b => (
                    <tr 
                      key={b.name} 
                      className="border-b border-border-subtle hover:bg-surface-container-highest cursor-pointer transition-colors"
                      onClick={() => toggleBranch(b.name)}
                    >
                      <td className="p-3">
                        <input 
                          type="checkbox" 
                          checked={selectedBranches.includes(b.name)}
                          onChange={() => {}}
                          className="w-4 h-4 text-primary focus:ring-0 border-border-subtle rounded"
                        />
                      </td>
                      <td className="p-3 font-code-sm">
                        {b.name} {b.name === repoInfo.default_branch && <span className="ml-2 text-[10px] bg-primary/20 text-primary px-1.5 py-0.5 rounded">Default</span>}
                      </td>
                      <td className="p-3 font-code-sm text-on-surface-variant">
                        <div className="flex flex-col">
                          <span>{b.last_commit}</span>
                          <span className="text-[10px]">{b.last_updated}</span>
                        </div>
                      </td>
                      <td className="p-3 text-body-sm text-on-surface-variant hidden md:table-cell">{b.author}</td>
                      <td className="p-3 text-body-sm text-on-surface-variant hidden md:table-cell">{b.commit_count}</td>
                    </tr>
                  ))}
                  {filteredBranches.length === 0 && (
                    <tr>
                      <td colSpan="5" className="p-8 text-center text-on-surface-variant">No branches match your filter.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-8 flex justify-between items-center py-6 border-t border-border-subtle">
            <button onClick={() => navigate('/onboarding')} className="flex items-center gap-2 px-6 py-2.5 rounded border border-border-subtle hover:bg-surface-container transition-colors text-on-surface font-bold">
              <span className="material-symbols-outlined">arrow_back</span> Back
            </button>
            <button
              onClick={() => navigate('/onboarding/analyze')}
              disabled={selectedBranches.length === 0}
              className="bg-primary text-on-primary px-10 py-2.5 rounded font-bold hover:opacity-90 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Analyze {selectedBranches.length} Branch{selectedBranches.length !== 1 ? 'es' : ''} <span className="material-symbols-outlined">arrow_forward</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
