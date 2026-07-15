import os
import re
from functools import lru_cache


def parse_gitignore(path: str) -> list[str]:
    gitignore_path = os.path.join(path, ".gitignore")
    return _parse_ignore_file(gitignore_path)


def parse_dnaignore(path: str) -> list[str]:
    dnaignore_path = os.path.join(path, ".dnaignore")
    return _parse_ignore_file(dnaignore_path)


def _parse_ignore_file(filepath: str) -> list[str]:
    if not os.path.isfile(filepath):
        return []

    patterns: list[str] = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                patterns.append(line)
    except OSError:
        return []

    return patterns


def translate_pattern(pattern: str) -> tuple[re.Pattern, bool, bool]:
    is_negated = False
    if pattern.startswith("!"):
        is_negated = True
        pattern = pattern[1:]

    is_dir_only = False
    if pattern.endswith("/"):
        is_dir_only = True
        pattern = pattern[:-1]

    is_root_relative = False
    if pattern.startswith("/"):
        is_root_relative = True
        pattern = pattern[1:]
    elif "/" in pattern:
        is_root_relative = True

    regex_parts = []
    i = 0
    n = len(pattern)

    while i < n:
        char = pattern[i]
        if char == "*":
            if i + 1 < n and pattern[i+1] == "*":
                if i + 2 < n and pattern[i+2] == "/":
                    regex_parts.append("(?:.*/)?")
                    i += 3
                else:
                    regex_parts.append(".*")
                    i += 2
            else:
                regex_parts.append("[^/]*")
                i += 1
        elif char == "?":
            regex_parts.append("[^/]")
            i += 1
        elif char == "/":
            regex_parts.append("/")
            i += 1
        elif char in r".+^$()|[]{}":
            regex_parts.append("\\" + char)
            i += 1
        else:
            regex_parts.append(char)
            i += 1

    regex_str = "".join(regex_parts)

    if is_root_relative:
        regex_str = "^" + regex_str + "(?:/|$)"
    else:
        regex_str = "(?:^|/)" + regex_str + "(?:/|$)"

    return re.compile(regex_str), is_negated, is_dir_only


@lru_cache(maxsize=256)
def _compile_patterns(patterns_key: tuple[str, ...]) -> tuple[tuple[re.Pattern, bool, bool], ...]:
    """Compile a frozen set of ignore patterns once and cache the result.

    The cache is keyed on the sorted unique tuple of pattern strings so that
    repeated calls with the same pattern list reuse compiled regexes instead
    of recompiling on every should_ignore() invocation.
    """
    compiled = []
    seen = set()
    for pattern in patterns_key:
        pattern = pattern.strip()
        if not pattern or pattern.startswith("#"):
            continue
        if pattern in seen:
            continue
        seen.add(pattern)
        compiled.append(translate_pattern(pattern))
    return tuple(compiled)


class IgnoreFilter:
    """Stateful ignore matcher that compiles patterns exactly once.

    Construct once for a set of patterns and call .should_ignore(path) many
    times. This avoids recompiling regexes on every file/dir check.
    """

    __slots__ = ("_compiled",)

    def __init__(self, patterns: list[str] | None = None):
        if not patterns:
            self._compiled: tuple[tuple[re.Pattern, bool, bool], ...] = ()
        else:
            key = tuple(patterns)
            self._compiled = _compile_patterns(key)

    def should_ignore(self, file_path: str) -> bool:
        if not self._compiled:
            return False

        file_path = file_path.replace("\\", "/")
        is_dir = file_path.endswith("/")
        clean_path = file_path.strip("/")

        parts = clean_path.split("/")
        for i in range(1, len(parts)):
            ancestor = "/".join(parts[:i])
            if self._is_path_ignored(ancestor, is_d=True):
                return True

        return self._is_path_ignored(clean_path, is_d=is_dir)

    def _is_path_ignored(self, p: str, is_d: bool) -> bool:
        ignored = False
        for regex, is_negated, is_dir_only in self._compiled:
            if is_dir_only and not is_d:
                continue
            if regex.search(p):
                ignored = not is_negated
        return ignored


def should_ignore(file_path: str, patterns: list[str]) -> bool:
    """Backward-compatible entry point.

    Compiles patterns once (cached) and matches. Repeated calls with the same
    pattern list reuse the cached compiled regexes instead of recompiling.
    """
    if not patterns:
        return False
    compiled = _compile_patterns(tuple(patterns))

    file_path = file_path.replace("\\", "/")
    is_dir = file_path.endswith("/")
    clean_path = file_path.strip("/")

    def is_path_ignored(p: str, is_d: bool) -> bool:
        ignored = False
        for regex, is_negated, is_dir_only in compiled:
            if is_dir_only and not is_d:
                continue
            if regex.search(p):
                ignored = not is_negated
        return ignored

    parts = clean_path.split("/")
    for i in range(1, len(parts)):
        ancestor = "/".join(parts[:i])
        if is_path_ignored(ancestor, is_d=True):
            return True

    return is_path_ignored(clean_path, is_d=is_dir)
