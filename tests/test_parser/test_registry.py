from dna.parser.registry import LanguageRegistry, get_registry, get_parser, is_language_supported
from dna.models import LanguageInfo


def _clean_registry():
    reg = LanguageRegistry.get_instance()
    reg._languages = {}
    reg._parser_cache = {}
    reg._by_extension = {}
    return reg


def setup_method():
    _clean_registry()


def test_default_registry_initialized():
    reg = _clean_registry()
    reg.initialize_defaults()
    assert reg.is_supported("Python")
    assert reg.is_supported("JavaScript")
    assert reg.is_supported("TypeScript")
    assert not reg.is_supported("COBOL")


def test_register_custom_language():
    reg = _clean_registry()
    info = LanguageInfo(
        name="Rust",
        extensions=[".rs"],
        parser_module="tree_sitter_rust",
    )
    reg.register(info)
    assert reg.is_supported("Rust")
    assert reg.get_by_extension(".rs") is not None


def test_unregister():
    reg = _clean_registry()
    info = LanguageInfo(name="Python", extensions=[".py"], parser_module="x")
    reg.register(info)
    assert reg.is_supported("Python")
    reg.unregister("Python")
    assert not reg.is_supported("Python")


def test_get_by_extension():
    reg = _clean_registry()
    info = LanguageInfo(name="Python", extensions=[".py", ".pyi"], parser_module="x")
    reg.register(info)
    assert reg.get_by_extension(".py") is info
    assert reg.get_by_extension(".PY") is info
    assert reg.get_by_extension(".rs") is None


def test_get_language():
    reg = _clean_registry()
    info = LanguageInfo(name="Python", extensions=[".py"], parser_module="x")
    reg.register(info)
    assert reg.get_language("Python") is info
    assert reg.get_language("COBOL") is None


def test_get_all_languages():
    reg = _clean_registry()
    reg.register(LanguageInfo(name="A", extensions=[], parser_module=""))
    reg.register(LanguageInfo(name="B", extensions=[], parser_module=""))
    assert len(reg.get_all_languages()) == 2


def test_get_parser_supported():
    reg = _clean_registry()
    reg.initialize_defaults()
    parser = reg.get_parser("Python")
    assert parser is not None


def test_get_parser_unsupported():
    reg = _clean_registry()
    parser = reg.get_parser("COBOL")
    assert parser is None


def test_is_language_supported():
    reg = _clean_registry()
    reg.initialize_defaults()
    assert reg.is_supported("Python") is True
    assert reg.is_supported("Brainfuck") is False


def test_singleton():
    r1 = LanguageRegistry()
    r2 = LanguageRegistry()
    assert r1 is r2


def test_initialize_defaults():
    reg = _clean_registry()
    reg.initialize_defaults()
    assert reg.is_supported("Python")


def test_get_parser_python_via_module():
    reg = _clean_registry()
    reg.initialize_defaults()
    from dna.parser.registry import get_parser as gp
    parser = gp("Python")
    assert parser is not None
