# LENS 实地勘探报告：pv13 及备选域字段候选清单

## 0. Browse note

- Live Data Explorer navigation for `pv13` redirected to sign-in in this browser session, so the authoritative field inventory below comes from the saved official BRAIN data-fields response at `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`.
- Inventory scope: `2663` total fields across the USA/TOP3000 snapshot; `pv13` contributes `165` entries, of which `30` are `MATRIX` fields and `135` are `GROUP` fields.
- The saved inventory surfaces `coverage`, `dateCoverage`, `userCount`, `alphaCount`, `type`, and `description`; a separate update-frequency value was not exposed, so the table records it as `未显示` when needed.

## 1. pv13 (Relationship Data for Equity) 完整字段清单

### 1.1 Matrix fields

| 字段名 | 类型 | 覆盖率 | 日期覆盖率 | 用户数 / Alpha 数 | 优先级 | 更新频率 | 备注 | 平台原文描述 |
|---|---|---:|---:|---:|---|---|---|---|
| `primary_sector_focused_company_count` | MATRIX | 35.08% | 100.00% | 16 / 19 | 🟢 | 未显示 | sector concentration / focus proxy | Number of companies primarily focused in a given sector. |
| `pv13_com_page_rank` | MATRIX | 89.66% | — | 1090 / 1914 | 🟢 | 未显示 | competitor-side lead indicator / relationship signal | the PageRank of competitors |
| `pv13_com_rk_au` | MATRIX | 89.66% | — | 1205 / 2201 | 🟢 | 未显示 | competitor-side lead indicator / relationship signal | the HITS authority score of competitors |
| `pv13_custretsig_retsig` | MATRIX | 92.76% | 100.00% | 1052 / 2435 | 🟢 | 未显示 | customer-side lead indicator / relationship signal | Sign of customer return |
| `pv13_ompetitorgraphrank_hub_rank` | MATRIX | 89.66% | — | 798 / 1398 | 🟢 | 未显示 | competitor-side lead indicator / relationship signal | the HITS hub score of competitors |
| `pv13_reveremap` | MATRIX | 99.26% | 100.00% | 1415 / 3130 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Mapping data |
| `pv13_revere_city` | MATRIX | 99.99% | — | 756 / 1484 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | City code |
| `pv13_revere_company_total` | MATRIX | 35.08% | 100.00% | 544 / 659 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Total number of companies in the sector |
| `pv13_revere_comproduct_company` | MATRIX | 40.78% | — | 37 / 45 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Company product |
| `pv13_revere_country` | MATRIX | 100.00% | — | 608 / 1102 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Country code |
| `pv13_revere_index_cap` | MATRIX | 100.00% | — | 933 / 1746 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Company market capitalization |
| `pv13_revere_index_value` | MATRIX | 100.00% | — | 295 / 425 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Value of specified index for the date |
| `pv13_revere_key_sector_total` | MATRIX | 100.00% | — | 1801 / 3318 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Number of key focus sectors for the company |
| `pv13_revere_level` | MATRIX | 62.05% | 100.00% | 364 / 589 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Level of the sector within the hierarchy |
| `pv13_revere_parent` | MATRIX | 62.05% | 100.00% | 364 / 482 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Code of parent sector |
| `pv13_revere_term` | MATRIX | 41.15% | — | 138 / 260 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Indicates when a sector is the terminal sector (i.e., no sub-sectors) |
| `pv13_revere_term_sector_total` | MATRIX | 100.00% | — | 1178 / 3103 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Number of terminal sectors for the company |
| `pv13_revere_zipcode` | MATRIX | 92.38% | — | 467 / 1165 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Zip code |
| `pv13_ustomergraphrank_auth_rank` | MATRIX | 79.06% | — | 384 / 570 | 🟢 | 未显示 | customer-side lead indicator / relationship signal | the HITS authority score of customers |
| `pv13_ustomergraphrank_hub_rank` | MATRIX | 79.06% | — | 594 / 956 | 🟢 | 未显示 | customer-side lead indicator / relationship signal | the HITS hub score of customers |
| `pv13_ustomergraphrank_page_rank` | MATRIX | 79.06% | — | 578 / 890 | 🟢 | 未显示 | customer-side lead indicator / relationship signal | the PageRank of customers |
| `rel_num_all` | MATRIX | 99.39% | — | 1726 / 4263 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | number of the companies whose product overlapped with the instrument |
| `rel_num_comp` | MATRIX | 89.02% | — | 1110 / 1912 | 🟢 | 未显示 | competitor-side lead indicator / relationship signal | number of the instrument's competitors |
| `rel_num_cust` | MATRIX | 50.68% | — | 1009 / 2416 | 🟢 | 未显示 | customer-side lead indicator / relationship signal | number of the instrument's customers |
| `rel_num_part` | MATRIX | 78.37% | — | 2454 / 6416 | 🟢 | 未显示 | concentration / relationship structure signal | number of the instrument's partners |
| `rel_ret_all` | MATRIX | 96.13% | — | 1035 / 2025 | 🟡 | 未显示 | structural mapping or aggregate relationship metadata; plausible but indirect | Averaged one-day return of the companies whose product overlapped with the instrument |
| `rel_ret_comp` | MATRIX | 82.28% | — | 1684 / 2790 | 🟢 | 未显示 | competitor-side lead indicator / relationship signal | Averaged one-day return of the competing companies |
| `rel_ret_cust` | MATRIX | 49.21% | — | 232 / 579 | 🟢 | 未显示 | customer-side lead indicator / relationship signal | averaged one-day-return of the instrument's customers |
| `rel_ret_part` | MATRIX | 70.97% | — | 1189 / 2746 | 🟢 | 未显示 | concentration / relationship structure signal | Averaged one-day return of the instrument's partners |
| `single_sector_pureplay_company_count` | MATRIX | 35.08% | 100.00% | 12 / 16 | 🟢 | 未显示 | sector concentration / pureplay proxy | Number of companies exclusively operating in a single sector. |

