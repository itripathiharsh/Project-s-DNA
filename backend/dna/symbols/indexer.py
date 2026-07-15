from dna.models import NormalizedFile, SymbolIndex, SymbolOccurrence


def build_symbol_index(normalized_files: list[NormalizedFile]) -> SymbolIndex:
    index = SymbolIndex()

    for nf in normalized_files:
        for func in nf.symbols.functions:
            index.add(func.name, SymbolOccurrence(
                symbol_name=func.name,
                kind="function",
                file_path=nf.relative_path,
                line=func.start_line,
                role="definition",
            ))

        for cls in nf.symbols.classes:
            index.add(cls.name, SymbolOccurrence(
                symbol_name=cls.name,
                kind="class",
                file_path=nf.relative_path,
                line=cls.start_line,
                role="definition",
            ))

            for method in cls.methods:
                full_name = f"{cls.name}.{method.name}"
                index.add(full_name, SymbolOccurrence(
                    symbol_name=full_name,
                    kind="method",
                    file_path=nf.relative_path,
                    line=method.start_line,
                    role="definition",
                ))

        for imp in nf.symbols.imports:
            for name in imp.names:
                index.add(name, SymbolOccurrence(
                    symbol_name=name,
                    kind="import",
                    file_path=nf.relative_path,
                    line=0,
                    role="reference",
                ))

            if imp.source and not imp.source.startswith("."):
                index.add(imp.source, SymbolOccurrence(
                    symbol_name=imp.source,
                    kind="module",
                    file_path=nf.relative_path,
                    line=0,
                    role="reference",
                ))

            if imp.source and imp.source.startswith("."):
                for name in imp.names:
                    resolved = _resolve_relative_import(nf.relative_path, imp.source, name)
                    if resolved:
                        index.add(resolved, SymbolOccurrence(
                            symbol_name=resolved,
                            kind="module",
                            file_path=nf.relative_path,
                            line=0,
                            role="reference",
                        ))

        for exp in nf.symbols.exports:
            index.add(exp.name, SymbolOccurrence(
                symbol_name=exp.name,
                kind="export",
                file_path=nf.relative_path,
                line=0,
                role="definition",
            ))

    return index


def _resolve_relative_import(current_file: str, source: str, name: str) -> str | None:
    import os
    base = os.path.dirname(current_file) if current_file else ""
    dots = 0
    while dots < len(source) and source[dots] == ".":
        dots += 1
    module_name = source[dots:]
    parts = base.replace("\\", "/").split("/") if base else []
    if dots > 1:
        parts = parts[:-(dots - 1)]
    if not parts and not module_name:
        return None
    if parts:
        resolved = "/".join(parts) + "/" + module_name if module_name else "/".join(parts)
    else:
        resolved = module_name
    return resolved


def query_symbol(index: SymbolIndex, name: str) -> dict:
    occurrences = index.find(name)
    return {
        "name": name,
        "definitions": [o for o in occurrences if o.role == "definition"],
        "references": [o for o in occurrences if o.role == "reference"],
        "total_count": len(occurrences),
    }
