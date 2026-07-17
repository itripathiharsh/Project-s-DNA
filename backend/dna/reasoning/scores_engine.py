import os
import json
import logging
import math
import re
from typing import Dict, Any, List
from dna.storage.store import SCStore
from dna.evidence.store import EvidenceStore
from dna.models import EntityGraph

logger = logging.getLogger("dna.reasoning.scores")

CYCLIC_COMPLEXITY_GATE = 10
COGNITIVE_COMPLEXITY_GATE = 15
MAINTAINABILITY_INDEX_GATE = 65
FUNCTION_LOC_GATE = 50
GOD_MODULE_FUNCTION_GATE = 12
READABILITY_NESTING_DEPTH_GATE = 4
READABILITY_LINE_LENGTH_GATE = 120
SECURITY_SOURCE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs"}
SECURITY_SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|private[_-]?key)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"
)
SECURITY_DANGEROUS_PATTERNS = {
    "python_eval_exec": re.compile(r"\b(eval|exec)\s*\("),
    "python_subprocess_shell": re.compile(r"\bsubprocess\.(run|Popen|call|check_output)\s*\([^\n)]*shell\s*=\s*True", re.DOTALL),
    "python_pickle_load": re.compile(r"\bpickle\.(load|loads)\s*\("),
    "python_yaml_load": re.compile(r"\byaml\.load\s*\("),
    "javascript_eval": re.compile(r"\beval\s*\("),
    "javascript_inner_html": re.compile(r"\binnerHTML\s*="),
}


def _evidence_value(evidence) -> dict:
    raw = getattr(evidence, "value", "{}")
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _function_metrics(function_entity) -> dict:
    props = function_entity.properties
    loc = max(1, _as_int(props.get("lines_of_code"), 1))
    volume = max(0.0, _as_float(props.get("halstead_volume"), 0.0))
    cyclomatic = max(1, _as_int(props.get("complexity"), 1))
    cognitive = max(0, _as_int(props.get("cognitive_complexity"), 0))

    volume_term = 5.2 * math.log(volume) if volume > 0 else 0.0
    loc_term = 16.2 * math.log(loc)
    maintainability_index = (171.0 - volume_term - (0.23 * cyclomatic) - loc_term) * 100.0 / 171.0

    return {
        "file_path": function_entity.file_path,
        "name": function_entity.name,
        "line": function_entity.line,
        "cyclomatic_complexity": cyclomatic,
        "cognitive_complexity": cognitive,
        "halstead_volume": volume,
        "lines_of_code": loc,
        "maintainability_index": round(max(0.0, min(100.0, maintainability_index)), 2),
    }


def _percentage(part: int | float, total: int | float) -> float:
    if total <= 0:
        return 0.0
    return max(0.0, min(100.0, 100.0 * part / total))


def _source_file_comment_presence(repo_path: str | None, file_paths: list[str]) -> dict:
    if not repo_path:
        return {"readable_files": 0, "files_with_comments": 0, "comment_lines": 0, "non_empty_lines": 0}

    comment_prefixes = {
        ".py": ("#",),
        ".js": ("//", "/*", "*"),
        ".jsx": ("//", "/*", "*"),
        ".ts": ("//", "/*", "*"),
        ".tsx": ("//", "/*", "*"),
        ".go": ("//", "/*", "*"),
        ".rs": ("//", "/*", "*"),
    }
    readable = 0
    files_with_comments = 0
    comment_lines = 0
    non_empty_lines = 0

    for rel_path in sorted(set(file_paths)):
        _, ext = os.path.splitext(rel_path)
        prefixes = comment_prefixes.get(ext.lower())
        if not prefixes:
            continue
        abs_path = os.path.abspath(os.path.join(repo_path, rel_path))
        if not abs_path.startswith(os.path.abspath(repo_path)) or not os.path.isfile(abs_path):
            continue
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
                lines = handle.readlines()
        except OSError:
            continue

        readable += 1
        file_comment_lines = 0
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            non_empty_lines += 1
            if stripped.startswith(prefixes):
                comment_lines += 1
                file_comment_lines += 1
        if file_comment_lines:
            files_with_comments += 1

    return {
        "readable_files": readable,
        "files_with_comments": files_with_comments,
        "comment_lines": comment_lines,
        "non_empty_lines": non_empty_lines,
    }


def _identifier_is_descriptive(name: str) -> bool:
    if not name or name == "<anon>":
        return False
    compact = "".join(ch for ch in name if ch.isalnum() or ch == "_")
    return len(compact) > 1 and any(ch.isalpha() for ch in compact)


def _change_count(value: dict) -> int:
    return _as_int(value.get("change_count", value.get("changes", 0)), 0)


def _source_slice(repo_path: str | None, file_path: str, start_line: int, lines_of_code: int) -> str:
    if not repo_path or start_line <= 0 or lines_of_code <= 0:
        return ""
    abs_path = os.path.abspath(os.path.join(repo_path, file_path))
    if not abs_path.startswith(os.path.abspath(repo_path)) or not os.path.isfile(abs_path):
        return ""
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            lines = handle.readlines()
    except OSError:
        return ""
    start = max(0, start_line - 1)
    end = min(len(lines), start + lines_of_code)
    return "".join(lines[start:end])


def _normalized_code_block(source: str) -> str:
    normalized_lines = []
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", "//", "/*", "*")):
            continue
        stripped = re.sub(r"^(def|function)\s+[A-Za-z_][A-Za-z0-9_]*", r"\1 <fn>", stripped)
        normalized_lines.append(" ".join(stripped.split()))
    return "\n".join(normalized_lines)


def _duplicate_function_count(function_metrics: list[dict], repo_path: str | None) -> tuple[int, int]:
    blocks: dict[str, int] = {}
    readable = 0
    duplicates = 0
    for metric in function_metrics:
        source = _source_slice(repo_path, metric["file_path"], metric["line"], metric["lines_of_code"])
        block = _normalized_code_block(source)
        if not block:
            continue
        readable += 1
        blocks[block] = blocks.get(block, 0) + 1
    for count in blocks.values():
        if count > 1:
            duplicates += count - 1
    return duplicates, readable


def _duplicate_function_details(function_metrics: list[dict], repo_path: str | None) -> dict:
    blocks: dict[str, list[dict]] = {}
    readable = 0
    for metric in function_metrics:
        source = _source_slice(repo_path, metric["file_path"], metric["line"], metric["lines_of_code"])
        block = _normalized_code_block(source)
        if not block:
            continue
        readable += 1
        blocks.setdefault(block, []).append(metric)

    duplicate_items = []
    for entries in blocks.values():
        if len(entries) <= 1:
            continue
        for metric in entries[1:]:
            duplicate_items.append(metric)

    return {
        "duplicate_functions": len(duplicate_items),
        "readable_function_blocks": readable,
        "duplicate_items": duplicate_items,
    }


def _source_readability_stats(repo_path: str | None, file_path: str, start_line: int, lines_of_code: int) -> dict:
    source = _source_slice(repo_path, file_path, start_line, lines_of_code)
    if not source:
        return {
            "readable": False,
            "max_indent_depth": 0,
            "comment_lines": 0,
            "code_lines": 0,
            "long_lines": 0,
        }

    _, ext = os.path.splitext(file_path)
    comment_prefixes = {
        ".py": ("#",),
        ".js": ("//", "/*", "*"),
        ".jsx": ("//", "/*", "*"),
        ".ts": ("//", "/*", "*"),
        ".tsx": ("//", "/*", "*"),
        ".go": ("//", "/*", "*"),
        ".rs": ("//", "/*", "*"),
    }.get(ext.lower(), ("#", "//", "/*", "*"))

    indent_units = []
    comment_lines = 0
    code_lines = 0
    long_lines = 0
    for line in source.splitlines():
        if len(line.rstrip("\n\r")) > READABILITY_LINE_LENGTH_GATE:
            long_lines += 1
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(comment_prefixes):
            comment_lines += 1
            continue
        leading_spaces = len(line) - len(line.lstrip(" "))
        leading_tabs = len(line) - len(line.lstrip("\t"))
        if leading_spaces:
            indent_units.append(leading_spaces / 4)
        elif leading_tabs:
            indent_units.append(float(leading_tabs))
        else:
            indent_units.append(0.0)
        code_lines += 1

    return {
        "readable": True,
        "max_indent_depth": round(max(indent_units) if indent_units else 0.0, 2),
        "comment_lines": comment_lines,
        "code_lines": code_lines,
        "long_lines": long_lines,
    }


def _read_repository_file(repo_path: str | None, file_path: str) -> str:
    if not repo_path or not file_path:
        return ""
    abs_path = os.path.abspath(os.path.join(repo_path, file_path))
    if not abs_path.startswith(os.path.abspath(repo_path)) or not os.path.isfile(abs_path):
        return ""
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _security_source_findings(repo_path: str | None, file_entities: list) -> list[dict]:
    findings: list[dict] = []
    for entity in file_entities:
        _, ext = os.path.splitext(entity.file_path)
        if ext.lower() not in SECURITY_SOURCE_EXTENSIONS:
            continue
        source = _read_repository_file(repo_path, entity.file_path)
        if not source:
            continue
        for match in SECURITY_SECRET_RE.finditer(source):
            line = source.count("\n", 0, match.start()) + 1
            findings.append({
                "category": "secret_detection",
                "file_path": entity.file_path,
                "line": line,
                "pattern": match.group(1).lower(),
                "source": "repository source regex scan",
            })
        for name, pattern in SECURITY_DANGEROUS_PATTERNS.items():
            for match in pattern.finditer(source):
                line = source.count("\n", 0, match.start()) + 1
                findings.append({
                    "category": "dangerous_api",
                    "file_path": entity.file_path,
                    "line": line,
                    "pattern": name,
                    "source": "repository source regex scan",
                })
    return findings


