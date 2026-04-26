# Analyst Actual Sales Vs Annual Sales Consensus Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `analyst_actual_sales_vs_annual_sales_consensus`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Realized annual sales surprise versus annual sales consensus may reprice the cross-section when actual top-line results land above or below expectations.

## Research Contract

- Mechanism: realized annual sales surprise vs annual consensus
- Data category: `Analyst`
- Idea type: top-line expectation reset
- Universe: `USA / TOP3000`
- Liquidity fit: liquid US equities with broad analyst coverage
- Holding frequency: daily refresh with no added time-series memory in the baseline
- Delay: `1`
- Neutralization target: `industry`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `OFF`
- Pasteurization: `ON`
- Unit handling: `VERIFY`
- Coverage floor: `95%`
- Freshness floor days: `90`
- Factor risk hypothesis: the line can collapse into a size or generic analyst-coverage effect if the actual/consensus gap is not the real driver.
- Kill condition: freeze the family if the baseline and sign control both fail, or if only normalization tricks survive.

## Validation Design

- Primary test period: `1Y0M`
- Regime slices: none before the first direction read
- Liquidity slice: `TOP3000` first
- Subuniverse gate: required before any submit posture
- Factor overlay: compare against the frozen guidance-band shell and the frozen EPS / cashflow / model branches
- Comparison controls: sign control, raw-gap control, rank-normalized gap control
- Promotion rule: continue only if the first batch is directionally credible and not obviously crowded
- Demotion rule: stop if the family only survives through cosmetic normalization

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `actual_sales_value_annual`
  - `sales_estimate_average_annual`
- Equivalent fallback fields:
  - none yet; keep the annual pair as the primary lane
- Unconfirmed assumptions:
  - The actual/consensus ratio is the cleanest first anchor.
  - Industry neutralization is sufficient for the first batch.

## Baseline Expression

```text
group_rank(actual_sales_value_annual / sales_estimate_average_annual - 1, industry)
```

## Variant 1

- Goal: Test the sign immediately if the baseline points the wrong way.
- Main lever: sign only.

```text
group_rank(-(actual_sales_value_annual / sales_estimate_average_annual - 1), industry)
```

## Variant 2

- Goal: Test whether the raw same-unit gap is cleaner than the ratio surprise.
- Main lever: ratio to difference.

```text
group_rank(actual_sales_value_annual - sales_estimate_average_annual, industry)
```

## Variant 3

- Goal: Diagnostic control only, not the primary first-batch lever.
- Main lever: rank-normalize each leg before comparing them.

```text
group_rank(rank(actual_sales_value_annual) - rank(sales_estimate_average_annual), industry)
```

## Expected First Failure

- Sharpe: the surprise may be real but too weak after cross-sectional ranking.
- Fitness: the family may be directionally sensible but still below continuation floor.
- Turnover: should stay moderate because the anchor updates slowly.
- Weight: large-cap or analyst-covered clusters may dominate the signal.
- Sub-universe: unknown until a real official batch exists.
- Self-correlation: the main danger is analyst crowding, not a frozen-shell reuse.

## Optimization Order

1. Establish sign on the ratio surprise.
2. Compare the raw-gap control against the ratio baseline.
3. Use the rank-normalized gap only if the family stays alive after the first read.

## Next Simulation Batch

- Baseline:
  `group_rank(actual_sales_value_annual / sales_estimate_average_annual - 1, industry)`
- Variant 1:
  `group_rank(-(actual_sales_value_annual / sales_estimate_average_annual - 1), industry)`
- Variant 2:
  `group_rank(actual_sales_value_annual - sales_estimate_average_annual, industry)`
- Variant 3:
  `group_rank(rank(actual_sales_value_annual) - rank(sales_estimate_average_annual), industry)`
