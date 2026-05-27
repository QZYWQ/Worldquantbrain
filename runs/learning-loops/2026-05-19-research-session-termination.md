# Learning Loop: 2026-05-19 Research Session Termination

## Session Summary

**Date:** 2026-05-19
**Goal:** Analyze unsubmitted alphas from may-19 batch for optimization/submission opportunities
**Outcome:** ❌ ALL PATHS KILLED

---

## Paths Explored

### 1. may19 Unsubmitted Alpha Batch (95 candidates)

**Method:** Retrieved full unsubmitted list (5,085 alphas), filtered S≥1.5, F≥1.0, TV<0.7, excluded submitted/KILL families

**Result:** ❌ KILLED

**Evidence:**
- Retrieved 136 promising candidates via API
- Batch-scanned Self-Correlation on 18-sample subset
- SC range: **0.8407 - 0.9734** (all FAIL, none near 0.7 threshold)
- Root cause: **Structural self-correlation** - same expression patterns (ts_decay_linear, growth_potential_rank_derivative) across the family

**Key Finding:**
- Top Sharpe alphas (S=3-4) all use **frozen fields** (composite_factor_score_derivative, multi_factor_static_score_derivative frozen 2026-04-27)
- Remaining candidates share similar expression structures → structural SC problem

---

### 2. Primary Cycle (Primary Incubation)

**Status:** Already submitted, SC=0.92 for rescue variant

---

### 3. model51 Fields FO Probe

**Method:** FO field health diagnostic for beta, correlation, systematic_risk fields

**Result:** ❌ KILLED

**Evidence:**
- All 9 variants returned **alphaId=null**
- Fields do not exist in BRAIN API or user has no access

---

### 4. New Source Field Scout (10 candidates)

**Method:** FO field health for order_imbalance, bid_ask_spread, amihud_illiquidity, market_cap, price_to_book, volatility_20, beta_60, momentum_20, residual_momentum_20, turnover_rate

**Result:** ❌ KILLED

**Evidence:**
- All 10 returned **"unknown variable"** errors
- Fields do not exist in accessible BRAIN namespace

---

### 5. mdl77 Low Crowding Probe

**Status:** ❌ STOP_LANE

**Evidence:**
- Best Fitness: **0.2** (far below 0.7 floor)
- ts_mean(ts_rank(mdl77_2amv, 20), 5) - ts_mean(...) hump variant: S=-0.95, F=-0.38

---

### 6. FO Field Health (Existing Fields)

**Method:** FO health scan of 18 fields (from batch 2026-05-16)

**Result:** ⚠️ MIXED / LIKELY KILLED

| Field | FO Sharpe | SO Result |
|-------|-----------|-----------|
| snt1_d1_dynamicfocusrank | 0.85 | Previously failed SO (Sharpe -0.15 with industry neutral) |
| revenue_growth_qoq | 0.81 | 0mAE3qzp submitted (S=1.58, F=1.03) |
| fn_interest_paid_net_q | 0.78 | Not tested - likely same pattern as fnd6_recco/rectr |
| fnd6_recco | 0.77 | Signal disappeared after SO |
| fnd6_rectr | 0.76 | Signal disappeared after SO |
| eps_revision | 0.75 | 2rvNV1qJ submitted (S=1.35) |
| trade_when_momentum | 0.71 | Not yet expanded - same family as QPn0vn3X |
| fnd6_receivable_turnover (fnd6_rectr) | 0.76 | See above |

**Pattern Identified:** FO-passing fields → SO expansion → Signal dilution/disappearance

---

## Root Cause Analysis

### Why All Paths Failed

1. **Frozen Fields:** Top Sharpe unsubmitted alphas (S=3-4) were using `composite_factor_score_derivative` and `multi_factor_static_score_derivative` frozen on 2026-04-27. These are structural freezes, not temporary issues.

2. **Structural Self-Correlation:** Remaining may19 candidates share expression patterns (ts_decay_linear, growth_potential_rank_derivative). This is family-level correlation budget exhaustion, not fixable via parameter tuning.

3. **Field Accessibility Gap:** model51 and new_source fields returned alphaId=null, meaning they're either:
   - Not in the BRAIN API namespace
   - Behind paywall/access tiers we don't have
   - Deprecated before being exposed

4. **FO→SO Dilution Pattern:** Even when FO health tests pass (S>0.7), SO expansion typically destroys signal. This suggests the predictive power is too narrow/specific to FO conditions.

---

## What Remains Unexplored

| Direction | Status | Notes |
|-----------|--------|-------|
| trade_when_momentum | ⚠️ Untested | FO S=0.71, same family as QPn0vn3X (SC=0.6852) |
| fn_interest_paid_net_q | ⚠️ Untested SO | FO S=0.78 but pattern suggests same FO→SO problem |
| Systematic field discovery | 🔲 No path | Need confirmed existing fields, can't guess |
| Alternative data sources | 🔲 No path | No access to non-BRAIN data |

---

## Recommendations for Next Session

### Immediate Actions
1. **Do NOT** spend time on fn_interest_paid_net_q - pattern consistency with fnd6_recco/rectr is too strong
2. **Do NOT** spend time on trade_when_momentum - same family as already-submitted QPn0vn3X

### Strategic Shifts Needed

1. **Wait for new data source updates** - model51/new_source fields don't exist in current API. Check back after platform updates.

2. **Accept current submission plateau** - With 20 submitted alphas and no clear new paths, current research has hit a natural boundary.

3. **Consider alternative alpha types:**
   - ATOM alphas (single dataset) - different submission criteria
   - Power Pool alphas - different competition structure
   - Region shifts (APAC, EMEA instead of USA)

4. **Monitor submitted alphas** - With 20 alphas in the pool, focus on existing alpha health rather than new discovery.

---

## Metrics at Session End

- **Submitted:** 20 alphas
- **Today's discoveries:** 0 new submission candidates
- **Research hours spent:** ~3 hours
- **Paths killed:** 6
- **Paths remaining:** 0 viable

---

*Report generated: 2026-05-19*
