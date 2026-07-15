from dna.models import FileChange
from dna.git_history.commit_parser import _run_git


def get_file_changes(path: str, sha: str) -> list[FileChange]:
    out = _run_git(["git", "diff-tree", "--numstat", "-r", "--root", sha], path)
    changes: list[FileChange] = []

    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            insertions = int(parts[0]) if parts[0] != "-" else 0
            deletions = int(parts[1]) if parts[1] != "-" else 0
        except ValueError:
            insertions = 0
            deletions = 0
        file_path = parts[2]

        change_type = "modified"
        if insertions > 0 and deletions == 0:
            change_type = "added"
        elif deletions > 0 and insertions == 0:
            change_type = "deleted"

        changes.append(FileChange(
            file_path=file_path,
            insertions=insertions,
            deletions=deletions,
            change_type=change_type,
        ))

    return changes


def get_commit_diff(path: str, sha: str) -> str:
    return _run_git(["git", "diff-tree", "-p", "--root", sha], path)
