# Social Media Sentiment Value Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `socialmedia8-sentiment-value`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

`socialmedia8` may still carry a direct, interpretable sentiment edge even though the broader social-media lanes are crowded. The cleanest first test is the raw sentiment value field itself; if that does not work, sign-flip and short persistence windows are the only allowed next checks before the family is frozen.

## Research Contract

- Mechanism: direct social-media sentiment z-score from the `socialmedia8` dataset
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
- Coverage floor heuristic: roughly `86%`; the live inventory is not full, so this is a usable but not robust field
- Freshness floor days: `0`
- Factor risk hypothesis: the main risk is crowding / self-correlation, not field availability
- Kill condition: if the first batch is weak or only cosmetic variants survive, freeze the family immediately and rotate to the next source

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

- Confirmed platform fields from the live official Data Explorer page and live search results:
  - `snt_social_value` — `socialmedia8` / `Social Media Data for Equity`, `MATRIX`, coverage `86%`, date coverage `100%`, visible alphas `4,855`
  - `snt_social_volume` — same dataset, `MATRIX`, coverage `86%`, date coverage `100%`, visible alphas `4,788`
- Equivalent fallback fields:
  - `snt_social_volume`
- Unconfirmed assumptions:
  - The direct sentiment value field is the right first-pass shape for this family.
  - `Subindustry` neutralization with `decay=4` is still the right baseline contract for the first official batch.

## Baseline Expression

```text
snt_social_value
```

## Variant 1

- Goal: test sign orientation immediately.
- Main lever: invert the field without changing the source.

```text
-snt_social_value
```

## Variant 2

- Goal: test a short persistence window on the same field.
- Main lever: add a 20-day time-rank only.

```text
ts_rank(snt_social_value, 20)
```

## Variant 3

- Goal: test a slower persistence window on the same field.
- Main lever: add a 60-day time-rank only.

```text
ts_rank(snt_social_value, 60)
```

## Expected First Failure

- Sharpe: the field may be too crowded to carry fresh edge on its own
- Fitness: crowding and self-correlation are the primary risk
- Turnover: the raw daily field may be noisy, so turnover is still a watch item
- Weight: lower risk than the sparse event lanes because the field is covered
- Sub-universe: needs the real official result because coverage is not full
- Self-correlation: the most likely first hard bottleneck

## Optimization Order

1. Run the raw field baseline first; do not add smoothing or group tweaks before the raw family proves it deserves time.
2. Use the sign-flip control as the first orientation check, not as a new family.
3. Compare the 20-day and 60-day persistence windows directly; if both are weak, freeze the family and rotate to the next new source.

## Next Simulation Batch

- Baseline: `snt_social_value`
- Variant 1: `-snt_social_value`
- Variant 2: `ts_rank(snt_social_value, 20)`
- Variant 3: `ts_rank(snt_social_value, 60)`

## Official Evidence

- Live Data Explorer search for `snt_social_value`: `https://platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=snt_social_value&universe=TOP3000`
- Live Data Explorer field page: `https://platform.worldquantbrain.com/data/data-fields/snt_social_value?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer search for `snt_social_volume`: `https://platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=snt_social_volume&universe=TOP3000`

