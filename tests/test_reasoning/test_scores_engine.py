from dna.models import Entity, EntityGraph, EntityRelation, Evidence
from dna.reasoning.scores_engine import (
    compute_architecture_score,
    compute_code_quality_score,
    compute_maintainability_score,
    compute_readability_score,
    compute_repository_health_score,
    compute_security_score,
    compute_scalability_score,
    compute_technical_debt_score,
)


def _evidence(evidence_type, value):
    return Evidence(type=evidence_type, value=value)


def test_repository_health_uses_ast_graph_git_and_database_evidence():
    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:app.py", name="app.py", kind="file", file_path="app.py"))
    graph.add_entity(Entity(uid="file:tests/test_app.py", name="test_app.py", kind="file", file_path="tests/test_app.py"))
    graph.add_entity(Entity(
        uid="function:app.py:run",
        name="run",
        kind="function",
        file_path="app.py",
        line=3,
        properties={
            "complexity": "2",
            "cognitive_complexity": "1",
            "halstead_volume": "12",
            "lines_of_code": "6",
        },
    ))
    graph.add_relation(EntityRelation(source_uid="file:app.py", target_uid="function:app.py:run", kind="CONTAINS"))

    score = compute_repository_health_score(graph, [
        _evidence("risk_metrics", '{"test_file_ratio": 1.0}'),
        _evidence("growth_trend", '{"commits": 3}'),
        _evidence("ownership_score", '{"bus_factor": 2}'),
    ])

    assert score["score"] == 100.0
    assert score["confidence"] == 1.0
    assert score["formula"] == "health_score = 100 * passing_checks / total_checks"
    assert len(score["components"]) == 8
    assert all(component["passed"] for component in score["components"])
    assert score["evidence_used"]["database"] == ["EntityModel", "RelationModel", "EvidenceModel"]


def test_repository_health_reports_failed_checks_from_real_values():
    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:a.py", name="a.py", kind="file", file_path="a.py"))
    graph.add_entity(Entity(uid="file:b.py", name="b.py", kind="file", file_path="b.py"))
    graph.add_entity(Entity(
        uid="function:a.py:hard",
        name="hard",
        kind="function",
        file_path="a.py",
        line=10,
        properties={
            "complexity": "18",
            "cognitive_complexity": "30",
            "halstead_volume": "200000",
            "lines_of_code": "80",
        },
    ))
    graph.add_relation(EntityRelation(source_uid="file:a.py", target_uid="file:b.py", kind="IMPORTS"))
    graph.add_relation(EntityRelation(source_uid="file:b.py", target_uid="file:a.py", kind="IMPORTS"))

    score = compute_repository_health_score(graph, [])

    failed = [component for component in score["components"] if not component["passed"]]
    failed_names = {component["name"] for component in failed}

    assert score["score"] == 0.0
    assert score["confidence"] == 0.4
    assert failed_names == {
        "cyclomatic_complexity_gate",
        "cognitive_complexity_gate",
        "maintainability_index_gate",
        "function_size_gate",
        "dependency_cycle_gate",
    }
    assert "a.py" in score["affected_files"]
    assert score["recommendations"]


