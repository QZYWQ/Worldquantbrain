# 2026-04-27 MDL177 Growth Analyst Model QGA NIROE Alt Prescreen Results

## Loaded State

- `harness/progress.md`: `idle`, no active feature.
- `runs/research-contracts/family-budget-ledger.json`: no active incubate family.
- Scout queue under `runs/research-queues/2026-04-27-s1-profitability-value-scout.md` was executed in order.

## Official Field Check

- Field: `mdl177_growthanalystmodel_qga_niroe_alt`
- Coverage: `100%`
- Date coverage: `100%`
- Visible users: `28`
- Visible alphas: `58`
- Official page: live official field page for `mdl177_growthanalystmodel_qga_niroe_alt`

## S-1 Method

- The live field metadata is still usable, but this lane is now being retired on S0 weakness rather than on an S-1 block.
- The crowding level is high enough to keep the field as a final fallback, but not strong enough to justify more budget once the baseline stays only mildly positive.
- Proxy verdict: pass.

## S0 Baseline: `mdl177_growthanalystmodel_qga_niroe_alt`

- Expression: `ts_rank(mdl177_growthanalystmodel_qga_niroe_alt, 20)`
- Settings: `TOP3000`, `delay=1`, `decay=0`, standard industry neutralization, `truncation=0.08`, `pasteurization=ON`, `unitHandling=VERIFY`, `nanHandling=OFF`, `language=FASTEXPR`, `testPeriod=P1Y`.
- Alpha id: `leQLXVle`
- IS: `Sharpe 0.34`, `Fitness 0.06`
- TEST: `Sharpe 0.66`, `Fitness 0.18`
- Turnover: `42.25%`
- Verdict: `fail`
- Read: positive, but too weak to justify opening incubate. The line is better than the dead profitability names, but not by enough margin to spend more budget.

## Overall Read

- The profitability/value lane is exhausted after `proforma_earnings_to_price`, `return_on_invested_capital_4`, `cash_earnings_return_on_equity`, and `mdl177_growthanalystmodel_qga_niroe_alt`.
- No incubate family should be opened from this lane.
- The next data family should be `growth_potential_rank_derivative`.

## Recommendation

- Close the profitability/value lane.
- Pivot the next S-1 probe to growth potential rerating.
- Leave the ledger untouched because no field cleared S0 into incubate.
