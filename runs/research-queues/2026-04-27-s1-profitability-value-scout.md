# S-1 Profitability / Value Scout Queue

## Current Truth

- `harness/progress.md`: idle, no active feature.
- `runs/research-contracts/family-budget-ledger.json`: no active incubate family.
- The profitability/value lane is now closed after the final fallback `mdl177_growthanalystmodel_qga_niroe_alt` stayed too weak to open incubate.
- `mdl177_growthanalystmodel_qga_niroe_alt`: baseline `ts_rank(..., 20)` returned `leQLXVle` with IS Sharpe `0.34` / Fitness `0.06`, TEST Sharpe `0.66` / Fitness `0.18`, and Turnover `42.25%`; retire the lane.
- `cash_earnings_return_on_equity`: baseline and sign-flip are retired.
- `proforma_earnings_to_price`: sign-flip failed TEST, retired.
- `return_on_invested_capital_4`: raw baseline was too weak to continue, retired.
- The next data family is `growth_potential_rank_derivative`; use the new queue at `runs/research-queues/2026-04-27-s1-growth-potential-rerating-scout.md`.

## Closed Queue

| rank | name | status | note | next_step |
| --- | --- | --- | --- | --- |
| 1 | `mdl177_growthanalystmodel_qga_niroe_alt` | retire | final fallback tested; positive but too weak to justify incubate | Leave this lane closed. |
| 2 | `cash_earnings_return_on_equity` | retire | sign-flip recovered TEST sign but remained far too weak on IS/Fitness | Leave this lane closed. |
| 3 | `proforma_earnings_to_price` | retire | sign-flip failed on TEST | Leave this lane closed. |
| 4 | `return_on_invested_capital_4` | retire | raw baseline was too weak to continue | Leave this lane closed. |

## Closure Note

- This file is now a closure record, not a live queue.
- The next live queue lives at `runs/research-queues/2026-04-27-s1-growth-potential-rerating-scout.md`.
