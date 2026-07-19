import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { analyzeRepository, getLatestAnalysis, setApiBranch, getHeaders } from '../services/api';

const AnalysisContext = createContext(null);

export function AnalysisProvider({ children }) {
  const [repoPath, setRepoPath] = useState('');
  const [repoInfo, setRepoInfo] = useState(null);
  const [selectedBranches, setSelectedBranches] = useState([]);
  const [activeBranch, setActiveBranch] = useState('');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true); // Start loading to check for cached analysis first

  // Sync active branch to API service whenever it changes
  useEffect(() => {
    setApiBranch(activeBranch);
  }, [activeBranch]);

  const loadLatest = useCallback(async (options = {}) => {
    setLoading(true);
    try {
      const result = await getLatestAnalysis({ headers: getHeaders(), ...options });
      setData(result);
      if (result.repository?.path) {
        setRepoPath(result.repository.path);
      }
      return result;
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.log('No existing active analysis cached on backend:', err.message || err);
        setData(null);
      }
    } finally {
      if (!options?.signal?.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    loadLatest({ signal: controller.signal });
    return () => controller.abort();
  }, [loadLatest, activeBranch]);

  // ── POST + fake-progress polling ──────────────────────────────────────────
  // Replaces the broken SSE approach which dies on Render's 60-second idle
  // timeout. We POST to /v1/analyze (a normal HTTP request, no streaming)
  // and emit synthetic progress events every 4 s so the UI stays alive.
  const runAnalysisStream = useCallback((path, onEvent) => {
    if (!path) return null;
    setRepoPath(path);
    setLoading(true);
    setError(null);

    let cancelled = false;
    let stepInterval = null;

    const PROGRESS_STEPS = [
      { step_id: 'discovery',  message: 'Discovering repository files...',     percent: 10 },
      { step_id: 'ast',        message: 'Running AST extraction engine...',     percent: 25 },
      { step_id: 'structural', message: 'Analysing structural dependencies...', percent: 40 },
      { step_id: 'evolution',  message: 'Running evolution & git engine...',    percent: 55 },
      { step_id: 'knowledge',  message: 'Building knowledge graph...',          percent: 70 },
      { step_id: 'risk',       message: 'Evaluating risk patterns...',          percent: 85 },
      { step_id: 'reasoning',  message: 'Generating insights...',               percent: 95 },
    ];

    const apiBase = import.meta.env.VITE_API_BASE_URL || 'https://project-dna-backend.onrender.com';

    (async () => {
      try {
        if (onEvent) onEvent({ type: 'connected' });

        // Emit fake progress ticks every 4 s while the POST is in-flight
        let stepIdx = 0;
        stepInterval = setInterval(() => {
          if (cancelled || stepIdx >= PROGRESS_STEPS.length) {
            clearInterval(stepInterval);
            return;
          }
          const step = PROGRESS_STEPS[stepIdx++];
          if (onEvent) onEvent({ type: 'progress', ...step, status: 'running' });
        }, 4000);

        // Single POST – may take several minutes on Render free tier, that is OK
        const response = await fetch(`${apiBase}/v1/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ repo_path: path }),
        });

        clearInterval(stepInterval);
        if (cancelled) return;

        if (!response.ok) {
          const text = await response.text();
          let detail = text;
          try { detail = JSON.parse(text).detail || text; } catch { /* ignore */ }
          throw new Error(detail || `HTTP ${response.status}`);
        }

        const result = await response.json();
        if (cancelled) return;

        setData(result);
        setLoading(false);
        if (onEvent) onEvent({ type: 'complete', result });

      } catch (err) {
        if (cancelled) return;
        clearInterval(stepInterval);
        const msg = err.message || String(err);
        setError(msg);
        setData(null);
        setLoading(false);
        if (onEvent) onEvent({ type: 'error', message: msg });
      }
    })();

    // Return a cancel handle with the same .close() interface as EventSource
    return {
      close: () => {
        cancelled = true;
        if (stepInterval) clearInterval(stepInterval);
      }
    };
  }, []);

  const runAnalysisStreamBranch = useCallback((path, branch, onEvent) => {
    if (!path) return null;
    setRepoPath(path);
    setLoading(true);
    setError(null);

    let cancelled = false;
    let stepInterval = null;

    const PROGRESS_STEPS = [
      { step_id: 'discovery',  message: `[${branch}] Discovering repository files...`,     percent: 10 },
      { step_id: 'ast',        message: `[${branch}] Running AST extraction engine...`,     percent: 25 },
      { step_id: 'structural', message: `[${branch}] Analysing structural dependencies...`, percent: 40 },
      { step_id: 'evolution',  message: `[${branch}] Running evolution & git engine...`,    percent: 55 },
      { step_id: 'knowledge',  message: `[${branch}] Building knowledge graph...`,          percent: 70 },
      { step_id: 'risk',       message: `[${branch}] Evaluating risk patterns...`,          percent: 85 },
      { step_id: 'reasoning',  message: `[${branch}] Generating insights...`,               percent: 95 },
    ];

    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    (async () => {
      try {
        if (onEvent) onEvent({ type: 'connected', branch });

        let stepIdx = 0;
        stepInterval = setInterval(() => {
          if (cancelled || stepIdx >= PROGRESS_STEPS.length) {
            clearInterval(stepInterval);
            return;
          }
          const step = PROGRESS_STEPS[stepIdx++];
          if (onEvent) onEvent({ type: 'progress', ...step, status: 'running', branch });
        }, 4000);

        const response = await fetch(`${apiBase}/v1/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ repo_path: path, branch: branch }),
        });

        clearInterval(stepInterval);
        if (cancelled) return;

        if (!response.ok) {
          const text = await response.text();
          let detail = text;
          try { detail = JSON.parse(text).detail || text; } catch { /* ignore */ }
          throw new Error(detail || `HTTP ${response.status}`);
        }

        const result = await response.json();
        if (cancelled) return;

        setData(result);
        setLoading(false);
        if (onEvent) onEvent({ type: 'complete', result, branch });

      } catch (err) {
        if (cancelled) return;
        clearInterval(stepInterval);
        const msg = err.message || String(err);
        setError(msg);
        setLoading(false);
        if (onEvent) onEvent({ type: 'error', message: msg, branch });
      }
    })();

    return {
      close: () => {
        cancelled = true;
        if (stepInterval) clearInterval(stepInterval);
      }
    };
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
    setRepoInfo(null);
    setSelectedBranches([]);
    setActiveBranch('');
    setLoading(false);
  }, []);

  return (
    <AnalysisContext.Provider
      value={{ repoPath, data, error, loading, repoInfo, selectedBranches, activeBranch, setActiveBranch, runAnalysis, runAnalysisStream, runAnalysisStreamBranch, reset, setRepoPath, setRepoInfo, setSelectedBranches, loadLatest }}
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
