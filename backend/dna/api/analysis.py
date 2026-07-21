import os
import shutil
import json
import logging
from typing import Callable, Any

from dna.config import get_config
from dna.logging import configure_logging
from dna.pipeline.dag import PipelineDAG, PipelineContext
from dna.storage.store import SCStore
from dna.evidence.store import EvidenceStore

logger = logging.getLogger("dna.api")

def run_full_analysis(repo_path: str, branch: str = None, progress_callback: Callable[[str, str, int, str], None] = None) -> dict:
    import gc
    from dna.storage.db import clear_db_registry
    from dna.config import reset_config
    # Ensure all stale engines and configuration are reset before starting a fresh analysis
    clear_db_registry()
    reset_config()
    gc.collect()
    
    cfg = get_config()
    # Stale cache from a previous run can poison incremental analysis (files from a different repo).
    # Wipe it so every analysis starts fresh.
    for _p in (cfg.store_path, cfg.evidence_path):
        if _p and os.path.exists(_p):
            try:
                os.remove(_p)
            except OSError as e:
                logger.debug("Failed to remove stale cache file %s: %s", _p, e)
            for _ext in ('-wal', '-shm'):
                _wal = _p + _ext
                if os.path.exists(_wal):
                    try:
                        os.remove(_wal)
                    except OSError:
                        logger.debug("Failed to remove stale WAL/SHM %s", _wal)

    configure_logging(level=cfg.log_level)
    logger.info("Starting declarative DAG codebase analysis for: %s", repo_path)

    # Set up temporary storage directories
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "sc_store.db")
        ev_path = os.path.join(tmpdir, "ev_store.db")

        # Create pipeline context
        context = PipelineContext(repo_path, store_path, ev_path)

        # Pre-initialize databases to avoid concurrent table creation race conditions
        try:
            with SCStore(store_path) as store:
                pass
            with EvidenceStore(ev_path) as ev_store:
                pass
        except Exception as e:
            logger.warning("Failed to pre-initialize databases: %s", e)

        # Instantiate declarative DAG
        dag = PipelineDAG()

        # Intercept steps to perform incremental merging after 'entities' step
        original_progress_callback = progress_callback
        
        def dag_progress_callback(step_id: str, status: str, percent: int, message: str):
            # When the entities step succeeds, merge it with the existing database graph
            if step_id == "entities" and status == "success":
                try:
                    _perform_incremental_merge(context, branch)
                except Exception as e:
                    logger.error("Failed to perform incremental merge: %s", e)
            
            if original_progress_callback:
                original_progress_callback(step_id, status, percent, message)

        # Execute DAG
        success = dag.execute(context, progress_callback=dag_progress_callback)

        if not success:
            logger.error("Pipeline execution failed. Errors: %s", context.errors)
            first_err = next(iter(context.errors.values())) if context.errors else "Unknown pipeline error"
            raise RuntimeError(f"Analysis pipeline execution failed: {first_err}")

        # Dispose all engines to release temp file locks before copying/deletion
        clear_db_registry()
        gc.collect()

        # Post-process: persist stores
        cfg = get_config()
        branch_suffix = f"_{branch.replace('/', '_')}" if branch else ""
        
        dest_store_path = getattr(cfg, "store_path", "") or os.path.join(os.getcwd(), f"sc_store{branch_suffix}.db")
        dest_ev_path = getattr(cfg, "evidence_path", "") or os.path.join(os.getcwd(), f"ev_store{branch_suffix}.db")

        os.makedirs(os.path.dirname(os.path.abspath(dest_store_path)), exist_ok=True)
        os.makedirs(os.path.dirname(os.path.abspath(dest_ev_path)), exist_ok=True)

        # Copy the temporary databases back to the configured production database paths
        shutil.copy2(store_path, dest_store_path)
        shutil.copy2(ev_path, dest_ev_path)
        
        # Also ALWAYS overwrite the default databases so that when branch context is lost, 
        # the fallback data is always the absolute latest scanned repository
        default_store_path = getattr(cfg, "store_path", "") or os.path.join(os.getcwd(), "sc_store.db")
        default_ev_path = getattr(cfg, "evidence_path", "") or os.path.join(os.getcwd(), "ev_store.db")
        if dest_store_path != default_store_path:
            shutil.copy2(store_path, default_store_path)
            shutil.copy2(ev_path, default_ev_path)

        # Collect results
        evolution = context.data.get("evolution_engine", {})
        knowledge = context.data.get("knowledge_engine", {})
        risks = context.data.get("risk_engine", {})
        structural = context.data.get("structural_engine", {})
        insights = context.data.get("reasoning", [])
        inventory = context.data.get("indexer")

        repo = context.data.get("discovery")

        # Register to System DB
        try:
            from dna.storage.system import SystemDB
            with SystemDB() as sys_db:
                sys_db.add_repository(
                    path=repo_path,
                    name=os.path.basename(repo_path) or repo_path,
                    total_files=inventory.total_files if inventory else 0,
                    source_files=len([f for f in inventory.files if f.category == "source"]) if inventory else 0,
                    commits=evolution.get("total_commits", 0) if isinstance(evolution, dict) else 0,
                    risk_score=risks.get("overall_risk_score", 0.0) if isinstance(risks, dict) else 0.0
                )
        except Exception as e:
            logger.error("Failed to register repository to SystemDB: %s", e)

        res_dict = {
            "repository": {
                "path": repo.path if repo else repo_path,
                "is_git": repo.is_git if repo else False,
            },
            "summary": {
                "total_commits": evolution.get("total_commits", 0) if isinstance(evolution, dict) else 0,
                "total_authors": evolution.get("total_authors", 0) if isinstance(evolution, dict) else 0,
                "total_files": inventory.total_files if inventory else 0,
                "source_files": len([f for f in inventory.files if f.category == "source"]) if inventory else 0,
                "test_files": len([f for f in inventory.files if f.category == "test"]) if inventory else 0,
            },
            "evolution": evolution,
            "knowledge": knowledge,
            "risk": risks,
            "structural": structural,
            "insights": insights,
        }

        # Save to latest_analysis.json
        try:
            latest_path = os.path.join(os.getcwd(), f"latest_analysis{branch_suffix}.json")
            with open(latest_path, "w", encoding="utf-8") as f:
                json.dump(res_dict, f, indent=2)
            
            # ALWAYS overwrite the default as well
            default_latest = os.path.join(os.getcwd(), "latest_analysis.json")
            if latest_path != default_latest:
                with open(default_latest, "w", encoding="utf-8") as f:
                    json.dump(res_dict, f, indent=2)
        except Exception as e:
            logger.error("Failed to write latest_analysis.json: %s", e)

        return res_dict

