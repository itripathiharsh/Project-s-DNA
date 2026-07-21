import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { globalSearch } from '../services/api';
import { useNotification } from '../components/NotificationContext';

export default function SearchPalette() {
  const [query, setQuery] = useState('');
  const [type, setType] = useState('');
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const navigate = useNavigate();
  const { toast } = useNotification();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await globalSearch(query, type);
      setResults(res.results || []);
      setTotal(res.total || 0);
      setSearched(true);
    } catch (err) {
      toast('Search failed: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const getResultIcon = (rType) => {
    switch (rType) {
      case 'repository': return 'science';
      case 'file': return 'description';
      case 'class': return 'account_tree';
      case 'function': return 'code';
      case 'symbol': return 'psychology';
      case 'author': return 'person';
      case 'insight': return 'insights';
      case 'risk': return 'security';
      case 'commit': return 'history';
      default: return 'search';
    }
  };

  const handleResultClick = (result) => {
    if (result.path) {
      navigate(`/explorer?path=${encodeURIComponent(result.path)}`);
    } else if (result.type === 'repository') {
      navigate('/dashboard');
    } else if (result.type === 'insight') {
      navigate('/intelligence');
    } else if (result.type === 'risk') {
      navigate('/risk');
    }
  };

  const TYPES = [
    { value: '', label: 'All Categories' },
    { value: 'repositories', label: 'Repositories' },
    { value: 'files', label: 'Files' },
    { value: 'symbols', label: 'Symbols' },
    { value: 'classes', label: 'Classes' },
    { value: 'functions', label: 'Functions' },
    { value: 'authors', label: 'Authors' },
    { value: 'insights', label: 'Insights' },
    { value: 'risk', label: 'Risk Indicators' },
    { value: 'commits', label: 'Commits' }
  ];

  return (
    <>
      <PageHeader title="Search Center" subtitle="Global indexed search across code tokens, symbols, risks, and history" />
      <div className="p-6 flex-1 flex flex-col gap-6 max-w-4xl mx-auto w-full font-body-sm">
        <form onSubmit={handleSearch} className="card-base bg-[#0d0d0d] flex gap-3 p-4">
          <div className="relative flex-1">
            <span className="material-symbols-outlined absolute left-3 top-3 text-on-surface-variant text-[20px]">search</span>
            <input
              type="text"
              required
              placeholder="Search code tokens, authors, functions, risk metrics..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="input-base pl-10 pr-3 py-3 text-base"
            />
          </div>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="input-base w-48 bg-[#161616]"
          >
            {TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          <button type="submit" disabled={loading} className="btn-primary px-8 h-[44px]">
            {loading ? 'Searching' : 'Search'}
          </button>
        </form>

        {loading ? (
          <div className="flex justify-center items-center py-16">
            <div className="w-10 h-10 border-4 border-surface-container-high border-t-primary rounded-full animate-spin" />
          </div>
        ) : searched ? (
          <div className="flex flex-col gap-4">
            <div className="text-text-muted text-xs font-bold uppercase">
              Found {total} search results matching "{query}"
            </div>
            
            <div className="flex flex-col gap-2">
              {results.map((res, idx) => (
                <div
                  key={idx}
                  onClick={() => handleResultClick(res)}
                  className="p-3.5 bg-surface-container hover:bg-surface-container-high border border-border-subtle hover:border-primary/30 rounded cursor-pointer transition-all flex items-start gap-4"
                >
                  <div className="w-8 h-8 rounded bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-[16px] text-primary">{getResultIcon(res.type)}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold text-on-surface text-sm truncate">{res.name}</span>
                      <span className="badge badge-info text-[9px] uppercase">{res.type}</span>
                    </div>
                    <p className="text-xs text-text-muted truncate">{res.detail}</p>
                    {res.path && (
                      <code className="text-[10px] text-primary block mt-1.5 font-code-sm truncate">{res.path}</code>
                    )}
                  </div>
                  <span className="material-symbols-outlined text-text-muted text-[14px] self-center">chevron_right</span>
                </div>
              ))}
              {results.length === 0 && (
                <div className="text-center text-text-muted py-16 card-base">
                  <span className="material-symbols-outlined text-[48px] block mb-2 text-on-surface-variant">search_off</span>
                  No results found. Try adjusting filters or search query terms.
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center text-text-muted py-16 card-base">
            <span className="material-symbols-outlined text-[48px] block mb-2 text-on-surface-variant">search</span>
            Enter search parameters to query the workspace analysis indexes.
          </div>
        )}
      </div>
    </>
  );
}
