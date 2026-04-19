# Analyst Sibling Submission Memo

- Date: `2026-04-19`
- Cycle: `official-alpha-cycle-02`
- Research direction: `analyst_eps_sibling_qfv4_industry`
- Source artifacts:
  - `./runs/simulation-captures/analyst-sibling-branch.json`
  - `./runs/candidate-batches/analyst-sibling-candidates.json`
  - `./harness/artifacts/2026-04-19/ALPHA-CAND-002/candidate-check-status.json`

## Recommendation

Current action: `submitted E5repQ81 on the official site; wait for OS testing while starting the next low-correlation branch`.

Why this is the current best action:

- `anl4_afv4_median_60d_industry` is now the strongest line across both official cycles by a clear margin, not just inside the second-cycle batch.
- Real platform alpha detail showed IS Sharpe `1.93`, Fitness `1.40`, Turnover `0.1768`, and Returns `0.0935`.
- The holdout slice was meaningfully stronger than the first-cycle baseline and both qfv4 siblings: test Sharpe `1.23`, Fitness `0.59`, Returns `0.0407`.
- A later `2026-04-19` official `/alphas/{id}/check` refresh returned `CONCENTRATED_WEIGHT=PASS`, `SELF_CORRELATION=PASS`, `LOW_FITNESS=PASS`, and `LOW_SUB_UNIVERSE_SHARPE=PASS`.
- The qfv4 siblings were useful research branches, but neither produced enough holdout lift to beat the annual-median analyst4 control.
- Manual website review was completed on `2026-04-19`, the alpha was submitted successfully, and the official page moved to `ACTV`.
- Immediate post-submit official state showed `OS Testing Status = 4 PENDING`, including pending OS-side sharpe and self-correlation checks.

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

| Rank | Candidate | Alpha | Expression | IS Summary | Test Summary | Official Check Posture | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `anl4_afv4_median_60d_industry` | `E5repQ81` | `group_rank(ts_rank(anl4_afv4_median_eps/close, 60), industry)` | Sharpe `1.93`, Fitness `1.40`, Turnover `0.1768`, Returns `0.0935` | Sharpe `1.23`, Fitness `0.59`, Returns `0.0407` | weight `PASS`, self-corr `PASS`, fitness `PASS`, sub-universe `PASS`; submitted on `2026-04-19`; OS `4 PENDING` at capture time | `submitted primary candidate` |
| 2 | `anl4_qfv4_median_60d_industry` | `qMm6xPVv` | `group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry)` | Sharpe `1.65`, Fitness `1.04`, Turnover `0.1729`, Returns `0.0691` | Sharpe `0.25`, Fitness `0.06`, Returns `0.0083` | weight `PASS`, self-corr `PASS`, fitness `PASS`, sub-universe `PASS` | `backup branch` |
| 3 | `anl4_qfv4_mean_60d_industry` | `QP59baMg` | `group_rank(ts_rank(anl4_qfv4_eps_mean/close, 60), industry)` | Sharpe `1.64`, Fitness `1.03`, Turnover `0.1733`, Returns `0.0689` | Sharpe `0.20`, Fitness `0.04`, Returns `0.0064` | weight `PASS`, self-corr `PASS`, fitness `PASS`, sub-universe `PASS` | `lower-priority backup` |

## Primary Candidate

`E5repQ81` should replace the first-cycle `qMmld9JE` baseline as the active front-of-queue alpha.

The key reason is not only that its in-sample metrics are stronger. The key reason is that the holdout slice stayed meaningfully positive instead of collapsing to a weak near-zero profile. That removes the main structural objection that blocked a more aggressive submission posture in the first cycle.

The one nuance is source freshness: during one refresh window, the official alpha object still lagged with `SELF_CORRELATION=PENDING` while `/alphas/{id}/check` had already moved to `PASS`. For current truth, this memo treats the official `/check` endpoint as the fresher source.

## Backup Candidates

`qMm6xPVv` is the right backup branch because it preserved the lower-crowding quarterly sibling idea and kept all visible official checks clean. It still did not solve the holdout-strength problem decisively, so it remains a branch, not the main submission line.

`QP59baMg` is a weaker backup because it is nearly indistinguishable from the qfv4 median sibling but slightly worse in the holdout slice.

## Why This Memo Is More Aggressive Than The First Cycle

- The first-cycle block was weak holdout robustness on the best baseline.
- The second-cycle primary candidate fixed that specific problem enough to justify advancing from `polish and branch` to `final manual submission review`.
- This is still not an instruction to click `Submit Alpha` blindly. It is a recommendation to do the final website-level confirmation now instead of spending another research hour on minor edits.

## Submission Outcome

The manual website action is complete.

- Official site confirmation on `2026-04-19`: `Alpha submitted successfully`
- Official alpha page status after submission: `ACTV`
- Post-submit official section visible on the page: `OS Testing Status`
- First captured post-submit OS state: `4 PENDING`
  - `Self-correlation check pending.`
  - `Sharpe check pending.`
  - `IS sharpe check pending.`
  - `Other check pending`

Do not edit or rework `E5repQ81` while OS is running. Treat it as the locked submitted line.

## Next Research Actions

1. Monitor `E5repQ81` until `OS Testing Status` resolves from pending into a final pass/fail state.
2. Keep `qMm6xPVv` and `QP59baMg` as same-family backups, but do not spend the next session over-polishing them first.
3. Rotate the next research hour to a more distinct backup family such as analyst disagreement around `anl4_afv4_dts_spe` or a non-analyst lane, so the next submitted line has lower family correlation.
