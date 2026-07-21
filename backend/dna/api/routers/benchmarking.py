import os
import json
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

logger = logging.getLogger("dna.api.benchmarking")
router = APIRouter(prefix="/v1/benchmarking", tags=["benchmarking"])

class BranchCompareRequest(BaseModel):
    branches: List[str]

def load_analysis_for_branch(branch: str) -> dict:
    branch_suffix = f"_{branch.replace('/', '_')}"
    latest_path = os.path.join(os.getcwd(), f"latest_analysis{branch_suffix}.json")
    if not os.path.exists(latest_path):
        return None
    try:
        with open(latest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {latest_path}: {e}")
        return None

@router.post("/compare")
async def compare_branches(req: BranchCompareRequest):
    if not req.branches or len(req.branches) < 2:
        raise HTTPException(status_code=400, detail="Provide at least two branches to compare.")
    
    results = {}
    for b in req.branches:
        data = load_analysis_for_branch(b)
        if not data:
            results[b] = None
            continue
        
        summary = data.get("summary", {})
        risk = data.get("risk", {})
        evolution = data.get("evolution", {})
        structural = data.get("structural", {})
        
        results[b] = {
            "health": 100 - risk.get("overall_risk_score", 0),
            "complexity": structural.get("avg_complexity", 1.0) * 10,
            "maintainability": max(0, 100 - structural.get("max_complexity", 0) * 2),
            "technical_debt": risk.get("overall_risk_score", 0),
            "security": max(0, 100 - sum(1 for r in risk.get("architectural_risks", []) if r.get("severity") == "high") * 5),
            "performance": max(0, 100 - structural.get("max_directory_depth", 0) * 2),
            "architecture": max(0, 100 - structural.get("structural_coupling", 0) * 2),
            "scalability": min(100, 50 + summary.get("total_files", 0)),
            "production_readiness": 90 if risk.get("overall_risk_score", 0) < 50 else 40,
            "risk_score": risk.get("overall_risk_score", 0),
            "bus_factor": evolution.get("bus_factor", 1),
            "total_files": summary.get("total_files", 0),
            "total_classes": structural.get("total_classes", 0),
            "total_functions": structural.get("total_functions", 0),
            "loc": summary.get("total_size_bytes", 0) // 30
        }

    return {"benchmarks": results}

class DiffRequest(BaseModel):
    base_branch: str
    compare_branch: str

@router.post("/diff")
async def diff_branches(req: DiffRequest):
    base_data = load_analysis_for_branch(req.base_branch)
    compare_data = load_analysis_for_branch(req.compare_branch)

    if not base_data or not compare_data:
        raise HTTPException(status_code=400, detail="Analysis data for one or both branches not found.")
    
    # Calculate differences
    base_files = base_data.get("summary", {}).get("total_files", 0)
    compare_files = compare_data.get("summary", {}).get("total_files", 0)
    
    base_risk = base_data.get("risk", {}).get("overall_risk_score", 0)
    compare_risk = compare_data.get("risk", {}).get("overall_risk_score", 0)

    complexity_diff = compare_data.get("structural", {}).get("avg_complexity", 0) - base_data.get("structural", {}).get("avg_complexity", 0)
    
    ai_summary = []
    if compare_risk < base_risk:
        ai_summary.append(f"What improved: The overall risk score decreased by {base_risk - compare_risk:.1f} points.")
    elif compare_risk > base_risk:
        ai_summary.append(f"What became worse: The risk score increased by {compare_risk - base_risk:.1f} points.")
    else:
        ai_summary.append("Risk score remained unchanged.")
        
    if complexity_diff > 0:
        ai_summary.append(f"Note: Average complexity increased by {complexity_diff:.2f}.")
    else:
        ai_summary.append(f"Note: Average complexity decreased or stayed the same.")
        
    ai_summary.append("What should be merged: Changes seem structurally sound.")
    if compare_risk > 50:
        ai_summary.append("What should be fixed before merge: Address the newly introduced structural risks.")

    return {
        "files_added": max(0, compare_files - base_files),
        "files_removed": max(0, base_files - compare_files),
        "files_modified": abs(compare_files - base_files),
        "complexity_difference": round(complexity_diff, 2),
        "risk_difference": compare_risk - base_risk,
        "score_changes": {
            "health": base_risk - compare_risk
        },
        "ai_summary": ai_summary
    }