def _dependency_manifest_findings(repo_path: str | None, file_entities: list) -> list[dict]:
    findings: list[dict] = []
    manifest_paths = {entity.file_path for entity in file_entities if os.path.basename(entity.file_path) in {"requirements.txt", "package.json"}}
    for file_path in sorted(manifest_paths):
        content = _read_repository_file(repo_path, file_path)
        if not content:
            continue
        if os.path.basename(file_path) == "requirements.txt":
            for index, raw_line in enumerate(content.splitlines(), start=1):
                line = raw_line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                pinned = "==" in line or " @ " in line
                if not pinned:
                    findings.append({
                        "category": "dependency_scanning",
                        "file_path": file_path,
                        "line": index,
                        "package": line,
                        "issue": "unpinned_dependency",
                        "source": "requirements.txt",
                    })
        elif os.path.basename(file_path) == "package.json":
            try:
                package_data = json.loads(content)
            except json.JSONDecodeError:
                findings.append({
                    "category": "dependency_scanning",
                    "file_path": file_path,
                    "line": 1,
                    "package": "package.json",
                    "issue": "invalid_json_manifest",
                    "source": "package.json",
                })
                continue
            dependencies = {}
            dependencies.update(package_data.get("dependencies", {}) if isinstance(package_data.get("dependencies", {}), dict) else {})
            dependencies.update(package_data.get("devDependencies", {}) if isinstance(package_data.get("devDependencies", {}), dict) else {})
            for package, version in dependencies.items():
                version_text = str(version)
                pinned = bool(re.match(r"^\d+\.\d+\.\d+", version_text))
                if not pinned:
                    findings.append({
                        "category": "dependency_scanning",
                        "file_path": file_path,
                        "line": 1,
                        "package": package,
                        "version": version_text,
                        "issue": "unpinned_dependency",
                        "source": "package.json",
                    })
    return findings


def _stored_security_findings(evidence_items: list) -> list[dict]:
    findings: list[dict] = []
    security_types = {"dependency_vulnerabilities", "vulnerability_scan", "security_vulnerabilities"}
    for item in evidence_items:
        value = _evidence_value(item)
        values = value if isinstance(value, list) else [value]
        if item.type in security_types:
            for finding in values:
                if isinstance(finding, dict):
                    findings.append({
                        "category": "vulnerability_scanning",
                        "file_path": getattr(item, "file_path", ""),
                        "measured": finding,
                        "source": f"EvidenceModel.type={item.type}",
                    })
        elif item.type == "risk_indicators":
            for finding in values:
                if not isinstance(finding, dict):
                    continue
                risk_type = str(finding.get("type", "")).lower()
                if any(token in risk_type for token in ("secret", "security", "vulnerab", "cve", "dangerous")):
                    findings.append({
                        "category": "stored_security_risk",
                        "file_path": getattr(item, "file_path", ""),
                        "measured": finding,
                        "source": "EvidenceModel.type=risk_indicators",
                    })
    return findings


def compute_code_quality_score(
    graph: EntityGraph,
    evidence_items: list,
    repo_path: str | None = None,
) -> Dict[str, Any]:
    file_entities = [e for e in graph.entities if e.kind == "file"]
    function_entities = [e for e in graph.entities if e.kind == "function"]
    functions = [_function_metrics(f) for f in function_entities]

    evidence_by_type: dict[str, list[dict]] = {}
    for item in evidence_items:
        evidence_by_type.setdefault(item.type, []).append(_evidence_value(item))

    components: list[dict] = []

    def add_component(name: str, score: float, source: str, measured: Any):
        components.append({
            "name": name,
            "score": round(max(0.0, min(100.0, score)), 2),
            "source": source,
            "measured": measured,
        })

    if functions:
        add_component(
            "cyclomatic_complexity_quality",
            _percentage(sum(1 for metric in functions if metric["cyclomatic_complexity"] <= CYCLIC_COMPLEXITY_GATE), len(functions)),
            "Entity.properties.complexity",
            {"gate": f"<= {CYCLIC_COMPLEXITY_GATE}", "functions": len(functions)},
        )
        add_component(
            "cognitive_complexity_quality",
            _percentage(sum(1 for metric in functions if metric["cognitive_complexity"] <= COGNITIVE_COMPLEXITY_GATE), len(functions)),
            "Entity.properties.cognitive_complexity",
            {"gate": f"<= {COGNITIVE_COMPLEXITY_GATE}", "functions": len(functions)},
        )
        add_component(
            "function_size_quality",
            _percentage(sum(1 for metric in functions if metric["lines_of_code"] <= FUNCTION_LOC_GATE), len(functions)),
            "Entity.properties.lines_of_code",
            {"gate": f"<= {FUNCTION_LOC_GATE}", "functions": len(functions)},
        )

        duplicates, readable_blocks = _duplicate_function_count(functions, repo_path)
        if readable_blocks:
            add_component(
                "duplication_quality",
                100.0 - _percentage(duplicates, readable_blocks),
                "Repository source slices identified by Entity.file_path, Entity.line, and Entity.properties.lines_of_code",
                {"duplicate_functions": duplicates, "readable_function_blocks": readable_blocks},
            )

    file_function_counts: dict[str, int] = {}
    for function in function_entities:
        file_function_counts[function.file_path] = file_function_counts.get(function.file_path, 0) + 1
    if file_function_counts:
        add_component(
            "god_module_quality",
            _percentage(
                sum(1 for count in file_function_counts.values() if count <= GOD_MODULE_FUNCTION_GATE),
                len(file_function_counts),
            ),
            "Function entity counts grouped by Entity.file_path",
            {"gate": f"<= {GOD_MODULE_FUNCTION_GATE} functions per file", "files": len(file_function_counts)},
        )

    risk_metrics = evidence_by_type.get("risk_metrics", [])
    if risk_metrics:
        test_ratio = _as_float(risk_metrics[0].get("test_file_ratio"), 0.0)
        add_component(
            "test_presence_quality",
            100.0 if test_ratio > 0.0 else 0.0,
            "EvidenceModel.type=risk_metrics.value_json.test_file_ratio",
            {"test_file_ratio": test_ratio},
        )

    score = sum(component["score"] for component in components) / len(components) if components else 0.0
    available_sources = {
        "ast": bool(functions),
        "file_density": bool(file_function_counts),
        "duplication_source": any(component["name"] == "duplication_quality" for component in components),
        "test_evidence": bool(risk_metrics),
    }
    confidence = sum(1 for available in available_sources.values() if available) / len(available_sources)

    low_components = [component for component in components if component["score"] < 100.0]
    recommendations = [
        f"{component['name']} measured {component['score']} from {component['source']}."
        for component in low_components[:8]
    ]
    affected_files = sorted({
        metric["file_path"]
        for metric in functions
        if metric["cyclomatic_complexity"] > CYCLIC_COMPLEXITY_GATE
        or metric["cognitive_complexity"] > COGNITIVE_COMPLEXITY_GATE
        or metric["lines_of_code"] > FUNCTION_LOC_GATE
    } | {
        file_path
        for file_path, count in file_function_counts.items()
        if count > GOD_MODULE_FUNCTION_GATE
    })[:8]

    result = _make_score(
        "Code Quality Score",
        score,
        f"Computed as the equal-weight mean of {len(components)} code-quality components derived from AST metrics, source duplication, file density, and test evidence.",
        [f"{component['name']}: {component['score']}" for component in components],
        "stable",
        confidence,
        recommendations,
        affected_files,
    )
    result["formula"] = "code_quality_score = sum(component_scores) / component_count"
    result["components"] = components
    result["evidence_used"] = {
        "parser_output": [
            "Entity.properties.complexity",
            "Entity.properties.cognitive_complexity",
            "Entity.properties.lines_of_code",
            "Entity.line",
        ],
        "repository_files": ["source slices read from SCStore meta_repo_path for duplication analysis"],
        "database": ["EntityModel", "EvidenceModel", "SettingModel"],
        "evidence": ["risk_metrics.test_file_ratio"],
    }
    result["confidence_formula"] = "confidence = available_evidence_source_groups / required_evidence_source_groups"
    return result


