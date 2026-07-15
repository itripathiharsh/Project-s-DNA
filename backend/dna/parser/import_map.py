import os
from dna.models import ParsedFile, ImportEntry


def build_import_map(parsed_files: list[ParsedFile]) -> dict[str, list[ImportEntry]]:
    result: dict[str, list[ImportEntry]] = {}
    for pf in parsed_files:
        if pf.relative_path and pf.symbols.imports:
            result[pf.relative_path] = pf.symbols.imports
    return result


def resolve_imports(
    file_path: str,
    imports: list[ImportEntry],
    all_files: list[str],
) -> list[str]:
    resolved: list[str] = []
    base_dir = os.path.dirname(file_path)

    for imp in imports:
        source = imp.source
        if not source:
            continue

        target = _resolve_single(source, base_dir)
        if target:
            resolved.append(target)

    result = []
    for r in resolved:
        if r in all_files:
            result.append(r)
        elif r + ".py" in all_files:
            result.append(r + ".py")
        elif r + "/__init__.py" in all_files:
            result.append(r + "/__init__.py")
    return result


def _resolve_single(source: str, base_dir: str) -> str | None:
    if source.startswith("."):
        dots = 0
        while dots < len(source) and source[dots] == ".":
            dots += 1
        module_name = source[dots:]
        parts = base_dir.replace("\\", "/").split("/")
        if dots > 1:
            parts = parts[:-(dots - 1)]
        if parts:
            rel = "/".join(parts) + "/" + module_name if module_name else "/".join(parts)
            result = os.path.normpath(rel).replace("\\", "/")
            return result + ".py" if module_name else result
        return None

    return None
