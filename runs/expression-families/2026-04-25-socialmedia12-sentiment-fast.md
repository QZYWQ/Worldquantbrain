# Social Media Sentiment Fast Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `socialmedia12-sentiment-fast`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The `socialmedia12` sentiment family may provide a genuinely new, interpretable alpha source because it is separate from the frozen analyst / focus / rerating lanes and has much lower crowding than the broad social-media sibling. The first pass should test the direct fast sentiment field itself, before adding any lookback, smoothing, or group-axis polishing.

## Research Contract

- Mechanism: direct social-media sentiment from the `socialmedia12` dataset
- Data category: `Social Media`
- Idea type: field-family probe
- Universe: `TOP3000`
- Liquidity fit: daily liquid US equities
- Holding frequency: short horizon, first pass
- Delay: `1`
- Neutralization target: `Subindustry`
- Decay: `4`
- Truncation: `0.08`
- NaN policy: `On`
- Pasteurization: `On`
- Unit handling: `Verify`
- Coverage floor heuristic: roughly `98%`; the exact live inventory is slightly under full coverage, so this is a strong but not perfect field
- Freshness floor days: `0`
- Factor risk hypothesis: the main risk is crowding / self-correlation, not field availability
- Kill condition: if the first batch is weak or only rewards cosmetic lookback/sign swaps, freeze the family immediately and rotate to a new source

## Validation Design

- Primary test period: `1Y`
- Regime slices: not introduced in batch 01
- Liquidity slice: not introduced in batch 01
- Subuniverse gate: watch the real batch output and stop if it fails hard
- Factor overlay: none in batch 01
- Comparison controls: sign flip plus short persistence windows on the same field
- Promotion rule: keep the family alive only if the baseline is directionally plausible and at least one time-window variant is not just a cosmetic duplicate
- Demotion rule: freeze if the batch only shows weak near-neighbors or a negative / flat first read

## Confirmed Or Assumed Inputs

- Confirmed platform fields from the live official Data Explorer page and live API inventory:
  - `scl12_sentiment_fast_d1` — `socialmedia12` / `Sentiment Data for Equity`, `MATRIX`, coverage `97.56%` (`98%` displayed), date coverage `100%`, visible users `111`, visible alphas `125`
  - `scl12_sentiment` — same dataset, `MATRIX`, coverage `100%`, date coverage `100%`, visible users `1,182`, visible alphas `3,230`
  - `scl12_alltype_sentvec` — same dataset, `VECTOR`, coverage `95.25%`, date coverage `100%`, visible users `37`, visible alphas `68`
- Equivalent fallback fields:
  - none for batch 01
- Unconfirmed assumptions:
  - The direct fast sentiment field is the right first-pass shape for this family.
  - The current `Subindustry` + `decay=4` simulation contract is a reasonable starting setup for batch 01.

## Baseline Expression

```text
scl12_sentiment_fast_d1
```

## Variant 1

- Goal: test sign orientation immediately.
- Main lever: invert the field without changing the source.

```text
-scl12_sentiment_fast_d1
```

## Variant 2

- Goal: test a short persistence window on the same field.
- Main lever: add a 20-day time-rank only.

```text
ts_rank(scl12_sentiment_fast_d1, 20)
```

## Variant 3

- Goal: test a slower persistence window on the same field.
- Main lever: add a 60-day time-rank only.

```text
ts_rank(scl12_sentiment_fast_d1, 60)
```

## Expected First Failure

- Sharpe: the field may be too weak once neutralized, even if it is directionally sensible
- Fitness: crowding and self-correlation are the primary risk
- Turnover: the raw daily field may be noisy, so turnover could be the first practical bottleneck
- Weight: lower risk than the sparse event lanes because the field is covered
- Sub-universe: needs the real official result because coverage is not full
- Self-correlation: the most likely first hard bottleneck if this is just a broad social-media proxy

## Optimization Order

1. Run the direct field baseline first; do not add smoothing or group-axis changes before the raw family proves it deserves time.
2. Use the sign-flip control as the first orientation check, not as a new family.
3. Compare the 20-day and 60-day persistence windows directly; if both are weak, freeze the family and rotate to the next new source.

## Next Simulation Batch

- Baseline: `scl12_sentiment_fast_d1`
- Variant 1: `-scl12_sentiment_fast_d1`
- Variant 2: `ts_rank(scl12_sentiment_fast_d1, 20)`
- Variant 3: `ts_rank(scl12_sentiment_fast_d1, 60)`

## Official Evidence

- Live Data Explorer search for `scl12_sentiment_fast_d1`: `https://platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=scl12_sentiment_fast_d1&universe=TOP3000`
- Live Data Explorer field page: `https://platform.worldquantbrain.com/data/data-fields/scl12_sentiment_fast_d1?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live API search response: `https://api.worldquantbrain.com/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=scl12_sentiment_fast_d1&universe=TOP3000`

## Batch 01 Status

- Live simulation has been launched from the official Simulate page with the batch 01 contract above.
- The first request created simulation `1MijU56c74vqc7djviffdii`.
- Batch outcome is pending until the simulation finishes and the official result can be captured.
