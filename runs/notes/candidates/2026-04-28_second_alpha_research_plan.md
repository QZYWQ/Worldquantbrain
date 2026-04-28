# Second Alpha Research Plan

- Date: 2026-04-28 19:59:18 CST

## First Submitted Alpha Baseline

- Alpha id: E5g7vMjJ
- Expression: `group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 5), subindustry)`
- Fingerprint: f972f609f569c27be374678af9345ec4
- Status: ACTIVE
- Stage: OS
- Grade: AVERAGE
- Date submitted: 2026-04-28T07:50:15-04:00
- Sharpe: 1.37
- Fitness: 1.01
- Turnover: 0.175
- Margin: 0.001088
- Drawdown: 0.0737
- Returns: 0.0952
- Latest alpha detail checks: LOW_SHARPE=PASS, LOW_FITNESS=PASS, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=PASS, MATCHES_COMPETITION=PASS
- Latest `/alphas/E5g7vMjJ/check`: HTTP 200, ALREADY_SUBMITTED=FAIL

## Research Goal

Find a second alpha that is not just a local neighbor of E5g7vMjJ.

## Avoided Structures

- close-volume corr70 reversal
- direct corr60/70/80/90 variants
- decay-only variants of E5g7vMjJ
- same `ts_delta(close, 10)` plus ranked close-volume correlation structure

## Candidate Families

- price mean reversion with volatility/range conditioning
- liquidity/volume surprise without direct close-volume corr
- stability/risk-conditioned reversal

## Batch Size

- Maximum 3 generated alpha simulations.

## Decision Rule

- Hopeful if Fitness > 0.5.
- Internal candidate if Fitness > 0.8, Sharpe > 1.25, Returns > 0, and Margin > 0.

## Next Step

Run one small feedback-aware generation batch, then evaluate.

## First Small Batch Results

Batch source: `results/batch_second_alpha_1777378050.json`

### Candidate 1

- Alpha expression: `group_neutralize(ts_decay_linear(-rank(ts_delta(vwap, 20)) * rank(ts_zscore(volume / ts_mean(volume, 60), 20)) * (1 - rank(ts_std_dev(returns, 20))), 10), subindustry)`
- Fingerprint: 3ad788e9c334b0e24742015f3f65f8c5
- Alpha id: MPKWeelM
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Stage: IS
- Grade: INFERIOR
- Sharpe: 0.17
- Fitness: 0.06
- Turnover: 0.1857
- Margin: 0.000232
- Drawdown: 0.4587
- Returns: 0.0215
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=PASS, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ family: distinct
- Decision: discard

### Candidate 2

- Alpha expression: `group_neutralize(ts_decay_linear(-rank(ts_delta(close, 40)) * rank(ts_mean((high - low) / close, 20)) * rank(adv20 / volume), 12), subindustry)`
- Fingerprint: d878e62e796a77abe4793a8df33e43d0
- Alpha id: xAP62WGJ
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Stage: IS
- Grade: INFERIOR
- Sharpe: 0.64
- Fitness: 0.44
- Turnover: 0.145
- Margin: 0.000951
- Drawdown: 0.3004
- Returns: 0.069
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=PASS, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ family: distinct
- Decision: archive only; no manual variants because Fitness is below the hopeful threshold

### Candidate 3

- Alpha expression: `group_neutralize(ts_decay_linear(-rank(ts_sum(returns,20)) * rank(1 / (ts_std_dev(returns,60) + 0.001)) * rank(1 / (ts_mean((high - low) / close,20) + 0.001)), 10), subindustry)`
- Fingerprint: d388d69ce4231858d9cfa28f58122db7
- Alpha id: xAP6G6vg
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Stage: IS
- Grade: INFERIOR
- Sharpe: 0.10
- Fitness: 0.04
- Turnover: 0.0728
- Margin: 0.000459
- Drawdown: 0.6023
- Returns: 0.0167
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=PASS, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ family: distinct
- Decision: discard

## Batch Decision

- Any hopeful: no
- Any internal candidate: no
- Any alpha too close to E5g7vMjJ: no
- Recommended next action: stop this batch and do not run manual variants. If continuing later, use another tiny generator batch with a stronger non-price-correlation family prompt rather than tuning these three outputs.
