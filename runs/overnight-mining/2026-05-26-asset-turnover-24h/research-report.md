# Asset Turnover Efficiency — 24h Batch Mining Report

**Date**: 2026-05-26
**Duration**: 2.4h (44 variants, 5 phases)
**Script**: `scripts/asset_turnover_24h_batch.py`

---

## Key Discoveries

### 1. Asset Turnover (Revenue/Assets) is CONFIRMED as a viable signal ✅
**Best variant: `p1_base_at_subind`** — S=**1.16**, F=0.82, TVR=0.0168
- Economic direction: higher revenue/assets → higher returns (sign confirmed via flip)
- Optimal grouping: subindustry (beats industry S=0.98 and market S=1.14)
- Very low turnover (0.0168) — balance-sheet fundamental, quarterly update

### 2. Densify Upgrade Works 🚀
`group_rank(x, densify(bucket(rank(cap))))`:
- d0: S=1.15, F=0.95, TVR=0.0440
- d3: S=1.13, F=0.93, TVR=0.0286  
- d6: S=1.12, F=0.92, TVR=0.0224
- **Fitness jump**: 0.82 → 0.95 (densify improves size-neutrality)

### 3. Level > Change (key structural finding)
| Signal type | Best S | Best F | Insight |
|------------|--------|--------|---------|
| Level (revenue/assets) | **1.16** | **1.03** | Efficiency level matters most |
| Delta (change in turnover) | 0.90 | 0.54 | Long-window delta helps (126/252) |
| Revenue-only delta | 1.26 | 0.96 | = revenue_momentum family (known SUS issue) |

### 4. Total Assets is the Optimal Denominator
| Denominator | Best S | Best F |
|------------|--------|--------|
| **Total Assets** | **1.16** | **1.03** |
| Current Assets | 0.81 | 0.57 |
| PP&E (Fixed Assets) | 0.62 | 0.28 |
| Operating Assets (PPENT+ACUR) | 0.60 | 0.38 |

### 5. What Doesn't Work ❌
- DuPont composite (turnover + margin): S=0.60-0.67
- Group_neutralize: kills the signal (S=0.01)
- Short-window delta of turnover: S=0.48-0.70
- PPENT/revenue: S=0.36-0.62

---

## Top Candidates (S≥1.0)

| Rank | Name | S | F | TVR | Expression |
|------|------|---|----|-----|-----------|
| 1 | p1_base_at_subind | **1.16** | 0.82 | 0.0168 | `group_rank(revenue/assets_w, subindustry)` |
| 2 | p4_densify_d0 | **1.15** | 0.95 | 0.0440 | `group_rank(revenue/assets_w, densify(bucket(rank(cap))))` d0 |
| 3 | p1_base_at_market | **1.14** | **1.03** | 0.0090 | `group_rank(revenue/assets_w, market)` |
| 4 | p4_densify_d3 | **1.13** | 0.93 | 0.0286 | densify d3 |
| 5 | p4_densify_d6 | **1.12** | 0.92 | 0.0224 | densify d6 |
| 6 | p1_base_at_i252 | 0.98 | 0.69 | 0.0111 | industry, 252d smoothed |
| 7 | p1_base_at_i126 | 0.92 | 0.64 | 0.0152 | industry, 126d |
| 8 | p2_dr_126_252 | 0.90 | 0.54 | 0.0178 | long delta (revenue/assets) |

---

## Next Steps (SC Verification)

### Priority for /check:
1. **p1_base_at_subind** (S=1.16, F=0.82) — best pure turnover signal
2. **p4_densify_d0** (S=1.15, F=0.95) — best fitness, size-neutral via densify
3. **p1_base_at_market** (S=1.14, F=1.03) — highest fitness

### Self-correlation concerns:
- Revenue/assets is structurally orthogonal to:
  - Operating profitability (S already submitted) — different DuPont leg
  - Debt/leverage (E5kobRlG) — different side of balance sheet
  - Revenue momentum — different mechanism (level vs delta)
- Estimated cross-correlation: 0.3-0.5 with operating_income families

### Alpha IDs on platform (all tagged `asset_turnover_24h`, YELLOW)
Need to extract from simulation-captures JSON files and run /check.

---

## Memory Update Needed
- Asset Turnover (revenue/assets) confirmed as new viable research direction
- Best structure: group_rank(divide(revenue, assets), subindustry)
- Densify wrapper effective but not as dramatic as with operating_income
- Level signal stronger than change signal for efficiency metrics
- Total assets is the optimal denominator
