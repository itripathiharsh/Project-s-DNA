import logging
from dna.models import EntityGraph, DependencyGraph
from dna.evidence.store import EvidenceStore

logger = logging.getLogger("dna.engines.risk")


def analyze_risks(
    entity_graph: EntityGraph,
    dependency_graph: DependencyGraph | None = None,
    evidence_store: EvidenceStore | None = None,
) -> dict:
    logger.info("Starting risk analysis")
    file_entities = [e for e in entity_graph.entities if e.kind == "file"]
    function_entities = [e for e in entity_graph.entities if e.kind == "function"]

    source_files = [e for e in file_entities if not e.file_path.startswith("test_")
                    and "/test_" not in e.file_path and "/tests/" not in e.file_path]
    test_files = [e for e in file_entities if e.file_path.startswith("test_")
                  or "/test_" in e.file_path or "/tests/" in e.file_path]

    test_file_ratio = round(len(test_files) / max(len(source_files), 1), 4)

    orphaned_modules = []
    if dependency_graph:
        for fe in source_files:
            deps = dependency_graph.get_dependencies(fe.file_path)
            if not deps:
                orphaned_modules.append(fe.file_path)

    high_complexity_files = []
    for fe in source_files:
        funcs_in_file = [f for f in function_entities if f.file_path == fe.file_path]
        func_count = len(funcs_in_file)
        if func_count > 5:
            high_complexity_files.append({
                "file": fe.file_path,
                "function_count": func_count,
            })
    high_complexity_files.sort(key=lambda x: -x["function_count"])

    cycle_risk = 0
    if dependency_graph:
        cycles = dependency_graph.detect_cycles()
        cycle_risk = len(cycles)

    top_risk_indicators = []

    if len(orphaned_modules) > 5:
        top_risk_indicators.append({
            "type": "orphaned_modules",
            "count": len(orphaned_modules),
            "severity": "medium",
            "description": f"{len(orphaned_modules)} modules have no dependencies",
        })

    if cycle_risk > 0:
        top_risk_indicators.append({
            "type": "dependency_cycles",
            "count": cycle_risk,
            "severity": "high",
            "description": f"{cycle_risk} dependency cycles detected",
        })

    if test_file_ratio < 0.1:
        top_risk_indicators.append({
            "type": "low_test_file_ratio",
            "count": int(test_file_ratio * 100),
            "severity": "high",
            "description": f"Test file ratio: {test_file_ratio}",
        })

    if high_complexity_files:
        top_risk_indicators.append({
            "type": "high_complexity",
            "count": len(high_complexity_files),
            "severity": "medium",
            "description": f"{len(high_complexity_files)} files with >5 functions",
        })

    result = {
        "total_files": len(file_entities),
        "source_files": len(source_files),
        "test_files": len(test_files),
        "test_file_ratio": test_file_ratio,
        "test_coverage_ratio": test_file_ratio,  # backward compatibility
        "high_complexity_files": high_complexity_files[:10],
        "orphaned_modules": orphaned_modules[:10],
        "dependency_cycles": cycle_risk,
        "risk_indicators": top_risk_indicators,
        "overall_risk_score": min(10, cycle_risk * 2 + len(top_risk_indicators)),
    }

    if evidence_store:
        evidence_store.add_evidence(
            "risk_metrics",
            {
                "test_file_ratio": test_file_ratio,
                "test_coverage_ratio": test_file_ratio,  # backward compatibility
                "dependency_cycles": cycle_risk,
                "orphaned_modules": len(orphaned_modules),
                "high_complexity_files": len(high_complexity_files),
                "overall_risk_score": result["overall_risk_score"],
            },
            source="risk_engine",
        )

    logger.info("Risk analysis completed. Overall risk score: %d", result["overall_risk_score"])
    return result
