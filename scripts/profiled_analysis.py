"""Instrumented analysis pipeline - prints timing for every stage."""
import sys, os, time, traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dna.discovery.orchestrator import discover_repository, NotAGitRepositoryError
from dna.git_history.miner import mine_git_history
from dna.indexer.orchestrator import index_repository
from dna.parser.orchestrator import parse_repository
from dna.normalizer.orchestrator import normalize_parsed_files
from dna.symbols.indexer import build_symbol_index
from dna.graph.builder import build_dependency_graph
from dna.entities.builder import build_entity_graph
from dna.storage.store import SCStore
from dna.evidence.store import EvidenceStore
from dna.engines.structural import analyze_structure
from dna.engines.evolution import analyze_evolution
from dna.engines.knowledge import analyze_knowledge
from dna.engines.risk import analyze_risks
from dna.reasoning.engine import generate_insights
from dna.models import CommitHistory
import tempfile


def log_stage(name, start, end, detail=""):
    elapsed = (end - start) * 1000
    flag = " *** SLOW ***" if elapsed > 5000 else ""
    print(f"  [{name:40s}] {elapsed:8.1f}ms{flag} {detail}")


def log_start(name):
    print(f"\n>>> {name}")
    return time.perf_counter()


def run_profiled(repo_path: str):
    print(f"Analyzing: {repo_path}")
    overall_start = time.perf_counter()

    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "sc_store.db")
        ev_path = os.path.join(tmpdir, "ev_store.db")

        # 1. Repository Discovery
        t0 = log_start("1. Repository Discovery")
        repo = discover_repository(repo_path)
        log_stage("1. Repository Discovery", t0, time.perf_counter(),
                  f"is_git={repo.is_git if repo else 'N/A'}, files={repo.file_count if repo else 0}")

        # 2. Git History
        t0 = log_start("2. Git History")
        try:
            history = mine_git_history(repo_path)
            log_stage("2. Git History", t0, time.perf_counter(),
                      f"commits={len(history.commits)}, branches={history.total_branches}")
        except NotAGitRepositoryError:
            history = CommitHistory()
            log_stage("2. Git History", t0, time.perf_counter(), "NOT a git repo - empty history")

        # 3. Repository Indexing
        t0 = log_start("3. Repository Indexing")
        inventory = index_repository(repo_path, repo)
        n_files = len(inventory.files)
        log_stage("3. Repository Indexing", t0, time.perf_counter(),
                  f"files={n_files}, source={sum(1 for f in inventory.files if f.category == 'source')}")

        # 4. Tree-sitter Parsing
        t0 = log_start("4. Tree-sitter Parsing")
        parsed = parse_repository(inventory)
        parse_elapsed = (time.perf_counter() - t0) * 1000
        log_stage("4. Tree-sitter Parsing", t0, time.perf_counter(),
                  f"parsed={len(parsed)} files")
        # Detailed progress if slow
        if parse_elapsed > 5000:
            for p in parsed:
                n_syms = len(p.symbols.symbols) if hasattr(p.symbols, 'symbols') else 0
                n_imps = len(p.imports) if hasattr(p, 'imports') and p.imports else 0
                print(f"    parsed: {p.file_path} ({n_syms} symbols, {n_imps} imports)")

        # 5. AST Normalization
        t0 = log_start("5. AST Normalization")
        normalized = normalize_parsed_files(parsed)
        log_stage("5. AST Normalization", t0, time.perf_counter(),
                  f"normalized={len(normalized)} files")

        # 6. Symbol Extraction
        t0 = log_start("6. Symbol Extraction")
        symbol_index = build_symbol_index(normalized)
        sym_count = len(symbol_index.symbols) if hasattr(symbol_index, 'symbols') else 0
        log_stage("6. Symbol Extraction", t0, time.perf_counter(),
                  f"symbols={sym_count}")

        # 7. Dependency Graph
        t0 = log_start("7. Dependency Graph")
        dep_graph = build_dependency_graph(normalized, symbol_index)
        n_edges = len(dep_graph.edges) if hasattr(dep_graph, 'edges') else 0
        log_stage("7. Dependency Graph", t0, time.perf_counter(),
                  f"edges={n_edges}")

        # 8. Entity Graph
        t0 = log_start("8. Entity Graph Construction")
        entity_graph = build_entity_graph(normalized, symbol_index, dep_graph)
        n_entities = len(entity_graph.entities) if hasattr(entity_graph, 'entities') else 0
        n_relations = len(entity_graph.relations) if hasattr(entity_graph, 'relations') else 0
        log_stage("8. Entity Graph Construction", t0, time.perf_counter(),
                  f"entities={n_entities}, relations={n_relations}")

        # 9. SCM Storage
        t0 = log_start("9. SCM Storage")
        with SCStore(store_path) as sc_store:
            sc_store.save_entity_graph(entity_graph)
            sc_store.set_metadata("repo_path", repo_path)
            sc_store.set_metadata("analysis_time", "now")
        log_stage("9. SCM Storage", t0, time.perf_counter())

        # 10. Evidence Storage (opening)
        t0 = log_start("10. Evidence Store Open")
        ev_store = EvidenceStore(ev_path)
        ev_store.open()
        log_stage("10. Evidence Store Open", t0, time.perf_counter())

        # 11. Structural Engine
        t0 = log_start("11. Structural Engine")
        structural = analyze_structure(entity_graph, ev_store)
        log_stage("11. Structural Engine", t0, time.perf_counter())

        # 12. Evolution Engine
        t0 = log_start("12. Evolution Engine")
        evolution = analyze_evolution(history, evidence_store=ev_store)
        log_stage("12. Evolution Engine", t0, time.perf_counter())

        # 13. Knowledge Engine
        t0 = log_start("13. Knowledge Engine")
        knowledge = analyze_knowledge(history, entity_graph, ev_store)
        log_stage("13. Knowledge Engine", t0, time.perf_counter())

        # 14. Risk Engine
        t0 = log_start("14. Risk Engine")
        risks = analyze_risks(entity_graph, dep_graph, ev_store)
        log_stage("14. Risk Engine", t0, time.perf_counter())

        # 15. Reasoning Engine
        t0 = log_start("15. Reasoning Engine")
        insights = generate_insights(ev_store)
        log_stage("15. Reasoning Engine", t0, time.perf_counter())

        # 16. Response serialization
        t0 = log_start("16. Response Serialization")
        ev_store.close()
        result = {
            "repository": {"path": repo.path if repo else repo_path, "is_git": repo.is_git if repo else False},
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
        log_stage("16. Response Serialization", t0, time.perf_counter())

    overall = (time.perf_counter() - overall_start) * 1000
    print(f"\n{'='*60}")
    print(f"  TOTAL ANALYSIS TIME: {overall:.1f}ms ({overall/1000:.1f}s)")
    return result


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "F:\\code\\ig\\ig-costing-main\\ig-costing-main"
    try:
        run_profiled(path)
    except Exception:
        traceback.print_exc()
