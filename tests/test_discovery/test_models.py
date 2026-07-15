from dna.models import RepositoryMetadata, BuildSystem, Framework, LanguageStats


def test_repository_metadata_defaults():
    m = RepositoryMetadata(name="test", path="/tmp/test", is_git=True)
    assert m.file_count == 0
    assert m.languages == []
    assert m.build_systems == []
    assert m.frameworks == []
    assert m.primary_language is None


def test_repository_metadata_to_json():
    m = RepositoryMetadata(
        name="test",
        path="/tmp/test",
        is_git=True,
        file_count=5,
        primary_language="Python",
        build_systems=[BuildSystem(name="pip", config_file="pyproject.toml")],
        frameworks=[Framework(name="FastAPI", category="backend", confidence=1.0)],
        languages=[LanguageStats(language="Python", file_count=5, total_bytes=1000, percentage=1.0)],
    )
    json_str = m.to_json()
    assert "Python" in json_str
    assert "pip" in json_str
    assert "FastAPI" in json_str


def test_repository_metadata_roundtrip():
    m1 = RepositoryMetadata(
        name="my-project",
        path="/home/user/my-project",
        is_git=True,
        file_count=42,
        primary_language="TypeScript",
        build_systems=[BuildSystem(name="npm", config_file="package.json")],
        frameworks=[Framework(name="React", category="frontend", confidence=1.0)],
        languages=[LanguageStats(language="TypeScript", file_count=30, total_bytes=90000, percentage=0.714)],
    )
    json_str = m1.to_json()
    m2 = RepositoryMetadata.from_json(json_str)
    assert m2.name == m1.name
    assert m2.path == m1.path
    assert m2.is_git == m1.is_git
    assert m2.file_count == m1.file_count
    assert m2.primary_language == m1.primary_language
    assert len(m2.build_systems) == 1
    assert m2.build_systems[0].name == "npm"
    assert len(m2.frameworks) == 1
    assert m2.frameworks[0].name == "React"


def test_build_system_defaults():
    bs = BuildSystem(name="pip", config_file="pyproject.toml")
    assert bs.version is None


def test_framework_fields():
    fw = Framework(name="React", category="frontend", confidence=1.0)
    assert fw.name == "React"
    assert fw.category == "frontend"
    assert fw.confidence == 1.0