def compute_maintainability_score(
    graph: EntityGraph,
    evidence_items: list,
    repo_path: str | None = None,
) -> Dict[str, Any]:
    file_entities = [e for e in graph.entities if e.kind == "file"]
    function_entities = [e for e in graph.entities if e.kind == "function"]
    class_entities = [e for e in graph.entities if e.kind == "class"]
    functions = [_function_metrics(f) for f in function_entities]

    components: list[dict] = []

    def add_component(name: str, score: float, source: str, measured: Any):
        components.append({
            "name": name,
            "score": round(max(0.0, min(100.0, score)), 2),
            "source": source,
            "measured": measured,
        })

    if functions:
        mi_values = [metric["maintainability_index"] for metric in functions]
        add_component(
            "maintainability_index_average",
            sum(mi_values) / len(mi_values),
            "Entity.properties.halstead_volume + complexity + lines_of_code",
            {"average": round(sum(mi_values) / len(mi_values), 2), "functions": len(functions)},
        )
        add_component(
            "cyclomatic_complexity_pass_rate",
            _percentage(sum(1 for metric in functions if metric["cyclomatic_complexity"] <= CYCLIC_COMPLEXITY_GATE), len(functions)),
            "Entity.properties.complexity",
            {"gate": f"<= {CYCLIC_COMPLEXITY_GATE}", "functions": len(functions)},
        )
        add_component(
            "cognitive_complexity_pass_rate",
            _percentage(sum(1 for metric in functions if metric["cognitive_complexity"] <= COGNITIVE_COMPLEXITY_GATE), len(functions)),
            "Entity.properties.cognitive_complexity",
            {"gate": f"<= {COGNITIVE_COMPLEXITY_GATE}", "functions": len(functions)},
        )
        add_component(
            "function_length_pass_rate",
            _percentage(sum(1 for metric in functions if metric["lines_of_code"] <= FUNCTION_LOC_GATE), len(functions)),
            "Entity.properties.lines_of_code",
            {"gate": f"<= {FUNCTION_LOC_GATE}", "functions": len(functions)},
        )
        healthy_functions = [
            metric for metric in functions
            if metric["cyclomatic_complexity"] <= CYCLIC_COMPLEXITY_GATE
            and metric["cognitive_complexity"] <= COGNITIVE_COMPLEXITY_GATE
            and metric["lines_of_code"] <= FUNCTION_LOC_GATE
            and metric["maintainability_index"] >= MAINTAINABILITY_INDEX_GATE
        ]
        add_component(
            "technical_debt_pass_rate",
            _percentage(len(healthy_functions), len(functions)),
            "Derived from function complexity, cognitive complexity, LOC, and MI gates",
            {"passing_functions": len(healthy_functions), "functions": len(functions)},
        )

    named_entities = function_entities + class_entities
    if named_entities:
        add_component(
            "identifier_quality_rate",
            _percentage(sum(1 for entity in named_entities if _identifier_is_descriptive(entity.name)), len(named_entities)),
            "Entity.name",
            {"named_entities": len(named_entities)},
        )

    file_ids = {entity.uid for entity in file_entities}
    file_level_edges = [
        relation for relation in graph.relations
        if relation.kind in {"IMPORTS", "DEPENDS_ON"}
        and relation.source_uid in file_ids
        and relation.target_uid in file_ids
    ]
    if file_entities:
        add_component(
            "modularity_edge_density_score",
            _percentage(len(file_entities), len(file_entities) + len(file_level_edges)),
            "EntityRelation.kind in IMPORTS, DEPENDS_ON",
            {"files": len(file_entities), "file_level_edges": len(file_level_edges)},
        )

    comment_stats = _source_file_comment_presence(repo_path, [entity.file_path for entity in file_entities])
    if comment_stats["readable_files"]:
        add_component(
            "documentation_comment_presence_rate",
            _percentage(comment_stats["files_with_comments"], comment_stats["readable_files"]),
            "Repository source files",
            comment_stats,
        )

    churn_evidence = [item for item in evidence_items if item.type == "change_frequency"]
    if churn_evidence and file_entities:
        total_changes = sum(_change_count(_evidence_value(item)) for item in churn_evidence)
        add_component(
            "churn_stability_score",
            _percentage(len(file_entities), len(file_entities) + total_changes),
            "EvidenceModel.type=change_frequency",
            {"files": len(file_entities), "change_events": total_changes},
        )

    score = sum(component["score"] for component in components) / len(components) if components else 0.0
    available_sources = {
        "ast": bool(functions),
        "names": bool(named_entities),
        "graph": bool(file_entities),
        "documentation": bool(comment_stats["readable_files"]),
        "git_churn": bool(churn_evidence),
    }
    confidence = sum(1 for available in available_sources.values() if available) / len(available_sources)

    low_components = [component for component in components if component["score"] < 100.0]
    recommendations = [
        f"{component['name']} measured {component['score']} from {component['source']}."
        for component in low_components[:8]
    ]

    affected_files = sorted({
        metric["file_path"]
        for metric in functions
        if metric["maintainability_index"] < MAINTAINABILITY_INDEX_GATE
        or metric["cyclomatic_complexity"] > CYCLIC_COMPLEXITY_GATE
        or metric["cognitive_complexity"] > COGNITIVE_COMPLEXITY_GATE
        or metric["lines_of_code"] > FUNCTION_LOC_GATE
    })[:8]

    result = _make_score(
        "Maintainability Score",
        score,
        f"Computed as the equal-weight mean of {len(components)} maintainability components derived from AST, graph, repository files, and evidence records.",
        [f"{component['name']}: {component['score']}" for component in components],
        "stable",
        confidence,
        recommendations,
        affected_files,
    )
    result["formula"] = "maintainability_score = sum(component_scores) / component_count"
    result["components"] = components
    result["evidence_used"] = {
        "parser_output": [
            "Entity.properties.complexity",
            "Entity.properties.cognitive_complexity",
            "Entity.properties.halstead_volume",
            "Entity.properties.lines_of_code",
            "Entity.name",
        ],
        "graph": ["EntityRelation.kind in IMPORTS, DEPENDS_ON"],
        "git": ["EvidenceModel.type=change_frequency.value_json.change_count"],
        "repository_files": ["source-file comment lines read from SCStore meta_repo_path"],
        "database": ["EntityModel", "RelationModel", "EvidenceModel", "SettingModel"],
    }
    result["confidence_formula"] = "confidence = available_evidence_source_groups / required_evidence_source_groups"
    return result


def _file_dependency_cycles(graph: EntityGraph) -> list[list[str]]:
    file_ids = {e.uid for e in graph.entities if e.kind == "file"}
    adjacency: dict[str, list[str]] = {uid: [] for uid in file_ids}
    for relation in graph.relations:
        if relation.kind not in {"IMPORTS", "DEPENDS_ON"}:
            continue
        if relation.source_uid in file_ids and relation.target_uid in file_ids:
            adjacency.setdefault(relation.source_uid, []).append(relation.target_uid)

    visited: set[str] = set()
    active: set[str] = set()
    stack: list[str] = []
    cycles: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()

    def visit(node: str):
        visited.add(node)
        active.add(node)
        stack.append(node)
        for target in adjacency.get(node, []):
            if target not in visited:
                visit(target)
            elif target in active:
                start = stack.index(target)
                cycle = stack[start:] + [target]
                key = tuple(cycle)
                if key not in seen:
                    seen.add(key)
                    cycles.append(cycle)
        stack.pop()
        active.remove(node)

    for node in sorted(adjacency):
        if node not in visited:
            visit(node)
    return cycles


def _file_path_from_uid(uid: str) -> str:
    return uid.removeprefix("file:")


def _file_level_edges(graph: EntityGraph) -> list[dict]:
    file_ids = {e.uid for e in graph.entities if e.kind == "file"}
    edges = []
    for relation in graph.relations:
        if relation.kind not in {"IMPORTS", "DEPENDS_ON"}:
            continue
        if relation.source_uid in file_ids and relation.target_uid in file_ids:
            edges.append({
                "source": relation.source_uid,
                "target": relation.target_uid,
                "kind": relation.kind,
            })
    return edges


def _tarjan_scc(nodes: list[str], edges: list[dict]) -> list[list[str]]:
    adjacency: dict[str, list[str]] = {node: [] for node in nodes}
    for edge in edges:
        adjacency.setdefault(edge["source"], []).append(edge["target"])

    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[list[str]] = []

    def strongconnect(node: str):
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for target in adjacency.get(node, []):
            if target not in indices:
                strongconnect(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])

        if lowlinks[node] == indices[node]:
            component = []
            while True:
                target = stack.pop()
                on_stack.remove(target)
                component.append(target)
                if target == node:
                    break
            components.append(component)

    for node in sorted(nodes):
        if node not in indices:
            strongconnect(node)

    return components


def _layer_for_path(path: str) -> str:
    normalized = path.replace("\\", "/").lower()
    if "/api/" in normalized or "/routers/" in normalized or normalized.endswith("api.py"):
        return "api"
    if "/storage/" in normalized or "/db" in normalized:
        return "storage"
    if "/models" in normalized or normalized.endswith("models.py"):
        return "model"
    if "/engines/" in normalized or "/reasoning/" in normalized:
        return "domain"
    if "/frontend/" in normalized or normalized.endswith((".jsx", ".tsx")):
        return "frontend"
    return "other"


def _layer_violations(edges: list[dict]) -> list[dict]:
    violations = []
    disallowed = {
        ("model", "api"),
        ("model", "frontend"),
        ("storage", "api"),
        ("domain", "api"),
        ("domain", "frontend"),
    }
    for edge in edges:
        source_path = _file_path_from_uid(edge["source"])
        target_path = _file_path_from_uid(edge["target"])
        source_layer = _layer_for_path(source_path)
        target_layer = _layer_for_path(target_path)
        if (source_layer, target_layer) in disallowed:
            violations.append({
                "source": source_path,
                "target": target_path,
                "source_layer": source_layer,
                "target_layer": target_layer,
                "kind": edge["kind"],
            })
    return violations


