# Option Breakeven 360 Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `option_breakeven_360`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The 360-day combined option breakeven price may capture a slower market-implied consensus signal that is distinct from the frozen 30d and 90d breakeven lanes. A first batch should test whether the raw longer-tenor field survives a short-horizon sector-ranked transform before any smoothing or group-axis polishing is allowed.

## Research Contract

- Mechanism: combined call+put option breakeven as a slower market-implied consensus signal
- Data category: `Options Analytics`
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
- Unit handling: `VERIFY`
- Coverage floor: `70%` is acceptable for a first probe, but the family still needs a real batch read before promotion
- Freshness floor days: `0`
- Factor risk hypothesis: the main risk is crowding or self-correlation, not field availability
- Kill condition: if the baseline and the slower `60d` control both fail to show a plausible read, freeze the family immediately and rotate away

## Validation Design

- Primary test period: `1Y`
- Regime slices: not introduced in batch 01
- Liquidity slice: not introduced in batch 01
- Subuniverse gate: watch the real batch output and stop if the baseline fails hard
- Factor overlay: none in batch 01
- Comparison controls: sign flip plus a slower rank window and one light smoothing control
- Promotion rule: keep the family alive only if the baseline is directionally plausible and the slower control is not just a cosmetic duplicate
- Demotion rule: freeze if the batch only shows weak near-neighbors or a negative / flat first read

## Confirmed Or Assumed Inputs

- Confirmed platform field:
  - `option_breakeven_360`
- Confirmed platform field family:
  - `Options Analytics` / `Option Analytics`
- Unconfirmed assumptions:
  - The 360d combined breakeven field is the right first-pass shape for this family.
  - `sector` grouping with `ts_rank(..., 20)` is the right first baseline.
  - `Subindustry` neutralization with `decay=4` remains the correct baseline contract for batch 01.

## Baseline Expression

```text
group_rank(ts_rank(option_breakeven_360 / close, 20), sector)
```

## Variant 1

- Goal: test sign orientation immediately.
- Main lever: invert the baseline without changing the source.

```text
-group_rank(ts_rank(option_breakeven_360 / close, 20), sector)
```

## Variant 2

- Goal: test whether a slower ranking window improves robustness on the longer tenor.
- Main lever: extend the rank window from `20` to `60`.

```text
group_rank(ts_rank(option_breakeven_360 / close, 60), sector)
```

## Variant 3

- Goal: test whether light smoothing on the ratio leg reduces noise without changing the source.
- Main lever: add a 5-day mean before the rank.

```text
group_rank(ts_rank(ts_mean(option_breakeven_360 / close, 5), 20), sector)
```

## Expected First Failure

- Sharpe: the slower breakeven may still be too smooth to carry fresh edge
- Fitness: the family may still be too crowded even at the longer tenor
- Turnover: likely lower than shorter-horizon options families, but still worth checking
- Weight: sector concentration may show up if only a few industries react strongly
- Sub-universe: the family still needs a real batch read before promotion
- Self-correlation: could be the main blocker if this longer tenor is already represented in the existing alpha pool

## Optimization Order

1. Run the raw sector-ranked baseline first; do not add extra smoothing before the source proves it deserves time.
2. Use the sign-flip control as the immediate orientation check, not as a new family.
3. Compare the slower `60d` rank directly after the baseline read; if it is still weak, freeze the family and rotate away.

## Next Simulation Batch

- Baseline: `group_rank(ts_rank(option_breakeven_360 / close, 20), sector)`
- Variant 1: `-group_rank(ts_rank(option_breakeven_360 / close, 20), sector)`
- Variant 2: `group_rank(ts_rank(option_breakeven_360 / close, 60), sector)`
- Variant 3: `group_rank(ts_rank(ts_mean(option_breakeven_360 / close, 5), 20), sector)`

## Official Evidence

- Live Data Explorer field page for `option_breakeven_360`: `https://platform.worldquantbrain.com/data/data-fields/option_breakeven_360?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer search for `option4`: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=option4&universe=TOP3000`
