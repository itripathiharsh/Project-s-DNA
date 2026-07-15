# Sprint 02 — Git History Engine

## Goal
Extract complete Git history (commits, branches, tags, authors, file changes) from a repository using `git` CLI subprocess calls. Enable downstream evolution and knowledge analysis.

## Package
`backend/dna/git_history/`

## Data Models (in `backend/dna/models.py`)

### Commit
- `sha: str` — full commit hash
- `parents: list[str]` — parent hashes
- `author_name: str`
- `author_email: str`
- `authored_at: datetime` — author timestamp
- `committer_name: str`
- `committer_email: str`
- `committed_at: datetime`
- `message: str` — subject line
- `insertions: int = 0`
- `deletions: int = 0`
- `files_changed: int = 0`

### Branch
- `name: str`
- `target_sha: str`
- `is_head: bool`
- `is_remote: bool`

### Tag
- `name: str`
- `target_sha: str`
- `tagger_name: str | None`
- `tagger_email: str | None`
- `tagged_at: datetime | None`
- `message: str = ""`

### FileChange
- `file_path: str`
- `insertions: int`
- `deletions: int`
- `change_type: str` — added / modified / deleted

### AuthorStats
- `name: str`
- `email: str`
- `commit_count: int = 0`
- `first_commit_at: datetime | None`
- `last_commit_at: datetime | None`
- `insertions: int = 0`
- `deletions: int = 0`

### CommitHistory
- `commits: list[Commit]`
- `branches: list[Branch]`
- `tags: list[Tag]`
- `author_stats: list[AuthorStats]`
- `total_branches: int`
- `total_tags: int`

## Modules

### `commit_parser.py`
- `parse_commit_log(path: str) -> list[Commit]` — runs `git log --all --reverse --format=... --numstat`, streams parse
- `categorize_commit(message: str) -> str` — returns feat/fix/refactor/test/docs/chore using keyword matching

### `branch_detector.py`
- `detect_branches(path: str) -> list[Branch]` — runs `git branch -a` and `git branch --show-current`
- `detect_merge_commits(commits: list[Commit]) -> list[Commit]` — filters commits with >1 parent

### `tag_mapper.py`
- `map_tags(path: str) -> list[Tag]` — runs `git tag -l --format=...` and parses annotated vs lightweight

### `author_analyzer.py`
- `analyze_authors(commits: list[Commit]) -> list[AuthorStats]` — aggregates per author
- `build_contribution_matrix(commits: list[Commit]) -> dict[str, int]` — author → commit count

### `diff_analyzer.py`
- `get_file_changes(path: str, sha: str) -> list[FileChange]` — runs `git diff-tree --numstat`
- `get_commit_diff(path: str, sha: str) -> str` — runs `git diff-tree -p`

### `miner.py` (orchestrator)
- `mine_git_history(path: str) -> CommitHistory` — orchestrates all steps
- Raises `PathNotFoundError` / `NotAGitRepositoryError` / `GitNotInstalledError` / `GitCommandError`

### `errors.py`
- `GitHistoryError(Exception)` — base
- `GitNotInstalledError(GitHistoryError)`
- `GitCommandError(GitHistoryError)`

## Test Plan
- `test_commit_parser.py` — parse empty repo, single commit, merge commit, categorized commits
- `test_branch_detector.py` — detect branches, detect merge commits
- `test_tag_mapper.py` — lightweight tag, annotated tag, no tags
- `test_author_analyzer.py` — single author, multiple authors, contributions sorted
- `test_diff_analyzer.py` — single file change, rename, delete
- `test_miner.py` — full integration test with temp git repo
