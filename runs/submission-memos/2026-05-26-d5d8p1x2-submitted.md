# d5d8p1x2 Submission Memo — Accrued Liabilities / Assets

**Date**: 2026-05-26
**Status**: ✅ ACTIVE (confirmed via API)

## Alpha Details
- **ID**: d5d8p1x2
- **Family**: accrued_liabilities / assets (负债增长负向信号)
- **Expression**: `group_rank(reverse(ts_zscore(ts_delta(ts_mean(accrued_liabilities/assets, 63), 21), 126), 63)), industry)`
- **Decay**: 3
- **Neutralization**: INDUSTRY
- **Sharpe**: 1.50
- **Fitness**: 1.03
- **Turnover**: 0.0204
- **SC**: 0.4865 (PASS)

## Pre-Submit Check (8-PASS)
| Check | Result | Value |
|-------|--------|-------|
| LOW_SHARPE | ✅ PASS | 1.50 |
| LOW_FITNESS | ✅ PASS | 1.03 |
| LOW_TURNOVER | ✅ PASS | 0.0204 |
| HIGH_TURNOVER | ✅ PASS | 0.0204 |
| CONCENTRATED_WEIGHT | ✅ PASS | None |
| LOW_SUB_UNIVERSE_SHARPE | ✅ PASS | 0.82 |
| SELF_CORRELATION | ✅ PASS | 0.4865 |
| MATCHES_COMPETITION | ✅ PASS | None |

## Economic Logic
Companies with rising accrued liabilities relative to assets signal financial distress or aggressive accounting. The market underreacts to this deterioration, creating a negative cross-sectional signal. Low turnover (0.0204) confirms this is a slow, fundamental signal.

## Account State (Post-Submit)
- Total alphas: 875
- Active submitted: 6 (A1kWl0LE, O0ovYJXg, 0mzWQbPK, j21QzK9E, np3Jrqal, **d5d8p1x2**)
- Unsubmitted: ~869
- S≥1.5 unsubmitted: ~96
- Favorites: 96

## Notes
- d5d8p1x2 was the 6th submission on the new account
- Independent family (accrued liabilities), not correlated with existing submissions
- Submission via POST /alphas/{id}/submit → HTTP 201 → status: ACTIVE
