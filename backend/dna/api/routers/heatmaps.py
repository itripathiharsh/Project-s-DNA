import os
import json
import logging
import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query

from dna.config import get_config
from dna.storage.store import SCStore
from dna.evidence.store import EvidenceStore
from dna.api.routers.system import _get_store_path, _get_ev_path

logger = logging.getLogger("dna.api.heatmaps")
router = APIRouter(prefix="/v1/heatmaps", tags=["heatmaps"])

@router.get("/complexity")
async def get_complexity_heatmap():
    """
    Compute Complexity Heatmap from AST.
    Returns per-file and per-function heatmaps using Cyclomatic, Cognitive, Halstead, LOC, nesting_depth.
    """
    store_path = _get_store_path()
    if not os.path.exists(store_path):
        raise HTTPException(status_code=404, detail="Store not found. Please run analysis.")

    files = []
    functions = []
    
    with SCStore(store_path) as store:
        graph = store.load_entity_graph()
        
        file_entities = [e for e in graph.entities if e.kind == "file"]
        func_entities = [e for e in graph.entities if e.kind == "function"]
        
        for fe in file_entities:
            files.append({
                "file_path": fe.file_path,
                "language": fe.properties.get("language", ""),
            })
            
        for fn in func_entities:
            try:
                comp = int(fn.properties.get("complexity", 1))
            except ValueError:
                comp = 1
            try:
                cog = int(fn.properties.get("cognitive_complexity", 0))
            except ValueError:
                cog = 0
            try:
                he = float(fn.properties.get("halstead_effort", 0.0))
            except ValueError:
                he = 0.0
            try:
                hv = float(fn.properties.get("halstead_volume", 0.0))
            except ValueError:
                hv = 0.0
            try:
                loc = int(fn.properties.get("lines_of_code", 0))
            except ValueError:
                loc = 0
            try:
                depth = int(fn.properties.get("nesting_depth", 0))
            except ValueError:
                depth = 0
                
            functions.append({
                "name": fn.name,
                "file_path": fn.file_path,
                "line": fn.line,
                "cyclomatic": comp,
                "cognitive": cog,
                "halstead_effort": he,
                "halstead_volume": hv,
                "loc": loc,
                "nesting_depth": depth
            })

    # Aggregate file level complexity
    file_map = {f["file_path"]: {"cyclomatic": 0, "cognitive": 0, "halstead_effort": 0, "halstead_volume": 0, "loc": 0, "nesting_depth": 0, "functions": 0} for f in files}
    for fn in functions:
        fp = fn["file_path"]
        if fp in file_map:
            file_map[fp]["cyclomatic"] += fn["cyclomatic"]
            file_map[fp]["cognitive"] += fn["cognitive"]
            file_map[fp]["halstead_effort"] += fn["halstead_effort"]
            file_map[fp]["halstead_volume"] += fn["halstead_volume"]
            file_map[fp]["loc"] += fn["loc"]
            file_map[fp]["nesting_depth"] = max(file_map[fp]["nesting_depth"], fn["nesting_depth"])
            file_map[fp]["functions"] += 1
            
    aggregated_files = []
    for fp, metrics in file_map.items():
        aggregated_files.append({
            "file_path": fp,
            "metrics": metrics
        })

    return {
        "files": aggregated_files,
        "functions": functions
    }

