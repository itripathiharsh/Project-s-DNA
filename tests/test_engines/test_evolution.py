from dna.engines.evolution import analyze_evolution
from dna.models import Commit, CommitHistory, AuthorStats


def _make_history(commits: list[Commit] = None) -> CommitHistory:
    c = commits or [
        Commit(sha="a", message="feat: add login", author_name="Alice",
               insertions=10, deletions=2, files_changed=2,
               committed_at="2024-01-01T00:00:00+00:00"),
        Commit(sha="b", message="fix: crash", author_name="Alice",
               insertions=3, deletions=5, files_changed=1,
               committed_at="2024-01-02T00:00:00+00:00"),
        Commit(sha="c", message="refactor: clean up", author_name="Bob",
               insertions=15, deletions=10, files_changed=3,
               committed_at="2024-01-03T00:00:00+00:00"),
    ]
    return CommitHistory(
        commits=c,
        author_stats=[
            AuthorStats(name="Alice", email="alice@a.com", commit_count=2, insertions=13, deletions=7),
            AuthorStats(name="Bob", email="bob@b.com", commit_count=1, insertions=15, deletions=10),
        ],
    )


def test_analyze_empty():
    result = analyze_evolution(CommitHistory())
    assert result["total_commits"] == 0
    assert result["total_authors"] == 0


def test_commit_counts():
    result = analyze_evolution(_make_history())
    assert result["total_commits"] == 3
    assert result["total_authors"] == 2


def test_commit_categories():
    result = analyze_evolution(_make_history())
    cats = result["commit_categories"]
    assert cats.get("feat") == 1
    assert cats.get("fix") == 1
    assert cats.get("refactor") == 1


def test_insertions_deletions():
    result = analyze_evolution(_make_history())
    assert result["total_insertions"] == 28
    assert result["total_deletions"] == 17


def test_with_evidence_store():
    import tempfile
    import os
    from dna.evidence.store import EvidenceStore

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ev.db")
        with EvidenceStore(path) as store:
            result = analyze_evolution(_make_history(), evidence_store=store)
            assert store.count() >= 2
            evolution_evidence = store.get_by_source("evolution_engine")
            assert len(evolution_evidence) >= 2


def test_evolution_hotspots():
    from dna.models import Entity, EntityGraph, FileChange
    c = [
        Commit(
            sha="a", message="feat: add login", author_name="Alice",
            insertions=10, deletions=2, files_changed=2,
            committed_at="2024-01-01T00:00:00+00:00",
            per_file_changes=[
                FileChange(file_path="src/login.py", insertions=5, deletions=1),
                FileChange(file_path="src/utils.py", insertions=5, deletions=1),
            ]
        ),
        Commit(
            sha="b", message="fix: crash", author_name="Alice",
            insertions=3, deletions=5, files_changed=1,
            committed_at="2024-01-02T00:00:00+00:00",
            per_file_changes=[
                FileChange(file_path="src/login.py", insertions=3, deletions=5),
            ]
        ),
    ]
    history = CommitHistory(
        commits=c,
        author_stats=[
            AuthorStats(name="Alice", email="alice@a.com", commit_count=2, insertions=13, deletions=7),
        ],
    )
    
    eg = EntityGraph()
    eg.add_entity(Entity(uid="f:src/login.py", name="login.py", kind="file", file_path="src/login.py"))
    eg.add_entity(Entity(uid="f:src/utils.py", name="utils.py", kind="file", file_path="src/utils.py"))
    
    result = analyze_evolution(history, entity_graph=eg)
    hotspots = result.get("hotspot_list", [])
    assert len(hotspots) == 2
    assert hotspots[0]["file"] == "src/login.py"
    assert hotspots[0]["change_count"] == 2
    assert hotspots[1]["file"] == "src/utils.py"
    assert hotspots[1]["change_count"] == 1
