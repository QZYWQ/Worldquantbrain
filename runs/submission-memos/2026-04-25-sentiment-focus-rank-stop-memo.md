# 2026-04-25 Sentiment Focus Rank Stop Memo

## Decision

- Stop `sentiment_focus_rank`.
- Freeze the family for the current budget.
- Do not reopen this lane for more sign, lookback, smoothing, or grouping polish.

## Why

- The first official live read was too weak to justify a full `1 baseline + 3 variants` batch.
- The baseline is positive, so sign-flip control is not the issue.
- The only obvious next moves are cosmetic field swaps inside the same Sentiment subfamily.
- That is not a genuinely new family advance, so it should not receive more budget.

## Field Facts

- `snt1_d1_dynamicfocusrank` — `sentiment1` / `Research Sentiment Data`, `MATRIX`, coverage `56.51%`, date coverage `100%`, visible users `291`, visible alphas `1,866`
- `snt1_d1_stockrank` — `sentiment1` / `Research Sentiment Data`, `MATRIX`, coverage `56.72%`, date coverage `100%`, visible users `226`, visible alphas `2,142`
- `snt1_d1_fundamentalfocusrank` — `sentiment1` / `Research Sentiment Data`, `MATRIX`, coverage `56.84%`, date coverage `100%`, visible users `234`, visible alphas `2,505`
- `snt1_cored1_score` — `sentiment1` / `Research Sentiment Data`, `MATRIX`, coverage `63.29%`, date coverage `100%`, visible users `540`, visible alphas `3,731`

## Evidence

- `runs/field-search-packs/2026-04-25-sentiment-focus-rank.md`
- `runs/expression-families/2026-04-25-sentiment-focus-rank.md`
- `runs/simulation-captures/2026-04-25-sentiment-focus-rank-batch-01.json`
- `runs/submission-memos/2026-04-25-sentiment-focus-rank-live-first-batch.md`

## Next Step

- Rotate the next official budget away from this Sentiment focus-rank branch and into a genuinely different field source.
- Do not reopen the frozen Model, analyst, cashflow, operating-income, or event-news lanes.
- Best next jump from the current queue: the options / `call_breakeven_60` branch.

## Status

- `freeze`
- `rotate`
