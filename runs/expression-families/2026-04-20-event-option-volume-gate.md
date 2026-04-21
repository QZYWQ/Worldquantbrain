# Event Option Volume Gate Expression Family

## Metadata

- Date: `2026-04-20`
- Topic: `event_option_volume_gate`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Option sentiment should matter more when the put-to-call volume ratio is actively elevated versus its own recent norm. A simple `trade_when` gate on `pcr_vol_all`, paired with a cross-sectional ranking on put-call skew, is the cheapest way to test that idea.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `pcr_vol_all`
  - `pcr_oi_all`
- Unconfirmed assumptions:
  - Lower put-call ratio should be directionally better than higher put-call ratio once the gate says option flow is active.
  - The current simulate workspace still handles `trade_when(..., ..., -1)` normally.
  - `industry` remains a reasonable first comparison frame before testing more granular group structure.

## Baseline Expression

```text
trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 20), group_rank(-pcr_oi_all, industry), -1)
```

## Variant 1

- Goal:
  Fire the event gate a bit faster in case the option-volume shock decays more quickly than the 20-day mean comparison.
- Main lever:
  Gate window from `20` to `10`.

```text
trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 10), group_rank(-pcr_oi_all, industry), -1)
```

## Variant 2

- Goal:
  Keep the same gate but use the volume-ratio field itself as the ranking leg, which tests whether the fresher field contains enough signal without the slower OI sibling.
- Main lever:
  Signal field from `pcr_oi_all` to `pcr_vol_all`.

```text
trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 20), group_rank(-pcr_vol_all, industry), -1)
```

## Variant 3

- Goal:
  Keep the same gate and slower OI thesis, but smooth the ranking leg slightly so the active positions are less sensitive to one noisy daily observation.
- Main lever:
  Signal structure from raw `pcr_oi_all` to `ts_mean(pcr_oi_all, 5)`.

```text
trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 20), group_rank(-ts_mean(pcr_oi_all, 5), industry), -1)
```

## Expected First Failure

- Sharpe:
  The sign may still be wrong if elevated put-call ratio is a continuation warning instead of a contrarian signal.
- Fitness:
  Sparse coverage and gated participation may limit robustness even if one branch becomes directionally positive.
- Turnover:
  The 10-day gate is the main turnover risk.
- Weight:
  If option activity clusters in a narrow subset of names, concentration could become the first hard stop.
- Sub-universe:
  The first structural bottleneck is likely sub-universe or other sparse-coverage behavior because both confirmed fields cover only about `70%` of `TOP3000`.
- Self-correlation:
  Less likely than in the buzz lane, but still must be read from real platform output.

## Optimization Order

1. Run the first gated batch unchanged and check whether sign, coverage, or concentration fails first.
2. If sign is wrong, flip the signal sign before adding more gate logic.
3. If sparse coverage dominates immediately, do not over-polish this lane; branch again instead of piling on complexity.

## Next Simulation Batch

- Baseline:
  `trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 20), group_rank(-pcr_oi_all, industry), -1)`
- Variant 1:
  `trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 10), group_rank(-pcr_oi_all, industry), -1)`
- Variant 2:
  `trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 20), group_rank(-pcr_vol_all, industry), -1)`
- Variant 3:
  `trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 20), group_rank(-ts_mean(pcr_oi_all, 5), industry), -1)`
