from dna.models import SymbolTable, FunctionDef, ClassDef, ImportEntry, ExportEntry
from dna.parser.complexity import calculate_complexity


def extract_symbols(root_node, source_bytes: bytes, language: str) -> SymbolTable:
    if language == "Python":
        return _extract_python(root_node, source_bytes)
    elif language == "JavaScript":
        return _extract_js(root_node, source_bytes)
    elif language == "TypeScript":
        return _extract_ts(root_node, source_bytes)
    elif language == "Go":
        return _extract_go(root_node, source_bytes)
    elif language == "Rust":
        return _extract_rust(root_node, source_bytes)
    return SymbolTable()


def _node_text(node, source: bytes) -> str:
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _extract_python(root, source: bytes) -> SymbolTable:
    functions: list[FunctionDef] = []
    classes: list[ClassDef] = []
    imports: list[ImportEntry] = []
    exports: list[ExportEntry] = []
    _class_stack: list[ClassDef] = []

    def visit(node):
        if node.type == "function_definition":
            name = _get_child_text_by_type(node, "identifier", source) or "<anon>"
            params_node = _find_child(node, "parameters")
            params = _extract_python_params(params_node, source) if params_node else []
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            is_method = bool(_class_stack)
            complexity = calculate_complexity(node, "Python")
            calls = _extract_calls(node, source, "Python")
            func = FunctionDef(name=name, params=params, start_line=start, end_line=end, is_method=is_method, complexity=complexity, calls=calls)
            if _class_stack:
                _class_stack[-1].methods.append(func)
            functions.append(func)

        elif node.type == "class_definition":
            name = _get_child_text_by_type(node, "identifier", source) or "<anon>"
            bases = _extract_python_bases(node, source)
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            cls = ClassDef(name=name, base_classes=bases, start_line=start, end_line=end)
            _class_stack.append(cls)
            for child in node.children:
                visit(child)
            _class_stack.pop()
            classes.append(cls)
            return

        elif node.type == "import_statement":
            text = _node_text(node, source)
            names = _extract_python_imported_names(node, source)
            imports.append(ImportEntry(source=text, names=names, kind="import"))

        elif node.type == "import_from_statement":
            module = _get_child_text_by_type(node, "dotted_name", source)
            if not module:
                module = _get_child_text_by_type(node, "relative_import", source) or ""
            names = _extract_python_imported_names(node, source)
            imports.append(ImportEntry(source=module, names=names, kind="from"))

        elif node.type == "decorated_definition":
            for child in node.children:
                visit(child)
            return

        for child in node.children:
            visit(child)

    visit(root)
    return SymbolTable(functions=functions, classes=classes, imports=imports, exports=exports)


def _extract_python_params(params_node, source: bytes) -> list[str]:
    params = []
    for child in params_node.children:
        if child.type == "identifier":
            params.append(_node_text(child, source))
        elif child.type == "typed_parameter":
            id_child = _find_child(child, "identifier")
            if id_child:
                params.append(_node_text(id_child, source))
        elif child.type in ("default_parameter", "list_splat_pattern", "dictionary_splat_pattern"):
            id_child = _find_child(child, "identifier")
            if id_child:
                params.append(_node_text(id_child, source))
    return params


def _extract_python_bases(node, source: bytes) -> list[str]:
    arg_list = _find_child(node, "argument_list")
    if not arg_list:
        return []
    bases = []
    for child in arg_list.children:
        if child.type in ("identifier", "attribute", "subscript"):
            bases.append(_node_text(child, source))
    return bases


def _extract_python_imported_names(node, source: bytes) -> list[str]:
    names = []
    for child in node.children:
        if child.type == "dotted_name":
            names.append(_node_text(child, source))
        elif child.type == "aliased_import":
            name_child = _find_child(child, "dotted_name")
            if name_child:
                names.append(_node_text(name_child, source))
    return names


