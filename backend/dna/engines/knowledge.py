import logging
from dna.models import CommitHistory, EntityGraph
from dna.evidence.store import EvidenceStore

logger = logging.getLogger("dna.engines.knowledge")


def analyze_knowledge(
    commit_history: CommitHistory,
    entity_graph: EntityGraph | None = None,
    evidence_store: EvidenceStore | None = None,
    repo_path: str | None = None,
) -> dict:
    logger.info("Starting knowledge analysis")
    author_stats = commit_history.author_stats
    total_commits = max(len(commit_history.commits), 1)

    contributions = []
    for a in author_stats:
        share = round(a.commit_count / total_commits, 4) if total_commits > 0 else 0
        contributions.append({
            "name": a.name,
            "email": a.email,
            "commit_count": a.commit_count,
            "share": share,
            "insertions": a.insertions,
            "deletions": a.deletions,
        })

    contributions.sort(key=lambda x: -x["commit_count"])

    top_contributor = contributions[0]["name"] if contributions else None
    top_share = contributions[0]["share"] if contributions else 0

    bus_factor = 0
    cumulative = 0
    for c in contributions:
        cumulative += c["share"]
        bus_factor += 1
        if cumulative >= 0.5:
            break

    if entity_graph:
        file_entities = [e for e in entity_graph.entities if e.kind == "file"]

        # Fetch all per-file git blame data in ONE batched, concurrent pass
        # instead of spawning one sequential `git blame` subprocess per file.
        # The per-file blame mapping is identical to the previous per-call
        # behavior; only the order of subprocess execution changes (parallel
        # rather than serial). When repo_path is unset or blame fails for all
        # files, blame_map stays empty and each file's ownership falls back to
        # the commit-share heuristic, exactly as before.
        blame_map: dict[str, dict[str, int]] = {}
        if repo_path:
            try:
                from dna.git_history.blame import get_files_blame
                blame_map = get_files_blame(repo_path, [fe.file_path for fe in file_entities])
            except Exception:
                blame_map = {}

        ownership_scores = {}
        for fe in file_entities:
            score = 0.0
            primary_owner = top_contributor

            blame_data = blame_map.get(fe.file_path) if blame_map else None

            if blame_data:
                total_lines = sum(blame_data.values())
                if total_lines > 0:
                    primary_owner = max(blame_data, key=blame_data.get)
                    score = blame_data[primary_owner] / total_lines
                else:
                    if contributions:
                        score = contributions[0]["share"]
            else:
                if contributions:
                    score = contributions[0]["share"]

            ownership_scores[fe.file_path] = {
                "primary_owner": primary_owner,
                "ownership_score": round(score, 4),
            }

        expertise_scores = {}
        for a in author_stats:
            score = round(a.commit_count / total_commits, 4)
            expertise_scores[a.name] = {
                "expertise_score": score,
                "commit_count": a.commit_count,
            }
    else:
        ownership_scores = {}
        expertise_scores = {}

    bus_factor_risk = "low"
    if bus_factor <= 2:
        bus_factor_risk = "high"
    elif bus_factor <= 4:
        bus_factor_risk = "medium"

    result = {
        "total_authors": len(author_stats),
        "contributions": contributions[:10],
        "top_contributor": top_contributor,
        "top_contributor_share": top_share,
        "bus_factor": bus_factor,
        "bus_factor_risk": bus_factor_risk,
        "ownership_scores": ownership_scores,
        "expertise_scores": expertise_scores,
    }

    if evidence_store:
        for c in contributions:
            evidence_store.add_evidence(
                "author_contribution",
                {"author": c["name"], "percentage": c["share"],
                 "commits": c["commit_count"]},
                source="knowledge_engine",
            )

        evidence_store.add_evidence(
            "ownership_score",
            {
                "primary_owner": top_contributor,
                "ownership_share": top_share,
                "bus_factor": bus_factor,
                "bus_factor_risk": bus_factor_risk,
            },
            source="knowledge_engine",
        )
        for fp, details in ownership_scores.items():
            evidence_store.add_evidence(
                "ownership_score",
                {
                    "primary_owner": details["primary_owner"],
                    "ownership_score": details["ownership_score"],
                    "bus_factor": bus_factor,
                    "bus_factor_risk": bus_factor_risk,
                },
                source="knowledge_engine",
                file_path=fp,
            )

    logger.info("Knowledge analysis completed. Bus factor: %d (risk: %s)", bus_factor, bus_factor_risk)
    return result
