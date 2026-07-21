import os
import logging
from collections import defaultdict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from dna.storage.store import SCStore
from dna.api.routers.system import _get_store_path

logger = logging.getLogger("dna.api.journeys")
router = APIRouter(prefix="/v1/journeys", tags=["journeys"])

JOURNEY_TYPES = [
    "code_understanding", "execution_flow", "data_flow",
    "variable_flow", "state_flow", "api_journey", "request_journey", "response_journey",
    "database_journey", "event_timeline",
    "object_lifetime", "dependency_galaxy",
    "runtime_simulation", "repository_dna"
]

def _build_graph_data(nodes_list, edges_list):
    return {"nodes": nodes_list, "links": edges_list}

def _get_graph():
    store_path = _get_store_path()
    if not os.path.exists(store_path):
        raise HTTPException(400, "Run an analysis first.")
    with SCStore(store_path) as sc:
        return sc.load_entity_graph()

def _filter_nodes(entities, keyword):
    return [e for e in entities if keyword.lower() in e.file_path.lower() or keyword.lower() in e.name.lower()]

def _get_file_metrics(filepath):
    try:
        from dna.api.routers.system import _get_active_repo_path
        # Resolve real path relative to the active repository path
        full_path = filepath
        if not os.path.isabs(filepath):
            full_path = os.path.join(_get_active_repo_path(), filepath)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                loc = sum(1 for _ in f)
            return {"size": size, "loc": loc}
    except Exception:
        pass
    return {"size": 0, "loc": 0}

