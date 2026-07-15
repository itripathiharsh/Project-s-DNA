"""Tests for GitHub repository support (remote clone, cache, lock, cleanup)."""

import os
import time
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from dna.api.app import app
from dna.remote import is_github_url, parse_github_url, DirLock, cleanup_cache, get_local_repo_from_github

client = TestClient(app)


# ---------------------------------------------------------------------------
# GitHub URL detection
# ---------------------------------------------------------------------------

class TestGitHubUrlDetection:
    def test_valid_github_urls(self):
        assert is_github_url("https://github.com/user/repo")
        assert is_github_url("https://github.com/user/repo.git")
        assert is_github_url("https://github.com/user/repo/")
        assert is_github_url("http://github.com/user/repo")
        assert is_github_url("https://www.github.com/user/repo")

    def test_invalid_inputs(self):
        assert not is_github_url("C:\\Users\\repo")
        assert not is_github_url("/home/user/repo")
        assert not is_github_url("not-a-url")
        assert not is_github_url("")
        assert not is_github_url("https://gitlab.com/user/repo")
        assert not is_github_url("git@github.com:user/repo.git")

    def test_parse_github_url(self):
        assert parse_github_url("https://github.com/user/repo") == ("user", "repo")
        assert parse_github_url("https://github.com/user/repo.git") == ("user", "repo")
        assert parse_github_url("https://github.com/user/repo/") == ("user", "repo")

    def test_parse_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_github_url("not-a-url")


# ---------------------------------------------------------------------------
# DirLock (concurrency control)
# ---------------------------------------------------------------------------

class TestDirLock:
    def test_lock_release(self, tmp_path):
        lock_path = str(tmp_path / "test.lock")
        lock = DirLock(lock_path)
        lock.acquire()
        assert os.path.exists(lock_path)
        lock.release()
        assert not os.path.exists(lock_path)

    def test_lock_release_via_context(self, tmp_path):
        lock_path = str(tmp_path / "test.lock")
        with DirLock(lock_path):
            assert os.path.exists(lock_path)
        assert not os.path.exists(lock_path)

    def test_lock_timeout_raises(self, tmp_path):
        lock_path = str(tmp_path / "test.lock")
        os.mkdir(lock_path)
        with pytest.raises(TimeoutError):
            DirLock(lock_path, timeout=1, poll_interval=0.1).acquire()
        os.rmdir(lock_path)


# ---------------------------------------------------------------------------
# Cache cleanup
# ---------------------------------------------------------------------------

class TestCleanupCache:
    def test_removes_expired(self, tmp_path):
        cache_dir = str(tmp_path / "cache")
        repo_path = os.path.join(cache_dir, "owner_repo")
        os.makedirs(repo_path)

        old_time = time.time() - (10 * 86400)  # 10 days ago
        os.utime(repo_path, (old_time, old_time))

        cleanup_cache(cache_dir, ttl_days=7)
        assert not os.path.exists(repo_path)

    def test_keeps_recent(self, tmp_path):
        cache_dir = str(tmp_path / "cache")
        repo_path = os.path.join(cache_dir, "owner_repo")
        os.makedirs(repo_path)

        cleanup_cache(cache_dir, ttl_days=7)
        assert os.path.exists(repo_path)

    def test_skips_locked(self, tmp_path):
        cache_dir = str(tmp_path / "cache")
        repo_path = os.path.join(cache_dir, "owner_repo")
        os.makedirs(repo_path)

        old_time = time.time() - (10 * 86400)
        os.utime(repo_path, (old_time, old_time))

        # Create lock
        lock_path = os.path.join(cache_dir, "owner_repo.lock")
        os.makedirs(lock_path)

        cleanup_cache(cache_dir, ttl_days=7)
        assert os.path.exists(repo_path)
        os.rmdir(lock_path)


# ---------------------------------------------------------------------------
# API endpoint integration
# ---------------------------------------------------------------------------

class TestApiRemoteEndpoints:
    def test_local_path_still_works(self):
        """Existing local path validation still works."""
        r = client.post("/v1/analyze", json={"repo_path": "C:\\nonexistent_xyz"})
        assert r.status_code == 400
        assert "not exist" in r.json()["detail"].lower()

    def test_github_url_rejected_when_disabled(self):
        """If remote repos are disabled via config, return 400."""
        with patch("dna.remote.get_config") as mock_cfg:
            mock_cfg.return_value.enable_remote_repos = False
            mock_cfg.return_value.repo_cache_dir = str(os.path.join(os.path.dirname(__file__), "..", "cache"))
            mock_cfg.return_value.repo_cache_ttl_days = 7
            r = client.post("/v1/analyze", json={"repo_path": "https://github.com/itripathiharsh/Green_Minds"})
            assert r.status_code == 400
            assert "disabled" in r.json()["detail"].lower()

    def test_github_url_missing_git(self):
        """If git is not installed, return 503."""
        with patch("dna.remote.check_git_installed") as mock_check:
            mock_check.side_effect = RuntimeError("Git is not installed")
            r = client.post("/v1/analyze", json={"repo_path": "https://github.com/itripathiharsh/Green_Minds"})
            assert r.status_code == 503

    def test_invalid_github_url(self):
        """Malformed GitHub URL returns 400."""
        r = client.post("/v1/analyze", json={"repo_path": "https://github.com/only-user-no-repo"})
        assert r.status_code == 400

    def test_empty_repo_path(self):
        """Empty path returns 400."""
        r = client.post("/v1/analyze", json={"repo_path": ""})
        assert r.status_code == 400

    @pytest.mark.slow
    def test_github_clone_and_analyze(self):
        """End-to-end: clone a public GitHub repo and analyze it."""
        r = client.post("/v1/analyze", json={
            "repo_path": "https://github.com/itripathiharsh/Green_Minds"
        })
        assert r.status_code == 200, f"Response: {r.json()}"
        data = r.json()

        # Must return the original URL, not the cache path
        assert data["repository"]["path"] == "https://github.com/itripathiharsh/Green_Minds"
        assert "summary" in data
        assert data["summary"]["total_files"] > 0
        assert "evolution" in data
        assert "knowledge" in data
        assert "risk" in data
        assert "structural" in data
        assert "insights" in data

    @pytest.mark.slow
    @pytest.mark.depends(on=["test_github_clone_and_analyze"])
    def test_github_cached_analysis(self):
        """Second request must reuse cache and complete successfully."""
        r = client.post("/v1/analyze", json={
            "repo_path": "https://github.com/itripathiharsh/Green_Minds"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["repository"]["path"] == "https://github.com/itripathiharsh/Green_Minds"
        assert data["summary"]["total_files"] > 0
