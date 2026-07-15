import hashlib
from dna.models import FileInfo


_HASH_BLOCK_SIZE = 65536


def compute_file_hash(path: str) -> str:
    h = hashlib.blake2b(digest_size=16)
    try:
        with open(path, "rb") as f:
            while True:
                block = f.read(_HASH_BLOCK_SIZE)
                if not block:
                    break
                h.update(block)
    except OSError:
        return ""
    return h.hexdigest()


def compute_file_hashes(files: list[FileInfo]) -> dict[str, str]:
    result: dict[str, str] = {}
    for f in files:
        result[f.relative_path] = compute_file_hash(f.path)
    return result


def detect_changes(
    old_hashes: dict[str, str],
    new_hashes: dict[str, str],
) -> dict[str, dict[str, str]]:
    old_paths = set(old_hashes)
    new_paths = set(new_hashes)

    added = {p: new_hashes[p] for p in new_paths - old_paths}
    removed = {p: old_hashes[p] for p in old_paths - new_paths}
    modified = {}
    unchanged = {}

    for p in new_paths & old_paths:
        if new_hashes[p] != old_hashes[p]:
            modified[p] = new_hashes[p]
        else:
            unchanged[p] = new_hashes[p]

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }
