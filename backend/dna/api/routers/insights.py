"""
GET /v1/insights           — list all generated insights
GET /v1/insights/{id}      — get single insight by index/id
POST /v1/insights/generate — trigger fresh insight generation from the persisted evidence store
"""
import json
import os
import logging
from fastapi import APIRouter, HTTPException, Query
from dna.evidence.store import EvidenceStore
from dna.reasoning.engine import generate_insights
from dna.config import get_config

logger = logging.getLogger("dna.api.insights")

router = APIRouter(prefix="/v1/insights", tags=["insights"])


def _get_ev_path() -> str:
    cfg = get_config()
    path = getattr(cfg, "evidence_path", "")
    return path if path else os.path.join(os.getcwd(), "ev_store.db")


@router.get("")
async def list_insights(
    category: str | None = Query(None, description="Filter by insight category"),
    severity: str | None = Query(None, description="Filter by severity (low/medium/high/critical)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    ev_path = _get_ev_path()
    if not os.path.exists(ev_path):
        return {"insights": [], "total": 0, "offset": offset, "limit": limit}

    try:
        latest_path = os.path.join(os.getcwd(), "latest_analysis.json")
        with open(latest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            insights = data.get("insights", [])
    except Exception:
        logger.debug("Failed to load latest_analysis.json, returning empty insights")
        insights = []

    if category:
        insights = [i for i in insights if i.get("category") == category]
    if severity:
        insights = [i for i in insights if i.get("severity") == severity]

    total = len(insights)
    page = insights[offset: offset + limit]

    return {
        "insights": page,
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("/generate")
async def trigger_generate():
    ev_path = _get_ev_path()
    if not os.path.exists(ev_path):
        raise HTTPException(
            status_code=404,
            detail="No evidence store found. Run /analyze first.",
        )

    with EvidenceStore(ev_path) as store:
        insights = generate_insights(store)

    return {"insights": insights, "count": len(insights)}
