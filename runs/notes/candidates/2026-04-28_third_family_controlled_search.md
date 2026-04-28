# Third-Family Controlled Search

- Date: 2026-04-28 20:44:42 CST
- Miner batch: `results/batch_1_1777380254.json`
- Worldquantbrain import: `runs/candidate-batches/2026-04-28/204435_batch_1_1777380254.json`

## Goal

Continue toward a second submitted alpha with a controlled third-family search after the failed second-alpha exploratory batch. The goal was to test at most three distinct, low-correlation ideas rather than expanding into a random large batch.

## Why The Second-Alpha Exploratory Batch Stopped

The previous batch produced three alphas distinct from E5g7vMjJ, but none crossed the hopeful threshold:

- MPKWeelM: Fitness 0.06, Sharpe 0.17
- xAP62WGJ: Fitness 0.44, Sharpe 0.64
- xAP6G6vg: Fitness 0.04, Sharpe 0.10

Because no alpha reached Fitness > 0.5, no manual variants were justified.

## Generator Constraint Changes

The feedback-aware prompt was tightened in `worldquant-miner` to:

- treat MPKWeelM, xAP62WGJ, and xAP6G6vg as negative recent examples
- avoid E5g7vMjJ near-neighbor variants
- avoid close-volume correlation reversal with `ts_corr(rank(close), rank(volume), 60/70/80/90)`
- avoid window-only and decay-only variants around the submitted alpha
- prefer a distinct family: longer-horizon price mean reversion with volatility/range conditioning, liquidity/volume anomaly without direct close-volume correlation, or stability/risk-conditioned reversal
- target Sharpe > 1.1, Fitness > 0.5, Drawdown < 0.12, and Turnover between 0.08 and 0.30
- prefer subindustry neutralization unless there is a clear reason not to
- output exactly one expression with no Markdown, explanation, code fence, or Chinese

## Batch Size Limit

- Maximum generated alpha simulations: 3
- Actual submitted simulations: 3

## Alpha Results

### Candidate 1

- Alpha id: npZJXnja
- Expression: `group_neutralize(ts_decay_linear((rank(ts_mean(cashflow_op / assets, 252)) + rank(ts_delta(revenue / assets, 120))) * rank(-ts_std_dev(returns, 120)), 20), subindustry)`
- Fingerprint: e421aa7c76ece2236e8546d5db380eb7
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Sharpe: -0.03
- Fitness: -0.01
- Turnover: 0.0257
- Margin: -0.000399
- Drawdown: 0.6195
- Returns: -0.0051
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=FAIL, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ: distinct; fundamental quality/stability structure, not close-volume correlation reversal
- Relation to failed second-alpha batch: distinct field family, but the stability filter still failed to create positive edge

### Candidate 2

- Alpha id: RR23vp31
- Expression: `group_neutralize(ts_decay_linear(-rank(ts_delta(close,60)) * rank(1 / (ts_std_dev(returns,120) + ts_mean((high - low) / close,20))),10),subindustry)`
- Fingerprint: 280ac18a34b0f97b8daf378375b4359e
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Sharpe: 0.24
- Fitness: 0.13
- Turnover: 0.0563
- Margin: 0.001336
- Drawdown: 0.4755
- Returns: 0.0376
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=PASS, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ: distinct; no close-volume correlation and no `ts_delta(close, 10)` corr70 structure
- Relation to failed second-alpha batch: adjacent to the risk-conditioned reversal attempt, but longer-horizon and still too weak

### Candidate 3

- Alpha id: O0bY2GYb
- Expression: `group_neutralize(ts_decay_linear(-rank(ts_delta(close, 60)) * (1 - rank(ts_std_dev(returns, 120))) * rank(ts_mean(volume, 20) / ts_mean(volume, 120)), 20), subindustry)`
- Fingerprint: d7afedae2044e9571920abc65547bba7
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Sharpe: 0.12
- Fitness: 0.04
- Turnover: 0.058
- Margin: 0.000523
- Drawdown: 0.3756
- Returns: 0.0152
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=PASS, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ: distinct; no close-volume correlation reversal
- Relation to failed second-alpha batch: adjacent to second-alpha volume/risk-conditioned reversal ideas, but not strong enough

## Decision

- Any hopeful: no
- Any internal candidate: no
- Any result too close to E5g7vMjJ: no
- Decision: stop. Do not create manual variants from this batch.
- Recommended next action: pivot away from pure price/risk-conditioned reversal and test a truly different data family or field source in a future tiny batch.
