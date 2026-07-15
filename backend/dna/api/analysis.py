import tempfile
import os
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


import logging
from dna.logging import log_stage, configure_logging
from dna.config import get_config

logger = logging.getLogger("dna.api")


def run_full_analysis(repo_path: str) -> dict:
    # Ensure logging is configured (e.g. if run directly from a script/test rather than FastAPI server)
    configure_logging(level=get_config().log_level)

    logger.info("Starting codebase analysis for repository: %s", repo_path)
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "sc_store.db")
        ev_path = os.path.join(tmpdir, "ev_store.db")

        with log_stage("discovery"):
            repo = discover_repository(repo_path)

        with log_stage("git_history"):
            try:
                history = mine_git_history(repo_path)
            except NotAGitRepositoryError:
                history = CommitHistory()

        with log_stage("indexer"):
            inventory = index_repository(repo_path, repo)

        with log_stage("parser"):
            parsed = parse_repository(inventory)

        with log_stage("normalizer"):
            normalized = normalize_parsed_files(parsed)

        with log_stage("symbols"):
            symbol_index = build_symbol_index(normalized)

        with log_stage("graph"):
            dep_graph = build_dependency_graph(normalized, symbol_index)

        with log_stage("entities"):
            entity_graph = build_entity_graph(normalized, symbol_index, dep_graph)

        with SCStore(store_path) as sc_store:
            sc_store.save_entity_graph(entity_graph)
            sc_store.set_metadata("repo_path", repo_path)
            sc_store.set_metadata("analysis_time", "now")

        with EvidenceStore(ev_path) as ev_store:
            with log_stage("structural_engine"):
                with ev_store.transaction():
                    structural = analyze_structure(entity_graph, ev_store)
            with log_stage("evolution_engine"):
                with ev_store.transaction():
                    evolution = analyze_evolution(history, entity_graph, evidence_store=ev_store)
            with log_stage("knowledge_engine"):
                with ev_store.transaction():
                    knowledge = analyze_knowledge(history, entity_graph, ev_store, repo_path=repo_path)
            with log_stage("risk_engine"):
                with ev_store.transaction():
                    risks = analyze_risks(entity_graph, dep_graph, ev_store)
            with log_stage("reasoning"):
                insights = generate_insights(ev_store)

        logger.info("Analysis successfully completed for repository: %s", repo_path)

        # Copy temporary DB files to permanent locations
        cfg = get_config()
        dest_store_path = cfg.store_path or os.path.join(os.getcwd(), "sc_store.db")
        dest_ev_path = cfg.evidence_path or os.path.join(os.getcwd(), "ev_store.db")
        
        import shutil
        os.makedirs(os.path.dirname(os.path.abspath(dest_store_path)), exist_ok=True)
        os.makedirs(os.path.dirname(os.path.abspath(dest_ev_path)), exist_ok=True)
        
        shutil.copy2(store_path, dest_store_path)
        shutil.copy2(ev_path, dest_ev_path)

        # Register to System DB
        try:
            from dna.storage.system import SystemDB
            with SystemDB() as sys_db:
                sys_db.add_repository(
                    path=repo_path,
                    name=os.path.basename(repo_path) or repo_path,
                    total_files=inventory.total_files if inventory else 0,
                    source_files=len([f for f in inventory.files if f.category == "source"]) if inventory else 0,
                    commits=evolution.get("total_commits", 0),
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
                "total_commits": evolution.get("total_commits", 0),
                "total_authors": evolution.get("total_authors", 0),
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
            latest_path = os.path.join(os.getcwd(), "latest_analysis.json")
            import json
            with open(latest_path, "w", encoding="utf-8") as f:
                json.dump(res_dict, f, indent=2)
        except Exception as e:
            logger.error("Failed to write latest_analysis.json: %s", e)

        return res_dict
