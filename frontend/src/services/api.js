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

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

async function readError(res) {
  const text = await res.text();
  let data = {};
  try { data = JSON.parse(text); } catch { /* non-json */ }
  return data.detail || data.message || text || `HTTP ${res.status}`;
}

export async function analyzeRepository(repo_path) {
  const res = await fetch(`${API_BASE}/v1/analyze`, {
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

export async function getLatestAnalysis() {
  const res = await fetch(`${API_BASE}/v1/analysis/latest`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getEntities() {
  const res = await fetch(`${API_BASE}/v1/entities`);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(await readError(res));
  return data;
}

export async function getEntity(uid) {
  const res = await fetch(`${API_BASE}/v1/entities/${encodeURIComponent(uid)}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getEvidence() {
  const res = await fetch(`${API_BASE}/v1/evidence`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getEvidenceById(id) {
  const res = await fetch(`${API_BASE}/v1/evidence/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function generateInsights() {
  const res = await fetch(`${API_BASE}/v1/insights/generate`, { method: 'POST' });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function getStatus() {
  const res = await fetch(`${API_BASE}/status`);
  return res.json();
}

// 1. Explorer
export async function getExplorerTree() {
  const res = await fetch(`${API_BASE}/v1/explorer/tree`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getExplorerFile(path) {
  const res = await fetch(`${API_BASE}/v1/explorer/file?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getExplorerSymbols(path) {
  const res = await fetch(`${API_BASE}/v1/explorer/symbols?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 2. Dependency Graph
export async function getDependencyGraph() {
  const res = await fetch(`${API_BASE}/v1/graph`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 3. Cross Repo
export async function getCrossRepoCompare() {
  const res = await fetch(`${API_BASE}/v1/cross-repo/compare`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 4. Reviews
export async function getReviews() {
  const res = await fetch(`${API_BASE}/v1/reviews`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function createReview(review) {
  const res = await fetch(`${API_BASE}/v1/reviews`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(review),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getReview(rid) {
  const res = await fetch(`${API_BASE}/v1/reviews/${encodeURIComponent(rid)}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function addReviewComment(rid, comment) {
  const res = await fetch(`${API_BASE}/v1/reviews/${encodeURIComponent(rid)}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(comment),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function updateReviewStatus(rid, status) {
  const res = await fetch(`${API_BASE}/v1/reviews/${encodeURIComponent(rid)}/status?status=${encodeURIComponent(status)}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 5. Refactoring Pipeline
export async function getPipelines() {
  const res = await fetch(`${API_BASE}/v1/refactoring`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function createPipeline(pipeline) {
  const res = await fetch(`${API_BASE}/v1/refactoring`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(pipeline),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function runPipelineStep(pid, stepIndex, status, logMessage = '') {
  const res = await fetch(
    `${API_BASE}/v1/refactoring/${encodeURIComponent(pid)}/steps/${stepIndex}?status=${encodeURIComponent(status)}&log_message=${encodeURIComponent(logMessage)}`,
    { method: 'POST' }
  );
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 6. Settings
export async function getSettings() {
  const res = await fetch(`${API_BASE}/v1/settings`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function saveSettings(settings) {
  const res = await fetch(`${API_BASE}/v1/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 7. Notifications
export async function getNotifications() {
  const res = await fetch(`${API_BASE}/v1/notifications`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function readNotification(nid) {
  const res = await fetch(`${API_BASE}/v1/notifications/${encodeURIComponent(nid)}/read`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function readAllNotifications() {
  const res = await fetch(`${API_BASE}/v1/notifications/read-all`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function deleteNotification(nid) {
  const res = await fetch(`${API_BASE}/v1/notifications/${encodeURIComponent(nid)}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 8. Organizations
export async function getTeams() {
  const res = await fetch(`${API_BASE}/v1/organizations/teams`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function updateTeam(team) {
  const res = await fetch(`${API_BASE}/v1/organizations/teams`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(team),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function deleteTeam(teamId) {
  const res = await fetch(`${API_BASE}/v1/organizations/teams/${encodeURIComponent(teamId)}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 9. AI Assistant
export async function queryAssistant(query) {
  const res = await fetch(`${API_BASE}/v1/assistant`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 10. Diff Viewer
export async function getFileDiff(path, version = 'original') {
  const res = await fetch(
    `${API_BASE}/v1/diff?path=${encodeURIComponent(path)}&version=${encodeURIComponent(version)}`
  );
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// 11. Global Search
export async function globalSearch(q, type = '') {
  const res = await fetch(
    `${API_BASE}/v1/search?q=${encodeURIComponent(q)}${type ? `&type=${encodeURIComponent(type)}` : ''}`
  );
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

