from dna.models import CanonicalNode, SymbolTable, FunctionDef, ClassDef, ImportEntry, ExportEntry


def normalize_typescript(root_node, source_bytes: bytes) -> CanonicalNode:
    source = source_bytes.decode("utf-8", errors="replace")
    symbols = SymbolTable()

    module = CanonicalNode(kind="module", name="<module>")
    module.start_line = root_node.start_point[0] + 1
    module.end_line = root_node.end_point[0] + 1

    for child in root_node.children:
        node = _normalize_ts_node(child, source, symbols)
        if node is not None:
            module.children.append(node)

    return module


def _normalize_ts_node(node, source: str, symbols: SymbolTable) -> CanonicalNode | None:
    if node.type == "function_declaration":
        name = _get_text(_find_child(node, "identifier"), source)
        params_node = _find_child(node, "formal_parameters")
        params = ", ".join(_collect_texts(params_node, "identifier", source)) if params_node else ""

        symbols.functions.append(FunctionDef(
            name=name or "<anon>",
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
        ))

        cn = CanonicalNode(kind="function", name=name or "<anon>",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1,
                           metadata={"params": params})
        return cn

    elif node.type == "class_declaration":
        name = _get_text(_find_child(node, "type_identifier"), source) or _get_text(_find_child(node, "identifier"), source)
        cls_def = ClassDef(name=name or "<anon>",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1)
        symbols.classes.append(cls_def)

        cn = CanonicalNode(kind="class", name=name or "<anon>",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1)

        body = _find_child(node, "class_body")
        if body:
            for child in body.children:
                if child.type == "method_definition":
                    mname = _get_text(_find_child(child, "property_identifier"), source)
                    mparams_node = _find_child(child, "formal_parameters")
                    mparams = ", ".join(_collect_texts(mparams_node, "identifier", source)) if mparams_node else ""

                    func_def = FunctionDef(name=mname or "<anon>", is_method=True,
                                           start_line=child.start_point[0] + 1,
                                           end_line=child.end_point[0] + 1)
                    symbols.functions.append(func_def)
                    cls_def.methods.append(func_def)

                    cn.children.append(CanonicalNode(
                        kind="function", name=mname or "<anon>",
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        metadata={"params": mparams, "is_method": "true"},
                    ))
        return cn

    elif node.type == "interface_declaration":
        name = _get_text(_find_child(node, "type_identifier"), source)
        cn = CanonicalNode(kind="interface", name=name or "<anon>",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1)
        return cn

    elif node.type == "enum_declaration":
        name = _get_text(_find_child(node, "identifier"), source)
        cn = CanonicalNode(kind="enum", name=name or "<anon>",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1)
        return cn

    elif node.type == "type_alias_declaration":
        name = _get_text(_find_child(node, "type_identifier"), source)
        cn = CanonicalNode(kind="type_alias", name=name or "<anon>",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1)
        return cn

    elif node.type == "import_statement":
        source_str = _extract_string_value(node, source)
        names = _collect_import_names(node, source)
        symbols.imports.append(ImportEntry(source=source_str, names=names, kind="import"))
        return CanonicalNode(kind="import", name=source_str,
                             start_line=node.start_point[0] + 1,
                             end_line=node.end_point[0] + 1)

    elif node.type == "export_statement":
        name = _extract_export_name(node, source)
        export_source = _extract_string_value(node, source)
        if name or export_source:
            symbols.exports.append(ExportEntry(name=name, source=export_source, kind="export"))
        cn = CanonicalNode(kind="export", name=name or export_source or "",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1)
        for child in node.children:
            child_node = _normalize_ts_node(child, source, symbols)
            if child_node is not None:
                cn.children.append(child_node)
        return cn

    elif node.type == "lexical_declaration" or node.type == "variable_declaration":
        for child in node.children:
            if child.type == "variable_declarator":
                var_name = _get_text(_find_child(child, "identifier"), source)
                if var_name:
                    cn = CanonicalNode(kind="variable", name=var_name,
                                       start_line=child.start_point[0] + 1,
                                       end_line=child.end_point[0] + 1)
                    arrow = _find_child(child, "arrow_function")
                    if arrow:
                        cn.metadata["arrow"] = "true"
                    return cn
        return None

    return None


def _extract_string_value(node, source: str) -> str:
    for child in node.children:
        if child.type == "string":
            text = source[child.start_byte:child.end_byte]
            return text.strip("\"'")
    return ""


def _collect_import_names(node, source: str) -> list[str]:
    names = []
    for child in node.children:
        if child.type == "import_clause":
            for sub in child.children:
                if sub.type == "identifier":
                    names.append(source[sub.start_byte:sub.end_byte])
                elif sub.type == "namespace_import":
                    alias = _find_child(sub, "identifier")
                    if alias:
                        names.append("* as " + source[alias.start_byte:alias.end_byte])
                elif sub.type == "named_imports":
                    for spec in sub.children:
                        if spec.type == "import_specifier":
                            n = _get_text(_find_child(spec, "identifier"), source)
                            if n:
                                names.append(n)
    return names


def _extract_export_name(node, source: str) -> str:
    for child in node.children:
        if child.type in ("function_declaration", "class_declaration", "interface_declaration", "enum_declaration"):
            return _get_text(_find_child(child, "identifier"), source) or _get_text(_find_child(child, "type_identifier"), source) or ""
        if child.type == "variable_declaration":
            for vc in child.children:
                if vc.type == "variable_declarator":
                    return _get_text(_find_child(vc, "identifier"), source) or ""
    return ""


def _find_child(node, type_name: str):
    for child in node.children:
        if child.type == type_name:
            return child
    return None


def _get_text(node, source: str) -> str:
    if node is None:
        return ""
    return source[node.start_byte:node.end_byte]


def _collect_texts(node, type_name: str, source: str) -> list[str]:
    if node is None:
        return []
    return [source[c.start_byte:c.end_byte] for c in node.children if c.type == type_name]
