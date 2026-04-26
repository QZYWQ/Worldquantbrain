# 2026-04-24 Sales Acceleration Live Blocked

## Decision

- Keep `sales_acceleration` as the next family to spend budget on once live official BRAIN access is available.
- Do not reopen the frozen EPS-close, cashflow/cap, capex, or operating-income lines.
- Treat the current registry survivors as closed unless a new official page/API read changes the problem.

## Why This Is Still The Best Next Family

- `analyst_disagreement_dts_spe_industry` was rechecked live and failed on IS plus sub-universe.
- `event_option_volume_gate` was killed after the first dead batch and a materially different local-factory follow-up.
- `operating_income_history_position` still produces unit warnings and weak holdout, so it is a backup at best.
- `sales_acceleration` is the only remaining branch that is both structurally different and still simple enough for a cheap first-pass control test.

## Next Minimal Experiment

- Baseline:
  `group_rank(ts_delta(ts_delta(revenue, 63), 63), industry)`
- Immediate control:
  `group_rank(ts_delta(revenue, 63), industry)`

## Live Status In This Session

- I could not attach the Chrome DevTools MCP session to the already-running browser profile.
- Computer Use access to the Chrome app was denied by the environment.
- Because of that, no fresh official simulation was launched in this session.
- No new `runs/simulation-captures/` artifact was written for `sales_acceleration`.

## Official Evidence Used

- `runs/submission-memos/2026-04-24-next-step-family-stop.md`
- `runs/submission-memos/2026-04-24-sales-acceleration-branch.md`
- `runs/submission-memos/2026-04-24-operating-income-history-position-batch-05.json`
- `runs/submission-memos/2026-04-24-analyst-disagreement-live-recheck.md`
- `runs/submission-memos/2026-04-24-live-unsubmitted-triage.md`

## Next Trigger

- Run the baseline/control pair as the first live batch when browser/API access is available.
- If the second-difference baseline does not beat the first-difference control, kill the family quickly and transfer the next research hour to a truly new information source.