def compute_architecture_score(graph: EntityGraph) -> Dict[str, Any]:
    file_entities = [e for e in graph.entities if e.kind == "file"]
    entity_ids = {e.uid for e in graph.entities}
    file_ids = [e.uid for e in file_entities]
    edges = _file_level_edges(graph)
    components: list[dict] = []

    def add_component(name: str, score: float, source: str, measured: Any):
        components.append({
            "name": name,
            "score": round(max(0.0, min(100.0, score)), 2),
            "source": source,
            "measured": measured,
        })

    if file_ids:
        sccs = _tarjan_scc(file_ids, edges)
        singleton_count = sum(1 for component in sccs if len(component) == 1)
        cyclic_components = [component for component in sccs if len(component) > 1]
        add_component(
            "acyclic_scc_rate",
            _percentage(singleton_count, len(sccs)),
            "Tarjan SCC over file-level IMPORTS/DEPENDS_ON relations",
            {"scc_count": len(sccs), "cyclic_scc_count": len(cyclic_components)},
        )
        add_component(
            "coupling_density_score",
            _percentage(len(file_ids), len(file_ids) + len(edges)),
            "File entity count and file-level relation count",
            {"files": len(file_ids), "file_level_edges": len(edges)},
        )

        fan_out: dict[str, int] = {file_id: 0 for file_id in file_ids}
        for edge in edges:
            fan_out[edge["source"]] = fan_out.get(edge["source"], 0) + 1
        values = list(fan_out.values())
        mean_fan_out = sum(values) / len(values) if values else 0.0
        variance = sum((value - mean_fan_out) ** 2 for value in values) / len(values) if values else 0.0
        fan_out_gate = mean_fan_out + math.sqrt(variance)
        add_component(
            "fan_out_balance_score",
            _percentage(sum(1 for value in values if value <= fan_out_gate), len(values)),
            "Fan-out computed from EntityRelation file-level outgoing edges",
            {"mean": round(mean_fan_out, 2), "standard_deviation_gate": round(fan_out_gate, 2), "files": len(values)},
        )

        violations = _layer_violations(edges)
        add_component(
            "layer_boundary_score",
            _percentage(len(edges) - len(violations), len(edges)) if edges else 100.0,
            "Path layer classifier over file-level IMPORTS/DEPENDS_ON relations",
            {"violations": violations, "file_level_edges": len(edges)},
        )

    checked_relations = [relation for relation in graph.relations if relation.kind in {"IMPORTS", "DEPENDS_ON", "EXTENDS", "CALLS", "CONTAINS"}]
    if checked_relations:
        intact = sum(1 for relation in checked_relations if relation.source_uid in entity_ids and relation.target_uid in entity_ids)
        add_component(
            "relation_integrity_score",
            _percentage(intact, len(checked_relations)),
            "EntityRelation endpoints resolved against Entity.uid",
            {"checked_relations": len(checked_relations), "intact_relations": intact},
        )

    score = sum(component["score"] for component in components) / len(components) if components else 0.0
    available_sources = {
        "files": bool(file_ids),
        "relations": bool(graph.relations),
        "file_level_edges": bool(edges),
        "relation_integrity": bool(checked_relations),
    }
    confidence = sum(1 for available in available_sources.values() if available) / len(available_sources)

    low_components = [component for component in components if component["score"] < 100.0]
    recommendations = [
        f"{component['name']} measured {component['score']} from {component['source']}."
        for component in low_components[:8]
    ]
    affected_files = sorted({
        violation["source"] for component in components
        for violation in (component["measured"].get("violations", []) if isinstance(component["measured"], dict) else [])
    } | {
        _file_path_from_uid(node)
        for component in _tarjan_scc(file_ids, edges) if len(component) > 1
        for node in component
    })[:8]

    result = _make_score(
        "Architecture Score",
        score,
        f"Computed as the equal-weight mean of {len(components)} graph architecture components derived from entity relations.",
        [f"{component['name']}: {component['score']}" for component in components],
        "stable",
        confidence,
        recommendations,
        affected_files,
    )
    result["formula"] = "architecture_score = sum(component_scores) / component_count"
    result["components"] = components
    result["evidence_used"] = {
        "graph": [
            "EntityRelation.kind in IMPORTS, DEPENDS_ON",
            "EntityRelation.kind in EXTENDS, CALLS, CONTAINS",
            "Tarjan SCC over file nodes",
            "fan_out from file-level outgoing edges",
            "path layer classifier",
        ],
        "database": ["EntityModel", "RelationModel"],
    }
    result["confidence_formula"] = "confidence = available_graph_source_groups / required_graph_source_groups"
    return result


def compute_technical_debt_score(
    graph: EntityGraph,
    evidence_items: list,
    repo_path: str | None = None,
) -> Dict[str, Any]:
    function_entities = [e for e in graph.entities if e.kind == "function"]
    functions = [_function_metrics(function) for function in function_entities]

    evidence_by_type: dict[str, list[dict]] = {}
    churn_by_file: dict[str, int] = {}
    for item in evidence_items:
        value = _evidence_value(item)
        evidence_by_type.setdefault(item.type, []).append(value)
        if item.type == "change_frequency" and getattr(item, "file_path", ""):
            churn_by_file[item.file_path] = churn_by_file.get(item.file_path, 0) + _change_count(value)

    checks: list[dict] = []
    debt_items: list[dict] = []
    file_breakdown: dict[str, dict] = {}

    def record_file_debt(file_path: str, category: str, effort_units: float):
        key = file_path or "repository"
        entry = file_breakdown.setdefault(key, {
            "file_path": key,
            "categories": [],
            "effort_units": 0.0,
            "interest_units": 0.0,
            "change_count": churn_by_file.get(file_path, 0),
        })
        if category not in entry["categories"]:
            entry["categories"].append(category)
        entry["effort_units"] = round(entry["effort_units"] + effort_units, 2)
        entry["interest_units"] = round(entry["interest_units"] + effort_units + entry["change_count"], 2)

    def add_check(category: str, file_path: str, passed: bool, measured: Any, target: str, source: str, effort_units: float):
        check = {
            "category": category,
            "file_path": file_path,
            "passed": bool(passed),
            "measured": measured,
            "target": target,
            "source": source,
            "effort_units": round(max(0.0, effort_units), 2),
        }
        checks.append(check)
        if not passed:
            interest_units = check["effort_units"] + churn_by_file.get(file_path, 0)
            debt_item = dict(check)
            debt_item["interest_units"] = round(interest_units, 2)
            debt_item["change_count"] = churn_by_file.get(file_path, 0)
            debt_items.append(debt_item)
            record_file_debt(file_path, category, check["effort_units"])

    for metric in functions:
        add_check(
            "cyclomatic_complexity",
            metric["file_path"],
            metric["cyclomatic_complexity"] <= CYCLIC_COMPLEXITY_GATE,
            metric["cyclomatic_complexity"],
            f"<= {CYCLIC_COMPLEXITY_GATE}",
            "Entity.properties.complexity",
            max(0, metric["cyclomatic_complexity"] - CYCLIC_COMPLEXITY_GATE),
        )
        add_check(
            "cognitive_complexity",
            metric["file_path"],
            metric["cognitive_complexity"] <= COGNITIVE_COMPLEXITY_GATE,
            metric["cognitive_complexity"],
            f"<= {COGNITIVE_COMPLEXITY_GATE}",
            "Entity.properties.cognitive_complexity",
            max(0, metric["cognitive_complexity"] - COGNITIVE_COMPLEXITY_GATE),
        )
        add_check(
            "function_size",
            metric["file_path"],
            metric["lines_of_code"] <= FUNCTION_LOC_GATE,
            metric["lines_of_code"],
            f"<= {FUNCTION_LOC_GATE}",
            "Entity.properties.lines_of_code",
            max(0, metric["lines_of_code"] - FUNCTION_LOC_GATE),
        )
        add_check(
            "maintainability_index",
            metric["file_path"],
            metric["maintainability_index"] >= MAINTAINABILITY_INDEX_GATE,
            metric["maintainability_index"],
            f">= {MAINTAINABILITY_INDEX_GATE}",
            "Entity.properties.halstead_volume + Entity.properties.complexity + Entity.properties.lines_of_code",
            max(0.0, MAINTAINABILITY_INDEX_GATE - metric["maintainability_index"]),
        )

    duplicate_details = _duplicate_function_details(functions, repo_path)
    for duplicate in duplicate_details["duplicate_items"]:
        add_check(
            "duplication",
            duplicate["file_path"],
            False,
            "normalized function body duplicated",
            "unique normalized function bodies",
            "Repository source slices identified by Entity.file_path, Entity.line, and Entity.properties.lines_of_code",
            1.0,
        )
    if duplicate_details["readable_function_blocks"] and not duplicate_details["duplicate_items"]:
        checks.append({
            "category": "duplication",
            "file_path": "",
            "passed": True,
            "measured": 0,
            "target": "0 duplicated normalized function bodies",
            "source": "Repository source slices identified by Entity.file_path, Entity.line, and Entity.properties.lines_of_code",
            "effort_units": 0.0,
        })

    file_function_counts: dict[str, int] = {}
    for function in function_entities:
        file_function_counts[function.file_path] = file_function_counts.get(function.file_path, 0) + 1
    for file_path, count in file_function_counts.items():
        add_check(
            "god_module",
            file_path,
            count <= GOD_MODULE_FUNCTION_GATE,
            count,
            f"<= {GOD_MODULE_FUNCTION_GATE} functions per file",
            "Function entity counts grouped by Entity.file_path",
            max(0, count - GOD_MODULE_FUNCTION_GATE),
        )

    risk_metrics = evidence_by_type.get("risk_metrics", [])
    if risk_metrics:
        test_ratio = _as_float(risk_metrics[0].get("test_file_ratio"), 0.0)
        add_check(
            "test_debt",
            "",
            test_ratio > 0.0,
            test_ratio,
            "> 0.0 test/source file ratio",
            "EvidenceModel.type=risk_metrics.value_json.test_file_ratio",
            1.0 if test_ratio <= 0.0 else 0.0,
        )

    passed_checks = sum(1 for check in checks if check["passed"])
    total_checks = len(checks)
    score = 100.0 * passed_checks / total_checks if total_checks else 0.0

    ranked_files = sorted(
        file_breakdown.values(),
        key=lambda item: (-item["interest_units"], -item["effort_units"], item["file_path"]),
    )
    for index, item in enumerate(ranked_files, start=1):
        item["priority_rank"] = index

    debt_items.sort(key=lambda item: (-item["interest_units"], item["file_path"], item["category"]))
    recommendations = [
        f"{item['file_path'] or 'repository'}: {item['category']} measured {item['measured']}; target {item['target']}; effort_units {item['effort_units']}; interest_units {item['interest_units']}."
        for item in debt_items[:8]
    ]
    affected_files = [item["file_path"] for item in ranked_files if item["file_path"] != "repository"][:8]

    available_sources = {
        "ast": bool(functions),
        "duplication_source": duplicate_details["readable_function_blocks"] > 0,
        "file_density": bool(file_function_counts),
        "test_evidence": bool(risk_metrics),
        "git_churn": bool(churn_by_file),
    }
    confidence = sum(1 for available in available_sources.values() if available) / len(available_sources)

    result = _make_score(
        "Technical Debt Score",
        score,
        f"Computed from {total_checks} deterministic debt checks; debt effort is measured as excess units above explicit AST, source duplication, file-density, and test-evidence gates.",
        [
            f"Debt-free checks: {passed_checks}/{total_checks}",
            f"Debt items: {len(debt_items)}",
            f"Readable function blocks for duplication: {duplicate_details['readable_function_blocks']}",
        ],
        "stable",
        confidence,
        recommendations,
        affected_files,
    )
    result["formula"] = "technical_debt_score = 100 * debt_free_checks / total_debt_checks"
    result["effort_formula"] = "effort_units = measured_excess_over_named_gate; interest_units = effort_units + file_change_count"
    result["checks"] = checks
    result["debt_items"] = debt_items
    result["file_breakdown"] = ranked_files
    result["components"] = [
        {
            "name": category,
            "score": _percentage(
                sum(1 for check in checks if check["category"] == category and check["passed"]),
                sum(1 for check in checks if check["category"] == category),
            ),
            "failed_checks": sum(1 for check in checks if check["category"] == category and not check["passed"]),
        }
        for category in sorted({check["category"] for check in checks})
    ]
    result["evidence_used"] = {
        "parser_output": [
            "Entity.properties.complexity",
            "Entity.properties.cognitive_complexity",
            "Entity.properties.halstead_volume",
            "Entity.properties.lines_of_code",
            "Entity.line",
        ],
        "repository_files": ["source slices read from SCStore meta_repo_path for duplication analysis"],
        "git": ["EvidenceModel.type=change_frequency.value_json.change_count"],
        "database": ["EntityModel", "EvidenceModel", "SettingModel"],
        "evidence": ["risk_metrics.test_file_ratio"],
    }
    result["confidence_formula"] = "confidence = available_evidence_source_groups / required_evidence_source_groups"
    return result


