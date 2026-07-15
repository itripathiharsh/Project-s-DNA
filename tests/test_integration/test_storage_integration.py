import os
import tempfile
from dna.storage.store import SCStore
from dna.evidence.store import EvidenceStore
from dna.models import EntityGraph, Entity, EntityRelation

def test_storage_integration_flow():
    with tempfile.TemporaryDirectory() as tmpdir:
        sc_db = os.path.join(tmpdir, "sc.db")
        ev_db = os.path.join(tmpdir, "ev.db")
        
        # 1. SCStore Integration
        with SCStore(sc_db) as sc_store:
            # Check user_version set by migration
            conn = sc_store._conn
            cursor = conn.cursor()
            cursor.execute("PRAGMA user_version")
            version = cursor.fetchone()[0]
            assert version > 0
            
            # Save entity graph
            graph = EntityGraph()
            graph.add_entity(Entity(uid="file:a.py", name="a.py", kind="file", file_path="a.py"))
            graph.add_entity(Entity(uid="function:a.py:hello", name="hello", kind="function", file_path="a.py", line=1))
            graph.add_relation(EntityRelation(source_uid="file:a.py", target_uid="function:a.py:hello", kind="CONTAINS"))
            
            sc_store.save_entity_graph(graph)
            
            # Verify stats
            stats = sc_store.get_stats()
            assert stats["entities"] == 2
            assert stats["relations"] == 1
            
        # Re-open and verify persistence
        with SCStore(sc_db) as sc_store:
            loaded_graph = sc_store.load_entity_graph()
            assert len(loaded_graph.entities) == 2
            assert "file:a.py" in loaded_graph.entities
            assert "function:a.py:hello" in loaded_graph.entities
            
        # 2. EvidenceStore Integration
        with EvidenceStore(ev_db) as ev_store:
            # Check user_version set by migration
            conn = ev_store._conn
            cursor = conn.cursor()
            cursor.execute("PRAGMA user_version")
            version = cursor.fetchone()[0]
            assert version > 0
            
            # Add evidence
            ev1 = ev_store.add_evidence("complexity_metrics", {"complexity": 8}, source="structural_engine", file_path="a.py")
            ev2 = ev_store.add_evidence("ownership_score", {"owner": "Alice", "score": 0.9}, source="knowledge_engine", file_path="a.py")
            
            assert ev_store.count() == 2
            
            # Retrieve evidence by type
            comp_ev = ev_store.get_by_type("complexity_metrics")
            assert len(comp_ev) == 1
            assert comp_ev[0].value == '{"complexity": 8}' or comp_ev[0].value == {"complexity": 8}
            
            # Retrieve evidence by file_path
            file_ev = ev_store.get_by_file("a.py")
            assert len(file_ev) == 2
