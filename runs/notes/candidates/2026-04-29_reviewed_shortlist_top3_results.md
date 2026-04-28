# Reviewed Shortlist Top-3 Results

- Date: 2026-04-29
- Scope: offline-reviewed shortlist capped top-3 simulation
- Source review commit: `d0894a8`
- Miner manual batch: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_reviewed_shortlist_top3_manual_batch.json`
- Miner result file: `/Users/zpdedn/Documents/github/worldquant-miner/results/batch_manual_1777394114.json`
- Archived result copy: `runs/candidate-batches/2026-04-29/003552_batch_manual_1777394114.json`
- Archived ledger tail: `runs/simulation-captures/2026-04-29/003552_ledger_last10.csv`
- Archived fingerprints snapshot: `runs/simulation-captures/2026-04-29/003552_fingerprints.json`
- Import manifest: `runs/simulation-captures/2026-04-29/003552_manifest.json`
- Simulations run: exactly 3
- Variants run: none
- Replacement alphas run: none

## Summary

This was the first real simulation batch from the offline-reviewed shortlist.
It ran exactly the three approved expressions from the review memo. No variants,
neutralization backups, or replacement candidates were added.

Outcome: no hopeful and no internal candidate.

All three completed as `INFERIOR`. The insider proxy was the least bad result,
but Fitness was only 0.16 and Drawdown was above the target range. The analyst
revision and valuation-quality candidates had negative Fitness. The reviewed
shortlist lane should stop here and return to offline generation and triage
rather than spending immediate variants.

Target future metric band was Sharpe > 1.1, Fitness > 0.5, Drawdown < 0.12,
and Turnover between 0.08 and 0.30. None reached hopeful evidence.

## Results

### 1. insider_proxy_rp_ess_insider_cashflow_efficiency_rank_derivative_126_126_20

- Family: `ownership_or_insider_proxy`
- Alpha id: `QP2kljY5`
- Fingerprint: `bc66ff5f5dd9b17a2c9617bd0f010643`
- Status: `success`
- Grade: `INFERIOR`
- Expression:

```text
group_neutralize(ts_decay_linear(rank(ts_mean(rp_ess_insider, 126)) + rank(ts_delta(cashflow_efficiency_rank_derivative, 126)) - rank(ts_delta(fn_entity_common_stock_shares_out_q, 252)), 20), subindustry)
```

| Metric | Value |
| --- | ---: |
| Sharpe | 0.37 |
| Fitness | 0.16 |
| Turnover | 0.0423 |
| Margin | 0.001045 |
| Drawdown | 0.1588 |
| Returns | 0.0221 |

- Checks: `LOW_SHARPE` fail, `LOW_FITNESS` fail, `LOW_TURNOVER` pass,
  `HIGH_TURNOVER` pass, `CONCENTRATED_WEIGHT` pass,
  `LOW_SUB_UNIVERSE_SHARPE` pass, `SELF_CORRELATION` pending,
  `MATCHES_COMPETITION` pass.
- Hopeful: no. Fitness is below 0.5.
- Internal candidate: no. Sharpe and Fitness are far below the internal
  candidate threshold.
- Relation to E5: distinct; no close-volume correlation or price reversal.
- Relation to failed lanes: distinct from the failed Ravenpack
  credit/dividend aggregate and the failed corporate-action debt/buyback seed.
- Readout: positive direction but too weak. Turnover is below the desired
  0.08-0.30 band and Drawdown is above the 0.12 target.

### 2. earnings_revision_anl4_qfv4_eps_mean_anl4_qfv4_dts_spe_126_120_20_subindustry

- Family: `forecast_dispersion`
- Alpha id: `om35zVa6`
- Fingerprint: `0ae85e0062b76883247ad2213712846b`
- Status: `success`
- Grade: `INFERIOR`
- Expression:

```text
group_neutralize(ts_decay_linear(rank(ts_delta(anl4_qfv4_eps_mean, 126)) - rank(ts_rank(anl4_qfv4_dts_spe, 120)) + rank(ts_mean(analyst_revision_rank_derivative, 120)), 20), subindustry)
```

| Metric | Value |
| --- | ---: |
| Sharpe | -0.19 |
| Fitness | -0.05 |
| Turnover | 0.0562 |
| Margin | -0.000274 |
| Drawdown | 0.112 |
| Returns | -0.0077 |

- Checks: `LOW_SHARPE` fail, `LOW_FITNESS` fail, `LOW_TURNOVER` pass,
  `HIGH_TURNOVER` pass, `CONCENTRATED_WEIGHT` pass,
  `LOW_SUB_UNIVERSE_SHARPE` pass, `SELF_CORRELATION` pending,
  `MATCHES_COMPETITION` pass.
- Hopeful: no. Fitness is negative.
- Internal candidate: no.
- Relation to E5: distinct; no close-volume correlation or price reversal.
- Relation to failed lanes: materially different from raw `anl4_mark` and raw
  analyst disagreement, but still analyst-source adjacent.
- Readout: sign was wrong or too weak. Do not spend immediate variants on this
  exact construction.

### 3. valuation_quality_relative_valuation_rank_derivative_cashflow_efficiency_rank_derivative_126_126_20_subindustry

- Family: `valuation_quality_acceleration`
- Alpha id: `QP2klQAM`
- Fingerprint: `4279a3f041145f1c57aa9bebb2d6b0ce`
- Status: `success`
- Grade: `INFERIOR`
- Expression:

```text
group_neutralize(ts_decay_linear(rank(ts_mean(relative_valuation_rank_derivative, 126)) + rank(ts_delta(cashflow_efficiency_rank_derivative, 126)) + rank(ts_mean(growth_potential_rank_derivative, 126)), 20), subindustry)
```

| Metric | Value |
| --- | ---: |
| Sharpe | -0.91 |
| Fitness | -0.63 |
| Turnover | 0.0193 |
| Margin | -0.00629 |
| Drawdown | 0.3922 |
| Returns | -0.0605 |

- Checks: `LOW_SHARPE` fail, `LOW_FITNESS` fail, `LOW_TURNOVER` pass,
  `HIGH_TURNOVER` pass, `CONCENTRATED_WEIGHT` pass,
  `LOW_SUB_UNIVERSE_SHARPE` fail, `SELF_CORRELATION` pending,
  `MATCHES_COMPETITION` pass.
- Hopeful: no. Fitness is strongly negative.
- Internal candidate: no.
- Relation to E5: distinct; no close-volume correlation or price reversal.
- Relation to failed lanes: not the simple cashflow/assets plus revenue/assets
  stability lane and not the exact static quality seed, but it remains close to
  the broader failed fundamental/model16 area.
- Readout: weak sign, poor drawdown, low turnover, and sub-universe failure.
  Kill this construction.

## Batch Decision

- Hopefuls: none.
- Internal candidates: none.
- Best result by Fitness: `QP2kljY5`, Fitness 0.16, Sharpe 0.37.
- Best result still fails `LOW_SHARPE` and `LOW_FITNESS`; Drawdown is also above
  target and turnover is below the desired 0.08-0.30 band.

## Next Step

Because no hopeful appeared, stop this reviewed shortlist simulation lane. Do
not run local variants from these three expressions now.

Recommended next action: return to offline broad generation and triage. The
next offline generation should reduce dependence on vendor composite model16
fields, avoid analyst-only reruns unless paired with a genuinely different data
source, and keep event-news candidates away from sparse single-event aggregates
unless coverage or concentration risk can be reduced before simulation.