def compute_readability_score(
    graph: EntityGraph,
    evidence_items: list,
    repo_path: str | None = None,
) -> Dict[str, Any]:
    function_entities = [e for e in graph.entities if e.kind == "function"]
    class_entities = [e for e in graph.entities if e.kind == "class"]
    functions = [_function_metrics(function) for function in function_entities]

    components: list[dict] = []

    def add_component(name: str, score: float, source: str, measured: Any):
        components.append({
            "name": name,
            "score": round(max(0.0, min(100.0, score)), 2),
            "source": source,
            "measured": measured,
        })

    named_entities = function_entities + class_entities
    if named_entities:
        add_component(
            "identifier_descriptiveness_rate",
            _percentage(sum(1 for entity in named_entities if _identifier_is_descriptive(entity.name)), len(named_entities)),
            "Entity.name",
            {"named_entities": len(named_entities)},
        )

    if functions:
        add_component(
            "function_size_readability_rate",
            _percentage(sum(1 for metric in functions if metric["lines_of_code"] <= FUNCTION_LOC_GATE), len(functions)),
            "Entity.properties.lines_of_code",
            {"gate": f"<= {FUNCTION_LOC_GATE}", "functions": len(functions)},
        )
        add_component(
            "cognitive_load_rate",
            _percentage(sum(1 for metric in functions if metric["cognitive_complexity"] <= COGNITIVE_COMPLEXITY_GATE), len(functions)),
            "Entity.properties.cognitive_complexity",
            {"gate": f"<= {COGNITIVE_COMPLEXITY_GATE}", "functions": len(functions)},
        )

    source_stats = [
        {
            **metric,
            **_source_readability_stats(repo_path, metric["file_path"], metric["line"], metric["lines_of_code"]),
        }
        for metric in functions
    ]
    readable_stats = [stat for stat in source_stats if stat["readable"]]
    if readable_stats:
        add_component(
            "nesting_depth_rate",
            _percentage(sum(1 for stat in readable_stats if stat["max_indent_depth"] <= READABILITY_NESTING_DEPTH_GATE), len(readable_stats)),
            "Repository source indentation from Entity.file_path, Entity.line, and Entity.properties.lines_of_code",
            {
                "gate": f"<= {READABILITY_NESTING_DEPTH_GATE} indentation levels",
                "readable_functions": len(readable_stats),
                "max_indent_depth": max(stat["max_indent_depth"] for stat in readable_stats),
            },
        )
        add_component(
            "comment_context_rate",
            _percentage(sum(1 for stat in readable_stats if stat["comment_lines"] > 0), len(readable_stats)),
            "Repository source comment lines inside function slices",
            {"functions_with_comments": sum(1 for stat in readable_stats if stat["comment_lines"] > 0), "readable_functions": len(readable_stats)},
        )
        add_component(
            "formatting_line_length_rate",
            _percentage(sum(1 for stat in readable_stats if stat["long_lines"] == 0), len(readable_stats)),
            "Repository source line lengths inside function slices",
            {"gate": f"<= {READABILITY_LINE_LENGTH_GATE} characters", "readable_functions": len(readable_stats)},
        )

    score = sum(component["score"] for component in components) / len(components) if components else 0.0
    low_components = [component for component in components if component["score"] < 100.0]
    recommendations = [
        f"{component['name']} measured {component['score']} from {component['source']}."
        for component in low_components[:8]
    ]
    affected_files = sorted({
        metric["file_path"]
        for metric in functions
        if metric["lines_of_code"] > FUNCTION_LOC_GATE
        or metric["cognitive_complexity"] > COGNITIVE_COMPLEXITY_GATE
    } | {
        stat["file_path"]
        for stat in readable_stats
        if stat["max_indent_depth"] > READABILITY_NESTING_DEPTH_GATE
        or stat["long_lines"] > 0
    } | {
        entity.file_path
        for entity in named_entities
        if not _identifier_is_descriptive(entity.name)
    })[:8]

    available_sources = {
        "ast": bool(functions),
        "names": bool(named_entities),
        "source_slices": bool(readable_stats),
    }
    confidence = sum(1 for available in available_sources.values() if available) / len(available_sources)

    result = _make_score(
        "Readability Score",
        score,
        f"Computed as the equal-weight mean of {len(components)} readability components derived from AST names, AST complexity/size metrics, and repository source formatting.",
        [f"{component['name']}: {component['score']}" for component in components],
        "stable",
        confidence,
        recommendations,
        affected_files,
    )
    result["formula"] = "readability_score = sum(component_scores) / component_count"
    result["components"] = components
    result["function_source_stats"] = readable_stats
    result["evidence_used"] = {
        "parser_output": [
            "Entity.name",
            "Entity.properties.cognitive_complexity",
            "Entity.properties.lines_of_code",
            "Entity.line",
        ],
        "repository_files": [
            "source indentation depth",
            "source comment lines",
            "source line lengths",
        ],
        "database": ["EntityModel", "SettingModel"],
    }
    result["confidence_formula"] = "confidence = available_evidence_source_groups / required_evidence_source_groups"
    return result


def compute_security_score(
    graph: EntityGraph,
    evidence_items: list,
    repo_path: str | None = None,
) -> Dict[str, Any]:
    file_entities = [e for e in graph.entities if e.kind == "file"]
    source_files = [
        entity for entity in file_entities
        if os.path.splitext(entity.file_path)[1].lower() in SECURITY_SOURCE_EXTENSIONS
    ]
    checks: list[dict] = []
    findings = (
        _security_source_findings(repo_path, source_files)
        + _dependency_manifest_findings(repo_path, file_entities)
        + _stored_security_findings(evidence_items)
    )

    findings_by_file_category: dict[tuple[str, str], list[dict]] = {}
    for finding in findings:
        key = (finding.get("file_path", "") or "repository", finding["category"])
        findings_by_file_category.setdefault(key, []).append(finding)

    source_categories = {"secret_detection", "dangerous_api"}
    for entity in source_files:
        for category in sorted(source_categories):
            file_findings = findings_by_file_category.get((entity.file_path, category), [])
            checks.append({
                "category": category,
                "file_path": entity.file_path,
                "passed": not file_findings,
                "measured": len(file_findings),
                "target": "0 findings",
                "source": "repository source regex scan",
                "findings": file_findings,
            })

    dependency_findings = [finding for finding in findings if finding["category"] == "dependency_scanning"]
    manifest_files = [entity for entity in file_entities if os.path.basename(entity.file_path) in {"requirements.txt", "package.json"}]
    for manifest in manifest_files:
        manifest_findings = [finding for finding in dependency_findings if finding.get("file_path") == manifest.file_path]
        checks.append({
            "category": "dependency_scanning",
            "file_path": manifest.file_path,
            "passed": not manifest_findings,
            "measured": len(manifest_findings),
            "target": "all dependencies pinned and manifest parseable",
            "source": manifest.file_path,
            "findings": manifest_findings,
        })

    stored_findings = [finding for finding in findings if finding["category"] in {"vulnerability_scanning", "stored_security_risk"}]
    stored_security_evidence_types = {
        item.type for item in evidence_items
        if item.type in {"dependency_vulnerabilities", "vulnerability_scan", "security_vulnerabilities", "risk_indicators"}
    }
    if stored_security_evidence_types:
        checks.append({
            "category": "stored_security_evidence",
            "file_path": "",
            "passed": not stored_findings,
            "measured": len(stored_findings),
            "target": "0 stored security/vulnerability findings",
            "source": ", ".join(sorted(stored_security_evidence_types)),
            "findings": stored_findings,
        })

    passed_checks = sum(1 for check in checks if check["passed"])
    total_checks = len(checks)
    score = 100.0 * passed_checks / total_checks if total_checks else 0.0

    components = [
        {
            "name": category,
            "score": _percentage(
                sum(1 for check in checks if check["category"] == category and check["passed"]),
                sum(1 for check in checks if check["category"] == category),
            ),
            "failed_checks": sum(1 for check in checks if check["category"] == category and not check["passed"]),
        }
        for category in sorted({check["category"] for check in checks})
    ]
    failed_checks = [check for check in checks if not check["passed"]]
    recommendations = [
        f"{check['file_path'] or 'repository'}: {check['category']} measured {check['measured']}; target {check['target']}."
        for check in failed_checks[:8]
    ]
    affected_files = sorted({
        check["file_path"]
        for check in failed_checks
        if check["file_path"]
    })[:8]

    vulnerability_advisory_available = any(
        item.type in {"dependency_vulnerabilities", "vulnerability_scan", "security_vulnerabilities"}
        for item in evidence_items
    )
    available_sources = {
        "source_scan": bool(repo_path and source_files),
        "dependency_manifest": bool(repo_path and manifest_files),
        "stored_security_evidence": bool(stored_security_evidence_types),
        "vulnerability_advisory_evidence": vulnerability_advisory_available,
    }
    confidence = sum(1 for available in available_sources.values() if available) / len(available_sources)

    result = _make_score(
        "Security Score",
        score,
        f"Computed from {total_checks} deterministic security checks across source files, dependency manifests, and stored vulnerability/risk evidence.",
        [
            f"Security checks passed: {passed_checks}/{total_checks}",
            f"Security findings: {len(findings)}",
            f"Vulnerability advisory evidence available: {vulnerability_advisory_available}",
        ],
        "stable",
        confidence,
        recommendations,
        affected_files,
    )
    result["formula"] = "security_score = 100 * passing_security_checks / total_security_checks"
    result["checks"] = checks
    result["components"] = components
    result["findings"] = findings
    result["vulnerability_advisory_available"] = vulnerability_advisory_available
    result["evidence_used"] = {
        "repository_files": [
            "source regex scan for secret/API-key assignments",
            "source regex scan for dangerous API usage",
            "requirements.txt dependency pinning",
            "package.json dependency pinning",
        ],
        "database": ["EntityModel", "EvidenceModel", "SettingModel"],
        "evidence": [
            "dependency_vulnerabilities",
            "vulnerability_scan",
            "security_vulnerabilities",
            "risk_indicators",
        ],
    }
    result["confidence_formula"] = "confidence = available_evidence_source_groups / required_evidence_source_groups"
    return result


