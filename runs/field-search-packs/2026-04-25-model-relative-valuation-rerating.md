<!-- FROZEN as of 2026-04-27: scout generation paused due to S0 failure pattern. See runs/research-queues/2026-04-27-frozen-pipeline.md -->

# Model Relative Valuation Rerating Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `model_relative_valuation_rerating`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `D1`

## Hypothesis

Recent changes in WorldQuant's model-layer relative valuation ranking may identify cross-sectional rerating before that repricing is fully reflected in the stock cross-section.

## Why This Could Matter

- This is a genuinely new information source versus the frozen raw-fundamental and analyst-price lanes: it uses official `Model` data, not `EPS / close`, `cashflow / cap`, `operating_income`, or option/news attention.
- The signal is simple enough to explain: if the platform's valuation model says a stock just moved up or down in relative valuation rank, peers may still be slow to catch up.
- The saved official field inventory shows full `USA / TOP3000 / D1` coverage and full date coverage, which makes a first batch cheap and interpretable.

## Official Evidence Boundary

- Confirmed hard facts in this pack come from two official API captures:
  - fresh session capture:
    `./runs/session-briefs/2026-04-25-model-live-search.json`
  - saved broad field inventory:
    `./runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`
- The fresh session capture was created from a logged-in official `GET /data-fields` request against `api.worldquantbrain.com` and then read back by the main thread.

## Data Explorer Search Terms

- Primary terms: `relative valuation`, `valuation derivative`, `model valuation`
- Synonyms: `rerating`, `valuation rank`, `model score derivative`
- Abbreviations: `model16`, `valuation`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `relative_valuation_rank_derivative` | `model16` / `Model > Valuation Models` | Cleanest valuation-rerating anchor; the mechanism is direct and the crowding is the lightest in the shortlist | Fresh official capture: `100%` coverage, `100%` date coverage, `MATRIX` in `USA / TOP3000 / D1` | Fresh official capture: `60` users / `77` alphas |
| `multi_factor_static_score_derivative` | `model16` / `Model > Valuation Models` | Good backup if the pure valuation derivative is too narrow and needs a broader model composite | Fresh official capture: `100%` coverage, `100%` date coverage, `MATRIX` | Fresh official capture: `73` users / `86` alphas |
| `growth_potential_rank_derivative` | `model16` / `Model > Valuation Models` | Growth-rerating backup if the winner ends up too value-like or too crowded | Fresh official capture: `100%` coverage, `100%` date coverage, `MATRIX` | Fresh official capture: `115` users / `133` alphas |

## Coverage And Quality Checks

- Coverage:
  `relative_valuation_rank_derivative` is fully covered in the fresh official `2026-04-25` model search capture.
- Missingness:
  No missingness warning is visible in the saved official capture; this looks materially cleaner than the half-covered frozen news/fundamental lanes.
- Region / delay compatibility:
  Confirmed in the fresh official `USA / TOP3000 / D1` model search capture.
- Field type:
  All shortlisted Model candidates are `MATRIX`.

## Why This Is Not A Frozen Family Shell

- It is not an `EPS` sibling or `EPS / close` alias.
- It is not another `cashflow / cap` or capex normalization.
- It is not an `operating_income` history-position repair.
- It is not an option/event/news attention near-neighbor.
- It is a packaged `Model` rerating source, so the mechanism is valuation-model repricing rather than raw-accounting smoothing.

## Baseline Expression Ideas

1. `group_rank(relative_valuation_rank_derivative, industry)`
2. `group_rank(ts_rank(relative_valuation_rank_derivative, 20), industry)`
3. `rank(relative_valuation_rank_derivative)`

## Likely First Failure

- Sharpe:
  The field may be too close to a generic value rerating factor if the recent derivative is not strong enough on its own.
- Fitness:
  A simple one-field model score can still be too shallow if the rerating is slow or already crowded.
- Turnover:
  The derivative could react too quickly if the field updates in bursts.
- Weight:
  Pure value rerating could concentrate in a subset of industries if the grouping choice is wrong.
- Sub-universe:
  This still needs live official validation; the saved field inventory alone does not prove sub-universe behavior.
- Self-correlation:
  The main risk is accidental overlap with generic value-model crowding, not with the frozen EPS/cashflow lines.

## Next Action

- Winner field for continuation: `relative_valuation_rank_derivative`
- Winner baseline to simulate once fresh logged-in access is restored in the main thread: `group_rank(relative_valuation_rank_derivative, industry)`
- First bounded follow-ups:
  - `group_rank(-relative_valuation_rank_derivative, industry)` for sign control
  - `group_rank(ts_rank(relative_valuation_rank_derivative, 20), industry)` for time-rank stabilization
  - `rank(relative_valuation_rank_derivative)` for neutralization removal control
