from dna.models import Commit, AuthorStats


def analyze_authors(commits: list[Commit]) -> list[AuthorStats]:
    stats_map: dict[str, AuthorStats] = {}

    for c in commits:
        key = c.author_email or c.author_name
        if key not in stats_map:
            stats_map[key] = AuthorStats(
                name=c.author_name,
                email=c.author_email,
            )
        s = stats_map[key]
        s.commit_count += 1
        s.insertions += c.insertions
        s.deletions += c.deletions
        if s.first_commit_at is None:
            s.first_commit_at = c.committed_at
        else:
            s.first_commit_at = min(s.first_commit_at, c.committed_at) if c.committed_at else s.first_commit_at
        if s.last_commit_at is None:
            s.last_commit_at = c.committed_at
        else:
            s.last_commit_at = max(s.last_commit_at, c.committed_at) if c.committed_at else s.last_commit_at

    result = list(stats_map.values())
    result.sort(key=lambda a: a.commit_count, reverse=True)
    return result


def build_contribution_matrix(commits: list[Commit]) -> dict[str, int]:
    matrix: dict[str, int] = {}
    for c in commits:
        key = c.author_email or c.author_name
        matrix[key] = matrix.get(key, 0) + 1
    return matrix
