"""Tests for /v1/ resource endpoints (entities, evidence, insights)."""
import tempfile
import os
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from dna.api.app import app
from dna.models import EntityGraph, Entity, EntityRelation, Evidence

client = TestClient(app)


# ---------------------------------------------------------------------------
# /v1/entities
# ---------------------------------------------------------------------------

def _mock_entity_graph() -> EntityGraph:
    g = EntityGraph()
    g.add_entity(Entity(uid="file:main.py", name="main.py", kind="file", file_path="main.py"))
    g.add_entity(Entity(uid="function:main.py:foo", name="foo", kind="function", file_path="main.py"))
    g.add_entity(Entity(uid="file:utils.py", name="utils.py", kind="file", file_path="utils.py"))
    g.add_relation(EntityRelation(source_uid="file:main.py", target_uid="function:main.py:foo", kind="CONTAINS"))
    return g


def test_v1_entities_no_store(tmp_path):
    with patch("dna.api.routers.entities._get_store_path", return_value=str(tmp_path / "nonexistent.db")):
        r = client.get("/v1/entities")
    assert r.status_code == 200
    data = r.json()
    assert data["entities"] == []
    assert data["total"] == 0


def test_v1_entities_list(tmp_path):
    from dna.storage.store import SCStore
    store_path = str(tmp_path / "sc.db")
    with SCStore(store_path) as store:
        store.save_entity_graph(_mock_entity_graph())

    with patch("dna.api.routers.entities._get_store_path", return_value=store_path):
        r = client.get("/v1/entities")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert len(data["entities"]) == 3


def test_v1_entities_filter_kind(tmp_path):
    from dna.storage.store import SCStore
    store_path = str(tmp_path / "sc.db")
    with SCStore(store_path) as store:
        store.save_entity_graph(_mock_entity_graph())

    with patch("dna.api.routers.entities._get_store_path", return_value=store_path):
        r = client.get("/v1/entities?kind=file")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert all(e["kind"] == "file" for e in data["entities"])


def test_v1_entities_filter_file_path(tmp_path):
    from dna.storage.store import SCStore
    store_path = str(tmp_path / "sc.db")
    with SCStore(store_path) as store:
        store.save_entity_graph(_mock_entity_graph())

    with patch("dna.api.routers.entities._get_store_path", return_value=store_path):
        r = client.get("/v1/entities?file_path=utils")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["entities"][0]["name"] == "utils.py"


def test_v1_entities_get_single(tmp_path):
    from dna.storage.store import SCStore
    store_path = str(tmp_path / "sc.db")
    with SCStore(store_path) as store:
        store.save_entity_graph(_mock_entity_graph())

    with patch("dna.api.routers.entities._get_store_path", return_value=store_path):
        r = client.get("/v1/entities/file:main.py")
    assert r.status_code == 200
    data = r.json()
    assert data["uid"] == "file:main.py"
    assert data["name"] == "main.py"
    assert isinstance(data["relations"], list)


def test_v1_entities_not_found(tmp_path):
    from dna.storage.store import SCStore
    store_path = str(tmp_path / "sc.db")
    with SCStore(store_path) as store:
        store.save_entity_graph(_mock_entity_graph())

    with patch("dna.api.routers.entities._get_store_path", return_value=store_path):
        r = client.get("/v1/entities/file:nonexistent.py")
    assert r.status_code == 404


def test_v1_entities_pagination(tmp_path):
    from dna.storage.store import SCStore
    store_path = str(tmp_path / "sc.db")
    with SCStore(store_path) as store:
        store.save_entity_graph(_mock_entity_graph())

    with patch("dna.api.routers.entities._get_store_path", return_value=store_path):
        r = client.get("/v1/entities?limit=2&offset=0")
    assert r.status_code == 200
    data = r.json()
    assert len(data["entities"]) == 2
    assert data["total"] == 3


# ---------------------------------------------------------------------------
# /v1/evidence
# ---------------------------------------------------------------------------

def _seed_evidence_store(store_path: str):
    from dna.evidence.store import EvidenceStore
    with EvidenceStore(store_path) as store:
        store.add_evidence("change_frequency", {"changes": 10}, source="git", file_path="main.py")
        store.add_evidence("risk_metrics", {"test_file_ratio": 0.2}, source="risk")
        store.add_evidence("complexity_metrics", {"complexity": 5}, source="structural", file_path="main.py")


