import os
from dna.models import FileInventory, RepositoryMetadata
from dna.discovery.orchestrator import PathNotFoundError, get_cached_files
from dna.discovery.scanner import scan_files
from dna.discovery.ignore import parse_gitignore, parse_dnaignore
from dna.indexer.inventory import build_file_inventory


def index_repository(
    path: str,
    repo_metadata: RepositoryMetadata,
    previous_inventory: FileInventory | None = None,
) -> FileInventory:
    if not os.path.exists(path):
        raise PathNotFoundError(path)

    # Reuse the file list discovered by discover_repository() if present,
    # avoiding a redundant second filesystem walk + ignore-pattern parse.
    cached = get_cached_files(path)
    if cached is not None:
        files = list(cached)
    else:
        gitignore_patterns = parse_gitignore(path)
        dnaignore_patterns = parse_dnaignore(path)
        all_ignore_patterns = list(set(gitignore_patterns + dnaignore_patterns))
        files = scan_files(path, all_ignore_patterns)

    return build_file_inventory(files, repo_metadata, previous_inventory)
