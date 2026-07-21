import os
import time
import logging
from dna.models import RepositoryMetadata
from dna.discovery.git import is_git_repository
from dna.discovery.ignore import parse_gitignore, parse_dnaignore
from dna.discovery.scanner import scan_files
from dna.discovery.languages import classify_files
from dna.discovery.build_system import detect_build_systems
from dna.discovery.frameworks import detect_frameworks

logger = logging.getLogger("dna.discovery")


class DiscoveryError(Exception):
    pass


class PathNotFoundError(DiscoveryError):
    def __init__(self, path: str):
        super().__init__(f"Path does not exist: {path}")
        self.path = path


class NotAGitRepositoryError(DiscoveryError):
    def __init__(self, path: str):
        super().__init__(f"Not a Git repository: {path}. Initialize with 'git init' first.")
        self.path = path


# In-process cache of discovered files per repository path. Populated by
# discover_repository() so that index_repository() can reuse the result
# without walking the filesystem a second time. Keyed on the normalized
# absolute repo path. Cleared only when the process exits or when explicitly
# invalidated (see clear_discovery_cache).
_discovered_files_cache: dict[str, list] = {}


def clear_discovery_cache() -> None:
    """Drop the cached discovered file lists (used by tests)."""
    _discovered_files_cache.clear()


def get_cached_files(path: str):
    """Return the cached list[FileInfo] for ``path`` if present, else None."""
    key = os.path.normpath(os.path.abspath(path))
    return _discovered_files_cache.get(key)


def _count_visible_files(root: str) -> int:
    count = 0
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            count += len(filenames)
    except OSError:
        logger.debug("Failed to count visible files in %s", root)
    return count


def discover_repository(path: str) -> RepositoryMetadata:
    logger.info("Starting repository discovery for path: %s", path)
    if not os.path.exists(path):
        logger.error("Path not found: %s", path)
        raise PathNotFoundError(path)

    if not os.path.isdir(path):
        logger.error("Path is not a directory: %s", path)
        raise PathNotFoundError(path)

    start = time.perf_counter()

    is_git = is_git_repository(path)
    name = os.path.basename(os.path.normpath(path))

    gitignore_patterns = parse_gitignore(path)
    dnaignore_patterns = parse_dnaignore(path)
    all_ignore_patterns = list(set(gitignore_patterns + dnaignore_patterns))

    total_before_filter = _count_visible_files(path)
    files = scan_files(path, all_ignore_patterns)
    ignored_count = max(0, total_before_filter - len(files))

    # Cache the discovered file list so downstream stages (e.g. the indexer)
    # can reuse it without re-walking the filesystem.
    cache_key = os.path.normpath(os.path.abspath(path))
    _discovered_files_cache[cache_key] = list(files)

    language_stats = classify_files(files)
    stats_list = list(language_stats.values())
    stats_list.sort(key=lambda s: s.file_count, reverse=True)

    primary_language = stats_list[0].language if stats_list else None
    total_size = sum(s.total_bytes for s in stats_list)

    build_systems = detect_build_systems(path)
    frameworks = detect_frameworks(path, build_systems)

    duration = (time.perf_counter() - start) * 1000

    logger.info(
        "Discovery completed. Found %d files. Primary language: %s. Size: %d bytes. Ignored: %d",
        len(files), primary_language, total_size, ignored_count
    )

    return RepositoryMetadata(
        name=name,
        path=os.path.abspath(path),
        is_git=is_git,
        languages=stats_list,
        primary_language=primary_language,
        build_systems=build_systems,
        frameworks=frameworks,
        file_count=len(files),
        total_size_bytes=total_size,
        ignored_files_count=ignored_count,
        scan_duration_ms=round(duration, 2),
        has_dna_ignore=len(dnaignore_patterns) > 0,
    )
