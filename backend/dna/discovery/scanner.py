import os
import logging
from dna.models import FileInfo
from dna.discovery.languages import detect_language, is_source_file
from dna.discovery.ignore import IgnoreFilter

logger = logging.getLogger("dna.discovery")


def scan_files(
    path: str,
    ignore_patterns: list[str] | None = None,
) -> list[FileInfo]:
    if not os.path.isdir(path):
        return []

    from dna.config import get_config
    config = get_config()

    all_patterns = list(config.always_ignore)
    if ignore_patterns:
        all_patterns.extend(ignore_patterns)

    # Compile ignore patterns ONCE for this walk; the same compiled matcher
    # is reused for every directory and file rather than recompiling per call.
    ignore_filter = IgnoreFilter(all_patterns)

    results: list[FileInfo] = []
    root = os.path.normpath(path)

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace("\\", "/")
        if rel_dir == ".":
            rel_dir = ""

        # Prune ignored directories
        if ignore_filter._compiled:
            pruned_dirnames = []
            for d in dirnames:
                d_rel = f"{rel_dir}/{d}" if rel_dir else d
                if not ignore_filter.should_ignore(d_rel + "/"):
                    pruned_dirnames.append(d)
            dirnames[:] = pruned_dirnames

        for filename in filenames:
            rel_path = f"{rel_dir}/{filename}" if rel_dir else filename
            if ignore_filter._compiled and ignore_filter.should_ignore(rel_path):
                continue

            full_path = os.path.join(dirpath, filename)

            try:
                stat = os.stat(full_path)
                size = stat.st_size
            except OSError:
                continue

            if size > config.max_file_size_bytes:
                logger.warning("Skipping file %s: size %d bytes exceeds limit", rel_path, size)
                continue

            _, ext = os.path.splitext(filename)
            # Skip ignored binary/archive extensions
            if ext.lower() in config.ignore_extensions:
                continue
            # Only index supported source extensions
            if ext.lower() not in config.supported_extensions:
                continue
            language = detect_language(ext)

            results.append(FileInfo(
                path=full_path,
                relative_path=rel_path,
                filename=filename,
                extension=ext,
                language=language,
                size_bytes=size,
                is_directory=False,
                is_source=is_source_file(ext),
            ))

    return results
