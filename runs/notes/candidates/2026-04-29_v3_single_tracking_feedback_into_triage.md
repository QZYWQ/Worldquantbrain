# V3 Single Tracking Feedback Into Offline Triage

- Date: 2026-04-29
- Scope: feedback import into offline triage and v4 planning
- No WQ simulation was run in this feedback task.
- No simulation endpoint was called.
- No runnable batch was created.
- Miner source changes: `tools/build_offline_candidate_shortlist.py`, `tests/test_offline_candidate_triage.py`
- Miner v4 design artifact: `manual_alphas/2026-04-29_offline_generation_v4_design_DO_NOT_RUN.json`

## Source Result

- Name: `alt_accrual_balance_earnings_certainty_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_common_stock_q_126_24_industry`
- Alpha id: `om3M3Agb`
- Fingerprint: `b9a2cbcda81d7f29c78271cbaab13415`
- Family: `accruals_asset_growth_balance_sheet`
- Expression:

```text
group_neutralize(ts_decay_linear(group_zscore(rank(ts_delta(earnings_certainty_rank_derivative, 126)), sector) + group_zscore(rank(ts_delta(inventory_turnover, 126)), sector) - group_zscore(rank(ts_delta(fn_proceeds_from_issuance_of_common_stock_q, 252)), sector), 24), industry)
```

| Metric | Value |
| --- | ---: |
| Sharpe | 0.05 |
| Fitness | 0.01 |
| Turnover | 0.0586 |
| Margin | 0.000102 |
| Drawdown | 0.1743 |
| Returns | 0.003 |

Checks failed `LOW_SHARPE` and `LOW_FITNESS`. Turnover, concentration,
sub-universe, and competition checks passed; `SELF_CORRELATION` remained
pending. The readout remains: not hopeful, not an internal candidate, inferior.

## Decision

Close and penalize this simple near-neighbor lane:

- `earnings_certainty_rank_derivative`
- `inventory_turnover`
- `fn_proceeds_from_issuance_of_common_stock_q`
- medium-horizon `ts_delta` / `group_zscore` / `rank` / `ts_decay_linear`
- 126/189 style siblings and neutralization-only twins

This is not a global ban on `accruals_asset_growth_balance_sheet`. Distinct
balance-sheet or accrual formulations may remain viable when they use materially
different fields, a different economic mechanism, and cleaner turnover profile.

## Triage Changes

The miner offline triage now adds these v3 single tracking risk flags for the
simple same-field-trio near-neighbor:

- `failed_v3_single_tracking_accrual_inventory_common_stock_simple_form`
- `failed_v3_single_tracking_low_sharpe_low_fitness`
- `failed_v3_single_tracking_drawdown_watch`

The failed-lane relation now treats `failed_v3_*` and `v3_*` flags as
`penalized`, consistent with the earlier reviewed top3, v2 top3, and historical
lesson penalties. The low-turnover inertia check was also widened so slow
fundamental/analyst medium-horizon structures with decay up to 24 can be flagged;
this covers the observed Turnover 0.0586 case.

Focused tests were added for:

- exact v3 failed near-expression penalty
- low-turnover inertia risk on the 0.0586 lane shape
- same-field-trio sibling relation marked as penalized
- distinct accrual/balance-sheet candidate with different fields still retained
- output remains `DO_NOT_RUN`
- no simulation command appears in offline output

## V4 Design Direction

The new v4 design artifact is planning-only and `DO_NOT_RUN`. It continues to
use historical lessons as non-runnable negative knowledge and explicitly avoids:

- the v3 failed simple accrual field trio
- reviewed top3 and v2 top3 failed near-neighbors
- confirmed historical killed/frozen near-neighbors
- E5 close-volume correlation reversal and corr60/70/80/90
- close60 reversal lanes
- raw single-field seeds
- ultra-low-turnover inert candidates

For v4, keep accruals/balance-sheet open only when the candidate changes both
field mix and mechanism. Prefer truly different field families, profitability
acceleration, rebuilt forecast/option/news structures, and medium-horizon
multi-field composites with expected turnover closer to 0.08 to 0.30.
