import os


def is_git_repository(path: str) -> bool:
    if not os.path.isdir(path):
        return False
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir) or os.path.isfile(git_dir)
