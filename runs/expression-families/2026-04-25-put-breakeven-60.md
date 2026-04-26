# Put Breakeven 60 Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `put-breakeven-60`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

`put_breakeven_60` may capture a cleaner downside-demand or crash-insurance signal than the already-explored call breakeven lane, because the 60-day put breakeven source is less crowded than its 10-day sibling and still remains a direct options-analytics matrix field. The first batch should test whether the raw source survives a short-horizon sector-ranked transform before any follow-up polishing is allowed.

## Research Contract

- Mechanism: direct put-option breakeven / downside-demand signal from the options analytics dataset
- Data category: `Option Analytics`
- Idea type: field-family probe
- Universe: `TOP3000`
- Liquidity fit: daily liquid US equities
- Holding frequency: short horizon, first pass
- Delay: `1`
- Neutralization target: `Subindustry`
- Decay: `4`
- Truncation: `0.08`
- NaN policy: `OFF`
- Pasteurization: `ON`
- Unit handling: `Verify`
- Coverage floor heuristic: `70%` is usable for a first probe, but the family still needs a real batch read before it can be promoted
- Freshness floor days: `0`
- Factor risk hypothesis: the main risk is crowding / self-correlation rather than field availability
- Kill condition: if the first batch is weak or only cosmetic variants survive, freeze the family immediately and rotate to a new source

## Validation Design

- Primary test period: `1Y`
- Regime slices: not introduced in batch 01
- Liquidity slice: not introduced in batch 01
- Subuniverse gate: watch the real batch output and stop if the family fails hard
- Factor overlay: none in batch 01
- Comparison controls: sign flip plus direct sibling field only
- Promotion rule: keep the family alive only if the baseline is directionally plausible and the sibling field is not just a cosmetic duplicate
- Demotion rule: freeze if the batch only shows weak near-neighbors or a negative / flat first read

## Confirmed Or Assumed Inputs

- Confirmed platform fields from the live official Data Explorer pages:
  - `put_breakeven_60` — `Options Analytics`, `MATRIX`, coverage `70%`, date coverage `100%`, visible alphas `309`
  - `put_breakeven_10` — `Options Analytics`, `MATRIX`, coverage `70%`, date coverage `100%`, visible alphas `901`
- Equivalent fallback fields:
  - `put_breakeven_10`
- Unconfirmed assumptions:
  - The raw put breakeven signal is the right first-pass shape for this family.
  - `sector` grouping with `ts_rank(..., 10)` is the right starting transform.
  - `Subindustry` neutralization with `decay=4` remains the correct baseline contract for the first official batch.

## Baseline Expression

```text
group_rank(ts_rank(put_breakeven_60 / close, 10), sector)
```

## Variant 1

- Goal: test sign orientation immediately.
- Main lever: invert the baseline without changing the source.

```text
-group_rank(ts_rank(put_breakeven_60 / close, 10), sector)
```

## Variant 2

- Goal: test the same-family 10-day sibling from the same options-analytics theme.
- Main lever: switch to the more crowded sibling field without any smoothing.

```text
group_rank(ts_rank(put_breakeven_10 / close, 10), sector)
```

## Variant 3

- Goal: test sign orientation on the sibling field.
- Main lever: invert the sibling field without changing the source.

```text
-group_rank(ts_rank(put_breakeven_10 / close, 10), sector)
```

## Expected First Failure

- Sharpe: the downside signal may be too smooth or too regime-dependent
- Fitness: options crowding and self-correlation could cap the family early
- Turnover: the short-horizon rank may still be noisy
- Weight: the 10-day sibling is more crowded and may fail concentration sooner
- Sub-universe: options signals often look cleaner on the full universe than on the sub-universe slice
- Self-correlation: the family may be close to already-known breakeven templates

## Optimization Order

1. Run the raw sector-ranked baseline first; do not add smoothing or group tweaks before the source proves it deserves time.
2. Use the sign-flip control as the first orientation check, not as a new family.
3. Compare the 10-day sibling directly after the baseline read; if both are weak, freeze the family and rotate to the next new source.

## Next Simulation Batch

- Baseline: `group_rank(ts_rank(put_breakeven_60 / close, 10), sector)`
- Variant 1: `-group_rank(ts_rank(put_breakeven_60 / close, 10), sector)`
- Variant 2: `group_rank(ts_rank(put_breakeven_10 / close, 10), sector)`
- Variant 3: `-group_rank(ts_rank(put_breakeven_10 / close, 10), sector)`

## Official Evidence

- Live Data Explorer field page for `put_breakeven_60`: `https://platform.worldquantbrain.com/data/data-fields/put_breakeven_60?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer field page for `put_breakeven_10`: `https://platform.worldquantbrain.com/data/data-fields/put_breakeven_10?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer search for `put breakeven`: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=put%20breakeven&universe=TOP3000`
