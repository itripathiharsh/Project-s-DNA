================================================================================
# Tier 1 Fixes — CHANGELOG
================================================================================

## C04 — V1 Scope Contradiction

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 0 Success Metrics said "V1 target: 1,000 active repositories" while Phase 2 defines V1 as "One repository, one user, one machine." The metric was an adoption target (cumulative across all instances), not a per-instance capability. Wording was ambiguous. |
| Files modified | `Phase_0_Foundation_Product_Strategy_COMBINED.md` (2 locations) |
| Change | Clarified "1,000 active repositories analyzed" → "1,000 active repositories analyzed cumulatively across all V1 deployments." Same clarification applied to Metric 3.1 detailed metrics section. |
| Why required | Without clarification, a reader would see the Phase 0 target contradict Phase 2's explicit V1 scope definition, creating confusion about what V1 actually supports. |

---

## C05 — Time to Understanding Metric Contradiction

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 0 defined the same metric (Time to Understanding) in two different sections with different baselines, targets, and percentages. Section 5 used baseline 3-6 months, V1=2 weeks, V2=3 days. Metric 4.1 used baseline 3 weeks, V1=2 days, V2=3 days with swapped/incorrect percentages. |
| Files modified | `Phase_0_Foundation_Product_Strategy_COMBINED.md` (2 locations + glossary) |
| Change | Aligned Metric 4.1 to match Section 5's authoritative definition. Updated glossary entry to use consistent baseline (3-6 months) and targets (2 weeks V1, 3 days V2). |
| Why required | Two conflicting definitions of the same core metric made the document internally contradictory and unusable for measuring success. |

---

## C06 — Performance Targets Unachievable

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 5/01 set < 2 sec simple QA with < 1 sec LLM inference budget. Phase 5/02's hardware benchmarks showed even the smallest 3B Q4 model on CPU delivers 15-25 tok/s, requiring 20-33 seconds for a 500-token response. The targets were impossible on any Phase 5/02 hardware config. |
| Files modified | `Phase_5/01_Reasoning_Overview.md`, `Phase_5/02_LLM_Architecture.md` |
| Change | Phase 5/01: Updated targets table to split CPU vs GPU columns (CPU = minimum hardware, GPU = with accelerator). Simple QA: < 2 sec → < 10 sec (CPU) / < 3 sec (GPU). Added hardware note. Updated latency budget to GPU (7B Q4 on RTX 3060) and CPU (3B Q4) as separate totals. Phase 5/02: Updated Target: End-to-End Latency table to match Phase 5/01's new CPU/GPU columns and adjusted LLM budgets accordingly. |
| Why required | Implementors cannot target impossible specs. Without this fix, developers would attempt to optimize toward unachievable latency targets, or ship a product that misses stated goals. |

---

## C07 — Token Budget Contradiction

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase 5/02 allocated 1000 tokens for "Prompt template" while Phase 5/03 (the dedicated prompt architecture document) allocated only 400 tokens. Phase 5/03's per-type budget tables summed to 7592-7800 tokens, leaving an unexplained 400-600 token gap against the 8192 window. |
| Files modified | `Phase_5/02_LLM_Architecture.md` |
| Change | Changed Phase 5/02's prompt template allocation from 1000 to 400 tokens to match Phase 5/03. Documented the remaining 600 tokens as a "Safety margin" for tokenizer variance and model-specific special tokens, with a cross-reference to Phase 5/03 for per-type allocations. |
| Why required | Token budgets directly affect prompt template implementation. Developers following Phase 5/02's 1000-token budget would create templates that overflow Phase 5/03's constraints, or vice versa. |

---

## C01 — V4 Version Contradiction

| Field | Value |
|---|---|
| Severity | Critical |
| Root cause | Phase -1 defines V4+ (Ecosystem Cognition), Phase 0 defines V1-V4 explicitly, Phase 2 has V4 architecture sections. But Phase 11/01 and Phase 12/01 only defined V1-V3, truncating the roadmap. Phase 12/06's glossary entry labeled Ecosystem Cognition as "V3+ research direction" instead of "V4 capability." |
| Files modified | `Phase_11/01_Product_Roadmap.md`, `Phase_11/02_Milestones.md`, `Phase_12/01_Future_Vision.md`, `Phase_12/10_Glossary.md` |
| Change | Phase 11/01: Added V4 row to roadmap overview, added "V4 — Ecosystem Cognition" section with M11-M13 milestones. Updated intro from "three major versions" to "four major versions." Phase 11/02: Added V4 milestones (M11-M13) table. Phase 12/01: Changed "Three Horizons" to "Four Horizons" and added H4 with V4 timeframe/capabilities. Phase 12/10: Changed Ecosystem Cognition from "V3+ research direction" to "V4 capability." |
| Why required | Versioning is referenced across every phase. The silent truncation from 4 to 3 versions created confusion about whether V4 was cancelled, deferred, or simply forgotten. Aligning to the foundational Phase -1/0/2 definitions restores consistency. |

---

## Validation Results

| Check | Status |
|---|---|
| No broken references | ✓ — All cross-references verified against actual doc titles |
| No contradictory terminology | ✓ — Version labels, metric definitions, and hardware targets aligned |
| No inconsistent version numbers | ✓ — V1-V4 consistent across Phase -1, 0, 2, 11, 12 |
| No undefined components | ✓ — Token budgets reference Phase 5/03; hardware targets reference Phase 5/02 benchmarks |
| No broken architecture | ✓ — V1 scope, performance targets, and versioning now consistent with architectural constraints |

*End of Tier 1 Fixes*
