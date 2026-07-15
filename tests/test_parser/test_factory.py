from dna.parser.factory import get_parser, is_language_supported


def test_get_parser_python():
    parser = get_parser("Python")
    assert parser is not None


def test_get_parser_javascript():
    parser = get_parser("JavaScript")
    assert parser is not None


def test_get_parser_unsupported():
    parser = get_parser("Cobol")
    assert parser is None


def test_is_language_supported():
    assert is_language_supported("Python") is True
    assert is_language_supported("Cobol") is False
