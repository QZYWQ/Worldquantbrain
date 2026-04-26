# 2026-04-26 pcr_oi_720 E-Stage Check

- Alpha id: `KPwW3LGN`
- Source alpha: `group_rank(ts_rank(signed_power(ts_rank(pcr_oi_720, 20), 2), 20) + ts_rank(anl4_af_eps_value / close, 60), industry)`
- Test Period readback: `PASS` — `test Sharpe 0.99`, `test Fitness 0.37`, `turnover 0.2699`
- Check Submission readback: `FAIL` — `LOW_FITNESS FAIL`, `CONCENTRATED_WEIGHT FAIL`, `SELF_CORRELATION PENDING`
- Other checks: `LOW_SHARPE PASS`, `LOW_TURNOVER PASS`, `HIGH_TURNOVER PASS`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `MATCHES_COMPETITION PASS`

## Causal Template

- causal_statement: `PCR pressure and analyst lag mean-revert price`
- mechanism_class: `information_delay`
- falsifier: `If analyst leg turns contemporaneous, edge dies`
- reverse_event_test: `Flip the analyst leg and recheck sign`

## Decision

- Verdict: `hold`
- Causal template: `PASS`
- Rationale: the test window stays above the E floor, but submission checks fail on fitness and concentration, so this line is not submit-ready.
- Budget: reclaim the remaining `0.5` from `pcr_oi_720` back to `cold_pool`.
