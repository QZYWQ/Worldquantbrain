# Skill Candidate: Post-Submission Self-Correlation Gate

## Scope Guardrail

This is a workflow rule candidate for WorldQuant BRAIN alpha engineering. It should not preserve any specific alpha formula as a reusable recipe.

## Source Artifacts

- `runs/submission-memos/2026-04-30-price-volume-corr-self-corr-stop.md`
- `runs/learning-loops/2026-04-30-self-corr-after-submission-project-lessons.md`
- `runs/simulation-captures/2026-04-30-pv-price-volume-corr-rescue.json`

## Candidate Skill Rule

When a candidate passes all visible checks but has `SELF_CORRELATION: PENDING`, keep it in `near-pass` state. Do not describe it as final submission-ready until self-correlation has been checked against the current submitted alpha set.

If a candidate later fails self-correlation after another alpha is submitted:

- official self-correlation evidence overrides formula-family intuition
- update the original capture or add a superseding memo
- if self-correlation is above `0.95`, stop the branch rather than trying cosmetic lookback, decay, or group changes
- only resume if the next branch changes the core information source or mechanism enough to plausibly reduce realized overlap

## Anti-Pattern To Add

Do not say "these two can both submit" solely because one is price-volume and the other is fundamental / analyst. That distinction is useful for triage, but the platform-level realized self-correlation check is the gate that matters.

## Promotion Posture

- Status: `HOLD`
- Recommendation: promote into the skill after one more future case confirms the same high-self-correlation stop rule on a different candidate pair.
