from dna.models import ParsedFile, NormalizedFile, CanonicalNode, SymbolTable, FunctionDef, ClassDef, ImportEntry, ExportEntry
from dna.normalizer.python_normalizer import normalize_python
from dna.normalizer.js_normalizer import normalize_javascript
from dna.normalizer.ts_normalizer import normalize_typescript
from dna.parser.factory import get_parser


def normalize_parsed_files(parsed_files: list[ParsedFile]) -> list[NormalizedFile]:
    result: list[NormalizedFile] = []

    for pf in parsed_files:
        nf = _normalize_single(pf)
        if nf is not None:
            result.append(nf)

    return result


def normalize_file(file_path: str, language: str, source: bytes, content_hash: str = "") -> NormalizedFile:
    parser = get_parser(language)
    if parser is None:
        return NormalizedFile(relative_path=file_path, language=language, content_hash=content_hash)

    try:
        tree = parser.parse(source)
    except Exception:
        return NormalizedFile(relative_path=file_path, language=language, content_hash=content_hash)

    root_node = tree.root_node

    if language == "Python":
        root = normalize_python(root_node, source)
    elif language == "JavaScript":
        root = normalize_javascript(root_node, source)
    elif language == "TypeScript":
        root = normalize_typescript(root_node, source)
    else:
        return NormalizedFile(relative_path=file_path, language=language, content_hash=content_hash)

    symbols = _extract_symbols_from_canonical(root)

    return NormalizedFile(
        relative_path=file_path,
        language=language,
        content_hash=content_hash,
        root=root,
        symbols=symbols,
    )


def _normalize_single(pf: ParsedFile) -> NormalizedFile | None:
    if not pf.file_path or not pf.language:
        return None

    if not pf.source_bytes:
        return None

    if pf.ast_tree is not None:
        tree = pf.ast_tree
    else:
        parser = get_parser(pf.language)
        if parser is None:
            return None
        try:
            tree = parser.parse(pf.source_bytes)
        except Exception:
            return None

    root_node = tree.root_node

    if pf.language == "Python":
        root = normalize_python(root_node, pf.source_bytes)
    elif pf.language == "JavaScript":
        root = normalize_javascript(root_node, pf.source_bytes)
    elif pf.language == "TypeScript":
        root = normalize_typescript(root_node, pf.source_bytes)
    else:
        return None

    symbols = _extract_symbols_from_canonical(root)

    return NormalizedFile(
        relative_path=pf.relative_path or "",
        language=pf.language,
        content_hash=pf.content_hash,
        root=root,
        symbols=symbols,
    )


def _extract_symbols_from_canonical(root: CanonicalNode) -> SymbolTable:
    symbols = SymbolTable()

    def walk(node: CanonicalNode, current_class: ClassDef | None = None):
        if node.kind == "function":
            is_method = current_class is not None or node.metadata.get("is_method") == "true"
            func_name = node.name
            if is_method and current_class:
                method_def = FunctionDef(
                    name=func_name,
                    start_line=node.start_line,
                    end_line=node.end_line,
                    is_method=True,
                )
                current_class.methods.append(method_def)
            else:
                symbols.functions.append(FunctionDef(
                    name=func_name,
                    start_line=node.start_line,
                    end_line=node.end_line,
                    is_method=is_method,
                ))
        elif node.kind in ("class", "interface", "enum", "type_alias"):
            cls_def = ClassDef(
                name=node.name,
                start_line=node.start_line,
                end_line=node.end_line,
                base_classes=node.metadata.get("bases", "").split(", ") if node.metadata.get("bases") else [],
            )
            symbols.classes.append(cls_def)
            for child in node.children:
                walk(child, cls_def)
            return

        elif node.kind == "import":
            symbols.imports.append(ImportEntry(source=node.name, kind="import"))
        elif node.kind == "export":
            symbols.exports.append(ExportEntry(name=node.name, kind="export"))

        for child in node.children:
            walk(child, current_class)

    walk(root)
    return symbols
