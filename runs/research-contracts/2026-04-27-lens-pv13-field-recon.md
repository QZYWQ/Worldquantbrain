# LENS 实地勘探报告：pv13 及备选域字段候选清单

## 0. Browse note

- Live Data Explorer navigation for `pv13` redirected to sign-in in this browser session, so the authoritative field inventory below comes from the saved official BRAIN data-fields response at `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`.
- Inventory scope: `2663` total fields across the USA/TOP3000 snapshot; `pv13` contributes `165` entries (`30` MATRIX, `135` GROUP).
- Because `pv13` exceeds 100 fields, this report lists the top 50 rows by crowding (`userCount`, then `alphaCount`) and records the remaining 115 as a count only.
- The saved inventory surfaces `coverage`, `dateCoverage`, `userCount`, `alphaCount`, `type`, and `description`; a separate update-frequency value was not exposed, so the table records it as `未显示`.

## 1. pv13 (Relationship Data for Equity) 字段清单

- Priority distribution across all `165` pv13 entries: `🟢 15`, `🟡 15`, `🔴 135`.
- Detailed rows shown: `50` / `165`; omitted remainder: `115` fields.

| 字段名 | 类型 | 覆盖率 | 日期覆盖率 | 用户数 / Alpha 数 | 优先级 | 更新频率 | 备注 | 平台原文描述 |
|---|---|---:|---:|---:|---|---|---|---|
| `pv13_r2_min2_3000_sector` | GROUP | 100.00% | — | 3466 / 18273 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_h_min2_3000_sector` | GROUP | 100.00% | — | 3150 / 18360 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_r2_min20_3000_sector` | GROUP | 100.00% | — | 2610 / 11040 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `rel_num_part` | MATRIX | 78.37% | — | 2454 / 6416 | 🟢 | 未显示 | partner count / relationship breadth signal | number of the instrument's partners |
| `pv13_h_min2_focused_pureplay_3000_sector` | GROUP | 100.00% | — | 2226 / 10681 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_revere_key_sector_total` | MATRIX | 100.00% | — | 1801 / 3318 | 🟢 | 未显示 | focus breadth / concentration proxy | Number of key focus sectors for the company |
| `rel_num_all` | MATRIX | 99.39% | — | 1726 / 4263 | 🟡 | 未显示 | overlap breadth / broad relationship proxy | number of the companies whose product overlapped with the instrument |
| `rel_ret_comp` | MATRIX | 82.28% | — | 1684 / 2790 | 🟡 | 未显示 | competitor-return basket / broad relationship proxy | Averaged one-day return of the competing companies |
| `pv13_h_f1_sector` | GROUP | 100.00% | — | 1468 / 5076 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_reveremap` | MATRIX | 99.26% | 100.00% | 1415 / 3130 | 🟡 | 未显示 | mapping / structural relationship metadata; plausible but indirect | Mapping data |
| `pv13_1l_scibr` | GROUP | 92.56% | — | 1245 / 3109 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_com_rk_au` | MATRIX | 89.66% | — | 1205 / 2201 | 🟢 | 未显示 | competitor authority centrality / direct relationship signal | the HITS authority score of competitors |
| `rel_ret_part` | MATRIX | 70.97% | — | 1189 / 2746 | 🟢 | 未显示 | partner-return basket / relationship-linked pressure proxy | Averaged one-day return of the instrument's partners |
| `pv13_revere_term_sector_total` | MATRIX | 100.00% | — | 1178 / 3103 | 🟡 | 未显示 | sector breadth / structural metadata | Number of terminal sectors for the company |
| `pv13_h2_sector` | GROUP | 100.00% | — | 1119 / 2591 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `rel_num_comp` | MATRIX | 89.02% | — | 1110 / 1912 | 🟢 | 未显示 | competitor count / relationship breadth signal | number of the instrument's competitors |
| `pv13_com_page_rank` | MATRIX | 89.66% | — | 1090 / 1914 | 🟢 | 未显示 | competitor-network centrality / direct relationship signal | the PageRank of competitors |
| `pv13_custretsig_retsig` | MATRIX | 92.76% | 100.00% | 1052 / 2435 | 🟢 | 未显示 | customer return sign / direct lead signal | Sign of customer return |
| `rel_ret_all` | MATRIX | 96.13% | — | 1035 / 2025 | 🟡 | 未显示 | overlap-return basket / broad relationship proxy | Averaged one-day return of the companies whose product overlapped with the instrument |
| `rel_num_cust` | MATRIX | 50.68% | — | 1009 / 2416 | 🟢 | 未显示 | customer count / relationship breadth signal | number of the instrument's customers |
| `pv13_rha2_min5_sector` | GROUP | 72.20% | — | 993 / 1870 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_rha2_min2_sector` | GROUP | 72.20% | — | 951 / 1765 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_h2_min2_1k_sector` | GROUP | 36.81% | — | 941 / 1854 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | Grouping fields for top 1000 |
| `pv13_revere_index_cap` | MATRIX | 100.00% | — | 933 / 1746 | 🟡 | 未显示 | size / scale proxy; indirect | Company market capitalization |
| `pv13_3l_scibr` | GROUP | 100.00% | — | 873 / 1514 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_new_1l_scibr` | GROUP | 87.17% | — | 861 / 1443 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_hierarchy23_sector` | GROUP | 100.00% | — | 837 / 1266 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_h_min2_focused_sector` | GROUP | 18.60% | — | 829 / 1486 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | Grouping fields for top 200 |
| `pv13_hierarchy_min2_pureplay_only_sector` | GROUP | 71.96% | — | 805 / 1288 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_ompetitorgraphrank_hub_rank` | MATRIX | 89.66% | — | 798 / 1398 | 🟢 | 未显示 | competitor hub centrality / direct relationship signal | the HITS hub score of competitors |
| `pv13_revere_city` | MATRIX | 99.99% | — | 756 / 1484 | 🟡 | 未显示 | geography / structural metadata | City code |
| `pv13_hierarchy_min2_focused_only_sector` | GROUP | 71.96% | — | 710 / 1241 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_5l_scibr` | GROUP | 100.00% | — | 636 / 921 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_revere_country` | MATRIX | 100.00% | — | 608 / 1102 | 🟡 | 未显示 | geography / structural metadata | Country code |
| `pv13_ustomergraphrank_hub_rank` | MATRIX | 79.06% | — | 594 / 956 | 🟢 | 未显示 | customer hub centrality / direct relationship signal | the HITS hub score of customers |
| `pv13_ustomergraphrank_page_rank` | MATRIX | 79.06% | — | 578 / 890 | 🟢 | 未显示 | customer PageRank / direct relationship signal | the PageRank of customers |
| `pv13_revere_company_total` | MATRIX | 35.08% | 100.00% | 544 / 659 | 🟡 | 未显示 | sector breadth / concentration proxy | Total number of companies in the sector |
| `pv13_h_min52_1k_sector` | GROUP | 36.73% | — | 538 / 1037 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | Grouping fields for top 1000 |
| `pv13_h_min22_1000_sector` | GROUP | 36.73% | — | 529 / 1221 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | Grouping fields for top 1000 |
| `pv13_4l_scibr` | GROUP | 100.00% | — | 505 / 714 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_h_min24_500_sector` | GROUP | 18.60% | — | 484 / 839 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | Grouping fields for top 500 |
| `pv13_revere_zipcode` | MATRIX | 92.38% | — | 467 / 1165 | 🟡 | 未显示 | geography / structural metadata | Zip code |
| `pv13_6l_scibr` | GROUP | 100.00% | — | 458 / 709 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_ustomergraphrank_auth_rank` | MATRIX | 79.06% | — | 384 / 570 | 🟢 | 未显示 | customer authority centrality / direct relationship signal | the HITS authority score of customers |
| `pv13_revere_level` | MATRIX | 62.05% | 100.00% | 364 / 589 | 🟡 | 未显示 | hierarchy depth / structural metadata | Level of the sector within the hierarchy |
| `pv13_revere_parent` | MATRIX | 62.05% | 100.00% | 364 / 482 | 🟡 | 未显示 | hierarchy link / structural metadata | Code of parent sector |
| `pv13_revere_index_value` | MATRIX | 100.00% | — | 295 / 425 | 🟡 | 未显示 | index value / structural metadata | Value of specified index for the date |
| `pv13_hierarchy_min2_focused_pureplay_3000_513_sector` | GROUP | 99.29% | — | 285 / 378 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_r2_liquid_min10_sector` | GROUP | 18.66% | — | 263 / 615 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |
| `pv13_h_min10_top3000_sector` | GROUP | 100.00% | — | 238 / 781 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than direct alpha | grouping fields |

