from dna.models import Branch, Commit
from dna.git_history.commit_parser import _run_git


def detect_branches(path: str) -> list[Branch]:
    out = _run_git(["git", "branch", "-a"], path)
    branches: list[Branch] = []
    head_name = _run_git(["git", "branch", "--show-current"], path).strip()

    for line in out.splitlines():
        name = line.strip()
        is_head = False
        is_remote = False

        if line.startswith("* "):
            is_head = True
            name = line[2:].strip()
        elif line.startswith("  "):
            name = line.strip()

        if name.startswith("remotes/"):
            is_remote = True
            name = name[len("remotes/"):]

        if not name:
            continue

        branches.append(Branch(
            name=name,
            is_head=is_head or (name == head_name),
            is_remote=is_remote,
        ))

    if not branches:
        branches.append(Branch(name="HEAD", is_head=True))

    return branches


def detect_merge_commits(commits: list[Commit]) -> list[Commit]:
    return [c for c in commits if len(c.parents) > 1]