def _extract_js(root, source: bytes) -> SymbolTable:
    functions: list[FunctionDef] = []
    classes: list[ClassDef] = []
    imports: list[ImportEntry] = []
    exports: list[ExportEntry] = []

    def visit(node):
        if node.type == "function_declaration":
            name = _get_child_text_by_type(node, "identifier", source) or "<anon>"
            params = _extract_js_params(node, source)
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            complexity = calculate_complexity(node, "JavaScript")
            functions.append(FunctionDef(name=name, params=params, start_line=start, end_line=end, complexity=complexity, calls=_extract_calls(node, source, "JavaScript")))

        elif node.type == "class_declaration":
            name = _get_child_text_by_type(node, "identifier", source) or "<anon>"
            extends_node = _find_child(node, "extends_clause")
            bases = []
            if extends_node:
                base_ident = _find_child(extends_node, "identifier") or _find_child(extends_node, "member_expression")
                if base_ident:
                    bases.append(_node_text(base_ident, source))
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            cls = ClassDef(name=name, base_classes=bases, start_line=start, end_line=end)
            body = _find_child(node, "class_body")
            if body:
                for child in body.children:
                    if child.type == "method_definition":
                        mname = _get_child_text_by_type(child, "property_identifier", source) or "<anon>"
                        mparams = _extract_js_params(child, source)
                        mstart = child.start_point[0] + 1
                        mend = child.end_point[0] + 1
                        mcomplexity = calculate_complexity(child, "JavaScript")
                        mfunc = FunctionDef(name=mname, params=mparams, start_line=mstart, end_line=mend, is_method=True, complexity=mcomplexity, calls=_extract_calls(child, source, "JavaScript"))
                        cls.methods.append(mfunc)
                        functions.append(mfunc)
            classes.append(cls)

        elif node.type == "import_statement":
            source_str = _extract_js_import_source(node, source)
            names = _extract_js_imported_names(node, source)
            imports.append(ImportEntry(source=source_str, names=names, kind="import"))

        elif node.type == "export_statement":
            name = _extract_js_export_name(node, source)
            export_source = _extract_js_import_source(node, source)
            if name or export_source:
                exports.append(ExportEntry(name=name, source=export_source, kind="export"))
            for child in node.children:
                visit(child)
            return

        elif node.type == "lexical_declaration" or node.type == "variable_declaration":
            for child in node.children:
                if child.type == "variable_declarator":
                    name_node = _find_child(child, "identifier")
                    value = _find_child(child, "arrow_function") or _find_child(child, "function")
                    if name_node and value:
                        name = _node_text(name_node, source)
                        params = _extract_js_params(value, source)
                        start = value.start_point[0] + 1
                        end = value.end_point[0] + 1
                        functions.append(FunctionDef(name=name, params=params, start_line=start, end_line=end, calls=_extract_calls(value, source, "JavaScript")))

        for child in node.children:
            visit(child)

    visit(root)
    return SymbolTable(functions=functions, classes=classes, imports=imports, exports=exports)


