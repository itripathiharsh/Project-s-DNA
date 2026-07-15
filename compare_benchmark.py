"""Produce BEFORE (baseline) and AFTER (optimized) benchmarks in one run,
by toggling the optimizations on/off via runtime monkey-patching. This avoids
needing to revert the source files and gives an apples-to-apples comparison on
the same repository.

BEFORE mode simulates the original implementation:
- Indexer recomputes content hashes for EVERY file (compute_file_hash per file)
- Hit should_ignore() recompiling all regexes each call (use raw should_ignore)
- Indexer re-walks the filesystem and re-parses gitignore
- Evidence store commits after every add_evidence
- Knowledge engine calls get_file_blame sequentially per file

AFTER mode uses the optimized code paths exactly as checked in.
"""
import sys
import os
import time
import logging
import shutil
import sqlite3
import tempfile
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "backend"))
os.environ.setdefault("DNA_TIMING", "0")

import sqlite3 as _sqlite

from dna.logging import configure_logging
from dna.models import FileCategory
import dna.discovery.scanner as scanner_mod
import dna.discovery.orchestrator as disc_orch
import dna.indexer.orchestrator as idx_orch
import dna.indexer.inventory as inv_mod
import dna.indexer.hasher as hasher_mod
import dna.engines.knowledge as knowledge_mod
import dna.evidence.store as es
import dna.parser.orchestrator as po


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


# ---- baseline simulation helpers ----------------------------------------------

def _baseline_should_ignore(file_path, patterns):
    """Original non-cached should_ignore: recompiles all patterns every call."""
    import re
    if not patterns:
        return False
    from dna.discovery.ignore import translate_pattern
    file_path = file_path.replace("\\", "/")
    is_dir = file_path.endswith("/")
    clean_path = file_path.strip("/")
    compiled = []
    for pattern in patterns:
        pattern = pattern.strip()
        if not pattern or pattern.startswith("#"):
            continue
        compiled.append(translate_pattern(pattern))

    def is_path_ignored(p, is_d):
        ignored = False
        for regex, is_negated, is_dir_only in compiled:
            if is_dir_only and not is_d:
                continue
            if regex.search(p):
                ignored = not is_negated
        return ignored

    parts = clean_path.split("/")
    for i in range(1, len(parts)):
        ancestor = "/".join(parts[:i])
        if is_path_ignored(ancestor, is_d=True):
            return True
    return is_path_ignored(clean_path, is_d=is_dir)


def _baseline_scan_files(path, ignore_patterns=None):
    """Original scanner behavior: per-call should_ignore (no compiled cache)."""
    if not os.path.isdir(path):
        return []
    from dna.config import get_config
    from dna.discovery.ignore import should_ignore as _orig_should_ignore  # not used
    from dna.models import FileInfo
    from dna.discovery.languages import detect_language, is_source_file
    config = get_config()
    all_patterns = list(config.always_ignore)
    if ignore_patterns:
        all_patterns.extend(ignore_patterns)
    results = []
    root = os.path.normpath(path)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace("\\", "/")
        if rel_dir == ".":
            rel_dir = ""
        pruned = []
        for d in dirnames:
            d_rel = f"{rel_dir}/{d}" if rel_dir else d
            if not _baseline_should_ignore(d_rel + "/", all_patterns):
                pruned.append(d)
        dirnames[:] = pruned
        for filename in filenames:
            rel_path = f"{rel_dir}/{filename}" if rel_dir else filename
            if _baseline_should_ignore(rel_path, all_patterns):
                continue
            full_path = os.path.join(dirpath, filename)
            try:
                stat = os.stat(full_path)
                size = stat.st_size
            except OSError:
                continue
            if size > config.max_file_size_bytes:
                continue
            _, ext = os.path.splitext(filename)
            if ext.lower() in config.ignore_extensions:
                continue
            if ext.lower() not in config.supported_extensions:
                continue
            language = detect_language(ext)
            results.append(FileInfo(
                path=full_path, relative_path=rel_path, filename=filename,
                extension=ext, language=language, size_bytes=size,
                is_directory=False, is_source=is_source_file(ext),
            ))
    return results


