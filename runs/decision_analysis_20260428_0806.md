# 2026-04-28 Submission Decision Analysis

- Source preview: `runs/submission_preview_20260428.md`
- Source recommendation list: `runs/recommended_submission.json`
- Winner ledger: `runs/evidence/result_ledger.db`
- Analysis mode: offline, read-only

## Final decision

**Recommended option: b) 仅提交前 3 个最安全的 alpha，剩余 2 个留待下一轮扩展。**

### Why this is the best choice

- None of the 5 recommended candidates is an exact structural repeat of the current winner set.
- The queue still has mild family concentration: two ratio variants are near each other, and the nested `group_rank(ts_rank(...), industry)` branch is the most crowded against historical winners.
- Submitting all 5 would spend quota on two lower-efficiency branches.
- Re-running another parameter scan is not necessary yet: the batch is already A-grade and the main question now is quota allocation, not structural rescue.
- Re-evolving again is premature because the current batch already achieved a materially better novelty / similarity balance.

## Candidate review

| # | Candidate | Expression | Surrogate | Novelty | Avg sim to winners | Max sim to winners | Exact repeat |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `gen001-18712db91872` | `ts_rank(sentiment_focus_rank, 60)` | 0.4338 | 0.6667 | 0.1607 | 0.3333 | No |
| 2 | `gen001-232ac5c76bd9` | `ts_mean(pv13_revere_index_value, 63)` | 0.2178 | 0.3333 | 0.0503 | 0.6667 | No |
| 3 | `gen001-8c5bbca421a8` | `ts_rank(anl4_af_eps_value / close, 60)` | 0.2630 | 0.4000 | 0.1838 | 0.6000 | No |
| 4 | `gen001-af24b0eee1d1` | `ts_rank(anl4_afv4_median_eps/close, 60)` | 0.2630 | 0.4000 | 0.1756 | 0.6000 | No |
| 5 | `gen001-5caf569d9422` | `group_rank(ts_rank(fundamental_model_slow_ratio_equity_cap_follow_up_batch_06/close, 120), industry)` | 0.2519 | 0.3333 | 0.3711 | 0.6667 | No |

## Structural verdict

- **Candidate 1** is the strongest all-around branch: highest surrogate, highest novelty, and low historical similarity.
- **Candidate 2** is the most orthogonal branch to the ledger, but its surrogate is weaker, so it is a useful hedge rather than the core bet.
- **Candidate 3 / 4** are a near-duplicate sibling pair; only one should be submitted now.
- **Candidate 5** is the most crowded against winner structure and should be held back.
- The current queue is diverse enough to submit a small tranche, but not all 5.

## Recommended submission queue

1. `ts_rank(sentiment_focus_rank, 60)` — `USA` / `TOP3000` / `decay=0` / `neutralization=NONE`
2. `ts_mean(pv13_revere_index_value, 63)` — `USA` / `TOP3000` / `decay=0` / `neutralization=NONE`
3. `ts_rank(anl4_afv4_median_eps/close, 60)` — `USA` / `TOP3000` / `decay=0` / `neutralization=NONE`

## Held for next round

- `ts_rank(anl4_af_eps_value / close, 60)` — near-sibling to the chosen ratio branch.
- `group_rank(ts_rank(fundamental_model_slow_ratio_equity_cap_follow_up_batch_06/close, 120), industry)` — highest crowding risk vs winner structure.

## Submission caution

- Do **not** submit anything live until the user explicitly sets `WQB_API_ENABLED=true` and confirms they want real submission.
- This memo is a decision aid only; no network call and no submission was performed.
