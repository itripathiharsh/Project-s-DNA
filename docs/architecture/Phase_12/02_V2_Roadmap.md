================================================================================
# 02 V2 Roadmap
================================================================================

# V2 Roadmap

## Purpose

V2 (Team Cognition) extends DNA from a single-developer tool to a team platform. Multiple developers can share a DNA instance, query the same evidence corpus, and collaborate on insights.

---

## V2 Theme: Team Cognition

**Problem:** Engineering teams have fragmented knowledge. One developer knows module A, another knows module B, and no one has the full picture. When the developer who owns a module leaves, their knowledge leaves with them.

**Solution:** A shared DNA instance that continuously analyzes the team's repositories, making institutional knowledge persistent and queryable.

## V2 Capabilities

| Capability | Description | Epic |
|---|---|---|
| Multi-user | Multiple developers can log in and use the same instance | M5 |
| PostgreSQL backend | Production-grade storage for shared evidence | M5 |
| Auth + RBAC | JWT authentication, role-based access control | M5 |
| Shared dashboards | Dashboards that surface team-wide insights | M6 |
| Insight commenting | Discuss and annotate insights as a team | M6 |
| Notifications | Be notified when relevant insights are discovered | M6 |
| GitHub/GitLab webhooks | Auto-analyze new PRs, issues, and commits | M7 |
| Slack bot | Query DNA from Slack | M7 |
| CI/CD integration | Run DNA analysis in CI pipelines | M7 |

## V2 Architecture Changes

```
V1:                       V2:
┌──────────┐             ┌──────────────────┐
│  sqlite   │             │  postgresql       │
└──────────┘             └──────────────────┘
┌──────────┐             ┌──────────────────┐
│  local    │             │  auth (JWT/SSO)   │
└──────────┘             └──────────────────┘
┌──────────┐             ┌──────────────────┐
│  single   │             │  webhooks/graphql │
└──────────┘             └──────────────────┘
```

## V2 User Stories

| Story | Priority |
|---|---|
| As a team lead, I want to see what areas of the codebase are most complex | P1 |
| As a new hire, I want to query the codebase to understand how a feature works | P1 |
| As a developer, I want to know if my PR introduces new technical debt | P2 |
| As an on-call engineer, I want to find who owns a failing module | P2 |
| As a CTO, I want a dashboard showing codebase health trends | P3 |
