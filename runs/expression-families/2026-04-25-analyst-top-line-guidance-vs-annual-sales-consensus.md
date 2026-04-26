# Analyst Top-Line Guidance vs Annual Sales Consensus Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `analyst-top-line-guidance-vs-annual-sales-consensus`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

When management guidance for annual sales sits away from annual sales consensus, the cross-section may keep repricing the forward top-line outlook for more than one day, especially when the guidance band is explicit and fully covered.

## Research Contract

- Mechanism: guidance-band disagreement versus annual sales consensus
- Data category: `Analyst`
- Idea type: forward top-line expectation reset
- Universe: `USA / TOP3000`
- Liquidity fit: liquid US equities with analyst coverage
- Holding frequency: daily refresh with short-to-medium memory
- Delay: `1`
- Neutralization target: `Subindustry`
- Decay: `4`
- Truncation: `0.08`
- NaN policy: `OFF`
- Pasteurization: `ON`
- Unit handling: `VERIFY`
- Coverage floor: `95%`
- Freshness floor days: satisfied by the live official field re-check in this session
- Factor risk hypothesis: the band may collapse into a generic analyst consensus proxy if the gap is not the real driver.
- Kill condition: freeze the family if the midpoint gap, max gap, min gap, and spread-width control all fail to show a plausible direction in the first batch.

## Validation Design

- Primary test period: `1Y0M`
- Regime slices: keep the first batch minimal; no extra slicing before the direction read
- Liquidity slice: `TOP3000` first
- Subuniverse gate: required before any submit posture
- Factor overlay: compare against generic analyst consensus crowding, not the frozen EPS/cashflow/model shells
- Comparison controls: midpoint gap, sign flip, max gap, min gap
- Promotion rule: continue only if the sign-flipped control or one of the one-sided gaps is directionally credible and the family does not immediately look crowded
- Demotion rule: stop if the family only survives through cosmetic expression edits

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `sales_max_guidance_value`
  - `sales_min_guidance_value`
  - `sales_estimate_average_annual`
- Equivalent fallback fields:
  - none yet; the verified trio already covers the family
- Unconfirmed assumptions:
  - The guidance midpoint is the best first anchor.
  - The spread-width control will help distinguish conviction from noise.

## Baseline Expression

```text
0.5 * (rank(sales_max_guidance_value) + rank(sales_min_guidance_value)) - rank(sales_estimate_average_annual)
```

## Variant 1

- Goal: Test the sign immediately because the baseline can easily point the wrong way.
- Main lever: flip the midpoint gap sign and keep the same normalization.

```text
-1 * (0.5 * (rank(sales_max_guidance_value) + rank(sales_min_guidance_value)) - rank(sales_estimate_average_annual))
```

## Variant 2

- Goal: Test the upper-edge guidance gap directly.
- Main lever: replace the midpoint with the max guidance bound.

```text
rank(sales_max_guidance_value) - rank(sales_estimate_average_annual)
```

## Variant 3

- Goal: Test the lower-edge guidance gap directly.
- Main lever: replace the midpoint with the min guidance bound.

```text
rank(sales_min_guidance_value) - rank(sales_estimate_average_annual)
```

## Expected First Failure

- Sharpe: the rank-normalized gap may still be directionally wrong or too weak.
- Fitness: the family may be sensible but still too shallow after penalties.
- Turnover: not expected to be the first blocker.
- Weight: the signal could concentrate in a narrow large-cap or high-coverage subset.
- Sub-universe: unknown until a real official batch exists.
- Self-correlation: the main risk is generic analyst crowding, not a frozen-family shell.

## Optimization Order

1. Test the midpoint guidance gap first.
2. Compare the two one-sided gap controls before any smoothing or grouping idea.
3. Use the spread-width control only as a diagnostic, not as a new family.

## Next Simulation Batch

- Baseline: `0.5 * (rank(sales_max_guidance_value) + rank(sales_min_guidance_value)) - rank(sales_estimate_average_annual)`
- Variant 1: `-1 * (0.5 * (rank(sales_max_guidance_value) + rank(sales_min_guidance_value)) - rank(sales_estimate_average_annual))`
- Variant 2: `rank(sales_max_guidance_value) - rank(sales_estimate_average_annual)`
- Variant 3: `rank(sales_min_guidance_value) - rank(sales_estimate_average_annual)`

## Current Decision

- Winner family: `analyst-top-line-guidance-vs-annual-sales-consensus`
- Official batch status: the batch is complete; the first raw-gap attempt returned a unit-verify warning, and the family is now frozen after a weak sign-flip control plus weak one-sided gap controls.
- Reason: the live official field re-check is clean enough to justify a minimal first batch, and the lane is distinct from the frozen EPS / cashflow / operating-income / model-relative-valuation branches.
