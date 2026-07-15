import os
from dna.models import BuildSystem

BUILD_SYSTEM_MAP: list[tuple[str, str]] = [
    ("package.json", "npm"),
    ("yarn.lock", "yarn"),
    ("pnpm-lock.yaml", "pnpm"),
    ("Cargo.toml", "Cargo"),
    ("pom.xml", "Maven"),
    ("build.gradle", "Gradle"),
    ("build.gradle.kts", "Gradle"),
    ("pyproject.toml", "pip"),
    ("setup.py", "pip"),
    ("requirements.txt", "pip"),
    ("Pipfile", "pipenv"),
    ("go.mod", "Go Modules"),
    ("Makefile", "Make"),
    ("CMakeLists.txt", "CMake"),
    ("tsconfig.json", "TypeScript"),
    ("Dockerfile", "Docker"),
    ("docker-compose.yml", "Docker Compose"),
    ("docker-compose.yaml", "Docker Compose"),
    ("composer.json", "Composer"),
    ("Gemfile", "Bundler"),
    ("mix.exs", "Mix"),
    ("rebar.config", "Rebar3"),
    ("workspace.json", "Nx"),
]


def detect_build_systems(path: str) -> list[BuildSystem]:
    if not os.path.isdir(path):
        return []

    detected: list[BuildSystem] = []
    for config_file, system_name in BUILD_SYSTEM_MAP:
        config_path = os.path.join(path, config_file)
        if os.path.isfile(config_path):
            detected.append(BuildSystem(
                name=system_name,
                config_file=config_file,
            ))

    return detected
