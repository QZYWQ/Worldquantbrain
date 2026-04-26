# 2026-04-25 Call Breakeven Live Re-check

- Re-check time: `2026-04-25 01:28:13 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN Data Explorer and alpha API from the logged-in browser session
- Scope: `call_breakeven_60`

## Decision

- Keep `call_breakeven_60` alive.
- Keep `mLxN1mlX` as the active main.
- Do not reopen the frozen EPS-close, cashflow/cap, or operating-income lanes.
- Do not kill the call breakeven family yet; it still has genuine headroom, but the current bottlenecks are now Sharpe recovery, fitness, and concentration.

## Official Evidence

- Data Explorer `option9` shows `call_breakeven_60` with `70%` coverage, `100%` date coverage, and `542` visible alphas.
- `mLxN1mlX`
  - Expression: `group_rank(ts_rank(call_breakeven_60 / close, 20), industry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - IS summary: `Sharpe 1.44 / Fitness 0.62 / Turnover 38.88% / Returns 7.14%`
  - Test summary: `Sharpe 2.18 / Fitness 0.89`
  - Checks: `LOW_SHARPE=PASS`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`
- `O05jg5Og`
  - Simulation id: `1QFKrP7dv4OVcaGzfc1Aa1b`
  - Expression: `group_rank(ts_rank(call_breakeven_60 / close, 60), industry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - IS summary: `Sharpe 1.34 / Fitness 0.66 / Turnover 30.03% / Returns 7.21%`
  - Test summary: `Sharpe 1.77 / Fitness 0.77`
  - Checks: `LOW_SHARPE=PASS`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- `zqJEG2z8`
  - Expression: `group_rank(call_breakeven_60 / close, industry)`
  - IS summary: `Sharpe 0.37 / Fitness 0.21 / Turnover 18.24%`
  - This is the direct control and is much weaker than the ts-rank variants.
- `6XYQ2955`
  - Simulation id: `3Lr15J5jR5j8cwJN9qoHrMH`
  - Expression: `group_rank(ts_rank(ts_mean(call_breakeven_60 / close, 5), 20), industry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - IS summary: `Sharpe 1.04 / Fitness 0.43 / Turnover 26.39% / Returns 4.53%`
  - Test summary: `Sharpe 1.15 / Fitness 0.41`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- `LLlw2roL`
  - Simulation id: `Fy44L6XD4ns97aXWIbBcSb`
  - Expression: `group_rank(ts_rank(ts_mean(call_breakeven_60 / close, 3), 20), industry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - IS summary: `Sharpe 1.22 / Fitness 0.52 / Turnover 30.86% / Returns 5.58%`
  - Test summary: `Sharpe 1.30 / Fitness 0.46`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`
- `2rnxxJA8`
  - Simulation id: `17Jw9Z7Hj50nb2CoxzjKek`
  - Expression: `group_rank(ts_rank(ts_mean(call_breakeven_60 / close, 2), 20), subindustry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - IS summary: `Sharpe 1.36 / Fitness 0.58 / Turnover 33.96% / Returns 6.14%`
  - Test summary: `Sharpe 1.71 / Fitness 0.65`
  - Checks: `LOW_SHARPE=PASS`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`, `SELF_CORRELATION=PENDING`

## Why This Is the Right Direction

- This is a genuinely different information source from the frozen EPS-close and cashflow/cap families.
- The family is not dead: the best line still clears the main Sharpe floor and produces strong test behavior.
- The problem is now structural, not a basic viability problem.
- The latest smoothing repairs proved that concentration is fixable, and the 2-day subindustry mean is now the closest repair so far.

## Next Minimal Experiment

- Keep the decay-axis follow-up running: `nL3JAa64wxbRGHWA1MmGG`.
- If the decay variant cannot close the low-sub-universe gap, the branch should be very close to a freeze decision.
- Do not widen the tenor sweep yet.

## Status

- Current family: `continue`
- Current main: `mLxN1mlX`
- Backup: `O05jg5Og`
- Latest repair probe: `2rnxxJA8` is the closest completed repair so far
- Pending probe: `nL3JAa64wxbRGHWA1MmGG` tests a lighter decay-axis repair
