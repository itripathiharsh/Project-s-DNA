import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
from dna.config import DNAConfig, get_config, reset_config


def test_config_defaults():
    reset_config()
    config = DNAConfig()
    assert config.max_file_size_bytes == 1024 * 1024
    assert ".git" in config.always_ignore
    assert config.parser_max_workers == 4


def test_config_env_vars():
    reset_config()
    with patch.dict(os.environ, {
        "DNA_MAX_FILE_SIZE_BYTES": "2048",
        "DNA_ALWAYS_IGNORE": "foo,bar",
        "DNA_PARSER_MAX_WORKERS": "8"
    }):
        config = DNAConfig.load()
        assert config.max_file_size_bytes == 2048
        assert config.always_ignore == ["foo", "bar"]
        assert config.parser_max_workers == 8


def test_config_file():
    reset_config()
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "dna"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "dna.json"
        
        with open(config_file, "w") as f:
            json.dump({
                "max_file_size_bytes": 5000,
                "always_ignore": ["temp_ignore"],
                "parser_max_workers": 2
            }, f)
            
        with patch("os.path.expanduser", lambda p: p.replace("~", tmpdir, 1)):
            config = DNAConfig.load()
            assert config.max_file_size_bytes == 5000
            assert config.always_ignore == ["temp_ignore"]
            assert config.parser_max_workers == 2
