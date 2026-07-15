from tree_sitter import Language, Parser
from dna.models import LanguageInfo


_DEFAULT_LANGUAGES: list[LanguageInfo] = [
    LanguageInfo(
        name="Python",
        extensions=[".py", ".pyi", ".pyx"],
        parser_module="tree_sitter_python",
        query_function="(function_definition name: (identifier) @name) @func",
        query_class="(class_definition name: (identifier) @name) @class",
        query_method="(function_definition) @method",
    ),
    LanguageInfo(
        name="JavaScript",
        extensions=[".js", ".jsx", ".mjs", ".cjs"],
        parser_module="tree_sitter_javascript",
        query_function="(function_declaration name: (identifier) @name) @func",
        query_class="(class_declaration name: (identifier) @name) @class",
        query_method="(method_definition name: (property_identifier) @name) @method",
    ),
    LanguageInfo(
        name="TypeScript",
        extensions=[".ts", ".tsx"],
        parser_module="tree_sitter_typescript",
        query_function="(function_declaration name: (identifier) @name) @func",
        query_class="(class_declaration name: (identifier) @name) @class",
        query_method="(method_definition name: (property_identifier) @name) @method",
    ),
    LanguageInfo(
        name="Go",
        extensions=[".go"],
        parser_module="tree_sitter_go",
        query_function="(function_declaration name: (identifier) @name) @func",
        query_class="(type_declaration (type_spec name: (type_identifier) @name type: (struct_type))) @class",
        query_method="(method_declaration name: (field_identifier) @name) @method",
    ),
    LanguageInfo(
        name="Rust",
        extensions=[".rs"],
        parser_module="tree_sitter_rust",
        query_function="(function_item name: (identifier) @name) @func",
        query_class="(struct_item name: (type_identifier) @name) @class",
        query_method="(function_item name: (identifier) @name) @method",
    ),
]


class LanguageRegistry:
    _instance: "LanguageRegistry | None" = None
    _languages: dict[str, LanguageInfo]
    _parser_cache: dict[str, Parser]
    _by_extension: dict[str, LanguageInfo]

    def __new__(cls) -> "LanguageRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._languages = {}
            cls._instance._parser_cache = {}
            cls._instance._by_extension = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> "LanguageRegistry":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._languages = {}
            cls._instance._parser_cache = {}
            cls._instance._by_extension = {}
        return cls._instance

    def register(self, info: LanguageInfo) -> None:
        self._languages[info.name] = info
        for ext in info.extensions:
            self._by_extension[ext.lower()] = info

    def unregister(self, name: str) -> None:
        info = self._languages.pop(name, None)
        if info:
            for ext in info.extensions:
                self._by_extension.pop(ext.lower(), None)
            self._parser_cache.pop(name, None)

    def get_language(self, name: str) -> LanguageInfo | None:
        return self._languages.get(name)

    def get_by_extension(self, ext: str) -> LanguageInfo | None:
        return self._by_extension.get(ext.lower())

    def get_parser(self, name: str) -> Parser | None:
        if name in self._parser_cache:
            return self._parser_cache[name]

        info = self._languages.get(name)
        if info is None:
            return None

        try:
            import importlib
            mod = importlib.import_module(info.parser_module)
            if info.parser_module == "tree_sitter_typescript":
                lang = Language(mod.language_typescript())
            else:
                lang = Language(mod.language())
            parser = Parser(lang)
            self._parser_cache[name] = parser
            return parser
        except (ImportError, AttributeError):
            return None

    def get_all_languages(self) -> list[LanguageInfo]:
        return list(self._languages.values())

    def is_supported(self, name: str) -> bool:
        return name in self._languages

    @classmethod
    def initialize_defaults(cls) -> "LanguageRegistry":
        reg = cls.get_instance()
        for lang_info in _DEFAULT_LANGUAGES:
            reg.register(lang_info)
        return reg


_registry: LanguageRegistry | None = None


def get_registry() -> LanguageRegistry:
    global _registry
    if _registry is None:
        _registry = LanguageRegistry.initialize_defaults()
    return _registry


def get_parser(language: str) -> Parser | None:
    return get_registry().get_parser(language)


def is_language_supported(language: str) -> bool:
    return get_registry().is_supported(language)
