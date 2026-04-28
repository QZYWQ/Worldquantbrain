# Sixth Manual Batch Results

- Date: 2026-04-28
- Source planning file: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-28_sixth_batch_candidate_designs_DO_NOT_RUN.json`
- Runnable file: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-28_sixth_batch_manual_seed_batch.json`
- Miner result file: `/Users/zpdedn/Documents/github/worldquant-miner/results/batch_manual_1777391339.json`
- Worldquantbrain import: `runs/candidate-batches/2026-04-28/234931_batch_manual_1777391339.json`
- Batch size limit: 3 manual seeds, no generator exploration, no variants

## Goal

Run exactly the three candidate designs selected by field-family discovery v2:

- option9 forward curve
- news18 Ravenpack slow event aggregates
- model51 standalone risk anomaly

The batch intentionally avoids E5g7vMjJ near-neighbor structures, close-volume correlation reversal, close60 reversal, raw social sentiment, raw analyst marks/disagreement, short-interest delta, simple accounting quality ratios, weak model16 quality/efficiency, and the failed second/third/fourth/fifth batch structures.

## Verification Result

- JSON parse: pass
- `do_not_run`: true in planning file
- `purpose`: `fresh_field_source_discovery_v2_planning_only`
- `simulation_trigger`: false
- Run command key: absent
- Candidate count: 3
- Matched discovery v2 note: yes
- Unsupported fields: none found in cached data-fields inventory, except `close` as a standard price field
- Failed-family near-neighbor: no

## Confirmed Complete Expressions

1. `option_forward_curve_carry_seed`

```text
group_neutralize(ts_decay_linear(rank(ts_rank((forward_price_120 - forward_price_60) / close, 60)), 20), subindustry)
```

2. `ravenpack_credit_dividend_slow_seed`

```text
group_neutralize(ts_decay_linear(rank(ts_mean(rp_nip_credit_ratings, 63)) + rank(ts_mean(rp_ess_dividends, 63)), 20), subindustry)
```

3. `model51_residual_risk_compression_seed`

```text
group_neutralize(ts_decay_linear(-rank(ts_rank(unsystematic_risk_last_90_days, 60)) - rank(ts_rank(beta_last_90_days_spy, 60)), 20), subindustry)
```

## Results

### option_forward_curve_seed

- Alpha id: `88a9A0Yl`
- Expression:

```text
group_neutralize(ts_decay_linear(rank(ts_rank((forward_price_120 - forward_price_60) / close, 60)), 20), subindustry)
```

- Fingerprint: `c38db002633500dac0901828c5b46554`
- Simulation status: COMPLETE
- Platform alpha status: UNSUBMITTED
- Sharpe: 0.32
- Fitness: 0.05
- Turnover: 0.2986
- Margin: 0.000057
- Drawdown: 0.0414
- Returns: 0.0086
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=FAIL, LOW_SUB_UNIVERSE_SHARPE=PASS 0.9 / 0.14, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ: distinct option-implied forward curve family; no close-volume correlation
- Relation to failed prior lanes: distinct from prior reversal, social, analyst, short-interest, model16 quality, and direct PCR/skew lanes
- Decision: discard for now; headline signal too weak and concentration failed

### ravenpack_slow_event_seed

- Alpha id: `Vk2jK36J`
- Expression:

```text
group_neutralize(ts_decay_linear(rank(ts_mean(rp_nip_credit_ratings, 63)) + rank(ts_mean(rp_ess_dividends, 63)), 20), subindustry)
```

- Fingerprint: `a925885eed895546c49f7a176dd6f46d`
- Simulation status: COMPLETE
- Platform alpha status: UNSUBMITTED
- Sharpe: -0.60
- Fitness: -0.26
- Turnover: 0.0743
- Margin: -0.000643
- Drawdown: 0.1943
- Returns: -0.0239
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=PASS, LOW_SUB_UNIVERSE_SHARPE=PASS 0.01 / -0.26, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ: distinct Ravenpack event-news family; no price-volume structure
- Relation to failed prior lanes: distinct from fast social sentiment and generic news attention, but event sparsity remains a risk
- Decision: discard; negative return and negative Fitness

### model51_risk_anomaly_seed

- Alpha id: `j29RL7rj`
- Expression:

```text
group_neutralize(ts_decay_linear(-rank(ts_rank(unsystematic_risk_last_90_days, 60)) - rank(ts_rank(beta_last_90_days_spy, 60)), 20), subindustry)
```

- Fingerprint: `5e913b074d63e3b86e1786dba518d266`
- Simulation status: COMPLETE
- Platform alpha status: UNSUBMITTED
- Sharpe: -0.90
- Fitness: -0.42
- Turnover: 0.2296
- Margin: -0.000435
- Drawdown: 0.2789
- Returns: -0.0500
- Platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_TURNOVER=PASS, HIGH_TURNOVER=PASS, CONCENTRATED_WEIGHT=FAIL 0.12271 / 0.1, LOW_SUB_UNIVERSE_SHARPE=FAIL -0.67 / -0.39, SELF_CORRELATION=PENDING, MATCHES_COMPETITION=PASS
- Hopeful: no
- Internal candidate: no
- Relation to E5g7vMjJ: distinct standalone risk-model family; no close-volume correlation or price reversal
- Relation to failed prior lanes: avoids using risk as a close60 reversal conditioner, but standalone risk signal failed directly
- Decision: discard; negative Sharpe/Fitness plus concentration and sub-universe failures

## Batch Decision

- Any hopeful: no
- Any internal candidate: no
- Any result too similar to E5g7vMjJ: no
- Recommended action: stop. Do not create variants from this batch.
