# Debug Report — API Hang on Repository Analysis

## Error

`POST /analyze` on `F:\code\ig\ig-costing-main` hangs indefinitely (timeout after 60+ seconds). The inner path `F:\code\ig\ig-costing-main\ig-costing-main` completes in 0.3s.

## Profiled Execution Times

All 16 pipeline stages instrumented with `time.perf_counter()`. Target: `F:\code\ig\ig-costing-main` (outer path).

### Before Fix (`node_modules` NOT in ALWAYS_IGNORE)

| # | Stage | Time | Notes |
|---|-------|------|-------|
| 1 | Repository Discovery | 904ms | 37,670 files found (all of node_modules) |
| 2 | Git History | 0ms | Not a git repo |
| 3 | Repository Indexing | 3,673ms | 37,670 files scanned + hashed |
| 4 | Tree-sitter Parsing | **75,477ms** | 14,142 JS files parsed |
| 5-16 | Remaining stages | ~3s | |
| | **Total** | **~80s+** | **Failed (timeout)** |

### After Fix (`node_modules` in ALWAYS_IGNORE)

| # | Stage | Time | Notes |
|---|-------|------|-------|
| 1 | Repository Discovery | 151ms | 726 files (node_modules excluded) |
| 2 | Git History | 0ms | Not a git repo |
| 3 | Repository Indexing | 544ms | 726 files (250 source) |
| 4 | Tree-sitter Parsing | 5,779ms | 196 files (includes `.next` build output) |
| 5 | AST Normalization | 3,859ms | 196 normalized |
| 6 | Symbol Extraction | 1ms | 76 symbols |
| 7 | Dependency Graph | 1ms | 0 edges |
| 8 | Entity Graph | 3ms | 424 entities, 228 relations |
| 9 | SCM Storage | 111ms | |
| 10 | Evidence Store | 42ms | |
| 11 | Structural Engine | 15ms | |
| 12 | Evolution Engine | 6ms | |
| 13 | Knowledge Engine | 4ms | |
| 14 | Risk Engine | 13ms | |
| 15 | Reasoning Engine | 2ms | |
| 16 | Response Serialization | 9ms | |
| | **Total** | **10.5s** | **Pass (under 20s)** |

## Root Cause

`backend/dna/discovery/scanner.py:6` — `ALWAYS_IGNORE` did not include `"node_modules"`.

When analyzing a directory that contains `node_modules` but has no `.gitignore` at that level (e.g., the outer `F:\code\ig\ig-costing-main` directory doesn't have its own `.gitignore`; only the inner `ig-costing-main` has one), `scan_files` walks the entire `node_modules` tree (37,670 files). All `.js`/`.ts` files inside `node_modules` are classified as `FileCategory.SOURCE`, then sent to Tree-sitter for parsing. This results in 14,142 files being parsed, taking **75+ seconds**.

## Fix Applied

### `backend/dna/discovery/scanner.py` line 6

```python
# Before:
ALWAYS_IGNORE: set[str] = {".git", ".dnaignore", ".gitignore"}

# After:
ALWAYS_IGNORE: set[str] = {".git", ".dnaignore", ".gitignore", "node_modules"}
```

`node_modules` is a universal convention for vendored JavaScript dependencies. These files are never project source code and should always be excluded from scans, regardless of `.gitignore` presence.

The scanner already checks path components against `ignore` (which includes `ALWAYS_IGNORE`). When it encounters a directory named `node_modules`, it excludes it from `os.walk` traversal, preventing all descendant files from being discovered.

## Regression Tests Added

| Test | File | What it verifies |
|------|------|-----------------|
| `test_node_modules_ignored` | `tests/test_discovery/test_scanner_edge.py` | `scan_files` excludes `node_modules` directory and all its contents |
| `test_analysis_with_node_modules` | `tests/test_api/test_analysis.py` | `run_full_analysis` skips `node_modules` (500 JS files → 1 source file) |

## Test Results

```
262 passed in 6.80s
```

(Up from 260 — 2 new regression tests.)

`ruff`: All checks passed (zero warnings).

## Total Analysis Time

| | Before Fix | After Fix | Improvement |
|--|-----------|-----------|-------------|
| Direct pipeline | ~80s+ (timeout) | **10.5s** | ~8x faster |
| API endpoint | timeout (60s+) | **15.7s** | Functional |
| Inner path (control) | 0.3s | 0.25s | No regression |
