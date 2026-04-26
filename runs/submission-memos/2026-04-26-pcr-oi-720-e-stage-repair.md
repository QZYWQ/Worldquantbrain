# 2026-04-26 pcr_oi_720 E-Stage Repair

## Scope

- Family: `pcr_oi_720`
- Baseline lane: `KPwW3LGN`
- Objective: repair `CONCENTRATED_WEIGHT` first, then lift `LOW_FITNESS`

## Repair Sweep

- `WjWvndwN`: `group_rank(ts_rank(signed_power(ts_rank(pcr_oi_720, 20), 2), 20) + ts_rank(rank(anl4_af_eps_value / close), 60), industry)` with truncation `0.08`
  - Outcome: concentration still failed and TEST degraded sharply; discard.
- `6XY53pWJ`: original analyst leg with truncation `0.05`
  - Outcome: concentration still failed; IS fitness remained below submit gate.
- `3qn8XVVX`: `group_rank(ts_rank(signed_power(ts_zscore(ts_mean(pcr_oi_720, 5), 126), 2), 20) + ts_rank(rank(anl4_af_eps_value / close), 60), industry)` with INDUSTRY neutralization and truncation `0.05`
  - IS: `Sharpe 1.35`, `Fitness 0.77`, `Turnover 0.1640`
  - TEST: `Sharpe 1.30`, `Fitness 0.66`
  - Checks: `LOW_SHARPE PASS`, `CONCENTRATED_WEIGHT PASS`, `LOW_FITNESS FAIL`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`
  - Status: current best repaired candidate; still not submit-ready.
- `E5r9V5d0`: `group_rank(ts_rank(signed_power(ts_zscore(ts_mean(pcr_oi_720, 10), 126), 2), 20) + ts_rank(rank(anl4_af_eps_value / close), 60), industry)` with `decay=8`
  - IS: `Sharpe 1.10`, `Fitness 0.59`, `Turnover 0.1222`
  - TEST: `Sharpe -0.24`, `Fitness -0.05`
  - Checks: `LOW_SHARPE FAIL`, `CONCENTRATED_WEIGHT PASS`, `LOW_FITNESS FAIL`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`
  - Status: over-smoothed; turnover improved, but TEST Sharpe collapsed.
- `npOLAKpl`: `group_rank(ts_rank(signed_power(ts_zscore(ts_mean(pcr_oi_720, 7), 126), 2), 20) + ts_rank(rank(anl4_af_eps_value / close), 60), industry)` with `decay=6`
  - IS: `Sharpe 1.24`, `Fitness 0.68`, `Turnover 0.1401`
  - TEST: `Sharpe -0.15`, `Fitness -0.02`
  - Checks: `LOW_SHARPE FAIL`, `CONCENTRATED_WEIGHT PASS`, `LOW_FITNESS FAIL`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`
  - Status: milder smoothing preserved more IS strength than `E5r9V5d0`, but still failed LOW_FITNESS and flipped TEST Sharpe negative.

## Decision

- Verdict: `hold`
- Reason: smoothing the pcr leg reduced turnover, but the stronger variants broke TEST Sharpe and the milder variant still failed LOW_FITNESS. `LOW_SUB_UNIVERSE_SHARPE` stayed PASS throughout, so there is no S-1 trigger yet.
- Budget: keep the family on hold; do not submit, and do not allocate more of the reclaimed cold-pool budget until a genuinely new path appears.
