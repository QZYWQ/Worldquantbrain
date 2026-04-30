# Skill Candidate: Gate-Targeted Near-Miss Rescue

## Scope Guardrail

This file proposes workflow-level heuristics for the WorldQuant BRAIN alpha engineering skill. Do not hard-code the specific fields `sales_estimate_count` or `high/low/close` into the skill as permanent recipes.

## Source Artifacts

- `runs/learning-loops/2026-04-30-two-alpha-rescue-project-lessons.md`
- `runs/submission-memos/2026-04-30-sales-estimate-count-decay10-submitted.md`
- `runs/submission-memos/2026-04-30-llgowzmn-pv-range-close-position-ready.md`
- `runs/simulation-captures/2026-04-30-unsubmitted-near-miss-filter.md`

## Candidate Skill Rule

When rescuing a near-miss alpha, classify the dominant failing gate before changing the expression:

- If Fitness is slightly low on a slow count / coverage field, try simplifying and shortening the smoothing window before adding group transforms.
- If Sub-universe Sharpe is slightly low on an otherwise strong price-volume family, try a coherent stability repair: lengthen the core measurement window and increase decay smoothing slightly.
- If self-correlation passes but with a narrow margin, submit or protect only the best family representative and suppress near-neighbor variants.

## Anti-Pattern To Add

Do not keep polishing a family after one clean representative passes official checks. Same-family near-misses should become evidence, not additional submission targets, unless the first representative later fails fresh official evidence.

## Why This Belongs In Skill Later

The reusable point is not the specific alpha formula. The reusable point is that near-miss rescue should be a one-lever response to the failing check:

- Fitness rescue should improve reward per turnover / drawdown without adding unrelated complexity.
- Sub-universe rescue should improve robustness before changing the thesis.
- Self-correlation risk should trigger family locking, not more same-family submissions.

## Promotion Posture

- Status: `HOLD`
- Recommendation: keep as skill-candidate material until another future rescue confirms the same gate-targeted pattern on a different information source.
