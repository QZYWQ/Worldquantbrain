# Fifth Manual Batch Results

- Date: 2026-04-28 22:36:19 CST
- Miner runnable seed file: `manual_alphas/2026-04-28_fifth_batch_manual_seed_batch.json`
- Source planning file: `manual_alphas/2026-04-28_fifth_batch_candidate_designs_DO_NOT_RUN.json`
- Miner result batch: `results/batch_manual_1777386948.json`
- Worldquantbrain import: `runs/candidate-batches/2026-04-28/223619_batch_manual_1777386948.json`
- Simulations submitted: 3
- Batch cap: 3

## Goal

Run exactly the three approved fifth-batch field-discovery designs as a tiny manual batch, then stop if no hopeful appears.

## Seed Designs Run

| Seed | Family | Expression |
| --- | --- | --- |
| `social_sentiment_fast_persistence_seed` | `socialmedia12_fast_sentiment` | `group_neutralize(ts_decay_linear(rank(ts_mean(scl12_sentiment_fast_d1, 20)), 10), subindustry)` |
| `analyst_disagreement_slow_seed` | `analyst4_estimate_dispersion` | `group_neutralize(ts_decay_linear(-rank(ts_rank(anl4_qfv4_dts_spe, 120)), 20), subindustry)` |
| `short_interest_change_seed` | `news12_short_interest` | `group_neutralize(ts_decay_linear(-rank(ts_rank(news_short_interest, 60)) - rank(ts_delta(news_short_interest, 20)), 20), subindustry)` |

## Alpha Results

### social_sentiment_fast_persistence_seed

- Alpha id: `npZR9X0q`
- Expression: `group_neutralize(ts_decay_linear(rank(ts_mean(scl12_sentiment_fast_d1, 20)), 10), subindustry)`
- Fingerprint: `593d8abe3a21a664051bb1ead073c050`
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Sharpe: -0.31
- Fitness: -0.09
- Turnover: 0.0894
- Margin: -0.000248
- Drawdown: 0.0945
- Returns: -0.0111
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=FAIL (-0.37 / -0.13), SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to `E5g7vMjJ`: distinct; no close-volume correlation and no price reversal structure
- Relation to failed second/third/fourth candidates: distinct field family, but direction was negative despite target-range turnover
- Decision: discard

### analyst_disagreement_slow_seed

- Alpha id: `2razM6bN`
- Expression: `group_neutralize(ts_decay_linear(-rank(ts_rank(anl4_qfv4_dts_spe, 120)), 20), subindustry)`
- Fingerprint: `d53dd5229429ec87c131d21997908643`
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Sharpe: -0.04
- Fitness: -0.00
- Turnover: 0.0674
- Margin: -0.000037
- Drawdown: 0.0876
- Returns: -0.0012
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=FAIL (-0.15 / -0.02), SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to `E5g7vMjJ`: distinct; analyst estimate dispersion source, no price-volume correlation
- Relation to failed second/third/fourth candidates: distinct from raw `anl4_mark`; slower and lower turnover but still no edge
- Decision: discard

### short_interest_change_seed

- Alpha id: `P0waNmxK`
- Expression: `group_neutralize(ts_decay_linear(-rank(ts_rank(news_short_interest, 60)) - rank(ts_delta(news_short_interest, 20)), 20), subindustry)`
- Fingerprint: `b415bf24d01e1968eaca68bbaa0568d6`
- Simulation status: COMPLETE
- Platform status: UNSUBMITTED
- Sharpe: 0.73
- Fitness: 0.25
- Turnover: 1.0018
- Margin: 0.000241
- Drawdown: 0.1524
- Returns: 0.1209
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=FAIL, CONCENTRATED_WEIGHT=FAIL, LOW_SUB_UNIVERSE_SHARPE=FAIL (0.26 / 0.32), SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to `E5g7vMjJ`: distinct; short-interest positioning source with no close-volume correlation
- Relation to failed second/third/fourth candidates: distinct from reversal, model16 quality, raw analyst mark, and corporate-action seeds
- Decision: discard for this cycle; positive returns are offset by Fitness 0.25, high turnover, concentration failure, sub-universe failure, and drawdown above target

## Batch Decision

- Any hopeful: no
- Any internal candidate: no
- Any alpha too close to `E5g7vMjJ`: no
- Best result by Fitness: `P0waNmxK`, Fitness 0.25
- Decision: stop. Do not create manual variants from this batch.
- Recommended next action: pause simulation spending and do another field-source discovery pass before any new manual batch.
