import subprocess
import shutil
from datetime import datetime, timezone
from dna.models import Commit, FileChange
from dna.git_history.errors import GitNotInstalledError, GitCommandError


_COMMIT_FORMAT = "---COMMIT---%n%H%n%P%n%an%n%ae%n%at%n%cn%n%ce%n%ct%n%s%n---DIFF---"


def _check_git_installed():
    if shutil.which("git") is None:
        raise GitNotInstalledError()


def _run_git(cmd: list[str], cwd: str) -> str:
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", cwd=cwd, timeout=300
        )
    except FileNotFoundError:
        raise GitNotInstalledError()
    if proc.returncode != 0:
        raise GitCommandError(" ".join(cmd), proc.returncode, proc.stderr)
    return proc.stdout


def _run_git_stream(cmd: list[str], cwd: str):
    _check_git_installed()
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, text=True, encoding="utf-8"
        )
    except FileNotFoundError:
        raise GitNotInstalledError()
    return proc


def parse_commit_log(path: str) -> list[Commit]:
    cmd = [
        "git", "log", "--all", "--reverse",
        f"--format={_COMMIT_FORMAT}",
        "--numstat",
    ]
    proc = _run_git_stream(cmd, path)
    try:
        commits = _stream_parse(proc)
        stderr = proc.stderr.read() if proc.stderr else ""
        ret = proc.wait()
        if ret != 0:
            raise GitCommandError(" ".join(cmd), ret, stderr)
        return commits
    except:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
        raise


def _stream_parse(proc) -> list[Commit]:
    commits: list[Commit] = []
    current: dict = {}
    in_diff = False
    files_changed = 0
    insertions = 0
    deletions = 0
    field_idx = 0
    file_changes: list[FileChange] = []

    for line in proc.stdout:
        line = line.rstrip("\n")

        if line == "---COMMIT---":
            if current.get("sha"):
                current["files_changed"] = files_changed
                current["insertions"] = insertions
                current["deletions"] = deletions
                current["per_file_changes"] = file_changes
                commits.append(Commit(**current))
            current = {}
            in_diff = False
            field_idx = 0
            files_changed = 0
            insertions = 0
            deletions = 0
            file_changes = []
            continue

        if line == "---DIFF---":
            in_diff = True
            continue

        if in_diff:
            if not line.strip():
                continue
            parts = line.split("\t", 2)
            if len(parts) == 3:
                try:
                    add = int(parts[0]) if parts[0] != "-" else 0
                    dlt = int(parts[1]) if parts[1] != "-" else 0
                    file_path = parts[2].strip()
                    insertions += add
                    deletions += dlt
                    files_changed += 1
                    file_changes.append(FileChange(
                        file_path=file_path,
                        insertions=add,
                        deletions=dlt,
                        change_type="modified",
                    ))
                except ValueError:
                    pass
            continue

        if field_idx == 0:
            current["sha"] = line
        elif field_idx == 1:
            current["parents"] = line.split() if line else []
        elif field_idx == 2:
            current["author_name"] = line
        elif field_idx == 3:
            current["author_email"] = line
        elif field_idx == 4:
            current["authored_at"] = _ts_to_iso(line)
        elif field_idx == 5:
            current["committer_name"] = line
        elif field_idx == 6:
            current["committer_email"] = line
        elif field_idx == 7:
            current["committed_at"] = _ts_to_iso(line)
        elif field_idx == 8:
            current["message"] = line
        field_idx += 1

    if current.get("sha"):
        current["files_changed"] = files_changed
        current["insertions"] = insertions
        current["deletions"] = deletions
        current["per_file_changes"] = file_changes
        commits.append(Commit(**current))

    return commits


def _ts_to_iso(ts: str) -> str:
    try:
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        return dt.isoformat()
    except (ValueError, OSError):
        return ts


_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "feat": ["feat", "feature", "add", "implement", "introduce"],
    "fix": ["fix", "bug", "patch", "hotfix", "correct"],
    "refactor": ["refactor", "clean", "rename", "restructure", "rewrite"],
    "test": ["test", "spec", "assert"],
    "docs": ["doc", "readme", "documentation"],
    "chore": ["chore", "bump", "update", "upgrade", "downgrade"],
}


def categorize_commit(message: str) -> str:
    msg_lower = message.lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        for kw in keywords:
            first_word = msg_lower.split()[0].rstrip(":") if msg_lower.split() else ""
            if first_word == kw:
                return category
    return "other"
