from dna.engines.knowledge import analyze_knowledge
from dna.models import Commit, CommitHistory, AuthorStats


def _make_history() -> CommitHistory:
    commits = [Commit(sha=str(i), message="msg", author_name=a)
               for i, a in enumerate(["Alice"] * 8 + ["Bob"] * 2)]
    return CommitHistory(
        commits=commits,
        author_stats=[
            AuthorStats(name="Alice", email="alice@a.com", commit_count=8, insertions=100, deletions=20),
            AuthorStats(name="Bob", email="bob@b.com", commit_count=2, insertions=30, deletions=10),
        ],
    )


def test_empty():
    result = analyze_knowledge(CommitHistory())
    assert result["total_authors"] == 0
    assert result["top_contributor"] is None


def test_contributions():
    result = analyze_knowledge(_make_history())
    assert len(result["contributions"]) == 2
    assert result["contributions"][0]["name"] == "Alice"
    assert result["contributions"][0]["share"] == 0.8


def test_top_contributor():
    result = analyze_knowledge(_make_history())
    assert result["top_contributor"] == "Alice"
    assert result["top_contributor_share"] == 0.8


def test_bus_factor():
    result = analyze_knowledge(_make_history())
    assert result["bus_factor"] >= 1
    assert result["bus_factor_risk"] in ("low", "medium", "high")


def test_with_evidence_store():
    import tempfile
    import os
    from dna.evidence.store import EvidenceStore

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            result = analyze_knowledge(_make_history(), evidence_store=store)
            author_evidence = store.get_by_type("author_contribution")
            assert len(author_evidence) >= 2
            assert store.get_by_type("ownership_score") != []


def test_ownership_via_blame():
    import tempfile
    import os
    import subprocess
    from dna.models import Entity, EntityGraph
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize Git repo
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "alice@test.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Alice"], cwd=tmpdir, capture_output=True)
        
        # Alice writes a file
        fpath = os.path.join(tmpdir, "main.txt")
        with open(fpath, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, capture_output=True)
        
        # Bob updates the file (1 line out of 4)
        subprocess.run(["git", "config", "user.email", "bob@test.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Bob"], cwd=tmpdir, capture_output=True)
        with open(fpath, "a") as f:
            f.write("Line 4\n")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "update"], cwd=tmpdir, capture_output=True)
        
        # Setup entity graph with the file
        entities = [
            Entity(uid="main.txt", kind="file", name="main.txt", file_path="main.txt")
        ]
        graph = EntityGraph(entities=entities)
        
        # Analyze knowledge
        from dna.git_history.miner import mine_git_history
        history = mine_git_history(tmpdir)
        result = analyze_knowledge(history, entity_graph=graph, repo_path=tmpdir)
        
        # Check ownership
        scores = result["ownership_scores"]
        assert "main.txt" in scores
        assert scores["main.txt"]["primary_owner"] == "Alice"
        assert scores["main.txt"]["ownership_score"] == 0.75
