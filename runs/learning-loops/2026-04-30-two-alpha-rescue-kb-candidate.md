# KB Candidate: Near-Miss Rescue Patterns From Two Successful Alphas

## Scope

This is candidate material for the external knowledge base. It should not be promoted as a universal rule until more families confirm it, but it is strong enough to reuse inside this project.

## Pattern 1: Slow Count Field Fitness Rescue

When a slow coverage / count field has acceptable Sharpe and turnover but fails Fitness, first test a shorter decay plus simple cross-sectional rank before adding group-rank structure.

Observed successful example:

```text
rank(ts_decay_linear(sales_estimate_count, 10))
```

Why it worked:

- kept the hypothesis clean: analyst coverage intensity
- kept turnover low
- avoided adding a group transform that did not directly solve Fitness
- passed official Fitness and self-correlation

Boundary:

- once submitted, do not keep mining cosmetic count-field siblings from the same field
- same field plus nearby windows should be treated as family-neighbor risk

## Pattern 2: Price-Volume Sub-Universe Rescue

When a price-volume range-position alpha already has strong Sharpe and Fitness but narrowly fails Sub-universe, first stabilize the signal by lengthening the measurement window and decay together.

Observed successful transition:

```text
20d range / vol window + decay 9
```

to:

```text
30d range / vol window + decay 12
```

Why it worked:

- preserved the same economic thesis
- reduced unstable short-horizon noise
- improved Sub-universe behavior
- lowered turnover from the failing seed

Boundary:

- this is not permission to sweep every nearby window
- once a clean representative passes self-correlation, suppress same-family siblings

## General Rescue Rule

Classify the failing gate first:

- `LOW_FITNESS` on slow count field: simplify, shorten, rank.
- `LOW_SUB_UNIVERSE_SHARPE` on price-volume family: stabilize window and smoothing.
- `SELF_CORRELATION` risk after one representative passes: stop same-family submissions and branch to a new information source.

## Evidence Trace

- `A1g6AlWg`: `rank(ts_decay_linear(sales_estimate_count, 10))`, official pre-submission checks passed.
- `LLgOWZmn`: range-close-position 30d / decay12 variant, official checks passed, self-correlation `0.6392 / 0.7`.
- `KPXaX5Yz`: 20d / decay9 seed failed only Sub-universe before successful rescue.

## Promotion Posture

- Project rule: use immediately.
- External KB: promote after one more non-overlapping family confirms the failure-targeted rescue pattern.
- Skill: promote only the gate-targeted rescue discipline, not field names.