def test_maintainability_uses_ast_graph_churn_and_source_comments(tmp_path):
    source_file = tmp_path / "app.py"
    source_file.write_text("# module comment\n\ndef run(x):\n    return x\n", encoding="utf-8")

    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:app.py", name="app.py", kind="file", file_path="app.py"))
    graph.add_entity(Entity(
        uid="function:app.py:run",
        name="run",
        kind="function",
        file_path="app.py",
        line=3,
        properties={
            "complexity": "2",
            "cognitive_complexity": "1",
            "halstead_volume": "12",
            "lines_of_code": "6",
        },
    ))
    graph.add_relation(EntityRelation(source_uid="file:app.py", target_uid="function:app.py:run", kind="CONTAINS"))

    score = compute_maintainability_score(
        graph,
        [_evidence("change_frequency", '{"change_count": 0}')],
        repo_path=str(tmp_path),
    )

    component_names = {component["name"] for component in score["components"]}

    assert score["score"] > 90.0
    assert score["confidence"] == 1.0
    assert score["formula"] == "maintainability_score = sum(component_scores) / component_count"
    assert {
        "maintainability_index_average",
        "cyclomatic_complexity_pass_rate",
        "cognitive_complexity_pass_rate",
        "function_length_pass_rate",
        "technical_debt_pass_rate",
        "identifier_quality_rate",
        "modularity_edge_density_score",
        "documentation_comment_presence_rate",
        "churn_stability_score",
    } == component_names
    assert score["evidence_used"]["database"] == ["EntityModel", "RelationModel", "EvidenceModel", "SettingModel"]


def test_maintainability_reports_low_components_from_measured_values():
    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:a.py", name="a.py", kind="file", file_path="a.py"))
    graph.add_entity(Entity(uid="file:b.py", name="b.py", kind="file", file_path="b.py"))
    graph.add_entity(Entity(
        uid="function:a.py:x",
        name="x",
        kind="function",
        file_path="a.py",
        line=1,
        properties={
            "complexity": "25",
            "cognitive_complexity": "40",
            "halstead_volume": "500000",
            "lines_of_code": "120",
        },
    ))
    graph.add_relation(EntityRelation(source_uid="file:a.py", target_uid="file:b.py", kind="IMPORTS"))
    graph.add_relation(EntityRelation(source_uid="file:b.py", target_uid="file:a.py", kind="DEPENDS_ON"))

    score = compute_maintainability_score(
        graph,
        [_evidence("change_frequency", '{"change_count": 8}')],
    )

    low_component_names = {component["name"] for component in score["components"] if component["score"] < 100.0}

    assert score["score"] < 50.0
    assert "a.py" in score["affected_files"]
    assert "maintainability_index_average" in low_component_names
    assert "cyclomatic_complexity_pass_rate" in low_component_names
    assert "cognitive_complexity_pass_rate" in low_component_names
    assert "function_length_pass_rate" in low_component_names
    assert "technical_debt_pass_rate" in low_component_names
    assert "identifier_quality_rate" in low_component_names
    assert "modularity_edge_density_score" in low_component_names
    assert "churn_stability_score" in low_component_names
    assert score["recommendations"]


def test_code_quality_uses_ast_duplication_density_and_test_evidence(tmp_path):
    source_file = tmp_path / "app.py"
    source_file.write_text(
        "def run(x):\n"
        "    return x\n"
        "\n"
        "def format_value(x):\n"
        "    return str(x)\n",
        encoding="utf-8",
    )

    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:app.py", name="app.py", kind="file", file_path="app.py"))
    graph.add_entity(Entity(
        uid="function:app.py:run",
        name="run",
        kind="function",
        file_path="app.py",
        line=1,
        properties={
            "complexity": "1",
            "cognitive_complexity": "0",
            "halstead_volume": "8",
            "lines_of_code": "2",
        },
    ))
    graph.add_entity(Entity(
        uid="function:app.py:format_value",
        name="format_value",
        kind="function",
        file_path="app.py",
        line=4,
        properties={
            "complexity": "1",
            "cognitive_complexity": "0",
            "halstead_volume": "8",
            "lines_of_code": "2",
        },
    ))

    score = compute_code_quality_score(
        graph,
        [_evidence("risk_metrics", '{"test_file_ratio": 0.5}')],
        repo_path=str(tmp_path),
    )

    component_names = {component["name"] for component in score["components"]}

    assert score["score"] == 100.0
    assert score["confidence"] == 1.0
    assert score["formula"] == "code_quality_score = sum(component_scores) / component_count"
    assert {
        "cyclomatic_complexity_quality",
        "cognitive_complexity_quality",
        "function_size_quality",
        "duplication_quality",
        "god_module_quality",
        "test_presence_quality",
    } == component_names
    assert score["evidence_used"]["database"] == ["EntityModel", "EvidenceModel", "SettingModel"]


