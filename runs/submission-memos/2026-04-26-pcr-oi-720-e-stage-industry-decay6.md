# 2026-04-26 pcr_oi_720 E-Stage Industry/Decay-6 Repair

## Scope

- Family: `pcr_oi_720`
- Probe alpha: `ZYWOgoMY`
- Objective: keep `LOW_SUB_UNIVERSE_SHARPE` green while pushing `LOW_FITNESS` upward

## Official Result

- Expression: `group_rank(ts_rank(signed_power(ts_zscore(ts_mean(pcr_oi_720, 7), 126), 2), 20) + ts_rank(anl4_af_eps_value / close, 60), industry)`
- Settings: `USA` / `TOP3000` / `delay=1` / `decay=6` / `neutralization=INDUSTRY` / `truncation=0.05` / `testPeriod=P1Y` / `pasteurization=ON` / `unitHandling=VERIFY`
- IS: `Sharpe 1.36 / Fitness 0.80 / Turnover 13.88% / Returns 5.12%`
- TEST: `Sharpe 1.24 / Fitness 0.60 / Turnover 13.50% / Returns 3.58%`
- Checks: `LOW_SHARPE PASS`, `LOW_FITNESS FAIL`, `CONCENTRATED_WEIGHT PASS`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`, `MATCHES_COMPETITION PASS`

## Decision

- Verdict: `hold`
- Reason: the extra smoothing and higher decay improved turnover and held `LOW_SUB_UNIVERSE_SHARPE` green, but `LOW_FITNESS` is still below the floor.
- S-1 trigger: not fired, because `LOW_SUB_UNIVERSE_SHARPE` stayed PASS.
- Budget: keep the lane on hold and wait for a genuinely new path before spending more budget.
