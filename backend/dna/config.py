import json
import os
from pathlib import Path
from typing import Any, Optional


class DNAConfig:
    def __init__(
        self,
        max_file_size_bytes: int = 1024 * 1024,
        always_ignore: Optional[list[str]] = None,
        parser_max_workers: int = 4,
        log_level: str = "INFO",
        network_mode: bool = False,
        api_keys: Optional[list[str]] = None,
        store_path: str = "",
        evidence_path: str = "",
        repo_cache_dir: str = "backend/cache/repos",
        repo_cache_ttl_days: int = 7,
        enable_remote_repos: bool = True,
        git_clone_timeout: int = 600,
        git_fetch_timeout: int = 30,
    ):
        self.max_file_size_bytes = max_file_size_bytes
        self.always_ignore = always_ignore or [
            # Directories to always ignore (source code only)
            ".git",
            ".github",
            ".idea",
            ".vscode",
            ".venv",
            "venv",
            "env",
            "node_modules",
            "dist",
            "build",
            "coverage",
            "__pycache__",
            "target",
            "bin",
            "obj",
            "site-packages",
            ".next",
            ".cache",
            "tmp",
            "logs",
            "out",
        ]

        self.parser_max_workers = parser_max_workers
        # Timeout for analysis requests (seconds). None means no timeout.
        self.request_timeout_seconds = None
        # File extensions to ignore completely (binary, archives, etc.)
        self.ignore_extensions = [
            ".dll", ".so", ".dylib", ".exe", ".pyd", ".class", ".jar",
            ".zip", ".tar", ".gz", ".7z",
        ]
        # Extensions that are considered source code and should be indexed
        self.supported_extensions = [
            ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".kt", ".go", ".rs",
            ".cpp", ".cc", ".c", ".h", ".hpp", ".cs", ".swift", ".php",
            ".rb", ".scala", ".sql", ".html", ".css", ".scss", ".md",
            ".yaml", ".yml", ".toml", ".json", ".xml",
        ]
        self.log_level = log_level
        self.network_mode = network_mode
        self.api_keys: list[str] = api_keys or []
        self.store_path = store_path
        self.evidence_path = evidence_path
        self.repo_cache_dir = repo_cache_dir
        self.repo_cache_ttl_days = repo_cache_ttl_days
        self.enable_remote_repos = enable_remote_repos
        self.git_clone_timeout = git_clone_timeout
        self.git_fetch_timeout = git_fetch_timeout

    @classmethod
    def load(cls) -> "DNAConfig":
        # Start with defaults
        config = cls()

        # Load from config file: ~/.config/dna/dna.json
        config_path = Path(os.path.expanduser("~/.config/dna/dna.json"))
        if config_path.is_file():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    config._apply_dict(data)
            except Exception:
                # Fallback silently or log if needed
                pass

        # Load from environment variables
        config._apply_env()

        return config

    def _apply_dict(self, data: dict[str, Any]) -> None:
        if "max_file_size_bytes" in data:
            try:
                self.max_file_size_bytes = int(data["max_file_size_bytes"])
            except (ValueError, TypeError):
                pass
        if "always_ignore" in data:
            if isinstance(data["always_ignore"], list):
                self.always_ignore = [str(x) for x in data["always_ignore"]]
        if "parser_max_workers" in data:
            try:
                self.parser_max_workers = int(data["parser_max_workers"])
            except (ValueError, TypeError):
                pass
        if "log_level" in data:
            self.log_level = str(data["log_level"])
        if "network_mode" in data:
            self.network_mode = bool(data["network_mode"])
        if "api_keys" in data:
            if isinstance(data["api_keys"], list):
                self.api_keys = [str(k) for k in data["api_keys"]]
        if "store_path" in data:
            self.store_path = str(data["store_path"])
        if "evidence_path" in data:
            self.evidence_path = str(data["evidence_path"])
        if "repo_cache_dir" in data:
            self.repo_cache_dir = str(data["repo_cache_dir"])
        if "repo_cache_ttl_days" in data:
            try:
                self.repo_cache_ttl_days = int(data["repo_cache_ttl_days"])
            except (ValueError, TypeError):
                pass
        if "enable_remote_repos" in data:
            self.enable_remote_repos = bool(data["enable_remote_repos"])
        if "git_clone_timeout" in data:
            try:
                self.git_clone_timeout = int(data["git_clone_timeout"])
            except (ValueError, TypeError):
                pass
        if "git_fetch_timeout" in data:
            try:
                self.git_fetch_timeout = int(data["git_fetch_timeout"])
            except (ValueError, TypeError):
                pass

    def _apply_env(self) -> None:
        if "DNA_MAX_FILE_SIZE_BYTES" in os.environ:
            try:
                self.max_file_size_bytes = int(os.environ["DNA_MAX_FILE_SIZE_BYTES"])
            except ValueError:
                pass
        if "DNA_ALWAYS_IGNORE" in os.environ:
            val = os.environ["DNA_ALWAYS_IGNORE"]
            self.always_ignore = [x.strip() for x in val.split(",") if x.strip()]
        if "DNA_PARSER_MAX_WORKERS" in os.environ:
            try:
                self.parser_max_workers = int(os.environ["DNA_PARSER_MAX_WORKERS"])
            except ValueError:
                pass
        if "DNA_LOG_LEVEL" in os.environ:
            self.log_level = os.environ["DNA_LOG_LEVEL"]
        if "DNA_NETWORK_MODE" in os.environ:
            self.network_mode = os.environ["DNA_NETWORK_MODE"].lower() in ("1", "true", "yes")
        if "DNA_API_KEYS" in os.environ:
            val = os.environ["DNA_API_KEYS"]
            self.api_keys = [k.strip() for k in val.split(",") if k.strip()]
        if "DNA_STORE_PATH" in os.environ:
            self.store_path = os.environ["DNA_STORE_PATH"]
        if "DNA_EVIDENCE_PATH" in os.environ:
            self.evidence_path = os.environ["DNA_EVIDENCE_PATH"]
        if "REPO_CACHE_DIR" in os.environ:
            self.repo_cache_dir = os.environ["REPO_CACHE_DIR"]
        if "REPO_CACHE_TTL_DAYS" in os.environ:
            try:
                self.repo_cache_ttl_days = int(os.environ["REPO_CACHE_TTL_DAYS"])
            except ValueError:
                pass
        if "ENABLE_REMOTE_REPOS" in os.environ:
            self.enable_remote_repos = os.environ["ENABLE_REMOTE_REPOS"].lower() in ("1", "true", "yes")
        if "GIT_CLONE_TIMEOUT" in os.environ:
            try:
                self.git_clone_timeout = int(os.environ["GIT_CLONE_TIMEOUT"])
            except ValueError:
                pass
        if "GIT_FETCH_TIMEOUT" in os.environ:
            try:
                self.git_fetch_timeout = int(os.environ["GIT_FETCH_TIMEOUT"])
            except ValueError:
                pass


# Global configuration instance
_global_config: Optional[DNAConfig] = None


def get_config() -> DNAConfig:
    global _global_config
    if _global_config is None:
        _global_config = DNAConfig.load()
    
    if "PYTEST_CURRENT_TEST" in os.environ:
        import tempfile
        # Generate unique path for this specific test case
        test_env = os.environ["PYTEST_CURRENT_TEST"]
        # Sanitize to be a safe filename prefix
        safe_name = "".join(c if c.isalnum() else "_" for c in test_env.split(" ")[0])
        _global_config.store_path = os.path.join(tempfile.gettempdir(), f"sc_store_{safe_name}.db")
        _global_config.evidence_path = os.path.join(tempfile.gettempdir(), f"ev_store_{safe_name}.db")
        
    return _global_config


def reset_config() -> None:
    global _global_config
    _global_config = None