def _baseline_build_file_inventory(files, repo_metadata, previous_inventory=None):
    """Original inventory: hash every file, classify every file twice via loop."""
    from dna.models import IndexedFile, FileInventory
    from dna.indexer.classifier import classify_file, build_classification_map
    from dna.indexer.hasher import compute_file_hash, detect_changes
    indexed = []
    new_hashes = {}
    categories = build_classification_map(files, repo_metadata)
    for f in files:
        cat = classify_file(f, repo_metadata)
        mtime = 0.0
        try: mtime = os.path.getmtime(f.path)
        except OSError: pass
        content_hash = compute_file_hash(f.path)   # <-- always hashes
        new_hashes[f.relative_path] = content_hash
        indexed.append(IndexedFile(
            path=f.path, relative_path=f.relative_path, filename=f.filename,
            extension=f.extension, language=f.language, size_bytes=f.size_bytes,
            is_directory=f.is_directory, is_source=f.is_source, category=cat,
            content_hash=content_hash, mtime=mtime,
        ))
    if previous_inventory:
        old_map = {f.relative_path: f.content_hash for f in previous_inventory.files}
        changes = detect_changes(old_map, new_hashes)
        for f in indexed:
            if f.relative_path in changes.get("added", {}):
                f.change_type = "added"
            elif f.relative_path in changes.get("modified", {}):
                f.change_type = "modified"
            elif f.relative_path in changes.get("removed", {}):
                f.change_type = "removed"
    total_size = sum(f.size_bytes for f in indexed)
    return FileInventory(files=indexed, categories=categories,
                        total_files=len(indexed), total_size_bytes=total_size)


def _baseline_index_repository(path, repo_metadata, previous_inventory=None):
    """Original indexer: re-walk filesystem + re-parse gitignore instead of cache."""
    from dna.discovery.scanner import scan_files  # patched above
    from dna.discovery.ignore import parse_gitignore, parse_dnaignore
    gitignore = parse_gitignore(path)
    dnaignore = parse_dnaignore(path)
    all_ignore = list(set(gitignore + dnaignore))
    # Force the baseline scanner (which uses uncached should_ignore)
    files = _baseline_scan_files(path, all_ignore)
    return _baseline_build_file_inventory(files, repo_metadata, previous_inventory)


def _baseline_file_blame(repo_path, file_path):
    """Original single-file git blame."""
    import shutil, subprocess
    from dna.discovery.git import is_git_repository
    from dna.discovery.orchestrator import NotAGitRepositoryError
    from dna.git_history.errors import GitNotInstalledError, GitCommandError
    if shutil.which("git") is None:
        raise GitNotInstalledError()
    if not is_git_repository(repo_path):
        raise NotAGitRepositoryError(repo_path)
    rel = file_path
    if os.path.isabs(file_path):
        try: rel = os.path.relpath(file_path, repo_path)
        except ValueError: pass
    cmd = ["git", "blame", "--line-porcelain", rel]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path, timeout=30)
    except FileNotFoundError:
        raise GitNotInstalledError()
    except subprocess.TimeoutExpired:
        raise GitCommandError(" ".join(cmd), -1, "Timeout expired")
    if proc.returncode != 0:
        return {}
    counts = {}
    for line in proc.stdout.splitlines():
        if line.startswith("author "):
            name = line[len("author "):].strip()
            if name == "Not Committed Yet":
                name = "Uncommitted"
            counts[name] = counts.get(name, 0) + 1
    return counts


