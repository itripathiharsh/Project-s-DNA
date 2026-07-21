import os
from dna.models import CommitHistory
from dna.discovery.git import is_git_repository
from dna.discovery.orchestrator import PathNotFoundError, NotAGitRepositoryError
from dna.git_history.errors import GitNotInstalledError, GitCommandError
from dna.git_history.commit_parser import parse_commit_log
from dna.git_history.branch_detector import detect_branches
from dna.git_history.tag_mapper import map_tags
from dna.git_history.author_analyzer import analyze_authors
from dna.config import get_config


def mine_git_history(path: str) -> CommitHistory:
    # SECURITY: Canonicalize path to resolve any .. components
    from dna.security.path_validation import safe_validate_path
    try:
        path = safe_validate_path(path)
    except ValueError:
        raise PathNotFoundError(path)
    if not os.path.exists(path):
        raise PathNotFoundError(path)
    if not os.path.isdir(path):
        raise PathNotFoundError(path)
    if not is_git_repository(path):
        raise NotAGitRepositoryError(path)

    try:
        commits = parse_commit_log(path)
    except GitCommandError as e:
        if "does not have any commits" in e.stderr:
            commits = []
        else:
            raise

    try:
        branches = detect_branches(path)
    except (GitCommandError, GitNotInstalledError):
        branches = []

    try:
        tags = map_tags(path)
    except (GitCommandError, GitNotInstalledError):
        tags = []

    author_stats = analyze_authors(commits)

    return CommitHistory(
        commits=commits,
        branches=branches,
        tags=tags,
        author_stats=author_stats,
        total_branches=len(branches),
        total_tags=len(tags),
    )
