<!-- FROZEN as of 2026-04-27: scout generation paused due to S0 failure pattern. See runs/research-queues/2026-04-27-frozen-pipeline.md -->

# Model Growth Potential Rerating Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `model_growth_potential_rerating`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `D1`

## Hypothesis

Changes in the model-layer growth potential rank may identify cross-sectional rerating before that repricing is fully reflected in the stock cross-section.

## Why This Could Matter

- This is a genuinely new information source versus the frozen raw-fundamental and analyst-price lanes: it uses official `Model` data, not `EPS / close`, `cashflow / cap`, `operating_income`, or option/news attention.
- The signal is simple enough to explain: if the platform's growth model says a stock just moved up or down in growth potential rank, peers may still be slow to catch up.
- The field has full `USA / TOP3000 / D1` coverage and full date coverage, which makes a first batch cheap and interpretable.

## Official Evidence Boundary

- Confirmed hard facts in this pack come from the official API captures already read in the live browser session:
  - `https://api.worldquantbrain.com/data-fields?instrumentType=EQUITY&region=USA&delay=1&universe=TOP3000&dataset.id=model16&type=MATRIX&limit=20&offset=20`
- The same session also confirmed the sibling model family facts for `relative_valuation_rank_derivative` and `multi_factor_static_score_derivative`.

## Data Explorer Search Terms

- Primary terms: `growth potential`, `growth rank`, `model growth`
- Synonyms: `rerating`, `growth score`, `model score derivative`
- Abbreviations: `model16`, `growth`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `growth_potential_rank_derivative` | `model16` / `Model > Valuation Models` | Cleanest growth-rerating anchor in the model family; the mechanism is direct and the crowding is still moderate | Official API capture: `100%` coverage, `100%` date coverage, `MATRIX` in `USA / TOP3000 / D1` | Official API capture: `115` users / `133` alphas |
| `multi_factor_static_score_derivative` | `model16` / `Model > Valuation Models` | Backup if the pure growth derivative is too narrow and needs a broader model composite | Official API capture: `100%` coverage, `100%` date coverage, `MATRIX` | Official API capture: `73` users / `86` alphas |
| `multi_factor_acceleration_score_derivative` | `model16` / `Model > Valuation Models` | Backup if the static model composite is too slow and the derivative of acceleration is cleaner | Official API capture: `100%` coverage, `100%` date coverage, `MATRIX` | Official API capture: `106` users / `122` alphas |

## Coverage And Quality Checks

- Coverage:
  `growth_potential_rank_derivative` is fully covered in the official `USA / TOP3000 / D1` model inventory.
- Missingness:
  No missingness warning is visible in the official capture.
- Region / delay compatibility:
  Confirmed in the official live Data Explorer API read.
- Field type:
  All shortlisted Model candidates are `MATRIX`.

## Why This Is Not A Frozen Family Shell

- It is not an `EPS` sibling or `EPS / close` alias.
- It is not another `cashflow / cap` or capex normalization.
- It is not an `operating_income` history-position repair.
- It is not an option/event/news attention near-neighbor.
- It is a packaged `Model` growth rerating source, so the mechanism is growth-model repricing rather than raw-accounting smoothing.

## Baseline Expression Ideas

1. `group_rank(growth_potential_rank_derivative, industry)`
2. `group_rank(ts_rank(growth_potential_rank_derivative, 20), industry)`
3. `rank(growth_potential_rank_derivative)`

## Likely First Failure

- Sharpe:
  The field may be too close to a generic growth factor if the recent derivative is not strong enough on its own.
- Fitness:
  A simple one-field model score can still be too shallow if the rerating is slow or already crowded.
- Turnover:
  The derivative could react too quickly if the field updates in bursts.
- Weight:
  Pure growth rerating could concentrate in a subset of industries if the grouping choice is wrong.
- Sub-universe:
  This still needs live official validation; the saved field inventory alone does not prove sub-universe behavior.
- Self-correlation:
  The main risk is accidental overlap with generic growth-model crowding, not with the frozen EPS/cashflow lines.

## Next Action

- Winner field for continuation: `growth_potential_rank_derivative`
- Winner baseline to simulate immediately: `group_rank(growth_potential_rank_derivative, industry)`
- First bounded follow-ups:
  - `group_rank(-growth_potential_rank_derivative, industry)` for sign control
  - `group_rank(ts_rank(growth_potential_rank_derivative, 20), industry)` for time-rank stabilization
  - `rank(growth_potential_rank_derivative)` for neutralization removal control
