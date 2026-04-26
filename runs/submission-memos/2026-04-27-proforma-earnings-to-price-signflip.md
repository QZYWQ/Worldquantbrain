# 2026-04-27 Proforma Earnings To Price Sign-Flip Result

- Re-check time: `2026-04-27 01:46:24 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN Simulate page plus alpha detail API from the logged-in browser session
- Scope: `proforma_earnings_to_price`
- Family: `proforma_earnings_to_price`

## Decision

- Do not open an incubate family from this lane.
- Retire `proforma_earnings_to_price` for the current budget.
- Rotate the next official budget to `cash_earnings_return_on_equity`.
- Do not spend more budget on lookback, smoothing, neutralization, or group-axis polishing around this field.

## Official Evidence

- Prescreen results:
  - `runs/research-contracts/2026-04-27-s1-profitability-value-prescreen-results.md`
- Scout queue:
  - `runs/research-queues/2026-04-27-s1-profitability-value-scout.md`
- Live simulation:
  - `api.worldquantbrain.com/simulations/t9Jjb3B4Arcfsov6UfAqg`
- Alpha detail:
  - `api.worldquantbrain.com/alphas/QP21klOp`

## Batch Result

- Sign flip `QP21klOp`
  - expression: `-ts_rank(proforma_earnings_to_price, 20)`
  - settings: `TOP3000`, `delay=1`, `decay=0`, `neutralization=INDUSTRY`, `truncation=0.08`, `pasteurization=ON`, `unitHandling=VERIFY`, `nanHandling=OFF`, `selectionHandling=POSITIVE`, `selectionLimit=10`, `language=FASTEXPR`, `testPeriod=P1Y`
  - IS Sharpe `0.93`
  - IS Fitness `0.32`
  - Turnover `46.11%`
  - Returns `5.51%`
  - Drawdown `6.64%`
  - Margin `0.239‱`
  - Checks: `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_TURNOVER=PASS`, `HIGH_TURNOVER=PASS`, `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, `SELF_CORRELATION=PENDING`, `MATCHES_COMPETITION=PASS`
  - TEST Sharpe `-0.57`
  - TEST Fitness `-0.13`
  - Turnover `44.77%`
  - Returns `-2.25%`
  - Drawdown `3.93%`
  - Margin `-0.10‱`

## Why This Stops Here

- The sign-flipped control turns negative on TEST.
- Compared with the baseline `pwVqm3kV` (`IS Sharpe -0.92`, `TEST Sharpe 0.57`), the sign flip repairs IS but breaks the holdout.
- This is a lane-level reject, not a polishing candidate.

## Next Minimal Experiment

- Rotate to `cash_earnings_return_on_equity` as the next S-1 fallback.
- If that lane also stalls, move to `mdl177_growthanalystmodel_qga_niroe_alt`.

## Status

- Family state: `retire`
- Portfolio posture: `rotate`
- Batch posture: `complete`
