# 2026-05-23 Independent Economic Rebuild S0

- Mode: SIMULATION ONLY. No alpha was submitted.
- Objective: rebuild independent economic-logic candidates from non-inherited ideas.
- Candidates planned: 17
- Results recorded: 17

## Strategy

1. Exclude 2026-05-22 inherited-variation formulas and submitted families.
2. Test mechanism-level expressions, not cosmetic parameter neighbors.
3. Include sign controls for unclear balance-sheet directions.
4. Promote only if real metrics and official check evidence justify it.

## Results

| Rank | Alpha | Family | Posture | Score | Sharpe | Fitness | Turnover | SubU | Check | Expression |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | vRdgb3dA | operating_profitability | rebuild_or_rescue | 37.0 | 1.19 | 0.78 | 0.0498 | 0.92 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252), industry)` |
| 2 | N1A929Ag | operating_profitability | rebuild_or_rescue | 34.4 | 1.09 | 0.74 | 0.0506 | 0.75 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(operating_income,252), industry)` |
| 3 | LLkJQK16 | cashflow_surprise | rebuild_or_rescue | 32.98 | 1.06 | 0.67 | 0.0264 | 0.8 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(ts_mean(anl4_fs_actuals_advanced_qf_nd_fcf_value,63),252), industry)` |
| 4 | RRdWv8jo | operating_profitability | rebuild_or_rescue | 32.3 | 1.08 | 0.65 | 0.0485 | 0.66 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(divide(operating_income, add(abs(revenue), 1)),252), industry)` |
| 5 | E5kJng9r | cashflow_expectation | rebuild_or_rescue | 30.82 | 1.02 | 0.61 | 0.0183 | 0.65 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(ts_mean(free_cashflow_max,126),252), industry)` |
| 6 | kqQlpxX6 | cashflow_expectation | rebuild_or_rescue | 30.52 | 1.01 | 0.6 | 0.0227 | 0.65 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(ts_mean(free_cashflow_max,63),252), industry)` |
| 7 | 9qJ0NoKx | cashflow_surprise | rebuild_or_rescue | 28.88 | 0.98 | 0.56 | 0.0213 | 0.51 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(ts_mean(anl4_fs_detail_estimate_1qf_v4_nd_fcf_low,63),252), industry)` |
| 8 | 9qJ0nvXo | cashflow_surprise | kill_or_hold | 11.5 | 0.34 | 0.11 | 0.1816 | 0.11 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_zscore(anl4_fs_actuals_advanced_qf_nd_fcf_value,20) - ts_zscore(anl4_fs_detail_estimate_1qf_v4_nd_fcf_low,20), industry)` |
| 9 | d5dLN1bX | working_capital_quality | kill_or_hold | 8.34 | 0.27 | 0.07 | 0.047 | -0.29 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(divide(assets_curr, add(abs(revenue),1)),252), industry)` |
| 10 | kqQl6brz | fair_value_liability_pressure | kill_or_hold | 5.64 | 0.1 | 0.02 | 0.041 | -0.23 | NOT_CHECKED_METRIC_FILTER | `reverse(group_rank(ts_zscore(winsorize(ts_backfill(fn_liab_fair_val_l1_a,252), std=4),120), industry))` |
| 11 | j21mKjNk | fair_value_liability_pressure | kill_or_hold | 4.36 | -0.1 | -0.02 | 0.041 | 0.23 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_zscore(winsorize(ts_backfill(fn_liab_fair_val_l1_a,252), std=4),120), industry)` |
| 12 | xARgEpLl | operating_profitability | kill_or_hold | 3.52 | -0.12 | -0.02 | 0.1796 | 0.08 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_zscore(ts_delta(operating_income,252), 20), industry)` |
| 13 | xARgJpQq | working_capital_quality | kill_or_hold | 1.66 | -0.27 | -0.07 | 0.047 | 0.29 | NOT_CHECKED_METRIC_FILTER | `reverse(group_rank(ts_rank(divide(assets_curr, add(abs(revenue),1)),252), industry))` |
| 14 | RRdWO9An | cashflow_guidance | kill_or_hold | 1.22 | -0.19 | -0.07 | 0.016 | -0.06 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_delta(ts_mean(anl4_fs_guidances_advanced_af_nd_fcfps_maxguidance,20),63), industry)` |
| 15 | mLZ9nm01 | cashflow_guidance | kill_or_hold | -2.6 | -0.34 | -0.14 | 0.0309 | -0.25 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_zscore(ts_mean(anl4_fs_guidances_advanced_af_nd_fcfps_maxguidance,63),120), industry)` |
| 16 | 78J9rPKv | fair_value_liability_pressure | kill_or_hold | -11.12 | -0.7 | -0.34 | 0.0171 | -0.4 | NOT_CHECKED_METRIC_FILTER | `reverse(group_rank(ts_rank(divide(ts_backfill(fn_liab_fair_val_l1_a,252), add(abs(ts_backfill(assets_curr,252)),1)),252), industry))` |
| 17 | E5kJMlpm | fair_value_liability_pressure | kill_or_hold | -14.52 | -0.79 | -0.4 | 0.01 | -0.71 | NOT_CHECKED_METRIC_FILTER | `reverse(group_rank(ts_rank(ts_backfill(fn_liab_fair_val_l1_a,252),252), industry))` |

## Family Takeaways

- `cashflow_expectation` best `fcf-max-slow-rank-126`: Sharpe=1.02, Fitness=0.61, Turnover=0.0183, posture=rebuild_or_rescue.
- `cashflow_guidance` best `fcfps-guidance-change`: Sharpe=-0.19, Fitness=-0.07, Turnover=0.016, posture=kill_or_hold.
- `cashflow_surprise` best `fcf-actual-slow-rank`: Sharpe=1.06, Fitness=0.67, Turnover=0.0264, posture=rebuild_or_rescue.
- `fair_value_liability_pressure` best `fair-liability-zscore-negative`: Sharpe=0.1, Fitness=0.02, Turnover=0.041, posture=kill_or_hold.
- `operating_profitability` best `op-income-current-assets-ratio`: Sharpe=1.19, Fitness=0.78, Turnover=0.0498, posture=rebuild_or_rescue.
- `working_capital_quality` best `current-assets-revenue-ratio`: Sharpe=0.27, Fitness=0.07, Turnover=0.047, posture=kill_or_hold.

## Failed Or Error Records

- None.