def test_code_quality_reports_duplicate_and_complexity_failures_from_real_source(tmp_path):
    first = tmp_path / "a.py"
    second = tmp_path / "b.py"
    first.write_text("def x(v):\n    if v:\n        return 1\n    return 0\n", encoding="utf-8")
    second.write_text("def y(v):\n    if v:\n        return 1\n    return 0\n", encoding="utf-8")

    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:a.py", name="a.py", kind="file", file_path="a.py"))
    graph.add_entity(Entity(uid="file:b.py", name="b.py", kind="file", file_path="b.py"))
    graph.add_entity(Entity(
        uid="function:a.py:x",
        name="x",
        kind="function",
        file_path="a.py",
        line=1,
        properties={
            "complexity": "20",
            "cognitive_complexity": "30",
            "halstead_volume": "200",
            "lines_of_code": "80",
        },
    ))
    graph.add_entity(Entity(
        uid="function:b.py:y",
        name="y",
        kind="function",
        file_path="b.py",
        line=1,
        properties={
            "complexity": "1",
            "cognitive_complexity": "0",
            "halstead_volume": "20",
            "lines_of_code": "4",
        },
    ))

    score = compute_code_quality_score(
        graph,
        [_evidence("risk_metrics", '{"test_file_ratio": 0.0}')],
        repo_path=str(tmp_path),
    )
    low_component_names = {component["name"] for component in score["components"] if component["score"] < 100.0}
    duplicate_component = next(component for component in score["components"] if component["name"] == "duplication_quality")

    assert score["score"] < 70.0
    assert duplicate_component["measured"]["duplicate_functions"] == 1
    assert "cyclomatic_complexity_quality" in low_component_names
    assert "cognitive_complexity_quality" in low_component_names
    assert "function_size_quality" in low_component_names
    assert "duplication_quality" in low_component_names
    assert "test_presence_quality" in low_component_names
    assert "a.py" in score["affected_files"]
    assert score["recommendations"]


def test_technical_debt_uses_ast_duplication_churn_and_test_evidence(tmp_path):
    source_file = tmp_path / "app.py"
    source_file.write_text(
        "def run(x):\n"
        "    return x\n"
        "\n"
        "def format_value(x):\n"
        "    return str(x)\n",
        encoding="utf-8",
    )

    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:app.py", name="app.py", kind="file", file_path="app.py"))
    graph.add_entity(Entity(
        uid="function:app.py:run",
        name="run",
        kind="function",
        file_path="app.py",
        line=1,
        properties={
            "complexity": "1",
            "cognitive_complexity": "0",
            "halstead_volume": "8",
            "lines_of_code": "2",
        },
    ))
    graph.add_entity(Entity(
        uid="function:app.py:format_value",
        name="format_value",
        kind="function",
        file_path="app.py",
        line=4,
        properties={
            "complexity": "1",
            "cognitive_complexity": "0",
            "halstead_volume": "8",
            "lines_of_code": "2",
        },
    ))

    churn = _evidence("change_frequency", '{"change_count": 0}')
    churn.file_path = "app.py"

    score = compute_technical_debt_score(
        graph,
        [
            churn,
            _evidence("risk_metrics", '{"test_file_ratio": 1.0}'),
        ],
        repo_path=str(tmp_path),
    )

    component_names = {component["name"] for component in score["components"]}

    assert score["score"] == 100.0
    assert score["confidence"] == 1.0
    assert score["formula"] == "technical_debt_score = 100 * debt_free_checks / total_debt_checks"
    assert score["effort_formula"] == "effort_units = measured_excess_over_named_gate; interest_units = effort_units + file_change_count"
    assert score["debt_items"] == []
    assert {
        "cognitive_complexity",
        "cyclomatic_complexity",
        "duplication",
        "function_size",
        "god_module",
        "maintainability_index",
        "test_debt",
    } == component_names
    assert score["evidence_used"]["database"] == ["EntityModel", "EvidenceModel", "SettingModel"]


