# Actual EPS Value Close Industry Expression Family

## Metadata

- Date: `2026-04-24`
- Topic: `actual_eps_value_close_industry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Reported EPS levels should help same-industry peers re-rank over a slow horizon, and the live official Data Explorer search in this session found a lower-crowding analyst4 actual-EPS field with full coverage.

## Research Contract

- Mechanism: slow actual EPS level normalized by price
- Data category: analyst4 actual EPS values
- Idea type: fundamentals-first
- Universe: USA / TOP3000
- Liquidity fit: liquid US equities with enough coverage for a slow EPS signal
- Holding frequency: slow / medium-slow
- Delay: 1
- Neutralization target: industry
- Decay: 4
- Truncation: 0.08
- NaN policy: OFF
- Pasteurization: ON
- Unit handling: VERIFY
- Coverage floor: 95%
- Freshness floor days: 90
- Factor risk hypothesis: actual EPS may be episodic, but the field is full coverage and low crowding enough to justify one small batch.
- Kill condition: if the sign control fails and the slower 120d control does not beat the baseline cleanly, freeze the family.

## Validation Design

- Primary test period: 1Y
- Regime slices: 2020-2021, 2022-2023
- Liquidity slice: top3000 liquid names only
- Subuniverse gate: require a real sub-universe check before any packaging claim
- Factor overlay: compare against the analyst EPS estimate family and the broader actual-EPS quarterly alias
- Comparison controls: sign-inverted control, quarterly alias control, slower 120d control
- Promotion rule: promote only if sign, field choice, and subuniverse all improve without an obvious concentration penalty
- Demotion rule: demote to hold after one failed sign control or repeated full-IS weakness

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `anl4_af_eps_value`
  - `actual_eps_value_quarterly`
  - `close`
- Equivalent fallback fields:
  - `eps_estimate_value`
- Unconfirmed assumptions:
  - The price-normalized actual-EPS form is cleaner than the raw level.
  - `60d` is the right first baseline before extra smoothing.
  - `industry` grouping is the right first-pass neutralization.

## Baseline Expression

```text
group_rank(ts_rank(anl4_af_eps_value / close, 60), industry)
```

## Variant 1

- Goal: Test the thesis sign directly before doing anything else.
- Main lever: Sign only, holding field and horizon fixed.

```text
group_rank(-ts_rank(anl4_af_eps_value / close, 60), industry)
```

## Variant 2

- Goal: Check whether the explicit quarterly field alias behaves differently from the shorter analyst4 field.
- Main lever: Field axis from `anl4_af_eps_value` to `actual_eps_value_quarterly`.

```text
group_rank(ts_rank(actual_eps_value_quarterly / close, 60), industry)
```

## Variant 3

- Goal: Check whether a slower memory window improves robustness.
- Main lever: Window axis from `60` to `120`.

```text
group_rank(ts_rank(anl4_af_eps_value / close, 120), industry)
```

## Expected First Failure

- Sharpe:
  The signal may still be too crowded even though the field is cleaner than the older estimate lanes.
- Fitness:
  A fully covered field can still look weak after grouping if the actual-EPS move is too blunt.
- Turnover:
  This is unlikely to be the first blocker because the thesis is intentionally slow.
- Weight:
  A few industries may dominate the useful signal.
- Sub-universe:
  This remains a real risk and needs an official check before any packaging claim.
- Self-correlation:
  Unknown until a real official check exists.

## Optimization Order

1. Test sign first.
2. Compare the shorter actual-EPS field alias against the lower-crowding analyst4 anchor.
3. If the baseline is promising, compare `120d` before changing neutralization or adding more structure.

## Next Simulation Batch

- Baseline: `group_rank(ts_rank(anl4_af_eps_value / close, 60), industry)`
- Variant 1: `group_rank(-ts_rank(anl4_af_eps_value / close, 60), industry)`
- Variant 2: `group_rank(ts_rank(actual_eps_value_quarterly / close, 60), industry)`
- Variant 3: `group_rank(ts_rank(anl4_af_eps_value / close, 120), industry)`
