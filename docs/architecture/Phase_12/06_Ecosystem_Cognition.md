================================================================================
# 06 Ecosystem Cognition
================================================================================

# Ecosystem Cognition

## Purpose

Ecosystem cognition extends DNA beyond the organization to model the external software ecosystem — open-source libraries, SaaS dependencies, and their relationships.

---

## Why Ecosystem Cognition?

| Question | Today's Answer | With Ecosystem Cognition |
|---|---|---|
| "Is our version of this library vulnerable?" | Check CVE database manually | DNA flags it automatically |
| "What does this dependency actually do?" | Read its README | DNA provides a grounded analysis |
| "Which dependencies are most critical?" | Gut feeling | DNA ranks by usage, risk, coupling |
| "Should we migrate to this new library?" | Manual evaluation | DNA compares API surfaces, deprecation risk |

## The Ecosystem Model

DNA models the external ecosystem using:

| Source | Data Extracted |
|---|---|
| npm registry | Package metadata, dependencies, downloads |
| PyPI | Package metadata, dependencies, Python version support |
| crates.io | Package metadata, features, semver compatibility |
| GitHub API | Stars, issues, release cadence, bus factor |
| OpenSSF Scorecard | Security posture, maintenance risk |
| CVE database | Known vulnerabilities by version range |

## Ecosystem Queries

| Query | What DNA Returns |
|---|---|
| "Audit our JavaScript dependencies for CVEs" | List of vulnerable packages + remediation |
| "Which dependencies have the highest bus factor?" | Dependencies with single maintainer |
| "What's the upgrade risk for django 4.2 → 5.0?" | Breaking changes + our usage sites |
| "Find alternatives to lodash" | Top N alternatives with diff analysis |

## Trust Model

| Level | Trust | Source |
|---|---|---|
| T1 | High | Well-known, actively maintained, widely used |
| T2 | Medium | Active but small community, periodic releases |
| T3 | Low | Unmaintained, single author, low downloads |
| T4 | Unknown | First-time install, no reputation data |