def apply_baseline_patches():
    """Apply baseline-simulation patches to the modules that dna.api.analysis
    actually references. The pipeline imports these names directly, so we must
    rebind them on the analysis module too, not just on their origin modules.
    """
    import dna.api.analysis as analysis
    patches = []

    # 1. Inventory always hashes (patched on inv_mod AND on the indirection in analysis)
    orig_inv_build = inv_mod.build_file_inventory
    inv_mod.build_file_inventory = _baseline_build_file_inventory
    patches.append(("inv_mod.build_file_inventory", inv_mod, "build_file_inventory", orig_inv_build))
    # (analysis.py does not import build_file_inventory directly, but the indexer uses inv_mod's binding)

    # 2. Indexer re-walks (no cache reuse) + uses old scanner
    orig_idx = idx_orch.index_repository
    idx_orch.index_repository = _baseline_index_repository
    analysis.index_repository = _baseline_index_repository  # analysis imports it by name
    patches.append(("idx_orch.index_repository", idx_orch, "index_repository", orig_idx))
    patches.append(("analysis.index_repository", analysis, "index_repository", orig_idx))

    # 3. Knowledge engine uses sequential per-file blame
    orig_know = knowledge_mod.analyze_knowledge

    def baseline_knowledge(commit_history, entity_graph=None, evidence_store=None, repo_path=None):
        # Inline copy of original knowledge logic using _baseline_file_blame
        import logging
        log = logging.getLogger("dna.engines.knowledge")
        log.info("Starting knowledge analysis")
        author_stats = commit_history.author_stats
        total_commits = max(len(commit_history.commits), 1)
        contributions = []
        for a in author_stats:
            share = round(a.commit_count / total_commits, 4) if total_commits > 0 else 0
            contributions.append({"name": a.name, "email": a.email,
                                  "commit_count": a.commit_count, "share": share,
                                  "insertions": a.insertions, "deletions": a.deletions})
        contributions.sort(key=lambda x: -x["commit_count"])
        top = contributions[0]["name"] if contributions else None
        top_share = contributions[0]["share"] if contributions else 0
        bus_factor = 0; cum = 0
        for c in contributions:
            cum += c["share"]; bus_factor += 1
            if cum >= 0.5: break
        if entity_graph:
            file_entities = [e for e in entity_graph.entities if e.kind == "file"]
            ownership = {}
            for fe in file_entities:
                score = 0.0; primary_owner = top
                blame = None
                if repo_path:
                    try: blame = _baseline_file_blame(repo_path, fe.file_path)
                    except Exception: blame = None
                if blame:
                    tl = sum(blame.values())
                    if tl > 0:
                        primary_owner = max(blame, key=blame.get)
                        score = blame[primary_owner] / tl
                    elif contributions:
                        score = contributions[0]["share"]
                elif contributions:
                    score = contributions[0]["share"]
                ownership[fe.file_path] = {"primary_owner": primary_owner,
                                            "ownership_score": round(score, 4)}
            expertise = {a.name: {"expertise_score": round(a.commit_count/total_commits, 4),
                                  "commit_count": a.commit_count} for a in author_stats}
        else:
            ownership = {}; expertise = {}
        bfr = "high" if bus_factor <= 2 else "medium" if bus_factor <= 4 else "low"
        result = {"total_authors": len(author_stats),
                  "contributions": contributions[:10], "top_contributor": top,
                  "top_contributor_share": top_share, "bus_factor": bus_factor,
                  "bus_factor_risk": bfr, "ownership_scores": ownership,
                  "expertise_scores": expertise}
        if evidence_store:
            for c in contributions:
                evidence_store.add_evidence("author_contribution",
                    {"author": c["name"], "percentage": c["share"], "commits": c["commit_count"]},
                    source="knowledge_engine")
            evidence_store.add_evidence("ownership_score",
                {"primary_owner": top, "ownership_share": top_share,
                 "bus_factor": bus_factor, "bus_factor_risk": bfr},
                source="knowledge_engine")
        log.info("Knowledge analysis completed. Bus factor: %d (risk: %s)", bus_factor, bfr)
        return result
    knowledge_mod.analyze_knowledge = baseline_knowledge
    analysis.analyze_knowledge = baseline_knowledge
    patches.append(("knowledge.analyze_knowledge", knowledge_mod, "analyze_knowledge", orig_know))
    patches.append(("analysis.analyze_knowledge", analysis, "analyze_knowledge", orig_know))

    # 4. Evidence store: per-row commit (disable transaction batching on analysis)
    orig_analysis_run = analysis.run_full_analysis
    # Re-implement run_full_analysis so the per-engine evidence writes are NOT wrapped in
    # ev_store.transaction() — restoring the per-row commit behaviour.
    import tempfile, os
    from dna.discovery.orchestrator import discover_repository, NotAGitRepositoryError
    from dna.git_history.miner import mine_git_history
    from dna.parser.orchestrator import parse_repository
    from dna.normalizer.orchestrator import normalize_parsed_files
    from dna.symbols.indexer import build_symbol_index
    from dna.graph.builder import build_dependency_graph
    from dna.entities.builder import build_entity_graph
    from dna.storage.store import SCStore
    from dna.config import get_config
    from dna.logging import log_stage, configure_logging
    from dna.models import CommitHistory

    def baseline_run_full_analysis(repo_path):
        configure_logging(level=get_config().log_level)
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = os.path.join(tmpdir, "sc_store.db")
            ev_path = os.path.join(tmpdir, "ev_store.db")
            with log_stage("discovery"): repo = discover_repository(repo_path)
            with log_stage("git_history"):
                try: history = mine_git_history(repo_path)
                except NotAGitRepositoryError: history = CommitHistory()
            with log_stage("indexer"): inventory = idx_orch.index_repository(repo_path, repo)  # patched baseline
            with log_stage("parser"): parsed = parse_repository(inventory)
            with log_stage("normalizer"): normalized = normalize_parsed_files(parsed)
            with log_stage("symbols"): symbol_index = build_symbol_index(normalized)
            with log_stage("graph"): dep_graph = build_dependency_graph(normalized, symbol_index)
            with log_stage("entities"): entity_graph = build_entity_graph(normalized, symbol_index, dep_graph)
            with SCStore(store_path) as sc_store:
                sc_store.save_entity_graph(entity_graph)
                sc_store.set_metadata("repo_path", repo_path)
                sc_store.set_metadata("analysis_time", "now")
            with es.EvidenceStore(ev_path) as ev_store:
                # NO transaction batching — original per-row commit behaviour
                _structural = analysis.analyze_structure
                _evolution  = analysis.analyze_evolution
                _risks      = analysis.analyze_risks
                _insights   = analysis.generate_insights
                with log_stage("structural_engine"):
                    structural = _structural(entity_graph, ev_store)
                with log_stage("evolution_engine"):
                    evolution = _evolution(history, entity_graph, evidence_store=ev_store)
                with log_stage("knowledge_engine"):
                    knowledge = knowledge_mod.analyze_knowledge(history, entity_graph, ev_store, repo_path=repo_path)
                with log_stage("risk_engine"):
                    risks = _risks(entity_graph, dep_graph, ev_store)
                with log_stage("reasoning"):
                    insights = _insights(ev_store)
            return {
                "repository": {"path": repo.path if repo else repo_path,
                                "is_git": repo.is_git if repo else False},
                "summary": {
                    "total_commits": evolution.get("total_commits", 0),
                    "total_authors": evolution.get("total_authors", 0),
                    "total_files": inventory.total_files if inventory else 0,
                    "source_files": len([f for f in inventory.files if f.category == "source"]) if inventory else 0,
                    "test_files": len([f for f in inventory.files if f.category == "test"]) if inventory else 0,
                },
                "evolution": evolution, "knowledge": knowledge, "risk": risks,
                "structural": structural, "insights": insights,
            }
    analysis.run_full_analysis = baseline_run_full_analysis
    patches.append(("analysis.run_full_analysis", analysis, "run_full_analysis", orig_analysis_run))

    return patches