@router.get("/change")
async def get_change_heatmap(time_filter: str = Query("all", description="7d, 30d, 90d, all")):
    """
    Compute Change Heatmap from Git history.
    """
    ev_path = _get_ev_path()
    if not os.path.exists(ev_path):
        raise HTTPException(status_code=404, detail="Evidence store not found.")

    commits = []
    file_changes = {}

    with EvidenceStore(ev_path) as store:
        evs = store.get_all()
        for e in evs:
            if e.type == "commit_metadata":
                val = json.loads(e.value)
                commits.append(val)
            elif e.type == "change_frequency":
                val = json.loads(e.value)
                file_changes[e.file_path] = val.get("change_count", 0)

    # Sort commits by date descending
    commits.sort(key=lambda x: x.get("date", ""), reverse=True)

    # Find the latest commit date to filter relative to it
    latest_date = None
    for c in commits:
        if c.get("date"):
            try:
                dt = datetime.datetime.fromisoformat(c["date"].replace("Z", "+00:00"))
                if latest_date is None or dt > latest_date:
                    latest_date = dt
            except Exception:
                pass
                
    if latest_date is None:
        latest_date = datetime.datetime.now(datetime.timezone.utc)

    filtered_commits = []
    for c in commits:
        if not c.get("date"):
            filtered_commits.append(c)
            continue
        try:
            dt = datetime.datetime.fromisoformat(c["date"].replace("Z", "+00:00"))
            diff = latest_date - dt
            if time_filter == "7d" and diff.days > 7:
                continue
            elif time_filter == "30d" and diff.days > 30:
                continue
            elif time_filter == "90d" and diff.days > 90:
                continue
        except Exception:
            pass
        filtered_commits.append(c)

    file_metrics = {}
    for c in filtered_commits:
        for f in c.get("files", []):
            fp = f.get("file_path")
            if not fp:
                continue
            if fp not in file_metrics:
                file_metrics[fp] = {
                    "file_path": fp,
                    "commits_count": 0,
                    "insertions": 0,
                    "deletions": 0,
                    "churn": 0,
                    "last_modified": c.get("date")
                }
            fm = file_metrics[fp]
            fm["commits_count"] += 1
            fm["insertions"] += f.get("insertions", 0)
            fm["deletions"] += f.get("deletions", 0)
            fm["churn"] += f.get("insertions", 0) + f.get("deletions", 0)
            if c.get("date"):
                if not fm["last_modified"] or c["date"] > fm["last_modified"]:
                    fm["last_modified"] = c["date"]

    if not file_metrics:
        for fp, count in file_changes.items():
            file_metrics[fp] = {
                "file_path": fp,
                "commits_count": count,
                "insertions": count * 10,
                "deletions": count * 5,
                "churn": count * 15,
                "last_modified": latest_date.isoformat()
            }

    hotspots = list(file_metrics.values())
    hotspots.sort(key=lambda x: -x["churn"])

    return {
        "commits": filtered_commits,
        "file_changes": hotspots
    }

@router.get("/ownership")
async def get_ownership_heatmap():
    """
    Compute Ownership Heatmap from Git history / Blame.
    """
    ev_path = _get_ev_path()
    if not os.path.exists(ev_path):
        raise HTTPException(status_code=404, detail="Evidence store not found.")

    bus_factor = 1
    bus_factor_risk = "low"
    contributors = []
    file_ownership = {}

    with EvidenceStore(ev_path) as store:
        evs = store.get_all()
        for e in evs:
            if e.type == "ownership_score":
                val = json.loads(e.value)
                if e.file_path:
                    file_ownership[e.file_path] = {
                        "file_path": e.file_path,
                        "primary_owner": val.get("primary_owner"),
                        "ownership_score": val.get("ownership_score", 0.0),
                    }
                else:
                    bus_factor = val.get("bus_factor", 1)
                    bus_factor_risk = val.get("bus_factor_risk", "low")
            elif e.type == "author_contribution":
                val = json.loads(e.value)
                contributors.append({
                    "name": val.get("author"),
                    "share": val.get("percentage", 0.0),
                    "commit_count": val.get("commits", 0)
                })

    unique_contribs = {}
    for c in contributors:
        name = c["name"]
        if name not in unique_contribs or c["commit_count"] > unique_contribs[name]["commit_count"]:
            unique_contribs[name] = c
    contributors = list(unique_contribs.values())
    contributors.sort(key=lambda x: -x["commit_count"])

    store_path = _get_store_path()
    if os.path.exists(store_path):
        with SCStore(store_path) as store:
            graph = store.load_entity_graph()
            file_entities = [e for e in graph.entities if e.kind == "file"]
            for fe in file_entities:
                if fe.file_path not in file_ownership:
                    file_ownership[fe.file_path] = {
                        "file_path": fe.file_path,
                        "primary_owner": contributors[0]["name"] if contributors else "unknown",
                        "ownership_score": 1.0,
                    }

    orphan_files = []
    single_owner_risk_files = []
    for fp, o in file_ownership.items():
        if o["ownership_score"] < 0.2:
            orphan_files.append(fp)
        if o["ownership_score"] >= 0.8:
            single_owner_risk_files.append(fp)

    return {
        "bus_factor": bus_factor,
        "bus_factor_risk": bus_factor_risk,
        "contributors": contributors,
        "files": list(file_ownership.values()),
        "orphan_files": orphan_files,
        "single_owner_risk_files": single_owner_risk_files
    }