def _perform_incremental_merge(context: PipelineContext, branch: str = None):
    """Merges the newly parsed delta entity graph with the existing full entity graph."""
    inventory = context.data.get("indexer")
    delta_graph = context.data.get("entities")
    
    if not inventory or not delta_graph:
        return

    # Determine changed or deleted files
    changed_files = {f.relative_path for f in inventory.files if getattr(f, "change_type", "modified") in ("added", "modified", "removed")}
    
    cfg = get_config()
    branch_suffix = f"_{branch.replace('/', '_')}" if branch else ""
    dest_store_path = getattr(cfg, "store_path", "") or os.path.join(os.getcwd(), f"sc_store{branch_suffix}.db")
    
    previous_graph = None
    if os.path.exists(dest_store_path):
        try:
            with SCStore(dest_store_path) as old_store:
                old_repo = old_store.get_metadata("repo_path")
                if old_repo != context.repo_path:
                    logger.info("Existing database belongs to a different repository. Skipping incremental merge.")
                else:
                    previous_graph = old_store.load_entity_graph()
                    logger.info("Loaded previous entity graph of %d entities for merging", len(previous_graph.entities))
        except Exception as ex:
            logger.warning("Could not load previous entity graph for merging: %s", ex)
            
    if previous_graph and changed_files:
        # Filter out old elements for changed files
        merged_entities = [e for e in previous_graph.entities if e.file_path not in changed_files]
        kept_uids = {e.uid for e in merged_entities}
        
        merged_relations = [
            r for r in previous_graph.relations 
            if r.source_uid in kept_uids and r.target_uid in kept_uids
        ]
        
        from dna.models import EntityGraph
        full_graph = EntityGraph(entities=merged_entities, relations=merged_relations)
        
        # Add new entities with content hashes attached
        for e in delta_graph.entities:
            file_info = next((f for f in inventory.files if f.relative_path == e.file_path), None)
            if file_info:
                setattr(e, "hash", file_info.content_hash)
            full_graph.add_entity(e)
            
        # Add new relations
        for r in delta_graph.relations:
            full_graph.add_relation(r)
            
        logger.info("Merged: previous graph entities=%d, delta graph entities=%d, final merged graph entities=%d",
                    len(previous_graph.entities), len(delta_graph.entities), len(full_graph.entities))
        
        context.data["entities"] = full_graph
    else:
        # First run: attach hashes to all entities
        for e in delta_graph.entities:
            file_info = next((f for f in inventory.files if f.relative_path == e.file_path), None)
            if file_info:
                setattr(e, "hash", file_info.content_hash)
        logger.info("First analysis run; saving entity graph directly with hashes")
        
    # Write to local temp store database path so that subsequent engines (which read from ctx) get the full graph
    # and saving it updates the temp DB which is copied to destination at the end of execution.
    with SCStore(context.store_path) as temp_store:
        temp_store.save_entity_graph(context.data["entities"])
        temp_store.set_metadata("repo_path", context.repo_path)
        temp_store.set_metadata("analysis_time", "now")
