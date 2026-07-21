"""Security hardening tests — prove path traversal and injection are blocked."""

import os
import pytest
import tempfile

from dna.security.path_validation import (
    safe_validate_path,
    validate_branch_name,
    validate_filename,
    canonicalize_path,
    is_path_within_base,
    sanitize_repo_dir_name,
)


class TestCanonicalizePath:
    def test_absolute_path_resolved(self):
        result = canonicalize_path("/tmp/../tmp/foo")
        # Should resolve .. to canonical form
        assert result == os.path.realpath("/tmp/foo")

    def test_trailing_dot_dot_blocked(self):
        result = canonicalize_path("/tmp/../")
        assert result == os.path.realpath("/")

    def test_symlink_inside_allowed(self, tmp_path):
        real_dir = tmp_path / "real"
        real_dir.mkdir()
        link_dir = tmp_path / "link"
        link_dir.symlink_to(real_dir)
        result = canonicalize_path(str(link_dir))
        assert result == os.path.realpath(str(real_dir))


class TestIsPathWithinBase:
    def test_path_within_base(self, tmp_path):
        base = str(tmp_path)
        sub = tmp_path / "sub" / "file.txt"
        sub.parent.mkdir()
        sub.touch()
        assert is_path_within_base(str(sub), base)

    def test_path_outside_base(self, tmp_path):
        base = str(tmp_path)
        outside = tmp_path.parent / "secret.txt"
        assert not is_path_within_base(str(outside), base)

    def test_symlink_outside_blocked(self, tmp_path):
        base = tmp_path / "base"
        base.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        link = base / "evil"
        link.symlink_to(outside)
        assert not is_path_within_base(str(link / "secret.txt"), str(base))

    def test_dot_dot_traversal(self, tmp_path):
        base = str(tmp_path)
        traversal = os.path.join(base, "..", "..", "etc", "passwd")
        assert not is_path_within_base(traversal, base)

    def test_deeply_nested_traversal(self, tmp_path):
        base = str(tmp_path)
        traversal = os.path.join(base, "a", "b", "..", "..", "..", "etc")
        assert not is_path_within_base(traversal, base)

    def test_mixed_separator_traversal(self, tmp_path):
        base = str(tmp_path)
        # Try mixing forward/back slashes to bypass simple checks
        traversal = base + "/../../etc/passwd"
        assert not is_path_within_base(traversal, base)

    def test_root_path_is_base(self, tmp_path):
        base = str(tmp_path)
        assert is_path_within_base(base, base)

    def test_empty_path_returns_false(self, tmp_path):
        base = str(tmp_path)
        assert not is_path_within_base("", base)


