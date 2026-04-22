# Event Trigger / Low Turnover Volume-Gated VWAP Pressure Follow-up Expression Family

## Metadata

- Date: `2026-04-22`
- Topic: `event_trigger_low_turnover_volume_gate_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/field-search-packs/2026-04-22-event-trigger-low-turnover-volume-gate.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-catalog.md`

## Hypothesis

Volume spikes should be the right trigger for a low-turnover event alpha, and VWAP pressure may only be useful when it is activated inside those regimes.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `volume`
  - `adv20`
  - `close`
  - `vwap`
  - `industry`
- Assumptions to test:
  - The volume gate should reduce turnover without destroying the signal.
  - `close - vwap` should be a better pressure proxy than raw momentum once it is gated.
  - The first batch should stay simple enough to diagnose sign, gate width, and signal smoothing separately.

## Baseline Expression

```text
trade_when(volume > adv20, group_rank(ts_zscore(close - vwap, 10), industry), -1)
```

## Variant 1

- Goal:
  Fire the volume gate a bit faster in case the high-volume regime decays quickly.
- Main lever:
  Replace the `adv20` gate with a faster `10d` moving-average gate.

```text
trade_when(volume > ts_mean(volume, 10), group_rank(ts_zscore(close - vwap, 10), industry), -1)
```

## Variant 2

- Goal:
  Check whether the event condition should react more slowly.
- Main lever:
  Replace the `adv20` gate with a slower `20d` moving-average gate.

```text
trade_when(volume > ts_mean(volume, 20), group_rank(ts_zscore(close - vwap, 10), industry), -1)
```

## Variant 3

- Goal:
  Check whether the VWAP pressure signal needs a slower normalization window.
- Main lever:
  Keep the `adv20` gate and smooth the pressure signal over `20d` instead of `10d`.

```text
trade_when(volume > adv20, group_rank(ts_zscore(close - vwap, 20), industry), -1)
```

## Current Status

- Latest visible Simulation 20 results for this lane are still weak: Sharpe -1.52, Fitness -0.50, Turnover 42.17%, Returns -4.65%, Drawdown 20.39%, Margin -2.20‱.
- Submit Alpha remains disabled, and no visible Check Submission evidence or non-null `subuniverse_pass` surfaced in the browser session.
- Treat the lane as exploratory until a later variant materially beats this result and shows real submission evidence.

## Expected First Failure

- Sharpe:
  The pressure signal may still be wrong in sign or too common even after gating.
- Fitness:
  Event gating may reduce turnover, but the signal can still be noisy if the gate is too broad.
- Turnover:
  The `10d` gate is the main turnover risk.
- Weight:
  If the event fires on a narrow subset of names, concentration can still become a problem.
- Sub-universe:
  Still unknown until real TEST and submission-style evidence appear.
- Self-correlation:
  Likely lower than the direct momentum family, but not safe yet.

## Optimization Order

1. Test the `adv20` gate first because it is the simplest volume benchmark and keeps the batch interpretable.
2. Compare the faster `10d` and slower `20d` moving-average gates before changing the signal structure.
3. Only if the gate survives should the signal window be smoothed or the volatility fallback be opened.
4. If the lane still looks dead, kill it quickly rather than stretching it into another crowded price-volume clone.

## Next Simulation Batch

- Planned batch:
  `adv20` gate baseline + `10d` gate + `20d` gate + `20d` signal smoother.
- Backup comparison:
  if the pressure signal fails outright, pivot to the volatility fallback signal with `historical_volatility_20` or the return-volatility gate before trying any wider structural changes.
