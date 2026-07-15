class ParserError(Exception):
    pass


class UnsupportedLanguageError(ParserError):
    def __init__(self, language: str):
        self.language = language
        super().__init__(f"Unsupported language: {language}")


class ParseError(ParserError):
    def __init__(self, path: str, message: str):
        self.path = path
        super().__init__(f"Parse error in {path}: {message}")