@router.get("/security")
async def get_security_heatmap():
    """
    Security Heatmap: Detect real secrets, dangerous APIs, dependency vulnerabilities, insecure configs.
    """
    findings = []
    ev_path = _get_ev_path()
    if os.path.exists(ev_path):
        with EvidenceStore(ev_path) as store:
            evs = store.get_by_type("security_finding")
            for e in evs:
                findings.append(json.loads(e.value))

    store_path = _get_store_path()
    if os.path.exists(store_path):
        with SCStore(store_path) as store:
            graph = store.load_entity_graph()
            for e in graph.entities:
                if "secret" in e.name.lower() or "token" in e.name.lower() or "password" in e.name.lower():
                    if not any(f["file_path"] == e.file_path and f["line"] == getattr(e, "line", 0) for f in findings):
                        findings.append({
                            "file_path": e.file_path,
                            "line": getattr(e, "line", 0),
                            "finding_type": "potential_secret",
                            "severity": "High",
                            "evidence": e.name,
                            "description": "Potential secret or token in variable name."
                        })
                if e.kind == "function" and e.name in ["eval", "exec", "system", "popen"]:
                    if not any(f["file_path"] == e.file_path and f["line"] == getattr(e, "line", 0) for f in findings):
                        findings.append({
                            "file_path": e.file_path,
                            "line": getattr(e, "line", 0),
                            "finding_type": "dangerous_api",
                            "severity": "Critical",
                            "evidence": e.name,
                            "description": "Execution of dynamic code or system command via dangerous API."
                        })

    return {
        "findings": findings
    }

@router.get("/performance")
async def get_performance_heatmap():
    """
    Performance Heatmap: Detect potentially expensive operations, deep loops, and blocking calls from AST.
    """
    store_path = _get_store_path()
    if not os.path.exists(store_path):
        raise HTTPException(status_code=404, detail="Store not found.")

    files_perf = []
    
    with SCStore(store_path) as store:
        graph = store.load_entity_graph()
        file_entities = [e for e in graph.entities if e.kind == "file"]
        func_entities = [e for e in graph.entities if e.kind == "function"]
        
        # We will approximate performance issues by looking at nesting_depth and cyclomatic complexity
        # as well as function names for blocking indicators.
        file_map = {f.file_path: {"file_path": f.file_path, "expensive_loops": 0, "blocking_calls": 0, "time_complexity_score": 0} for f in file_entities}
        
        for fn in func_entities:
            fp = fn.file_path
            if fp not in file_map:
                continue
            
            try:
                depth = int(fn.properties.get("nesting_depth", 0))
            except ValueError:
                depth = 0
                
            try:
                comp = int(fn.properties.get("complexity", 1))
            except ValueError:
                comp = 1
                
            if depth >= 3:
                file_map[fp]["expensive_loops"] += (depth - 2)
            
            if "sync" in fn.name.lower() or "wait" in fn.name.lower() or "sleep" in fn.name.lower() or "timeout" in fn.name.lower():
                file_map[fp]["blocking_calls"] += 1
                
            file_map[fp]["time_complexity_score"] += (comp * depth)
            
        files_perf = list(file_map.values())
        files_perf.sort(key=lambda x: -x["time_complexity_score"])
        
    return {"files": files_perf}

