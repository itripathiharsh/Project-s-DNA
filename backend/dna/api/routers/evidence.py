"""
GET /v1/evidence           — list evidence (filterable by type, source, file_path)
GET /v1/evidence/{id}      — get single evidence item by ID
"""
import json
import os
from fastapi import APIRouter, HTTPException, Query
from dna.evidence.store import EvidenceStore
from dna.config import get_config

router = APIRouter(prefix="/v1/evidence", tags=["evidence"])


def _get_ev_path() -> str:
    cfg = get_config()
    path = getattr(cfg, "evidence_path", "")
    return path if path else os.path.join(os.getcwd(), "ev_store.db")


def _serialize(ev) -> dict:
    try:
        value = json.loads(ev.value) if isinstance(ev.value, str) else ev.value
    except (json.JSONDecodeError, TypeError):
        value = ev.value
    return {
        "id": ev.id,
        "type": ev.type,
        "value": value,
        "source": ev.source,
        "file_path": ev.file_path,
        "timestamp": ev.timestamp,
    }


@router.get("")
async def list_evidence(
    type: str | None = Query(None, description="Filter by evidence type"),
    source: str | None = Query(None, description="Filter by source engine"),
    file_path: str | None = Query(None, description="Filter by file path substring"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    ev_path = _get_ev_path()
    if not os.path.exists(ev_path):
        return {"evidence": [], "total": 0, "offset": offset, "limit": limit}

    with EvidenceStore(ev_path) as store:
        if type:
            items = store.get_by_type(type)
        elif source:
            items = store.get_by_source(source)
        else:
            items = store.get_all()

    if file_path:
        items = [e for e in items if file_path in e.file_path]
    if source and not type:
        # already filtered
        pass
    elif source and type:
        items = [e for e in items if e.source == source]

    total = len(items)
    page = items[offset: offset + limit]

    return {
        "evidence": [_serialize(e) for e in page],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/{evidence_id}")
async def get_evidence(evidence_id: str):
    ev_path = _get_ev_path()
    if not os.path.exists(ev_path):
        raise HTTPException(status_code=404, detail="No evidence store found")

    with EvidenceStore(ev_path) as store:
        items = store.get_all()

    match = next((e for e in items if e.id == evidence_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Evidence not found: {evidence_id}")

    return _serialize(match)