## 2. pv13 首选 3 字段

1. **`pv13_custretsig_retsig`** — customer return sign is the cleanest direct relationship-derived directional signal in the set, and it stays orthogonal to the failed analyst / profitability families because it reads from customer interaction flow rather than accounting magnitude.
2. **`pv13_ustomergraphrank_page_rank`** — customer-network centrality is a structural relationship signal, so it can pick up operating breadth and partner topology without collapsing into the same slow statement signals that failed before.
3. **`pv13_com_page_rank`** — competitor-network centrality gives the opposite side of the relationship graph; it is useful when the signal comes from market structure and competition intensity rather than balance-sheet or analyst revisions.

**Near ties / backups:** `pv13_com_rk_au`, `pv13_ustomergraphrank_hub_rank`, `rel_ret_cust`, and `rel_num_part`.

## 3. 备选域概要

### fundamental2 report footnotes
- 字段总数: `318`
- 代表字段: fn_liab_fair_val_l1_a — Liabilities Fair Value, Recurring, Level 1, fn_oth_income_loss_fx_transaction_and_tax_translation_adj_a — after-tax FX translation / transaction adjustments, fn_accrued_liab_a — accrued liabilities on the balance sheet date, fn_op_lease_rent_exp_a — operating-lease rental expense, fn_op_lease_min_pay_due_a — minimum required lease payments due
- RECURVE 匹配判断: **中等匹配** — it is a richer footnote layer than the main statements and can surface operating pressure earlier, but it still sits inside the same slow accounting shell.
- 高优先级字段（若按操作压力口径放宽定义）: `fn_op_lease_rent_exp_a`, `fn_op_lease_min_pay_due_a`, `fn_accrued_liab_a`.

