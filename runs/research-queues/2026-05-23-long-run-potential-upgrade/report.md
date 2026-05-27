# 2026-05-23 Long-Run Potential Upgrade

- Mode: SIMULATION ONLY. No alpha was submitted.
- Source: interrupted 24h operating-profitability run.
- Source candidates live-checked: 23
- Upgrade simulations recorded: 13

## Upgrade Results

| Rank | Alpha | Parent | Posture | Score | Sharpe | Fitness | Turnover | SubU | SelfCorr | Check | Name | Expression |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| 1 | qMgbqzPV | N1Aoapdo/3qzWJ95O | hard_8pass_record_only | 75.01 | 1.6 | 1.12 | 0.0411 | 1.19 | 0.5137 | 8/8 | op126-fcfmax-70-30 | `group_rank(0.7 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),126) + 0.3 * ts_rank(ts_mean(free_cashflow_max,126),252), subindustry)` |
| 2 | np30b6rw | A1kdL3gX/9qJQPNXV | hard_8pass_record_only | 74.08 | 1.53 | 1.05 | 0.0347 | 1.4 | 0.4727 | 8/8 | smooth63-r63-fcfmax-85-15 | `group_rank(0.85 * ts_rank(divide(ts_mean(operating_income,63), add(abs(ts_mean(assets_curr,63)), 1)),63) + 0.15 * ts_rank(ts_mean(free_cashflow_max,126),252), subindustry)` |
| 3 | A1k6KQQd | N1Aoapdo/3qzWJ95O | hard_8pass_record_only | 73.77 | 1.56 | 1.08 | 0.0398 | 1.13 | 0.4882 | 8/8 | op126-fcfmax-60-40 | `group_rank(0.6 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),126) + 0.4 * ts_rank(ts_mean(free_cashflow_max,126),252), subindustry)` |
| 4 | kqQRRQ2k | A1kdL3gX/9qJQPNXV | hard_8pass_record_only | 73.18 | 1.53 | 1.04 | 0.0361 | 1.21 | 0.4675 | 8/8 | smooth63-r63-fcflow-90-10 | `group_rank(0.9 * ts_rank(divide(ts_mean(operating_income,63), add(abs(ts_mean(assets_curr,63)), 1)),63) + 0.1 * ts_rank(ts_mean(anl4_fs_detail_estimate_1qf_v4_nd_fcf_low,63),252), subindustry)` |
| 5 | mLZOOpK9 | YPQdleoo/omVeAnZb | hard_8pass_record_only | 72.07 | 1.48 | 1.0 | 0.0331 | 1.28 | 0.476 | 8/8 | smooth63-r84-fcfmax-85-15 | `group_rank(0.85 * ts_rank(divide(ts_mean(operating_income,63), add(abs(ts_mean(assets_curr,63)), 1)),84) + 0.15 * ts_rank(ts_mean(free_cashflow_max,126),252), subindustry)` |
| 6 | e7LAJmdN | N1Aoapdo/3qzWJ95O | hard_8pass_record_only | 71.66 | 1.54 | 1.04 | 0.0435 | 0.91 | 0.5229 | 8/8 | op126-fcflow-85-15 | `group_rank(0.85 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),126) + 0.15 * ts_rank(ts_mean(anl4_fs_detail_estimate_1qf_v4_nd_fcf_low,63),252), subindustry)` |
| 7 | kqQR51bd | N1Aoapdo/3qzWJ95O | near_pass_fitness_rescue | 41.08 | 1.58 | 0.98 | 0.0585 | 1.12 | None | 6/8 | op126-margin-75-25 | `group_rank(0.75 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),126) + 0.25 * ts_rank(divide(operating_income, add(abs(revenue), 1)),126), subindustry)` |
| 8 | LLkebZne | 78JVlV6L/9qJQanJ1 | near_pass_fitness_rescue | 40.02 | 1.47 | 0.99 | 0.0375 | 1.14 | None | 6/8 | margin-s63-r84-op168-fcfmax | `group_rank(0.5 * ts_rank(divide(ts_mean(operating_income,63), add(abs(ts_mean(revenue,63)), 1)),84) + 0.3 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),168) + 0.2 * ts_rank(ts_mean(free_cashflow_max,126),252), subindustry)` |
| 9 | QPEemdYw | P0vE8GZL/qMgZPd12 | near_pass_fitness_rescue | 37.22 | 1.4 | 0.91 | 0.0493 | 1.01 | None | 6/8 | margin-s63-r378-op168-50-50 | `group_rank(0.5 * ts_rank(divide(ts_mean(operating_income,63), add(abs(ts_mean(revenue,63)), 1)),378) + 0.5 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),168), subindustry)` |
| 10 | E5k3oRNK | MPkAz8Ko/58MVqNp5 | research_hold | 35.3 | 1.35 | 0.81 | 0.0528 | 1.13 | None | 6/8 | margin-s63-r126-op168-50-50 | `group_rank(0.5 * ts_rank(divide(ts_mean(operating_income,63), add(abs(ts_mean(revenue,63)), 1)),126) + 0.5 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),168), subindustry)` |
| 11 | gJxvqYoQ | 2rJkN9X5 | research_hold | 34.36 | 1.35 | 0.78 | 0.0555 | 1.03 | None | 6/8 | margin-raw-r126-op168-50-50 | `group_rank(0.5 * ts_rank(divide(operating_income, add(abs(revenue), 1)),126) + 0.5 * ts_rank(divide(operating_income, add(abs(assets_curr), 1)),168), subindustry)` |
| 12 | Xg1qqxXl | P0vE8GZL/qMgZPd12 | research_hold | 33.16 | 1.24 | 0.8 | 0.0255 | 0.97 | None | 5/8 | margin-s63-r378-fcfmax-70-30 | `group_rank(0.7 * ts_rank(divide(ts_mean(operating_income,63), add(abs(ts_mean(revenue,63)), 1)),378) + 0.3 * ts_rank(ts_mean(free_cashflow_max,126),252), subindustry)` |
| 13 | RRdXZ2Nn | P0vE8GZL/qMgZPd12 | kill_or_hold | 30.2 | 1.16 | 0.72 | 0.0262 | 0.83 | None | NOT_CHECKED_METRIC_FILTER | margin-s63-r378-fcflow-85-15 | `group_rank(0.85 * ts_rank(divide(ts_mean(operating_income,63), add(abs(ts_mean(revenue,63)), 1)),378) + 0.15 * ts_rank(ts_mean(anl4_fs_detail_estimate_1qf_v4_nd_fcf_low,63),252), subindustry)` |

