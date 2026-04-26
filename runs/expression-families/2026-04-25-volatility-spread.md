# Volatility Spread Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `volatility-spread`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The implied-vs-realized volatility spread may still carry a usable short-horizon edge if the raw matrix fields are clean enough and the signal is not already fully crowded. The family begins with the raw official field, checks the sign orientation immediately, and then tests the direct sibling spread field before any cosmetic transformation is allowed.

## Research Contract

- Mechanism: direct volatility spread between implied volatility and recent realized volatility
- Data category: `Model / Technical Models`
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
- Coverage floor heuristic: `83%` for the sparse baseline, `97%` for the sibling field
- Freshness floor days: `0`
- Factor risk hypothesis: the primary risk is that the spread behaves like a crowded risk proxy rather than a fresh alpha source
- Kill condition: if the first batch is weak or only the sign flip survives, freeze the family immediately and rotate to a new source

## Validation Design

- Primary test period: `1Y`
- Regime slices: not introduced in batch 01
- Liquidity slice: not introduced in batch 01
- Subuniverse gate: watch the real batch output and stop if the sparse baseline fails hard
- Factor overlay: none in batch 01
- Comparison controls: sign flip plus direct sibling field only
- Promotion rule: keep the family alive only if the raw baseline is directionally plausible and the sibling field is not just a cosmetic duplicate
- Demotion rule: freeze if the batch only shows weak near-neighbors or a negative / flat first read

## Confirmed Or Assumed Inputs

- Confirmed platform fields from the live official Data Explorer pages:
  - `mdl77_2400_rmi` — `Analysts' Factor Model` / `Technical Models`, `MATRIX`, coverage `83%`, date coverage `100%`, visible alphas `1`
  - `implied_minus_realized_volatility_2` — `Analysts' Factor Model` / `Technical Models`, `MATRIX`, coverage `97%`, date coverage `100%`, visible alphas `11`
- Equivalent fallback fields:
  - `implied_minus_realized_volatility_2`
- Unconfirmed assumptions:
  - The raw implied-minus-realized spread is the right first-pass shape for this family.
  - `Subindustry` neutralization with `decay=4` is still the right baseline contract for the first official batch.

## Baseline Expression

```text
mdl77_2400_rmi
```

## Variant 1

- Goal: test sign orientation immediately.
- Main lever: invert the raw field without changing the source.

```text
-mdl77_2400_rmi
```

## Variant 2

- Goal: test the more covered sibling field from the same volatility-spread theme.
- Main lever: switch to the direct sibling field without any smoothing.

```text
implied_minus_realized_volatility_2
```

## Variant 3

- Goal: test sign orientation on the sibling field.
- Main lever: invert the sibling field without changing the source.

```text
-implied_minus_realized_volatility_2
```

## Expected First Failure

- Sharpe: the raw spread may be too close to a direct risk proxy to carry fresh edge
- Fitness: crowding is the main risk if the family is real but not distinctive
- Turnover: likely acceptable if the signal is real, but still worth checking
- Weight: the sparse baseline may fail structurally if coverage is too thin
- Sub-universe: the more covered sibling should be the cleaner test here
- Self-correlation: if the raw field is already crowded, the family may be capped early

## Optimization Order

1. Run the raw sparse baseline first; do not add smoothing or group tweaks before the raw family proves it deserves time.
2. Use the sign-flip control as the immediate orientation check, not as a new family.
3. Compare the direct sibling field and its sign flip only after the raw baseline has been read.

## Next Simulation Batch

- Baseline: `mdl77_2400_rmi`
- Variant 1: `-mdl77_2400_rmi`
- Variant 2: `implied_minus_realized_volatility_2`
- Variant 3: `-implied_minus_realized_volatility_2`

## Official Evidence

- Live Data Explorer search for `volatility spread`: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=volatility%20spread&universe=TOP3000`
- Live Data Explorer field page for `mdl77_2400_rmi`: `https://platform.worldquantbrain.com/data/data-fields/mdl77_2400_rmi?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer field page for `implied_minus_realized_volatility_2`: `https://platform.worldquantbrain.com/data/data-fields/implied_minus_realized_volatility_2?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