### 1.2 Group fields

- These rows are grouping scaffolds. They are useful as neutralization / bucketing helpers, but they are not the best first S-1 targets by themselves.

| 字段名 | 类型 | 覆盖率 | 日期覆盖率 | 用户数 / Alpha 数 | 优先级 | 更新频率 | 备注 | 平台原文描述 |
|---|---|---:|---:|---:|---|---|---|---|
| `pv13_1l_scibr` | GROUP | 92.56% | — | 1245 / 3109 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_2l_scibr` | GROUP | 100.00% | — | 149 / 303 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_3l_scibr` | GROUP | 100.00% | — | 873 / 1514 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_4l_scibr` | GROUP | 100.00% | — | 505 / 714 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_5l_scibr` | GROUP | 100.00% | — | 636 / 921 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_6l_scibr` | GROUP | 100.00% | — | 458 / 709 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_di_5l` | GROUP | 100.00% | 100.00% | 9 / 10 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_di_6l` | GROUP | 100.00% | 100.00% | 6 / 6 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h2_min2_1k_sector` | GROUP | 36.81% | — | 941 / 1854 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | Grouping fields for top 1000 |
| `pv13_h2_sector` | GROUP | 100.00% | — | 1119 / 2591 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy23_513_sector` | GROUP | 99.33% | — | 44 / 61 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy23_sector` | GROUP | 100.00% | — | 837 / 1266 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy2_513_sector` | GROUP | 99.33% | — | 60 / 67 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy2_min2_1k_513_sector` | GROUP | 35.48% | — | 4 / 4 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchys32_513_sector` | GROUP | 99.33% | — | 13 / 13 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchys32_sector` | GROUP | 100.00% | — | 65 / 73 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_f1_513_sector` | GROUP | 99.29% | — | 22 / 38 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_f2_513_sector` | GROUP | 99.29% | — | 25 / 28 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_f2_sector` | GROUP | 100.00% | — | 38 / 47 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_f3_513_sector` | GROUP | 99.29% | — | 9 / 9 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_f4_513_sector` | GROUP | 99.29% | — | 14 / 14 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_f4_sector` | GROUP | 100.00% | — | 26 / 35 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min100_2000_513_sector` | GROUP | 69.45% | — | 9 / 10 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min100_corr21_513_sector` | GROUP | 62.99% | — | 19 / 25 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min100_corr21_sector` | GROUP | 64.74% | — | 6 / 7 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_1000_513_sector` | GROUP | 35.39% | — | 2 / 2 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_2k_513_sector` | GROUP | 69.45% | — | 12 / 15 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_2k_sector` | GROUP | 71.96% | — | 72 / 129 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_3k_all_sector` | GROUP | 100.00% | — | 24 / 33 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_513_sector` | GROUP | 69.45% | — | 37 / 54 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_industry_3000_513_sector` | GROUP | 99.29% | — | 31 / 38 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_industry_3000_sector` | GROUP | 100.00% | — | 29 / 42 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_sector` | GROUP | 71.96% | — | 60 / 80 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_sector_3000_513_sector` | GROUP | 99.29% | — | 12 / 29 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_sector_3000_sector` | GROUP | 100.00% | — | 25 / 31 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min10_top3000_513_sector` | GROUP | 99.29% | — | 12 / 24 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min20_3k_513_sector` | GROUP | 99.29% | — | 7 / 8 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min20_3k_sector` | GROUP | 100.00% | — | 29 / 33 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min20_513_sector` | GROUP | 69.45% | — | 7 / 8 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min20_f3_513_sector` | GROUP | 99.29% | — | 12 / 13 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min20_sector` | GROUP | 71.96% | — | 16 / 16 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min20_top3000_513_sector` | GROUP | 99.29% | — | 13 / 15 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min22_1000_513_sector` | GROUP | 35.39% | — | 6 / 6 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min22_513_sector` | GROUP | 69.45% | — | 4 / 4 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min22_sector` | GROUP | 71.96% | — | 14 / 24 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min25_513_sector` | GROUP | 69.45% | — | 4 / 6 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min25_sector` | GROUP | 71.96% | — | 17 / 19 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_1000_513_sector` | GROUP | 35.39% | — | 9 / 11 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_3000_513_sector` | GROUP | 99.29% | — | 16 / 21 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_513_sector` | GROUP | 69.45% | — | 13 / 13 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_focused_only_513_sector` | GROUP | 69.45% | — | 7 / 8 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_focused_only_sector` | GROUP | 71.96% | — | 710 / 1241 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_focused_pureplay_3000_513_sector` | GROUP | 99.29% | — | 285 / 378 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_focused_pureplay_513_sector` | GROUP | 69.45% | — | 18 / 22 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_focused_pureplay_sector` | GROUP | 71.96% | — | 25 / 33 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_pureplay_only_513_sector` | GROUP | 69.45% | — | 67 / 111 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_pureplay_only_sector` | GROUP | 71.96% | — | 805 / 1288 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min2_sector` | GROUP | 71.96% | — | 73 / 113 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min30_3000_513_sector` | GROUP | 99.29% | — | 14 / 23 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min30_3000_mapped_513_sector` | GROUP | 99.29% | — | 10 / 13 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min30_513_sector` | GROUP | 69.45% | — | 9 / 9 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min30_sector` | GROUP | 71.96% | — | 12 / 13 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min40_3000_513_sector` | GROUP | 99.29% | — | 14 / 16 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min50_f3_513_sector` | GROUP | 99.29% | — | 18 / 21 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min51_f1_513_sector` | GROUP | 99.29% | — | 7 / 10 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min51_f1_sector` | GROUP | 100.00% | — | 38 / 52 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min51_f2_513_sector` | GROUP | 99.29% | — | 12 / 13 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min51_f2_sector` | GROUP | 100.00% | — | 17 / 20 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min51_f3_513_sector` | GROUP | 99.29% | — | 12 / 16 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min51_f4_513_sector` | GROUP | 99.29% | — | 25 / 29 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min51_f4_sector` | GROUP | 100.00% | — | 37 / 47 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min52_1k_513_sector` | GROUP | 35.39% | — | 4 / 5 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min52_2k_513_sector` | GROUP | 69.45% | — | 5 / 5 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min52_2k_sector` | GROUP | 71.96% | — | 11 / 12 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min52_513_sector` | GROUP | 99.29% | — | 11 / 13 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min52_sector` | GROUP | 100.00% | — | 23 / 27 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min54_3000_sector` | GROUP | 100.00% | — | 32 / 37 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min5_1000_513_sector` | GROUP | 35.39% | — | 22 / 23 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min5_3000_513_sector` | GROUP | 99.29% | — | 14 / 16 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min5_513_sector` | GROUP | 69.45% | — | 7 / 7 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min5_corr21_1000_513_sector` | GROUP | 35.39% | — | 7 / 7 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min5_f3g2_sector` | GROUP | 100.00% | — | 54 / 67 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_min5_sector` | GROUP | 71.96% | — | 18 / 20 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_hierarchy_sector` | GROUP | 100.00% | — | 81 / 105 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_f1_sector` | GROUP | 100.00% | — | 1468 / 5076 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_f3_sector` | GROUP | 100.00% | — | 226 / 733 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_min10_all_sector` | GROUP | 100.00% | — | 231 / 886 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_min10_top3000_sector` | GROUP | 100.00% | — | 238 / 781 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_min20_top3000_sector` | GROUP | 100.00% | — | 227 / 933 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_min22_1000_sector` | GROUP | 36.73% | — | 529 / 1221 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | Grouping fields for top 1000 |
| `pv13_h_min24_500_sector` | GROUP | 18.60% | — | 484 / 839 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | Grouping fields for top 500 |
| `pv13_h_min2_3000_sector` | GROUP | 100.00% | — | 3150 / 18360 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_min2_focused_pureplay_3000_sector` | GROUP | 100.00% | — | 2226 / 10681 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_min2_focused_sector` | GROUP | 18.60% | — | 829 / 1486 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | Grouping fields for top 200 |
| `pv13_h_min30_3000_mapped_sector` | GROUP | 100.00% | — | 134 / 480 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_min51_f3_sector` | GROUP | 100.00% | — | 141 / 687 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_min52_1k_sector` | GROUP | 36.73% | — | 538 / 1037 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | Grouping fields for top 1000 |
| `pv13_h_min52_3000_sector` | GROUP | 100.00% | — | 91 / 433 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_min5_3000_sector` | GROUP | 100.00% | — | 169 / 593 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_h_min5_500_sector` | GROUP | 18.60% | — | 132 / 243 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | Grouping fields |
| `pv13_new_1l_scibr` | GROUP | 87.17% | — | 861 / 1443 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_new_2l_scibr` | GROUP | 100.00% | — | 68 / 83 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_new_3l_scibr` | GROUP | 100.00% | — | 49 / 61 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_new_4l_scibr` | GROUP | 100.00% | — | 74 / 104 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_new_5l_scibr` | GROUP | 100.00% | — | 92 / 128 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_new_6l_scibr` | GROUP | 100.00% | — | 101 / 184 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_liquid_min10_sector` | GROUP | 18.66% | — | 263 / 615 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_liquid_min2_sector` | GROUP | 18.66% | — | 58 / 80 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_liquid_min5_sector` | GROUP | 18.66% | — | 72 / 125 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_min10_1000_sector` | GROUP | 36.74% | — | 51 / 190 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_min10_3000_sector` | GROUP | 100.00% | — | 185 / 618 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_min20_1000_sector` | GROUP | 36.74% | — | 87 / 249 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_min20_3000_sector` | GROUP | 100.00% | — | 2610 / 11040 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_min2_1000_sector` | GROUP | 36.74% | — | 59 / 190 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_min2_3000_sector` | GROUP | 100.00% | — | 3466 / 18273 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_min5_1000_sector` | GROUP | 36.74% | — | 53 / 184 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_r2_min5_3000_sector` | GROUP | 100.00% | — | 192 / 773 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rcsed_6l` | GROUP | 100.00% | 100.00% | 3 / 3 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min10_1000_513_sector` | GROUP | 35.39% | — | 4 / 4 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min10_3000_513_sector` | GROUP | 99.33% | — | 14 / 18 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min10_513_sector` | GROUP | 69.59% | — | 5 / 7 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min10_sector` | GROUP | 72.20% | — | 18 / 21 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min20_3000_513_sector` | GROUP | 99.33% | — | 22 / 27 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min20_513_sector` | GROUP | 69.59% | — | 11 / 14 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min20_sector` | GROUP | 72.20% | — | 15 / 19 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min2_1000_513_sector` | GROUP | 35.39% | — | 6 / 8 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min2_3000_513_sector` | GROUP | 99.33% | — | 11 / 12 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min2_513_sector` | GROUP | 69.59% | — | 6 / 6 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min2_sector` | GROUP | 72.20% | — | 951 / 1765 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min30_3000_513_sector` | GROUP | 99.30% | — | 18 / 21 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min40_3000_513_sector` | GROUP | 99.30% | — | 34 / 38 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min5_1000_513_sector` | GROUP | 35.39% | — | 9 / 10 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min5_3000_513_sector` | GROUP | 99.33% | — | 12 / 12 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min5_513_sector` | GROUP | 69.59% | — | 3 / 3 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |
| `pv13_rha2_min5_sector` | GROUP | 72.20% | — | 993 / 1870 | 🔴 | 未显示 | group scaffold; use for grouping/neutralization rather than as a direct alpha source | grouping fields |

## 2. 首选 3 字段

1. **`pv13_custretsig_retsig`** — customer return sign; it is the cleanest direct relationship-derived directional signal in the set, with high coverage and moderate crowding.
2. **`pv13_ustomergraphrank_page_rank`** — customer-network centrality; this is a structural proxy for relationship importance rather than a simple accounting or analyst variable.
3. **`pv13_com_page_rank`** — competitor-network centrality; it adds the opposite side of the relationship graph and stays close to the forward-leading operating-state hypothesis.

**Near ties / backups:** `pv13_ustomergraphrank_auth_rank`, `pv13_ustomergraphrank_hub_rank`, and `rel_ret_cust` (lower crowding, but materially weaker coverage than the three above).

## 3. 备选域概要

### fundamental2 report footnotes
- 字段数: `318`
- 代表字段: `fnd2_a_restructuringcharges`, `fnd2_a_sbcpnargmpmwggil`, `fnd2_a_unrgtxbnfthatwdiptetxr`, `fnd2_a_seniornotes`, `fn_op_lease_rent_exp_a`
- 匹配判断: **中等匹配** — it is a richer footnote layer than the main statements and could surface operating pressure earlier, but it still sits inside the same slow accounting shell.

### model51 risk models
- 字段数: `16`
- 代表字段: `beta_last_60_days_spy`, `correlation_last_90_days_spy`, `systematic_risk_last_60_days`, `unsystematic_risk_last_360_days`
- 匹配判断: **弱匹配** — useful as a stabilizer / regime filter, but it is not a primary source of forward-leading operating state.

## 4. 自由探索发现

- 未发现新的、超出 `pv13` / `fundamental2` / `model51` 的额外数据大类；live route access to Data Explorer was sign-in gated, so the saved official inventory remained the browse source of record.

## 5. 下一步建议

- 建议进入 S-1 的字段顺序：1) `pv13_custretsig_retsig` → 2) `pv13_ustomergraphrank_page_rank` → 3) `pv13_com_page_rank`
- 不建议立即进入 S-1 的方向：`fundamental2` 与 `model51` 作为主线；前者更像 accounting-footnote refinement，后者更像 risk stabilization, not a fresh operating-state source.
- If we need a fallback after the first three, the next candidate is `rel_ret_cust` because it is cheaper in crowding than the competitor graph fields, even though its coverage is lower.

