# Manual Submission Record: E5g7vMjJ

- recorded at: 2026-04-28 19:52:15 CST
- alpha id: E5g7vMjJ
- submitted by: manual WorldQuant BRAIN UI action
- automated submission performed: no
- source family: kq17QGe8 corr-window interpolation family
- expression: `group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 5), subindustry)`
- fingerprint: f972f609f569c27be374678af9345ec4

## Pre-submit Snapshot

- Sharpe: 1.37
- Fitness: 1.01
- Turnover: 0.175
- Margin: 0.001088
- Drawdown: 0.0737
- Returns: 0.0952
- LOW_SHARPE: PASS
- LOW_FITNESS: PASS
- LOW_TURNOVER: PASS
- HIGH_TURNOVER: PASS
- CONCENTRATED_WEIGHT: PASS
- LOW_SUB_UNIVERSE_SHARPE: PASS, value 0.59 / limit 0.59
- SELF_CORRELATION: PASS, value 0.6804 / limit 0.7 from `/alphas/E5g7vMjJ/check`
- MATCHES_COMPETITION: PASS

## Post-submit Platform Fetch

- alpha detail HTTP status: 200
- latest alpha status: ACTIVE
- latest stage: OS
- latest grade: AVERAGE
- date submitted: 2026-04-28T07:50:15-04:00
- date modified: 2026-04-28T07:50:09-04:00
- `/alphas/E5g7vMjJ/check`: HTTP 200, populated checks, SELF_CORRELATION=PASS
- `/alphas/E5g7vMjJ/correlations/self`: HTTP 200, empty payload after submission

## Decision

The alpha has been manually submitted in the BRAIN UI. No automated submission was performed by the local tooling.
