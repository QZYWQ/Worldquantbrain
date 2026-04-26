# Invested Capital History Position Expression Family

## Metadata

- Date: `2026-04-24`
- Topic: `invested_capital_history_position`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Ranking invested capital against its own history should capture whether a company is in a capital-deployment regime that peers have not yet fully priced, and the first official Data Explorer check in this session confirms a distinct annual sibling field that is less crowded than the public quarterly alias.

## Research Contract

- Mechanism: slow capital-deployment state on invested capital
- Data category: fundamental6 company fundamentals
- Idea type: fundamentals-first
- Universe: USA / TOP3000
- Liquidity fit: liquid US equities with enough coverage for a slow history-position signal
- Holding frequency: slow / medium-slow
- Delay: 1
- Neutralization target: industry
- Decay: 4
- Truncation: 0.08
- NaN policy: OFF
- Pasteurization: ON
- Unit handling: VERIFY
- Coverage floor: 50% observed, so keep the first batch small and diagnostic
- Freshness floor days: 90
- Factor risk hypothesis: half-coverage fundamentals can still concentrate by industry and may show unit warnings under VERIFY.
- Kill condition: if the baseline sign is wrong and the quarterly sibling does not offer a cleaner control, freeze the family.

## Validation Design

- Primary test period: 1Y
- Regime slices: 2020-2021, 2022-2023
- Liquidity slice: top3000 liquid names only
- Subuniverse gate: require a real sub-universe check before any packaging claim
- Factor overlay: compare against the killed `liabilities / assets` leverage lane and the analyst-price sibling pool
- Comparison controls: sign-inverted control, quarterly sibling control, slower 504d window control
- Promotion rule: promote only if sign, horizon, and subuniverse all improve without a severe unit warning or concentration penalty
- Demotion rule: demote to hold after one failed sign control or repeated full-IS weakness

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `fnd6_newa1v1300_icapt`
  - `invested_capital`
  - `fnd6_newqv1300_icaptq`
- Unconfirmed assumptions:
  - The annual alias is the best first anchor because it is less crowded.
  - `252d` is the right first baseline before extra smoothing.
  - `industry` grouping is the right first-pass neutralization.

## Baseline Expression

```text
group_rank(ts_rank(fnd6_newa1v1300_icapt, 252), industry)
```

## Variant 1

- Goal: Test the thesis sign directly before doing anything else.
- Main lever: Sign only, holding field and horizon fixed.

```text
group_rank(-ts_rank(fnd6_newa1v1300_icapt, 252), industry)
```

## Variant 2

- Goal: Check whether the public quarterly alias behaves similarly.
- Main lever: Field sibling swap from annual to quarterly alias.

```text
group_rank(ts_rank(invested_capital, 252), industry)
```

## Variant 3

- Goal: Check whether a slower window better captures capital-deployment regime changes.
- Main lever: Horizon from `252` to `504`.

```text
group_rank(ts_rank(fnd6_newa1v1300_icapt, 504), industry)
```

## Expected First Failure

- Sharpe:
  The sign may still be wrong, or the half-covered field may not be directional enough.
- Fitness:
  Sparse effective coverage after grouping can still make the family look weak.
- Turnover:
  This is unlikely to be the first blocker.
- Weight:
  A small number of industries may dominate the useful signal.
- Sub-universe:
  Still a major risk because the field family is only half covered.
- Self-correlation:
  Unknown until a real official check exists, though the family should be far from the analyst-price pool.

## Next Simulation Batch

- Baseline: `group_rank(ts_rank(fnd6_newa1v1300_icapt, 252), industry)`
- Variant 1: `group_rank(-ts_rank(fnd6_newa1v1300_icapt, 252), industry)`
- Variant 2: `group_rank(ts_rank(invested_capital, 252), industry)`
- Variant 3: `group_rank(ts_rank(fnd6_newa1v1300_icapt, 504), industry)`

## Batch 01 Official Results

- Baseline `group_rank(ts_rank(fnd6_newa1v1300_icapt, 252), industry)` was a diagnostic dead end: IS Sharpe `-0.25`, Fitness `-0.06`, low-sub-universe-sharpe failed, and the `UNITS` warning showed the raw history-position shape is not a clean fit for this field.
- Sign-flip `group_rank(-ts_rank(fnd6_newa1v1300_icapt, 252), industry)` improved the sub-universe check, but IS Sharpe only reached `0.25` and Fitness `0.06`, which is still nowhere near a real candidate.
- Submission posture: frozen. Do not continue polishing this raw annual invested-capital history-position family.
- Next move: if the capital-deployment idea is worth another hour, it needs a normalized ratio or a different field family rather than more same-axis smoothing.
