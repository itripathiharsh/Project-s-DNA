import logging
import os
import json
from dna.models import EntityGraph, DependencyGraph
from dna.evidence.store import EvidenceStore

logger = logging.getLogger("dna.engines.risk")


def analyze_risks(
    entity_graph: EntityGraph,
    dependency_graph: DependencyGraph | None = None,
    evidence_store: EvidenceStore | None = None,
    repo_path: str | None = None,
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

    # Security Scan
    findings = []
    import re
    
    # Slack token, AWS keys, generic credentials
    slack_re = re.compile(r"xox[bapr]-[0-9a-zA-Z]{10,40}")
    aws_re = re.compile(r"AKIA[0-9A-Z]{16}")
    generic_secret_re = re.compile(r"(?:secret|token|password|passwd|private_key|api_key)\s*=\s*['\"][a-zA-Z0-9_\-\.\+/~]{16,}['\"]", re.IGNORECASE)
    
    if repo_path and os.path.exists(repo_path):
        for fe in file_entities:
            file_path = fe.file_path
            abs_path = os.path.join(repo_path, file_path)
            if not os.path.isfile(abs_path):
                continue
            
            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except Exception:
                logger.warning("Failed to read file %s for risk analysis", abs_path)
                lines = []
                
            # Line by line checks
            for idx, line in enumerate(lines):
                line_no = idx + 1
                
                # Check secrets
                if slack_re.search(line):
                    findings.append({
                        "file_path": file_path,
                        "line": line_no,
                        "finding_type": "hardcoded_secret",
                        "severity": "Critical",
                        "evidence": "Slack token detected",
                        "description": "Slack token was found hardcoded in source file."
                    })
                if aws_re.search(line):
                    findings.append({
                        "file_path": file_path,
                        "line": line_no,
                        "finding_type": "hardcoded_secret",
                        "severity": "Critical",
                        "evidence": "AWS Access Key ID detected",
                        "description": "AWS access key was found hardcoded in source file."
                    })
                if generic_secret_re.search(line):
                    findings.append({
                        "file_path": file_path,
                        "line": line_no,
                        "finding_type": "hardcoded_secret",
                        "severity": "High",
                        "evidence": "Potential credential in assignment",
                        "description": "A variable with secret/token/password name assigned a value."
                    })
                    
                # Check dangerous APIs
                if any(x in line for x in ["eval(", "exec(", "os.system(", "subprocess.Popen(", "child_process.exec("]):
                    if not line.strip().startswith("#") and not line.strip().startswith("//"):
                        findings.append({
                            "file_path": file_path,
                            "line": line_no,
                            "finding_type": "dangerous_api",
                            "severity": "High",
                            "evidence": line.strip(),
                            "description": "Execution of dynamic code or system command via dangerous API."
                        })
            
            # Check insecure configs
            lower_path = file_path.lower()
            if "dockerfile" in lower_path:
                content = "".join(lines)
                if "user root" in content.lower():
                    findings.append({
                        "file_path": file_path,
                        "line": 1,
                        "finding_type": "insecure_config",
                        "severity": "High",
                        "evidence": "USER root",
                        "description": "Docker container configured to run as root user."
                    })
            
            if ".env" in lower_path:
                for idx, line in enumerate(lines):
                    if "=" in line and not line.strip().startswith("#"):
                        parts = line.split("=", 1)
                        val = parts[1].strip().strip("\"'")
                        if val and len(val) > 8:
                            findings.append({
                                "file_path": file_path,
                                "line": idx + 1,
                                "finding_type": "insecure_config",
                                "severity": "High",
                                "evidence": parts[0].strip(),
                                "description": "Actual secret value configured in git-tracked .env file."
                            })

            if "package.json" in lower_path:
                content = "".join(lines)
                try:
                    pkg_data = json.loads(content)
                    deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                    # Check known vulnerable packages
                    for dep, ver in deps.items():
                        v_clean = ver.replace("^", "").replace("~", "")
                        if dep == "lodash" and v_clean < "4.17.21":
                            findings.append({
                                "file_path": file_path,
                                "line": 1,
                                "finding_type": "vulnerability",
                                "severity": "High",
                                "evidence": f"lodash@{ver}",
                                "description": "Lodash version contains known prototype pollution vulnerability."
                            })
                        elif dep == "qs" and v_clean < "6.5.3":
                            findings.append({
                                "file_path": file_path,
                                "line": 1,
                                "finding_type": "vulnerability",
                                "severity": "Medium",
                                "evidence": f"qs@{ver}",
                                "description": "Qs version contains known prototype pollution vulnerability."
                            })
                except Exception:
                    logger.debug("Failed to parse package.json for dependency vulnerabilities")

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

    if findings:
        top_risk_indicators.append({
            "type": "security_vulnerabilities",
            "count": len(findings),
            "severity": "high",
            "description": f"{len(findings)} security findings detected",
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
        "overall_risk_score": min(10, cycle_risk * 2 + len(top_risk_indicators) + (2 if findings else 0)),
        "security_findings": findings
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
        
        for f in findings:
            evidence_store.add_evidence(
                "security_finding",
                f,
                source="risk_engine",
                file_path=f["file_path"],
            )

    logger.info("Risk analysis completed. Overall risk score: %d, Security findings: %d", result["overall_risk_score"], len(findings))
    return result
