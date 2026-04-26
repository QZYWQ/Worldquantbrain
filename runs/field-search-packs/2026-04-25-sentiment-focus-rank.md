# Sentiment Focus Rank Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `sentiment-focus-rank`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Research Sentiment composite rank fields may capture changes in analyst conviction and ranking pressure better than the frozen EPS, cashflow, or social-buzz lanes. The cleanest live entry is `snt1_d1_dynamicfocusrank`, with sibling fields available if the baseline is viable.

## Why This Could Matter

- This is a genuinely new source versus the frozen analyst EPS, cashflow, operating-income, model rerating, and social buzz lanes.
- The live Data Explorer page shows the sentiment family is available in `USA / D1 / TOP3000` with full date coverage.
- The least crowded live field in this lane is still much lighter than the broad social-media / news families that were already killed or frozen.
- The field descriptions are interpretable enough to explain the thesis without operator soup.

## Data Explorer Search Terms

- Primary terms: `sentiment`, `focus rank`, `dynamicfocusrank`
- Synonyms: `analyst sentiment`, `composite rank`, `stockrank`, `fundamentalfocusrank`
- Abbreviations: `snt1`, `cored1`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `snt1_d1_dynamicfocusrank` | `sentiment1` / `Research Sentiment Data` | Best live baseline; composite rank emphasizing dynamic, short-term analyst sentiment signals | Live Data Explorer: `Matrix`, `56.51%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live Data Explorer: `291` users, `1,866` alphas |
| `snt1_d1_stockrank` | `sentiment1` / `Research Sentiment Data` | Equity-style sibling that keeps the same sentiment family but changes the score semantics | Live Data Explorer: `Matrix`, `56.72%` coverage, `100%` date coverage | Live Data Explorer: `226` users, `2,142` alphas |
| `snt1_d1_fundamentalfocusrank` | `sentiment1` / `Research Sentiment Data` | Fundamental/value sibling that stays inside the same sentiment source but shifts the emphasis | Live Data Explorer: `Matrix`, `56.84%` coverage, `100%` date coverage | Live Data Explorer: `234` users, `2,505` alphas |
| `snt1_cored1_score` | `sentiment1` / `Research Sentiment Data` | Broader proprietary analyst score; useful as a higher-coverage sibling control | Live Data Explorer: `Matrix`, `63.29%` coverage, `100%` date coverage | Live Data Explorer: `540` users, `3,731` alphas |

## Coverage And Quality Checks

- Coverage: live Sentiment family coverage is usable for a first probe, but the exact inventory is marginal: `56.51%`-`56.84%` on the three rank siblings and `63.29%` on `snt1_cored1_score`.
- Missingness: the family is not fully covered, so the first batch should still watch for concentration or sparse-name behavior.
- Region / delay compatibility: confirmed live on the official Data Explorer page under `USA / 1 / TOP3000`.
- Field type: all four candidate fields are `Matrix` fields.

## Baseline Expression Ideas

1. `snt1_d1_dynamicfocusrank`
2. `snt1_d1_stockrank`
3. `snt1_d1_fundamentalfocusrank`

## Likely First Failure

- Sharpe: the family may already be crowded, so the raw signal can be weak even if the direction is sensible.
- Fitness: the first bottleneck is likely to be crowding rather than coverage.
- Turnover: probably not the main failure mode for the rank fields, but still worth checking.
- Weight: less likely to fail structurally than the sparse event lanes because the field coverage is respectable.
- Sub-universe: should be watched in the real batch because coverage is not full.
- Self-correlation: the main expected bottleneck, given the dataset-wide usage visible on the official page.

## Next Action

- Which field should be tried first? `snt1_d1_dynamicfocusrank`
- Which baseline expression should be simulated first? `snt1_d1_dynamicfocusrank`
- Which 2-3 same-family variants should follow? `snt1_d1_stockrank`, `snt1_d1_fundamentalfocusrank`, `snt1_cored1_score`

## Official Evidence

- Live Data Explorer search for `snt1_d1_dynamicfocusrank`: `platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=snt1_d1_dynamicfocusrank&universe=TOP3000`
- Live Data Explorer search for `snt1_cored1_score`: `platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=snt1_cored1_score&universe=TOP3000`
- Saved official API field inventory: `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`