def _extract_ts(root, source: bytes) -> SymbolTable:
    functions: list[FunctionDef] = []
    classes: list[ClassDef] = []
    imports: list[ImportEntry] = []
    exports: list[ExportEntry] = []

    def visit(node):
        if node.type == "function_declaration":
            name = _get_child_text_by_type(node, "identifier", source) or "<anon>"
            params = _extract_js_params(node, source)
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            complexity = calculate_complexity(node, "TypeScript")
            functions.append(FunctionDef(name=name, params=params, start_line=start, end_line=end, complexity=complexity, calls=_extract_calls(node, source, "TypeScript")))

        elif node.type == "class_declaration":
            name = _get_child_text_by_type(node, "type_identifier", source) or _get_child_text_by_type(node, "identifier", source) or "<anon>"
            extends_node = _find_child(node, "extends_clause")
            bases = []
            if extends_node:
                base_ident = _find_child(extends_node, "type_identifier") or _find_child(extends_node, "identifier") or _find_child(extends_node, "member_expression")
                if base_ident:
                    bases.append(_node_text(base_ident, source))
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            cls = ClassDef(name=name, base_classes=bases, start_line=start, end_line=end)
            body = _find_child(node, "class_body")
            if body:
                for child in body.children:
                    if child.type == "method_definition":
                        mname = _get_child_text_by_type(child, "property_identifier", source) or "<anon>"
                        mparams = _extract_js_params(child, source)
                        mstart = child.start_point[0] + 1
                        mend = child.end_point[0] + 1
                        mcomplexity = calculate_complexity(child, "TypeScript")
                        mfunc = FunctionDef(name=mname, params=mparams, start_line=mstart, end_line=mend, is_method=True, complexity=mcomplexity, calls=_extract_calls(child, source, "TypeScript"))
                        cls.methods.append(mfunc)
                        functions.append(mfunc)
            classes.append(cls)

        elif node.type == "interface_declaration":
            name = _get_child_text_by_type(node, "type_identifier", source) or "<anon>"
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            classes.append(ClassDef(name=name, start_line=start, end_line=end))

        elif node.type == "enum_declaration":
            name = _get_child_text_by_type(node, "identifier", source) or "<anon>"
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            classes.append(ClassDef(name=name, start_line=start, end_line=end))

        elif node.type == "type_alias_declaration":
            name = _get_child_text_by_type(node, "type_identifier", source) or "<anon>"
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            classes.append(ClassDef(name=name, start_line=start, end_line=end))

        elif node.type == "import_statement":
            source_str = _extract_js_import_source(node, source)
            names = _extract_js_imported_names(node, source)
            imports.append(ImportEntry(source=source_str, names=names, kind="import"))

        elif node.type == "export_statement":
            name = _extract_ts_export_name(node, source)
            export_source = _extract_js_import_source(node, source)
            if name or export_source:
                exports.append(ExportEntry(name=name, source=export_source, kind="export"))
            for child in node.children:
                visit(child)
            return

        elif node.type == "lexical_declaration" or node.type == "variable_declaration":
            for child in node.children:
                if child.type == "variable_declarator":
                    name_node = _find_child(child, "identifier")
                    value = _find_child(child, "arrow_function") or _find_child(child, "function")
                    if name_node and value:
                        name = _node_text(name_node, source)
                        params = _extract_js_params(value, source)
                        start = value.start_point[0] + 1
                        end = value.end_point[0] + 1
                        functions.append(FunctionDef(name=name, params=params, start_line=start, end_line=end))

        for child in node.children:
            visit(child)

    visit(root)
    return SymbolTable(functions=functions, classes=classes, imports=imports, exports=exports)


def _extract_js_params(node, source: bytes) -> list[str]:
    params_node = _find_child(node, "formal_parameters") or _find_child(node, "parameters")
    if not params_node:
        return []
    params = []
    for child in params_node.children:
        if child.type in ("identifier", "property_identifier"):
            params.append(_node_text(child, source))
        elif child.type == "required_parameter":
            id_child = _find_child(child, "identifier")
            if id_child:
                params.append(_node_text(id_child, source))
    return params


def _extract_js_import_source(node, source: bytes) -> str:
    for child in node.children:
        if child.type == "string":
            text = _node_text(child, source)
            return text.strip("\"'")
    return ""


def _extract_js_imported_names(node, source: bytes) -> list[str]:
    names = []
    for child in node.children:
        if child.type == "import_clause":
            for sub in child.children:
                if sub.type == "identifier":
                    names.append(_node_text(sub, source))
                elif sub.type == "namespace_import":
                    alias = _find_child(sub, "identifier")
                    if alias:
                        names.append("* as " + _node_text(alias, source))
                elif sub.type == "named_imports":
                    for spec in sub.children:
                        if spec.type == "import_specifier":
                            n = _get_child_text_by_type(spec, "identifier", source)
                            if n:
                                names.append(n)
    return names


def _extract_js_export_name(node, source: bytes) -> str:
    for child in node.children:
        if child.type in ("function_declaration", "class_declaration", "generator_function_declaration"):
            return _get_child_text_by_type(child, "identifier", source) or ""
        if child.type == "variable_declaration":
            for vc in child.children:
                if vc.type == "variable_declarator":
                    return _get_child_text_by_type(vc, "identifier", source) or ""
        if child.type == "assignment_expression":
            return _get_child_text_by_type(child, "identifier", source) or ""
    return ""


def _find_child(node, type_name: str):
    for child in node.children:
        if child.type == type_name:
            return child
    return None


def _get_child_text_by_type(node, type_name: str, source: bytes) -> str:
    child = _find_child(node, type_name)
    if child:
        return _node_text(child, source)
    return ""


def _find_children(node, type_name: str) -> list:
    return [c for c in node.children if c.type == type_name]


