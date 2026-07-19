// API service layer for Project DNA.
// Reuses the existing backend endpoints (no backend changes):
//   POST /v1/analyze         — run a full analysis
//   GET  /v1/entities         — list entities
//   GET  /v1/entities/{uid}    — get a single entity
//   GET  /v1/evidence          — list evidence
//   GET  /v1/evidence/{id}     — get evidence by id
//   POST /v1/insights/generate — generate insights
//   GET  /health | /status     — liveness / version
//
// All calls are made same-origin (frontend is served by FastAPI).

export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://project-dna-backend.onrender.com';

let currentBranch = '';

export function setApiBranch(branch) {
  currentBranch = branch;
}

export function getHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  if (currentBranch) {
    headers['X-Branch'] = currentBranch;
  }
  return headers;
}

async function readError(res) {
  const text = await res.text();
  let data = {};
  try { data = JSON.parse(text); } catch { /* non-json */ }
  return data.detail || data.message || text || `HTTP ${res.status}`;
}

export async function analyzeRepository(repo_path, options = {}) {
  const res = await fetch(`${API_BASE}/v1/analyze`, { ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repo_path }),
  });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { throw new Error(text || `HTTP ${res.status}`); }
  if (!res.ok) throw new Error(data.detail || data.message || `HTTP ${res.status}`);
  return data;
}

