LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".hpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".sql": "SQL",
    ".css": "CSS",
    ".scss": "CSS",
    ".less": "CSS",
    ".html": "HTML",
    ".htm": "HTML",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".tf": "Terraform",
    ".dockerfile": "Docker",
    ".proto": "Protocol Buffers",
    ".xml": "XML",
    ".svg": "SVG",
    ".png": "Image",
    ".jpg": "Image",
    ".jpeg": "Image",
    ".gif": "Image",
    ".ico": "Image",
    ".woff": "Font",
    ".woff2": "Font",
    ".ttf": "Font",
    ".eot": "Font",
    ".otf": "Font",
}

SOURCE_EXTENSIONS: set[str] = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs",
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".rb", ".php",
    ".swift", ".kt", ".kts", ".sh", ".bash", ".zsh", ".tf",
    ".css", ".scss", ".less", ".html", ".htm", ".sql",
}


def detect_language(extension: str) -> str:
    return LANGUAGE_MAP.get(extension.lower(), "Unknown")


def is_source_file(extension: str) -> bool:
    return extension.lower() in SOURCE_EXTENSIONS


def classify_files(files: list) -> dict:
    from dna.models import LanguageStats

    counts: dict[str, int] = {}
    sizes: dict[str, int] = {}

    for f in files:
        lang = f.language
        counts[lang] = counts.get(lang, 0) + 1
        sizes[lang] = sizes.get(lang, 0) + f.size_bytes

    total = sum(counts.values())
    if total == 0:
        return {}

    stats = {}
    for lang in counts:
        stats[lang] = LanguageStats(
            language=lang,
            file_count=counts[lang],
            total_bytes=sizes[lang],
            percentage=round(counts[lang] / total, 4),
        )
    return stats
