# Capital Expenditure Amount Close Industry Expression Family

## Metadata

- Date: `2026-04-24`
- Topic: `capital_expenditure_amount_close_industry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Capex estimate intensity relative to price may identify firms in stronger reinvestment regimes that cross-sectionally outrank peers over a slow horizon, and the live official Data Explorer search in this session found a low-crowding analyst4 field that should be cleaner than the older capex symbols.

## Research Contract

- Mechanism: capex estimate intensity normalized by price
- Data category: analyst4 estimate data
- Idea type: fundamentals-first
- Universe: USA / TOP3000
- Liquidity fit: liquid US equities with enough coverage for a slow capex-intensity signal
- Holding frequency: slow / medium-slow
- Delay: 1
- Neutralization target: industry
- Decay: 4
- Truncation: 0.08
- NaN policy: OFF
- Pasteurization: ON
- Unit handling: VERIFY
- Coverage floor: 75% observed, so keep the first batch diagnostic and price-normalized
- Freshness floor days: 90
- Factor risk hypothesis: analyst estimate capex can still be concentrated by industry even with low crowding.
- Kill condition: if the sign control fails and the 126d control does not improve the anchor, freeze the family.

## Validation Design

- Primary test period: 1Y
- Regime slices: 2020-2021, 2022-2023
- Liquidity slice: top3000 liquid names only
- Subuniverse gate: require a real sub-universe check before any packaging claim
- Factor overlay: compare against the failed invested-capital history-position lane and the legacy capex symbols
- Comparison controls: sign-inverted control, 126d control, 252d control
- Promotion rule: promote only if sign, horizon, and subuniverse all improve without a severe concentration penalty
- Demotion rule: demote to hold after one failed sign control or repeated full-IS weakness

## Confirmed Or Assumed Inputs

- Confirmed platform field:
  - `capital_expenditure_amount`
- Fallback controls:
  - `fnd6_capxs`
  - `capex`
- Unconfirmed assumptions:
  - The price-normalized form is the cleanest first anchor.
  - `84d` is a reasonable first history window before extra smoothing.
  - `industry` grouping is the right first-pass neutralization.

## Baseline Expression

```text
group_rank(ts_rank(capital_expenditure_amount / close, 84), industry)
```

## Variant 1

- Goal: Test the thesis sign directly before doing anything else.
- Main lever: Sign only, holding field and horizon fixed.

```text
group_rank(-ts_rank(capital_expenditure_amount / close, 84), industry)
```

## Variant 2

- Goal: Check whether a slower memory window improves robustness.
- Main lever: Horizon from `84` to `126`.

```text
group_rank(ts_rank(capital_expenditure_amount / close, 126), industry)
```

## Variant 3

- Goal: Check whether a much slower memory window helps the estimate field more than the faster one.
- Main lever: Horizon from `84` to `252`.

```text
group_rank(ts_rank(capital_expenditure_amount / close, 252), industry)
```

## Expected First Failure

- Sharpe:
  The sign may still be wrong, or the capex estimate may be too noisy as a standalone history signal.
- Fitness:
  Coverage is decent but not full, so the branch could still look weak after grouping.
- Turnover:
  This is unlikely to be the first blocker.
- Weight:
  A few industries may dominate the useful signal.
- Sub-universe:
  This still needs a real official check before any packaging claim.
- Self-correlation:
  Unknown until a real official check exists.
- Units:
  Price normalization should help avoid the raw unit mismatch seen in the invested-capital dead end.

## Next Simulation Batch

- Baseline: `group_rank(ts_rank(capital_expenditure_amount / close, 84), industry)`
- Variant 1: `group_rank(-ts_rank(capital_expenditure_amount / close, 84), industry)`
- Variant 2: `group_rank(ts_rank(capital_expenditure_amount / close, 126), industry)`
- Variant 3: `group_rank(ts_rank(capital_expenditure_amount / close, 252), industry)`

## Batch 01 Official Results

- Simulation `348RZu4P94Kx95O12rbWB4kg` completed as alpha `om9kLgo6`.
- Baseline `group_rank(ts_rank(capital_expenditure_amount / close, 84), industry)` landed at IS Sharpe `0.75`, Fitness `0.53`, test Sharpe `1.43`, and drawdown `13.64%`.
- Gate results: `LOW_SHARPE` `FAIL`, `LOW_FITNESS` `FAIL`, `LOW_SUB_UNIVERSE_SHARPE` `PASS`, `SELF_CORRELATION` `PENDING`.
- Submission posture: frozen. The price-normalized capex estimate idea is still below the submission floor on IS and Fitness even though TEST looks stronger.
- Next move: if capital-deployment research returns, it needs a different normalization or a different field family rather than more same-axis polishing.
