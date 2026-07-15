import os
from dna.models import FileInfo, IndexedFile, FileInventory, RepositoryMetadata
from dna.indexer.classifier import classify_file, build_classification_map
from dna.indexer.hasher import compute_file_hash, detect_changes


def build_file_inventory(
    files: list[FileInfo],
    repo_metadata: RepositoryMetadata,
    previous_inventory: FileInventory | None = None,
) -> FileInventory:
    indexed: list[IndexedFile] = []
    categories = build_classification_map(files, repo_metadata)

    # Compute content hashes for all files so we have consistent hash references
    # and incremental change detection can function correctly.
    need_hashes = True

    for f in files:
        cat = classify_file(f, repo_metadata)

        mtime = 0.0
        try:
            mtime = os.path.getmtime(f.path)
        except OSError:
            pass

        content_hash = compute_file_hash(f.path) if need_hashes else ""

        indexed.append(IndexedFile(
            path=f.path,
            relative_path=f.relative_path,
            filename=f.filename,
            extension=f.extension,
            language=f.language,
            size_bytes=f.size_bytes,
            is_directory=f.is_directory,
            is_source=f.is_source,
            category=cat,
            content_hash=content_hash,
            mtime=mtime,
        ))

    if previous_inventory:
        new_hashes = {f.relative_path: f.content_hash for f in indexed}
        old_map = {f.relative_path: f.content_hash for f in previous_inventory.files}
        changes = detect_changes(old_map, new_hashes)
        for f in indexed:
            if f.relative_path in changes.get("added", {}):
                f.change_type = "added"
            elif f.relative_path in changes.get("modified", {}):
                f.change_type = "modified"
            elif f.relative_path in changes.get("removed", {}):
                f.change_type = "removed"

    total_size = sum(f.size_bytes for f in indexed)

    return FileInventory(
        files=indexed,
        categories=categories,
        total_files=len(indexed),
        total_size_bytes=total_size,
    )
