# 2026-04-24 Next-Step Stop Memo

## Decision

- Stop same-family polishing in the current registry.
- Freeze the current operating-income / analyst / capex / cashflow lanes as research budget holders.
- Branch to a new family or information source instead of spending another batch on any of the current survivors.

## Why

- The best remaining registry line is still the operating-income cluster, but the latest official batch and follow-up both say it should branch away:
  - `runs/simulation-captures/2026-04-24-operating-income-history-position-batch-05.json`
  - `runs/expression-families/2026-04-21-operating-income-smoothed-history-position-follow-up.md`
- The analyst-EPS branch is blocked by live self-correlation pressure and weak holdout:
  - `qMmld9JE` is `IS 1.64 / Fitness 1.03`, but `TEST 0.15 / 0.03` is too weak for submit posture.
  - The live unsubmitted triage shows `qMm6xPVv`, `qMmld9JE`, `KPwQ2Pjz`, `RRk8k3Ln`, `A1O2Arjg`, and `d5lPJzpx` all failing self-correlation or otherwise not clearing the queue.
- The capex branch is also dead on core metrics:
  - `N15GoLWX` is `IS 0.43 / Fitness 0.15`, with negative TEST, so it is frozen.
- The cashflow/cap branch is already frozen:
  - `Jj5kq9pn` shows `IS 0.29 / Fitness 0.08`, `LOW_SHARPE FAIL`, `LOW_FITNESS FAIL`, `LOW_SUB_UNIVERSE_SHARPE FAIL`, and `UNITS WARNING`.
- The active reference alpha remains locked and should stay untouched:
  - `E5repQ81` is `ACTIVE` with `OS Testing Status = 4 PENDING`.

## Best Remaining Registry Line

- `operating_income_history_position` is still the least-bad surviving cluster on paper, but it no longer deserves more same-family budget.
- Its latest operating-income follow-up already says to stop polishing and branch away.

## Official Evidence Used

- `runs/submission-memos/E5repQ81-os-status-2026-04-24.md`
- `runs/submission-memos/2026-04-24-live-unsubmitted-triage.md`
- `runs/submission-memos/2026-04-24-analyst-eps-price-industry-live-recheck.md`
- `runs/submission-memos/2026-04-24-fundamental-model-slow-ratio-cashflow-cap-live-recheck.md`
- `runs/submission-memos/2026-04-24-capital-expenditure-amount-total-assets-live-recheck.md`
- `runs/simulation-captures/2026-04-24-operating-income-history-position-batch-05.json`
- `runs/expression-families/2026-04-21-operating-income-smoothed-history-position-follow-up.md`

## Next Minimal Experiment

- The stop decision was followed by a pivot to `sales_acceleration`.
- See `runs/submission-memos/2026-04-24-sales-acceleration-branch.md` for the current next branch.
- If that lane fails, return to the stop posture rather than reopening the closed capital-structure source.

## Status

- Current registry: frozen.
- Next action: branch to a new family / new information source.
