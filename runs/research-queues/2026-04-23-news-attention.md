# News Attention Research Queue

## Status

- Current qcm branch: kill
- New live family: news attention, centered on `nws18_bee` but scored locally toward `nws18_relevance` and `nws18_qcm`

## Official Field Check

- `nws18_bee`: news sentiment specializing in growth of earnings
- `nws18_qcm`: news sentiment of relevant news with high confidence
- `nws18_relevance`: relevance of news to the company
- `nws18_nip`: degree of impact of the news

## Local Mining Result

- Candidate pool generated from `runs/expression-families/2026-04-23-news-attention-bee-stability.md`
- Total local candidates: 81
- The local scorecard favored a 63d `subindustry` anchor on `nws18_relevance`, with `nws18_qcm` as the closest control
- The plain `nws18_bee` baseline stayed below the local keep threshold, so it is not the first live batch

## Recommended Next Batch

1. `group_rank(ts_mean(nws18_relevance, 63), subindustry)`
2. `group_rank(ts_mean(nws18_qcm, 63), subindustry)`

## Follow-On Rule

- If the relevance baseline holds up better than qcm, keep the field fixed and sweep the window next.
- If both look weak, branch to `nws18_nip` or drop the news family quickly.
