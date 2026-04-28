# Continued Probe Log

- Date: 2026-04-28
- Status: offline/live-valid probe in progress
- WQB API: not used
- agent-policies/: untouched

## Confirmed result

- Candidate: `gen001-8c5bbca421a8`
- Expression: `ts_rank(anl4_af_eps_value / close, 60)`
- Result snapshot:
  - Sharpe: `0.83`
  - Turnover: `2.19%`
  - Fitness: `1.48`
  - Returns: `39.84%`
  - Drawdown: `65.16%`
  - Margin: `364.01‱`

## Interpretation

- This confirms the current family is still viable.
- No need to switch to a new family yet.
- The next decision is whether to continue with the remaining live-valid queue or pause for manual live submission confirmation.
