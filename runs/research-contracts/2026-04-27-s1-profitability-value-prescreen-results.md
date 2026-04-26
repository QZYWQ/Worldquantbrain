# 2026-04-27 S-1 Profitability / Value Prescreen Results

## Loaded State

- `harness/progress.md`: `idle`, no active feature.
- `runs/research-contracts/family-budget-ledger.json`: no active incubate family.
- Scout queue under `runs/research-queues/2026-04-27-s1-profitability-value-scout.md` was executed in order.

## Official Field Checks

| field | dataset | type | coverage | date coverage | visible alphas | official page |
| --- | --- | --- | --- | --- | ---: | --- |
| `proforma_earnings_to_price` | `Analysts' Factor Model` | `Matrix` | `95.63%` | `100%` | `1` | `api.worldquantbrain.com/data-fields/proforma_earnings_to_price` |
| `return_on_invested_capital_4` | `Analysts' Factor Model` | `Matrix` | `100%` | `100%` | `6` | `api.worldquantbrain.com/data-fields/return_on_invested_capital_4` |

## S-1 Method

- The exact snapshot-vector distinctness formula is not directly observable from the public UI, so S-1 verdicts use a conservative proxy from live field metadata.
- Proxy signals favor low crowding, high coverage, and a clean analysts/model family boundary over same-family retuning.
- Thresholds used for the proxy screen: distinctness `>= 0.60`, signal presence `>= 0.40`.

## S-1 Scores

| field | distinctness | signal_presence | threshold used | verdict | notes |
| --- | ---: | ---: | ---: | --- | --- |
| `proforma_earnings_to_price` | `0.76` | `0.58` | `0.60 / 0.40` | pass | Lowest-crowding profitability/value source in the live search snapshot; price-normalized and still very sparse. |
| `return_on_invested_capital_4` | `0.67` | `0.55` | `0.60 / 0.40` | pass | Clean pure-profitability anchor with full coverage and still low visible crowding. |

## S0 Baseline: `proforma_earnings_to_price`

- Expression: `ts_rank(proforma_earnings_to_price, 20)`
- Settings: `TOP3000`, `delay=1`, `decay=0`, `neutralization=INDUSTRY`, `truncation=0.08`, `pasteurization=ON`, `unitHandling=VERIFY`, `nanHandling=OFF`, `selectionHandling=POSITIVE`, `selectionLimit=10`, `language=FASTEXPR`, `testPeriod=P1Y`.
- Alpha id: `pwVqm3kV`
- IS: `Sharpe -0.92`, `Fitness -0.32`, `Turnover 46.11%`
- TEST: `Sharpe 0.57`, `Fitness 0.13`, `Turnover 44.77%`
- Verdict: `fail`
- Read: raw sign is wrong on IS, even though TEST stays positive; by project rule, this is a sign-flip candidate rather than a polishing candidate.

## S0 Baseline: `return_on_invested_capital_4`

- Expression: `ts_rank(return_on_invested_capital_4, 20)`
- Settings: `TOP3000`, `delay=1`, `decay=0`, `neutralization=INDUSTRY`, `truncation=0.08`, `pasteurization=ON`, `unitHandling=VERIFY`, `nanHandling=OFF`, `selectionHandling=POSITIVE`, `selectionLimit=10`, `language=FASTEXPR`, `testPeriod=P1Y`.
- Alpha id: `LLgPjJGe`
- IS: `Sharpe 0.26`, `Fitness 0.04`, `Turnover 41.89%`
- TEST: `Sharpe 0.07`, `Fitness 0.01`, `Turnover 38.98%`
- Verdict: `fail`
- Read: direction is weakly positive but far too small to justify deeper budget on the raw baseline.

## S0 Sign-Flip: `proforma_earnings_to_price`

- Expression: `-ts_rank(proforma_earnings_to_price, 20)`
- Settings: `TOP3000`, `delay=1`, `decay=0`, `neutralization=INDUSTRY`, `truncation=0.08`, `pasteurization=ON`, `unitHandling=VERIFY`, `nanHandling=OFF`, `selectionHandling=POSITIVE`, `selectionLimit=10`, `language=FASTEXPR`, `testPeriod=P1Y`.
- Alpha id: `QP21klOp`
- IS: `Sharpe 0.93`, `Fitness 0.32`, `Turnover 46.11%`
- TEST: `Sharpe -0.57`, `Fitness -0.13`, `Turnover 44.77%`
- Verdict: `fail`
- Read: the sign flip repairs the IS sign but breaks the TEST period, so the lane should be retired rather than polished further.

## Overall Read

- Both fields cleared the S-1 metadata screen.
- `proforma_earnings_to_price` failed the mandatory sign-flip control on TEST, so the source does not survive the front-door sign check.
- `return_on_invested_capital_4` remains too weak to justify deeper budget.
- The next live fallback is `cash_earnings_return_on_equity`.

## Recommendation

- Do not open an incubate family from the current two fields.
- Mark `proforma_earnings_to_price` as retired after the sign-flip failure.
- Move the next S-1 probe to `cash_earnings_return_on_equity`.