def _extract_ts_export_name(node, source: bytes) -> str:
    for child in node.children:
        if child.type in ("function_declaration", "class_declaration", "interface_declaration", "enum_declaration", "type_alias_declaration"):
            return (_get_child_text_by_type(child, "identifier", source) or 
                    _get_child_text_by_type(child, "type_identifier", source) or "")
        if child.type == "variable_declaration":
            for vc in child.children:
                if vc.type == "variable_declarator":
                    return _get_child_text_by_type(vc, "identifier", source) or ""
    return ""


def _extract_go(root, source: bytes) -> SymbolTable:
    functions: list[FunctionDef] = []
    classes: list[ClassDef] = []
    imports: list[ImportEntry] = []
    exports: list[ExportEntry] = []

    class_map: dict[str, ClassDef] = {}

    def visit(node):
        if node.type == "import_declaration":
            def collect_imports(n):
                if n.type == "import_spec":
                    path_node = _find_child(n, "interpreted_string_literal")
                    if path_node:
                        path = _node_text(path_node, source).strip('"')
                        alias_node = _find_child(n, "package_identifier")
                        alias = _node_text(alias_node, source) if alias_node else ""
                        names = [alias] if alias else []
                        imports.append(ImportEntry(source=path, names=names, kind="import"))
                for child in n.children:
                    collect_imports(child)
            collect_imports(node)
            return

        elif node.type == "type_declaration":
            spec = _find_child(node, "type_spec")
            if spec:
                name = _get_child_text_by_type(spec, "type_identifier", source)
                if name:
                    is_struct_or_interface = False
                    for child in spec.children:
                        if child.type in ("struct_type", "interface_type"):
                            is_struct_or_interface = True
                            break
                    if is_struct_or_interface:
                        start = node.start_point[0] + 1
                        end = node.end_point[0] + 1
                        cls = ClassDef(name=name, start_line=start, end_line=end)
                        classes.append(cls)
                        class_map[name] = cls
            return

        elif node.type == "function_declaration":
            name = _get_child_text_by_type(node, "identifier", source) or "<anon>"
            params = []
            param_list = _find_child(node, "parameter_list")
            if param_list:
                for child in param_list.children:
                    if child.type == "parameter_declaration":
                        p_name = _get_child_text_by_type(child, "identifier", source)
                        if p_name:
                            params.append(p_name)
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            complexity = calculate_complexity(node, "Go")
            func = FunctionDef(name=name, params=params, start_line=start, end_line=end, complexity=complexity)
            functions.append(func)
            return

        elif node.type == "method_declaration":
            mname = _get_child_text_by_type(node, "field_identifier", source) or "<anon>"
            receiver_type = ""
            rec_list = _find_child(node, "parameter_list")
            if rec_list:
                decl = _find_child(rec_list, "parameter_declaration")
                if decl:
                    ptr = _find_child(decl, "pointer_type")
                    if ptr:
                        receiver_type = _get_child_text_by_type(ptr, "type_identifier", source)
                    else:
                        receiver_type = _get_child_text_by_type(decl, "type_identifier", source)

            params = []
            param_lists = _find_children(node, "parameter_list")
            if len(param_lists) >= 2:
                for child in param_lists[1].children:
                    if child.type == "parameter_declaration":
                        p_name = _get_child_text_by_type(child, "identifier", source)
                        if p_name:
                            params.append(p_name)

            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            mcomplexity = calculate_complexity(node, "Go")
            func = FunctionDef(name=mname, params=params, start_line=start, end_line=end, is_method=True, complexity=mcomplexity)
            functions.append(func)

            if receiver_type and receiver_type in class_map:
                class_map[receiver_type].methods.append(func)
            return

        for child in node.children:
            visit(child)

    visit(root)

    for func in functions:
        if func.name and func.name[0].isupper() and not func.is_method:
            exports.append(ExportEntry(name=func.name, kind="export"))
    for cls in classes:
        if cls.name and cls.name[0].isupper():
            exports.append(ExportEntry(name=cls.name, kind="export"))

    return SymbolTable(functions=functions, classes=classes, imports=imports, exports=exports)


