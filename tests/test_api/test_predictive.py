import os
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from dna.api.app import app
from dna.models import EntityGraph, Entity, EntityRelation

client = TestClient(app)

def _seed_test_data(tmp_path):
    from dna.storage.store import SCStore
    from dna.evidence.store import EvidenceStore

    sc_path = str(tmp_path / "sc.db")
    ev_path = str(tmp_path / "ev.db")

    # 1. Seed SCStore
    g = EntityGraph()
    g.add_entity(Entity(uid="file:src/main.py", name="main.py", kind="file", file_path="src/main.py"))
    g.add_entity(Entity(uid="function:src/main.py:hello", name="hello", kind="function", file_path="src/main.py"))
    g.add_entity(Entity(uid="file:src/utils.py", name="utils.py", kind="file", file_path="src/utils.py"))
    g.add_relation(EntityRelation(source_uid="file:src/main.py", target_uid="file:src/utils.py", kind="IMPORTS"))
    
    with SCStore(sc_path) as sc:
        sc.save_entity_graph(g)
        sc.set_metadata("repo_path", str(tmp_path))

    # 2. Seed EvidenceStore
    with EvidenceStore(ev_path) as ev:
        ev.add_evidence("change_frequency", {"change_count": 12}, source="git_history", file_path="src/main.py")
        ev.add_evidence("change_frequency", {"change_count": 3}, source="git_history", file_path="src/utils.py")
        ev.add_evidence("commit_metadata", {
            "hash": "abc1234",
            "author": "Alice",
            "date": "2026-07-18T00:00:00Z",
            "message": "feat: initial commit",
            "insertions": 100,
            "deletions": 5,
            "files": [{"file_path": "src/main.py", "insertions": 100, "deletions": 5, "change_type": "added"}]
        }, source="evolution_engine")

    return sc_path, ev_path

def test_predictive_forecast_endpoint(tmp_path):
    sc_path, ev_path = _seed_test_data(tmp_path)

    # Mock the paths returned by routers.system helpers
    with patch("dna.api.routers.predictive._get_store_path", return_value=sc_path), \
         patch("dna.api.routers.predictive._get_ev_path", return_value=ev_path), \
         patch("dna.api.routers.predictive._get_active_repo_path", return_value=str(tmp_path)):
        
        response = client.get("/v1/predictive/forecast")
        
    assert response.status_code == 200
    data = response.json()

    # Ensure all 10 main predictive sections exist
    assert "summary" in data
    assert "bug_prediction" in data
    assert "regression_prediction" in data
    assert "crash_probability" in data
    assert "scalability_prediction" in data
    assert "future_technical_debt" in data
    assert "future_complexity" in data
    assert "future_coupling" in data
    assert "future_risk" in data
    assert "future_architecture_drift" in data
    assert "future_maintenance_cost" in data

    # Verify bug prediction format
    bp = data["bug_prediction"]
    assert "score" in bp
    assert len(bp["top_affected"]) > 0
    assert bp["top_affected"][0]["file_path"] == "src/main.py"
    assert "probability" in bp["top_affected"][0]
    assert "reasons" in bp["top_affected"][0]

    # Verify regression prediction format
    rp = data["regression_prediction"]
    assert "score" in rp
    assert len(rp["top_affected"]) > 0

    # Verify crash probability format
    cp = data["crash_probability"]
    assert "score" in cp

    # Verify scalability format
    sp = data["scalability_prediction"]
    assert "score" in sp

    # Verify 12 month timeline projections
    for key in [
        "future_technical_debt",
        "future_complexity",
        "future_coupling",
        "future_risk",
        "future_architecture_drift",
        "future_maintenance_cost"
    ]:
        assert "timeline" in data[key]
        assert len(data[key]["timeline"]) == 13  # 0 to 12 inclusive
        assert data[key]["timeline"][0]["month"] == 0
        assert data[key]["timeline"][12]["month"] == 12
        assert "value" in data[key]["timeline"][0]
