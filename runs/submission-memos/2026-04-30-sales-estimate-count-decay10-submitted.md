# Sales Estimate Count Decay10 Submission Memo

Date: 2026-04-30

## Status

- Submission status: user-reported submitted.
- Platform post-submit status: not separately rechecked in this memo.
- Do not continue optimizing this exact line unless fresh official evidence shows a submission problem.

## Submitted Alpha

```text
rank(ts_decay_linear(sales_estimate_count, 10))
```

- Alpha ID: `A1g6AlWg`
- Instrument Type: Equity
- Region: USA
- Universe: TOP3000
- Delay: 1
- Neutralization: Industry
- Pasteurization: On
- Max Trade: Off
- Max Position: Off

## Latest Official Pre-Submission Check Evidence

Source: official `/alphas/A1g6AlWg/check` result observed on 2026-04-30.

- Sharpe: 1.70
- Fitness: 1.03
- Returns: 4.58%
- Turnover: 3.49%
- Drawdown: 2.71%
- Margin: 0.002626
- Long Count: 1549
- Short Count: 1509
- Sharpe gate: PASS
- Fitness gate: PASS
- Turnover gates: PASS
- Concentrated weight: PASS
- Sub-universe Sharpe: PASS, value 0.91, limit 0.74
- Self-correlation: PASS, value 0.0771, limit 0.7
- Matches competition: PASS

## Backup Variant

```text
rank(ts_decay_linear(sales_estimate_count, 5))
```

- Alpha ID: `Vk2nAk3b`
- Also passed official checks.
- Slightly weaker than decay10 due to lower returns, higher turnover, higher drawdown, and lower sub-universe Sharpe.

## Family Decision

- Keep the submitted decay10 line locked for post-submit monitoring.
- Do not polish the original raw baseline or group-rank branch further:
  - `rank(ts_decay_linear(sales_estimate_count, 20))` failed Fitness.
  - `group_rank(ts_decay_linear(sales_estimate_count, 20), industry)` failed Fitness.
  - delta variants damaged Sharpe, Fitness, and Sub-universe.
- Next research should branch to a different interpretable family or a genuinely distinct analyst-estimate feature, not a cosmetic mutation of this submitted expression.
