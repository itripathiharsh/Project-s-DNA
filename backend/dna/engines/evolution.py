import logging
from dna.models import CommitHistory, EntityGraph
from dna.evidence.store import EvidenceStore
from dna.git_history.commit_parser import categorize_commit

logger = logging.getLogger("dna.engines.evolution")


def analyze_evolution(
    commit_history: CommitHistory,
    entity_graph: EntityGraph | None = None,
    evidence_store: EvidenceStore | None = None,
) -> dict:
    logger.info("Starting evolution analysis")
    commits = commit_history.commits

    total_commits = len(commits)
    total_authors = len(commit_history.author_stats)

    category_counts: dict[str, int] = {}
    import re
    pr_count = 0
    issue_count = 0
    for c in commits:
        cat = categorize_commit(c.message)
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if re.search(r"merge pull request #\d+", c.message, re.IGNORECASE):
            pr_count += 1
        if re.search(r"(fixes|closes|resolves) #\d+", c.message, re.IGNORECASE):
            issue_count += 1

    total_insertions = sum(c.insertions for c in commits)
    total_deletions = sum(c.deletions for c in commits)

    file_change_counts: dict[str, int] = {}
    for c in commits:
        for fc in c.per_file_changes:
            file_change_counts[fc.file_path] = file_change_counts.get(fc.file_path, 0) + 1

    avg_changes_per_commit = round(total_commits / max(len(commit_history.author_stats), 1), 2)

    if commits:
        first = min(c.committed_at for c in commits if c.committed_at)
        last = max(c.committed_at for c in commits if c.committed_at)
    else:
        first = ""
        last = ""

    result = {
        # placeholder for hotspots; will be replaced later if entity_graph provided
        "total_commits": total_commits,
        "total_authors": total_authors,
        "total_insertions": total_insertions,
        "total_deletions": total_deletions,
        "commit_categories": category_counts,
        "changes_per_author": avg_changes_per_commit,
        "first_commit": first,
        "last_commit": last,
        "merge_commits": sum(1 for c in commits if len(c.parents) > 1),
        "pr_stats": pr_count,
        "issue_stats": issue_count,
    }

    hotspot_list: list[dict] = []
    if entity_graph:
        file_entities = [e for e in entity_graph.entities if e.kind == "file"]
        for fe in file_entities:
            change_count = file_change_counts.get(fe.file_path, 0)
            if change_count > 0:
                hotspot_list.append({
                    "file": fe.file_path,
                    "change_count": change_count,
                })
        hotspot_list.sort(key=lambda x: -x["change_count"])
        result["hotspots"] = hotspot_list[:10]

    if evidence_store:
        # Emit commit metadata evidence for each commit
        for c in commits:
            evidence_store.add_evidence(
                "commit_metadata",
                {
                    "hash": c.hash,
                    "author": getattr(c, "author_name", ""),
                    "date": c.committed_at,
                    "message": c.message,
                    "insertions": c.insertions,
                    "deletions": c.deletions,
                    "files": [{"file_path": fc.file_path, "insertions": fc.insertions, "deletions": fc.deletions, "change_type": fc.change_type} for fc in c.per_file_changes]
                },
                source="evolution_engine",
            )
        evidence_store.add_evidence(
            "commit_distribution",
            {
                "total_commits": total_commits,
                "categories": category_counts,
                "merge_commits": result["merge_commits"],
            },
            source="evolution_engine",
        )
        evidence_store.add_evidence(
            "growth_trend",
            {
                "commits": total_commits,
                "insertions": total_insertions,
                "deletions": total_deletions,
                "authors": total_authors,
                "first_commit": first,
                "last_commit": last,
            },
            source="evolution_engine",
        )
        if hotspot_list:
            evidence_store.add_evidence(
                "hotspot_list",
                {"hotspots": hotspot_list[:10]},
                source="evolution_engine",
            )
        for fp, count in file_change_counts.items():
            evidence_store.add_evidence(
                "change_frequency",
                {"change_count": count},
                source="evolution_engine",
                file_path=fp,
            )
        
        evidence_store.add_evidence(
            "pr_issue_stats",
            {
                "pr_count": pr_count,
                "issue_count": issue_count,
            },
            source="evolution_engine"
        )
        evidence_store.add_evidence(
            "branches_list",
            [{"name": getattr(b, "name", ""), "is_head": getattr(b, "is_head", False)} for b in commit_history.branches],
            source="evolution_engine"
        )
        evidence_store.add_evidence(
            "tags_list",
            [{"name": getattr(t, "name", ""), "date": getattr(t, "tagged_at", "")} for t in commit_history.tags],
            source="evolution_engine"
        )

    logger.info("Evolution analysis completed. Commits: %d, Authors: %d", total_commits, total_authors)
    # Provide backward‑compatible key for older callers
    result.setdefault("hotspot_list", result.get("hotspots", []))
    return result
