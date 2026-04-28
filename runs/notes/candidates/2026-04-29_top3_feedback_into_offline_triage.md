# Top-3 Feedback Into Offline Triage

- Date: 2026-04-29
- Scope: offline feedback and next-generation design only
- WQ simulations run in this task: none
- Simulation endpoint called in this task: no
- Runnable batch created in this task: no
- Miner triage tool updated: `/Users/zpdedn/Documents/github/worldquant-miner/tools/build_offline_candidate_shortlist.py`
- Miner tests updated: `/Users/zpdedn/Documents/github/worldquant-miner/tests/test_offline_candidate_triage.py`
- Miner planning artifact: `/Users/zpdedn/Documents/github/worldquant-miner/manual_alphas/2026-04-29_offline_generation_v2_design_DO_NOT_RUN.json`

## Summary

The reviewed shortlist top-3 batch produced no hopeful and no internal
candidate. This task feeds those failures back into the offline triage layer so
similar simple near-neighbor forms are penalized before future simulation
review.

This is not a whole-family ban. The failed structures were simple rank,
time-rank, and decay constructions. Future offline generation can still use
insider/news, analyst revision, and valuation-quality families if the designs
are better normalized, cross-confirmed, or structurally different.

## Top-3 Failure Readout

| Alpha | Family | Result | Main lesson |
| --- | --- | --- | --- |
| `QP2kljY5` / `insider_proxy_rp_ess_insider_cashflow_efficiency_rank_derivative_126_126_20` | `ownership_or_insider_proxy` | Sharpe 0.37, Fitness 0.16, Turnover 0.0423, Drawdown 0.1588, failed `LOW_SHARPE` and `LOW_FITNESS` | Simple `rp_ess_insider` plus cash-flow efficiency and share-count delta was too weak and too inert. |
| `om35zVa6` / `earnings_revision_anl4_qfv4_eps_mean_anl4_qfv4_dts_spe_126_120_20_subindustry` | `forecast_dispersion` | Sharpe -0.19, Fitness -0.05, Turnover 0.0562, Drawdown 0.112, failed `LOW_SHARPE` and `LOW_FITNESS` | Simple EPS mean change plus DTS dispersion did not have the right sign or strength. |
| `QP2klQAM` / `valuation_quality_relative_valuation_rank_derivative_cashflow_efficiency_rank_derivative_126_126_20_subindustry` | `valuation_quality_acceleration` | Sharpe -0.91, Fitness -0.63, Turnover 0.0193, Drawdown 0.3922, failed `LOW_SHARPE`, `LOW_FITNESS`, and `LOW_SUB_UNIVERSE_SHARPE` | Simple valuation-quality model-score blend is a strong negative signal for this lane. |

Decision: stop the reviewed shortlist lane and return to offline generation and
triage.

## Triage Updates

The offline shortlist builder now adds risk flags and score penalties for these
near-neighbor forms:

- `failed_reviewed_insider_proxy_simple_pair`
- `failed_reviewed_forecast_dispersion_simple_pair`
- `failed_reviewed_valuation_quality_simple_pair`
- `failed_reviewed_top3_low_sharpe_low_fitness`
- `reviewed_top3_high_drawdown_watch`
- `reviewed_top3_subuniverse_failure_watch`
- `low_turnover_inertia_risk`

These are scoring penalties, not hard bans. Candidates with richer
normalization or materially different field combinations can still pass offline
triage.

Tests now cover:

- failed reviewed insider proxy near-expression is penalized
- failed reviewed forecast-dispersion near-expression is penalized
- failed reviewed valuation-quality near-expression is penalized
- slow/low-turnover candidates receive an inertia risk flag
- distinct multi-field candidates remain retainable
- output remains `DO_NOT_RUN`
- no simulation command is produced

## Offline Generation V2 Direction

The next offline broad pool should prioritize:

- new field families not used in failed lanes
- sector-relative fundamental acceleration with explicit normalization
- estimate revision only when normalized differently from the failed EPS mean
  plus DTS dispersion pair
- option/PCR/skew ideas only if verified and not the failed forward-curve slope
- news/Ravenpack only when cross-confirmed and not the failed
  credit/dividend or raw insider proxy structures
- balance-sheet change, accruals, asset-growth, and dilution composites with
  normalization and turnover control
- multi-field composites with clear economic intuition

The next pool should avoid:

- E5 close-volume correlation reversal and corr60/70/80/90
- close60 reversal lanes
- failed fourth/fifth/sixth simple seeds
- the three reviewed top-3 near-neighbor forms
- raw single-field seeds
- high-turnover short-delta seeds
- ultra-low-turnover static seeds

## Next Step

Run no simulations until a new offline shortlist is generated and reviewed. The
next implementation step is a broad offline generation v2 seed pool using the
new feedback-aware triage penalties, followed by human review before any
future capped manual batch.
