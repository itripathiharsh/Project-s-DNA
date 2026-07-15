import json
import os
import re
from dna.models import BuildSystem, Framework


FRAMEWORK_SIGNATURES: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r'fastapi', re.IGNORECASE), "FastAPI", "backend"),
    (re.compile(r'flask', re.IGNORECASE), "Flask", "backend"),
    (re.compile(r'django', re.IGNORECASE), "Django", "backend"),
    (re.compile(r'react', re.IGNORECASE), "React", "frontend"),
    (re.compile(r'vue', re.IGNORECASE), "Vue", "frontend"),
    (re.compile(r'next', re.IGNORECASE), "Next.js", "frontend"),
    (re.compile(r'@?angular', re.IGNORECASE), "Angular", "frontend"),
    (re.compile(r'express', re.IGNORECASE), "Express", "backend"),
    (re.compile(r'svelte', re.IGNORECASE), "Svelte", "frontend"),
    (re.compile(r'@sveltejs', re.IGNORECASE), "SvelteKit", "frontend"),
    (re.compile(r'nuxt', re.IGNORECASE), "Nuxt", "frontend"),
    (re.compile(r'gatsby', re.IGNORECASE), "Gatsby", "frontend"),
    (re.compile(r'spring-boot', re.IGNORECASE), "Spring Boot", "backend"),
    (re.compile(r'actix', re.IGNORECASE), "Actix", "backend"),
    (re.compile(r'rocket', re.IGNORECASE), "Rocket", "backend"),
    (re.compile(r'axum', re.IGNORECASE), "Axum", "backend"),
    (re.compile(r'tensorflow', re.IGNORECASE), "TensorFlow", "ml"),
    (re.compile(r'torch', re.IGNORECASE), "PyTorch", "ml"),
    (re.compile(r'pytest', re.IGNORECASE), "pytest", "testing"),
    (re.compile(r'jest', re.IGNORECASE), "Jest", "testing"),
    (re.compile(r'vitest', re.IGNORECASE), "Vitest", "testing"),
]


def _detect_from_package_json(path: str) -> list[Framework]:
    pkg_path = os.path.join(path, "package.json")
    if not os.path.isfile(pkg_path):
        return []

    try:
        with open(pkg_path, encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    frameworks: list[Framework] = []
    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

    for dep_name in deps:
        for pattern, name, category in FRAMEWORK_SIGNATURES:
            if pattern.match(dep_name):
                frameworks.append(Framework(name=name, category=category, confidence=1.0))
                break

    return frameworks


def _detect_from_pyproject_toml(path: str) -> list[Framework]:
    toml_path = os.path.join(path, "pyproject.toml")
    if not os.path.isfile(toml_path):
        return []

    try:
        with open(toml_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except OSError:
        return []

    frameworks: list[Framework] = []
    for pattern, name, category in FRAMEWORK_SIGNATURES:
        if pattern.search(content):
            frameworks.append(Framework(name=name, category=category, confidence=1.0))

    return frameworks


def detect_frameworks(path: str, build_systems: list[BuildSystem]) -> list[Framework]:
    seen: set[str] = set()
    result: list[Framework] = []

    for fw in _detect_from_package_json(path) + _detect_from_pyproject_toml(path):
        if fw.name not in seen:
            seen.add(fw.name)
            result.append(fw)

    return result
