from dna.models import Tag
from dna.git_history.commit_parser import _run_git


def map_tags(path: str) -> list[Tag]:
    out = _run_git(["git", "tag", "-l"], path)
    tag_names = [t.strip() for t in out.splitlines() if t.strip()]

    tags: list[Tag] = []
    for name in tag_names:
        sha = _run_git(["git", "rev-list", "-1", name], path).strip()
        tags.append(Tag(name=name, target_sha=sha))

    return tags
