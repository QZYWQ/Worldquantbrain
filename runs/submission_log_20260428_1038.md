# Submission Live Log

- Timestamp: 2026-04-28 10:38 (Asia/Shanghai)
- Scope: live WQB browser workflow in progress; no submission has been confirmed yet
- WQB API: not used
- `agent-policies/`: not touched

## Current lane under test

- Candidate: `gen001-8c5bbca421a8`
- Expression: `group_rank(ts_sum(earnings_per_share_average/close, 60), industry)`
- Current settings at simulate time:
  - Region: USA
  - Universe: TOP3000
  - Delay: 1
  - Neutralization: Industry
  - Decay: 0
  - Truncation: 0.08
  - Pasteurization: On
  - Unit handling: Verify
  - Nan handling: Off
  - Test period: 1 year 0 months

## Observed live UI state

- Simulation is still running in the official `platform.worldquantbrain.com/simulate` page.
- Progress bar is currently at 35%.
- The platform TIP currently recommends using `trade_when` or `hump` operators to reduce turnover.
- `Check Submission` and `Submit Alpha` remain disabled while the simulation is in progress.

## Prior lane notes

- The same browser session already tested:
  - `ts_rank(anl4_af_eps_value / close, 60)`
  - `ts_mean(pv13_revere_index_value, 63)`
- Those earlier lanes were not the final live lane now under test.

## Next action

- Wait for the current simulation to complete, then re-evaluate whether the alpha becomes submission-ready.
- If the live status still blocks submission, move on to the next family rather than polishing indefinitely.
