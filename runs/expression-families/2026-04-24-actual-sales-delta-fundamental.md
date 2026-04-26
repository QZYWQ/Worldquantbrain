# Actual Sales Delta Fundamental Expression Family

## Metadata

- Date: `2026-04-24`
- Topic: `actual_sales_delta_fundamental`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Reported sales changes should help same-industry peers re-rank over a slow horizon, and the live official Data Explorer search in this session found a low-crowding analyst4 actual-sales field with near-full coverage.

## Research Contract

- Mechanism: slow top-line delta on actual reported sales
- Data category: analyst4 actual sales values
- Idea type: fundamentals-first
- Universe: USA / TOP3000
- Liquidity fit: liquid US equities with enough coverage for a slow delta signal
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
- Factor risk hypothesis: the field is healthy enough to start, but quarterly update cadence and industry clustering can still create sub-universe fragility.
- Kill condition: if the sign control fails and the 126d control does not beat the baseline cleanly, freeze the family.

## Validation Design

- Primary test period: 1Y
- Regime slices: 2020-2021, 2022-2023
- Liquidity slice: top3000 liquid names only
- Subuniverse gate: require a real sub-universe check before any packaging claim
- Factor overlay: compare against the old revenue/sales delta lane and the analyst EPS siblings
- Comparison controls: sign-inverted control, 126d control, annual actual-sales control
- Promotion rule: promote only if sign, horizon, and subuniverse all improve without an obvious turnover penalty
- Demotion rule: demote to hold after one failed sign control or repeated full-IS weakness

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `actual_sales_value_quarterly`
  - `actual_sales_value_annual`
- Equivalent fallback fields:
  - `sales_growth`
  - `revenue`
- Unconfirmed assumptions:
  - The quarterly actual-sales field is the best primary anchor.
  - `63d` is the right first baseline before extra smoothing.
  - `industry` grouping is the right first-pass neutralization.

## Baseline Expression

```text
group_rank(ts_delta(actual_sales_value_quarterly, 63), industry)
```

## Variant 1

- Goal: Test the thesis sign directly before doing anything else.
- Main lever: Sign only, holding field and horizon fixed.

```text
group_rank(-ts_delta(actual_sales_value_quarterly, 63), industry)
```

## Variant 2

- Goal: Check whether a faster window captures the move better.
- Main lever: Horizon from `63` to `21`.

```text
group_rank(ts_delta(actual_sales_value_quarterly, 21), industry)
```

## Variant 3

- Goal: Check whether a slower window is better for this slow fundamentals thesis.
- Main lever: Horizon from `63` to `126`.

```text
group_rank(ts_delta(actual_sales_value_quarterly, 126), industry)
```

## Expected First Failure

- Sharpe: The sign may still be wrong, or the cadence may be too slow.
- Fitness: Sparse effective coverage after grouping can still make the family look weak.
- Turnover: This is unlikely to be the first blocker.
- Weight: A small number of industries may dominate the useful signal.
- Sub-universe: This is the main structural risk to watch first.
- Self-correlation: Unknown until a real official check exists.

## Optimization Order

1. Test sign first.
2. Compare `21d`, `63d`, and `126d` before changing fields.
3. Only after the actual-sales branch proves viable should the family consider an annual control or a fallback to `sales_growth`.

## Next Simulation Batch

- Baseline: `group_rank(ts_delta(actual_sales_value_quarterly, 63), industry)`
- Variant 1: `group_rank(-ts_delta(actual_sales_value_quarterly, 63), industry)`
- Variant 2: `group_rank(ts_delta(actual_sales_value_quarterly, 21), industry)`
- Variant 3: `group_rank(ts_delta(actual_sales_value_quarterly, 126), industry)`


## Batch 01 Official Results

- Baseline `group_rank(ts_delta(actual_sales_value_quarterly, 63), industry)` finished with IS Sharpe 0.35, Fitness 0.13, and a negative holdout. Freeze this family.
- Sign control `group_rank(-ts_delta(actual_sales_value_quarterly, 63), industry)` flipped holdout positive, but it failed IS and the low-sub-universe-sharpe gate. Freeze this family.
- 21d control `group_rank(ts_delta(actual_sales_value_quarterly, 21), industry)` was essentially flat. Freeze this family.
- 126d control `group_rank(ts_delta(actual_sales_value_quarterly, 126), industry)` improved IS a little, but holdout still turned negative. Freeze this family.
- Annual actual-sales control was not run because the family froze after the first batch.
- Submission posture: frozen; do not spend more budget here unless a genuinely new actual-sales field source appears.
- Next active line: `operating_income_history_position`.
