# Submission Live Log

- Timestamp: 2026-04-28 11:46 (Asia/Shanghai)
- Scope: live WQB browser workflow in progress; no submission has been confirmed yet
- WQB API: not used
- `agent-policies/`: not touched

## Live lanes tested in this session

### Simulation 2
- Expression: `ts_rank(anl4_af_eps_value / close, 60)`
- Status: results loaded, `Submit Alpha` still disabled
- IS Testing Status: `6 PASS / 1 FAIL / 1 PENDING`
- Aggregate Data: `Sharpe 0.90`, `Turnover 17.18%`, `Fitness 1.45`, `Returns 44.50%`, `Drawdown 70.03%`, `Margin 51.81‱`
- Conclusion: promising metrics but not submit-ready

### Simulation 3
- Expression: `ts_mean(pv13_revere_index_value, 63)`
- Status: results loaded, `Submit Alpha` still disabled
- Result label: `Needs Improvement`
- Aggregate Data: `Sharpe -0.12`, `Turnover 0.58%`, `Fitness -0.04`, `Returns -1.38%`, `Drawdown 43.43%`, `Margin -47.33‱`
- Conclusion: dead branch

### Simulation 4
- Expression: `group_rank(ts_sum(earnings_per_share_average/close, 60), industry)`
- Status: results loaded, `Submit Alpha` still disabled
- Result label: `Needs Improvement`
- Aggregate Data: `Sharpe 1.00`, `Turnover 1.55%`, `Fitness 0.88`, `Returns 9.77%`, `Drawdown 10.95%`, `Margin 125.90‱`
- Conclusion: interesting but still not submit-ready

### Simulation 5
- Expression: `group_rank(ts_rank(earnings_per_share_average/close, 120), pv13_revere_key_sector_total)`
- Status: failed/errored branch (red error indicator in tab)
- Conclusion: invalid `group_rank(..., pv13_revere_key_sector_total)` family; no more retries on this branch

### Simulation 6
- Created as a blank clean tab but not used for a new candidate yet
- Conclusion: available for the next family probe

## Current decision

- The current live-valid queue is exhausted for practical submission purposes.
- The best-performing lane so far is Simulation 2, but it still has one FAIL and one PENDING in testing status.
- Next step should be a new family probe rather than more polishing of the current queue.