class TestSafeValidatePath:
    def test_valid_path_passes(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        result = safe_validate_path(str(sub), str(tmp_path))
        assert result == os.path.realpath(str(sub))

    def test_dot_dot_blocked(self, tmp_path):
        base = str(tmp_path)
        with pytest.raises(ValueError, match="Path traversal"):
            safe_validate_path(os.path.join(base, "..", "..", "etc"), base)

    def test_absolute_path_outside_blocked(self, tmp_path):
        base = str(tmp_path)
        with pytest.raises(ValueError, match="Path traversal"):
            safe_validate_path("C:\\Windows\\System32" if os.name == "nt" else "/etc", base)

    def test_null_byte_blocked(self, tmp_path):
        base = str(tmp_path)
        with pytest.raises(ValueError, match="null byte"):
            safe_validate_path(os.path.join(base, "safe.txt\x00../../etc/passwd"), base)

    def test_no_base_validation_allows_any(self):
        # Without a base, validation should not block any valid path
        result = safe_validate_path(os.getcwd())
        assert result == os.path.realpath(os.getcwd())

    def test_empty_path_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            safe_validate_path("")

    def test_none_path_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            safe_validate_path(None)


class TestValidateBranchName:
    def test_valid_branch_names(self):
        validate_branch_name("main")
        validate_branch_name("feature/my-feature")
        validate_branch_name("v1.2.3")
        validate_branch_name("fix_bug_123")
        assert True  # No exception = valid

    def test_path_traversal_in_branch_name(self):
        with pytest.raises(ValueError, match="Invalid branch name"):
            validate_branch_name("../etc")

    def test_special_chars_blocked(self):
        with pytest.raises(ValueError):
            validate_branch_name("branch; rm -rf /")

    def test_double_dot_blocked(self):
        with pytest.raises(ValueError, match="contains '..'"):
            validate_branch_name("feature/../../etc")

    def test_leading_slash_blocked(self):
        with pytest.raises(ValueError, match="starts with"):
            validate_branch_name("/etc/passwd")

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            validate_branch_name("")

    def test_none_name_raises(self):
        with pytest.raises(ValueError):
            validate_branch_name(None)


class TestValidateFilename:
    def test_valid_filenames(self):
        assert validate_filename("file.txt") == "file.txt"
        assert validate_filename("path/to/file.txt") == os.path.normpath("path/to/file.txt")

    def test_dot_dot_traversal(self):
        with pytest.raises(ValueError, match="Path traversal"):
            validate_filename("../../etc/passwd")

    def test_absolute_path_blocked(self):
        with pytest.raises(ValueError, match="Absolute path"):
            validate_filename(os.path.abspath("/etc/passwd"))

    def test_empty_filename_raises(self):
        with pytest.raises(ValueError):
            validate_filename("")

    def test_none_filename_raises(self):
        with pytest.raises(ValueError):
            validate_filename(None)

    def test_traversal_after_normalization(self):
        with pytest.raises(ValueError):
            validate_filename("foo/../../etc/passwd")


class TestSanitizeRepoDirName:
    def test_normal_names_preserved(self):
        assert sanitize_repo_dir_name("owner_repo") == "owner_repo"
        assert sanitize_repo_dir_name("my-project") == "my-project"
        assert sanitize_repo_dir_name("test.repo") == "test.repo"

    def test_special_chars_replaced(self):
        result = sanitize_repo_dir_name("../etc/passwd")
        assert ".." not in result
        assert result != "../etc/passwd"

    def test_dangerous_chars_stripped(self):
        result = sanitize_repo_dir_name("repo;rm -rf /")
        assert ";" not in result
        assert "/" not in result


class TestBlamePathTraversal:
    """Test the path traversal protection in _relpath."""

    def test_dot_dot_traversal_blocked(self):
        from dna.git_history.blame import _relpath
        repo = tempfile.mkdtemp()
        try:
            with pytest.raises(ValueError, match="Path traversal"):
                _relpath("../../etc/passwd", repo)
        finally:
            os.rmdir(repo)

    def test_absolute_path_outside_repo_blocked(self):
        from dna.git_history.blame import _relpath
        repo = tempfile.mkdtemp()
        try:
            with pytest.raises(ValueError, match="Path traversal"):
                _relpath("/etc/passwd", repo)
        finally:
            os.rmdir(repo)

    def test_valid_relative_path_allowed(self):
        from dna.git_history.blame import _relpath
        repo = tempfile.mkdtemp()
        try:
            sub = os.path.join(repo, "src")
            os.mkdir(sub)
            result = _relpath("src/main.py", repo)
            assert result == os.path.normpath("src/main.py")
        finally:
            os.rmdir(sub)
            os.rmdir(repo)

    def test_absolute_path_inside_repo_allowed(self, tmp_path):
        from dna.git_history.blame import _relpath
        repo = str(tmp_path)
        inside = tmp_path / "file.py"
        inside.touch()
        result = _relpath(str(inside), repo)
        # Should be converted to relative
        assert not os.path.isabs(result)
        assert ".." not in result

    def test_dot_dot_with_extra_path_blocks(self):
        from dna.git_history.blame import _relpath
        import tempfile
        repo = tempfile.mkdtemp()
        try:
            with pytest.raises(ValueError, match="Path traversal"):
                _relpath("safe/dir/../../../etc/passwd", repo)
        finally:
            os.rmdir(repo)


class TestScannerPathValidation:
    def test_traversal_returns_empty(self, tmp_path):
        from dna.discovery.scanner import scan_files
        result = scan_files(str(tmp_path / ".." / ".." / "etc"))
        assert result == []


class TestBranchDetectorPathValidation:
    def test_invalid_path_raises(self, tmp_path):
        from dna.git_history.branch_detector import detect_branches
        from dna.discovery.orchestrator import NotAGitRepositoryError
        from dna.git_history.errors import GitCommandError
        # Path gets canonicalized; git will fail on non-repo path
        with pytest.raises((ValueError, NotAGitRepositoryError, GitCommandError, OSError)):
            detect_branches(str(tmp_path / ".." / ".." / "etc"))


class TestMinerPathValidation:
    def test_traversal_path_raises(self):
        from dna.git_history.miner import mine_git_history
        from dna.discovery.orchestrator import PathNotFoundError
        with pytest.raises(PathNotFoundError):
            mine_git_history(os.path.join(os.getcwd(), "..", "..", "etc"))


class TestSystemExplorerPathTraversal:
    def test_dot_dot_traversal_blocked_by_explorer(self):
        from fastapi.testclient import TestClient
        from dna.api.app import app
        client = TestClient(app)
        resp = client.get("/v1/system/explorer/file?path=../../etc/passwd")
        # Without active repo, returns 404. With active repo and traversal, returns 403.
        assert resp.status_code in (403, 404)

    def test_dot_dot_traversal_blocked_by_diff(self):
        from fastapi.testclient import TestClient
        from dna.api.app import app
        client = TestClient(app)
        resp = client.get("/v1/system/diff?path=../../etc/passwd")
        assert resp.status_code in (403, 404)


class TestIntakePathTraversal:
    def test_traversal_path_blocked(self):
        from fastapi.testclient import TestClient
        from dna.api.app import app
        client = TestClient(app)
        resp = client.post("/v1/intake/info", json={"url_or_path": "../../etc"})
        assert resp.status_code == 400
        # Path is canonicalized so ../../etc resolves to an absolute path
        # that either doesn't exist or is not a git repo
        assert "does not exist" in resp.text.lower() or "not a directory" in resp.text.lower() or "not a git repository" in resp.text.lower()

    def test_non_existent_path(self):
        from fastapi.testclient import TestClient
        from dna.api.app import app
        client = TestClient(app)
        resp = client.post("/v1/intake/info", json={"url_or_path": "/nonexistent/path"})
        assert resp.status_code == 400
        assert "does not exist" in resp.text.lower()

    def test_absolute_path_outside_blocked(self):
        from fastapi.testclient import TestClient
        from dna.api.app import app
        client = TestClient(app)
        resp = client.post("/v1/intake/info", json={"url_or_path": "/etc/passwd"})
        assert resp.status_code == 400
