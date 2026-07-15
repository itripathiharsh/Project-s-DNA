import os
import subprocess
import tempfile
from dna.git_history.tag_mapper import map_tags


def _init_repo(path: str):
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=path, capture_output=True)


def _commit(path: str, msg: str = "init"):
    fpath = os.path.join(path, "f.txt")
    with open(fpath, "w") as f:
        f.write("x")
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=path, capture_output=True)


def test_map_tags_none():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir)
        tags = map_tags(tmpdir)
        assert tags == []


def test_map_tags_lightweight():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir)
        subprocess.run(["git", "tag", "v1.0.0"], cwd=tmpdir, capture_output=True)
        tags = map_tags(tmpdir)
        assert len(tags) == 1
        assert tags[0].name == "v1.0.0"
        assert len(tags[0].target_sha) == 40


def test_map_tags_annotated():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir)
        subprocess.run(
            ["git", "tag", "-a", "v2.0.0", "-m", "release v2"],
            cwd=tmpdir, capture_output=True,
        )
        tags = map_tags(tmpdir)
        assert len(tags) == 1
        assert tags[0].name == "v2.0.0"
        assert len(tags[0].target_sha) == 40


def test_map_tags_multiple():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        _commit(tmpdir)
        subprocess.run(["git", "tag", "v1.0.0"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "tag", "v1.1.0"], cwd=tmpdir, capture_output=True)
        tags = map_tags(tmpdir)
        assert len(tags) == 2
        names = {t.name for t in tags}
        assert names == {"v1.0.0", "v1.1.0"}


def test_map_tags_empty_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_repo(tmpdir)
        tags = map_tags(tmpdir)
        assert tags == []
