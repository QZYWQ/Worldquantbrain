# Submission Preview (Offline)

- Date: 2026-04-28
- Status: preview only, no live submission executed
- WQB API: disabled by default (`WQB_API_ENABLED=false`)
- Manual action required for any real submission

## Recommended Queue

| # | Candidate ID | Expression | Region | Universe | Decay | Neutralization | Reason |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| 1 | `gen001-18712db91872` | `ts_rank(sentiment_focus_rank, 60)` | USA | TOP3000 | 0 | NONE | Highest-confidence branch with balanced novelty and interpretability |
| 2 | `gen001-232ac5c76bd9` | `ts_mean(pv13_revere_index_value, 63)` | USA | TOP3000 | 0 | NONE | Simple, low-similarity branch with a distinct field family |
| 3 | `gen001-8c5bbca421a8` | `ts_rank(anl4_af_eps_value / close, 60)` | USA | TOP3000 | 0 | NONE | Direct fundamental ratio probe |
| 4 | `gen001-af24b0eee1d1` | `ts_rank(anl4_afv4_median_eps/close, 60)` | USA | TOP3000 | 0 | NONE | Alternate fundamental ratio branch |
| 5 | `gen001-5caf569d9422` | `group_rank(ts_rank(fundamental_model_slow_ratio_equity_cap_follow_up_batch_06/close, 120), industry)` | USA | TOP3000 | 0 | NONE | Industry-neutralized fundamental follow-up |

## Submission Rules

- This is only a preview of the curated queue.
- Any real submission must be started manually by the user.
- Before live mode, set `WQB_API_ENABLED=true` and provide valid credentials.
- Review `runs/recommended_submission.json` before sending anything live.
