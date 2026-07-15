import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dna.discovery.git import is_git_repository
from dna.discovery.orchestrator import NotAGitRepositoryError
from dna.git_history.errors import GitNotInstalledError, GitCommandError


def _check_git_installed():
    if shutil.which("git") is None:
        raise GitNotInstalledError()


def _git_repo_check(repo_path: str) -> None:
    # Combined, single is_git_repository check; the per-file calls used to
    # repeat this on every invocation.
    if not is_git_repository(repo_path):
        raise NotAGitRepositoryError(repo_path)


def _relpath(file_path: str, repo_path: str) -> str:
    if os.path.isabs(file_path):
        try:
            return os.path.relpath(file_path, repo_path)
        except ValueError:
            return file_path
    return file_path


def _blame_one(repo_path: str, rel_path: str) -> dict[str, int]:
    """Run a single git blame on one file. Returns author -> line count.

    On untracked/no-commit files git blame returns non-zero; we map that to
    {} (the original behavior) so downstream ownership scores fall back to
    the commit-share heuristic exactly as before.
    """
    cmd = ["git", "blame", "--line-porcelain", rel_path]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", cwd=repo_path, timeout=30
        )
    except FileNotFoundError:
        raise GitNotInstalledError()
    except subprocess.TimeoutExpired:
        raise GitCommandError(" ".join(cmd), -1, "Timeout expired")

    if proc.returncode != 0:
        return {}

    author_counts: dict[str, int] = {}
    for line in proc.stdout.splitlines():
        if line.startswith("author "):
            author_name = line[len("author "):].strip()
            if author_name == "Not Committed Yet":
                author_name = "Uncommitted"
            author_counts[author_name] = author_counts.get(author_name, 0) + 1
    return author_counts


def get_file_blame(repo_path: str, file_path: str) -> dict[str, int]:
    """
    Runs git blame --line-porcelain on the specified file and returns a dictionary
    mapping author name to the count of lines they authored.
    """
    _check_git_installed()
    _git_repo_check(repo_path)
    return _blame_one(repo_path, _relpath(file_path, repo_path))


def get_files_blame(
    repo_path: str,
    file_paths: list[str],
    max_workers: int = 8,
) -> dict[str, dict[str, int]]:
    """Batched per-file git blame.

    Replaces the previous pattern of one sequential subprocess per file with
    a single concurrent fan-out. Each file still gets its own `git blame`
    invocation (so per-file output is byte-for-byte identical), but the
    subprocesses run in parallel with a bounded worker pool, drastically
    reducing wall time on repos with many files.

    Returns a mapping {file_path: {author: line_count}} for every file.
    Files that are untracked / have no commits yield {} (matching the
    original single-file fallback).
    """
    _check_git_installed()
    _git_repo_check(repo_path)

    rel_paths = [(_relpath(fp, repo_path), fp) for fp in file_paths]
    out: dict[str, dict[str, int]] = {}

    with ThreadPoolExecutor(max_workers=max(1, min(max_workers, len(rel_paths) or 1))) as pool:
        future_to_path = {
            pool.submit(_blame_one, repo_path, rel): fp for rel, fp in rel_paths
        }
        for fut in __import__("concurrent.futures", fromlist=["as_completed"]).as_completed(future_to_path):
            fp = future_to_path[fut]
            try:
                out[fp] = fut.result()
            except (GitNotInstalledError, GitCommandError):
                # Preserve original fallback: ignore this file's blame and
                # let the caller downgrade to commit-share scoring.
                out[fp] = {}

    return out
