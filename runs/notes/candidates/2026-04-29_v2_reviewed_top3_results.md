# V2 Reviewed Shortlist Top-3 Results

- Date: 2026-04-29
- Scope: capped simulation of offline-reviewed v2 shortlist candidates
- Source review commit: `c63d755`
- Miner manual batch: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_v2_reviewed_top3_manual_batch.json`
- Miner result batch: `/Users/zpdedn/Documents/github/worldquant-miner/results/batch_manual_1777398729.json`
- Archived batch copy: `runs/candidate-batches/2026-04-29/015253_batch_manual_1777398729.json`
- Archive manifest: `runs/simulation-captures/2026-04-29/015253_manifest.json`

## Run Discipline

- This was the offline-reviewed v2 shortlist capped top-3 simulation.
- Exactly 3 alphas were run.
- No variants were run.
- No replacement alpha was added after failures.
- No Codex alpha generation was used.
- No automatic generation path was used.
- No alpha was submitted; this was simulation only.

## Summary

All three simulations completed, but none produced a hopeful or internal
candidate. Every result failed `LOW_SHARPE` and `LOW_FITNESS`; the option
positioning candidate also failed `CONCENTRATED_WEIGHT` and
`LOW_SUB_UNIVERSE_SHARPE`.

Decision: stop this v2 shortlist lane and feed these failures back into the
offline generation and triage loop. Do not run local variants automatically.

## Results

### 1. `balance_accrual_norm_cashflow_efficiency_rank_derivative_assets_cashflow_op_126_12_subindustry`

- Alpha id: `JjgEOmgm`
- Family: `accruals_asset_growth_balance_sheet`
- Neutralization: `subindustry`
- Fingerprint: `7e380c1441955f47eb9dc4e3dbdbd4f3`
- Status: `success` / simulation `COMPLETE`
- Sharpe: -0.27
- Fitness: -0.08
- Turnover: 0.0689
- Margin: -0.000317
- Drawdown: 0.1083
- Returns: -0.0109
- Failed checks: `LOW_SHARPE`, `LOW_FITNESS`
- Pending checks: `SELF_CORRELATION`
- Passing checks: `LOW_TURNOVER`, `HIGH_TURNOVER`, `CONCENTRATED_WEIGHT`,
  `LOW_SUB_UNIVERSE_SHARPE`, `MATCHES_COMPETITION`
- Hopeful: no
- Internal candidate: no
- Relation to E5: distinct; no close-volume correlation reversal and no
  corr60/70/80/90 structure.
- Relation to failed lanes: not an E5 neighbor and not the failed simple
  cashflow/assets plus revenue/assets stability form. The weak result suggests
  this specific cash-flow-efficiency plus asset-growth plus operating-cash-flow
  construction should be treated as a negative v2 example.
- Expression:

```text
group_neutralize(ts_decay_linear(group_zscore(rank(ts_delta(cashflow_efficiency_rank_derivative, 126)), sector) - group_zscore(rank(ts_delta(assets, 252)), sector) + group_zscore(rank(ts_delta(cashflow_op, 126)), sector), 12), subindustry)
```

### 2. `sales_revision_norm_sales_estimate_average_annual_lowest_sales_estimate_analyst_revision_rank_derivative_126_12_industry`

- Alpha id: `O0bPZ9L7`
- Family: `earnings_estimate_revision`
- Neutralization: `industry`
- Fingerprint: `1fe501d79ef9f780a511fc8753cc897d`
- Status: `success` / simulation `COMPLETE`
- Sharpe: -0.17
- Fitness: -0.04
- Turnover: 0.0553
- Margin: -0.000226
- Drawdown: 0.1214
- Returns: -0.0063
- Failed checks: `LOW_SHARPE`, `LOW_FITNESS`
- Pending checks: `SELF_CORRELATION`
- Passing checks: `LOW_TURNOVER`, `HIGH_TURNOVER`, `CONCENTRATED_WEIGHT`,
  `LOW_SUB_UNIVERSE_SHARPE`, `MATCHES_COMPETITION`
- Hopeful: no
- Internal candidate: no
- Relation to E5: distinct; no close-volume correlation reversal pattern.
- Relation to failed lanes: not the failed top-3 EPS mean plus DTS dispersion
  form, but this specific sales-estimate-average plus low-estimate penalty plus
  analyst-revision derivative design was weak and slightly below the preferred
  turnover range.
- Expression:

```text
group_neutralize(ts_decay_linear(group_zscore(rank(ts_delta(sales_estimate_average_annual, 126)), sector) - group_zscore(rank(ts_rank(lowest_sales_estimate, 120)), sector) + rank(ts_mean(analyst_revision_rank_derivative, 126)), 12), industry)
```

### 3. `option_skew_norm_pcr_oi_360_historical_volatility_60_120_12_industry`

- Alpha id: `RR2Q8Ye1`
- Family: `option_positioning_or_volatility`
- Neutralization: `industry`
- Fingerprint: `585edf345b523aba01825c04d0a089e3`
- Status: `success` / simulation `COMPLETE`
- Sharpe: -0.43
- Fitness: -0.17
- Turnover: 0.1087
- Margin: -0.000358
- Drawdown: 0.1206
- Returns: -0.0195
- Failed checks: `LOW_SHARPE`, `LOW_FITNESS`, `CONCENTRATED_WEIGHT`,
  `LOW_SUB_UNIVERSE_SHARPE`
- Pending checks: `SELF_CORRELATION`
- Passing checks: `LOW_TURNOVER`, `HIGH_TURNOVER`, `MATCHES_COMPETITION`
- Hopeful: no
- Internal candidate: no
- Relation to E5: distinct; no close-volume correlation reversal pattern.
- Relation to failed lanes: not the sixth-batch failed forward-curve seed
  because it does not use `(forward_price_120 - forward_price_60) / close`.
  However, this specific PCR open-interest minus historical-volatility
  structure failed quality and robustness checks and should be penalized in
  future offline triage.
- Expression:

```text
group_neutralize(ts_decay_linear(group_zscore(rank(ts_rank(pcr_oi_360, 120)), sector) - group_zscore(rank(ts_rank(historical_volatility_60, 120)), sector), 12), industry)
```

## Candidate Decision

| Name | Alpha id | Hopeful | Internal candidate | Decision |
| --- | --- | --- | --- | --- |
| `balance_accrual_norm_cashflow_efficiency_rank_derivative_assets_cashflow_op_126_12_subindustry` | `JjgEOmgm` | no | no | stop this exact structure |
| `sales_revision_norm_sales_estimate_average_annual_lowest_sales_estimate_analyst_revision_rank_derivative_126_12_industry` | `O0bPZ9L7` | no | no | stop this exact structure |
| `option_skew_norm_pcr_oi_360_historical_volatility_60_120_12_industry` | `RR2Q8Ye1` | no | no | stop this exact structure |

## Next Step

No hopeful emerged, so stop the v2 shortlist lane and return to offline
generation/triage. The next offline update should penalize these exact simple
v2 top-3 forms without banning the broader accruals, estimate-revision, or
options families permanently.
