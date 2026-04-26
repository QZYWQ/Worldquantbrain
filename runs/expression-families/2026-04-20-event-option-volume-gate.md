# Event Option Volume Gate Expression Family

## Metadata

- Date: `2026-04-20`
- Topic: `event_option_volume_gate`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Option sentiment should matter more when the put-to-call volume ratio is actively elevated versus its own recent norm. A simple `trade_when` gate on `pcr_vol_all`, paired with a cross-sectional ranking on put-call skew, is the cheapest way to test that idea.

## Research Contract

- Mechanism: `event_gate`
- Data category: `options`
- Idea type: `event_trigger`
- Universe: `TOP3000`
- Liquidity fit: `sparse_event_acceptable`
- Holding frequency: `event`
- Delay: `1`
- Neutralization target: `industry`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `drop_sparse`
- Pasteurization: `enabled`
- Unit handling: `verify`
- Coverage floor: `70%`
- Freshness floor days: `1`
- Factor risk hypothesis: `Primary risk is sparse option activity clustering into a small volatility-sensitive subset, which can leak both liquidity and volatility factor exposure.`
- Kill condition: `Kill the lane if the first dead captured batch plus one materially different local-factory follow-up still fail to produce a queue or official-budget candidate.`

## Validation Design

- Primary test period: `P6M`
- Regime slices: `earnings weeks; non-earnings weeks; high-volatility weeks`
- Liquidity slice: `TOP3000 names with stable listed-options activity`
- Subuniverse gate: `must keep subuniverse check green despite sparse option coverage`
- Factor overlay: `industry plus volatility and liquidity review`
- Comparison controls: `compare the gated OI leg against the sign-flipped leg and one abnormal-intensity gate`
- Promotion rule: `promote only if one anchor and one materially different control both survive local queue selection before spending any official slot`
- Demotion rule: `demote to kill after a dead first batch and an empty materially different local-factory follow-up`

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

## 2026-04-24 Local Factory Follow-Up

- Context:
  The first captured batch was uniformly negative, and the prior local factory queue stayed empty. Only one more local-only screen is justified, and it must test structure rather than nearby window polishing.
- Acceptable follow-up shapes:
  Keep `pcr_vol_all` as the event gate, but only branch into materially different legs: sign flip, abnormal-intensity gate, or gate-acceleration structure.
- Avoid in this lane:
  Do not revive the standalone `pcr_oi_all` direct-rank path, do not add smoothing-only neighbors, and do not broaden into unrelated event or price-volume families.

## Local Factory Options

### Option A

- Goal:
  Test whether the original family failed mainly because the ranking sign was backward while the event gate itself was still the right framing.

```text
trade_when(pcr_vol_all > ts_mean(pcr_vol_all, 20), group_rank(pcr_oi_all, industry), -1)
```

### Option B

- Goal:
  Keep the sign-flipped OI leg, but make the trigger depend on abnormal option-volume intensity rather than a simple level-above-mean gate.

```text
trade_when(ts_zscore(pcr_vol_all, 20) > 0.5, group_rank(pcr_oi_all, industry), -1)
```

### Option C

- Goal:
  Keep the sign-flipped OI leg, but trigger only when short-term option flow is running ahead of its slower baseline.

```text
trade_when(ts_mean(pcr_vol_all, 5) > ts_mean(pcr_vol_all, 20), group_rank(pcr_oi_all, industry), -1)
```

## Local Factory Recommendation

- Recommended path:
  Option B first, then let the local factory mutate around that shape.
- Why:
  It changes both the gate definition and the sign assumption without leaving the `event_option_volume_gate` family, so it is the cleanest remaining probe with material distance from the first four negative branches.

## 2026-04-24 Decision

- Current posture:
  Kill this lane and branch away rather than keep polishing it.
- Evidence:
  The first captured batch stayed negative across all four logged variants, the earlier local factory queue was empty, and the `2026-04-24-event-option-volume-gate-local-factory-003250` run still produced zero queue picks and zero official-budget picks after the last material follow-up seeds were added.
