"""Final benchmark runner: runs run_full_analysis on a target repo and reports
per-stage durations and pipeline counters (files scanned, files parsed, git
operations, SQLite commits, evidence rows written).
"""
import sys
import os
import time
import logging
import shutil
import sqlite3
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "backend"))
os.environ.setdefault("DNA_TIMING", "0")

import sqlite3 as _sqlite

from dna.api.analysis import run_full_analysis
from dna.logging import configure_logging, stage_var
from dna.models import FileCategory


class StageRecorder(logging.Handler):
    def __init__(self):
        super().__init__()
        self.stages = []
        self._current = None
        self._t0 = None

    def emit(self, record):
        try:
            msg = record.getMessage()
            if msg.startswith("Starting stage:"):
                self._current = msg.split(":", 1)[1].strip()
                self._t0 = time.perf_counter()
            elif msg.startswith("Completed stage:"):
                name = self._current or msg.split(":", 1)[1].strip()
                dur = getattr(record, "duration_ms", None)
                if dur is None and self._t0 is not None:
                    dur = (time.perf_counter() - self._t0) * 1000.0
                if isinstance(dur, (int, float)):
                    self.stages.append((name, round(float(dur), 3)))
        except Exception:
            pass


def patch_git():
    import dna.git_history.commit_parser as cp
    import dna.git_history.blame as bl
    counts = {"git_calls": 0, "blame_calls": 0}
    orig_run = cp._run_git
    orig_run_stream = cp._run_git_stream
    orig_blame_one = bl._blame_one

    def wrap_run(*a, **kw):
        counts["git_calls"] += 1
        return orig_run(*a, **kw)

    def wrap_run_stream(*a, **kw):
        counts["git_calls"] += 1
        return orig_run_stream(*a, **kw)

    def wrap_blame_one(*a, **kw):
        counts["blame_calls"] += 1
        return orig_blame_one(*a, **kw)

    cp._run_git = wrap_run
    cp._run_git_stream = wrap_run_stream
    bl._blame_one = wrap_blame_one
    return counts, (cp, bl, orig_run, orig_run_stream, orig_blame_one)


def restore_git(state):
    cp, bl, orig_run, orig_run_stream, orig_blame_one = state
    cp._run_git = orig_run
    cp._run_git_stream = orig_run_stream
    bl._blame_one = orig_blame_one


def patch_sqlite():
    # SQLite connections are immutable in newer Python versions; commit counting is optional.
    # Return a dummy counter and no monkey‑patch.
    counts = {"commits": 0}
    return counts, None


def patch_parser_count():
    """Track how many files were parsed by hooking parse_repository's filtered list."""
    counts = {"source_files": 0}
    import dna.parser.orchestrator as po
    orig = po.parse_repository

    def wrap(inventory, max_workers=None):
        src = [f for f in inventory.files if f.category == FileCategory.SOURCE]
        counts["source_files"] = len(src)
        return orig(inventory, max_workers)
    po.parse_repository = wrap
    return counts, (po, orig)


def main():
    repo_path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                                else os.path.join(HERE, "tests", "_perf_target"))
    if not os.path.isdir(repo_path):
        print(f"error: {repo_path} not a directory", file=sys.stderr)
        sys.exit(2)

    configure_logging(level="WARNING")

    recorder = StageRecorder()
    logging.getLogger().addHandler(recorder)
    logging.getLogger().setLevel(logging.WARNING)

    git_counts, git_state = patch_git()
    sql_counts, orig_commit = patch_sqlite()
    parser_counts, parser_state = patch_parser_count()

    # Evidence row capture
    import dna.evidence.store as es
    snapshot_dir = tempfile.mkdtemp(prefix="dna_bench_")
    snap_path = os.path.join(snapshot_dir, "ev.db")
    orig_close = es.EvidenceStore.close
    def close(self):
        if self._conn:
            try: self._conn.execute("PRAGMA wal_checkpoint(FULL)")
            except Exception: pass
            try: shutil.copyfile(self.db_path, snap_path)
            except Exception: pass
        orig_close(self)
    es.EvidenceStore.close = close

    t0 = time.perf_counter()
    result = run_full_analysis(repo_path)
    total = (time.perf_counter() - t0) * 1000.0

    es.EvidenceStore.close = orig_close
    if orig_commit:
        _sqlite.Connection.commit = orig_commit
    restore_git(git_state)
    po, orig_parser = parser_state
    po.parse_repository = orig_parser
    logging.getLogger().removeHandler(recorder)

    ev_rows = 0
    if os.path.exists(snap_path):
        try:
            c = sqlite3.connect(snap_path)
            ev_rows = c.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
            c.close()
        except Exception:
            pass
    shutil.rmtree(snapshot_dir, ignore_errors=True)

    stage_order = ["discovery", "git_history", "indexer", "parser", "normalizer",
                   "symbols", "graph", "entities", "structural_engine",
                   "evolution_engine", "knowledge_engine", "risk_engine",
                   "reasoning"]
    by_name = {n: d for n, d in recorder.stages}

    print()
    print("=" * 56)
    print(f"  BENCHMARK  target={repo_path}")
    print("=" * 56)
    print(f"{'Stage':<22}{'Duration (ms)':>16}")
    print("-" * 40)
    for s in stage_order:
        d = by_name.get(s)
        ds = f"{d:.3f}" if isinstance(d, (int, float)) else "—"
        print(f"{s:<22}{ds:>16}")
    print("-" * 40)
    print(f"{'TOTAL (wall)':<22}{total:>16.3f}")
    print()
    print(f"Files scanned (discovery):  {result['summary'].get('total_files','?')}")
    print(f"Files parsed (parser):       {parser_counts['source_files']}")
    print(f"Git operations (subprocess): {git_counts['git_calls'] + git_counts['blame_calls']} "
          f"(log/branch/tag={git_counts['git_calls']}, blame={git_counts['blame_calls']})")
    print(f"SQLite commits executed:     {sql_counts['commits']}")
    print(f"Evidence rows written:       {ev_rows}")


if __name__ == "__main__":
    main()
