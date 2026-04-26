<!-- FROZEN as of 2026-04-27: scout generation paused due to S0 failure pattern. See runs/research-queues/2026-04-27-frozen-pipeline.md -->

# Model Multi-Factor Acceleration Score Rerating Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `model_multi_factor_acceleration_score_rerating`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `D1`

## Hypothesis

Changes in the acceleration of the official model-layer multi-factor score may identify cross-sectional rerating before that repricing is fully reflected in the stock cross-section.

## Why This Could Matter

- This is a genuinely new information source versus the frozen static-score family: it uses the acceleration derivative of a model score, not the same field or a sign/lookback/group tweak on the prior lane.
- The signal is simple enough to explain: if the platform's multi-factor score acceleration is turning, peers may still be slow to catch up.
- The field has full `USA / TOP3000 / D1` coverage and full date coverage, which makes a first batch cheap and interpretable.
- Its visible crowding is moderate and still acceptable for a first minimal batch.

## Official Evidence Boundary

- Confirmed hard facts in this pack come from the official API capture already read in the logged-in browser session:
  - `./runs/session-briefs/2026-04-25-model-live-search.json`
- The session capture was created from a logged-in `GET /data-fields` request against `api.worldquantbrain.com`.

## Data Explorer Search Terms

- Primary terms: `multi factor acceleration`, `factor acceleration`, `model acceleration`
- Synonyms: `composite acceleration`, `style acceleration`, `rerating`
- Abbreviations: `model16`, `multi_factor`, `acceleration score`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `multi_factor_acceleration_score_derivative` | `model16` / `Model > Valuation Models` | Best first anchor for a model-score acceleration family; simple, direct, and still not the frozen static-score lane | Official API capture: `100%` coverage, `100%` date coverage, `MATRIX` in `USA / TOP3000 / D1` | Official API capture: `106` users / `122` alphas |

## Coverage And Quality Checks

- Coverage:
  `multi_factor_acceleration_score_derivative` is fully covered in the official `USA / TOP3000 / D1` model inventory.
- Missingness:
  No missingness warning is visible in the official capture.
- Region / delay compatibility:
  Confirmed in the official logged-in Data Explorer API read.
- Field type:
  The shortlisted Model field is `MATRIX`.

## Why This Is Not A Frozen Family Shell

- It is not an `EPS` sibling or `EPS / close` alias.
- It is not another `cashflow / cap` or capex normalization.
- It is not an `operating_income` history-position repair.
- It is not the same lane as `relative_valuation_rank_derivative` or `growth_potential_rank_derivative`.
- It is not the frozen `multi_factor_static_score_derivative` lane; the source field changes from static score to acceleration of the score.

## Baseline Expression Ideas

1. `group_rank(multi_factor_acceleration_score_derivative, industry)`
2. `group_rank(ts_rank(multi_factor_acceleration_score_derivative, 20), industry)`
3. `rank(multi_factor_acceleration_score_derivative)`

## Likely First Failure

- Sharpe:
  The field may be too bursty or too generic if the acceleration turn is already mostly priced in.
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

- Winner field for continuation: `multi_factor_acceleration_score_derivative`
- Winner baseline to simulate immediately: `group_rank(multi_factor_acceleration_score_derivative, industry)`
- First bounded follow-ups:
  - `group_rank(-multi_factor_acceleration_score_derivative, industry)` for sign control
  - `group_rank(ts_rank(multi_factor_acceleration_score_derivative, 20), industry)` for time-rank stabilization
  - `rank(multi_factor_acceleration_score_derivative)` for neutralization removal control