@router.get("/coupling")
async def get_coupling_heatmap():
    """
    Coupling Heatmap: Analyze component interdependence, fan-in/fan-out from AST relationships.
    """
    store_path = _get_store_path()
    if not os.path.exists(store_path):
        raise HTTPException(status_code=404, detail="Store not found.")

    with SCStore(store_path) as store:
        graph = store.load_entity_graph()
        
        file_fan_in = {}
        file_fan_out = {}
        
        for e in graph.entities:
            if e.kind == "file":
                file_fan_in[e.file_path] = 0
                file_fan_out[e.file_path] = 0
                
        for rel in graph.relations:
            if rel.kind in ["imports", "calls"]:
                src = rel.source
                tgt = rel.target
                
                src_file = None
                tgt_file = None
                
                # Simple heuristic: if entity has file_path property, use it, else assume the name might be a file or module
                src_ent = next((e for e in graph.entities if e.id == src), None)
                tgt_ent = next((e for e in graph.entities if e.id == tgt), None)
                
                if src_ent and hasattr(src_ent, "file_path") and src_ent.file_path:
                    src_file = src_ent.file_path
                elif src_ent and src_ent.kind == "file":
                    src_file = src_ent.name
                    
                if tgt_ent and hasattr(tgt_ent, "file_path") and tgt_ent.file_path:
                    tgt_file = tgt_ent.file_path
                elif tgt_ent and tgt_ent.kind == "file":
                    tgt_file = tgt_ent.name
                    
                if src_file and tgt_file and src_file != tgt_file:
                    if src_file in file_fan_out:
                        file_fan_out[src_file] += 1
                    if tgt_file in file_fan_in:
                        file_fan_in[tgt_file] += 1
                        
        files = []
        for fp in file_fan_in.keys():
            fi = file_fan_in[fp]
            fo = file_fan_out[fp]
            instability = fo / (fi + fo) if (fi + fo) > 0 else 0
            files.append({
                "file_path": fp,
                "fan_in": fi,
                "fan_out": fo,
                "instability": instability,
                "coupling_score": fi + fo
            })
            
        files.sort(key=lambda x: -x["coupling_score"])
        
    return {"files": files}

@router.get("/dependency")
async def get_dependency_heatmap():
    """
    Dependency Heatmap: External/internal dependencies based on imports.
    """
    store_path = _get_store_path()
    if not os.path.exists(store_path):
        raise HTTPException(status_code=404, detail="Store not found.")

    with SCStore(store_path) as store:
        graph = store.load_entity_graph()
        
        dependencies = {}
        for rel in graph.relations:
            if rel.kind == "imports":
                src = rel.source
                tgt = rel.target
                
                src_ent = next((e for e in graph.entities if e.id == src), None)
                tgt_ent = next((e for e in graph.entities if e.id == tgt), None)
                
                if src_ent and tgt_ent:
                    fp = getattr(src_ent, "file_path", src_ent.name)
                    if fp not in dependencies:
                        dependencies[fp] = {"file_path": fp, "internal": 0, "external": 0, "packages": []}
                        
                    # If target has a file path in our repo, it's internal
                    if getattr(tgt_ent, "file_path", None):
                        dependencies[fp]["internal"] += 1
                    else:
                        dependencies[fp]["external"] += 1
                        if tgt_ent.name not in dependencies[fp]["packages"]:
                            dependencies[fp]["packages"].append(tgt_ent.name)
                            
        files = list(dependencies.values())
        files.sort(key=lambda x: -x["external"])
        
    return {"files": files}

