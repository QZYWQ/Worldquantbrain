# 2026-05-23 Operating Profitability S1 Rescue

- Mode: SIMULATION ONLY. No alpha was submitted.
- Parent: `vRdgb3dA` / `group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252), industry)`.
- Goal: lift near-candidate operating-efficiency signal without converting it into operator soup.

| Rank | Alpha | Name | Posture | Score | Sharpe | Fitness | Turnover | SubU | Check | Expression |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | LLkxPd82 | op-assets-subindustry-group | near_candidate | 41.02 | 1.36 | 0.85 | 0.0516 | 1.1 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252), subindustry)` |
| 2 | P0vEQaQM | op-assets-composite-fcf-max | near_candidate | 39.14 | 1.25 | 0.89 | 0.0326 | 0.78 | NOT_CHECKED_METRIC_FILTER | `group_rank(0.7 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252) + 0.3 * ts_rank(ts_mean(free_cashflow_max,126),252), industry)` |
| 3 | vRdVR6Ar | op-assets-composite-actual-fcf | near_candidate | 37.26 | 1.19 | 0.83 | 0.0349 | 0.76 | NOT_CHECKED_METRIC_FILTER | `group_rank(0.7 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252) + 0.3 * ts_rank(ts_mean(anl4_fs_actuals_advanced_qf_nd_fcf_value,63),252), industry)` |
| 4 | rKAm1Zq3 | op-assets-decay3 | rebuild_or_hold | 35.04 | 1.13 | 0.72 | 0.045 | 0.88 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252), industry)` |
| 5 | qMgZMPQO | op-assets-smoothed-fundamentals | rebuild_or_hold | 27.26 | 0.85 | 0.49 | 0.0355 | 0.81 | NOT_CHECKED_METRIC_FILTER | `group_rank(ts_rank(divide(ts_mean(operating_income,63), add(abs(ts_mean(assets_curr,63)), 1)),252), industry)` |
| 6 | QPEdZ5oQ | op-assets-negative-control | kill_or_hold | -27.0 | -1.19 | -0.78 | 0.0498 | -0.92 | NOT_CHECKED_METRIC_FILTER | `reverse(group_rank(ts_rank(divide(operating_income, add(abs(assets_curr), 1)),252), industry))` |

## Takeaway

- Best result: `op-assets-subindustry-group` Sharpe=1.36, Fitness=0.85, Turnover=0.0516, posture=near_candidate.
