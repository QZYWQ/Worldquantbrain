# 2026-04-27 S-1 Growth Potential Rerating Prescreen Results

## Loaded State

- `harness/progress.md`: session idle, no active feature.
- `runs/research-contracts/family-budget-ledger.json`: no active incubate family.
- Scout queue under `runs/research-queues/2026-04-27-s1-growth-potential-rerating-scout.md` was executed in order.

## Official Field Check

| field | dataset | type | coverage | date coverage | visible users | visible alphas | official page |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `growth_potential_rank_derivative` | `Fundamental Scores` | `Matrix` | `100%` | `100%` | `115` | `133` | `https://platform.worldquantbrain.com/data/data-fields/growth_potential_rank_derivative?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000` |

- Update frequency: not exposed in the live field page or the captured API response.

## S-1 Method

- The exact snapshot-vector distinctness formula is not directly observable from the public UI, so S-1 verdicts use a conservative proxy from live field metadata.
- Signal presence is a conservative proxy from coverage, date coverage, visible alpha density, and the clean model-family boundary.
- Thresholds used for the proxy screen: distinctness `>= 0.60`, signal presence `>= 0.40`.
- No crowded-category bonus applies because this is a `Model` field, not an `options` or `social` source.

## S-1 Scores

| field | distinctness | signal_presence | threshold used | verdict | notes |
| --- | ---: | ---: | ---: | --- | --- |
| `growth_potential_rank_derivative` | `0.67` | `0.54` | `0.60 / 0.40` | pass | Full coverage, full date coverage, and a moderate crowding profile make the source distinct enough for the front door. |

## S0 Baseline: `growth_potential_rank_derivative`

- Expression: `group_rank(growth_potential_rank_derivative, industry)`
- Settings: `TOP3000`, `delay=1`, `decay=0`, `neutralization=INDUSTRY`, `truncation=0.08`, `pasteurization=ON`, `unitHandling=VERIFY`, `nanHandling=ON`, `language=FASTEXPR`, `testPeriod=P1Y`.
- Alpha id: `vReKxb7r`
- IS: `Sharpe -0.77`, `Fitness -0.51`, `Turnover 11.41%`, `Returns -5.59%`, `Drawdown 39.67%`, `Margin -0.000981`
- TEST: `Sharpe -0.11`, `Fitness -0.02`, `Turnover 11.44%`, `Returns -0.59%`, `Drawdown 7.52%`, `Margin -0.000103`
- Verdict: `fail`
- Read: the baseline sign is wrong and TEST is still negative, so the family does not justify further S0 budget in its raw form.

## S0 Sign-Flip: `growth_potential_rank_derivative`

- Expression: `group_rank(-growth_potential_rank_derivative, industry)`
- Settings: `TOP3000`, `delay=1`, `decay=0`, `neutralization=INDUSTRY`, `truncation=0.08`, `pasteurization=ON`, `unitHandling=VERIFY`, `nanHandling=ON`, `language=FASTEXPR`, `testPeriod=P1Y`.
- Alpha id: `qMPKdbQV`
- IS: `Sharpe 0.77`, `Fitness 0.51`, `Turnover 11.41%`, `Returns 5.59%`, `Drawdown 14.84%`, `Margin 0.000981`
- TEST: `Sharpe 0.11`, `Fitness 0.02`, `Turnover 11.44%`, `Returns 0.59%`, `Drawdown 4.90%`, `Margin 0.000103`
- Verdict: `fail`
- Read: the sign flip repairs direction on IS, but TEST remains far below the `0.5` floor and Fitness stays barely positive, so the line is not strong enough to incubate.

## Overall Read

- `growth_potential_rank_derivative` clears the S-1 proxy screen.
- The mandatory sign-flipped S0 control fails the continuation floor.
- The family should not be opened as an incubate line from this batch.
- The next move should be a different source family rather than deeper same-lane polishing.

## Recommendation

- Do not register `growth_potential_rank_derivative` as incubate.
- Mark the family as `screen-kill` for the current session.
- Keep the pipeline freeze note in place for the related model siblings.
