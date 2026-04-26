# Option Breakeven 30 Expression Family

## Metadata

- Date: `2026-04-25`
- Topic: `option_breakeven_30`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The 30-day combined option breakeven price may capture a market-implied consensus signal that is distinct from the frozen analyst and social-media lanes. A first batch should test whether the raw combined option field survives a short-horizon sector-ranked transform before any smoothing or lookback polishing is allowed.

## Research Contract

- Mechanism: combined call+put option breakeven as a market-implied forward consensus signal
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
- Coverage floor: `70%` is acceptable for a first probe, but the family still needs a real batch read before promotion
- Freshness floor days: `0`
- Factor risk hypothesis: the main risk is crowding or self-correlation, not field availability
- Kill condition: if the baseline and the 90-day sibling both fail to show a plausible read, freeze the family immediately and rotate to a new source

## Validation Design

- Primary test period: `1Y`
- Regime slices: not introduced in batch 01
- Liquidity slice: not introduced in batch 01
- Subuniverse gate: watch the real batch output and stop if the baseline fails hard
- Factor overlay: none in batch 01
- Comparison controls: sign flip plus the 90-day combined breakeven sibling only
- Promotion rule: keep the family alive only if the baseline is directionally plausible and the sibling is not just a cosmetic duplicate
- Demotion rule: freeze if the batch only shows weak near-neighbors or a negative / flat first read

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `option_breakeven_30`
  - `option_breakeven_90`
  - `call_breakeven_30`
  - `close`
- Equivalent fallback fields:
  - `option_breakeven_90`
  - `call_breakeven_30`
- Unconfirmed assumptions:
  - The combined 30-day breakeven field is the right first-pass shape for this family.
  - `sector` grouping with `ts_rank(..., 20)` is the right first baseline.
  - `Subindustry` neutralization with `decay=4` remains the correct baseline contract.

## Baseline Expression

```text
group_rank(ts_rank(option_breakeven_30 / close, 20), sector)
```

## Variant 1

- Goal: test sign orientation immediately.
- Main lever: invert the baseline without changing the source.

```text
-group_rank(ts_rank(option_breakeven_30 / close, 20), sector)
```

## Variant 2

- Goal: test the slower combined-breakeven horizon from the same options theme.
- Main lever: switch to the 90-day sibling without adding smoothing.

```text
group_rank(ts_rank(option_breakeven_90 / close, 20), sector)
```

## Variant 3

- Goal: test sign orientation on the sibling field.
- Main lever: invert the sibling field without changing the source.

```text
-group_rank(ts_rank(option_breakeven_90 / close, 20), sector)
```

## Expected First Failure

- Sharpe: the combined options consensus may be too smooth or too regime-dependent
- Fitness: crowding could cap the family early even if the field is clean
- Turnover: the short-horizon rank could still be noisy if the signal is real but unstable
- Weight: sector concentration may show up if only a few industries react strongly
- Sub-universe: the family still needs a real sub-universe read before promotion
- Self-correlation: the options consensus may already be close to an existing alpha

## Optimization Order

1. Run the raw sector-ranked baseline first; do not add smoothing or group tweaks before the source proves it deserves time.
2. Use the sign-flip control as the immediate orientation check, not as a new family.
3. Compare the 90-day sibling directly after the baseline read; if both are weak, freeze the family and rotate to the next new source.

## Next Simulation Batch

- Baseline: `group_rank(ts_rank(option_breakeven_30 / close, 20), sector)`
- Variant 1: `-group_rank(ts_rank(option_breakeven_30 / close, 20), sector)`
- Variant 2: `group_rank(ts_rank(option_breakeven_90 / close, 20), sector)`
- Variant 3: `-group_rank(ts_rank(option_breakeven_90 / close, 20), sector)`

## Official Evidence

- Live Data Explorer field page for `option_breakeven_30`: `https://platform.worldquantbrain.com/data/data-fields/option_breakeven_30?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer search for `call breakeven`: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=call%20breakeven&universe=TOP3000`
- Live Data Explorer search for `option breakeven`: `https://platform.worldquantbrain.com/data/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=option%20breakeven&universe=TOP3000`