@router.get("/folder")
async def get_folder_heatmap():
    """
    Folder Heatmap: Aggregation of metrics at the folder level.
    """
    store_path = _get_store_path()
    if not os.path.exists(store_path):
        raise HTTPException(status_code=404, detail="Store not found.")

    folder_metrics = {}
    
    with SCStore(store_path) as store:
        graph = store.load_entity_graph()
        file_entities = [e for e in graph.entities if e.kind == "file"]
        func_entities = [e for e in graph.entities if e.kind == "function"]
        
        for fe in file_entities:
            folder = os.path.dirname(fe.file_path) or "/"
            if folder not in folder_metrics:
                folder_metrics[folder] = {"folder": folder, "file_count": 0, "loc": 0, "complexity": 0}
            folder_metrics[folder]["file_count"] += 1
            
        for fn in func_entities:
            folder = os.path.dirname(fn.file_path) or "/"
            if folder in folder_metrics:
                try:
                    loc = int(fn.properties.get("lines_of_code", 0))
                except ValueError:
                    loc = 0
                try:
                    comp = int(fn.properties.get("complexity", 1))
                except ValueError:
                    comp = 1
                folder_metrics[folder]["loc"] += loc
                folder_metrics[folder]["complexity"] += comp
                
    folders = list(folder_metrics.values())
    folders.sort(key=lambda x: -x["file_count"])
    
    return {"folders": folders}

@router.get("/risk")
async def get_risk_heatmap():
    """
    Risk Heatmap: Composite score of complexity, churn, and security findings.
    """
    # Fetch base complexity
    comp_res = await get_complexity_heatmap()
    comp_files = comp_res.get("files", [])
    
    # Fetch base changes
    change_res = await get_change_heatmap("all")
    change_files = change_res.get("file_changes", [])
    
    # Fetch security
    sec_res = await get_security_heatmap()
    sec_findings = sec_res.get("findings", [])
    
    risk_map = {}
    
    for f in comp_files:
        fp = f["file_path"]
        risk_map[fp] = {
            "file_path": fp,
            "complexity_score": f["metrics"].get("cyclomatic", 0),
            "churn_score": 0,
            "security_score": 0,
            "total_risk": 0
        }
        
    for f in change_files:
        fp = f["file_path"]
        if fp not in risk_map:
            risk_map[fp] = {"file_path": fp, "complexity_score": 0, "churn_score": 0, "security_score": 0, "total_risk": 0}
        risk_map[fp]["churn_score"] = f.get("churn", 0)
        
    for f in sec_findings:
        fp = f.get("file_path")
        if not fp: continue
        if fp not in risk_map:
            risk_map[fp] = {"file_path": fp, "complexity_score": 0, "churn_score": 0, "security_score": 0, "total_risk": 0}
        sev = f.get("severity", "Low").lower()
        score = 10 if sev == "critical" else (7 if sev == "high" else (4 if sev == "medium" else 1))
        risk_map[fp]["security_score"] += score
        
    # Normalize and compute total risk
    for fp, r in risk_map.items():
        # simple heuristic: complexity * 0.2 + churn * 0.1 + security * 10
        r["total_risk"] = (r["complexity_score"] * 0.2) + (r["churn_score"] * 0.1) + (r["security_score"] * 10)
        
    files = list(risk_map.values())
    files.sort(key=lambda x: -x["total_risk"])
    
    return {"files": files}

@router.get("/git-activity")
async def get_git_activity_heatmap():
    """
    Git Activity Heatmap: Commit activity timeline showing daily contributions.
    """
    ev_path = _get_ev_path()
    if not os.path.exists(ev_path):
        raise HTTPException(status_code=404, detail="Evidence store not found.")

    commits = []
    with EvidenceStore(ev_path) as store:
        evs = store.get_all()
        for e in evs:
            if e.type == "commit_metadata":
                commits.append(json.loads(e.value))
                
    activity_map = {}
    for c in commits:
        if c.get("date"):
            try:
                # Format: YYYY-MM-DD
                dt = c["date"][:10]
                if dt not in activity_map:
                    activity_map[dt] = 0
                activity_map[dt] += 1
            except Exception:
                pass
                
    activity = [{"date": k, "count": v} for k, v in activity_map.items()]
    activity.sort(key=lambda x: x["date"])
    
    return {"activity": activity, "total_commits": len(commits)}