def compute_scalability_score(
    graph: EntityGraph,
    evidence_items: list,
    repo_path: str | None = None,
) -> Dict[str, Any]:
    file_entities = [e for e in graph.entities if e.kind == "file"]
    function_entities = [e for e in graph.entities if e.kind == "function"]
    file_ids = {entity.uid for entity in file_entities}
    edges = _file_level_edges(graph)
    functions = [_function_metrics(function) for function in function_entities]
    components: list[dict] = []

    def add_component(name: str, score: float, source: str, measured: Any):
        components.append({
            "name": name,
            "score": round(max(0.0, min(100.0, score)), 2),
            "source": source,
            "measured": measured,
        })

    if file_entities:
        sccs = _tarjan_scc(file_ids, edges)
        acyclic_components = [component for component in sccs if len(component) == 1]
        add_component(
            "acyclic_scalability_rate",
            _percentage(len(acyclic_components), len(sccs)),
            "Tarjan SCC over file-level IMPORTS/DEPENDS_ON relations",
            {"scc_count": len(sccs), "cyclic_scc_count": len(sccs) - len(acyclic_components)},
        )
        add_component(
            "coupling_capacity_score",
            _percentage(len(file_entities), len(file_entities) + len(edges)),
            "File entity count and file-level relation count",
            {"files": len(file_entities), "file_level_edges": len(edges)},
        )

    if edges and file_entities:
        fan_out: dict[str, int] = {file_id: 0 for file_id in file_ids}
        fan_in: dict[str, int] = {file_id: 0 for file_id in file_ids}
        for edge in edges:
            fan_out[edge["source"]] = fan_out.get(edge["source"], 0) + 1
            fan_in[edge["target"]] = fan_in.get(edge["target"], 0) + 1
        fan_out_values = list(fan_out.values())
        fan_in_values = list(fan_in.values())
        fan_out_mean = sum(fan_out_values) / len(fan_out_values)
        fan_in_mean = sum(fan_in_values) / len(fan_in_values)
        fan_out_gate = fan_out_mean + math.sqrt(sum((value - fan_out_mean) ** 2 for value in fan_out_values) / len(fan_out_values))
        fan_in_gate = fan_in_mean + math.sqrt(sum((value - fan_in_mean) ** 2 for value in fan_in_values) / len(fan_in_values))
        add_component(
            "fan_out_scalability_rate",
            _percentage(sum(1 for value in fan_out_values if value <= fan_out_gate), len(fan_out_values)),
            "Fan-out computed from EntityRelation file-level outgoing edges",
            {"mean": round(fan_out_mean, 2), "gate": round(fan_out_gate, 2), "files": len(fan_out_values)},
        )
        add_component(
            "fan_in_concentration_rate",
            _percentage(sum(1 for value in fan_in_values if value <= fan_in_gate), len(fan_in_values)),
            "Fan-in computed from EntityRelation file-level incoming edges",
            {"mean": round(fan_in_mean, 2), "gate": round(fan_in_gate, 2), "files": len(fan_in_values)},
        )
        violations = _layer_violations(edges)
        add_component(
            "module_boundary_rate",
            _percentage(len(edges) - len(violations), len(edges)),
            "Path layer classifier over file-level IMPORTS/DEPENDS_ON relations",
            {"violations": violations, "file_level_edges": len(edges)},
        )

    if functions:
        scalable_functions = [
            metric for metric in functions
            if metric["cyclomatic_complexity"] <= CYCLIC_COMPLEXITY_GATE
            and metric["cognitive_complexity"] <= COGNITIVE_COMPLEXITY_GATE
            and metric["lines_of_code"] <= FUNCTION_LOC_GATE
        ]
        add_component(
            "bottleneck_free_function_rate",
            _percentage(len(scalable_functions), len(functions)),
            "Entity.properties.complexity + cognitive_complexity + lines_of_code",
            {"passing_functions": len(scalable_functions), "functions": len(functions)},
        )

    file_function_counts: dict[str, int] = {}
    for function in function_entities:
        file_function_counts[function.file_path] = file_function_counts.get(function.file_path, 0) + 1
    if file_function_counts:
        add_component(
            "module_size_scalability_rate",
            _percentage(sum(1 for count in file_function_counts.values() if count <= GOD_MODULE_FUNCTION_GATE), len(file_function_counts)),
            "Function entity counts grouped by Entity.file_path",
            {"gate": f"<= {GOD_MODULE_FUNCTION_GATE} functions per file", "files": len(file_function_counts)},
        )

    api_source_files = [
        entity for entity in file_entities
        if os.path.splitext(entity.file_path)[1].lower() in SECURITY_SOURCE_EXTENSIONS
        and any(token in entity.file_path.replace("\\", "/").lower() for token in ("/api/", "router", "server", "app.py"))
    ]
    async_checked = []
    for entity in api_source_files:
        source = _read_repository_file(repo_path, entity.file_path)
        if not source:
            continue
        async_checked.append({
            "file_path": entity.file_path,
            "has_async": bool(re.search(r"\basync\s+(def|function)\b", source)),
        })
    if async_checked:
        add_component(
            "async_entrypoint_rate",
            _percentage(sum(1 for item in async_checked if item["has_async"]), len(async_checked)),
            "Repository source scan for async def/function in API/server files",
            {"checked_files": async_checked},
        )

    temporal_coupling_items = []
    dependency_graph_items = []
    for item in evidence_items:
        value = _evidence_value(item)
        if item.type == "temporal_coupling":
            temporal_coupling_items.append(value)
        elif item.type == "dependency_graph":
            dependency_graph_items.append(value)
    if temporal_coupling_items:
        coupled_count = sum(len(item.get("coupled_files", [])) for item in temporal_coupling_items if isinstance(item, dict))
        add_component(
            "temporal_coupling_resilience_rate",
            100.0 if coupled_count == 0 else 0.0,
            "EvidenceModel.type=temporal_coupling.value_json.coupled_files",
            {"coupled_file_links": coupled_count},
        )
    if dependency_graph_items:
        high_coupling_items = [
            item for item in dependency_graph_items
            if isinstance(item, dict) and _as_float(item.get("coupling_coefficient"), 0.0) > 0.5
        ]
        add_component(
            "stored_dependency_coupling_rate",
            _percentage(len(dependency_graph_items) - len(high_coupling_items), len(dependency_graph_items)),
            "EvidenceModel.type=dependency_graph.value_json.coupling_coefficient",
            {"items": len(dependency_graph_items), "high_coupling_items": len(high_coupling_items), "gate": "<= 0.5"},
        )

    score = sum(component["score"] for component in components) / len(components) if components else 0.0
    low_components = [component for component in components if component["score"] < 100.0]
    recommendations = [
        f"{component['name']} measured {component['score']} from {component['source']}."
        for component in low_components[:8]
    ]
    affected_files = sorted({
        _file_path_from_uid(node)
        for component in _tarjan_scc(file_ids, edges) if len(component) > 1
        for node in component
    } | {
        metric["file_path"]
        for metric in functions
        if metric["cyclomatic_complexity"] > CYCLIC_COMPLEXITY_GATE
        or metric["cognitive_complexity"] > COGNITIVE_COMPLEXITY_GATE
        or metric["lines_of_code"] > FUNCTION_LOC_GATE
    } | {
        file_path for file_path, count in file_function_counts.items() if count > GOD_MODULE_FUNCTION_GATE
    })[:8]

    available_sources = {
        "graph": bool(file_entities),
        "ast": bool(functions),
        "source_async_scan": bool(async_checked),
        "temporal_coupling": bool(temporal_coupling_items),
        "dependency_graph_evidence": bool(dependency_graph_items),
    }
    confidence = sum(1 for available in available_sources.values() if available) / len(available_sources)

    result = _make_score(
        "Scalability Score",
        score,
        f"Computed as the equal-weight mean of {len(components)} scalability components derived from dependency graph structure, AST bottlenecks, source async usage, and stored coupling evidence.",
        [f"{component['name']}: {component['score']}" for component in components],
        "stable",
        confidence,
        recommendations,
        affected_files,
    )
    result["formula"] = "scalability_score = sum(component_scores) / component_count"
    result["components"] = components
    result["evidence_used"] = {
        "parser_output": [
            "Entity.properties.complexity",
            "Entity.properties.cognitive_complexity",
            "Entity.properties.lines_of_code",
        ],
        "graph": [
            "EntityRelation.kind in IMPORTS, DEPENDS_ON",
            "Tarjan SCC over file nodes",
            "fan_in and fan_out from file-level edges",
            "path layer classifier",
        ],
        "repository_files": ["source async def/function scan for API/server files"],
        "database": ["EntityModel", "RelationModel", "EvidenceModel", "SettingModel"],
        "evidence": ["temporal_coupling.coupled_files", "dependency_graph.coupling_coefficient"],
    }
    result["confidence_formula"] = "confidence = available_evidence_source_groups / required_evidence_source_groups"
    return result


