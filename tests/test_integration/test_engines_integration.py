import os
import tempfile
from dna.engines.structural import analyze_structure
from dna.engines.evolution import analyze_evolution
from dna.engines.knowledge import analyze_knowledge
from dna.engines.risk import analyze_risks
from dna.evidence.store import EvidenceStore
from dna.models import (
    EntityGraph, Entity, EntityRelation, DependencyGraph,
    Commit, CommitHistory, AuthorStats
)

def test_all_engines_integration():
    # Setup mock entity graph
    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:main.py", name="main.py", kind="file", file_path="main.py"))
    graph.add_entity(Entity(uid="function:main.py:foo", name="foo", kind="function", file_path="main.py", line=1))
    graph.add_relation(EntityRelation(source_uid="file:main.py", target_uid="function:main.py:foo", kind="CONTAINS"))
    
    # Setup mock dependency graph
    dep_graph = DependencyGraph()
    
    # Setup mock git history
    commits = [
        Commit(
            sha="abc123",
            message="initial commit",
            author_name="Alice",
            insertions=10,
            deletions=0,
            files_changed=1,
            committed_at="2024-01-01T00:00:00+00:00"
        )
    ]
    history = CommitHistory(
        commits=commits,
        author_stats=[
            AuthorStats(name="Alice", email="alice@test.com", commit_count=1, insertions=10, deletions=0)
        ]
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        ev_db = os.path.join(tmpdir, "ev.db")
        
        with EvidenceStore(ev_db) as ev_store:
            # 1. Structural Engine
            struct_res = analyze_structure(graph, ev_store)
            assert struct_res is not None
            assert struct_res["total_functions"] == 1
            
            # 2. Evolution Engine
            evol_res = analyze_evolution(history, graph, evidence_store=ev_store)
            assert evol_res is not None
            assert evol_res["total_commits"] == 1
            
            # 3. Knowledge Engine
            know_res = analyze_knowledge(history, graph, ev_store, repo_path=tmpdir)
            assert know_res is not None
            
            # 4. Risk Engine
            risk_res = analyze_risks(graph, dep_graph, ev_store)
            assert risk_res is not None
            
            # Verify evidence store has compiled all engine outputs
            evidence_list = ev_store.get_all()
            assert len(evidence_list) > 0
            
            # Check presence of specific evidence types from the engines
            ev_types = {e.type for e in evidence_list}
            assert "complexity_metrics" in ev_types or "size_metrics" in ev_types
            assert "commit_metadata" in ev_types
            assert "author_contribution" in ev_types
            assert "risk_metrics" in ev_types