def restore(patches):
    for _, mod, attr, orig in patches:
        setattr(mod, attr, orig)


# ---- measurement harness -------------------------------------------------------

def run_once(label):
    import dna.api.analysis as analysis
    from dna.discovery.orchestrator import clear_discovery_cache

    recorder = StageRecorder()
    logging.getLogger().addHandler(recorder)
    logging.getLogger().setLevel(logging.WARNING)

    git_counts = {"git_calls": 0, "blame_calls": 0}
    import dna.git_history.commit_parser as cp
    import dna.git_history.blame as bl
    orig_run = cp._run_git
    orig_run_stream = cp._run_git_stream
    orig_blame_one = bl._blame_one
    def wr(*a, **kw): git_counts["git_calls"] += 1; return orig_run(*a, **kw)
    def wrs(*a, **kw): git_counts["git_calls"] += 1; return orig_run_stream(*a, **kw)
    def wb(*a, **kw): git_counts["blame_calls"] += 1; return orig_blame_one(*a, **kw)
    cp._run_git = wr; cp._run_git_stream = wrs; bl._blame_one = wb

    sql_counts = {"commits": 0}
    orig_es_add = es.EvidenceStore.add_evidence
    orig_es_tx = getattr(es.EvidenceStore, "transaction", None)
    def wrap_add(self, *a, **kw):
        r = orig_es_add(self, *a, **kw)
        if getattr(self, "_tx_depth", 0) == 0:
            sql_counts["commits"] += 1
        return r
    @contextlib.contextmanager
    def wrap_tx(self):
        if orig_es_tx is not None:
            with orig_es_tx(self):
                yield
        else:
            yield
        sql_counts["commits"] += 1  # the single commit at the end of the batch
    es.EvidenceStore.add_evidence = wrap_add
    if orig_es_tx is not None:
        es.EvidenceStore.transaction = wrap_tx

    parser_counts = {"source_files": 0}
    orig_parse = po.parse_repository
    def wp(inventory, max_workers=None):
        parser_counts["source_files"] = sum(1 for f in inventory.files if f.category == FileCategory.SOURCE)
        return orig_parse(inventory, max_workers)
    po.parse_repository = wp

    snap_dir = tempfile.mkdtemp(prefix=f"dna_{label}_")
    snap_path = os.path.join(snap_dir, "ev.db")
    orig_es_close = es.EvidenceStore.close
    def es_close(self):
        if self._conn:
            try: self._conn.execute("PRAGMA wal_checkpoint(FULL)")
            except Exception: pass
            try: shutil.copyfile(self.db_path, snap_path)
            except Exception: pass
        orig_es_close(self)
    es.EvidenceStore.close = es_close

    repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "tests", "_perf_target")
    repo = os.path.abspath(repo)

    t0 = time.perf_counter()
    clear_discovery_cache()
    result = analysis.run_full_analysis(repo)
    total_ms = (time.perf_counter() - t0) * 1000.0

    cp._run_git = orig_run; cp._run_git_stream = orig_run_stream; bl._blame_one = orig_blame_one
    es.EvidenceStore.add_evidence = orig_es_add
    if orig_es_tx is not None:
        es.EvidenceStore.transaction = orig_es_tx
    po.parse_repository = orig_parse
    es.EvidenceStore.close = orig_es_close
    logging.getLogger().removeHandler(recorder)

    ev_rows = 0
    if os.path.exists(snap_path):
        try:
            c = sqlite3.connect(snap_path)
            ev_rows = c.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
            c.close()
        except Exception:
            pass
    shutil.rmtree(snap_dir, ignore_errors=True)
    return {
        "total_ms": total_ms,
        "stages": dict(recorder.stages),
        "files_scanned": result["summary"]["total_files"],
        "files_parsed": parser_counts["source_files"],
        "git_calls": git_counts["git_calls"],
        "blame_calls": git_counts["blame_calls"],
        "commits": sql_counts["commits"],
        "ev_rows": ev_rows,
    }


