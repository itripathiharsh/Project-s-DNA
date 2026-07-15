import os
from tree_sitter import Parser
from dna.models import ParsedFile
from dna.parser.factory import get_parser
from dna.parser.traverser import extract_symbols
from dna.indexer.hasher import compute_file_hash
from dna.parser.errors import ParseError, UnsupportedLanguageError


def parse_file(file_path: str, language: str) -> ParsedFile | None:
    parser = get_parser(language)
    if parser is None:
        raise UnsupportedLanguageError(language)

    try:
        with open(file_path, "rb") as f:
            source = f.read()
    except OSError:
        return None

    return _parse_bytes(source, language, file_path=file_path, parser=parser)


def parse_source(source: str | bytes, language: str) -> ParsedFile | None:
    parser = get_parser(language)
    if parser is None:
        raise UnsupportedLanguageError(language)

    if isinstance(source, str):
        source = source.encode("utf-8")

    return _parse_bytes(source, language, file_path=None, parser=parser)


def _parse_bytes(source: bytes, language: str, file_path: str | None, parser: Parser) -> ParsedFile:
    try:
        tree = parser.parse(source)
    except Exception as e:
        raise ParseError(file_path or "<string>", str(e))

    content_hash = compute_file_hash(file_path) if file_path else ""
    symbols = extract_symbols(tree.root_node, source, language)

    rel_path = None
    if file_path:
        try:
            rel_path = os.path.relpath(file_path)
        except ValueError:
            rel_path = file_path

    return ParsedFile(
        file_path=file_path,
        relative_path=rel_path,
        language=language,
        content_hash=content_hash,
        source_bytes=source,
        ast_tree=tree,
        symbols=symbols,
    )
