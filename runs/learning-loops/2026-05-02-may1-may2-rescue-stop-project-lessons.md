# 2026-05-02 May1 / May2 Rescue Stop Project Lessons

## Context

This note records the deep reassessment of two official unsubmitted pools:

- `2026-05-01 EDT`, `UNSUBMITTED`, IS Sharpe `> 1.25`
- `2026-05-02 EDT`, `UNSUBMITTED`, IS Sharpe `> 1.1`

The purpose was to test whether project memory had become too pessimistic, or whether the stop posture was still supported by current official evidence plus public rescue playbooks.

## Main Lesson

The right question is not:

- "Can I still write one more variant?"

The right question is:

- "Did the correct first or second rescue lever materially move the dominant failure?"

If the answer is no, the lane is usually not rescue-worthy for current official budget.

## Reconfirmed Stop Patterns

### 1. Structural concentration is not a near-pass

Observed again across:

- `multi_factor_acceleration_score_derivative`
- `multi_factor_static_score_derivative`
- `relative_valuation_rank_derivative`
- `growth_potential_rank_derivative`
- older `composite_factor_score_derivative` evidence

Practical pattern:

- `CONCENTRATED_WEIGHT` around `0.50 / 0.10` or still above cutoff after repair
- tiny long / short books such as `1 / 15`, `0 / 4`, `0 / 5`
- headline Sharpe / Fitness can still look excellent

Carry-forward rule:

- Do not call these lines "almost passable."
- One breadth-forcing diagnostic is enough.
- If breadth stays tiny or concentration stays above cutoff, stop the same-family rescue path.

### 2. Correct turnover repair failing to move turnover means the lane is structurally blocked

Observed again in the May1 / May2 `fscore` family:

- baseline had extreme Sharpe / Fitness
- first correct repair was smoothing / decay
- the decay10 repair left Turnover at `100%` and Weight still failed

Carry-forward rule:

- If the first proper turnover-repair lever leaves turnover essentially unchanged, stop.
- Do not continue with rank/group/truncation cosmetics unless a genuinely different holding mechanism exists.

### 3. Near-pass Sub-universe misses deserve only bounded rescue

Observed again in:

- `rank(-ts_corr(ts_zscore(fnd2_a_consinprogressg, 51), systematic_risk_last_90_days, 76))`

Pattern:

- sign-flip repaired the direction
- light compression improved Sub-universe but not enough
- stronger grouping repaired Sub-universe only by killing Sharpe / Fitness

Carry-forward rule:

- A near-pass Sub-universe miss is real, but not open-ended.
- One light compression test and one group-relative test are usually enough.
- If the group-relative test kills the core signal, stop the lane unless a new gating mechanism is introduced.

### 4. Broad but low-Fitness risk lanes should not be endlessly polished

Observed again in:

- `unsystematic_risk_last_360_days`

Pattern:

- the lane was broad enough to avoid the tiny-book trap
- rank / group-rank / smoothing / truncation all helped partially
- best Fitness still stayed below `1`

Carry-forward rule:

- When a broad line repeatedly clusters just below Fitness after the obvious repairs, hold it for future conditional gating ideas.
- Do not keep spending budget on lookback order, truncation, or wrapper permutations alone.

## Portfolio-Level Lesson

A pool can contain many rows with Sharpe above threshold and still contain no good rescue target.

The reason is that official rescue value depends on failure shape, not headline Sharpe rank:

- structural concentration rows are usually lower value than broad but weaker rows
- same-family clones with `SELF_CORRELATION PENDING` should not be promoted just because they are numerically strong
- after one or two proper rescue probes, the expected value of more same-family polishing drops sharply

## Operational Rule

For future unsubmitted-pool cleanup:

1. classify by dominant failing check and family
2. prefer new information source over same-family cosmetics
3. allow at most one or two targeted rescue probes per lane
4. if the dominant failure is unchanged after the correct probe, stop and rotate

## Related Artifacts

- `runs/submission-memos/2026-05-02-may1-may2-rescue-deep-review.md`
- `runs/submission-memos/2026-05-02-fscore-value-growth-rescue-blocked.md`
- `runs/submission-memos/2026-05-02-close-delta-3d-decay10-rescue-stop.md`
- `runs/submission-memos/2026-05-01-fnd2-signflip-and-static-score-rescue-stop.md`
- `runs/submission-memos/2026-05-01-unsystematic-risk-360-rescue-blocked.md`

