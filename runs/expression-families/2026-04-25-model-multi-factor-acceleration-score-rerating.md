# Model Multi-Factor Acceleration Score Rerating Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `model_multi_factor_acceleration_score_rerating`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `D1`

## Hypothesis

When the official multi-factor score acceleration turns for a stock, the cross-section may keep repricing in that direction for long enough to support a simple industry-ranked rerating alpha.

## Research Contract

- Mechanism: model composite acceleration rerating
- Data category: `Model`
- Idea type: cross-sectional rerating / repricing
- Universe: `USA / TOP3000`
- Liquidity fit: liquid US equities with full field coverage
- Holding frequency: daily refresh with short-to-medium memory
- Delay: `1`
- Neutralization target: `industry`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `ON`
- Pasteurization: `ON`
- Unit handling: `VERIFY`
- Coverage floor: `0.95`
- Freshness floor days: satisfied by `./runs/session-briefs/2026-04-25-model-live-search.json` for this session; recheck again if execution slips to a later session
- Factor risk hypothesis: the line may inherit generic style-factor exposure if the acceleration derivative behaves like a broad rerating proxy.
- Kill condition: kill the family if the baseline plus sign control both fail to establish a plausible direction in the first batch, or if only cosmetic variants survive.

## Validation Design

- Primary test period: `1Y0M`
- Regime slices: keep the first batch minimal; no extra slicing before the direction read
- Liquidity slice: `TOP3000` first
- Subuniverse gate: required before any submit posture
- Factor overlay: compare against generic style/model crowding, not against the frozen static-score lane
- Comparison controls:
  - sign control
  - time-rank stabilization
  - no-group control
- Promotion rule: continue only if the sign-flipped control or one of the controls is directionally credible and the family does not immediately look like a crowded style echo
- Demotion rule: stop if the family only survives through cosmetic expression edits

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `multi_factor_acceleration_score_derivative`
- Equivalent fallback fields:
  - none yet; the verified field already covers the family
- Unconfirmed assumptions:
  - The acceleration derivative is the best first anchor.

## Baseline Expression

```text
group_rank(multi_factor_acceleration_score_derivative, industry)
```

## Variant 1

- Goal:
  Establish the correct sign immediately instead of polishing the wrong direction.
- Main lever:
  Sign only.

```text
group_rank(-multi_factor_acceleration_score_derivative, industry)
```

## Variant 2

- Goal:
  Stabilize a potentially bursty derivative field without changing the source.
- Main lever:
  Add a short time-rank memory.

```text
group_rank(ts_rank(multi_factor_acceleration_score_derivative, 20), industry)
```

## Variant 3

- Goal:
  Measure how much the family depends on industry grouping.
- Main lever:
  Remove industry grouping.

```text
rank(multi_factor_acceleration_score_derivative)
```

## Expected First Failure

- Sharpe:
  The raw acceleration rerating could be too noisy if the update is already mostly priced in.
- Fitness:
  One-field model signals can look sensible but still be too weak after robustness costs.
- Turnover:
  A derivative field can jump in bursts when the underlying model refreshes.
- Weight:
  Without the right grouping, the line could load on a narrow style cohort.
- Sub-universe:
  Unknown until fresh official simulation and check results exist.
- Self-correlation:
  The main danger is overlap with generic style-model crowding.

## Optimization Order

1. Determine the sign with the baseline and direct sign control.
2. Test whether short time-rank memory helps more than it hurts.
3. Only then decide whether industry grouping is necessary or overly constraining.

## Next Simulation Batch

- Baseline:
  `group_rank(multi_factor_acceleration_score_derivative, industry)`
- Variant 1:
  `group_rank(-multi_factor_acceleration_score_derivative, industry)`
- Variant 2:
  `group_rank(ts_rank(multi_factor_acceleration_score_derivative, 20), industry)`
- Variant 3:
  `rank(multi_factor_acceleration_score_derivative)`

## Current Decision

- Winner family: `model_multi_factor_acceleration_score_rerating`
- Official batch status: queued, not yet executed in this session.
- Reason:
  the field has been freshly reverified in-session, but the main thread has not yet submitted the minimal official batch.
