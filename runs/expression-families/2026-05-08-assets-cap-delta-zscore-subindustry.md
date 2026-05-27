# Assets Cap Delta Zscore Subindustry Expression Family

## Metadata

- Date: `2026-05-08`
- Topic: `assets_cap_delta_zscore_subindustry`
- Source: screenshot template showing `group_rank(ts_zscore(ts_delta(divide(assets, cap), 2), 20), subindustry)` and comments suggesting `hump()` / `ts_backfill`
- Region: `USA` assumed from screenshot; verify on official BRAIN
- Universe: `TOP3000` assumed from screenshot; verify on official BRAIN
- Delay: `1` assumed from screenshot; verify on official BRAIN

## Hypothesis

Within a subindustry, the recent change in `assets / cap` may capture companies whose balance-sheet scale is re-rating relative to market value. The expected edge is not the raw level alone, but the short-term displacement from its recent local history.

## Research Contract

- Mechanism: balance-sheet-to-market-value displacement
- Data category: fundamental ratio plus market capitalization denominator
- Idea type: fundamentals / valuation hybrid
- Universe: USA / TOP3000 assumed
- Liquidity fit: TOP3000, with Sub-universe risk explicitly monitored
- Holding frequency: medium-fast because `cap` moves daily despite slow `assets`
- Delay: 1
- Competition route posture: D1-first
- Competition route reason: screenshot settings use Delay 1; do not probe D0 until D1 viability exists
- Neutralization target: Subindustry
- Decay: 6 for screenshot-faithful first pass; later compare 0 / 3 only if needed
- Truncation: 0.08
- NaN policy: OFF unless `assets` coverage requires targeted `ts_backfill`
- Pasteurization: ON
- Unit handling: VERIFY; ratio normalizes unlike quantities before delta/zscore
- Coverage floor: do not promote if ratio coverage creates unstable long/short counts
- Freshness floor days: confirm `assets` update rhythm before deeper mining
- Factor risk hypothesis: can load on value, leverage, size, and asset-growth factors
- Kill condition: baseline and sign control both fail Sharpe/Fitness or show structural Sub-universe weakness without a clean repair lever

## Validation Design

- Primary test period: platform default full IS first; inspect Test Period after a viable line appears
- Competition route test: D1-first only
- Regime slices: review 2020 stress, 2021-2022 inflation/rate shift, 2023 recovery if platform exposes yearly table
- Liquidity slice: Sub-universe check is binding before any submit posture
- Subuniverse gate: require real official check evidence before candidate-batch triage
- Factor overlay: compare conceptually against prior balance-sheet / invested-capital / capex lanes
- Comparison controls: sign flip, rank-vs-zscore, backfill, wider group, longer delta
- Promotion rule: promote only if one direct expression clears Sharpe/Fitness and Sub-universe without unit warning or obvious concentration fragility
- Demotion rule: if direct and sign-flip controls both fail, stop instead of sweeping `hump()` and lookbacks

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - None in current project artifacts for this exact family.
- Assumed from screenshot:
  - `assets`
  - `cap`
  - `subindustry`
- Equivalent fallback fields:
  - `total_assets`
  - `total_assets_amount`
  - other Data Explorer total-asset aliases
- Unconfirmed assumptions:
  - `assets` is visible in the current account.
  - `assets / cap` has enough coverage in `USA / TOP3000`.
  - `hump()` signature is available in the active Fast Expression environment.

## Baseline Expression

```text
group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), subindustry)
```

## Variant 1

- Goal: Mandatory sign control.
- Main lever: Flip final executable expression only.

```text
-group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), subindustry)
```

## Variant 2

- Goal: Test whether `ts_rank` is more robust than zscore for outlier-heavy ratios.
- Main lever: Distribution transform.

```text
group_rank(ts_rank(ts_delta(assets / cap, 2), 20), subindustry)
```

## Variant 3

- Goal: Repair stale or sparse `assets` coverage before computing the ratio.
- Main lever: Targeted backfill on numerator.

```text
group_rank(ts_zscore(ts_delta(ts_backfill(assets, 60) / cap, 2), 20), subindustry)
```

## Variant 4

- Goal: Reduce short-horizon noise and possible turnover from daily `cap` movement.
- Main lever: Longer delta and zscore window.

```text
group_rank(ts_zscore(ts_delta(assets / cap, 5), 60), subindustry)
```

## Variant 5

- Goal: Test whether subindustry is too narrow for coverage / Sub-universe behavior.
- Main lever: Wider group comparison.

```text
group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), industry)
```

## Conditional Repair Batch

Only run these after the direct baseline or sign control has viable Sharpe/Fitness but weak Sub-universe Sharpe or excessive turnover.

```text
hump(group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), subindustry), hump=0.01)
```

```text
hump(group_rank(ts_zscore(ts_delta(ts_backfill(assets, 60) / cap, 2), 20), subindustry), hump=0.01)
```

If the platform rejects named `hump` syntax, verify the official operator signature before retrying. Do not spend rescue budget on syntax guessing.

## Expected First Failure

- Sharpe:
  Direction ambiguity; ratio increases can be bullish or bearish.
- Fitness:
  `2d` delta may be too active relative to return strength.
- Turnover:
  Daily denominator movement can make a slow-fundamental idea trade like a price-derived idea.
- Weight:
  Small-cap denominator outliers can concentrate weights.
- Sub-universe:
  Main expected bottleneck based on the screenshot context.
- Self-correlation:
  Moderate risk against value / balance-sheet / capital-structure families; lower risk than pure price-volume if the field survives.

## Optimization Order

1. Run baseline plus final-expression sign control.
2. If one sign is viable, test rank-vs-zscore and backfill as separate one-axis variants.
3. If Sub-universe is the only blocker, test group width and `hump()` repair.
4. If Fitness is the blocker, test longer delta/window before decay tuning.
5. If both signs are weak, kill this exact template and branch to a different assets denominator or a different balance-sheet field.

## Next Simulation Batch

- Baseline: `group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), subindustry)`
- Sign control: `-group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), subindustry)`
- Variant 1: `group_rank(ts_rank(ts_delta(assets / cap, 2), 20), subindustry)`
- Variant 2: `group_rank(ts_zscore(ts_delta(ts_backfill(assets, 60) / cap, 2), 20), subindustry)`
- Variant 3: `group_rank(ts_zscore(ts_delta(assets / cap, 5), 60), subindustry)`
- Variant 4: `group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), industry)`

## Submission Posture

- Current posture: exploratory only.
- No real Sharpe, Fitness, Turnover, Weight, Sub-universe, Self-correlation, or Test Period result exists yet for this current project family.
- Do not submit or claim submit-ready until official simulation and check evidence exists.
