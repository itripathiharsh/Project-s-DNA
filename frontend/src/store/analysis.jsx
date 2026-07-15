import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { analyzeRepository, getLatestAnalysis } from '../services/api';

const AnalysisContext = createContext(null);

export function AnalysisProvider({ children }) {
  const [repoPath, setRepoPath] = useState('');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true); // Start loading to check for cached analysis first

  const loadLatest = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getLatestAnalysis();
      setData(result);
      if (result.repository?.path) {
        setRepoPath(result.repository.path);
      }
      return result;
    } catch (err) {
      console.log('No existing active analysis cached on backend:', err.message || err);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLatest();
  }, [loadLatest]);

  const runAnalysis = useCallback(async (path) => {
    if (!path) return;
    setRepoPath(path);
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeRepository(path);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || String(err));
      setData(null);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setRepoPath('');
    setLoading(false);
  }, []);

  return (
    <AnalysisContext.Provider
      value={{ repoPath, data, error, loading, runAnalysis, reset, setRepoPath, loadLatest }}
    >
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  const ctx = useContext(AnalysisContext);
  if (!ctx) throw new Error('useAnalysis must be used within AnalysisProvider');
  return ctx;
}