def _extract_rust(root, source: bytes) -> SymbolTable:
    functions: list[FunctionDef] = []
    classes: list[ClassDef] = []
    imports: list[ImportEntry] = []
    exports: list[ExportEntry] = []

    class_map: dict[str, ClassDef] = {}

    def visit(node):
        is_pub = False
        vis = _find_child(node, "visibility_modifier")
        if vis and _node_text(vis, source).startswith("pub"):
            is_pub = True

        if is_pub:
            name = _get_child_text_by_type(node, "identifier", source) or _get_child_text_by_type(node, "type_identifier", source)
            if name:
                exports.append(ExportEntry(name=name, kind="export"))

        if node.type == "use_declaration":
            path = _node_text(node, source).strip("use ;").strip()
            names = []
            if " as " in path:
                names.append(path.split(" as ")[-1].strip())
            imports.append(ImportEntry(source=path, names=names, kind="import"))
            return

        elif node.type in ("struct_item", "enum_item", "union_item", "trait_item"):
            name = _get_child_text_by_type(node, "type_identifier", source)
            if name:
                start = node.start_point[0] + 1
                end = node.end_point[0] + 1
                cls = ClassDef(name=name, start_line=start, end_line=end)
                classes.append(cls)
                class_map[name] = cls
            return

        elif node.type == "function_item":
            name = _get_child_text_by_type(node, "identifier", source) or "<anon>"
            params = []
            params_node = _find_child(node, "parameters")
            if params_node:
                for child in params_node.children:
                    if child.type == "parameter":
                        p_name = _get_child_text_by_type(child, "identifier", source)
                        if p_name:
                            params.append(p_name)
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            complexity = calculate_complexity(node, "Rust")
            func = FunctionDef(name=name, params=params, start_line=start, end_line=end, complexity=complexity)
            functions.append(func)
            return

        elif node.type == "impl_item":
            receiver = _get_child_text_by_type(node, "type_identifier", source)
            decl_list = _find_child(node, "declaration_list")
            if decl_list:
                for child in decl_list.children:
                    if child.type == "function_item":
                        mname = _get_child_text_by_type(child, "identifier", source) or "<anon>"
                        params = []
                        params_node = _find_child(child, "parameters")
                        if params_node:
                            for p in params_node.children:
                                if p.type == "parameter":
                                    p_name = _get_child_text_by_type(p, "identifier", source)
                                    if p_name:
                                        params.append(p_name)
                        start = child.start_point[0] + 1
                        end = child.end_point[0] + 1
                        mcomplexity = calculate_complexity(child, "Rust")
                        func = FunctionDef(name=mname, params=params, start_line=start, end_line=end, is_method=True, complexity=mcomplexity)
                        functions.append(func)
                        if receiver and receiver in class_map:
                            class_map[receiver].methods.append(func)
            return

        for child in node.children:
            visit(child)

    visit(root)
    return SymbolTable(functions=functions, classes=classes, imports=imports, exports=exports)


def _get_call_name(node, source_bytes: bytes, language: str) -> str | None:
    if language == "Python":
        func_child = None
        for c in node.children:
            if c.type in ("identifier", "attribute", "call", "subscript"):
                func_child = c
                break
        if func_child:
            text = source_bytes[func_child.start_byte:func_child.end_byte].decode("utf-8", errors="replace")
            return text.split(".")[-1]
    elif language in ("JavaScript", "TypeScript"):
        func_child = None
        for c in node.children:
            if c.type in ("identifier", "member_expression", "property_identifier", "call_expression"):
                func_child = c
                break
        if func_child:
            text = source_bytes[func_child.start_byte:func_child.end_byte].decode("utf-8", errors="replace")
            return text.split(".")[-1]
    return None


def _extract_calls(node, source_bytes: bytes, language: str) -> list[str]:
    calls = []
    def visit(n):
        if n.type in ("function_definition", "function_declaration", "class_definition", "class_declaration") and n != node:
            return
        
        is_call = False
        if language == "Python" and n.type == "call":
            is_call = True
        elif language in ("JavaScript", "TypeScript") and n.type == "call_expression":
            is_call = True
        
        if is_call:
            name = _get_call_name(n, source_bytes, language)
            if name:
                calls.append(name)
        
        for child in n.children:
            visit(child)
            
    visit(node)
    return list(set(calls))

