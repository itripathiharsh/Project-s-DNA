import os
from dna.models import FileInfo, RepositoryMetadata, FileCategory, FileClassificationMap
from dna.discovery.languages import is_source_file


_TEST_DIR_NAMES = {"test", "tests", "__tests__", "spec", "specs"}
_TEST_PREFIXES = ("test_", "test-")
_TEST_SUFFIXES = (".test.", ".spec.", "_test.")
_CONFIG_FILENAMES = {
    "package.json", "tsconfig.json", "tsconfig.app.json",
    ".eslintrc", ".eslintrc.json", ".eslintrc.js", ".prettierrc",
    "webpack.config.js", "vite.config.ts", "vite.config.js",
    "jest.config.js", "jest.config.ts", "next.config.js",
    "babel.config.js", "rollup.config.js",
}
_BUILD_FILENAMES = {
    "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "build.gradle", "CMakeLists.txt", "Rakefile", "Cargo.toml",
    "justfile", "taskfile.yml",
}
_DOC_EXTENSIONS = {".md", ".rst", ".txt", ".pdf", ".doc", ".docx"}


def classify_file(file_info: FileInfo, repo_metadata: RepositoryMetadata) -> FileCategory:
    rel = file_info.relative_path.replace("\\", "/")
    parts = rel.split("/")
    filename = file_info.filename
    ext = file_info.extension.lower()

    for part in parts:
        if part in _TEST_DIR_NAMES:
            return FileCategory.TEST

    if filename in _CONFIG_FILENAMES:
        return FileCategory.CONFIG
    if ext in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}:
        return FileCategory.CONFIG

    if filename in _BUILD_FILENAMES or ext in {".gradle", ".bazel", ".bzl"}:
        return FileCategory.BUILD

    if ext in _DOC_EXTENSIONS:
        return FileCategory.DOCUMENTATION

    if is_source_file(file_info.extension):
        basename = os.path.splitext(filename)[0]
        if basename.startswith(_TEST_PREFIXES) or basename.endswith(_TEST_SUFFIXES):
            return FileCategory.TEST
        return FileCategory.SOURCE

    if ext in {".csv", ".jsonl", ".ndjson", ".xml", ".sql", ".db", ".sqlite"}:
        return FileCategory.DATA

    return FileCategory.OTHER


def build_classification_map(
    files: list[FileInfo],
    repo_metadata: RepositoryMetadata,
) -> FileClassificationMap:
    cmap = FileClassificationMap()
    for f in files:
        cat = classify_file(f, repo_metadata)
        cmap.add(cat, f.relative_path)
    return cmap
