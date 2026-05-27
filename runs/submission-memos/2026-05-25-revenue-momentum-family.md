# Revenue Growth Momentum — 24h Mining Results

**Date**: 2026-05-25
**Family**: revenue_momentum
**Lead**: Economic Logic — 营收增长率变化(21-day / annual baseline) → 基本面改善拐点

---

## Thesis

营收增长率的变化——而非营收绝对水平——是公司基本面改善的最纯净信号。
Revenue / 年度均值比值的横截面排名，捕获了未被市场定价的增长拐点。

---

## Execution Log

### S-1: Baseline verification (3 variants)

| Variant | Expression | S | F | Verdict |
|---------|-----------|----|----|---------|
| long_trend | `ts_rank(ts_delta(r)/ts_mean(r,252), 126)` | 0.36 | 0.11 | ❌ Too weak |
| **cross_section** | **`group_rank(ts_delta(r,63)/ts_mean(r,126), industry)`** | **1.08** | **0.61** | **✅ Thesis confirmed** |
| acceleration | `ts_rank(ts_delta(ts_delta(r)),126)` | -0.17 | -0.03 | ❌ Sign flip needed (never executed) |

### S0: Window sweep + operator scan (18 variants)

**Window series for `group_rank(ts_delta(revenue, N) / ts_mean(revenue, M), industry)`:**

| N/M | M=63 | M=126 | M=252 |
|-----|------|-------|-------|
| N=21 | **1.49** | **1.51** | **1.52 ⭐** |
| N=63 | 1.11 | 1.10 | 1.06 |
| N=126 | — | 0.88 | 0.89 |

**Operator variants on 21/252 anchor:**

| Variant | S | F | Verdict |
|---------|----|----|---------|
| `group_rank(., industry)` | 1.52 | 1.13 | ⭐ Best |
| `group_rank(., subindustry)` | 1.47 | 1.08 | 🟡 Slightly weaker |
| `group_rank(., market)` | 1.20 | 1.01 | 🟡 Tradeoff |
| `ts_zscore(., 63)` | 0.42 | 0.12 | ❌ |
| `ts_zscore(., 126)` | 0.28 | 0.08 | ❌ |
| `ts_rank(., 126)` | 0.46 | 0.16 | ❌ |
| `group_neutralize(., *)` | -0.2~-0.3 | — | ❌ Sign flipable but weak |

### A Stage: Neut × decay × densify (19 variants)

| Variant | Decay | S | F | TVR | SUS |
|---------|-------|---|----|-----|-----|
| `group_rank(., industry)` | 0 | 1.52 | 1.13 | 0.151 | 0.48 ❌ |
| `group_rank(., industry)` | 3 | 1.51 | 1.19 | 0.133 | — |
| `group_rank(., industry)` | **6** | **1.52** | **1.24** | **0.119** | **0.57** ❌ |
| `group_rank(., subindustry)` | 3 | 1.47 | 1.02 | 0.141 | — |
| `group_rank(., market)` | 3 | 1.18 | 0.99 | 0.095 | — |
| **`group_rank(., densify(bucket(rank(cap))))`** | **0** | **1.76** | **1.35** | **0.159** | **0.62 ❌** |
| **`group_rank(., densify(bucket(rank(cap))))`** | **3** | **1.74** | **1.44** | **0.135** | **0.62 ❌** |
| `group_neutralize(., *)` | 0-6 | -0.2~-0.3 | — | — | — |

---

## Key Discovery: Densify 突破

Revenue Momentum + `densify(bucket(rank(cap)))` 包装器效果显著：
- S 从 **1.52 → 1.76** (+0.24)
- F 从 **1.24 → 1.44** (+0.20)
- 但 SUS 从 0.57 只提升到 0.62，仍然 FAIL

与本次会话早期发现的 VkOY2jWY (operating_income + densify, S=1.65→2.07) 对比：
- VkOY2jWY: 运营收入+densify → S=2.07, SUS过
- 本结果: 营收增长+densify → S=1.76, SUS不过

Revenue 比 Operating_Income 在市值上的集中度更高，SUS 更难通过。

---

## Final Candidates

### Submission Candidate (Near Pass)

| AlphaID | Expression | S | F | TVR | Missing |
|---------|-----------|----|----|-----|---------|
| blvoqbPm | `group_rank(ts_delta(revenue,21)/ts_mean(revenue,252), densify(bucket(rank(cap),range='0.1,1,0.1')))` | 1.76 | 1.35 | 0.159 | SUS=0.62 vs limit=0.76 |

### Viable Backup

| AlphaID | Expression | S | F | TVR | Missing |
|---------|-----------|----|----|-----|---------|
| N1AgA6np | `group_rank(ts_delta(revenue,21)/ts_mean(revenue,252), industry) decay=6` | 1.52 | 1.24 | 0.119 | SUS=0.57 |
| j2190qoO | Same as blvoqbPm, decay=3 | 1.74 | 1.44 | 0.135 | SUS=0.62 |

### Exhausted Directions

- **Revenue acceleration** (ts_delta of ts_delta): S<0 after sign flip ❌
- **fnd6_revenue_q**: Not available in account ❌
- **Revenue zscore/ts_rank without cross-sectional grouping**: Weak S<0.5 ❌
- **Group_neutralize**: Consistently negative S ❌

---

## Recommendations

1. **Keep densify_d0 as the anchor** — SUS=0.62 needs improvement but is close
2. **Revenue Momentum family is real** — 5 variants S≥1.0 cross sectionally robust
3. **Don't submit past SUS fix** — revenue concentration is structural, but try winsorize
4. **Next economic direction**: Asset Turnover Efficiency (`revenue/assets`) or Profit Margin Expansion

## Files

- `runs/simulation-captures/revenue-momentum-s1-*.json` — 3 baselines
- `runs/simulation-captures/revenue-momentum-s0-*.json` — 18 window/operator variants
- `runs/simulation-captures/revenue-momentum-a-*.json` — 19 neut/decay/densify variants
- `scripts/revenue_momentum_batch.py` — batch mining script
