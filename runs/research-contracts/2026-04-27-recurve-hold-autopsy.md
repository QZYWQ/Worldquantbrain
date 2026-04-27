# 2026-04-27 RECURVE Hold Autopsy

## Scope

RECURVE is the reverse-engineering pass: start from hold families that still show positive TEST behavior, isolate what fails, and infer what kind of data is missing.

## Evidence Used

- `runs/research-contracts/2026-04-26-family-registry-incubation-update.md`
- `runs/research-contracts/current-incubation-summary.md`
- `runs/research-contracts/family-budget-ledger.json`
- `runs/expression-families/analyst-sibling-branch.md`
- `runs/expression-families/2026-04-21-operating-income-history-position-follow-up.md`
- `runs/expression-families/2026-04-24-actual-sales-delta-fundamental.md`
- `runs/expression-families/2026-04-23-fundamental-model-slow-ratio-equity-cap-structural-follow-up.md`

## Selection Note

- The latest registry update is the source of truth for `min_depth_completed` on legacy rows.
- The compact current summary and the ledger omit `min_depth_completed` on some older entries, so this note prefers the registry row where the sources differ.
- These families are treated as hold / branch families, not as new incubate openings.

## Selected Families

| Family | State | min_depth_completed | Best official line | Readout | Main failure mode |
| --- | --- | --- | --- | --- | --- |
| `actual_sales_delta_fundamental` | hold | true | `group_rank(ts_delta(actual_sales_value_quarterly, 63), industry)` | Baseline `0.35 / 0.13`; sign flip made TEST positive but failed IS and low-sub-universe-sharpe | Still just a lagged quarterly actual-sales delta; needs an earlier top-line lead signal |
| `operating_income_history_position` | hold | true | `group_rank(ts_rank(ts_mean(operating_income, 63), 252), industry)` | Current summary: `1.25 / 0.87`; later ridge/live checks still fail holdout | Reported operating-income history is too lagged and too representation-driven |
| `analyst_eps_sibling_qfv4_industry` | hold | true | `group_rank(ts_rank(anl4_afv4_median_eps/close, 60), industry)` | `1.93 / 1.40`; the annual-median control is still stronger on holdout | qfv4 is still a consensus sibling, not a new information source |
| `fundamental_model_slow_ratio_equity_cap` | hold | true | `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)` | Full-IS `0.89 / 0.60` versus shown-test `1.43 / 1.10`; neutralization-axis probe failed | Cap-normalized balance-sheet ratio is the wrong representation, even when the test card looks stronger |

## Reverse Demand

### `actual_sales_delta_fundamental`

- Need a pre-report top-line momentum signal, not another 63d / 126d delta on the same quarterly actuals.
- Desired properties: earlier turn, broader coverage, less sub-universe fragility, and less dependence on a single quarter-end cadence.

### `operating_income_history_position`

- Need an operational state variable that leads reported operating income instead of lagging it.
- Desired properties: medium-frequency refresh, lower decay, and a cleaner link to business run-rate than a smoothed history rank.

### `analyst_eps_sibling_qfv4_industry`

- Need a revision stream that is not just another EPS sibling and not just another annual-median control.
- Desired properties: less crowding, a more forward-looking surprise element, and enough novelty that holdout does not simply prefer the older consensus line.

### `fundamental_model_slow_ratio_equity_cap`

- Need a non-cap-normalized capital or financing-pressure state, not another balance-sheet ratio polished with more smoothing.
- Desired properties: direct signal on deployment, leverage, or asset-intensity change, with a representation that is less self-correlated to the existing slow-ratio shell.

## Common Denominator

All four lanes are trying to infer the same latent object: a slow corporate state transition. The current inputs are too lagged, too close to consensus, or too close to price-normalized accounting levels.

The missing data class is therefore a **forward-leading operational state proxy**: broad enough to survive holdout, slow enough to avoid bursty turnover, and orthogonal enough to avoid reusing the same accounting shell.

## What That Suggests Next

The most promising new data types are not more same-field windows. They are data classes that can lead the accounting statements:

- relationship / network data between firms and peers
- footnote-level accounting detail
- guidance / backlog / operational revision data
- other non-price state variables that update before the next quarterly print
