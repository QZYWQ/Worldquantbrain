# Learning Loop: pv13 D/E Stage Hold

## What We Tested
- Rechecked the lead pv13 relationship field at the D stage:
  - `pv13_ustomergraphrank_page_rank`
- Ran the main E-stage lane with two targeted rescue variants:
  - baseline `ts_rank(pv13_ustomergraphrank_page_rank, 150)`
  - longer-window repair `ts_rank(pv13_ustomergraphrank_page_rank, 180)`
  - industry-wrapped repair `group_rank(ts_rank(pv13_ustomergraphrank_page_rank, 180), industry)`
- Checked the secondary competitor lane:
  - `ts_rank(pv13_com_page_rank, 150)`

## What Happened
- D-stage platform availability was clean: the field is present, delay-1, Matrix typed, and reachable in Data Explorer.
- The baseline main candidate reached TEST Sharpe `1.01` and Fitness `1.77`, but the submission gate still failed on `LOW_SHARPE` and `LOW_SUB_UNIVERSE_SHARPE`.
- Repair 1 improved the main lane a little:
  - TEST Sharpe `1.03`
  - Fitness `1.82`
  - still failed `LOW_SHARPE`.
- Repair 2 improved turnover and fixed the sub-universe gate, but the core Sharpe gate still failed.
- The secondary competitor lane stayed weaker and did not justify rescue budget.

## What We Learned
- The binding barrier is not field availability; it is the Sharpe floor on the official check path.
- Longer smoothing helped a bit, but not enough to clear the gate.
- Industry wrapping can clean up the sub-universe problem, yet it does not solve the core Sharpe deficiency for this lane.
- The customer-centrality anchor is useful for exploratory research, but it is not submit-ready inside this bounded family.

## Next Move
- Keep the pv13 family in `incubate`.
- Do not spend more rescue budget on same-family polishing for this lane.
- If pv13 is revisited, use a genuinely new mechanism rather than more window or group wrappers around the same rank signal.
