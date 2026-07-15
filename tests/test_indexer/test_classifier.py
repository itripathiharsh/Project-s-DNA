from dna.indexer.classifier import classify_file
from dna.models import FileInfo, RepositoryMetadata, FileCategory


_EMPTY_META = RepositoryMetadata(name="test", path="/test", is_git=True)


def _fi(path: str, ext: str = ".py") -> FileInfo:
    return FileInfo(
        path=path,
        relative_path=path,
        filename=path.split("/")[-1],
        extension=ext,
        language="",
        size_bytes=0,
        is_directory=False,
        is_source=True,
    )


def test_classifier_source():
    f = _fi("src/main.py")
    assert classify_file(f, _EMPTY_META) == FileCategory.SOURCE


def test_classifier_test_by_directory():
    f = _fi("tests/test_auth.py")
    assert classify_file(f, _EMPTY_META) == FileCategory.TEST


def test_classifier_test_by_prefix():
    f = _fi("src/test_auth.py")
    assert classify_file(f, _EMPTY_META) == FileCategory.TEST


def test_classifier_config_json():
    f = _fi("package.json", ".json")
    assert classify_file(f, _EMPTY_META) == FileCategory.CONFIG


def test_classifier_config_yaml():
    f = _fi("config/app.yaml", ".yaml")
    assert classify_file(f, _EMPTY_META) == FileCategory.CONFIG


def test_classifier_documentation():
    f = _fi("README.md", ".md")
    assert classify_file(f, _EMPTY_META) == FileCategory.DOCUMENTATION


def test_classifier_build_makefile():
    f = _fi("Makefile", "")
    assert classify_file(f, _EMPTY_META) == FileCategory.BUILD


def test_classifier_data():
    f = _fi("data.csv", ".csv")
    assert classify_file(f, _EMPTY_META) == FileCategory.DATA


def test_classifier_other():
    f = _fi("logo.png", ".png")
    assert classify_file(f, _EMPTY_META) == FileCategory.OTHER


def test_classifier_unknown_ext():
    f = _fi("file.xyz", ".xyz")
    assert classify_file(f, _EMPTY_META) == FileCategory.OTHER
