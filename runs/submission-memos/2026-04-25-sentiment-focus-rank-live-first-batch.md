# 2026-04-25 Sentiment Focus Rank Live First Batch

- Re-check time: `2026-04-25 13:36 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN Simulate page plus official Data Explorer searches and project docs
- Scope: `sentiment_focus_rank`
- Family: `sentiment_focus_rank`

## Decision

- Freeze `sentiment_focus_rank` for the current budget.
- Do not spend more budget on sign flips, lookback tweaks, smoothing, or group-axis tweaks around this exact field family.
- Rotate the next official budget away from this Sentiment focus-rank lane.

## Official Evidence

- Field search pack:
  - `runs/field-search-packs/2026-04-25-sentiment-focus-rank.md`
- Expression family:
  - `runs/expression-families/2026-04-25-sentiment-focus-rank.md`
- Batch capture:
  - `runs/simulation-captures/2026-04-25-sentiment-focus-rank-batch-01.json`

## Field Facts

- `snt1_d1_dynamicfocusrank`
  - dataset/category: `sentiment1` / `Research Sentiment Data`
  - `USA / TOP3000 / D1`
  - coverage `56.51%`
  - date coverage `100%`
  - type `MATRIX`
  - visible users `291`
  - visible alphas `1,866`
- `snt1_d1_stockrank`
  - dataset/category: `sentiment1` / `Research Sentiment Data`
  - `USA / TOP3000 / D1`
  - coverage `56.72%`
  - date coverage `100%`
  - type `MATRIX`
  - visible users `226`
  - visible alphas `2,142`
- `snt1_d1_fundamentalfocusrank`
  - dataset/category: `sentiment1` / `Research Sentiment Data`
  - `USA / TOP3000 / D1`
  - coverage `56.84%`
  - date coverage `100%`
  - type `MATRIX`
  - visible users `234`
  - visible alphas `2,505`
- `snt1_cored1_score`
  - dataset/category: `sentiment1` / `Research Sentiment Data`
  - `USA / TOP3000 / D1`
  - coverage `63.29%`
  - date coverage `100%`
  - type `MATRIX`
  - visible users `540`
  - visible alphas `3,731`

## Batch Result

- Baseline `sentiment_focus_rank_baseline`
  - expression: `snt1_d1_dynamicfocusrank`
  - visible aggregate result: `Sharpe 0.13 / Fitness 0.04 / Turnover 9.07% / Returns 1.20% / Drawdown 21.73% / Margin 2.64‱`

## Why This Stops Here

- The baseline is positive but too weak to justify a same-family expansion budget.
- The planned follow-up family shape was only field swaps among close Sentiment siblings, which would be cosmetic rather than genuinely new.
- No sign-flip control is warranted here because the baseline is not negative.
- The family does not clear the continuation floor, so more polishing would be wasted budget.

## Next Minimal Experiment

- Do not continue this Sentiment focus-rank lane.
- Rotate to a genuinely different family source outside the frozen Model, analyst, cashflow, operating-income, event-news, and Sentiment focus-rank lanes.
- Best next jump from the current queue: the options / `call_breakeven_60` branch, if an orthogonal live family is needed next.

## Status

- Family state: `freeze`
- Portfolio posture: `rotate`
- Batch posture: `complete`
