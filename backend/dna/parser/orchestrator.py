import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dna.models import FileInventory, ParsedFile, FileCategory
from dna.parser.ast_builder import parse_file
from dna.parser.factory import is_language_supported
from dna.parser.errors import ParserError

logger = logging.getLogger("dna.parser")

def is_binary_file(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except OSError:
        return True

def parse_repository(
    inventory: FileInventory,
    max_workers: int | None = None,
) -> list[ParsedFile]:
    if max_workers is None:
        from dna.config import get_config
        max_workers = get_config().parser_max_workers

    source_files = []
    for f in inventory.files:
        if f.category == FileCategory.SOURCE and is_language_supported(f.language):
            if is_binary_file(f.path):
                logger.warning("Skipping binary file: %s", f.relative_path)
                continue
            
            # Incremental support: skip parsing if the file has not changed
            change_type = getattr(f, "change_type", "modified")
            if change_type == "unchanged":
                logger.info("Incremental: skipping parsing for unchanged file %s", f.relative_path)
                continue
                
            source_files.append(f)

    logger.info("Parsing %d changed/new source files using %d workers", len(source_files), max_workers)

    parsed: list[ParsedFile] = []

    if source_files:
        from dna.threadpool import get_executor
        executor = get_executor()
        if True:
            future_map = {}
            for f in source_files:
                future = executor.submit(_safe_parse, f.path, f.language)
                future_map[future] = f.relative_path

            for future in as_completed(future_map):
                rel_path = future_map[future]
                try:
                    result = future.result()
                    if result:
                        result.relative_path = rel_path
                        parsed.append(result)
                except ParserError as e:
                    logger.error("Failed to parse %s: %s", rel_path, str(e))

    logger.info("Successfully parsed %d files", len(parsed))
    parsed.sort(key=lambda p: p.relative_path or "")
    return parsed

def _safe_parse(path: str, language: str) -> ParsedFile | None:
    try:
        return parse_file(path, language)
    except ParserError:
        return None
