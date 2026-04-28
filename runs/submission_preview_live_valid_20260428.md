# Submission Preview (Live-valid)

- Date: 2026-04-28
- Status: preview only, no live submission executed
- WQB API: still disabled by default; set `WQB_API_ENABLED=true` only when you are ready to submit live
- Live validation: the current account exposes live-valid fields including `pv13_revere_index_value`, `anl4_af_eps_value`, `anl4_afv4_median_eps`, `earnings_per_share_average`, `actual_eps_value_quarterly`, and `pv13_revere_key_sector_total`
- Rejected as-is: `sentiment_focus_rank` and `fundamental_model_slow_ratio_equity_cap_follow_up_batch_06` were not directly live-valid on the current site

## Recommended Queue

| # | Candidate ID | Expression | Region | Universe | Decay | Neutralization | Surrogate | Novelty | Avg winner sim | Reason |
| --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| 1 | `gen001-8c5bbca421a8` | `ts_rank(anl4_af_eps_value / close, 60)` | USA | TOP3000 | 0 | NONE | 0.263 | 0.400 | 0.241 | Highest-surrogate simple analyst-price branch on a live-valid field |
| 2 | `gen001-232ac5c76bd9` | `ts_mean(pv13_revere_index_value, 63)` | USA | TOP3000 | 0 | NONE | 0.218 | 0.333 | 0.070 | Most orthogonal hedge against the crowded winner set |
| 3 | `gen001-8344235797bd` | `group_rank(ts_sum(earnings_per_share_average/close, 60), industry)` | USA | TOP3000 | 0 | NONE | 0.202 | 0.333 | 0.238 | Live-valid earnings-average branch that adds a group-relative frame |
| 4 | `gen001-bba7a731f511` | `group_rank(ts_rank(earnings_per_share_average/close, 120), pv13_revere_key_sector_total)` | USA | TOP3000 | 0 | NONE | 0.192 | 0.333 | 0.299 | Sector-relative earnings-average backup with a slower window |
| 5 | `gen001-7bb07f9b2ffa` | `group_rank(ts_rank(anl4_af_eps_value / close, 60), pv13_revere_key_sector_total)` | USA | TOP3000 | 0 | NONE | 0.186 | 0.333 | 0.306 | Sector-relative analyst-price backup for breadth |

## Submission Guidance

- If you want to submit now, use only the top 3 entries first.
- Keep the remaining 2 as backup branches; they are live-valid but more crowded than the top hedge branches.
- Do not treat this preview as a real submission; the platform still needs manual confirmation.
- Before any live step, export `WQB_API_ENABLED=true` in the shell that launches the submission command and provide credentials interactively.
