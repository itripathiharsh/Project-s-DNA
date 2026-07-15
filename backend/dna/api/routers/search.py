import os
import json
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any

from dna.config import get_config
from dna.storage.store import SCStore
from dna.evidence.store import EvidenceStore
from dna.storage.system import SystemDB
from dna.reasoning.engine import generate_insights

router = APIRouter(prefix="/v1/search", tags=["search"])

def _get_store_path() -> str:
    cfg = get_config()
    path = getattr(cfg, "store_path", "")
    return path if path else os.path.join(os.getcwd(), "sc_store.db")

def _get_ev_path() -> str:
    cfg = get_config()
    path = getattr(cfg, "evidence_path", "")
    return path if path else os.path.join(os.getcwd(), "ev_store.db")

@router.get("")
async def global_search(
    q: str = Query(..., min_length=1, description="Search query string"),
    type: Optional[str] = Query(None, description="Optional type filter")
):
    query = q.lower()
    results = []

    # 1. Repositories
    if not type or type == "repositories":
        try:
            with SystemDB() as db:
                repos = db.get_repositories()
            for r in repos:
                if query in r["name"].lower() or query in r["path"].lower():
                    results.append({
                        "type": "repository",
                        "name": r["name"],
                        "detail": f"Path: {r['path']} (Risk Score: {r['risk_score']})",
                        "path": r["path"],
                        "extra": r
                    })
        except Exception:
            pass

    # 2. Load entities (files, symbols, classes, functions) from SCStore
    store_path = _get_store_path()
    has_store = os.path.exists(store_path)
    entities = []
    if has_store:
        try:
            with SCStore(store_path) as store:
                graph = store.load_entity_graph()
                entities = list(graph.entities)
        except Exception:
            pass

    for e in entities:
        name_lower = e.name.lower()
        file_lower = e.file_path.lower()
        
        # Files
        if e.kind == "file" or not e.kind:
            if not type or type == "files":
                if query in file_lower:
                    results.append({
                        "type": "file",
                        "name": os.path.basename(e.file_path) or e.name,
                        "detail": e.file_path,
                        "path": e.file_path,
                        "extra": {"line": e.line, "properties": e.properties}
                    })
        else:
            # Classes
            if e.kind == "class":
                if not type or type in ("classes", "symbols"):
                    if query in name_lower or query in file_lower:
                        results.append({
                            "type": "class",
                            "name": e.name,
                            "detail": f"Class in {e.file_path}:{e.line}",
                            "path": e.file_path,
                            "extra": {"line": e.line, "kind": e.kind, "properties": e.properties}
                        })
            # Functions / Methods
            elif e.kind in ("function", "method"):
                if not type or type in ("functions", "symbols"):
                    if query in name_lower or query in file_lower:
                        results.append({
                            "type": "function",
                            "name": e.name,
                            "detail": f"{e.kind.capitalize()} in {e.file_path}:{e.line}",
                            "path": e.file_path,
                            "extra": {"line": e.line, "kind": e.kind, "properties": e.properties}
                        })
            # Other symbols
            else:
                if not type or type == "symbols":
                    if query in name_lower or query in file_lower:
                        results.append({
                            "type": "symbol",
                            "name": e.name,
                            "detail": f"{e.kind.capitalize()} in {e.file_path}:{e.line}",
                            "path": e.file_path,
                            "extra": {"line": e.line, "kind": e.kind, "properties": e.properties}
                        })

    # 3. Load evidence & insights (insights, risk, authors, knowledge)
    ev_path = _get_ev_path()
    has_ev = os.path.exists(ev_path)
    evidences = []
    insights = []
    if has_ev:
        try:
            with EvidenceStore(ev_path) as store:
                insights = generate_insights(store)
                evidences = store.get_all()
        except Exception:
            pass

    # Insights
    if not type or type == "insights":
        for ins in insights:
            title_lower = ins.get("title", "").lower()
            desc_lower = ins.get("description", "").lower()
            detail_lower = ins.get("detail", "").lower()
            if query in title_lower or query in desc_lower or query in detail_lower:
                results.append({
                    "type": "insight",
                    "name": ins.get("title") or ins.get("category", "Insight"),
                    "detail": ins.get("detail") or ins.get("description", ""),
                    "path": ins.get("file_path"),
                    "extra": ins
                })

    # Authors
    if not type or type == "authors":
        # Look for authors in bus_factor / git history evidence
        authors_found = set()
        for ev in evidences:
            if ev.type == "bus_factor" and isinstance(ev.value, str):
                try:
                    val = json.loads(ev.value)
                    for c in val.get("contributions", []):
                        author_name = c.get("name", "")
                        if author_name and query in author_name.lower() and author_name not in authors_found:
                            authors_found.add(author_name)
                            results.append({
                                "type": "author",
                                "name": author_name,
                                "detail": f"Git Contributor ({c.get('commit_count')} commits, {round(c.get('share', 0)*100)}% share)",
                                "extra": c
                            })
                except Exception:
                    pass

    # Knowledge / general evidence
    if not type or type == "knowledge":
        for ev in evidences:
            type_lower = ev.type.lower()
            val_str = str(ev.value).lower()
            if query in type_lower or query in val_str:
                results.append({
                    "type": "knowledge",
                    "name": f"Evidence: {ev.type}",
                    "detail": f"Source: {ev.source} | File: {ev.file_path}",
                    "path": ev.file_path,
                    "extra": {"id": ev.id, "type": ev.type, "source": ev.source, "timestamp": ev.timestamp}
                })

    # Risks
    if not type or type == "risk":
        for ev in evidences:
            if ev.type == "risk_indicator" or "risk" in ev.type:
                try:
                    val = json.loads(ev.value) if isinstance(ev.value, str) else ev.value
                    desc = val.get("description", "") if isinstance(val, dict) else str(val)
                    severity = val.get("severity", "medium") if isinstance(val, dict) else "medium"
                    if query in desc.lower() or query in ev.type.lower():
                        results.append({
                            "type": "risk",
                            "name": f"Risk Indicator ({severity})",
                            "detail": desc,
                            "path": ev.file_path,
                            "extra": val
                        })
                except Exception:
                    pass

    # Commits
    if not type or type == "commits":
        # Check commits in evidence (e.g. recent commits) or SystemDB
        for ev in evidences:
            if ev.type == "commits" or ev.type == "git_history":
                try:
                    val = json.loads(ev.value) if isinstance(ev.value, str) else ev.value
                    # If list of commits
                    if isinstance(val, list):
                        for commit in val:
                            msg = commit.get("message", "")
                            author = commit.get("author", "")
                            sha = commit.get("sha", "")
                            if query in msg.lower() or query in author.lower() or query in sha.lower():
                                results.append({
                                    "type": "commit",
                                    "name": f"Commit {sha[:8]}",
                                    "detail": f"{msg} - by {author}",
                                    "extra": commit
                                })
                except Exception:
                    pass

    return {
        "query": q,
        "type": type,
        "results": results[:100],  # cap at 100 results
        "total": len(results)
    }