@router.get("/{journey_type}")
async def get_journey(journey_type: str):
    if journey_type not in JOURNEY_TYPES:
        raise HTTPException(400, "Invalid journey type")

    graph = _get_graph()
    nodes_map = {}
    links = []

    def add_node(uid, name, group, val=1, desc="", metrics=None):
        if uid not in nodes_map:
            nodes_map[uid] = {"id": uid, "name": name, "group": group, "val": val, "desc": desc, "metrics": metrics or {}}
    
    def add_link(s, t, label="calls"):
        links.append({"source": s, "target": t, "label": label})

    file_entities = [e for e in graph.entities if e.kind == "file"]
    func_entities = [e for e in graph.entities if e.kind == "function"]
    class_entities = [e for e in graph.entities if e.kind == "class"]

    if journey_type == "code_understanding":
        for f in file_entities:
            if "node_modules" in f.file_path or ".venv" in f.file_path: continue
            group = 1 if "frontend" in f.file_path else 2 if "backend" in f.file_path else 3
            metrics = _get_file_metrics(f.file_path)
            # Node height based on REAL Lines of Code!
            val = max(1, metrics["loc"] // 10)
            add_node(f.uid, os.path.basename(f.file_path), group, val, f.file_path, metrics)
        for r in graph.relations:
            if r.kind in ["IMPORTS", "DEPENDS_ON"] and r.source_uid in nodes_map and r.target_uid in nodes_map:
                add_link(r.source_uid, r.target_uid, r.kind.lower())

    elif journey_type == "execution_flow":
        for f in func_entities:
            group = 1 if "api" in f.file_path else 2 if "engine" in f.file_path else 3
            add_node(f.uid, f.name, group, 3, f.file_path)
        for r in graph.relations:
            if r.kind == "CALLS" and r.source_uid in nodes_map and r.target_uid in nodes_map:
                add_link(r.source_uid, r.target_uid, "executes")

    elif journey_type == "api_journey":
        api_funcs = _filter_nodes(func_entities, "router") + _filter_nodes(func_entities, "api")
        core_funcs = _filter_nodes(func_entities, "engine") + _filter_nodes(func_entities, "service")
        db_funcs = _filter_nodes(func_entities, "store") + _filter_nodes(func_entities, "db")
        
        for f in api_funcs: add_node(f.uid, f.name, 1, 6, f.file_path)
        for f in core_funcs: add_node(f.uid, f.name, 2, 4, f.file_path)
        for f in db_funcs: add_node(f.uid, f.name, 3, 5, f.file_path)
        
        for r in graph.relations:
            if r.kind == "CALLS" and r.source_uid in nodes_map and r.target_uid in nodes_map:
                add_link(r.source_uid, r.target_uid, "requests")

    elif journey_type == "database_journey":
        db_nodes = _filter_nodes(graph.entities, "store") + _filter_nodes(graph.entities, "model") + _filter_nodes(graph.entities, "db")
        for n in db_nodes:
            add_node(n.uid, n.name, 4, 5, n.file_path)
        for r in graph.relations:
            if r.source_uid in nodes_map and r.target_uid in nodes_map:
                add_link(r.source_uid, r.target_uid, "queries")

    elif journey_type == "data_flow":
        # Connect classes to functions
        for c in class_entities: add_node(c.uid, c.name, 2, 6, c.file_path)
        for f in func_entities: 
            if "store" in f.file_path or "model" in f.file_path:
                add_node(f.uid, f.name, 3, 4, f.file_path)
        for r in graph.relations:
            if r.source_uid in nodes_map and r.target_uid in nodes_map:
                add_link(r.source_uid, r.target_uid, "data flow")

    elif journey_type == "event_timeline":
        import subprocess
        from dna.api.routers.system import _get_active_repo_path
        # Get real git log as events from the active repository
        try:
            cwd = _get_active_repo_path()
            log_output = subprocess.check_output(
                ["git", "log", "-n", "30", "--pretty=format:%H|%an|%s|%at"],
                cwd=cwd, text=True
            )
            for i, line in enumerate(log_output.strip().split("\n")):
                if not line: continue
                parts = line.split("|")
                if len(parts) >= 4:
                    commit_hash, author, msg, ts = parts[0], parts[1], "|".join(parts[2:-1]), parts[-1]
                    metrics = {"author": author, "timestamp": int(ts), "message": msg, "hash": commit_hash}
                    add_node(f"commit_{commit_hash}", msg[:30], 1, 5, msg, metrics)
        except Exception as e:
            add_node("1", "No Git History", 1, 10, str(e))

    elif journey_type == "dependency_galaxy":
        for f in file_entities:
            add_node(f.uid, os.path.basename(f.file_path), 1, 1, f.file_path)
        for r in graph.relations:
            if r.kind in ["IMPORTS", "DEPENDS_ON"] and r.source_uid in nodes_map and r.target_uid in nodes_map:
                # Increment value (mass) for each dependency to make them larger stars
                nodes_map[r.target_uid]["val"] += 1
                add_link(r.source_uid, r.target_uid, "depends")

    elif journey_type == "object_lifetime":
        var_entities = [e for e in graph.entities if e.kind == "variable"]
        targets = class_entities + var_entities
        for t in targets[:200]: # Cap to 200 for memory
            # Use line number or a hash as a pseudo-age
            age = max(1, hash(t.name) % 10)
            add_node(t.uid, t.name, 1, age, t.file_path)
        for r in graph.relations:
            if r.source_uid in nodes_map and r.target_uid in nodes_map:
                add_link(r.source_uid, r.target_uid, "references")

    else:
        # Generic flow for the rest
        targets = _filter_nodes(graph.entities, journey_type.split('_')[0])
        if not targets:
            targets = func_entities[:100] # fallback
        for n in targets:
            add_node(n.uid, n.name, hash(n.file_path)%5, 4, n.file_path)
        for r in graph.relations:
            if r.source_uid in nodes_map and r.target_uid in nodes_map:
                add_link(r.source_uid, r.target_uid, "transition")

    nodes_list = list(nodes_map.values())
    
    connected = set()
    for l in links:
        connected.add(l["source"])
        connected.add(l["target"])
    if connected:
        nodes_list = [n for n in nodes_list if n["id"] in connected]

    return {
        "journey_type": journey_type,
        "nodes": nodes_list,
        "links": links
    }
