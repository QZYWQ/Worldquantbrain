# 2026-04-27 Cash Earnings Return On Equity Prescreen Results

## Loaded State

- `harness/progress.md`: `idle`, no active feature.
- `runs/research-contracts/family-budget-ledger.json`: no active incubate family.
- Scout queue under `runs/research-queues/2026-04-27-s1-profitability-value-scout.md` was executed in order.

## Official Field Check

| field | dataset | type | coverage | date coverage | visible users | visible alphas | official page |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `cash_earnings_return_on_equity` | `Analysts' Factor Model` | `Matrix` | `94.98%` | `100%` | `8` | `10` | `api.worldquantbrain.com/data-fields/cash_earnings_return_on_equity` |

## S-1 Method

- The exact snapshot-vector distinctness and signal-presence formulas are not directly observable from the public UI.
- This prescreen therefore uses a conservative proxy: low visible crowding, high coverage, and no obvious crowding spike versus the closed qfv4 lane.
- Proxy verdict: pass.

## S0 Baseline: `cash_earnings_return_on_equity`

- Expression: `ts_rank(cash_earnings_return_on_equity, 20)`
- Settings: `TOP3000`, `delay=1`, `decay=0`, `neutralization=INDUSTRY`, `truncation=0.08`, `pasteurization=ON`, `unitHandling=VERIFY`, `nanHandling=OFF`, `language=FASTEXPR`, `testPeriod=P1Y`.
- Alpha id: `A1gRMvZd`
- IS: `Sharpe -0.05`, `Fitness 0`, `Turnover 42.46%`
- TEST: `Sharpe -0.47`, `Fitness -0.09`, `Turnover 41.01%`
- Verdict: `fail`
- Read: the raw baseline is effectively flat-to-negative, so it is not a continuation candidate on its own.

## S0 Sign-Flip: `cash_earnings_return_on_equity`

- Expression: `-ts_rank(cash_earnings_return_on_equity, 20)`
- Settings: `TOP3000`, `delay=1`, `decay=0`, `neutralization=INDUSTRY`, `truncation=0.08`, `pasteurization=ON`, `unitHandling=VERIFY`, `nanHandling=OFF`, `language=FASTEXPR`, `testPeriod=P1Y`.
- Alpha id: `0meb06eK`
- IS: `Sharpe 0.05`, `Fitness 0`, `Turnover 42.46%`
- TEST: `Sharpe 0.47`, `Fitness 0.09`, `Turnover 41.01%`
- Verdict: `fail`
- Read: the sign flip recovers TEST sign, but both IS and Fitness remain far below the continuation floor.

## Overall Read

- `cash_earnings_return_on_equity` clears the S-1 proxy screen but fails the simple S0 baseline.
- The mandatory sign-flip control is still too weak to justify an incubate registration.
- The next live fallback should be `mdl177_growthanalystmodel_qga_niroe_alt`.

## Recommendation

- Do not open an incubate family from the cash lane.
- Rotate away from `cash_earnings_return_on_equity` after the mandatory reverse check.
- Move the next S-1 probe to `mdl177_growthanalystmodel_qga_niroe_alt`.
