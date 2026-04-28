# Live-valid Decision Report

- Generated: 2026-04-28
- Mode: live validation against official WorldQuant BRAIN Data Explorer
- Real submission: not executed

## What changed

- The original offline queue was not directly portable because `sentiment_focus_rank` was missing on the live site.
- `fundamental_model_slow_ratio_equity_cap_follow_up_batch_06` also did not resolve as an exact live field; only related live fields were returned.
- The offline recommendation list was backed up to `runs/recommended_submission_offline_20260428.json` before the live-valid queue was written.
- Live Data Explorer validation confirmed usable fields for the replacement queue: `pv13_revere_index_value`, `anl4_af_eps_value`, `anl4_afv4_median_eps`, `earnings_per_share_average`, and `pv13_revere_key_sector_total`.

## Recommendation

Use the live-valid queue in `runs/recommended_submission.json` and submit only the top 3 if you decide to go live.

### Top 3 live-valid candidates

1. `ts_rank(anl4_af_eps_value / close, 60)` — surrogate 0.263, novelty 0.400, avg winner similarity 0.241
2. `ts_mean(pv13_revere_index_value, 63)` — surrogate 0.218, novelty 0.333, avg winner similarity 0.070
3. `group_rank(ts_sum(earnings_per_share_average/close, 60), industry)` — surrogate 0.202, novelty 0.333, avg winner similarity 0.238

### Backup branches

- `group_rank(ts_rank(earnings_per_share_average/close, 120), pv13_revere_key_sector_total)` — backup only
- `group_rank(ts_rank(anl4_af_eps_value / close, 60), pv13_revere_key_sector_total)` — backup only

## Safety reminder

- Real submission must be started manually by the user.
- Set `WQB_API_ENABLED=true` only in the shell you use for the live submission command.
- Do not treat the preview or the queue file as a submission result; no submit click has been confirmed.