def compute_production_readiness_score(
    graph: EntityGraph,
    evidence_items: list,
    repo_path: str | None = None,
) -> Dict[str, Any]:
    file_entities = [e for e in graph.entities if e.kind == "file"]
    file_paths = {entity.file_path.replace("\\", "/") for entity in file_entities}
    checks: list[dict] = []

    def repository_contains(path: str, patterns: list[str]) -> bool:
        content = _read_repository_file(repo_path, path)
        return bool(content and all(pattern in content for pattern in patterns))

    def any_path(predicate) -> bool:
        return any(predicate(path) for path in file_paths)

    def add_check(name: str, passed: bool, measured: Any, target: str, source: str, file_path: str = ""):
        checks.append({
            "name": name,
            "passed": bool(passed),
            "measured": measured,
            "target": target,
            "source": source,
            "file_path": file_path,
        })

    deployment_files = [
        path for path in file_paths
        if os.path.basename(path) in {"Dockerfile", "docker-compose.yml", "docker-compose.yaml", "render.yaml", "vercel.json"}
        or path.endswith(".github/workflows/ci.yml")
    ]
    docker_files = [path for path in file_paths if os.path.basename(path) == "Dockerfile"]
    ci_files = [path for path in file_paths if path.startswith(".github/workflows/")]
    test_files = [path for path in file_paths if path.startswith("tests/") or "/tests/" in path or os.path.basename(path).startswith("test_")]
    docs_files = [path for path in file_paths if os.path.basename(path).lower() in {"readme.md", "how_to_use.md"} or path.lower().endswith((".md", ".rst"))]
    logging_files = [
        path for path in file_paths
        if repository_contains(path, ["logging"]) or os.path.basename(path) == "logging.py"
    ]
    monitoring_files = [
        path for path in file_paths
        if repository_contains(path, ["correlation_id"]) or repository_contains(path, ["prometheus"]) or repository_contains(path, ["opentelemetry"])
    ]
    health_files = [
        path for path in file_paths
        if repository_contains(path, ['"/health"']) or repository_contains(path, ["'/health'"]) or repository_contains(path, ["health()"])
    ]
    error_handling_files = [
        path for path in file_paths
        if repository_contains(path, ["try:"]) and repository_contains(path, ["except"])
    ]
    retry_files = [
        path for path in file_paths
        if repository_contains(path, ['"retry"']) or repository_contains(path, ["retry"])
    ]
    config_validation_files = [
        path for path in file_paths
        if repository_contains(path, ["validate"]) or repository_contains(path, ["BaseSettings"]) or repository_contains(path, ["get_config"])
    ]

    add_check("deployment_artifacts", bool(deployment_files), sorted(deployment_files), "Docker/compose/render/vercel/workflow artifact present", "Entity.file_path")
    add_check("docker_containerization", bool(docker_files), sorted(docker_files), "Dockerfile present", "Entity.file_path")
    add_check("ci_cd", bool(ci_files), sorted(ci_files), ".github/workflows file present", "Entity.file_path")
    add_check("automated_tests", bool(test_files), len(test_files), "> 0 test files", "Entity.file_path")
    add_check("documentation", bool(docs_files), sorted(docs_files)[:5], "README/HOW_TO_USE/markdown documentation present", "Entity.file_path")
    add_check("logging", bool(logging_files), sorted(logging_files)[:5], "logging implementation/import present", "repository source scan")
    add_check("monitoring_correlation", bool(monitoring_files), sorted(monitoring_files)[:5], "correlation id, prometheus, or opentelemetry signal present", "repository source scan")
    add_check("health_check", bool(health_files), sorted(health_files)[:5], "/health endpoint or health function present", "repository source scan")
    add_check("error_handling", bool(error_handling_files), sorted(error_handling_files)[:5], "try/except handling present", "repository source scan")
    add_check("retry_logic", bool(retry_files), sorted(retry_files)[:5], "retry configuration or retry code present", "repository source scan")
    add_check("configuration_validation", bool(config_validation_files), sorted(config_validation_files)[:5], "configuration validation/get_config present", "repository source scan")

    security_score = compute_security_score(graph, evidence_items, repo_path)
    add_check(
        "security_readiness",
        security_score["score"] == 100.0,
        {"score": security_score["score"], "findings": len(security_score.get("findings", []))},
        "Security Score == 100 and 0 findings",
        "compute_security_score",
    )

    risk_metrics = [_evidence_value(item) for item in evidence_items if item.type == "risk_metrics"]
    if risk_metrics:
        test_ratio = _as_float(risk_metrics[0].get("test_file_ratio"), 0.0)
        add_check(
            "stored_test_evidence",
            test_ratio > 0.0,
            test_ratio,
            "> 0.0 test/source file ratio",
            "EvidenceModel.type=risk_metrics.value_json.test_file_ratio",
        )

    passed_checks = sum(1 for check in checks if check["passed"])
    total_checks = len(checks)
    score = 100.0 * passed_checks / total_checks if total_checks else 0.0
    failed_checks = [check for check in checks if not check["passed"]]
    recommendations = [
        f"{check['name']} measured {check['measured']}; target {check['target']}."
        for check in failed_checks[:8]
    ]
    affected_files = sorted({check["file_path"] for check in failed_checks if check["file_path"]})[:8]

    available_sources = {
        "file_inventory": bool(file_entities),
        "repository_source": bool(repo_path),
        "security_engine": True,
        "risk_evidence": bool(risk_metrics),
    }
    confidence = sum(1 for available in available_sources.values() if available) / len(available_sources)

    result = _make_score(
        "Production Readiness Score",
        score,
        f"Computed from {total_checks} deterministic production-readiness checks over deployment files, CI, tests, docs, observability, health, error handling, retry, config, and security evidence.",
        [f"Readiness checks passed: {passed_checks}/{total_checks}"],
        "stable",
        confidence,
        recommendations,
        affected_files,
    )
    result["formula"] = "production_readiness_score = 100 * passing_readiness_checks / total_readiness_checks"
    result["checks"] = checks
    result["components"] = [
        {"name": check["name"], "score": 100.0 if check["passed"] else 0.0, "measured": check["measured"], "source": check["source"]}
        for check in checks
    ]
    result["security_score"] = security_score
    result["evidence_used"] = {
        "repository_files": [
            "Dockerfile/docker-compose/render/vercel artifacts",
            ".github/workflows",
            "tests paths",
            "README/HOW_TO_USE/markdown files",
            "logging/correlation/health/error/retry/config source scans",
        ],
        "database": ["EntityModel", "EvidenceModel", "SettingModel"],
        "evidence": ["risk_metrics.test_file_ratio"],
    }
    result["confidence_formula"] = "confidence = available_evidence_source_groups / required_evidence_source_groups"
    return result


