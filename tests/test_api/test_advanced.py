import os
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from dna.api.app import app
from dna.models import EntityGraph, Entity, EntityRelation

client = TestClient(app)

def _mock_graph_with_data() -> EntityGraph:
    g = EntityGraph()
    g.add_entity(Entity(uid="file:main.py", name="main.py", kind="file", file_path="main.py"))
    g.add_entity(Entity(uid="class:main.py:UserModel", name="UserModel", kind="class", file_path="main.py"))
    g.add_entity(Entity(uid="function:main.py:get_user", name="get_user", kind="function", file_path="main.py"))
    
    g.add_relation(EntityRelation(source_uid="class:main.py:UserModel", target_uid="function:main.py:get_user", kind="DEPENDS_ON"))
    return g

def test_get_repository_scores(tmp_path):
    store_path = str(tmp_path / "sc_advanced.db")
    ev_path = str(tmp_path / "ev_advanced.db")
    
    from dna.storage.store import SCStore
    with SCStore(store_path) as store:
        store.save_entity_graph(_mock_graph_with_data())

    from dna.evidence.store import EvidenceStore
    with EvidenceStore(ev_path) as store:
        store.add_evidence("complexity_metrics", {"avg_complexity": 4.5, "max_complexity": 8}, source="structural")
        store.add_evidence("risk_metrics", {"overall_risk_score": 4.0}, source="risk")
        store.add_evidence("bus_factor", {"bus_factor": 2, "contributions": [{"name": "Tester", "commit_count": 10, "share": 1.0}]}, source="knowledge")

    with patch("dna.api.routers.advanced._get_store_path", return_value=store_path), \
         patch("dna.api.routers.advanced._get_ev_path", return_value=ev_path):
        r = client.get("/v1/advanced/scores")
    
    assert r.status_code == 200
    data = r.json()
    assert "scores" in data
    assert "health" in data["scores"]
    assert "quality" in data["scores"]
    assert data["scores"]["health"]["score"] > 0
    assert "ai_summary" in data

def test_get_architecture_views(tmp_path):
    store_path = str(tmp_path / "sc_advanced.db")
    from dna.storage.store import SCStore
    with SCStore(store_path) as store:
        store.save_entity_graph(_mock_graph_with_data())

    with patch("dna.api.routers.advanced._get_store_path", return_value=store_path):
        r = client.get("/v1/advanced/architecture/views?view_type=er")
    
    assert r.status_code == 200
    data = r.json()
    assert "nodes" in data
    assert "links" in data
    # Class nodes
    assert any(n["kind"] == "class" for n in data["nodes"])

def test_ask_repository_ai(tmp_path):
    ev_path = str(tmp_path / "ev_advanced.db")
    from dna.evidence.store import EvidenceStore
    with EvidenceStore(ev_path) as store:
        store.add_evidence("risk_metrics", {"overall_risk_score": 4.0}, source="risk")

    with patch("dna.api.routers.advanced._get_ev_path", return_value=ev_path):
        r = client.post("/v1/advanced/chat", json={"prompt": "Find complexity risks in my codebase"})
    
    assert r.status_code == 200
    data = r.json()
    assert "reply" in data
    assert "grounded_evidence_count" in data

def test_trigger_ai_agent_action():
    r = client.post("/v1/advanced/action", json={"action_type": "audit", "target_file": "backend/app.py"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert "findings" in data

def test_get_github_metrics(tmp_path):
    ev_path = str(tmp_path / "ev_advanced.db")
    with patch("dna.api.routers.advanced._get_ev_path", return_value=ev_path):
        r = client.get("/v1/advanced/github/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "bus_factor" in data
    assert "contributors" in data
    assert "commit_activity_heatmap" in data

def test_get_code_smells(tmp_path):
    store_path = str(tmp_path / "sc_advanced.db")
    with patch("dna.api.routers.advanced._get_store_path", return_value=store_path):
        r = client.get("/v1/advanced/code/smells")
    assert r.status_code == 200
    data = r.json()
    assert "smells" in data

def test_get_security_report(tmp_path):
    store_path = str(tmp_path / "sc_advanced.db")
    with patch("dna.api.routers.advanced._get_store_path", return_value=store_path):
        r = client.get("/v1/advanced/security/report")
    assert r.status_code == 200
    data = r.json()
    assert "security_score" in data
    assert "findings" in data

def test_get_performance_hotpaths():
    r = client.get("/v1/advanced/performance/hotpaths")
    assert r.status_code == 200
    data = r.json()
    assert "performance_score" in data
    assert "hotpaths" in data
