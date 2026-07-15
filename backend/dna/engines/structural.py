import os
import logging
from dna.models import EntityGraph
from dna.evidence.store import EvidenceStore

logger = logging.getLogger("dna.engines.structural")


def analyze_structure(
    graph: EntityGraph,
    evidence_store: EvidenceStore | None = None,
) -> dict:
    logger.info("Starting structural analysis")
    entities = graph.entities
    relations = graph.relations

    file_entities = [e for e in entities if e.kind == "file"]
    function_entities = [e for e in entities if e.kind == "function"]
    class_entities = [e for e in entities if e.kind == "class"]
    import_entities = [e for e in entities if e.kind == "import"]

    dir_depth: dict[str, int] = {}
    for fe in file_entities:
        parts = fe.file_path.replace("\\", "/").split("/")
        depth = len(parts)
        dir_depth[fe.file_path] = depth

    avg_depth = sum(dir_depth.values()) / len(dir_depth) if dir_depth else 0
    max_depth = max(dir_depth.values()) if dir_depth else 0

    dir_counts: dict[str, int] = {}
    for fe in file_entities:
        d = os.path.dirname(fe.file_path) or "/"
        dir_counts[d] = dir_counts.get(d, 0) + 1

    import_count = len(import_entities)

    depends_relations = [r for r in relations if r.kind == "DEPENDS_ON"]
    imports_relations = [r for r in relations if r.kind == "IMPORTS"]

    structural_coupling = len(depends_relations) + len(imports_relations)

    # Calculate complexity metrics
    file_funcs: dict[str, list[int]] = {}
    all_complexities: list[int] = []

    for fe in function_entities:
        comp_str = fe.properties.get("complexity", "1")
        try:
            comp = int(comp_str)
        except ValueError:
            comp = 1
        all_complexities.append(comp)
        
        file_path = fe.file_path
        if file_path not in file_funcs:
            file_funcs[file_path] = []
        file_funcs[file_path].append(comp)

    repo_avg_complexity = sum(all_complexities) / len(all_complexities) if all_complexities else 0.0
    repo_max_complexity = max(all_complexities) if all_complexities else 0

    file_complexities = {}
    for fp, comps in file_funcs.items():
        avg_comp = sum(comps) / len(comps) if comps else 0.0
        max_comp = max(comps) if comps else 0
        file_complexities[fp] = {
            "avg_complexity": round(avg_comp, 2),
            "max_complexity": max_comp,
            "complexity": max_comp,
        }

    result = {
        "total_files": len(file_entities),
        "total_functions": len(function_entities),
        "total_classes": len(class_entities),
        "total_imports": import_count,
        "total_relations": len(relations),
        "avg_directory_depth": round(avg_depth, 2),
        "max_directory_depth": max_depth,
        "top_directories": sorted(dir_counts.items(), key=lambda x: -x[1])[:5],
        "funcs_per_file": round(len(function_entities) / max(len(file_entities), 1), 2),
        "classes_per_file": round(len(class_entities) / max(len(file_entities), 1), 2),
        "structural_coupling": structural_coupling,
        "avg_complexity": round(repo_avg_complexity, 2),
        "max_complexity": repo_max_complexity,
    }

    if evidence_store:
        evidence_store.add_evidence(
            "module_structure",
            {
                "total_files": result["total_files"],
                "total_dirs": len(dir_counts),
                "max_depth": max_depth,
                "avg_depth": avg_depth,
            },
            source="structural_engine",
        )
        evidence_store.add_evidence(
            "size_metrics",
            {
                "files": result["total_files"],
                "functions": result["total_functions"],
                "classes": result["total_classes"],
                "funcs_per_file": result["funcs_per_file"],
            },
            source="structural_engine",
        )
        evidence_store.add_evidence(
            "complexity_metrics",
            {
                "structural_coupling": structural_coupling,
                "imports": import_count,
                "avg_complexity": result["avg_complexity"],
                "max_complexity": result["max_complexity"],
            },
            source="structural_engine",
        )
        
        # Add file-level complexity metrics
        for fp, metrics in file_complexities.items():
            evidence_store.add_evidence(
                "complexity_metrics",
                metrics,
                source="structural_engine",
                file_path=fp,
            )

    logger.info("Structural analysis completed. Found %d files, %d functions, %d classes. Max complexity: %d, Avg: %.2f",
                len(file_entities), len(function_entities), len(class_entities),
                repo_max_complexity, repo_avg_complexity)
    return result
