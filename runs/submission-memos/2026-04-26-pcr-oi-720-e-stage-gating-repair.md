# 2026-04-26 pcr_oi_720 E-Stage Gating Repair

## Scope

- Family: `pcr_oi_720`
- Baseline repair lane: `ZYWOgoMY`
- Objective: cut turnover enough to clear `LOW_FITNESS` without breaking `LOW_SUB_UNIVERSE_SHARPE`

## Structural Repair Attempts

- `trade_when(ts_std(log_return, 20) > 0.02, ...)`
  - Result: failed immediately because `ts_std` is not accessible on this account.
- `hump(group_rank(ts_rank(ts_zscore(ts_mean(pcr_oi_720, 7), 126), 20) + ts_rank(anl4_af_eps_value / close, 60), industry))`
  - Alpha: `leRoGzNn`
  - Result: IS `Sharpe -0.34 / Fitness -0.09`, TEST `Sharpe -1.17 / Fitness -0.51`.
  - Checks: `LOW_SHARPE FAIL`, `LOW_FITNESS FAIL`, `LOW_TURNOVER FAIL`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `CONCENTRATED_WEIGHT PASS`, `SELF_CORRELATION PENDING`.
  - Status: discard.
- `trade_when(ts_delta(close, 10) > 0, group_rank(ts_rank(ts_zscore(ts_mean(pcr_oi_720, 7), 126), 20) + ts_rank(anl4_af_eps_value / close, 60), industry), -1)`
  - Alpha: `3qn85MxQ`
  - Result: IS `Sharpe 0.87 / Fitness 0.44 / Turnover 0.1128`, TEST `Sharpe 1.23 / Fitness 0.69 / Turnover 0.1080`.
  - Checks: `LOW_SHARPE FAIL`, `LOW_FITNESS FAIL`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `CONCENTRATED_WEIGHT PASS`, `SELF_CORRELATION PENDING`.
  - Status: discard; the gate improved turnover, but IS Sharpe fell under the low-sharpe floor and the lane still does not clear the fitness gate.

## Decision

- Verdict: `hold`
- Reason: the trend gate materially improved the turnover/fitness trade-off, but it still did not clear `LOW_FITNESS`; the sub-universe check remained green, so there is no S-1 trigger.
- Budget: keep the lane on hold and wait for a genuinely new gating / normalization path or a new field family.

## Evidence

- `https://api.worldquantbrain.com/alphas/leRoGzNn`
- `https://api.worldquantbrain.com/alphas/3qn85MxQ`
- `runs/simulation-captures/2026-04-26-pcr-oi-720-e-stage-gating-repair-batch-01.json`
