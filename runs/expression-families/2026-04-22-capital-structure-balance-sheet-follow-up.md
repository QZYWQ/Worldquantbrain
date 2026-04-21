# Capital Structure Balance Sheet Follow-up Expression Family

## Metadata

- Date: `2026-04-22`
- Topic: `capital_structure_balance_sheet_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/field-search-packs/2026-04-22-capital-structure-balance-sheet.md`
  - official Data Explorer search results for `fnd6_teq`, `assets`, `liabilities`, `equity`, `assets_curr`, and `liabilities_curr`

## Hypothesis

A slowly improving equity cushion relative to assets should be underreacted by the market, and an industry-relative leverage ratio may capture that signal more cleanly than the earlier earnings and analyst branches.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `fnd6_teq`
  - `assets`
  - `liabilities`
  - `equity`
  - `assets_curr`
  - `liabilities_curr`
- Assumptions to test:
  - A balance-sheet cushion ratio should be easier to interpret than a multi-input blend.
  - A slow `504d` history rank may still be useful because balance-sheet data refreshes slowly.
  - `industry` neutralization is the simplest first control; `subindustry` can be a structure-axis branch if the first batch is alive.

## Baseline Expression

```text
group_rank(ts_rank(ts_mean(fnd6_teq / assets, 63), 504), industry)
```

## Variant 1

- Goal:
  Test whether the sign should be inverted and whether the equity-cushion thesis is directionally correct.
- Main lever:
  Replace the equity-cushion ratio with the leverage complement.

```text
group_rank(ts_rank(ts_mean(liabilities / assets, 63), 504), industry)
```

## Variant 2

- Goal:
  Test whether the signal reacts faster when the smoothing window is shortened.
- Main lever:
  Reduce the smoothing window from `63` to `21`.

```text
group_rank(ts_rank(ts_mean(fnd6_teq / assets, 21), 504), industry)
```

## Variant 3

- Goal:
  Test whether the same ratio behaves better when the comparison frame is tightened.
- Main lever:
  Keep the baseline ratio and swap `industry` for `subindustry`.

```text
group_rank(ts_rank(ts_mean(fnd6_teq / assets, 63), 504), subindustry)
```

## Current Live Probe

- Simulation 17 tested the leverage family with the planned `subindustry` branch:

```text
group_rank(ts_rank(ts_mean(liabilities / assets, 63), 504), subindustry)
```

- IS summary:
  `Sharpe 0.30 / Fitness 0.08 / Turnover 2.43% / Returns 0.99% / Drawdown 6.23% / Margin 8.17‱`
- TEST view:
  `Sharpe 0.62 / Fitness 0.29 / Turnover 2.17% / Returns 2.82% / Drawdown 5.49% / Margin 25.96‱`
- No real `Check Submission` evidence or non-null `subuniverse_pass` appeared, and `Submit Alpha` stayed disabled.

## Expected First Failure

- Sharpe:
  The signal may collapse into a weak value / leverage proxy rather than a true alpha.
- Fitness:
  Balance-sheet ratios can be too stale to survive the full ranking stack.
- Turnover:
  Turnover should be lower than the earnings branches, so this is probably not the first bottleneck.
- Weight:
  Negative-equity or distressed names may dominate if the ratio is not stable.
- Sub-universe:
  Still structurally risky because the verified balance-sheet fields only have `50%` coverage.
- Self-correlation:
  Likely lower than the current operating-income ridge, but this must be verified with real checks.

## Optimization Order

1. Test sign first with the leverage-complement control.
2. If the sign is right, compare `21d` versus the `63d` baseline.
3. If the baseline is still alive, check `subindustry` before inventing extra fields or ratios.
4. If the whole lane is flat, branch to the liquidity fallback (`assets_curr / liabilities_curr`) instead of polishing the same ratio further.

## Next Simulation Batch

- Batch shape:
  baseline, sign control, `21d` time branch, and `subindustry` structure branch.
- Backup branch:
  if the subindustry branch still does not make the lane candidate-ready, test the liquidity ratio family with `assets_curr / liabilities_curr`.


## Liquidity Subindustry Probe

- Simulation 17's liquidity follow-up kept the same slow rank/smoothing stack but switched the neutralization axis to `subindustry`:

```text
group_rank(ts_rank(ts_mean(assets_curr / liabilities_curr, 63), 504), subindustry)
```

- TEST summary:
  `Sharpe 0.39 / Fitness 0.13 / Turnover 2.38% / Returns 1.37% / Drawdown 3.55% / Margin 11.49‱`
- IS summary:
  `Sharpe -0.43 / Fitness -0.14 / Turnover 2.65% / Returns -1.24% / Drawdown 11.89% / Margin -9.33‱`
- Visible testing status:
  `4 PASS / 3 FAIL / 1 PENDING`
- No visible `Check Submission` evidence or non-null `subuniverse_pass` appeared, and `Submit Alpha` stayed disabled.

## Decision

- Kill the capital-structure lane.
- Keep the branch-threshold lesson local for now; it is useful as a workflow rule, but it is not a submission-ready alpha family.
