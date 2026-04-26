# Model Growth Potential Rerating Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `model_growth_potential_rerating`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `D1`

## Hypothesis

Recent changes in the model-layer growth potential rank may identify cross-sectional rerating before that repricing is fully reflected in the stock cross-section.

## Research Contract

- Mechanism: growth-model rerating
- Data category: `Model`
- Idea type: cross-sectional rerating / repricing
- Universe: `USA / TOP3000`
- Liquidity fit: liquid US equities with full field coverage
- Holding frequency: daily refresh with short-to-medium memory
- Delay: `1`
- Neutralization target: `industry`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `OFF`
- Pasteurization: `ON`
- Unit handling: `VERIFY`
- Coverage floor: `0.95`
- Freshness floor days: satisfied by the live official API read in this session
- Factor risk hypothesis: the line may inherit generic growth-factor exposure if the derivative behaves like a broad rerating proxy
- Kill condition: kill the family if fresh official recheck no longer shows high coverage or if baseline plus sign control both fail to establish a plausible direction in the first batch

## Validation Design

- Primary test period: default full official run once live access is restored
- Regime slices: keep the first batch minimal; no extra regime slicing before a direction read
- Liquidity slice: rely on `TOP3000` first
- Subuniverse gate: required before any submit posture
- Factor overlay: compare against generic growth-model crowding, not against the frozen EPS/cashflow lanes
- Comparison controls:
  - sign control
  - time-rank stabilization
  - no-group control
- Promotion rule: continue only if the first batch shows a credible direction and does not immediately look like a crowded growth echo
- Demotion rule: stop if only cosmetic variants survive or if fresh official access remains unavailable

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `growth_potential_rank_derivative`
  - `multi_factor_static_score_derivative`
  - `multi_factor_acceleration_score_derivative`
- Equivalent fallback fields:
  - `multi_factor_static_score_derivative`
  - `multi_factor_acceleration_score_derivative`
- Unconfirmed assumptions:
  - No live simulation has been run for this family in this session.

## Baseline Expression

```text
group_rank(growth_potential_rank_derivative, industry)
```

## Variant 1

- Goal:
  Establish the correct sign immediately instead of polishing the wrong direction.
- Main lever:
  Sign only.

```text
group_rank(-growth_potential_rank_derivative, industry)
```

## Variant 2

- Goal:
  Stabilize a potentially bursty derivative field without changing the source.
- Main lever:
  Add a short time-rank memory.

```text
group_rank(ts_rank(growth_potential_rank_derivative, 20), industry)
```

## Variant 3

- Goal:
  Measure how much the family depends on industry grouping.
- Main lever:
  Remove industry grouping.

```text
rank(growth_potential_rank_derivative)
```

## Expected First Failure

- Sharpe:
  The raw growth rerating field could be too mild if the model update is already mostly priced in.
- Fitness:
  One-field model signals can look sensible but still be too weak after robustness costs.
- Turnover:
  A derivative field can jump in bursts when the underlying model refreshes.
- Weight:
  Without the right grouping, the line could load on a narrow growth cohort.
- Sub-universe:
  Unknown until fresh official simulation and check results exist.
- Self-correlation:
  The main risk is overlap with generic growth-model crowding.

## Optimization Order

1. Determine the sign with the baseline and direct sign control.
2. Test whether short time-rank memory helps more than it hurts.
3. Only then decide whether industry grouping is necessary or overly constraining.

## Next Simulation Batch

- Baseline:
  `group_rank(growth_potential_rank_derivative, industry)`
- Variant 1:
  `group_rank(-growth_potential_rank_derivative, industry)`
- Variant 2:
  `group_rank(ts_rank(growth_potential_rank_derivative, 20), industry)`
- Variant 3:
  `rank(growth_potential_rank_derivative)`

