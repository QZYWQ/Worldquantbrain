# Implied Volatility Skew Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `implied-volatility-skew`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Option implied-volatility skew may carry a clean, interpretable return signal because the official BRAIN community guidance says volatility skew can be negatively associated with individual stock returns at the company level. The raw tenor family is the right first source; live control on the first batch points to a positive working direction, with `implied_volatility_mean_skew_60` as the baseline and nearby tenor siblings as the first continuation set.

## Why This Could Matter

- This is a genuinely new source versus the frozen analyst, cashflow, operating-income, model rerating, and call-breakeven lanes.
- The live Data Explorer page shows the field under the official `Volatility Data` dataset, so this is not a recycled event or news proxy.
- The field is a direct skew measurement, not a cosmetic sign flip on a closed lane.
- Crowding is present but much lower than the broad call implied-volatility fields, so the skew lane still has room to test.

## Data Explorer Search Terms

- Primary terms: `implied volatility skew`, `volatility skew`, `iv skew`
- Synonyms: `mean skew`, `skew steepness`, `option volatility`
- Abbreviations: `iv`, `skew`, `option8`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `implied_volatility_mean_skew_60` | `option8` / `Volatility Data` | Best first baseline; medium-tenor skew is interpretable and centrally located in the curve | Live Data Explorer: `Matrix`, `69%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live page shows `935` alphas; saved inventory shows `367` visible users |
| `implied_volatility_mean_skew_20` | `option8` / `Volatility Data` | Shorter tenor sibling for the same skew thesis | Live Data Explorer: `Matrix`, `69%` coverage, `100%` date coverage | Live page shows `669` alphas |
| `implied_volatility_mean_skew_90` | `option8` / `Volatility Data` | Longer tenor sibling to test whether the curve is more stable farther out | Live Data Explorer: `Matrix`, `69%` coverage, `100%` date coverage | Live page shows `1,376` alphas |
| `implied_volatility_mean_skew_180` | `option8` / `Volatility Data` | Farther tenor control that tests a slower version of the same thesis | Live Data Explorer: `Matrix`, `69%` coverage, `100%` date coverage | Live page shows `975` alphas |

## Coverage And Quality Checks

- Coverage: the skew family is usable for a first official batch, with `69%` coverage and `100%` date coverage on the live page.
- Missingness: this is not full coverage, so the batch still needs to watch for concentration and sub-universe fragility.
- Region / delay compatibility: confirmed live on the official Data Explorer page under `USA / 1 / TOP3000`.
- Field type: all four candidate fields are `Matrix` fields.

## Baseline Expression Ideas

1. `group_rank(implied_volatility_mean_skew_60, industry)`
2. `group_rank(implied_volatility_mean_skew_20, industry)`
3. `group_rank(implied_volatility_mean_skew_90, industry)`

## Likely First Failure

- Sharpe: the skew thesis may be directionally right but too weak once normalized cross-sectionally.
- Fitness: crowding could suppress the edge even if the direction is sensible.
- Turnover: probably not the main failure mode for these matrix fields.
- Weight: less likely to fail structurally than the sparse event lanes because coverage is respectable.
- Sub-universe: still needs the real official result because coverage is not full.
- Self-correlation: a real risk because this is a recognizable options signal family.

## Next Action

- Which field should be tried first? `implied_volatility_mean_skew_60`
- Which baseline expression should be simulated first? `group_rank(implied_volatility_mean_skew_60, industry)`
- Which 3 same-family variants should follow? `group_rank(implied_volatility_mean_skew_20, industry)`, `group_rank(implied_volatility_mean_skew_90, industry)`, `group_rank(implied_volatility_mean_skew_180, industry)`

## Official Evidence

- Live Data Explorer search for `implied_volatility_mean_skew_60`: `platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=implied_volatility_mean_skew_60&universe=TOP3000`
- Live Data Explorer dataset page for the matching volatility dataset: `platform.worldquantbrain.com/data/data-sets/option8?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Saved official API field inventory: `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`

## Batch 01 Outcome

- The full tenor sweep did not clear the continuation floor.
- Test-period metrics from the live Simulate page:
  - `group_rank(implied_volatility_mean_skew_20, industry)` — Sharpe `1.15` / Fitness `0.22` / Turnover `102.90%` / Returns `3.91%` / Drawdown `2.13%` / Margin `0.76‱`
  - `group_rank(implied_volatility_mean_skew_60, industry)` — Sharpe `0.95` / Fitness `0.27` / Turnover `58.53%` / Returns `4.61%` / Drawdown `2.65%` / Margin `1.57‱`
  - `group_rank(implied_volatility_mean_skew_90, industry)` — Sharpe `0.92` / Fitness `0.27` / Turnover `55.02%` / Returns `4.69%` / Drawdown `3.55%` / Margin `1.70‱`
  - `group_rank(implied_volatility_mean_skew_180, industry)` — Sharpe `0.80` / Fitness `0.22` / Turnover `51.31%` / Returns `4.00%` / Drawdown `4.10%` / Margin `1.56‱`
- Decision: freeze this family for the current budget.
- Next jump family source: `option4` open-interest / volatility-spread branch, after fresh official field verification.
