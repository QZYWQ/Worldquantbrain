# V3 Single Tracking Candidate Simulation Result

- Date: 2026-04-29
- Scope: exactly one approved v3 future tracking candidate simulation
- Miner manual batch: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_v3_single_tracking_candidate_manual_batch.json`
- Miner result batch: `/Users/zpdedn/Documents/github/worldquant-miner/results/batch_manual_1777431340.json`
- Archived batch copy: `runs/candidate-batches/2026-04-29/105601_batch_manual_1777431340.json`
- Archive manifest: `runs/simulation-captures/2026-04-29/105601_manifest.json`
- Simulations run: exactly 1
- Variants run: none
- Runner-up hold candidates run: none
- Replacement alphas run: none
- Auth file contents manually inspected or displayed: no
- Push performed: no

## Run Discipline

The user explicitly approved simulation for only this single v3 tracking
candidate:

`alt_accrual_balance_earnings_certainty_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_common_stock_q_126_24_industry`

No other v3 `run_now_candidates`, runner-up hold candidates, variants, sibling
windows, neutralization twins, or replacement alphas were run.

## Result

- Name:
  `alt_accrual_balance_earnings_certainty_rank_derivative_inventory_turnover_fn_proceeds_from_issuance_of_common_stock_q_126_24_industry`
- Family: `accruals_asset_growth_balance_sheet`
- Alpha id: `om3M3Agb`
- Simulation id: `1777431210.523686_0.8857911503997973`
- Fingerprint: `b9a2cbcda81d7f29c78271cbaab13415`
- Platform status: `COMPLETE`
- Local status: `success`
- Grade: `INFERIOR`
- Stage: `IS`
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

## Checks

| Check | Result | Limit | Value |
| --- | --- | ---: | ---: |
| `LOW_SHARPE` | `FAIL` | 1.25 | 0.05 |
| `LOW_FITNESS` | `FAIL` | 1.0 | 0.01 |
| `LOW_TURNOVER` | `PASS` | 0.01 | 0.0586 |
| `HIGH_TURNOVER` | `PASS` | 0.7 | 0.0586 |
| `CONCENTRATED_WEIGHT` | `PASS` |  |  |
| `LOW_SUB_UNIVERSE_SHARPE` | `PASS` | 0.02 | 0.42 |
| `SELF_CORRELATION` | `PENDING` |  |  |
| `MATCHES_COMPETITION` | `PASS` |  |  |

## Classification

- Hopeful: no. Fitness is far below 0.5 and Sharpe is far below the practical
  continuation range.
- Internal candidate: no. Sharpe and Fitness are both too weak.
- Relation to E5: distinct; no close-volume correlation reversal and no
  `ts_corr(rank(close), rank(volume), 60/70/80/90)` structure.
- Relation to failed lanes: passes hard-negative filters for known failed lanes.
  It is not the failed v2 `cashflow_efficiency_rank_derivative + assets +
  cashflow_op` structure and not a close60 or E5 neighbor.
- Relation to historical lessons: no confirmed historical-kill penalty in the
  v3 shortlist review.

## Readout

The candidate completed but did not produce hopeful evidence. It had a very low
positive Fitness of 0.01, Sharpe 0.05, and Drawdown 0.1743. Turnover 0.0586 is
below the preferred 0.08 to 0.30 research band, which suggests the medium-horizon
fundamental formulation is still too inert even though it avoided the known v2
failed cashflow/assets/cashflow-op lane.

Decision: stop after this one simulation as requested. Do not run variants,
siblings, runner-up hold candidates, or replacement alphas automatically.
