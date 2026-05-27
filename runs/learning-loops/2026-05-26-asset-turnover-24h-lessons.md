# Asset Turnover Efficiency — 24h Mining & Upgrade Lessons

## Session Overview
- Date: 2026-05-26
- Duration: ~5h (44 baseline variants + 15 upgrade + 8 fitness boost)
- Account: mcydedn@outlook.com (new account)

## Submissions Made
1. **d5d8p1x2** — accrued_liabilities/assets (SC=0.4865) ✅ ACTIVE
   - Chosen from project records, not from starred favorites
   - Was 8-pass confirmed but not the strongest candidate
2. **E5kobRlG** — debt_carrying_value/assets (SC=0.6147) ✅ ACTIVE
   - Best independent family candidate
   - Removed star after submission

## Account State (Post-Session)
- Total alphas: 875
- Active submitted: 7 confirmed
- Starred favorites: 13 (3 removed: 2 old-account close_delta, 1 SC FAIL)
- 8-pass ready favorites waiting: 10 (S=1.53-2.23)

## Key Discovery: Asset Turnover (Revenue/Assets)

### What Worked
- **Level signal > change signal**: revenue/assets level (S=1.16) beats delta (S=0.90)
- **Subindustry > industry > market** for neutralization: S=1.16 vs 0.98 vs 1.14
- **Winsorize std=3** instead of std=4: pushed S from 1.16 → 1.19
- **Total assets > current assets > PPENT** as denominator: S=1.16 vs 0.81 vs 0.62
- **Densify bucket(rank(cap))** wrapper: improved Fitness 0.82→0.95

### What Didn't Work
- DuPont composite (turnover + margin): S=0.60-0.67 — diluted signal
- Group_neutralize: kills signal (S=0.01)
- ts_rank/ts_zscore on the ratio: S=0.12-0.44 — raw ratio better
- Short-window delta (21/63d): S=0.48-0.56
- PPENT-based turnover: S=0.36-0.62

### Threshold Bottleneck
- Best simulation: ws3+market+decay12 → S=1.25, F=0.92
- Submission check: S PASS (1.25) but F FAIL (0.92, need ≥1.0)
- Market neutral variants: F=1.04 but S=1.14
- **Cannot pass both simultaneously** with current operator set

## Starred Favorite Audit Findings

### Critical: Favorites vs 8-PASS Confusion
- Many YELLOW/tagged favorites are NOT actually 8-pass
- They were auto-marked based on high Sharpe, not submission readiness
- True 8-pass favorites (starred): **12/13** pass submission check
- Only MPkAX0LM (SC=0.9975) fails — operating_income same-family collision
- ts_decay_linear does NOT cause structural SC FAIL on new account (passed for rKA3eXKo, QPEJW2QG, d5dXKzmK, blvk8vpM)

### Old Account Families Still Usable
- close_delta old account alphas (QPEJ0oA5, RRd3e7jn) still pass 8-pass on new account
- Decision made to avoid them per project rules, not because they fail

## API & Tooling Notes
- Submission: `POST /alphas/{id}/submit` → HTTP 201 = success
- Unfavorite: `PATCH /alphas/{id}` with `{"favorite": false, "color": None, "tags": []}`
- `/check` endpoint returns `Retry-After` header during SC computation — must poll
- IS simulation (testPeriod=P0Y) vs submission check use different evaluation periods
- Existing `alpha_master_upgrade.py` build_upgrade_variants() is the correct upgrade framework

## Research Recommendations
- Asset turnover family is structurally sound but needs a different approach to cross threshold
- Consider: different region (Asia/Europe), different universe (mid-cap), D0 delay
- Next submission priority: remaining 10 starred favorites (wpLmjx55, rKA3eXKo, etc.)
- Star favorites are reliable 8-pass indicators — trust them for submission queue
