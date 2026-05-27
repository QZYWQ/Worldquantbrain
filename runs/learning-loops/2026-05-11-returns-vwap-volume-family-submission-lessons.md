# Alpha Cycle 05 — Research Session Lessons
**Date:** 2026-05-11
**Status:** COMPLETED — 1 submission (88Ob79jV)

## Session Summary

Started with goal of finding May 11 unsubmitted alphas with potential, excluding submitted families (pcr_oi, eps_quality_yield, price_volume_social_gate).

### Research Path
1. Discovered 33 May 11 alphas via BRAIN API
2. All candidates failed submission criteria (self-correlation or fitness issues)
3. Expanded to all-time scan — found `leQlaYNe` family (returns/vwap/volume subindustry decay_linear) as promising
4. Deep-optimized `leQlaYNe` expression through 10+ simulation iterations

### Optimization Journey (leQlaYNe → 88Ob79jV)

| Variant | Expression | Self-corr | Result |
|---------|-----------|-----------|--------|
| leQlaYNe (original) | ts_decay_linear(..., 40) | 0.858 | FAIL |
| wpnEgzz5 (+trade_when) | +scl12_sentiment filter | 0.9508 | FAIL |
| A1 (decay=20) | ts_decay_linear(..., 20) | 0.7224 | FAIL |
| A1b (decay=15) | ts_decay_linear(..., 15) | 0.7008 | FAIL (borderline) |
| **A1c (rank+decay=15)** | **rank(ts_decay_linear(...))** | **0.6796** | **PASS** |
| A1d (decay=10) | shorter decay | — | FAIL (Fitness 0.93) |

**Key finding:** Adding `rank()` wrapper was the critical break — reduced self-correlation from 0.7224 → 0.6796, below 0.7 threshold.

## Submission

- **Alpha ID:** 88Ob79jV
- **Expression:** `rank(group_neutralize(ts_decay_linear((-ts_zscore(returns, 252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry),15),subindustry))`
- **Family:** returns/vwap/volume subindustry decay_linear
- **Metrics:** Sharpe 1.89, Fitness 1.01, Turnover 38.17%, Self-corr 0.6796
- **Note:** A1b (no rank, decay=15) appeared to pass after A1c submission, but then self-corr spiked to 0.9646 — confirming family correlation budget was consumed by A1c submission.

## Key Learnings

### 1. Self-Correlation is Family-Level After Submission
Once a family member is submitted, all unsubmitted siblings immediately lose their correlation buffer. A1b showed "8 PASS" briefly but then revealed true self-corr of 0.9646 after A1c submission. **There is no post-submission rescue window.**

### 2. rank() Wrapper Breaks Time-Series Dependency
Plain smoothing (ts_decay_linear, ts_mean) creates strong auto-correlation. Wrapping with `rank()` before the final output was the only effective intervention that didn't destroy Sharpe/Fitness. This follows the playbook principle: "new information source, different structure" — rank is a structural break.

### 3. Shortening decay Helps But Destroys Signal
Reducing decay from 40→20→15 improved self-corr but at cost of signal strength. Decay=10 (A1d) destroyed fitness entirely (0.93 < 1.0). The optimal was decay=15 + rank wrapper — neither alone was sufficient.

### 4. Returns Window Choice (252 vs 60) Has Asymmetric Effect
- 252→60 (Variant A): Sharpe fell from 1.91→1.63, Fitness fell from 1.13→0.97. Signal too weak.
- Back to 252 (A1 series): Signal recovered but self-corr became the bottleneck.
- Conclusion: returns=252 is correct for this family; don't shorten.

### 5. Fitness = Sharpe × √(Returns / Turnover) — But Platform Uses Different Calibration
Platform Fitness formula doesn't match manual calculation. Platform threshold is the only truth.

### 6. Self-Correlation Threshold is Strict
0.7008 vs 0.7 cutoff — 0.0008 difference is enough to fail. No rounding mercy. The only reliable pass was 0.6796 with rank wrapper.

## Submitted Alphas Summary (Cycle 05)

| ID | Family | Sharpe | Fitness | Self-corr | Date |
|----|--------|--------|---------|-----------|------|
| 88Ob79jV | returns/vwap/volume/subindustry | 1.89 | 1.01 | 0.6796 | 2026-05-11 |

## Active Submissions (3 alphas)
- E5g7vMjJ (price_volume_corr): Sharpe 1.37, Fitness 1.01 — ACTIVE
- A1gVE97w (eps_quality_yield): Sharpe 1.63, Fitness 1.04 — ACTIVE/OS
- bloqmdJK (price_volume_social_gate): Sharpe 1.61, Fitness 1.25 — ACTIVE

## Research Queue — Exhausted Paths

| Family | Field | Result | Status |
|--------|-------|--------|--------|
| fscore_total | ts_std_dev(fscore_total, 60) != 0 | Sharpe 1.07, self-corr FAIL | KILL |
| historical_volatility | ts_rank(hvol_20) | Sharpe 0.76, Fitness 0.87 | KILL |
| option_breakeven | ts_rank(breakeven_30) | Same family as pcr_oi | KILL |
| returns/vwap/volume subindustry | leQlaYNe family | Submitted 88Ob79jV | DONE |

## Next Research Directions (New)

Since all viable May 11 candidates and the returns/vwap/volume family are exhausted:

1. **New data field exploration** — Run field-health diagnostic on untested fields from memory
2. **Close delta family** — ts_delta(close, N) variations with INDUSTRY neutralization (note: structural self-corr risk from prior learning)
3. **fn_interest_paid_net_a / fnd6_prstkc** — E5gdzRr9 showed Sharpe 1.31 but sub-universe FAIL; worth a structured variant probe
4. **count_nans(eps, 252)** — kq1NN36O family (Sharpe 1.54) but uses eps → same family as A1gVE97w

## Files Generated
- `runs/submission-memos/2026-05-11-88Ob79jV-submit.md` — submission record
- `runs/simulation-captures/` — full batch simulation history