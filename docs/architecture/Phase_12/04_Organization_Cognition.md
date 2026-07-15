================================================================================
# 04 Organization Cognition
================================================================================

# Organization Cognition

## Purpose

Organization cognition is the V3 vision: DNA becomes a persistent, queryable representation of the entire engineering organization's technical knowledge. This document explores what that means in practice.

---

## The Organization Graph

At V3, DNA's model extends beyond single repositories to encompass:

### Repository Layer

| Entity | Example |
|---|---|
| Repository | `github.com/acme/payment-service` |
| Module | `src/payment/checkout.py` |
| Dependency | `payment-service → auth-service` |
| API Contract | `POST /api/v1/checkout` |

### People Layer

| Entity | Example |
|---|---|
| Team | Payments Team |
| Owner | `alice@acme.com` |
| Expertise | `alice has 15 PRs in checkout module` |
| Bus factor | `checkout module: 1 primary owner` |

### Process Layer

| Entity | Example |
|---|---|
| CI/CD pipeline | `payment-service → deploy-prod` |
| On-call rotation | `payments-team → weekly rotation` |
| Incident | `INC-1234 → checkout timeout → resolved` |
| Decision | `ADR-42 → why we chose Stripe` |

## Queries Made Possible

| Query | Information Need |
|---|---|
| "Who to ask about payment retry logic?" | Expertise + Ownership |
| "What services are affected by this DB schema change?" | Dependency graph |
| "Which teams deploy most often on Fridays?" | CI/CD + People |
| "Is this module below the bus factor threshold?" | Ownership + PR history |
| "What decisions led to the current auth architecture?" | ADRs + dependency chain |

## Challenges

| Challenge | Approach |
|---|---|
| Data privacy | Role-based access, per-repo visibility |
| Data freshness | Webhook-driven incremental updates |
| Cross-repo dedup | Canonical entity IDs with aliases |
| Organizational politics | Respect team boundaries, opt-in sharing |
