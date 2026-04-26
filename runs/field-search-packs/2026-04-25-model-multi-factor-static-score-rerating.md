<!-- FROZEN as of 2026-04-27: scout generation paused due to S0 failure pattern. See runs/research-queues/2026-04-27-frozen-pipeline.md -->

# Model Multi-Factor Static Score Rerating Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `model_multi_factor_static_score_rerating`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `D1`

## Hypothesis

Recent changes in the model-layer static multi-factor score may identify cross-sectional rerating before that repricing is fully reflected in the stock cross-section.

## Why This Could Matter

- This is a genuinely new information source versus the frozen raw-fundamental, analyst-top-line, and model-relative-valuation lanes: it uses official `Model` data, not `EPS / close`, `cashflow / cap`, `operating_income`, or valuation-rank derivatives.
- The signal is simple enough to explain: if the platform's multi-factor score just moved up or down, peers may still be slow to catch up.
- The field has full `USA / TOP3000 / D1` coverage and full date coverage, which makes a first batch cheap and interpretable.
- Its visible crowding is lighter than the earlier frozen Model growth and valuation rerating branches.

## Official Evidence Boundary

- Confirmed hard facts in this pack come from the official API capture already read in the logged-in browser session:
  - `./runs/session-briefs/2026-04-25-model-live-search.json`
- The session capture was created from a logged-in `GET /data-fields` request against `api.worldquantbrain.com`.

## Data Explorer Search Terms

- Primary terms: `multi factor score`, `static score`, `model static`
- Synonyms: `composite score`, `factor score`, `style score`, `rerating`
- Abbreviations: `model16`, `multi_factor`, `static score`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `multi_factor_static_score_derivative` | `model16` / `Model > Valuation Models` | Best first anchor for a model-score rerating family; simple, direct, and lower crowding than the growth/valuation siblings | Official API capture: `100%` coverage, `100%` date coverage, `MATRIX` in `USA / TOP3000 / D1` | Official API capture: `73` users / `86` alphas |
| `multi_factor_acceleration_score_derivative` | `model16` / `Model > Valuation Models` | Backup if the static score is too slow and the derivative-of-acceleration version is cleaner | Official API capture: `100%` coverage, `100%` date coverage, `MATRIX` | Official API capture: `106` users / `122` alphas |

## Coverage And Quality Checks

- Coverage:
  `multi_factor_static_score_derivative` is fully covered in the official `USA / TOP3000 / D1` model inventory.
- Missingness:
  No missingness warning is visible in the official capture.
- Region / delay compatibility:
  Confirmed in the official logged-in Data Explorer API read.
- Field type:
  The shortlisted Model fields are `MATRIX`.

## Why This Is Not A Frozen Family Shell

- It is not an `EPS` sibling or `EPS / close` alias.
- It is not another `cashflow / cap` or capex normalization.
- It is not an `operating_income` history-position repair.
- It is not the same lane as `relative_valuation_rank_derivative` or `growth_potential_rank_derivative`.
- It is a packaged `Model` multi-factor score derivative, so the mechanism is composite-score repricing rather than raw-accounting smoothing.

## Baseline Expression Ideas

1. `group_rank(multi_factor_static_score_derivative, industry)`
2. `group_rank(ts_rank(multi_factor_static_score_derivative, 20), industry)`
3. `rank(multi_factor_static_score_derivative)`

## Likely First Failure

- Sharpe:
  The field may be too generic if the model score change is already fully priced in.
- Fitness:
  A one-field model score can still be too shallow after robustness penalties.
- Turnover:
  The derivative could react too quickly if the underlying model refreshes in bursts.
- Weight:
  The signal may concentrate in a narrow style cohort if the grouping choice is wrong.
- Sub-universe:
  This still needs live official validation; the saved field inventory alone does not prove sub-universe behavior.
- Self-correlation:
  The main risk is accidental overlap with generic style-factor crowding.

## Next Action

- Winner field for continuation: `multi_factor_static_score_derivative`
- Winner baseline to simulate immediately: `group_rank(multi_factor_static_score_derivative, industry)`
- First bounded follow-ups:
  - `group_rank(-multi_factor_static_score_derivative, industry)` for sign control
  - `group_rank(ts_rank(multi_factor_static_score_derivative, 20), industry)` for time-rank stabilization
  - `rank(multi_factor_static_score_derivative)` for neutralization removal control