def main():
    repo = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "tests", "_perf_target"))
    configure_logging(level="WARNING")

    # AFTER first (current optimized code)
    after = run_once("after")

    # BEFORE: apply baseline simulation patches, run, restore
    patches = apply_baseline_patches()
    try:
        before = run_once("before")
    finally:
        restore(patches)

    stage_order = ["discovery", "git_history", "indexer", "parser", "normalizer",
                   "symbols", "graph", "entities", "structural_engine",
                   "evolution_engine", "knowledge_engine", "risk_engine", "reasoning"]

    print()
    print("=" * 70)
    print(f"  BEFORE / AFTER BENCHMARK   target={repo}")
    print("=" * 70)
    print(f"{'Stage':<22}{'BEFORE (ms)':>14}{'AFTER (ms)':>14}{'Speedup':>10}")
    print("-" * 60)
    for s in stage_order:
        b = before["stages"].get(s); a = after["stages"].get(s)
        bs = f"{b:.3f}" if isinstance(b, (int, float)) else "—"
        as_ = f"{a:.3f}" if isinstance(a, (int, float)) else "—"
        su = ""
        if isinstance(b, (int, float)) and isinstance(a, (int, float)) and a > 0:
            su = f"{b/a:.2f}x"
        print(f"{s:<22}{bs:>14}{as_:>14}{su:>10}")
    print("-" * 60)
    print(f"{'TOTAL (wall)':<22}{before['total_ms']:>14.3f}{after['total_ms']:>14.3f}"
          f"{(before['total_ms']/after['total_ms']) if after['total_ms']>0 else 0:>9.2f}x")
    print()
    print(f"{'Metric':<28}{'BEFORE':>14}{'AFTER':>14}")
    print("-" * 56)
    print(f"{'Files scanned':<28}{before['files_scanned']:>14}{after['files_scanned']:>14}")
    print(f"{'Files parsed':<28}{before['files_parsed']:>14}{after['files_parsed']:>14}")
    print(f"{'Git subprocess calls':<28}{before['git_calls']+before['blame_calls']:>14}{after['git_calls']+after['blame_calls']:>14}")
    print(f"{'  - log/branch/tag':<28}{before['git_calls']:>14}{after['git_calls']:>14}")
    print(f"{'  - git blame':<28}{before['blame_calls']:>14}{after['blame_calls']:>14}")
    print(f"{'SQLite commits':<28}{before['commits']:>14}{after['commits']:>14}")
    print(f"{'Evidence rows written':<28}{before['ev_rows']:>14}{after['ev_rows']:>14}")


if __name__ == "__main__":
    main()
