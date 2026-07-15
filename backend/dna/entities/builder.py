from dna.models import (
    NormalizedFile, SymbolIndex, DependencyGraph,
    EntityGraph, Entity, EntityRelation,
)


def build_entity_graph(
    normalized_files: list[NormalizedFile],
    symbol_index: SymbolIndex,
    dependency_graph: DependencyGraph | None = None,
) -> EntityGraph:
    graph = EntityGraph()

    for nf in normalized_files:
        _add_file_entity(graph, nf)
        _add_symbol_entities(graph, nf)
        _add_import_relations(graph, nf)

    _add_symbol_reference_relations(graph, symbol_index, normalized_files)
    _add_extends_relations(graph, symbol_index, normalized_files)
    _add_calls_relations(graph, symbol_index, normalized_files)

    if dependency_graph:
        for edge in dependency_graph.edges:
            source_file = _file_uid(edge.source)
            target_file = _file_uid(edge.target)
            source_e = graph.get_entity(source_file)
            target_e = graph.get_entity(target_file)
            if source_e and target_e:
                graph.add_relation(EntityRelation(
                    source_uid=source_file,
                    target_uid=target_file,
                    kind="IMPORTS",
                ))

    return graph


def _file_uid(rel_path: str) -> str:
    return f"file:{rel_path}"


def _func_uid(rel_path: str, name: str) -> str:
    return f"function:{rel_path}:{name}"


def _class_uid(rel_path: str, name: str) -> str:
    return f"class:{rel_path}:{name}"


def _add_file_entity(graph: EntityGraph, nf: NormalizedFile):
    graph.add_entity(Entity(
        uid=_file_uid(nf.relative_path),
        name=nf.relative_path.split("/")[-1],
        kind="file",
        file_path=nf.relative_path,
        properties={"language": nf.language},
    ))


def _add_symbol_entities(graph: EntityGraph, nf: NormalizedFile):
    for func in nf.symbols.functions:
        uid = _func_uid(nf.relative_path, func.name)
        graph.add_entity(Entity(
            uid=uid,
            name=func.name,
            kind="function",
            file_path=nf.relative_path,
            line=func.start_line,
            properties={
                "is_method": str(func.is_method),
                "complexity": str(getattr(func, "complexity", 1)),
            },
        ))
        graph.add_relation(EntityRelation(
            source_uid=_file_uid(nf.relative_path),
            target_uid=uid,
            kind="CONTAINS",
        ))

    for cls in nf.symbols.classes:
        uid = _class_uid(nf.relative_path, cls.name)
        graph.add_entity(Entity(
            uid=uid,
            name=cls.name,
            kind="class",
            file_path=nf.relative_path,
            line=cls.start_line,
            properties={"bases": ",".join(cls.base_classes)},
        ))
        graph.add_relation(EntityRelation(
            source_uid=_file_uid(nf.relative_path),
            target_uid=uid,
            kind="CONTAINS",
        ))

        for method in cls.methods:
            method_uid = _func_uid(nf.relative_path, f"{cls.name}.{method.name}")
            graph.add_entity(Entity(
                uid=method_uid,
                name=method.name,
                kind="function",
                file_path=nf.relative_path,
                line=method.start_line,
                properties={
                    "is_method": "true",
                    "class_name": cls.name,
                    "complexity": str(getattr(method, "complexity", 1)),
                },
            ))
            graph.add_relation(EntityRelation(
                source_uid=uid,
                target_uid=method_uid,
                kind="CONTAINS",
            ))


def _add_import_relations(graph: EntityGraph, nf: NormalizedFile):
    for imp in nf.symbols.imports:
        source_file = _file_uid(nf.relative_path)
        for name in imp.names:
            import_uid = f"import:{nf.relative_path}:{name}"
            graph.add_entity(Entity(
                uid=import_uid,
                name=name,
                kind="import",
                file_path=nf.relative_path,
                properties={"source": imp.source},
            ))
            graph.add_relation(EntityRelation(
                source_uid=source_file,
                target_uid=import_uid,
                kind="CONTAINS",
            ))


def _add_symbol_reference_relations(
    graph: EntityGraph,
    symbol_index: SymbolIndex,
    normalized_files: list[NormalizedFile],
):
    file_paths = {nf.relative_path for nf in normalized_files}

    for symbol_name, occurrences in symbol_index.symbols.items():
        defs = [o for o in occurrences if o.role == "definition"]
        refs = [o for o in occurrences if o.role == "reference"]

        for ref in refs:
            if ref.file_path not in file_paths:
                continue
            for d in defs:
                if d.file_path != ref.file_path:
                    source_uid = _file_uid(ref.file_path)
                    target_uid = _file_uid(d.file_path)
                    graph.add_relation(EntityRelation(
                        source_uid=source_uid,
                        target_uid=target_uid,
                        kind="DEPENDS_ON",
                    ))


def _add_extends_relations(
    graph: EntityGraph,
    symbol_index: SymbolIndex,
    normalized_files: list[NormalizedFile],
):
    for nf in normalized_files:
        for cls in nf.symbols.classes:
            source_uid = _class_uid(nf.relative_path, cls.name)
            for base_name in (cls.base_classes if cls.base_classes else getattr(cls, "bases", [])):
                defs = symbol_index.get_definitions(base_name)
                class_defs = [d for d in defs if d.kind == "class"]
                if not class_defs:
                    class_defs = defs
                
                for d in class_defs:
                    target_uid = _class_uid(d.file_path, base_name)
                    if graph.get_entity(target_uid):
                        graph.add_relation(EntityRelation(
                            source_uid=source_uid,
                            target_uid=target_uid,
                            kind="EXTENDS",
                        ))


def _add_calls_relations(
    graph: EntityGraph,
    symbol_index: SymbolIndex,
    normalized_files: list[NormalizedFile],
):
    for nf in normalized_files:
        all_funcs = []
        for func in nf.symbols.functions:
            if not func.is_method:
                uid = _func_uid(nf.relative_path, func.name)
                all_funcs.append((uid, func))
        
        for cls in nf.symbols.classes:
            for method in cls.methods:
                uid = _func_uid(nf.relative_path, f"{cls.name}.{method.name}")
                all_funcs.append((uid, method))

        for source_uid, func in all_funcs:
            for called_name in func.calls:
                defs = symbol_index.get_definitions(called_name)
                
                if not defs:
                    for sym_name, occurrences in symbol_index.symbols.items():
                        if sym_name.endswith("." + called_name):
                            defs.extend([o for o in occurrences if o.role == "definition"])

                callable_defs = [d for d in defs if d.kind in ("function", "method")]
                if not callable_defs:
                    callable_defs = defs

                for d in callable_defs:
                    target_uid = _func_uid(d.file_path, d.symbol_name)
                    if graph.get_entity(target_uid):
                        graph.add_relation(EntityRelation(
                            source_uid=source_uid,
                            target_uid=target_uid,
                            kind="CALLS",
                        ))

