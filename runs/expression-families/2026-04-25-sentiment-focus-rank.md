# Sentiment Focus Rank Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `sentiment-focus-rank`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Research Sentiment composite rank fields may give a clean, interpretable family that is distinct from the frozen EPS, cashflow, operating-income, model rerating, and social-buzz lanes. The first pass should test whether the direct fields themselves have signal, before adding any lookback, smoothing, or group-axis polishing.

## Research Contract

- Mechanism: direct composite Sentiment fields from the `sentiment1` dataset
- Data category: `Sentiment`
- Idea type: field-family probe
- Universe: `TOP3000`
- Liquidity fit: daily liquid US equities
- Holding frequency: short horizon, first pass
- Delay: `1`
- Neutralization target: `Subindustry`
- Decay: `4`
- Truncation: `0.08`
- NaN policy: `Off`
- Pasteurization: `On`
- Unit handling: `Verify`
  - Coverage floor heuristic: roughly `57%`; the exact saved inventory for the three rank siblings sits slightly below that, so coverage is marginal rather than robust
- Freshness floor days: `0`
- Factor risk hypothesis: the main risk is crowding / self-correlation, not field availability
- Kill condition: if the first batch is weak or cosmetic, freeze the family immediately and do not start operator polishing

## Validation Design

- Primary test period: `1Y`
- Regime slices: not introduced in batch 01
- Liquidity slice: not introduced in batch 01
- Subuniverse gate: watch the real batch output and stop if it fails hard
- Factor overlay: none in batch 01
- Comparison controls: sibling field swap across the same Sentiment family
- Promotion rule: keep the family alive only if the baseline is directionally plausible and at least one sibling is not a cosmetic duplicate
- Demotion rule: freeze if the batch only shows crowded near-neighbors or a negative / flat first read

## Confirmed Or Assumed Inputs

- Confirmed platform fields from the saved official Data Explorer inventory:
  - `snt1_d1_dynamicfocusrank` — `sentiment1` / `Research Sentiment Data`, `MATRIX`, coverage `56.51%`, date coverage `100%`, visible users `291`, visible alphas `1,866`
  - `snt1_d1_stockrank` — `sentiment1` / `Research Sentiment Data`, `MATRIX`, coverage `56.72%`, date coverage `100%`, visible users `226`, visible alphas `2,142`
  - `snt1_d1_fundamentalfocusrank` — `sentiment1` / `Research Sentiment Data`, `MATRIX`, coverage `56.84%`, date coverage `100%`, visible users `234`, visible alphas `2,505`
  - `snt1_cored1_score` — `sentiment1` / `Research Sentiment Data`, `MATRIX`, coverage `63.29%`, date coverage `100%`, visible users `540`, visible alphas `3,731`
- Equivalent fallback fields:
  - none for batch 01
- Unconfirmed assumptions:
  - The direct field entries are the right first-pass shape for this family.
  - Lookback, smoothing, and group-axis tweaks would only be cosmetic unless the raw family proves itself first.

## Baseline Expression

```text
snt1_d1_dynamicfocusrank
```

## Variant 1

- Goal: test the closest sibling with a slightly different equity-style emphasis.
- Main lever: swap the field, not the operator stack.

```text
snt1_d1_stockrank
```

## Variant 2

- Goal: test the longer-term fundamental/value sentiment sibling.
- Main lever: swap to a different Sentiment subfield with the same daily setup.

```text
snt1_d1_fundamentalfocusrank
```

## Variant 3

- Goal: test the broader composite analyst score sibling with higher coverage.
- Main lever: swap to the broader score field, keeping the rest of the setup fixed.

```text
snt1_cored1_score
```

## Expected First Failure

- Sharpe: the family may be too crowded to carry fresh edge on its own
- Fitness: crowding and self-correlation are the primary risk
- Turnover: probably acceptable if the signal is real, but still a watch item
- Weight: lower risk than the sparse event lanes because the fields are covered, but still not free
- Sub-universe: needs the real official result, especially on the lower-coverage rank fields
- Self-correlation: the most likely first hard bottleneck

## Optimization Order

1. Run the raw field baseline first; do not add smoothing or lookback before the raw family proves it deserves time.
2. Compare the sibling fields directly rather than changing group keys or time windows.
3. If all four are weak or obviously crowded near-neighbors, freeze the family and rotate to the next new source.

## Next Simulation Batch

- Baseline: `snt1_d1_dynamicfocusrank`
- Variant 1: `snt1_d1_stockrank`
- Variant 2: `snt1_d1_fundamentalfocusrank`
- Variant 3: `snt1_cored1_score`

## Official Evidence

- Live Data Explorer search for `snt1_d1_dynamicfocusrank`: `platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=snt1_d1_dynamicfocusrank&universe=TOP3000`
- Live Data Explorer search for `snt1_cored1_score`: `platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=snt1_cored1_score&universe=TOP3000`
