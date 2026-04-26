# 2026-04-26 pcr_oi_720 E-Stage Sector Scan

## Scope

- Family: `pcr_oi_720`
- Goal: compare Sector neutralization against the already-repaired Industry baseline.

## Official Result

- Alpha id: `VkYANndb`
- Expression: `group_rank(ts_rank(signed_power(ts_zscore(ts_mean(pcr_oi_720, 5), 126), 2), 20) + ts_rank(anl4_af_eps_value / close, 60), industry)`
- Settings: `USA` / `TOP3000` / `delay=1` / `decay=4` / `neutralization=SECTOR` / `truncation=0.05` / `testPeriod=P1Y` / `pasteurization=ON` / `unitHandling=VERIFY`
- IS: `Sharpe 1.35 / Fitness 0.77 / Turnover 16.39% / Returns 5.28%`
- TEST: `Sharpe 1.30 / Fitness 0.66 / Turnover 15.94% / Returns 4.10%`
- Checks: `LOW_SHARPE PASS`, `LOW_FITNESS FAIL`, `CONCENTRATED_WEIGHT PASS`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`, `MATCHES_COMPETITION PASS`

## Decision

- Verdict: `hold`
- Reason: Sector neutralization matched the Industry baseline almost exactly and did not improve Fitness.
- Best held candidate remains `3qn8XVVX`.
- No S-1 trigger is warranted because `LOW_SUB_UNIVERSE_SHARPE` stayed green.
