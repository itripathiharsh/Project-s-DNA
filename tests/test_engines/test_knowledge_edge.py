from dna.engines.knowledge import analyze_knowledge
from dna.models import CommitHistory, AuthorStats, Commit


def test_single_author():
    h = CommitHistory(
        commits=[Commit(sha="a", message="m", author_name="Alice")],
        author_stats=[AuthorStats(name="Alice", email="a@a.com", commit_count=1, insertions=5, deletions=0)],
    )
    result = analyze_knowledge(h)
    assert result["total_authors"] == 1
    assert result["bus_factor"] == 1
    assert result["bus_factor_risk"] == "high"


def test_many_authors_bus_factor():
    stats = [AuthorStats(name=f"Dev{i}", email=f"{i}@x.com", commit_count=1, insertions=0, deletions=0)
             for i in range(20)]
    h = CommitHistory(
        commits=[Commit(sha=str(i), message="m", author_name=f"Dev{i}") for i in range(20)],
        author_stats=stats,
    )
    result = analyze_knowledge(h)
    assert result["bus_factor"] >= 10
    assert result["bus_factor_risk"] == "low"


def test_contributions_sorted():
    stats = [AuthorStats(name="Bob", email="b@b.com", commit_count=1, insertions=0, deletions=0),
             AuthorStats(name="Alice", email="a@a.com", commit_count=10, insertions=0, deletions=0)]
    h = CommitHistory(
        commits=[Commit(sha=str(i), message="m", author_name="Alice") for i in range(10)]
               + [Commit(sha="x", message="m", author_name="Bob")],
        author_stats=stats,
    )
    result = analyze_knowledge(h)
    assert result["contributions"][0]["name"] == "Alice"
