import os
from dna.models import NormalizedFile, SymbolIndex, DependencyGraph, DependencyNode, DependencyEdge


def build_dependency_graph(
    normalized_files: list[NormalizedFile],
    symbol_index: SymbolIndex,
) -> DependencyGraph:
    graph = DependencyGraph()

    file_paths = {nf.relative_path for nf in normalized_files}

    for nf in normalized_files:
        graph.add_node(DependencyNode(
            name=nf.relative_path,
            kind="file",
            file_path=nf.relative_path,
        ))

        for imp in nf.symbols.imports:
            resolved = _resolve_import_target(imp.source, nf.relative_path, file_paths)
            if resolved:
                is_external = resolved not in file_paths
                if is_external:
                    graph.add_node(DependencyNode(
                        name=resolved,
                        kind="external",
                        file_path="",
                    ))
                graph.add_edge(DependencyEdge(
                    source=nf.relative_path,
                    target=resolved,
                    kind="import",
                ))

            for name in imp.names:
                defs = symbol_index.get_definitions(name)
                for d in defs:
                    if d.file_path and d.file_path != nf.relative_path:
                        graph.add_edge(DependencyEdge(
                            source=nf.relative_path,
                            target=d.file_path,
                            kind="symbol_ref",
                        ))

        for exp in nf.symbols.exports:
            if exp.source:
                resolved = _resolve_import_target(exp.source, nf.relative_path, file_paths)
                if resolved:
                    is_external = resolved not in file_paths
                    if is_external:
                        graph.add_node(DependencyNode(
                            name=resolved,
                            kind="external",
                            file_path="",
                        ))
                    graph.add_edge(DependencyEdge(
                        source=nf.relative_path,
                        target=resolved,
                        kind="export",
                    ))

    return graph


def _resolve_import_target(source: str, current_file: str, all_files: set[str]) -> str | None:
    if not source:
        return None

    if source.startswith("."):
        base = os.path.dirname(current_file) if current_file else ""
        dots = 0
        while dots < len(source) and source[dots] == ".":
            dots += 1
        module = source[dots:].lstrip("/")
        parts = base.replace("\\", "/").split("/") if base else []
        if dots > 1:
            parts = parts[:-(dots - 1)]
        if parts:
            resolved_base = "/".join(parts)
        else:
            resolved_base = ""
        resolved = f"{resolved_base}/{module}" if resolved_base else module

        candidates = [
            resolved,
            resolved + ".py",
            resolved + ".js",
            resolved + ".ts",
            resolved + "/__init__.py",
            resolved + "/index.js",
            resolved + "/index.ts",
        ]
        for c in candidates:
            if c in all_files:
                return c
        return None

    # Absolute import handling
    PYTHON_STDLIB = {
        "os", "sys", "json", "math", "re", "collections", "itertools", "functools",
        "time", "datetime", "subprocess", "urllib", "hashlib", "socket", "threading",
        "logging", "pathlib", "tempfile", "shutil", "unittest", "abc", "inspect",
        "enum", "typing", "dataclasses", "uuid", "ctypes", "csv", "sqlite3", "xml",
        "html", "http", "email", "ftplib", "smtplib", "poplib", "imaplib",
        "asyncio", "contextlib", "copy", "traceback", "warnings", "weakref", "pickle",
        "fnmatch", "glob", "getopt", "argparse", "platform", "signal", "stat", "sysconfig"
    }
    JS_STDLIB = {
        "fs", "path", "http", "https", "os", "crypto", "events", "util", "stream",
        "child_process", "cluster", "dns", "net", "readline", "repl", "tls", "url",
        "v8", "vm", "zlib", "punycode", "querystring", "string_decoder", "tty"
    }

    source_normalized = source.replace("\\", "/")
    first_part = source_normalized.split("/")[0].split(".")[0]

    if first_part in PYTHON_STDLIB or first_part in JS_STDLIB:
        return first_part

    # 1. Node.js node_modules resolution
    current_dir = os.path.dirname(current_file) if current_file else ""
    parts = current_dir.replace("\\", "/").split("/") if current_dir else []
    for i in range(len(parts) + 1):
        ancestor = "/".join(parts[:-i]) if i > 0 and parts[:-i] else ("/".join(parts) if i == 0 else "")
        prefix = f"{ancestor}/" if ancestor else ""
        candidate_base = f"{prefix}node_modules/{source_normalized}"
        candidates = [
            candidate_base,
            candidate_base + ".js",
            candidate_base + ".ts",
            candidate_base + "/index.js",
            candidate_base + "/index.ts",
        ]
        for c in candidates:
            if c in all_files:
                return c

    # 2. Try resolving as project-root-relative or source-root-relative absolute import
    resolved_path = source_normalized.replace(".", "/")
    
    # Determine search roots dynamically from all_files
    search_dirs = {""}
    for f in all_files:
        parts = f.replace("\\", "/").split("/")
        for i in range(1, len(parts)):
            search_dirs.add("/".join(parts[:i]))

    for search_dir in sorted(search_dirs, key=len, reverse=True):
        prefix = f"{search_dir}/" if search_dir else ""
        candidate_base = f"{prefix}{resolved_path}"
        candidates = [
            candidate_base,
            candidate_base + ".py",
            candidate_base + ".js",
            candidate_base + ".ts",
            candidate_base + "/__init__.py",
            candidate_base + "/index.js",
            candidate_base + "/index.ts",
        ]
        for c in candidates:
            if c in all_files:
                return c

    # Fall back to returning the top-level external package name
    return first_part


def analyze_dependencies(graph: DependencyGraph) -> dict:
    high_fan_in = sorted(
        [(n.name, len(graph.get_dependents(n.name))) for n in graph.nodes],
        key=lambda x: -x[1],
    )[:10]

    high_fan_out = sorted(
        [(n.name, len(graph.get_dependencies(n.name))) for n in graph.nodes],
        key=lambda x: -x[1],
    )[:10]

    cycles = graph.detect_cycles()

    return {
        "total_nodes": len(graph.nodes),
        "total_edges": len(graph.edges),
        "high_fan_in": high_fan_in,
        "high_fan_out": high_fan_out,
        "cycle_count": len(cycles),
        "cycles": cycles,
    }
