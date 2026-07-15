from dna.git_history.author_analyzer import analyze_authors, build_contribution_matrix
from dna.models import Commit


def test_analyze_authors_single():
    commits = [
        Commit(sha="a", author_name="Alice", author_email="alice@a.com",
               insertions=10, deletions=2),
        Commit(sha="b", author_name="Alice", author_email="alice@a.com",
               insertions=5, deletions=1),
    ]
    stats = analyze_authors(commits)
    assert len(stats) == 1
    assert stats[0].name == "Alice"
    assert stats[0].commit_count == 2
    assert stats[0].insertions == 15
    assert stats[0].deletions == 3


def test_analyze_authors_multiple():
    commits = [
        Commit(sha="a", author_name="Alice", author_email="alice@a.com"),
        Commit(sha="b", author_name="Bob", author_email="bob@b.com"),
        Commit(sha="c", author_name="Alice", author_email="alice@a.com"),
    ]
    stats = analyze_authors(commits)
    assert len(stats) == 2
    assert stats[0].name == "Alice"
    assert stats[0].commit_count == 2
    assert stats[1].name == "Bob"
    assert stats[1].commit_count == 1


def test_analyze_authors_sorted_by_count():
    commits = [
        Commit(sha="a", author_name="Bob", author_email="bob@b.com"),
        Commit(sha="b", author_name="Alice", author_email="alice@a.com"),
        Commit(sha="c", author_name="Alice", author_email="alice@a.com"),
        Commit(sha="d", author_name="Alice", author_email="alice@a.com"),
    ]
    stats = analyze_authors(commits)
    assert stats[0].name == "Alice"
    assert stats[1].name == "Bob"


def test_analyze_authors_empty():
    assert analyze_authors([]) == []


def test_build_contribution_matrix():
    commits = [
        Commit(sha="a", author_name="Alice", author_email="alice@a.com"),
        Commit(sha="b", author_name="Bob", author_email="bob@b.com"),
        Commit(sha="c", author_name="Alice", author_email="alice@a.com"),
    ]
    matrix = build_contribution_matrix(commits)
    assert matrix["alice@a.com"] == 2
    assert matrix["bob@b.com"] == 1


def test_build_contribution_matrix_empty():
    assert build_contribution_matrix([]) == {}
