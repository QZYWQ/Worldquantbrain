# 2026-04-27 S-1 Analyst QFV4 Prescreen Results

## Loaded State

- `harness/progress.md`: session idle, no active feature.
- `runs/research-contracts/family-budget-ledger.json`: no active incubate family.
- `runs/research-queues/2026-04-26-s1-analyst-qfv4-scout.md`: qfv4 median, qfv4 mean, and afv4 median control were the queued candidates.

## Method

- S-0 baseline used the simple screen expression `ts_rank(<field>, 20)`.
- Live settings used: `EQUITY`, `USA`, `TOP3000`, `delay=1`, `decay=0`, `neutralization=INDUSTRY`, `truncation=0.08`, `pasteurization=ON`, `unitHandling=VERIFY`, `nanHandling=OFF`, `language=FASTEXPR`.
- Because the exact snapshot-vector distinctness formula is not directly observable from the public UI, S-1 verdicts below use a conservative proxy based on field family separation, coverage, and existing official branch evidence.

## Candidate Results

| field | role | S-1 verdict | S0 / baseline alpha | IS | TEST | result |
| --- | --- | --- | --- | --- | --- | --- |
| `anl4_qfv4_median_eps` | primary fresh sibling | pass | `kqLzzQvK` / `ts_rank(anl4_qfv4_median_eps, 20)` | `Sharpe 0.21`, `Fitness 0.04`, `Turnover 22.79%` | `Sharpe -0.62`, `Fitness -0.18`, `Turnover 22.77%` | fail |
| `anl4_qfv4_eps_mean` | first backup | pass | `leQLLe3A` / `ts_rank(anl4_qfv4_eps_mean, 20)` | `Sharpe 0.26`, `Fitness 0.05`, `Turnover 22.77%` | `Sharpe -0.54`, `Fitness -0.14`, `Turnover 22.76%` | fail |
| `anl4_afv4_median_eps` | control / comparator | comparator-only | `qMPKKd8K` / `ts_rank(anl4_afv4_median_eps, 20)` | `Sharpe 0.72`, `Fitness 0.25`, `Turnover 22.35%` | `Sharpe -0.35`, `Fitness -0.08`, `Turnover 22.45%` | fail |

## Interpretation

- The qfv4 sibling pair is clean on source selection but too weak on the simple S0 baseline.
- The afv4 control is the strongest of the three on IS, but it still turns negative on TEST and does not justify a new incubate lane from this baseline.
- No candidate registered a submit-worthy or incubate-worthy result in this scout batch.

## Decision

- No new incubate family opened.
- Keep the qfv4 scout lane closed for now and pivot to a different fresh source before the next live probe.