export async function getLatestAnalysis(options = {}) {
  const res = await fetch(`${API_BASE}/v1/analysis/latest`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getEntities(options = {}) {
  const res = await fetch(`${API_BASE}/v1/entities`, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(await readError(res));
  return data;
}

export async function getEntity(uid, options = {}) {
  const res = await fetch(`${API_BASE}/v1/entities/${encodeURIComponent(uid)}`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getEvidence(options = {}) {
  const res = await fetch(`${API_BASE}/v1/evidence`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getEvidenceById(id, options = {}) {
  const res = await fetch(`${API_BASE}/v1/evidence/${encodeURIComponent(id)}`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function generateInsights(options = {}) {
  const res = await fetch(`${API_BASE}/v1/insights/generate`, { ...options, method: 'POST' });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getHealth(options = {}) {
  const res = await fetch(`${API_BASE}/health`, options);
  return res.json();
}

export async function getStatus(options = {}) {
  const res = await fetch(`${API_BASE}/status`, options);
  return res.json();
}

// 1. Explorer
export async function getExplorerTree(options = {}) {
  const res = await fetch(`${API_BASE}/v1/explorer/tree`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getExplorerFile(path, options = {}) {
  const res = await fetch(`${API_BASE}/v1/explorer/file?path=${encodeURIComponent(path)}`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getExplorerSymbols(path, options = {}) {
  const res = await fetch(`${API_BASE}/v1/explorer/symbols?path=${encodeURIComponent(path)}`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 2. Dependency Graph
export async function getDependencyGraph(options = {}) {
  const res = await fetch(`${API_BASE}/v1/graph`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 3. Cross Repo
export async function getCrossRepoCompare(options = {}) {
  const res = await fetch(`${API_BASE}/v1/cross-repo/compare`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 4. Reviews
export async function getReviews(options = {}) {
  const res = await fetch(`${API_BASE}/v1/reviews`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function createReview(review, options = {}) {
  const res = await fetch(`${API_BASE}/v1/reviews`, { ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(review),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getReview(rid, options = {}) {
  const res = await fetch(`${API_BASE}/v1/reviews/${encodeURIComponent(rid)}`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function addReviewComment(rid, comment, options = {}) {
  const res = await fetch(`${API_BASE}/v1/reviews/${encodeURIComponent(rid)}/comments`, { ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(comment),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function updateReviewStatus(rid, status, options = {}) {
  const res = await fetch(`${API_BASE}/v1/reviews/${encodeURIComponent(rid)}/status?status=${encodeURIComponent(status)}`, { ...options,
    method: 'POST',
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 5. Refactoring Pipeline
export async function getPipelines(options = {}) {
  const res = await fetch(`${API_BASE}/v1/refactoring`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function createPipeline(pipeline, options = {}) {
  const res = await fetch(`${API_BASE}/v1/refactoring`, { ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(pipeline),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function runPipelineStep(pid, stepIndex, status, logMessage = '', options = {}) {
  const res = await fetch(
    `${API_BASE}/v1/refactoring/${encodeURIComponent(pid)}/steps/${stepIndex}?status=${encodeURIComponent(status)}&log_message=${encodeURIComponent(logMessage)}`,
    { method: 'POST' }
  , options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 6. Settings
export async function getSettings(options = {}) {
  const res = await fetch(`${API_BASE}/v1/settings`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function saveSettings(settings, options = {}) {
  const res = await fetch(`${API_BASE}/v1/settings`, { ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 7. Notifications
export async function getNotifications(options = {}) {
  const res = await fetch(`${API_BASE}/v1/notifications`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function readNotification(nid, options = {}) {
  const res = await fetch(`${API_BASE}/v1/notifications/${encodeURIComponent(nid)}/read`, { ...options,
    method: 'POST',
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function readAllNotifications(options = {}) {
  const res = await fetch(`${API_BASE}/v1/notifications/read-all`, { ...options,
    method: 'POST',
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function deleteNotification(nid, options = {}) {
  const res = await fetch(`${API_BASE}/v1/notifications/${encodeURIComponent(nid)}`, { ...options,
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 8. Organizations
export async function getTeams(options = {}) {
  const res = await fetch(`${API_BASE}/v1/organizations/teams`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function updateTeam(team, options = {}) {
  const res = await fetch(`${API_BASE}/v1/organizations/teams`, { ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(team),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function deleteTeam(teamId, options = {}) {
  const res = await fetch(`${API_BASE}/v1/organizations/teams/${encodeURIComponent(teamId)}`, { ...options,
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 9. AI Assistant
export async function queryAssistant(query, options = {}) {
  const res = await fetch(`${API_BASE}/v1/assistant`, { ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 10. Diff Viewer
export async function getFileDiff(path, version = 'original', options = {}) {
  const res = await fetch(
    `${API_BASE}/v1/diff?path=${encodeURIComponent(path)}&version=${encodeURIComponent(version)}`
  , options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 11. Global Search
export async function globalSearch(q, type = '', options = {}) {
  const res = await fetch(
    `${API_BASE}/v1/search?q=${encodeURIComponent(q)}${type ? `&type=${encodeURIComponent(type)}` : ''}`
  , options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 12. Advanced Repository Intelligence Center
export async function getAdvancedScores(options = {}) {
  const res = await fetch(`${API_BASE}/v1/advanced/scores`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getAdvancedArchitecture(viewType = 'dependency', options = {}) {
  const res = await fetch(`${API_BASE}/v1/advanced/architecture/views?view_type=${encodeURIComponent(viewType)}`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function postAdvancedChat(prompt, contextFiles = null, options = {}) {
  const res = await fetch(`${API_BASE}/v1/advanced/chat`, { ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, context_files: contextFiles }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function postAdvancedAction(actionType, targetFile = null, options = {}) {
  const res = await fetch(`${API_BASE}/v1/advanced/action`, { ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_type: actionType, target_file: targetFile }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getAdvancedGithubMetrics(options = {}) {
  const res = await fetch(`${API_BASE}/v1/advanced/github/metrics`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getAdvancedCodeSmells(options = {}) {
  const res = await fetch(`${API_BASE}/v1/advanced/code/smells`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getAdvancedSecurityReport(options = {}) {
  const res = await fetch(`${API_BASE}/v1/advanced/security/report`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getAdvancedPerformanceHotpaths(options = {}) {
  const res = await fetch(`${API_BASE}/v1/advanced/performance/hotpaths`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 13. Heatmaps
export async function getComplexityHeatmap(options = {}) {
  const res = await fetch(`${API_BASE}/v1/heatmaps/complexity`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getChangeHeatmap(timeFilter = 'all', options = {}) {
  const res = await fetch(`${API_BASE}/v1/heatmaps/change?time_filter=${encodeURIComponent(timeFilter)}`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getOwnershipHeatmap(options = {}) {
  const res = await fetch(`${API_BASE}/v1/heatmaps/ownership`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getSecurityHeatmap(options = {}) {
  const res = await fetch(`${API_BASE}/v1/heatmaps/security`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getPerformanceHeatmap(options = {}) {
  const res = await fetch(`${API_BASE}/v1/heatmaps/performance`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getCouplingHeatmap(options = {}) {
  const res = await fetch(`${API_BASE}/v1/heatmaps/coupling`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getDependencyHeatmap(options = {}) {
  const res = await fetch(`${API_BASE}/v1/heatmaps/dependency`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getFolderHeatmap(options = {}) {
  const res = await fetch(`${API_BASE}/v1/heatmaps/folder`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getRiskHeatmap(options = {}) {
  const res = await fetch(`${API_BASE}/v1/heatmaps/risk`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getGitActivityHeatmap(options = {}) {
  const res = await fetch(`${API_BASE}/v1/heatmaps/git-activity`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getPredictiveForecast(options = {}) {
  const res = await fetch(`${API_BASE}/v1/predictive/forecast`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getRefactoringAnalysis(options = {}) {
  const res = await fetch(`${API_BASE}/v1/refactoring/analysis`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function simulateRefactoring(payload, options = {}) {
  const res = await fetch(`${API_BASE}/v1/refactoring/simulate`, {
    ...options,
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getFlowJourney(options = {}) {
  const res = await fetch(`${API_BASE}/v1/insights/flow-journeys`, options);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function postBenchmarkingCompare(payload, options = {}) {
  const res = await fetch(`${API_BASE}/v1/predictive/benchmark/compare`, {
    ...options,
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function postBenchmarkingDiff(payload, options = {}) {
  const res = await fetch(`${API_BASE}/v1/predictive/benchmark/diff`, {
    ...options,
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}
