# Event Trigger / Low Turnover Volatility-Gated Pressure Follow-up Expression Family

## Metadata

- Date: `2026-04-22`
- Topic: `event_trigger_low_turnover_volatility_gate_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/field-search-packs/2026-04-22-event-trigger-low-turnover-volatility-gate.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-catalog.md`

## Hypothesis

The pressure signal that failed under a volume gate may only work when it is activated inside high-volatility regimes instead of quiet tape.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `historical_volatility_20`
  - `close`
  - `vwap`
  - `industry`
  - `returns`
- Equivalent fallback fields:
  - `ts_std_dev(returns, d)` as an operator-derived volatility gate
- Unconfirmed assumptions:
  - The volatility gate should reduce turnover without destroying the signal.
  - `close - vwap` should be more meaningful inside high-volatility regimes.
  - The first batch should stay simple enough to diagnose gate width and signal smoothing separately.

## Baseline Expression

```text
trade_when(ts_rank(historical_volatility_20, 20) > 0.5, group_rank(ts_zscore(close - vwap, 10), industry), -1)
```

## Variant 1

- Goal:
  Fire the gate faster in case the volatility regime changes quickly.
- Main lever:
  Use a shorter `10d` rank window on `historical_volatility_20`.

```text
trade_when(ts_rank(historical_volatility_20, 10) > 0.5, group_rank(ts_zscore(close - vwap, 10), industry), -1)
```

## Variant 2

- Goal:
  Check whether the gate should react more slowly.
- Main lever:
  Use a longer `30d` rank window on `historical_volatility_20`.

```text
trade_when(ts_rank(historical_volatility_20, 30) > 0.5, group_rank(ts_zscore(close - vwap, 10), industry), -1)
```

## Variant 3

- Goal:
  Check whether the signal itself needs a slower normalization window.
- Main lever:
  Keep the `20d` volatility gate and smooth the pressure signal over `20d` instead of `10d`.

```text
trade_when(ts_rank(historical_volatility_20, 20) > 0.5, group_rank(ts_zscore(close - vwap, 20), industry), -1)
```

## Expected First Failure

- Sharpe:
  The pressure leg may still be wrong in sign or too common even after gating.
- Fitness:
  The gate may narrow turnover, but the signal can still be noisy.
- Turnover:
  The gate could still be too broad if volatility is elevated too often.
- Weight:
  Concentration can still show up if the event only fires on a narrow subset of names.
- Sub-universe:
  This is still unknown until real submission-style evidence appears.
- Self-correlation:
  Probably lower than the dead always-on price-volume lane, but not safe yet.

## Optimization Order

1. Test the `20d` volatility gate first because it is the simplest benchmark and keeps the batch interpretable.
2. Compare the faster `10d` and slower `30d` windows before changing the signal structure.
3. Only if the gate survives should the signal window be smoothed or the returns-based backup be opened.
4. If the lane still looks dead, kill it quickly rather than stretching it into another crowded clone.

## Next Simulation Batch

- Planned batch:
  `20d` gate baseline + `10d` gate + `30d` gate + `20d` signal smoother.
- Backup comparison:
  if the field-based gate fails outright, pivot to the `returns` volatility gate before trying any wider structural changes.

## Batch 01 Update

- Simulation 2's `10d` gate was the least-bad result in the batch:
  `trade_when(ts_rank(historical_volatility_20, 10) > 0.5, group_rank(ts_zscore(close - vwap, 10), industry), -1)`
- It improved the baseline only modestly, landing at `Sharpe -1.19 / Fitness -0.37 / Turnover 41.37% / Returns -3.92% / Drawdown 18.14% / Margin -1.90‱`.
- Simulation 1 baseline remained worse on Sharpe and Fitness than the `10d` gate, but still decisively negative:
  `Sharpe -1.37 / Fitness -0.47 / Turnover 37.49% / Returns -4.36% / Drawdown 18.60% / Margin -2.33‱`.
- Simulation 3's slower `30d` gate reduced turnover but weakened the signal further:
  `Sharpe -1.46 / Fitness -0.52 / Turnover 36.40% / Returns -4.69% / Drawdown 19.39% / Margin -2.58‱`.
- Simulation 4's slower signal smoother was the weakest variant in the batch:
  `Sharpe -1.75 / Fitness -0.67 / Turnover 38.02% / Returns -5.50% / Drawdown 22.64% / Margin -2.89‱`.
- No visible `Check Submission` evidence or non-null `subuniverse_pass` appeared for any member of the batch, and `Submit Alpha` stayed disabled.

## Decision

- Kill the field-based volatility-gated pressure branch.
- Do not continue polishing `historical_volatility_20` gate timing or the `close - vwap` smoother.
- If this event-trigger idea is still worth preserving, switch the baseline to the `returns`-based volatility gate rather than adding more complexity to the dead field-based line.

## Batch 02 Update

- The returns-based fallback batch also failed to rescue the lane.
- Simulation 4's `20d` returns-volatility gate baseline was the least-bad visible result in the batch, landing at `Sharpe -0.74 / Fitness -0.18 / Turnover 37.70% / Returns -2.26% / Drawdown 10.96% / Margin -1.20‱`.
- Simulation 1's faster `10d` gate stayed negative and raised turnover:
  `Sharpe -0.79 / Fitness -0.18 / Turnover 44.47% / Returns -2.41% / Drawdown 15.70% / Margin -1.08‱`.
- Simulation 2's slower `30d` gate was worse than the baseline:
  `Sharpe -1.09 / Fitness -0.31 / Turnover 43.23% / Returns -3.47% / Drawdown 18.38% / Margin -1.60‱`.
- Simulation 3's `20d` smoother on the VWAP-pressure leg was the weakest variant:
  `Sharpe -1.34 / Fitness -0.42 / Turnover 43.32% / Returns -4.31% / Drawdown 19.07% / Margin -1.99‱`.
- No visible `Check Submission` evidence or non-null `subuniverse_pass` appeared for any member of the batch, and `Submit Alpha` stayed disabled.

## Final Decision

- Kill the entire event-trigger / VWAP-pressure volatility lane.
- Do not continue polishing the returns-based fallback or the original `historical_volatility_20` line.
- Rotate to a different KB-backed family next, with sentiment/news attention as the next live lane.
