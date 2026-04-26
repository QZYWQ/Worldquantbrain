# 2026-04-24 Operating Income History Position Closure Memo

- Re-check time: `2026-04-25 00:01:01 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN alpha API from the logged-in browser session plus existing official simulation captures
- Scope: `operating_income_history_position` / `operating_income_smoothed_history_position`

## Decision

- Freeze the operating-income family for the current budget.
- Do not run any more same-source polish batches inside `operating_income_history_position`.
- Pivot the next research hour to a genuinely new family or information source outside the current registry.

## Fresh Official Evidence

- `Gr37elr0`
  - `https://api.worldquantbrain.com/alphas/Gr37elr0`
  - `https://api.worldquantbrain.com/alphas/Gr37elr0/check`
  - Expression: `group_rank(ts_rank(ts_mean(operating_income, 63), 252), industry)`
  - Stage / status: `IS` / `UNSUBMITTED`
  - Grade: `INFERIOR`
  - IS summary: `Sharpe 0.71 / Fitness 0.40 / Turnover 3.16% / Returns 4.03%`
  - Official checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `UNITS=WARNING`, `SELF_CORRELATION=PENDING`
- `2026-04-22-operating-income-smoothed-history-position-batch-14`
  - The 84d/72d/90d/78d ridge stayed TEST-negative across the batch; the best visible point was `operating_income_sm90_hist504_us3k_d1_v1` with `Sharpe 0.96 / Fitness 0.64 / TEST Sharpe -0.29 / Fitness -0.10`.
  - No visible Check Submission evidence or non-null subuniverse verdict was captured.
- `2026-04-22-operating-income-smoothed-history-position-batch-13`
  - `operating_income_sm21_hist252_us3k_d1_v1` reached `IS Sharpe 1.28 / Fitness 0.89` but `TEST Sharpe -0.12 / Fitness -0.02`.
  - No submission path appeared.

## Why Freeze

- The best official API check still fails `LOW_SHARPE` and `LOW_FITNESS`, with a unit warning on the raw-history expression.
- The later ridge sweep never turned holdout positive; the best visible operating-income ridge points are still TEST-negative.
- No non-null subuniverse or submission-style evidence appeared in the captured UI state.
- The family has already consumed the obvious window and smoothing axes, so more same-source polishing is not worth the budget.

## Official Evidence Used

- `https://api.worldquantbrain.com/alphas/Gr37elr0`
- `https://api.worldquantbrain.com/alphas/Gr37elr0/check`
- `runs/simulation-captures/2026-04-22-operating-income-smoothed-history-position-batch-14.json`
- `runs/simulation-captures/2026-04-22-operating-income-smoothed-history-position-batch-13.json`
- `runs/simulation-captures/2026-04-24-operating-income-history-position-batch-05.json`

## Next Step

- Stop same-family polishing in the operating-income lane.
- Move the next research hour to a genuinely new family or information source.
