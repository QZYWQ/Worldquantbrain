# Implied Volatility Skew Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `implied-volatility-skew`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The official BRAIN community notes that volatility skew can have a negative association with individual stock returns. The first pass tests the raw skew family directly; the live sign control indicates the positive direction is the working baseline for this family, so batch 01 uses the positive sign before any tenor or style polishing.

## Research Contract

- Mechanism: direct implied-volatility skew fields from the `option8` dataset
- Data category: `Option`
- Idea type: field-family probe
- Universe: `TOP3000`
- Liquidity fit: daily liquid US equities with listed options coverage
- Holding frequency: short horizon, first pass
- Delay: `1`
- Neutralization target: `Industry`
- Decay: `0`
- Truncation: `0.08`
- NaN policy: `On`
- Pasteurization: `On`
- Unit handling: `Verify`
- Coverage floor heuristic: approximately `69%`; the exact live inventory is 69% for the tenor family
- Freshness floor days: `0`
- Factor risk hypothesis: the main risk is crowding / self-correlation, not field availability
- Kill condition: if the first batch is weak or cosmetic, freeze the family immediately and do not start operator polishing

## Validation Design

- Primary test period: `1Y`
- Regime slices: not introduced in batch 01
- Liquidity slice: not introduced in batch 01
- Subuniverse gate: watch the real batch output and stop if it fails hard
- Factor overlay: none in batch 01
- Comparison controls: tenor swap across the same implied-volatility skew family
- Promotion rule: keep the family alive only if the baseline is directionally plausible and at least one tenor sibling is not a cosmetic duplicate
- Demotion rule: freeze if the batch only shows crowded near-neighbors or a negative / flat first read

## Confirmed Or Assumed Inputs

- Confirmed platform fields from the live official Data Explorer page and saved inventory:
  - `implied_volatility_mean_skew_60` — `option8` / `Volatility Data`, `Matrix`, coverage `69%`, date coverage `100%`, visible users `367`, visible alphas `935`
  - `implied_volatility_mean_skew_20` — `option8` / `Volatility Data`, `Matrix`, coverage `69%`, date coverage `100%`, visible alphas `669`
  - `implied_volatility_mean_skew_90` — `option8` / `Volatility Data`, `Matrix`, coverage `69%`, date coverage `100%`, visible alphas `1,376`
  - `implied_volatility_mean_skew_180` — `option8` / `Volatility Data`, `Matrix`, coverage `69%`, date coverage `100%`, visible alphas `975`
- Equivalent fallback fields:
  - none for batch 01
- Unconfirmed assumptions:
  - The direct skew family is the right first-pass shape for this family.
  - The positive sign is the correct working direction, but it still needs the real simulation read on the remaining tenor siblings.

## Baseline Expression

```text
group_rank(implied_volatility_mean_skew_60, industry)
```

## Variant 1

- Goal: test the shorter tenor sibling in the same skew family.
- Main lever: swap the field, not the operator stack.

```text
group_rank(implied_volatility_mean_skew_20, industry)
```

## Variant 2

- Goal: test the longer tenor sibling in the same skew family.
- Main lever: swap to a different tenor with the same daily setup.

```text
group_rank(implied_volatility_mean_skew_90, industry)
```

## Variant 3

- Goal: test the farther tenor sibling to see whether the same thesis survives at slower speed.
- Main lever: swap to the 180-day tenor with the same neutralization setup.

```text
group_rank(implied_volatility_mean_skew_180, industry)
```

## Expected First Failure

- Sharpe: the family may be too crowded to carry fresh edge on its own
- Fitness: crowding and self-correlation are the primary risk
- Turnover: probably acceptable if the signal is real, but still a watch item
- Weight: lower risk than the sparse event lanes because the fields are covered, but still not free
- Sub-universe: needs the real official result, especially on the lower-coverage tenor siblings
- Self-correlation: the most likely first hard bottleneck

## Optimization Order

1. Run the raw skew baseline first; do not add smoothing or lookback before the raw family proves it deserves time.
2. Compare the tenor siblings directly rather than changing group keys or time windows.
3. If all four are weak or obviously crowded near-neighbors, freeze the family and rotate to the next new source.

## Next Simulation Batch

- Baseline: `group_rank(implied_volatility_mean_skew_60, industry)`
- Variant 1: `group_rank(implied_volatility_mean_skew_20, industry)`
- Variant 2: `group_rank(implied_volatility_mean_skew_90, industry)`
- Variant 3: `group_rank(implied_volatility_mean_skew_180, industry)`

## Official Evidence

- Live Data Explorer search for `implied_volatility_mean_skew_60`: `platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=implied_volatility_mean_skew_60&universe=TOP3000`
- Live Data Explorer dataset page for the matching volatility dataset: `platform.worldquantbrain.com/data/data-sets/option8?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Saved official API field inventory: `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`

## Batch 01 Outcome

- The raw tenor sweep stayed interpretable, but the ceiling was too low for a submit-ready branch.
- Test-period metrics from the live Simulate page:
  - `group_rank(implied_volatility_mean_skew_20, industry)` — Sharpe `1.15` / Fitness `0.22` / Turnover `102.90%` / Returns `3.91%` / Drawdown `2.13%` / Margin `0.76‱`
  - `group_rank(implied_volatility_mean_skew_60, industry)` — Sharpe `0.95` / Fitness `0.27` / Turnover `58.53%` / Returns `4.61%` / Drawdown `2.65%` / Margin `1.57‱`
  - `group_rank(implied_volatility_mean_skew_90, industry)` — Sharpe `0.92` / Fitness `0.27` / Turnover `55.02%` / Returns `4.69%` / Drawdown `3.55%` / Margin `1.70‱`
  - `group_rank(implied_volatility_mean_skew_180, industry)` — Sharpe `0.80` / Fitness `0.22` / Turnover `51.31%` / Returns `4.00%` / Drawdown `4.10%` / Margin `1.56‱`
- Decision: freeze this family for the current budget.
- Do not spend more budget on sign flips, lookback tweaks, smoothing, or group-axis tweaks around this exact `option8` skew lane.
- Next jump family source: `option4` open-interest / volatility-spread branch, after fresh official field verification.