def test_technical_debt_reports_categories_effort_interest_and_priority(tmp_path):
    first = tmp_path / "a.py"
    second = tmp_path / "b.py"
    first.write_text("def x(v):\n    if v:\n        return 1\n    return 0\n", encoding="utf-8")
    second.write_text("def y(v):\n    if v:\n        return 1\n    return 0\n", encoding="utf-8")

    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:a.py", name="a.py", kind="file", file_path="a.py"))
    graph.add_entity(Entity(uid="file:b.py", name="b.py", kind="file", file_path="b.py"))
    graph.add_entity(Entity(
        uid="function:a.py:x",
        name="x",
        kind="function",
        file_path="a.py",
        line=1,
        properties={
            "complexity": "20",
            "cognitive_complexity": "30",
            "halstead_volume": "200000",
            "lines_of_code": "80",
        },
    ))
    graph.add_entity(Entity(
        uid="function:b.py:y",
        name="y",
        kind="function",
        file_path="b.py",
        line=1,
        properties={
            "complexity": "1",
            "cognitive_complexity": "0",
            "halstead_volume": "20",
            "lines_of_code": "4",
        },
    ))

    churn = _evidence("change_frequency", '{"change_count": 5}')
    churn.file_path = "a.py"

    score = compute_technical_debt_score(
        graph,
        [
            churn,
            _evidence("risk_metrics", '{"test_file_ratio": 0.0}'),
        ],
        repo_path=str(tmp_path),
    )

    debt_categories = {item["category"] for item in score["debt_items"]}
    breakdown = {item["file_path"]: item for item in score["file_breakdown"]}
    cyclomatic_item = next(item for item in score["debt_items"] if item["category"] == "cyclomatic_complexity")

    assert score["score"] < 80.0
    assert {
        "cyclomatic_complexity",
        "cognitive_complexity",
        "function_size",
        "maintainability_index",
        "duplication",
        "test_debt",
    }.issubset(debt_categories)
    assert cyclomatic_item["effort_units"] == 10
    assert cyclomatic_item["interest_units"] == 15
    assert breakdown["a.py"]["priority_rank"] == 1
    assert "a.py" in score["affected_files"]
    assert score["recommendations"]
    assert any(item["file_path"] == "repository" and "test_debt" in item["categories"] for item in score["file_breakdown"])


def test_readability_uses_names_ast_metrics_comments_nesting_and_formatting(tmp_path):
    source_file = tmp_path / "app.py"
    source_file.write_text(
        "def readable_name(value):\n"
        "    # explains why this branch is readable\n"
        "    if value:\n"
        "        return value\n",
        encoding="utf-8",
    )

    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:app.py", name="app.py", kind="file", file_path="app.py"))
    graph.add_entity(Entity(
        uid="function:app.py:readable_name",
        name="readable_name",
        kind="function",
        file_path="app.py",
        line=1,
        properties={
            "complexity": "2",
            "cognitive_complexity": "1",
            "halstead_volume": "12",
            "lines_of_code": "4",
        },
    ))

    score = compute_readability_score(graph, [], repo_path=str(tmp_path))
    component_names = {component["name"] for component in score["components"]}

    assert score["score"] == 100.0
    assert score["confidence"] == 1.0
    assert score["formula"] == "readability_score = sum(component_scores) / component_count"
    assert {
        "identifier_descriptiveness_rate",
        "function_size_readability_rate",
        "cognitive_load_rate",
        "nesting_depth_rate",
        "comment_context_rate",
        "formatting_line_length_rate",
    } == component_names
    assert score["function_source_stats"][0]["comment_lines"] == 1
    assert score["evidence_used"]["database"] == ["EntityModel", "SettingModel"]


