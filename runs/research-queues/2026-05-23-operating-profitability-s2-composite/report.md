# 2026-05-23 Operating Profitability S2 Composite

- Mode: SIMULATION ONLY. No alpha was submitted.
- Goal: test whether subindustry peer grouping plus cash-flow confirmation lifts Fitness over 1.0.

| Rank | Alpha | Name | Posture | Score | Sharpe | Fitness | Turnover | SubU | Check | Expression |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | O0ovYJXg | subindustry-op-assets-rank126 | candidate_record_only | 80.76 | 1.74 | 1.12 | 0.0602 | 1.18 | 8/8 | `group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),126), subindustry)` |
| 2 | j21QzK9E | subindustry-op-assets-fcf-max-70-30 | candidate_record_only | 76.08 | 1.48 | 1.04 | 0.0367 | 1.15 | 8/8 | `group_rank(0.7 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252) + 0.3 * ts_rank(ts_mean(free_cashflow_max,126),252), subindustry)` |
| 3 | zqOzZojK | subindustry-op-assets-fcf-max-50-50 | near_candidate | 43.02 | 1.4 | 0.95 | 0.0342 | 1.03 | NOT_CHECKED_METRIC_FILTER | `group_rank(0.5 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252) + 0.5 * ts_rank(ts_mean(free_cashflow_max,126),252), subindustry)` |
| 4 | MPkAO1Go | subindustry-op-assets-fcf-actual-70-30 | near_candidate | 37.98 | 1.24 | 0.81 | 0.0399 | 0.88 | NOT_CHECKED_METRIC_FILTER | `group_rank(0.7 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252) + 0.3 * ts_rank(ts_mean(anl4_fs_actuals_advanced_qf_nd_fcf_value,63),252), subindustry)` |
| 5 | 58MVb8JM | subindustry-op-assets-fcf-actual-50-50 | near_candidate | 37.86 | 1.24 | 0.81 | 0.0397 | 0.85 | NOT_CHECKED_METRIC_FILTER | `group_rank(0.5 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252) + 0.5 * ts_rank(ts_mean(anl4_fs_actuals_advanced_qf_nd_fcf_value,63),252), subindustry)` |
| 6 | LLkxjlQ9 | subindustry-op-assets-rank504 | rebuild_or_hold | 32.86 | 1.09 | 0.65 | 0.0459 | 0.77 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),504), subindustry)` |
