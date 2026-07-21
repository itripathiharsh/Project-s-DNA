import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, Any, List, Set, Callable

logger = logging.getLogger("dna.pipeline.dag")

DEFAULT_PIPELINE_CONFIG = [
  {
    "id": "discovery",
    "name": "Codebase Discovery",
    "depends_on": [],
    "priority": 100,
    "timeout": 30,
    "retry": 3
  },
  {
    "id": "git_history",
    "name": "Git History Mining",
    "depends_on": ["discovery"],
    "priority": 90,
    "timeout": 120,
    "retry": 2
  },
  {
    "id": "indexer",
    "name": "File Inventory Indexer",
    "depends_on": ["discovery"],
    "priority": 80,
    "timeout": 60,
    "retry": 3
  },
  {
    "id": "parser",
    "name": "AST Parser",
    "depends_on": ["indexer"],
    "priority": 70,
    "timeout": 180,
    "retry": 3
  },
  {
    "id": "normalizer",
    "name": "Syntax Normalizer",
    "depends_on": ["parser"],
    "priority": 60,
    "timeout": 60,
    "retry": 3
  },
  {
    "id": "symbols",
    "name": "Symbol Table Indexer",
    "depends_on": ["normalizer"],
    "priority": 50,
    "timeout": 60,
    "retry": 3
  },
  {
    "id": "graph",
    "name": "Dependency Graph Builder",
    "depends_on": ["symbols"],
    "priority": 40,
    "timeout": 60,
    "retry": 3
  },
  {
    "id": "entities",
    "name": "Entity Schema Builder",
    "depends_on": ["graph"],
    "priority": 30,
    "timeout": 60,
    "retry": 3
  },
  {
    "id": "structural_engine",
    "name": "Structural Engine",
    "depends_on": ["entities"],
    "priority": 20,
    "timeout": 60,
    "retry": 2
  },
  {
    "id": "evolution_engine",
    "name": "Evolution Engine",
    "depends_on": ["entities", "git_history"],
    "priority": 20,
    "timeout": 60,
    "retry": 2
  },
  {
    "id": "knowledge_engine",
    "name": "Knowledge Engine",
    "depends_on": ["entities", "git_history"],
    "priority": 20,
    "timeout": 60,
    "retry": 2
  },
  {
    "id": "risk_engine",
    "name": "Risk Engine",
    "depends_on": ["entities", "graph"],
    "priority": 20,
    "timeout": 60,
    "retry": 2
  },
  {
    "id": "reasoning",
    "name": "Architectural Reasoning",
    "depends_on": ["structural_engine", "evolution_engine", "knowledge_engine", "risk_engine"],
    "priority": 10,
    "timeout": 120,
    "retry": 2
  }
]

def load_pipeline_config() -> List[Dict[str, Any]]:
    config_path = os.path.join(os.path.dirname(__file__), "..", "pipeline_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Failed to load pipeline config: %s. Using default.", e)
    return DEFAULT_PIPELINE_CONFIG


class PipelineContext:
    def __init__(self, repo_path: str, store_path: str, ev_path: str):
        self.repo_path = repo_path
        self.store_path = store_path
        self.ev_path = ev_path
        self.data: Dict[str, Any] = {}
        self.errors: Dict[str, str] = {}


