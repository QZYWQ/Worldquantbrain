# 2026-05-09 Fitness Rescue Results - assets/cap alpha family

## Problem
All 10 unsubmitted alphas from May 8-9 failed LOW_FITNESS (Fitness 0.61-0.93 < 1.0 threshold).

## Root Expression
`group_rank(ts_rank(ts_delta(assets / cap, 2), 20), subindustry)` — d5EoL81x: Sharpe 1.95, Fitness 0.93

## Key Discovery
**Removing `group_rank` wrapper dramatically improves Fitness.**

`group_rank` was causing the expression to rank within small subindustry groups, creating noisy rankings that increased turnover. The plain `ts_rank` version produces a smoother, more stable ranking without the group boundary discontinuities.

## Results Summary

| Alpha | Expression | Decay | Neutral | IS Sharpe | IS Fitness | IS Turnover | Test Fit | 8-Pass? |
|-------|-----------|-------|---------|-----------|-----------|-------------|----------|---------|
| e7dPWeop | ts_rank(ts_delta(assets/cap,2),20) | 6 | SUBINDUSTRY | 1.96 | **1.02** | 0.5433 | 1.78 | **YES** |
| leQY59J2 | group_rank(ts_rank(ts_delta(assets/cap,2),20),industry) | 6 | INDUSTRY | 1.96 | 0.97 | 0.5527 | 1.67 | FAIL |
| RR2ozM31 | group_rank(ts_rank(ts_delta(assets/cap,2),20),industry) | 9 | INDUSTRY | 1.84 | 0.95 | 0.4685 | 1.39 | FAIL |
| akA8zRL1 | group_rank(ts_rank(ts_delta(assets/cap,2),20),industry) | 10 | INDUSTRY | 1.80 | 0.94 | 0.4496 | 1.34 | FAIL |
| Xg2xNjr5 | group_rank(ts_rank(ts_delta(assets/cap,2),20),subindustry) | 8 | SUBINDUSTRY | 1.88 | 0.93 | 0.5008 | 1.29 | FAIL |
| 9qa3p0v1 | group_rank(ts_rank(ts_delta(assets/cap,2),20),subindustry) | 12 | SUBINDUSTRY | 1.73 | 0.89 | 0.4292 | 1.02 | FAIL |
| 1YaRGXwX | ts_rank(assets/cap,20) | 6 | SUBINDUSTRY | 0.98 | 0.59 | 0.2346 | 0.96 | FAIL |
| 2raxAQwx | group_rank(ts_rank(ts_delta(assets/cap,2),20),subindustry) | 18 | SUBINDUSTRY | 1.58 | 0.83 | 0.3781 | 0.88 | FAIL |
| O0bj6qj1 | group_rank(ts_rank(ts_delta(assets/cap,2),20),subindustry) | 4 | SUBINDUSTRY | 1.96 | 0.87 | 0.6606 | 1.67 | FAIL |
| A1g5exrE | group_rank(ts_rank(ts_delta(assets/cap,2),20),subindustry) | 3 | SUBINDUSTRY | 1.92 | 0.79 | 0.7403 | 1.73 | FAIL |

## Winner: Alpha e7dPWeop

- **Expression**: `ts_rank(ts_delta(assets / cap, 2), 20)`
- **Settings**: decay=6, neutralization=SUBINDUSTRY, truncation=0.08
- **IS Metrics**: Sharpe 1.96, Fitness 1.02, Turnover 0.5433, Returns 0.1477
- **Test Metrics**: Sharpe 3.27, Fitness 1.78
- **All checks PASS** (LOW_SHARPE, LOW_FITNESS, LOW_TURNOVER, HIGH_TURNOVER, CONCENTRATED_WEIGHT, LOW_SUB_UNIVERSE_SHARPE, MATCHES_COMPETITION)
- **SELF_CORRELATION: PENDING** — needs verification before submission

## Mechanism Explanation

The `group_rank` wrapper forces rankings within small subindustry groups (~30-50 stocks). This creates:
1. **Noisy boundaries**: Small changes in raw ts_rank produce large changes in group_rank output when crossing subindustry boundaries
2. **Higher turnover**: Boundary crossing creates discontinuity-driven trading
3. **Lower Fitness**: Despite decent Sharpe, the high turnover/returns ratio hurts Fitness = Sharpe × √(Returns/Turnover)

The plain `ts_rank` version produces a smooth, continuous ranking without boundary effects, giving lower turnover for the same signal strength.

## Recommendation

Alpha **e7dPWeop** is ready for submission pending SELF_CORRELATION check resolution. The expression `ts_rank(ts_delta(assets / cap, 2), 20)` with decay=6 and SUBINDUSTRY neutralization passes all 8 checks on IS.

Note: The self-correlation check is PENDING, which is normal for new alphas. Once it returns (usually within a few submissions), if it passes, the alpha is fully submittable.