### model51 risk models
- 字段总数: `16`
- 代表字段: unsystematic_risk_last_360_days — Unsystematic Risk Last 360 Days - Relative to SPY, unsystematic_risk_last_90_days — Unsystematic Risk Last 90 Days - Relative to SPY, systematic_risk_last_90_days — Systematic Risk Last 90 Days, correlation_last_60_days_spy — Correlation to SPY in 60 Days, beta_last_60_days_spy — Beta to SPY in 60 Days
- RECURVE 匹配判断: **弱匹配** — useful as a stabilizer / regime filter, but it is not a primary source of forward-leading operating state.
- 高优先级字段: none; this domain is better used for control, normalization, or regime checks.

## 4. 自由探索发现

- No additional unexpected data class was promoted in this pass. Live Data Explorer access stayed sign-in gated, so the saved official inventory remained the source of record and mostly confirmed the expected analyst / social / model families already present in project artifacts.

## 5. 下一步：S-1 候选推进建议

| 优先级 | 字段名 | 来源域 | 建议 |
|---|---|---|---|
| 1 | `pv13_custretsig_retsig` | pv13 | 立即生成 S-1 scout |
| 2 | `pv13_ustomergraphrank_page_rank` | pv13 | 立即生成 S-1 scout |
| 3 | `pv13_com_page_rank` | pv13 | 立即生成 S-1 scout |
| 备选 | `rel_ret_cust` | pv13 | 若前 3 个 S0 均失败，启用 |

**Raw inventory note:** the saved official response contains `165` pv13 entries, `318` fundamental2 entries, and `16` model51 entries for this USA/TOP3000 snapshot.
