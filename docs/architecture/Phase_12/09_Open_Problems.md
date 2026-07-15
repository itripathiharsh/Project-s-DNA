================================================================================
# 09 Open Problems
================================================================================

# Open Problems

## Purpose

Project DNA faces several hard problems that are not fully solved. This document catalogs them as honest admissions of limitation and invitations for contribution.

---

## Problem 1: The Hallucination Ceiling

**Problem:** Even with perfect grounding, LLMs occasionally hallucinate. As the reasoning pipeline grows more complex (synthesis, prediction), the hallucination risk compounds.

**Current approach:** Confidence scoring, evidence citations, human-in-the-loop validation.

**Open question:** Can we prove that an insight is supported by evidence? Is there a formal verification approach for LLM-grounded claims?

## Problem 2: The Repository Scale Problem

**Problem:** Large monorepos (100K+ files) strain the SCM and reasoning pipeline. Full analysis can take hours.

**Current approach:** Incremental analysis, paginated queries, lazy loading.

**Open question:** Can we build a truly incremental SCM that only re-analyzes the delta of a commit, with correct propagation through the dependency graph?

## Problem 3: The Novelty Problem

**Problem:** DNA answers questions that are answerable from the codebase. It cannot answer questions that require external context (business strategy, user feedback, team dynamics).

**Current approach:** Clearly scope what DNA can and cannot answer. Surface confidence scores.

**Open question:** How do we integrate human knowledge (documentation, ADRs, meeting notes) into the cognitive model without polluting it?

## Problem 4: The Evaluator Problem

**Problem:** Evaluating whether an insight is "correct" requires a human expert who already knows the answer. This makes benchmarking slow and expensive.

**Current approach:** Curated benchmark of 100 Q/A pairs. Manual review for model comparisons.

**Open question:** Can we build automated evaluators that approximate human judgment? Can we use one LLM to evaluate another's output reliably?

## Problem 5: The Privacy Paradox

**Problem:** The most valuable insights require the most data (full repository content, developer activity, team structure). Collecting this data raises privacy and security concerns.

**Current approach:** Local-first architecture. Data never leaves the user's machine in V1.

**Open question:** Can we build privacy-preserving analytics (differential privacy, federated learning) for cross-organization insights without centralizing data?
