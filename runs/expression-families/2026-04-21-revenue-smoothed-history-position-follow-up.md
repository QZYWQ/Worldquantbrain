# Revenue Smoothed History Position Follow-up Expression Family

## Metadata

- Date: `2026-04-21`
- Topic: `revenue_smoothed_history_position_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/field-search-packs/2026-04-21-sales-delta-fundamental.md`

## Hypothesis

A top-line revenue signal might become more stable if we smooth it before the long history rank, but the branch should only stay alive if the smoother plus long-rank structure improves on the already weak revenue-delta lane.

## Confirmed Or Assumed Inputs

- Confirmed platform field:
  - `revenue`
- Confirmed neutralization:
  - `industry`
- Assumptions to test:
  - Revenue may need a slower smoothing window than the raw delta family.
  - If the 63d baseline is weak, a slower control may still be worth one check.
  - If both windows stay weak, the branch should be killed quickly instead of polishing a sparse top-line lane.

## Baseline Expression

```text
group_rank(ts_rank(ts_mean(revenue, 63), 504), industry)
```

## Variant 1

- Goal:
  Test whether a slower revenue smoother improves stability and Fitness.
- Main lever:
  Increase the smoothing window from `63` to `126`.

```text
group_rank(ts_rank(ts_mean(revenue, 126), 504), industry)
```

## Batch 01 Update

- The `63d` baseline landed at `Sharpe 0.31 / Fitness 0.11 / Turnover 3.22% / Returns 1.70% / Drawdown 12.35% / Margin 10.57‱`.
- Year-by-year behavior was unstable, with `2022` negative on both Sharpe and Fitness.
- `Submit Alpha` stayed disabled and no visible `Check Submission` or non-null subuniverse evidence appeared.
- This was already far below the stronger operating-income ridge, so the revenue family remained exploratory only.

## Batch 02 Update

- The `126d` probe weakened further to `Sharpe 0.19 / Fitness 0.06 / Turnover 2.52% / Returns 1.05% / Drawdown 12.45% / Margin 8.30‱`.
- The slower smoother did not rescue the line; it reduced turnover, but it also gave back Sharpe, Fitness, returns, and margin.
- `Submit Alpha` stayed disabled and no visible `Check Submission` or non-null subuniverse evidence appeared.
- The revenue smoothed-history branch should be killed and replaced with a different information source or a different neutralization lever.

## Expected First Failure

- Sharpe:
  The revenue signal may still be too slow and too noisy to clear the bar.
- Fitness:
  Sparse top-line coverage can keep Fitness weak even when the sign is vaguely positive.
- Turnover:
  This is not the first bottleneck; the family trades slowly already.
- Weight:
  Structural sparsity may still concentrate the effective book.
- Sub-universe:
  Still unknown until real submission-style evidence appears.
- Self-correlation:
  Unknown until live check evidence exists.

## Optimization Order

1. Test the direct sign / horizon shape first.
2. If the slow control does not improve the family, stop polishing revenue and branch away.
3. Prefer a genuinely different information source or a neutralization change over more same-family smoothing.

## Branch Decision

- Kill the revenue smoothed-history family.
- Keep the revenue results as negative reference only.
- Move the next live branch back to a stronger fundamentals or model-dataset lane rather than more revenue smoothing.
