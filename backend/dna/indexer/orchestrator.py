import os
import logging
from dna.models import FileInventory, RepositoryMetadata, IndexedFile
from dna.discovery.orchestrator import PathNotFoundError, get_cached_files
from dna.discovery.scanner import scan_files
from dna.discovery.ignore import parse_gitignore, parse_dnaignore
from dna.indexer.inventory import build_file_inventory

logger = logging.getLogger("dna.indexer")

def index_repository(
    path: str,
    repo_metadata: RepositoryMetadata,
    previous_inventory: FileInventory | None = None,
) -> FileInventory:
    if not os.path.exists(path):
        raise PathNotFoundError(path)

    # If previous_inventory is not provided, try to load the previously stored entity graph
    # to construct the baseline inventory of file hashes.
    if previous_inventory is None:
        try:
            from dna.storage.store import SCStore
            from dna.config import get_config
            cfg = get_config()
            store_path = cfg.store_path or os.path.join(os.getcwd(), "sc_store.db")
            if os.path.exists(store_path):
                with SCStore(store_path) as store:
                    graph = store.load_entity_graph()
                
                old_files = []
                seen_files = {}
                for e in graph.entities:
                    if e.file_path and e.file_path not in seen_files:
                        seen_files[e.file_path] = getattr(e, "hash", "")
                
                for rel_path, h in seen_files.items():
                    old_files.append(IndexedFile(
                        path=os.path.join(path, rel_path),
                        relative_path=rel_path,
                        filename=os.path.basename(rel_path),
                        extension=os.path.splitext(rel_path)[1],
                        language="",
                        size_bytes=0,
                        is_directory=False,
                        is_source=True,
                        content_hash=h
                    ))
                previous_inventory = FileInventory(files=old_files)
                logger.info("Loaded %d files from cache for incremental analysis", len(old_files))
        except Exception as e:
            logger.warning("Could not load previous entity graph for incremental baseline: %s", e)

    # Reuse cached files or scan filesystem
    cached = get_cached_files(path)
    if cached is not None:
        files = list(cached)
    else:
        gitignore_patterns = parse_gitignore(path)
        dnaignore_patterns = parse_dnaignore(path)
        all_ignore_patterns = list(set(gitignore_patterns + dnaignore_patterns))
        files = scan_files(path, all_ignore_patterns)

    return build_file_inventory(files, repo_metadata, previous_inventory)