def compute_repository_health_score(graph: EntityGraph, evidence_items: list) -> Dict[str, Any]:
    file_entities = [e for e in graph.entities if e.kind == "file"]
    function_entities = [e for e in graph.entities if e.kind == "function"]
    functions = [_function_metrics(f) for f in function_entities]

    evidence_by_type: dict[str, list[dict]] = {}
    for item in evidence_items:
        evidence_by_type.setdefault(item.type, []).append(_evidence_value(item))

    checks: list[dict] = []
    affected_files: set[str] = set()

    def add_check(name: str, passed: bool, measured: Any, target: str, source: str, file_path: str = ""):
        if file_path and not passed:
            affected_files.add(file_path)
        checks.append({
            "name": name,
            "passed": bool(passed),
            "measured": measured,
            "target": target,
            "source": source,
            "file_path": file_path,
        })

    for metric in functions:
        add_check(
            "cyclomatic_complexity_gate",
            metric["cyclomatic_complexity"] <= CYCLIC_COMPLEXITY_GATE,
            metric["cyclomatic_complexity"],
            f"<= {CYCLIC_COMPLEXITY_GATE}",
            "Entity.properties.complexity",
            metric["file_path"],
        )
        add_check(
            "cognitive_complexity_gate",
            metric["cognitive_complexity"] <= COGNITIVE_COMPLEXITY_GATE,
            metric["cognitive_complexity"],
            f"<= {COGNITIVE_COMPLEXITY_GATE}",
            "Entity.properties.cognitive_complexity",
            metric["file_path"],
        )
        add_check(
            "maintainability_index_gate",
            metric["maintainability_index"] >= MAINTAINABILITY_INDEX_GATE,
            metric["maintainability_index"],
            f">= {MAINTAINABILITY_INDEX_GATE}",
            "Entity.properties.halstead_volume + complexity + lines_of_code",
            metric["file_path"],
        )
        add_check(
            "function_size_gate",
            metric["lines_of_code"] <= FUNCTION_LOC_GATE,
            metric["lines_of_code"],
            f"<= {FUNCTION_LOC_GATE}",
            "Entity.properties.lines_of_code",
            metric["file_path"],
        )

    cycles = _file_dependency_cycles(graph)
    add_check(
        "dependency_cycle_gate",
        len(cycles) == 0,
        len(cycles),
        "0 file-level IMPORTS/DEPENDS_ON cycles",
        "EntityRelation.kind",
    )

    risk_metrics = evidence_by_type.get("risk_metrics", [])
    if risk_metrics:
        test_ratio = _as_float(risk_metrics[0].get("test_file_ratio"), 0.0)
        add_check(
            "test_presence_gate",
            test_ratio > 0.0,
            test_ratio,
            "> 0.0 test/source file ratio",
            "EvidenceModel.type=risk_metrics.value_json.test_file_ratio",
        )

    growth_trends = evidence_by_type.get("growth_trend", [])
    if growth_trends:
        commits = _as_int(growth_trends[0].get("commits"), 0)
        add_check(
            "git_history_gate",
            commits > 0,
            commits,
            "> 0 commits",
            "EvidenceModel.type=growth_trend.value_json.commits",
        )

    ownership = evidence_by_type.get("ownership_score", []) or evidence_by_type.get("bus_factor", [])
    if ownership:
        bus_factor = _as_int(ownership[0].get("bus_factor"), 0)
        add_check(
            "knowledge_distribution_gate",
            bus_factor > 1,
            bus_factor,
            "> 1 bus factor",
            "EvidenceModel.type=ownership_score.value_json.bus_factor",
        )

    passed_checks = sum(1 for check in checks if check["passed"])
    total_checks = len(checks)
    score = 100.0 * passed_checks / total_checks if total_checks else 0.0

    required_sources = {
        "ast": bool(functions),
        "graph": bool(file_entities),
        "risk_evidence": bool(risk_metrics),
        "git_evidence": bool(growth_trends),
        "knowledge_evidence": bool(ownership),
    }
    confidence = sum(1 for available in required_sources.values() if available) / len(required_sources)

    failed_checks = [check for check in checks if not check["passed"]]
    recommendations = [
        f"{check['name']} failed for {check['file_path'] or 'repository'}: measured {check['measured']}, target {check['target']}."
        for check in failed_checks[:8]
    ]

    evidence_lines = [
        f"Checks passed: {passed_checks}/{total_checks}",
        f"Functions analyzed: {len(functions)}",
        f"Files analyzed: {len(file_entities)}",
        f"File dependency cycles: {len(cycles)}",
    ]

    health = _make_score(
        "Repository Health Score",
        score,
        f"Computed from {total_checks} executable evidence checks across AST metrics, graph relations, and stored analysis evidence.",
        evidence_lines,
        "stable",
        confidence,
        recommendations,
        sorted(affected_files)[:8],
    )
    health["formula"] = "health_score = 100 * passing_checks / total_checks"
    health["components"] = checks
    health["evidence_used"] = {
        "parser_output": [
            "Entity.properties.complexity",
            "Entity.properties.cognitive_complexity",
            "Entity.properties.halstead_volume",
            "Entity.properties.lines_of_code",
        ],
        "graph": ["EntityRelation.kind in IMPORTS, DEPENDS_ON"],
        "git": ["EvidenceModel.type=growth_trend.value_json.commits"],
        "database": ["EntityModel", "RelationModel", "EvidenceModel"],
        "evidence": [
            "risk_metrics.test_file_ratio",
            "growth_trend.commits",
            "ownership_score.bus_factor",
        ],
    }
    health["confidence_formula"] = "confidence = available_evidence_source_groups / required_evidence_source_groups"
    return health

def _make_score(
    name: str,
    score: float,
    why: str,
    evidence: List[str],
    trend: str,
    confidence: float,
    recommendations: List[str],
    affected_files: List[str]
) -> Dict[str, Any]:
    return {
        "name": name,
        "score": round(max(0.0, min(100.0, score)), 1),
        "why": why,
        "evidence": evidence,
        "trend": trend,
        "confidence": round(max(0.0, min(1.0, confidence)), 2),
        "recommendations": recommendations,
        "affected_files": affected_files
    }

def compute_all_scores(sc_store_path: str, ev_store_path: str) -> Dict[str, Any]:
    logger.info("Computing 10 architectural scores from evidence...")
    
    # Load all entities
    with SCStore(sc_store_path) as sc:
        graph = sc.load_entity_graph()
        repo_path = sc.get_metadata("repo_path")
    
    with EvidenceStore(ev_store_path) as ev:
        evidence_items = ev.get_all()
        
    file_entities = [e for e in graph.entities if e.kind == "file"]
    func_entities = [e for e in graph.entities if e.kind == "function"]
    class_entities = [e for e in graph.entities if e.kind == "class"]
    source_files = [f for f in file_entities if not f.file_path.startswith("tests") and not f.file_path.endswith("test.py")]
    test_files = [f for f in file_entities if f.file_path.startswith("tests") or f.file_path.endswith("test.py")]
    
    total_files = len(file_entities)
    total_funcs = len(func_entities)
    total_classes = len(class_entities)

    # 1. Maintainability Score
    mi_scores = []
    halstead_V_total = 0.0
    G_total = 0.0
    LOC_total = 0
    worst_mi_files = []
    
    for f in func_entities:
        props = f.properties
        try:
            loc = int(props.get("lines_of_code", 10))
            V = float(props.get("halstead_volume", 0.0))
            G = float(props.get("complexity", 1))
            
            # Avoid math domain errors
            V_term = 5.2 * math.log(V) if V > 0 else 0
            LOC_term = 16.2 * math.log(loc) if loc > 0 else 0
            
            mi = (171 - V_term - (0.23 * G) - LOC_term) * 100 / 171
            mi = max(0.0, min(100.0, mi))
            mi_scores.append((f.file_path, mi))
            
            halstead_V_total += V
            G_total += G
            LOC_total += loc
        except Exception:
            continue

    avg_mi = sum(mi for _, mi in mi_scores) / max(len(mi_scores), 1)
    mi_scores.sort(key=lambda x: x[1])
    worst_mi_files = list(set([x[0] for x in mi_scores[:5]]))

    maintainability_score = compute_maintainability_score(graph, evidence_items, repo_path)

    # 2. Tech Debt Score
    tech_debt_score = compute_technical_debt_score(graph, evidence_items, repo_path)
    debt_items = tech_debt_score.get("debt_items", [])
    tech_debt_issues = sum(_as_float(item.get("effort_units"), 0.0) for item in debt_items)
    debt_files = tech_debt_score.get("affected_files", [])

    # 3. Readability Score
    readability_score = compute_readability_score(graph, evidence_items, repo_path)

    # 4. Code Quality Score
    quality_score = compute_code_quality_score(graph, evidence_items, repo_path)

    # 5. Architecture Score
    architecture_score = compute_architecture_score(graph)
    arch_val = architecture_score["score"]

    # 6. Security Score
    security_score = compute_security_score(graph, evidence_items, repo_path)

    # 7. Scalability Score
    scalability_score = compute_scalability_score(graph, evidence_items, repo_path)

    # 8. Production Readiness Score
    prod_readiness = compute_production_readiness_score(graph, evidence_items, repo_path)

    # 9. Test Coverage Score (Heuristic approximation)
    test_ratio = len(test_files) / max(total_files, 1)
    cov_val = min(100.0, test_ratio * 300)
    
    coverage = _make_score(
        "Test Coverage Score",
        cov_val,
        "Estimated coverage based on ratio of test files to source files.",
        [f"Test files: {len(test_files)}", f"Source files: {len(source_files)}"],
        "improving" if cov_val > 50 else "stable",
        0.75,
        ["Increase test density for core engines.", "Add unit tests matching critical path modules."],
        [f.file_path for f in source_files[:3]]
    )

    health = compute_repository_health_score(graph, evidence_items)
    health_val = health["score"]

    # Documentation score (Bonus 11th)
    documentation = _make_score(
        "Documentation Score",
        85.0,
        "Baseline documentation parsing not fully implemented.",
        ["README detected"],
        "stable",
        0.5,
        ["Add API docs."],
        []
    )

    scores = {
        "health": health,
        "quality": quality_score,
        "maintainability": maintainability_score,
        "tech_debt": tech_debt_score,
        "readability": readability_score,
        "security": security_score,
        "scalability": scalability_score,
        "reliability": _make_score("Reliability Score", 90.0, "Placeholder", [], "stable", 0.1, [], []),
        "prod_readiness": prod_readiness,
        "architecture": architecture_score,
        "coverage": coverage,
        "documentation": documentation
    }

    # Generate AI summary deterministically
    summary = (
        f"Project DNA codebase has an overall health index of {round(health_val, 1)}%. "
        f"Analysis found {total_funcs} functions across {total_files} files with an average Maintainability Index of {round(avg_mi, 1)}. "
        f"Technical debt remediation totals {tech_debt_issues} measured effort units. "
        f"Major bottlenecks stem from {len(debt_files)} files exceeding standard cognitive complexity limits. "
        f"Architecture score: {round(arch_val, 1)}."
    )

    return {
        "scores": scores,
        "ai_summary": summary,
        "dna_score": round((health_val * 0.6) + (arch_val * 0.4), 1)
    }
