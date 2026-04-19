# Primary Cycle Submission Memo

- Date: `2026-04-19`
- Cycle: `official-alpha-cycle-01`
- Research direction: `analyst_eps_price_industry`
- Source artifacts:
  - `./runs/simulation-captures/primary-direction-baseline.json`
  - `./runs/candidate-batches/primary-cycle-candidates.json`
  - `./harness/artifacts/2026-04-19/ALPHA-CAND-001/candidate-check-status.json`

## Recommendation

Current action: `polish and branch, not submit now`.

Reason:

- `eps_average_60d_industry` is the best current primary candidate because its in-sample metrics are healthy and the official check refresh on `2026-04-19` returned `CONCENTRATED_WEIGHT=PASS`, `SELF_CORRELATION=PASS`, `LOW_FITNESS=PASS`, and `LOW_SUB_UNIVERSE_SHARPE=PASS`.
- The same line still has weak holdout strength. Official alpha detail showed test Sharpe `0.15`, test Fitness `0.03`, and test Returns `0.0050`, which is positive but not strong enough to call this line safely submission-ready.
- `eps_median_60d_industry` remains a valid backup because it kept nearly identical in-sample strength and also cleared the same official checks, but its holdout slice is still only weakly positive.
- The fast `20d` branch is not a primary submission candidate because official checks still show `LOW_FITNESS=FAIL` and `SELF_CORRELATION=PENDING`.
- The slow `120d` branch should not be submitted despite passing official checks because its holdout slice turned negative, which is a stronger warning than the visible in-sample pass.

## Platform Settings Used

- `Region`: `USA`
- `Universe`: `TOP3000`
- `Delay`: `1`
- `Decay`: `4`
- `Neutralization`: `SUBINDUSTRY`
- `Truncation`: `0.08`
- `Test Period`: `P1Y`
- `Pasteurization`: `ON`
- `Nan Handling`: `OFF`
- `Unit Handling`: `VERIFY`

## Ranked Candidate Queue

| Rank | Candidate | Expression | IS Summary | Test Summary | Official Check Posture | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `eps_average_60d_industry` | `group_rank(ts_rank(earnings_per_share_average/close, 60), industry)` | Sharpe `1.64`, Fitness `1.03`, Turnover `0.1732`, Returns `0.0682` | Sharpe `0.15`, Fitness `0.03`, Returns `0.0050` | weight `PASS`, self-corr `PASS`, fitness `PASS`, sub-universe `PASS` | `primary polish candidate` |
| 2 | `eps_median_60d_industry` | `group_rank(ts_rank(earnings_per_share_median_value/close, 60), industry)` | Sharpe `1.64`, Fitness `1.03`, Turnover `0.1729`, Returns `0.0682` | Sharpe `0.19`, Fitness `0.04`, Returns `0.0063` | weight `PASS`, self-corr `PASS`, fitness `PASS`, sub-universe `PASS` | `backup branch` |
| 3 | `eps_average_20d_industry` | `group_rank(ts_rank(earnings_per_share_average/close, 20), industry)` | Sharpe `1.25`, Fitness `0.57`, Turnover `0.2856`, Returns `0.0593` | Sharpe `1.25`, Fitness `0.51`, Returns `0.0464` | weight `PASS`, self-corr `PENDING`, fitness `FAIL`, sub-universe `PASS` | `deprioritize` |
| 4 | `eps_average_120d_industry` | `group_rank(ts_rank(earnings_per_share_average/close, 120), industry)` | Sharpe `1.67`, Fitness `1.22`, Turnover `0.1281`, Returns `0.0681` | Sharpe `-0.19`, Fitness `-0.04`, Returns `-0.0056` | weight `PASS`, self-corr `PASS`, fitness `PASS`, sub-universe `PASS` | `reject for now` |

## Primary Candidate

`eps_average_60d_industry` is the best current line to carry forward because it is interpretable, uses confirmed account-visible fields, and passed the official check refresh cleanly. It should stay at the front of the queue.

That said, the main bottleneck is not visible platform checks. The bottleneck is holdout robustness. This candidate should therefore be treated as a strong baseline for one more intentional branch cycle rather than a line that is already proven ready for submission.

## Backup Candidate

`eps_median_60d_industry` is the right backup because it preserves the same analyst-EPS thesis while changing the field family in a meaningful but still interpretable way. It is a better backup than the `20d` and `120d` variants because it keeps the official check posture clean without introducing a clear new failure mode.

## Why This Is Not A Submit-Now Memo

- This memo is grounded in real official alpha detail and official `/alphas/{id}/check` results.
- It does not claim a fresh platform `Check Submission` pass message was captured for the primary candidate.
- It does not treat weakly positive test-period behavior as equivalent to robust out-of-sample confirmation.
- It does not invent numeric `max_weight`, numeric `self_corr`, or a boolean `test_period_pass` when those values were not exposed by the official endpoints used for this cycle.

## Next Research Actions

1. Keep `eps_average_60d_industry` as the primary baseline and branch one less-crowded analyst sibling around `anl4_afv4_median_eps` using the same `60d` industry-relative frame.
2. Carry `eps_median_60d_industry` as the backup branch so the family has at least one same-thesis alternative with clean official checks.
3. Do not spend the next cycle polishing `eps_average_120d_industry`; the negative holdout slice is a stronger stop signal than the visible in-sample metrics are a green light.
4. Revisit `eps_average_20d_industry` only if a real gating idea appears and the official self-correlation status resolves; otherwise its current fitness failure makes it a poor use of research time.

## User Action

No immediate manual website action is required to continue this cycle locally.

The next useful official action is later, after a new branch is simulated:

1. open the new candidate on the official platform
2. refresh official checks
3. compare train/test behavior against the current `60d` baseline

Until then, this cycle should be treated as a validated research queue with one primary candidate and one backup, not as a confirmed ready-to-submit batch.