## Live-Checked Source Candidates

| Rank | Alpha | Posture | Sharpe | Fitness | Turnover | Check | SelfCorr | Dominant Block | Name |
| ---: | --- | --- | ---: | ---: | ---: | --- | ---: | --- | --- |
| 1 | N1Aoapdo | metric_pass_check_failed_or_pending | 1.76 | 1.15 | 0.0598 | 7/8 | 0.9872 | SELF_CORRELATION | op_assets_raw-rank126-subindustry-industry-d0 |
| 2 | 3qzWJ95O | metric_pass_check_failed_or_pending | 1.73 | 1.11 | 0.0568 | 7/8 | 0.9963 | SELF_CORRELATION | op_assets_raw-rank126-subindustry-decay3 |
| 3 | LLkxnXjM | metric_pass_check_failed_or_pending | 1.62 | 1.1 | 0.0586 | 7/8 | 0.9213 | SELF_CORRELATION | op_assets_raw-rank126-industry-industry-d0 |
| 4 | A1kdL3gX | metric_pass_check_failed_or_pending | 1.61 | 1.03 | 0.0516 | 7/8 | 0.8732 | SELF_CORRELATION | op_assets_s63-rank63-subindustry-industry-d0 |
| 5 | YPQdleoo | metric_pass_check_failed_or_pending | 1.58 | 1.02 | 0.0483 | 7/8 | 0.8632 | SELF_CORRELATION | op_assets_s63-rank84-subindustry-industry-d0 |
| 6 | 9qJQPNXV | near_candidate | 1.58 | 0.99 | 0.0528 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_s63-rank63-subindustry-subindustry-d0 |
| 7 | omVeAnZb | near_candidate | 1.54 | 0.97 | 0.0494 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_s63-rank84-subindustry-subindustry-d0 |
| 8 | kqQ5oOng | near_candidate | 1.52 | 0.96 | 0.0564 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_raw-rank168-subindustry-industry-d0 |
| 9 | LLkxkEem | near_candidate | 1.51 | 0.94 | 0.0659 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_raw-rank84-industry-industry-d0 |
| 10 | RRdLd1Qb | near_candidate | 1.52 | 0.93 | 0.0711 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_raw-rank63-industry-industry-d0 |
| 11 | KPkRjvGp | near_candidate | 1.5 | 0.93 | 0.0568 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_raw-rank168-subindustry-subindustry-d0 |
| 12 | P0vE8GZL | near_candidate | 1.42 | 0.93 | 0.036 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_margin_s63-rank378-subindustry-industry-d0 |
| 13 | O0ovgLj7 | near_candidate | 1.48 | 0.92 | 0.0536 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_raw-rank168-subindustry-decay3 |
| 14 | 2rJkmd1b | near_candidate | 1.39 | 0.89 | 0.0514 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_raw-rank252-subindustry-industry-d0 |
| 15 | qMgZPd12 | near_candidate | 1.38 | 0.88 | 0.036 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_margin_s63-rank378-subindustry-subindustry-d0 |
| 16 | vRdVvaQG | near_candidate | 1.36 | 0.86 | 0.0478 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_s63-rank63-industry-industry-d0 |
| 17 | YPQdN8L6 | near_candidate | 1.32 | 0.86 | 0.055 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_raw-rank168-industry-industry-d0 |
| 18 | MPkAz8Ko | near_candidate | 1.41 | 0.84 | 0.045 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_margin_s63-rank126-subindustry-industry-d0 |
| 19 | 78JVlV6L | near_candidate | 1.42 | 0.83 | 0.0503 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_margin_s63-rank84-subindustry-industry-d0 |
| 20 | P0vEbr5J | near_candidate | 1.32 | 0.82 | 0.0486 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_raw-rank252-subindustry-decay3 |
| 21 | 2rJkN9X5 | near_candidate | 1.35 | 0.81 | 0.0581 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_margin_raw-rank126-industry-industry-d0 |
| 22 | 9qJQdbLx | near_candidate | 1.3 | 0.8 | 0.0462 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_margin_raw-rank378-subindustry-industry-d0 |
| 23 | A1kdvORl | near_candidate | 1.28 | 0.8 | 0.0477 | 6/8 | None | LOW_FITNESS,SELF_CORRELATION | op_assets_raw-rank378-subindustry-industry-d0 |
