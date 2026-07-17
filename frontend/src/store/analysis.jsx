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

  const runAnalysisStream = useCallback((path, onEvent) => {
    if (!path) return null;
    setRepoPath(path);
    setLoading(true);
    setError(null);

    const apiBase = import.meta.env.VITE_API_BASE_URL || 'https://project-dna-backend.onrender.com';
    const sseUrl = `${apiBase}/v1/analyze/sse?repo_path=${encodeURIComponent(path)}`;
    const eventSource = new EventSource(sseUrl);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onEvent) {
          onEvent(data);
        }
        if (data.type === 'complete') {
          setData(data.result);
          setLoading(false);
          eventSource.close();
        } else if (data.type === 'error') {
          setError(data.message || 'Analysis failed');
          setData(null);
          setLoading(false);
          eventSource.close();
        }
      } catch (err) {
        console.error('Error handling SSE message:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('EventSource connection error:', err);
      setError('Connection to analysis stream lost.');
      setLoading(false);
      eventSource.close();
      if (onEvent) {
        onEvent({ type: 'error', message: 'Connection to analysis stream lost.' });
      }
    };

    return eventSource;
  }, []);

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
      value={{ repoPath, data, error, loading, runAnalysis, runAnalysisStream, reset, setRepoPath, loadLatest }}
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