def test_readability_reports_source_and_ast_failures_from_measured_values(tmp_path):
    source_file = tmp_path / "hard.py"
    source_file.write_text(
        "def x(value):\n"
        "                    if value:\n"
        "                        return '" + ("a" * 130) + "'\n",
        encoding="utf-8",
    )

    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:hard.py", name="hard.py", kind="file", file_path="hard.py"))
    graph.add_entity(Entity(
        uid="function:hard.py:x",
        name="x",
        kind="function",
        file_path="hard.py",
        line=1,
        properties={
            "complexity": "20",
            "cognitive_complexity": "30",
            "halstead_volume": "200",
            "lines_of_code": "80",
        },
    ))

    score = compute_readability_score(graph, [], repo_path=str(tmp_path))
    low_component_names = {component["name"] for component in score["components"] if component["score"] < 100.0}
    nesting_component = next(component for component in score["components"] if component["name"] == "nesting_depth_rate")

    assert score["score"] == 0.0
    assert {
        "identifier_descriptiveness_rate",
        "function_size_readability_rate",
        "cognitive_load_rate",
        "nesting_depth_rate",
        "comment_context_rate",
        "formatting_line_length_rate",
    } == low_component_names
    assert nesting_component["measured"]["max_indent_depth"] > 4
    assert "hard.py" in score["affected_files"]
    assert score["recommendations"]


def test_security_uses_source_scan_dependency_manifest_and_vulnerability_evidence(tmp_path):
    source_file = tmp_path / "app.py"
    source_file.write_text("def run(value):\n    return value\n", encoding="utf-8")
    manifest = tmp_path / "requirements.txt"
    manifest.write_text("fastapi==0.109.0\n", encoding="utf-8")

    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:app.py", name="app.py", kind="file", file_path="app.py"))
    graph.add_entity(Entity(uid="file:requirements.txt", name="requirements.txt", kind="file", file_path="requirements.txt"))

    score = compute_security_score(
        graph,
        [_evidence("dependency_vulnerabilities", "[]")],
        repo_path=str(tmp_path),
    )

    component_names = {component["name"] for component in score["components"]}

    assert score["score"] == 100.0
    assert score["confidence"] == 1.0
    assert score["formula"] == "security_score = 100 * passing_security_checks / total_security_checks"
    assert score["findings"] == []
    assert score["vulnerability_advisory_available"] is True
    assert {
        "dangerous_api",
        "dependency_scanning",
        "secret_detection",
        "stored_security_evidence",
    } == component_names
    assert score["evidence_used"]["database"] == ["EntityModel", "EvidenceModel", "SettingModel"]