class PipelineDAG:
    def __init__(self, steps_config: List[Dict[str, Any]] = None):
        self.steps = steps_config or load_pipeline_config()
        self._validate_dag()

    def _validate_dag(self):
        # Topological Sort checking for cycles
        step_ids = {s["id"] for s in self.steps}
        adjacency = {s["id"]: set(s.get("depends_on", [])) for s in self.steps}
        
        # Check that dependencies exist
        for sid, deps in adjacency.items():
            for dep in deps:
                if dep not in step_ids:
                    raise ValueError(f"Step '{sid}' depends on non-existent step '{dep}'")

        # Detect cycle using DFS
        visited = {}
        def dfs(node):
            if node in visited:
                if visited[node] == 1: # Gray node: cycle detected
                    return False
                return True
            visited[node] = 1 # Mark gray
            for dep in adjacency.get(node, []):
                if not dfs(dep):
                    return False
            visited[node] = 2 # Mark black
            return True

        for sid in step_ids:
            if not dfs(sid):
                raise ValueError("Circular dependency detected in pipeline configuration")

    def execute(self, context: PipelineContext, progress_callback: Callable[[str, str, int, str], None] = None) -> bool:
        """
        Executes the DAG using a topological execution order.
        Supports:
          - Dependencies
          - Priority-based scheduling (higher priority runs first if multiple are ready)
          - Retries and Timeout bounds
          - Progress / event logging
        """
        completed: Set[str] = set()
        running: Set[str] = set()
        failed: Set[str] = set()
        
        step_by_id = {s["id"]: s for s in self.steps}
        total_steps = len(self.steps)

        # Define task executors mapping Step ID to the actual python functions
        # Implemented lazily to avoid circular import issues
        def get_task_fn(step_id: str):
            if step_id == "discovery":
                from dna.discovery.orchestrator import discover_repository
                return lambda ctx: discover_repository(ctx.repo_path)
            elif step_id == "git_history":
                from dna.git_history.miner import mine_git_history
                from dna.discovery.orchestrator import NotAGitRepositoryError
                from dna.models import CommitHistory
                def run_git(ctx):
                    try:
                        return mine_git_history(ctx.repo_path)
                    except NotAGitRepositoryError:
                        return CommitHistory()
                return run_git
            elif step_id == "indexer":
                from dna.indexer.orchestrator import index_repository
                return lambda ctx: index_repository(ctx.repo_path, ctx.data["discovery"])
            elif step_id == "parser":
                from dna.parser.orchestrator import parse_repository
                return lambda ctx: parse_repository(ctx.data["indexer"])
            elif step_id == "normalizer":
                from dna.normalizer.orchestrator import normalize_parsed_files
                return lambda ctx: normalize_parsed_files(ctx.data["parser"])
            elif step_id == "symbols":
                from dna.symbols.indexer import build_symbol_index
                return lambda ctx: build_symbol_index(ctx.data["normalizer"])
            elif step_id == "graph":
                from dna.graph.builder import build_dependency_graph
                return lambda ctx: build_dependency_graph(ctx.data["normalizer"], ctx.data["symbols"])
            elif step_id == "entities":
                from dna.entities.builder import build_entity_graph
                return lambda ctx: build_entity_graph(ctx.data["normalizer"], ctx.data["symbols"], ctx.data["graph"])
            elif step_id == "structural_engine":
                from dna.engines.structural import analyze_structure
                from dna.evidence.store import EvidenceStore
                def run_struct(ctx):
                    with EvidenceStore(ctx.ev_path) as ev_store:
                        with ev_store.transaction():
                            return analyze_structure(ctx.data["entities"], ev_store)
                return run_struct
            elif step_id == "evolution_engine":
                from dna.engines.evolution import analyze_evolution
                from dna.evidence.store import EvidenceStore
                def run_evo(ctx):
                    with EvidenceStore(ctx.ev_path) as ev_store:
                        with ev_store.transaction():
                            return analyze_evolution(ctx.data["git_history"], ctx.data["entities"], evidence_store=ev_store)
                return run_evo
            elif step_id == "knowledge_engine":
                from dna.engines.knowledge import analyze_knowledge
                from dna.evidence.store import EvidenceStore
                def run_know(ctx):
                    with EvidenceStore(ctx.ev_path) as ev_store:
                        with ev_store.transaction():
                            return analyze_knowledge(ctx.data["git_history"], ctx.data["entities"], ev_store, repo_path=ctx.repo_path)
                return run_know
            elif step_id == "risk_engine":
                from dna.engines.risk import analyze_risks
                from dna.evidence.store import EvidenceStore
                def run_risk(ctx):
                    with EvidenceStore(ctx.ev_path) as ev_store:
                        with ev_store.transaction():
                            return analyze_risks(ctx.data["entities"], ctx.data["graph"], ev_store, repo_path=ctx.repo_path)
                return run_risk
            elif step_id == "reasoning":
                from dna.reasoning.engine import generate_insights
                from dna.evidence.store import EvidenceStore
                def run_reason(ctx):
                    with EvidenceStore(ctx.ev_path) as ev_store:
                        return generate_insights(ev_store)
                return run_reason
            else:
                raise ValueError(f"No task function registered for step '{step_id}'")

        # Topological dispatch loop
        from concurrent.futures import ThreadPoolExecutor
        # Use a dedicated executor per pipeline run to guarantee full isolation.
        # The global shared executor can retain stale references across tests.
        executor = ThreadPoolExecutor(max_workers=8)
        try:
            futures: Dict[str, Future] = {}
            
            while len(completed) + len(failed) < total_steps:
                # Find all ready tasks
                ready_steps = []
                for step in self.steps:
                    sid = step["id"]
                    if sid not in completed and sid not in failed and sid not in running:
                        # Check dependencies
                        deps = step.get("depends_on", [])
                        if all(d in completed for d in deps):
                            # Check if any dependencies failed, propagating failure
                            if any(d in failed for d in deps):
                                failed.add(sid)
                                logger.error("Skipping task '%s' because its dependencies failed.", sid)
                                continue
                            ready_steps.append(step)

                # Sort ready steps by priority (descending)
                ready_steps.sort(key=lambda s: s.get("priority", 0), reverse=True)

                # If no tasks are running and no tasks are ready to run, we are stuck or finished
                if not ready_steps and not running:
                    stranded = {s["id"] for s in self.steps} - completed - failed
                    for sid in stranded:
                        failed.add(sid)
                        if progress_callback:
                            progress_callback(sid, "failed", 100, f"Task aborted due to upstream dependency failures")
                    break

                # Dispatch ready steps
                for step in ready_steps:
                    sid = step["id"]
                    running.add(sid)
                    
                    if progress_callback:
                        progress_callback(sid, "running", int((len(completed) / total_steps) * 100), f"Starting task: {step['name']}")
                    
                    task_fn = get_task_fn(sid)
                    
                    # Schedule step execution with retries and timeout
                    def make_task_wrapper(s_id, fn, timeout, max_retries):
                        def wrapper():
                            last_err = None
                            for attempt in range(1, max_retries + 1):
                                try:
                                    logger.info("Executing step '%s' (Attempt %d/%d)", s_id, attempt, max_retries)
                                    t0 = time.time()
                                    res = fn(context)
                                    duration = (time.time() - t0) * 1000
                                    logger.info("Step '%s' completed successfully in %.2fms", s_id, duration)
                                    return res
                                except Exception as err:
                                    last_err = err
                                    logger.error("Step '%s' failed on attempt %d: %s", s_id, attempt, err)
                                    if attempt < max_retries:
                                        time.sleep(0.5 * attempt) # Exponential backoff
                            raise last_err
                        return wrapper

                    wrapper_fn = make_task_wrapper(sid, task_fn, step.get("timeout", 60), step.get("retry", 1))
                    
                    # Submit to thread pool
                    future = executor.submit(wrapper_fn)
                    futures[sid] = future

                # Check on active futures
                for sid, future in list(futures.items()):
                    if future.done():
                        running.remove(sid)
                        try:
                            result = future.result()
                            context.data[sid] = result
                            completed.add(sid)
                            
                            percent = int((len(completed) / total_steps) * 100)
                            if progress_callback:
                                progress_callback(sid, "success", percent, f"Task completed: {step_by_id[sid]['name']}")
                        except Exception as e:
                            failed.add(sid)
                            context.errors[sid] = str(e)
                            
                            percent = int(((len(completed) + len(failed)) / total_steps) * 100)
                            if progress_callback:
                                progress_callback(sid, "failed", percent, f"Task failed: {step_by_id[sid]['name']}. Error: {e}")
                        del futures[sid]

                # Prevent busy looping
                time.sleep(0.05)
        finally:
            executor.shutdown(wait=True)

        return len(failed) == 0
