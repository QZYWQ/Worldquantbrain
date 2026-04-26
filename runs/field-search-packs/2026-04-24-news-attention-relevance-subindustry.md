# News Attention Relevance Search Pack

## Metadata

- Date: `2026-04-24`
- Topic: `news_attention_relevance_subindustry`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Status: `frozen`

## Hypothesis

Company-specific news relevance may be a cleaner anchor than direct sentiment wording on this branch. Using `subindustry` neutralization should preserve shared sector news flow while keeping the first batch readable and easy to kill if it fails.

## Why This Could Matter

- Moves from the older bee-style anchor to the relevance field, using `vec_avg` so the event-style news data can be smoothed safely.
- Keeps the first batch interpretable instead of forcing a sparse or exotic signal.
- Uses `subindustry` because the current local branch review favored it over `industry`.

## Data Explorer Search Terms

- Primary terms: `nws18`, `Ravenpack News Data`
- Synonyms: `news relevance`, `relevance`, `high confidence news`, `impact`
- Abbreviations: `relevance`, `qcm`, `nip`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `nws18_relevance` | `Ravenpack News Data` | Best first anchor for the current branch; direct company relevance and the current live baseline focus | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `642` visible alphas |
| `nws18_qcm` | `Ravenpack News Data` | Control field for high-confidence relevant news; useful to test whether relevance is just wording or genuinely different | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `607` visible alphas |
| `nws18_nip` | `Ravenpack News Data` | Fallback if relevance and qcm both fail and we need a different proxy for news impact | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `1233` visible alphas |
| `nws18_bee` | `Ravenpack News Data` | Historical anchor from the previous branch; keep only as a comparison point, not the next live focus | `50%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | `485` visible alphas |

## Coverage And Quality Checks

- Coverage:
  The official Data Explorer search shows `50%` coverage and `100%` date coverage for the verified news fields.
- Missingness:
  Coverage is partial, so the first batch should stay simple.
- Region / delay compatibility:
  The fields are visible in official `USA / D1 / TOP3000` search results with `delay=1`.
- Field type:
  The fields are vector fields, so smoothing plus group ranking is the safest first move.

## Baseline Expression Ideas

1. `group_rank(ts_mean(vec_avg(nws18_relevance), 63), subindustry)`
2. `group_rank(ts_mean(vec_avg(nws18_qcm), 63), subindustry)`
3. `group_rank(ts_mean(vec_avg(nws18_nip), 63), subindustry)`

## Likely First Failure

- Sharpe:
  The relevance signal may still be noisy or too weak.
- Fitness:
  Crowding or weak holdout may be the first blocker.
- Turnover:
  Faster windows could be too active.
- Weight:
  Concentration risk if only a small subset of names carries the effect.
- Sub-universe:
  Unknown until real simulation and check evidence appear.
- Self-correlation:
  Unknown until official check resolves.

## Next Action

- Which field should be tried first? `nws18_relevance`
- Which baseline expression should be simulated first? `group_rank(ts_mean(vec_avg(nws18_relevance), 63), subindustry)`
- Which 2-3 same-family variants should follow? none; the family is frozen after negative partial tests and the duplicate live run was canceled
