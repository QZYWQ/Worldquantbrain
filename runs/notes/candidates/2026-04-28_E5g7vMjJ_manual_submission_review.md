# Manual Submission Review: E5g7vMjJ

- date: 2026-04-28 19:37:16 CST
- alpha id: E5g7vMjJ
- source family: kq17QGe8 corr-window interpolation family
- expression: `group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 5), subindustry)`
- fingerprint: f972f609f569c27be374678af9345ec4

## Latest Metrics

- Sharpe: 1.37
- Fitness: 1.01
- Turnover: 0.175
- Margin: 0.001088
- Drawdown: 0.0737
- Returns: 0.0952
- Alpha status: UNSUBMITTED
- Grade: AVERAGE

## Latest Platform Checks

- LOW_SHARPE: PASS, value 1.37 / limit 1.25
- LOW_FITNESS: PASS, value 1.01 / limit 1.0
- LOW_TURNOVER: PASS, value 0.175 / limit 0.01
- HIGH_TURNOVER: PASS, value 0.175 / limit 0.7
- CONCENTRATED_WEIGHT: PASS
- LOW_SUB_UNIVERSE_SHARPE: PASS, value 0.59 / limit 0.59
- SELF_CORRELATION: PASS from `/alphas/E5g7vMjJ/check`, value 0.6804 / limit 0.7
- MATCHES_COMPETITION: PASS

## Endpoint Evidence

- alpha detail endpoint: HTTP 200, alpha detail still shows SELF_CORRELATION=PENDING
- `/alphas/E5g7vMjJ/check`: HTTP 200, populated checks, SELF_CORRELATION=PASS with value 0.6804 / limit 0.7
- `/alphas/E5g7vMjJ/correlations/self`: HTTP 200, populated correlation records, min 0.4381, max 0.6804, records 3

## Comparison vs V2 / kq17QGe8

- V2 Sharpe: 1.32
- E5g7vMjJ Sharpe: 1.37
- V2 Fitness: 0.94
- E5g7vMjJ Fitness: 1.01
- Both turnover values are below 0.3.

## Why E5g7vMjJ Became The Lead

E5g7vMjJ improved both Sharpe and Fitness versus V2 while keeping turnover controlled. The corr70 interpolation preserved more Sharpe and Fitness than the corr90 branch while also clearing the visible LOW_SUB_UNIVERSE_SHARPE check.

## Risk Notes

- LOW_SUB_UNIVERSE_SHARPE was previously exactly at 0.59 / 0.59, so this is close to the boundary.
- Grade was AVERAGE at re-check time.
- Alpha detail still lagged with SELF_CORRELATION=PENDING even though `/check` returned SELF_CORRELATION=PASS.
- Manual review is still required before submission.

## Recommendation

Ready for manual submission review.

Automated submission was not performed.
