from dna.models import CanonicalNode, SymbolTable, FunctionDef, ClassDef, ImportEntry


def normalize_python(root_node, source_bytes: bytes) -> CanonicalNode:
    module = CanonicalNode(kind="module", name="<module>")
    source = source_bytes.decode("utf-8", errors="replace")
    symbols = SymbolTable()

    module.start_line = root_node.start_point[0] + 1
    module.end_line = root_node.end_point[0] + 1

    for child in root_node.children:
        node = _normalize_python_node(child, source, symbols, is_method=False)
        if node is not None:
            module.children.append(node)

    return module


def _normalize_python_node(node, source: str, symbols: SymbolTable, is_method: bool = False) -> CanonicalNode | None:
    if node.type == "function_definition":
        name = _get_text(_find_child(node, "identifier"), source)
        params_node = _find_child(node, "parameters")
        params = ", ".join(_collect_texts(params_node, "identifier", source)) if params_node else ""
        func_def = FunctionDef(
            name=name or "<anon>",
            params=[_get_text(c, source) for c in (params_node.children if params_node else []) if c.type in ("identifier",)],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            is_method=is_method,
        )
        symbols.functions.append(func_def)

        cn = CanonicalNode(kind="function", name=name or "<anon>",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1,
                           metadata={"params": params})

        for child in node.children:
            child_node = _normalize_python_node(child, source, symbols, is_method=False)
            if child_node is not None:
                cn.children.append(child_node)
        return cn

    elif node.type == "class_definition":
        name = _get_text(_find_child(node, "identifier"), source)
        bases_node = _find_child(node, "argument_list")
        bases = _collect_texts(bases_node, "identifier", source) if bases_node else []

        cls_def = ClassDef(name=name or "<anon>", base_classes=bases,
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1)
        symbols.classes.append(cls_def)

        cn = CanonicalNode(kind="class", name=name or "<anon>",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1,
                           metadata={"bases": ", ".join(bases)})

        for child in node.children:
            child_node = _normalize_python_node(child, source, symbols, is_method=True)
            if child_node is not None:
                cn.children.append(child_node)
                if child_node.kind == "function":
                    cls_def.methods.append(FunctionDef(
                        name=child_node.name,
                        start_line=child_node.start_line,
                        end_line=child_node.end_line,
                        is_method=True,
                    ))
                    # Register qualified method name for symbol indexing
                    symbols.functions.append(FunctionDef(
                        name=f"{cls_def.name}.{child_node.name}",
                        params=[],
                        start_line=child_node.start_line,
                        end_line=child_node.end_line,
                        is_method=True,
                    ))
            else:
                # Recurse into block children (e.g., method definitions inside a block)
                for sub in child.children:
                    sub_node = _normalize_python_node(sub, source, symbols, is_method=True)
                    if sub_node is not None:
                        cn.children.append(sub_node)
                        if sub_node.kind == "function":
                            cls_def.methods.append(FunctionDef(
                                name=sub_node.name,
                                start_line=sub_node.start_line,
                                end_line=sub_node.end_line,
                                is_method=True,
                            ))
                            # Register qualified method name for symbol indexing
                            symbols.functions.append(FunctionDef(
                                name=f"{cls_def.name}.{sub_node.name}",
                                params=[],
                                start_line=sub_node.start_line,
                                end_line=sub_node.end_line,
                                is_method=True,
                            ))
        return cn

    elif node.type == "import_statement":
        text = _get_full_text(node, source)
        names = _collect_texts(node, "dotted_name", source)
        symbols.imports.append(ImportEntry(source=text, names=names, kind="import"))
        return CanonicalNode(kind="import", name=text,
                             start_line=node.start_point[0] + 1,
                             end_line=node.end_point[0] + 1)

    elif node.type == "import_from_statement":
        module_name = _get_text(_find_child(node, "dotted_name"), source) or "."
        names = _collect_texts(node, "dotted_name", source)
        if not names:
            names = _collect_texts(node, "aliased_import", source)
        symbols.imports.append(ImportEntry(source=module_name, names=names, kind="from"))
        return CanonicalNode(kind="import", name=f"from {module_name}",
                             start_line=node.start_point[0] + 1,
                             end_line=node.end_point[0] + 1)

    elif node.type == "decorated_definition":
        for child in node.children:
            result = _normalize_python_node(child, source, symbols, is_method)
            if result is not None:
                return result


    elif node.type == "expression_statement":
        text = _get_full_text(node, source)
        return CanonicalNode(kind="expression", name=text[:40],
                             start_line=node.start_point[0] + 1,
                             end_line=node.end_point[0] + 1)

    elif node.type == "assignment":
        left = _get_text(_find_child(node, "identifier"), source) or "var"
        return CanonicalNode(kind="variable", name=left,
                             start_line=node.start_point[0] + 1,
                             end_line=node.end_point[0] + 1)
    # Recurse into unhandled nodes (e.g., block bodies) to capture nested constructs
    for child in node.children:
        _ = _normalize_python_node(child, source, symbols, is_method=is_method)
    return None


def _find_child(node, type_name: str):
    for child in node.children:
        if child.type == type_name:
            return child
    return None


def _get_text(node, source: str) -> str:
    if node is None:
        return ""
    return source[node.start_byte:node.end_byte]


def _get_full_text(node, source: str) -> str:
    return source[node.start_byte:node.end_byte]


def _collect_texts(node, type_name: str, source: str) -> list[str]:
    if node is None:
        return []
    return [_get_text(c, source) for c in node.children if c.type == type_name]
