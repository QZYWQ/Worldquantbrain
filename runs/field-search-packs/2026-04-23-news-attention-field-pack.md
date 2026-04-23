# News Attention Field Search Pack

## Metadata

- Date: `2026-04-23`
- Topic: `news_attention`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Company-specific news sentiment may be a cleaner and less crowded non-analyst family than the crowded buzz lane, especially if we start from the simplest earnings-growth news field and keep the first batch readable.

## Why This Could Matter

- Moves away from the crowded buzz line while staying inside the news family.
- Keeps the first batch interpretable instead of forcing a sparse or exotic signal.
- Lets us separate field choice from window tuning before any field replacement branch.

## Data Explorer Search Terms

- Primary terms: `nws18`, `Ravenpack News Data`
- Synonyms: `news sentiment`, `relevance`, `impact`
- Abbreviations: `bee`, `qcm`, `relevance`, `nip`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `nws18_bee` | `Ravenpack News Data` | Best first field for the news family; direct sentiment on earnings growth and the simplest anchor for a healthy baseline | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `485` visible alphas |
| `nws18_qcm` | `Ravenpack News Data` | Secondary control for high-confidence relevant news | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `607` visible alphas |
| `nws18_relevance` | `Ravenpack News Data` | Relevance-to-company control that may behave differently from direct sentiment wording | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `642` visible alphas |
| `nws18_nip` | `Ravenpack News Data` | Impact-of-news fallback if the sentiment/relevance pair needs a different proxy | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `1233` visible alphas |

## Coverage And Quality Checks

- Coverage:
  The official Data page shows `50%` coverage and `100%` date coverage for the verified news fields.
- Missingness:
  Coverage is not full, so keep the first batch simple and avoid extra repair logic.
- Region / delay compatibility:
  The verified fields are visible in official `USA / D1 / TOP3000` search results with `delay=1`.
- Field type:
  The listed fields are vector fields, so a simple aggregation or ranking wrapper is the safest first move.

## Baseline Expression Ideas

1. `group_rank(ts_mean(nws18_bee, 63), industry)`
2. `group_rank(ts_mean(nws18_bee, 21), industry)`
3. `group_rank(ts_mean(nws18_bee, 126), industry)`

## Likely First Failure

- Sharpe:
  The sentiment-growth signal may still be noisy or crowded.
- Fitness:
  Weak robustness if the signal is only a small crowding artifact.
- Turnover:
  Faster smoothing may be too active.
- Weight:
  Concentration risk if the field only works on a narrow subset of names.
- Sub-universe:
  Unknown until real simulation evidence appears.
- Self-correlation:
  Unknown until live check evidence exists.

## Next Action

- Which field should be tried first? `nws18_bee`
- Which baseline expression should be simulated first? `group_rank(ts_mean(nws18_bee, 63), industry)`
- Which 2-3 same-family variants should follow? `21d`, `126d`, `252d` window controls before any field replacement