def test_security_reports_secret_dangerous_api_dependency_and_stored_vulnerability(tmp_path):
    source_file = tmp_path / "app.py"
    source_file.write_text(
        "API_KEY = \"1234567890abcdef\"\n"
        "def run(value):\n"
        "    return eval(value)\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "requirements.txt"
    manifest.write_text("fastapi\n", encoding="utf-8")

    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:app.py", name="app.py", kind="file", file_path="app.py"))
    graph.add_entity(Entity(uid="file:requirements.txt", name="requirements.txt", kind="file", file_path="requirements.txt"))

    score = compute_security_score(
        graph,
        [_evidence("dependency_vulnerabilities", '[{"package": "fastapi", "cve": "CVE-LOCAL-1"}]')],
        repo_path=str(tmp_path),
    )

    finding_categories = {finding["category"] for finding in score["findings"]}
    failed_categories = {check["category"] for check in score["checks"] if not check["passed"]}

    assert score["score"] == 0.0
    assert {
        "secret_detection",
        "dangerous_api",
        "dependency_scanning",
        "vulnerability_scanning",
    } == finding_categories
    assert {
        "secret_detection",
        "dangerous_api",
        "dependency_scanning",
        "stored_security_evidence",
    } == failed_categories
    assert "app.py" in score["affected_files"]
    assert "requirements.txt" in score["affected_files"]
    assert score["recommendations"]


def test_scalability_uses_graph_ast_async_and_coupling_evidence(tmp_path):
    api_dir = tmp_path / "backend" / "dna" / "api"
    domain_dir = tmp_path / "backend" / "dna" / "reasoning"
    api_dir.mkdir(parents=True)
    domain_dir.mkdir(parents=True)
    (api_dir / "routes.py").write_text("async def route():\n    return 1\n", encoding="utf-8")
    (domain_dir / "service.py").write_text("def run():\n    return 1\n", encoding="utf-8")

    graph = EntityGraph()
    graph.add_entity(Entity(
        uid="file:backend/dna/api/routes.py",
        name="routes.py",
        kind="file",
        file_path="backend/dna/api/routes.py",
    ))
    graph.add_entity(Entity(
        uid="file:backend/dna/reasoning/service.py",
        name="service.py",
        kind="file",
        file_path="backend/dna/reasoning/service.py",
    ))
    graph.add_entity(Entity(
        uid="function:backend/dna/reasoning/service.py:run",
        name="run",
        kind="function",
        file_path="backend/dna/reasoning/service.py",
        line=1,
        properties={
            "complexity": "1",
            "cognitive_complexity": "0",
            "halstead_volume": "8",
            "lines_of_code": "2",
        },
    ))
    graph.add_relation(EntityRelation(
        source_uid="file:backend/dna/api/routes.py",
        target_uid="file:backend/dna/reasoning/service.py",
        kind="DEPENDS_ON",
    ))

    score = compute_scalability_score(
        graph,
        [
            _evidence("temporal_coupling", '{"coupled_files": []}'),
            _evidence("dependency_graph", '{"coupling_coefficient": 0.2}'),
        ],
        repo_path=str(tmp_path),
    )

    component_names = {component["name"] for component in score["components"]}

    assert score["score"] > 85.0
    assert score["confidence"] == 1.0
    assert score["formula"] == "scalability_score = sum(component_scores) / component_count"
    assert {
        "acyclic_scalability_rate",
        "async_entrypoint_rate",
        "bottleneck_free_function_rate",
        "coupling_capacity_score",
        "fan_in_concentration_rate",
        "fan_out_scalability_rate",
        "module_boundary_rate",
        "module_size_scalability_rate",
        "stored_dependency_coupling_rate",
        "temporal_coupling_resilience_rate",
    } == component_names
    assert score["evidence_used"]["database"] == ["EntityModel", "RelationModel", "EvidenceModel", "SettingModel"]


def test_scalability_reports_cycles_boundaries_bottlenecks_and_coupling(tmp_path):
    api_dir = tmp_path / "backend" / "dna" / "api"
    model_dir = tmp_path / "backend" / "dna"
    api_dir.mkdir(parents=True)
    (api_dir / "routes.py").write_text("def route():\n    return 1\n", encoding="utf-8")
    (model_dir / "models.py").write_text("def hard():\n    return 1\n", encoding="utf-8")

    graph = EntityGraph()
    graph.add_entity(Entity(
        uid="file:backend/dna/models.py",
        name="models.py",
        kind="file",
        file_path="backend/dna/models.py",
    ))
    graph.add_entity(Entity(
        uid="file:backend/dna/api/routes.py",
        name="routes.py",
        kind="file",
        file_path="backend/dna/api/routes.py",
    ))
    graph.add_entity(Entity(
        uid="function:backend/dna/models.py:hard",
        name="hard",
        kind="function",
        file_path="backend/dna/models.py",
        line=1,
        properties={
            "complexity": "20",
            "cognitive_complexity": "30",
            "halstead_volume": "200",
            "lines_of_code": "80",
        },
    ))
    graph.add_relation(EntityRelation(
        source_uid="file:backend/dna/models.py",
        target_uid="file:backend/dna/api/routes.py",
        kind="DEPENDS_ON",
    ))
    graph.add_relation(EntityRelation(
        source_uid="file:backend/dna/api/routes.py",
        target_uid="file:backend/dna/models.py",
        kind="DEPENDS_ON",
    ))

    score = compute_scalability_score(
        graph,
        [
            _evidence("temporal_coupling", '{"coupled_files": ["backend/dna/api/routes.py"]}'),
            _evidence("dependency_graph", '{"coupling_coefficient": 0.8}'),
        ],
        repo_path=str(tmp_path),
    )

    low_component_names = {component["name"] for component in score["components"] if component["score"] < 100.0}

    assert score["score"] < 70.0
    assert "acyclic_scalability_rate" in low_component_names
    assert "async_entrypoint_rate" in low_component_names
    assert "bottleneck_free_function_rate" in low_component_names
    assert "coupling_capacity_score" in low_component_names
    assert "module_boundary_rate" in low_component_names
    assert "stored_dependency_coupling_rate" in low_component_names
    assert "temporal_coupling_resilience_rate" in low_component_names
    assert "backend/dna/models.py" in score["affected_files"]
    assert score["recommendations"]


def test_architecture_score_uses_graph_scc_coupling_and_integrity():
    graph = EntityGraph()
    graph.add_entity(Entity(uid="file:domain.py", name="domain.py", kind="file", file_path="domain.py"))
    graph.add_entity(Entity(uid="file:storage.py", name="storage.py", kind="file", file_path="storage.py"))
    graph.add_entity(Entity(uid="function:domain.py:run", name="run", kind="function", file_path="domain.py"))
    graph.add_relation(EntityRelation(source_uid="file:domain.py", target_uid="file:storage.py", kind="DEPENDS_ON"))
    graph.add_relation(EntityRelation(source_uid="file:domain.py", target_uid="function:domain.py:run", kind="CONTAINS"))

    score = compute_architecture_score(graph)
    component_names = {component["name"] for component in score["components"]}

    assert score["score"] > 90.0
    assert score["formula"] == "architecture_score = sum(component_scores) / component_count"
    assert {
        "acyclic_scc_rate",
        "coupling_density_score",
        "fan_out_balance_score",
        "layer_boundary_score",
        "relation_integrity_score",
    } == component_names
    assert score["evidence_used"]["database"] == ["EntityModel", "RelationModel"]


def test_architecture_score_reports_cycles_and_layer_violations():
    graph = EntityGraph()
    graph.add_entity(Entity(
        uid="file:backend/dna/models.py",
        name="models.py",
        kind="file",
        file_path="backend/dna/models.py",
    ))
    graph.add_entity(Entity(
        uid="file:backend/dna/api/routers/users.py",
        name="users.py",
        kind="file",
        file_path="backend/dna/api/routers/users.py",
    ))
    graph.add_relation(EntityRelation(
        source_uid="file:backend/dna/models.py",
        target_uid="file:backend/dna/api/routers/users.py",
        kind="DEPENDS_ON",
    ))
    graph.add_relation(EntityRelation(
        source_uid="file:backend/dna/api/routers/users.py",
        target_uid="file:backend/dna/models.py",
        kind="DEPENDS_ON",
    ))

    score = compute_architecture_score(graph)
    low_component_names = {component["name"] for component in score["components"] if component["score"] < 100.0}
    layer_component = next(component for component in score["components"] if component["name"] == "layer_boundary_score")

    assert score["score"] < 80.0
    assert "acyclic_scc_rate" in low_component_names
    assert "coupling_density_score" in low_component_names
    assert "layer_boundary_score" in low_component_names
    assert layer_component["measured"]["violations"][0]["source_layer"] == "model"
    assert layer_component["measured"]["violations"][0]["target_layer"] == "api"
    assert "backend/dna/models.py" in score["affected_files"]
    assert score["recommendations"]
