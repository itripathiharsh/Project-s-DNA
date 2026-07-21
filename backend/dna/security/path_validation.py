import os
import re
import logging

logger = logging.getLogger("dna.security")

# Branch name must only contain alphanumeric chars, dots, dashes, underscores, slashes (for remote refs)
# No path traversal sequences allowed
VALID_BRANCH_RE = re.compile(r"^[a-zA-Z0-9_.\-/]+$")

# Reject any filename containing path traversal characters
VALID_FILENAME_RE = re.compile(r"^[^\\/:*?\"<>|\x00-\x1f]+$")

def canonicalize_path(path: str) -> str:
    return os.path.realpath(os.path.normpath(path))

def is_path_within_base(target_path: str, base_path: str) -> bool:
    """Check if target_path is within base_path, after canonicalization."""
    try:
        target = canonicalize_path(target_path)
        base = canonicalize_path(base_path)
        return target.startswith(base + os.sep) or target == base
    except (OSError, ValueError):
        return False

def safe_validate_path(path: str, base_path: str = None) -> str:
    """Validate and canonicalize a path. Raises ValueError if path is outside base_path."""
    if not path or not isinstance(path, str):
        raise ValueError("Path must be a non-empty string")
    if "\x00" in path:
        raise ValueError("Path contains null byte")
    canon = canonicalize_path(path)
    if base_path:
        if not is_path_within_base(canon, base_path):
            logger.warning("Path traversal blocked: %s is outside %s", path, base_path)
            raise ValueError(f"Path traversal detected: {path} is outside allowed directory")
    return canon

def validate_branch_name(name: str) -> str:
    """Validate a git branch name for path traversal and injection."""
    if not name or not isinstance(name, str):
        raise ValueError("Branch name must be a non-empty string")
    if ".." in name:
        raise ValueError(f"Invalid branch name (contains '..'): {name}")
    if name.startswith("/") or name.startswith("-"):
        raise ValueError(f"Invalid branch name (starts with / or -): {name}")
    if not VALID_BRANCH_RE.match(name):
        raise ValueError(f"Invalid branch name contains special characters: {name}")
    return name

def validate_filename(filename: str) -> str:
    """Validate a filename for path traversal."""
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty string")
    # Normalize and check for traversal
    norm = os.path.normpath(filename)
    if norm.startswith("..") or ".." in norm.split(os.sep):
        raise ValueError(f"Path traversal detected in filename: {filename}")
    if os.path.isabs(norm):
        raise ValueError(f"Absolute path not allowed in filename: {filename}")
    return norm

def sanitize_repo_dir_name(name: str) -> str:
    """Sanitize a directory name derived from repository info to prevent traversal."""
    safe = re.sub(r'[^a-zA-Z0-9_.\-]', '_', name)
    safe = safe.strip('._-')
    return safe or "unnamed_repo"
