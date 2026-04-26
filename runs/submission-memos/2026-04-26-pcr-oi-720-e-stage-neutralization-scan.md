# 2026-04-26 pcr_oi_720 E-Stage Neutralization Scan

## Scope

- Family: `pcr_oi_720`
- Goal: test whether the repaired E-stage lane improves when neutralization moves from Industry to Subindustry.

## Official Result

- Alpha id: `LLl0X852`
- Expression: `group_rank(ts_rank(signed_power(ts_zscore(ts_mean(pcr_oi_720, 5), 126), 2), 20) + ts_rank(anl4_af_eps_value / close, 60), industry)`
- Settings: `USA` / `TOP3000` / `delay=1` / `decay=4` / `neutralization=SUBINDUSTRY` / `truncation=0.05` / `testPeriod=P1Y` / `pasteurization=ON` / `unitHandling=VERIFY`
- IS: `Sharpe 1.22 / Fitness 0.62 / Turnover 17.03% / Returns 4.39%`
- TEST: `Sharpe 1.13 / Fitness 0.51 / Turnover 16.43% / Returns 3.38%`
- Checks: `LOW_SHARPE FAIL`, `LOW_FITNESS FAIL`, `CONCENTRATED_WEIGHT PASS`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`, `MATCHES_COMPETITION PASS`

## Decision

- Verdict: `hold`
- Reason: Subindustry neutralization did not rescue Fitness and also weakened Sharpe versus `3qn8XVVX`.
- Best held candidate remains `3qn8XVVX`.
- No S-1 trigger is warranted because `LOW_SUB_UNIVERSE_SHARPE` stayed green.
