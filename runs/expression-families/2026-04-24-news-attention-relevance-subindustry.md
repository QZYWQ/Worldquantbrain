# News Attention Relevance Subindustry Expression Family

## Metadata

- Date: `2026-04-24`
- Topic: `news_attention_relevance_subindustry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Status: `frozen`

## Hypothesis

Company-specific news relevance may be a cleaner signal than direct sentiment wording, especially if the market underreacts to what is relevant rather than what is merely positive or negative. `vec_avg` is needed here so the news field can be smoothed before the time-series window, and `subindustry` neutralization is the right first control for this branch.

## Research Contract

- Mechanism: news relevance diffusion with simple time smoothing
- Data category: news / altdata
- Idea type: readable single-field ranking
- Universe: `TOP3000`
- Liquidity fit: broad US equity universe
- Holding frequency: medium to slow
- Delay: `1`
- Neutralization target: `subindustry`
- Decay: platform default unless a later batch shows a reason to change it
- Truncation: platform default unless a later batch shows a reason to change it
- NaN policy: leave platform default handling in place for the first batch
- Pasteurization: platform default
- Unit handling: keep the field dimensionless and avoid mixing unlike raw quantities
- Coverage floor: use the verified 50 percent coverage as a first-batch warning, not a reason to add repair logic
- Freshness floor days: not explicitly set for the first batch
- Factor risk hypothesis: the branch may be crowded if relevance is just a proxy for common news tone
- Kill condition: if the relevance baseline and qcm control both fail quickly, stop the family and move to a different field source

## Validation Design

- Primary test period: official platform test period once the baseline loads
- Regime slices: only after the first batch shows real promise
- Liquidity slice: only after the core ridge is directionally viable
- Subuniverse gate: watch the official gate once real simulation results exist
- Factor overlay: none for the first batch
- Comparison controls: `vec_avg(nws18_qcm)` at the same 63d window, then later window sweeps if needed
- Promotion rule: keep the family only if the relevance baseline beats the qcm control and stays readable
- Demotion rule: kill quickly if the first batch looks weak or the holdout story turns bad

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `nws18_relevance`
  - `nws18_qcm`
  - `nws18_nip`
  - `vec_avg`
  - `subindustry`
- Equivalent fallback fields:
  - `nws18_bee`
- Unconfirmed assumptions:
  - `63` days is a sensible first smoothing ridge.
  - `subindustry` is the better first grouping choice than `industry` on this branch.
  - The qcm control is useful as a direct comparison, not as the new primary focus.

## Baseline Expression

```text
group_rank(ts_mean(vec_avg(nws18_relevance), 63), subindustry)
```

## Variant 1

- Goal:
  Compare the nearest control against the baseline.
- Main lever:
  Swap `nws18_relevance` for `nws18_qcm` while keeping the same window and grouping.

```text
group_rank(ts_mean(vec_avg(nws18_qcm), 63), subindustry)
```

## Variant 2

- Goal:
  Test whether faster smoothing reacts better to fresh news flow.
- Main lever:
  Reduce the smoothing window from `63` to `21`.

```text
group_rank(ts_mean(vec_avg(nws18_relevance), 21), subindustry)
```

## Variant 3

- Goal:
  Test whether slower smoothing improves stability and holdout behavior.
- Main lever:
  Increase the smoothing window from `63` to `126`.

```text
group_rank(ts_mean(vec_avg(nws18_relevance), 126), subindustry)
```

## Expected First Failure

- Sharpe:
  The relevance signal may still be too weak or too crowded.
- Fitness:
  Holdout weakness may show up before the in-sample ridge looks obviously bad.
- Turnover:
  Faster windows could still be too active.
- Weight:
  Concentration may show up if only a narrow subset of names carries the useful effect.
- Sub-universe:
  Unknown until real simulation and check evidence exist.
- Self-correlation:
  Unknown until official check resolves.

## Optimization Order

1. Keep the field fixed and compare `qcm` against `relevance` first.
2. Only if the relevance ridge survives should the window sweep move to `21` and `126`.
3. If the first batch is weak, branch to `nws18_nip` or kill the lane instead of adding operator soup.

## Current Decision

Frozen after the official budget ledger and the live partial tests both pointed away from further polishing.

## Next Simulation Batch

- Baseline:
  `group_rank(ts_mean(vec_avg(nws18_relevance), 63), subindustry)`
- Variant 1:
  `group_rank(ts_mean(vec_avg(nws18_qcm), 63), subindustry)`
- Variant 2:
  `group_rank(ts_mean(vec_avg(nws18_relevance), 21), subindustry)`
- Variant 3:
  `group_rank(ts_mean(vec_avg(nws18_relevance), 126), subindustry)`
