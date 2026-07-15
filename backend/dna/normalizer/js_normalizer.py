from dna.models import CanonicalNode, SymbolTable, FunctionDef, ClassDef, ImportEntry, ExportEntry


def normalize_javascript(root_node, source_bytes: bytes) -> CanonicalNode:
    source = source_bytes.decode("utf-8", errors="replace")
    symbols = SymbolTable()

    module = CanonicalNode(kind="module", name="<module>")
    module.start_line = root_node.start_point[0] + 1
    module.end_line = root_node.end_point[0] + 1

    for child in root_node.children:
        node = _normalize_js_node(child, source, symbols)
        if node is not None:
            module.children.append(node)

    return module


def _normalize_js_node(node, source: str, symbols: SymbolTable) -> CanonicalNode | None:
    if node.type == "function_declaration":
        name = _get_text(_find_child(node, "identifier"), source)
        params_node = _find_child(node, "formal_parameters")
        params = ", ".join(_collect_texts(params_node, "identifier", source)) if params_node else ""

        symbols.functions.append(FunctionDef(
            name=name or "<anon>",
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            calls=_extract_calls_from_js_node(node, source),
        ))

        cn = CanonicalNode(kind="function", name=name or "<anon>",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1,
                           metadata={"params": params})
        return cn

    elif node.type == "class_declaration":
        name = _get_text(_find_child(node, "identifier"), source)
        extends_node = _find_child(node, "extends_clause")
        bases = []
        if extends_node:
            base_ident = _find_child(extends_node, "identifier") or _find_child(extends_node, "member_expression")
            if base_ident:
                bases.append(_get_text(base_ident, source))

        cls_def = ClassDef(name=name or "<anon>",
                           base_classes=bases,
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
                    mname = _get_text(
                        _find_child(child, "property_identifier") or
                        _find_child(child, "private_property_identifier") or
                        _find_child(child, "identifier"),
                        source
                    )
                    mparams_node = _find_child(child, "formal_parameters")
                    mparams = ", ".join(_collect_texts(mparams_node, "identifier", source)) if mparams_node else ""

                    is_static = any(c.type == "static" or _get_text(c, source) == "static" for c in child.children)
                    is_getter = any(c.type == "get" or _get_text(c, source) == "get" for c in child.children)
                    is_setter = any(c.type == "set" or _get_text(c, source) == "set" for c in child.children)

                    func_def = FunctionDef(name=mname or "<anon>", is_method=True,
                                           start_line=child.start_point[0] + 1,
                                           end_line=child.end_point[0] + 1,
                                           calls=_extract_calls_from_js_node(child, source))
                    symbols.functions.append(func_def)
                    cls_def.methods.append(func_def)

                    metadata = {"params": mparams, "is_method": "true"}
                    if is_static:
                        metadata["is_static"] = "true"
                    if is_getter:
                        metadata["is_getter"] = "true"
                    if is_setter:
                        metadata["is_setter"] = "true"

                    cn.children.append(CanonicalNode(
                        kind="function", name=mname or "<anon>",
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        metadata=metadata,
                    ))
        return cn

    elif node.type == "import_statement":
        source_str = _extract_string_value(node, source)
        names = _collect_import_names(node, source)
        symbols.imports.append(ImportEntry(source=source_str, names=names, kind="import"))
        return CanonicalNode(kind="import", name=source_str,
                             start_line=node.start_point[0] + 1,
                             end_line=node.end_point[0] + 1)

    elif node.type == "export_statement":
        is_default = any(c.type == "default" or _get_text(c, source) == "default" for c in node.children)
        name = _extract_export_name(node, source)
        if not name and is_default:
            name = "default"
        export_source = _extract_string_value(node, source)
        kind = "export_default" if is_default else "export"
        if name or export_source:
            symbols.exports.append(ExportEntry(name=name, source=export_source, kind=kind))

        metadata = {}
        if is_default:
            metadata["default"] = "true"

        cn = CanonicalNode(kind="export", name=name or export_source or "",
                           start_line=node.start_point[0] + 1,
                           end_line=node.end_point[0] + 1,
                           metadata=metadata)

        for child in node.children:
            child_node = _normalize_js_node(child, source, symbols)
            if child_node is not None:
                cn.children.append(child_node)
        return cn

    elif node.type in ("lexical_declaration", "variable_declaration"):
        for child in node.children:
            if child.type == "variable_declarator":
                var_name = _get_text(_find_child(child, "identifier"), source)
                if var_name:
                    arrow = _find_child(child, "arrow_function")
                    if arrow:
                        params_node = _find_child(arrow, "formal_parameters")
                        params = ""
                        if params_node:
                            params = ", ".join(_collect_texts(params_node, "identifier", source))
                        else:
                            single_param = _find_child(arrow, "identifier")
                            if single_param:
                                params = _get_text(single_param, source)

                        symbols.functions.append(FunctionDef(
                            name=var_name,
                            start_line=child.start_point[0] + 1,
                            end_line=child.end_point[0] + 1,
                            calls=_extract_calls_from_js_node(arrow, source),
                        ))

                        cn = CanonicalNode(kind="function", name=var_name,
                                           start_line=child.start_point[0] + 1,
                                           end_line=child.end_point[0] + 1,
                                           metadata={"params": params, "arrow": "true"})
                        return cn
                    else:
                        cn = CanonicalNode(kind="variable", name=var_name,
                                           start_line=child.start_point[0] + 1,
                                           end_line=child.end_point[0] + 1)
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
        if child.type in ("function_declaration", "class_declaration"):
            return _get_text(_find_child(child, "identifier"), source) or ""
        if child.type == "variable_declaration":
            for vc in child.children:
                if vc.type == "variable_declarator":
                    return _get_text(_find_child(vc, "identifier"), source) or ""
        if child.type == "identifier":
            return _get_text(child, source) or ""
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


def _extract_calls_from_js_node(node, source: str) -> list[str]:
    calls = []
    def visit(n):
        if n.type in ("function_declaration", "class_declaration") and n != node:
            return
        if n.type == "call_expression":
            func_child = None
            for c in n.children:
                if c.type in ("identifier", "member_expression", "property_identifier", "call_expression"):
                    func_child = c
                    break
            if func_child:
                text = source[func_child.start_byte:func_child.end_byte]
                calls.append(text.split(".")[-1])
        for child in n.children:
            visit(child)
    visit(node)
    return list(set(calls))

