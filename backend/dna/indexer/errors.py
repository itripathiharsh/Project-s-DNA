class IndexerError(Exception):
    pass


class FileReadError(IndexerError):
    def __init__(self, path: str, reason: str):
        super().__init__(f"Cannot read {path}: {reason}")
        self.path = path
        self.reason = reason
