"""
GET /v1/entities         — list entities (filterable by kind, file_path)
GET /v1/entities/{uid}   — get single entity by UID
GET /v1/entities/{uid}/relations — get relations for an entity
"""
import json
import os
from fastapi import APIRouter, HTTPException, Query
from dna.storage.store import SCStore
from dna.config import get_config

router = APIRouter(prefix="/v1/entities", tags=["entities"])


def _get_store_path() -> str:
    cfg = get_config()
    path = getattr(cfg, "store_path", "")
    return path if path else os.path.join(os.getcwd(), "sc_store.db")


@router.get("")
async def list_entities(
    kind: str | None = Query(None, description="Filter by entity kind"),
    file_path: str | None = Query(None, description="Filter by file path substring"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    store_path = _get_store_path()
    if not os.path.exists(store_path):
        return {"entities": [], "total": 0}

    with SCStore(store_path) as store:
        graph = store.load_entity_graph()

    entities = list(graph.entities)
    if kind:
        entities = [e for e in entities if e.kind == kind]
    if file_path:
        entities = [e for e in entities if file_path in e.file_path]

    total = len(entities)
    page = entities[offset: offset + limit]

    return {
        "entities": [
            {
                "uid": e.uid,
                "name": e.name,
                "kind": e.kind,
                "file_path": e.file_path,
                "line": e.line,
                "properties": e.properties,
            }
            for e in page
        ],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/{uid:path}")
async def get_entity(uid: str):
    store_path = _get_store_path()
    if not os.path.exists(store_path):
        raise HTTPException(status_code=404, detail="No entity store found")

    with SCStore(store_path) as store:
        graph = store.load_entity_graph()

    entity = graph.get_entity(uid)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity not found: {uid}")

    relations = graph.get_relations(uid)

    return {
        "uid": entity.uid,
        "name": entity.name,
        "kind": entity.kind,
        "file_path": entity.file_path,
        "line": entity.line,
        "properties": entity.properties,
        "relations": [
            {"source_uid": r.source_uid, "target_uid": r.target_uid, "kind": r.kind}
            for r in relations
        ],
    }