def test_v1_evidence_no_store(tmp_path):
    with patch("dna.api.routers.evidence._get_ev_path", return_value=str(tmp_path / "nonexistent.db")):
        r = client.get("/v1/evidence")
    assert r.status_code == 200
    data = r.json()
    assert data["evidence"] == []
    assert data["total"] == 0


def test_v1_evidence_list(tmp_path):
    store_path = str(tmp_path / "ev.db")
    _seed_evidence_store(store_path)

    with patch("dna.api.routers.evidence._get_ev_path", return_value=store_path):
        r = client.get("/v1/evidence")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert len(data["evidence"]) == 3


def test_v1_evidence_filter_type(tmp_path):
    store_path = str(tmp_path / "ev.db")
    _seed_evidence_store(store_path)

    with patch("dna.api.routers.evidence._get_ev_path", return_value=store_path):
        r = client.get("/v1/evidence?type=change_frequency")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["evidence"][0]["type"] == "change_frequency"


def test_v1_evidence_filter_file_path(tmp_path):
    store_path = str(tmp_path / "ev.db")
    _seed_evidence_store(store_path)

    with patch("dna.api.routers.evidence._get_ev_path", return_value=store_path):
        r = client.get("/v1/evidence?file_path=main.py")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2


def test_v1_evidence_get_single(tmp_path):
    from dna.evidence.store import EvidenceStore
    store_path = str(tmp_path / "ev.db")
    with EvidenceStore(store_path) as store:
        ev = store.add_evidence("change_frequency", {"changes": 5}, source="git", file_path="a.py")

    with patch("dna.api.routers.evidence._get_ev_path", return_value=store_path):
        r = client.get(f"/v1/evidence/{ev.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == ev.id
    assert data["type"] == "change_frequency"


def test_v1_evidence_not_found(tmp_path):
    store_path = str(tmp_path / "ev.db")
    _seed_evidence_store(store_path)

    with patch("dna.api.routers.evidence._get_ev_path", return_value=store_path):
        r = client.get("/v1/evidence/nonexistent-id")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# /v1/insights
# ---------------------------------------------------------------------------

def test_v1_insights_no_store(tmp_path):
    with patch("dna.api.routers.insights._get_ev_path", return_value=str(tmp_path / "nonexistent.db")):
        r = client.get("/v1/insights")
    assert r.status_code == 200
    data = r.json()
    assert data["insights"] == []
    assert data["total"] == 0


def test_v1_insights_list(tmp_path):
    from dna.evidence.store import EvidenceStore
    store_path = str(tmp_path / "ev.db")
    with EvidenceStore(store_path) as store:
        store.add_evidence("change_frequency", {"changes": 30}, source="git", file_path="hot.py")
        store.add_evidence("complexity_metrics", {"max_complexity": 15}, source="structural", file_path="hot.py")
        store.add_evidence("ownership_score", {"bus_factor": 1}, source="knowledge")

    with patch("dna.api.routers.insights._get_ev_path", return_value=store_path):
        r = client.get("/v1/insights")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["insights"], list)
    assert data["total"] >= 1


def test_v1_insights_filter_severity(tmp_path):
    from dna.evidence.store import EvidenceStore
    store_path = str(tmp_path / "ev.db")
    with EvidenceStore(store_path) as store:
        store.add_evidence("change_frequency", {"changes": 30}, source="git", file_path="hot.py")
        store.add_evidence("complexity_metrics", {"max_complexity": 15}, source="structural", file_path="hot.py")

    with patch("dna.api.routers.insights._get_ev_path", return_value=store_path):
        r = client.get("/v1/insights?severity=high")
    assert r.status_code == 200
    data = r.json()
    assert all(i["severity"] == "high" for i in data["insights"])


def test_v1_insights_generate(tmp_path):
    from dna.evidence.store import EvidenceStore
    store_path = str(tmp_path / "ev.db")
    with EvidenceStore(store_path) as store:
        store.add_evidence("change_frequency", {"changes": 25}, source="git", file_path="main.py")
        store.add_evidence("complexity_metrics", {"max_complexity": 10}, source="structural", file_path="main.py")

    with patch("dna.api.routers.insights._get_ev_path", return_value=store_path):
        r = client.post("/v1/insights/generate")
    assert r.status_code == 200
    data = r.json()
    assert "insights" in data
    assert "count" in data
    assert data["count"] >= 1


def test_v1_analyze_alias(tmp_path):
    """POST /v1/analyze is a versioned alias for /analyze."""
    r = client.post("/v1/analyze", json={"repo_path": "C:\\nonexistent_xyz"})
    assert r.status_code == 400  # path doesn't exist — validation fires
