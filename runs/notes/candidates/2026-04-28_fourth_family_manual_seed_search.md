# Fourth-Family Manual Seed Search

- Date: 2026-04-28 21:15:07 CST
- Miner manual seed file: `manual_alphas/2026-04-28_fourth_family_seed_batch.json`
- Miner result batch: `results/batch_manual_1777382077.json`
- Worldquantbrain import: `runs/candidate-batches/2026-04-28/211503_batch_manual_1777382077.json`

## Goal

Run a fourth tiny controlled search with exactly three hand-written seed alphas from field families that are materially different from E5g7vMjJ and from the failed second/third-family reversal batches.

## Why The Prior Batches Stopped

The second-alpha exploratory batch stopped because MPKWeelM, xAP62WGJ, and xAP6G6vg all failed LOW_SHARPE and LOW_FITNESS, with no Fitness > 0.5 hopeful.

The third-family controlled search stopped because npZJXnja, RR23vp31, and O0bY2GYb also failed LOW_SHARPE and LOW_FITNESS, again with no hopeful. The main failed theme was price/risk-conditioned reversal, so this manual batch avoided that family.

## Field Availability Notes

Field availability was checked using local code/docs and the existing WQ data-fields API helper without printing credential contents.

- model16 quality/efficiency fields confirmed: `fscore_bfl_profitability`, `cashflow_efficiency_rank_derivative`, `earnings_certainty_rank_derivative`
- analyst4 recommendation vector confirmed: `anl4_mark`
- fundamental2 corporate-action/debt fields confirmed: `fn_proceeds_from_issuance_of_debt_q`, `fn_repayments_of_debt_q`, `fn_repurchased_shares_value_q`, `fn_proceeds_from_issuance_of_common_stock_q`
- Some estimate and buyback field searches hit API 429 during exact checks, so the manual seeds avoided those unconfirmed fields except where prior successful API output had already confirmed availability.

## Manual Seed Design Rationale

- `quality_efficiency_seed`: model16 quality/profitability and cash-flow efficiency, avoiding price-volume correlation and simple cashflow/assets plus revenue/assets stability.
- `estimate_or_revision_seed`: analyst recommendation consensus level/change via `anl4_mark`; this is a distinct analyst data family.
- `corporate_action_or_accrual_seed`: debt issuance, debt repayment, common-stock issuance, and repurchase value changes; this tests balance-sheet/corporate-action behavior without price-volume correlation.

## Batch Size Limit

- Maximum new simulations: 3
- Actual submitted simulations: 3

## Alpha Results

### quality_efficiency_seed

- Alpha id: O0bYdoK7
- Expression: `group_neutralize(ts_decay_linear(rank(ts_delta(fscore_bfl_profitability, 20)) + rank(ts_delta(cashflow_efficiency_rank_derivative, 20)) + rank(earnings_certainty_rank_derivative), 10), subindustry)`
- Fingerprint: cee24990d2598eae3b017d754958b763
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Sharpe: 0.05
- Fitness: 0.01
- Turnover: 0.0601
- Margin: 0.00009
- Drawdown: 0.1263
- Returns: 0.0027
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=PASS, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ: distinct; no close-volume correlation, no short-horizon close reversal
- Relation to failed second/third-family candidates: distinct data family, but still too weak and slightly above target drawdown

### estimate_or_revision_seed

- Alpha id: O0bYd0O1
- Expression: `group_neutralize(ts_decay_linear(-rank(vec_avg(anl4_mark)) - rank(ts_delta(vec_avg(anl4_mark), 20)), 10), subindustry)`
- Fingerprint: 363780657b6473bda00b800643e17cc3
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Sharpe: 0.43
- Fitness: 0.14
- Turnover: 1.3573
- Margin: 0.000215
- Drawdown: 0.961
- Returns: 0.1462
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=FAIL, CONCENTRATED_WEIGHT=FAIL, LOW_SUB_UNIVERSE_SHARPE=FAIL, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ: distinct; analyst recommendation vector family
- Relation to failed second/third-family candidates: distinct field source, but unusable due to very high turnover, concentration, drawdown, and weak Sharpe/Fitness

### corporate_action_or_accrual_seed

- Alpha id: om3pj7L2
- Expression: `group_neutralize(ts_decay_linear(rank(ts_delta(fn_repurchased_shares_value_q, 252)) + rank(ts_delta(fn_repayments_of_debt_q, 252)) - rank(ts_delta(fn_proceeds_from_issuance_of_debt_q, 252)) - rank(ts_delta(fn_proceeds_from_issuance_of_common_stock_q, 252)), 20), subindustry)`
- Fingerprint: 2835e2ff205ee460dba4b2b85e36c621
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Sharpe: 0.49
- Fitness: 0.17
- Turnover: 0.0296
- Margin: 0.000987
- Drawdown: 0.0389
- Returns: 0.0146
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=FAIL, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ: distinct; corporate-action/accounting family
- Relation to failed second/third-family candidates: distinct from reversal and risk-conditioned families; best drawdown but Fitness remains far below hopeful threshold

## Decision

- Any hopeful: no
- Any internal candidate: no
- Any result too close to E5g7vMjJ: no
- Decision: stop. Do not create manual variants.
- Recommended next action: do not keep tuning these seeds. If continuing, search for a stronger new data source or field family before spending more simulations.
