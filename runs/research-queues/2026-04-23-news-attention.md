# News Attention Research Queue

## Status

- Current qcm branch: kill
- New live family: news attention, centered on `nws18_bee` but scored locally toward `nws18_relevance` and `nws18_qcm`
- Current posture: `frozen`

## Official Field Check

- `nws18_bee`: news sentiment specializing in growth of earnings
- `nws18_qcm`: news sentiment of relevant news with high confidence
- `nws18_relevance`: relevance of news to the company
- `nws18_nip`: degree of impact of the news

## Local Mining Result

- Candidate pool generated from `runs/expression-families/2026-04-24-news-attention-relevance-subindustry.md`
- Total local candidates: 81
- The local scorecard favored a 63d `subindustry` anchor on `nws18_relevance`, with `nws18_qcm` as the closest control
- The plain `nws18_bee` baseline stayed below the local keep threshold, so it is not the first live batch

## Recommended Next Batch

1. none; the family is frozen after negative partial tests and the duplicate live run was canceled
2. none

## Follow-On Rule

- Do not allocate more batch budget to this lane unless a new official evidence source changes the freeze decision.
- If a future live recheck ever reopens the family, start again from the frozen docs and re-validate the operator compatibility first.
