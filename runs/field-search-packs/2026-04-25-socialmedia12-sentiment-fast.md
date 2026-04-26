# Social Media Sentiment Fast Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `socialmedia12-sentiment-fast`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

The `socialmedia12` sentiment family may carry a cleaner, genuinely new signal than the frozen analyst, model rerating, and event/news lanes because it is a different source of public sentiment rather than a recycled consensus or earnings proxy. The fastest matrix field, `scl12_sentiment_fast_d1`, is the best first probe because it has full date coverage, high USA/TOP3000 coverage, and far lower crowding than the broad `scl12_sentiment` sibling.

## Why This Could Matter

- This is a new source relative to the frozen analyst / focus / rerating lanes.
- The official Data Explorer shows the field in `USA / D1 / TOP3000` with `98%` coverage and `100%` date coverage.
- Crowding is materially lower than the broad social-media sibling, so this is not just a cosmetic re-skin of the crowded sentiment lane.
- The field is a `Matrix`, so the first pass can stay interpretable and cheap.

## Data Explorer Search Terms

- Primary terms: `social media sentiment`, `sentiment fast`, `scl12_sentiment_fast_d1`
- Synonyms: `socialmedia12`, `fast sentiment`, `sentiment matrix`
- Abbreviations: `scl12`, `sentvec`, `fast_d1`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `scl12_sentiment_fast_d1` | `socialmedia12` / `Sentiment Data for Equity` | Best first baseline; a fast daily sentiment matrix with low crowding | Live Data Explorer: `Matrix`, `97.56%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live Data Explorer: `111` visible users, `125` visible alphas |
| `scl12_sentiment` | `socialmedia12` / `Sentiment Data for Equity` | Broader sibling control; useful to compare against the fast field without changing the source family | Live Data Explorer: `Matrix`, `100%` coverage, `100%` date coverage | Live Data Explorer: `1,182` visible users, `3,230` visible alphas |
| `scl12_alltype_sentvec` | `socialmedia12` / `Sentiment Data for Equity` | Lower-crowding vector sibling; backup if the matrix field is flat | Live Data Explorer: `Vector`, `95.25%` coverage, `100%` date coverage | Live Data Explorer: `37` visible users, `68` visible alphas |

## Coverage And Quality Checks

- Coverage: `scl12_sentiment_fast_d1` is usable for a first official batch, with `97.56%` coverage and `100%` date coverage on the live page.
- Missingness: coverage is high but not perfect, so the first batch still needs to watch for concentration or sparse-name behavior.
- Region / delay compatibility: confirmed live on the official Data Explorer page under `USA / 1 / TOP3000`.
- Field type: the chosen first-pass field is `Matrix`.

## Baseline Expression Ideas

1. `scl12_sentiment_fast_d1`
2. `-scl12_sentiment_fast_d1`
3. `ts_rank(scl12_sentiment_fast_d1, 20)`

## Likely First Failure

- Sharpe: the field may be directionally real but too weak once the fast sentiment is neutralized.
- Fitness: crowding could suppress the edge even if the direction is sensible.
- Turnover: the raw daily field may be noisy, so turnover could be the first practical bottleneck.
- Weight: less likely to fail structurally because coverage is strong.
- Sub-universe: still needs the real official result because coverage is not full.
- Self-correlation: a real risk if the fast field mostly reproduces the broad `scl12_sentiment` sibling.

## Next Action

- Which field should be tried first? `scl12_sentiment_fast_d1`
- Which baseline expression should be simulated first? `scl12_sentiment_fast_d1`
- Which 2-3 same-family variants should follow? `-scl12_sentiment_fast_d1`, `ts_rank(scl12_sentiment_fast_d1, 20)`, `ts_rank(scl12_sentiment_fast_d1, 60)`

## Official Evidence

- Live Data Explorer search for `scl12_sentiment_fast_d1`: `https://platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=scl12_sentiment_fast_d1&universe=TOP3000`
- Live Data Explorer field page: `https://platform.worldquantbrain.com/data/data-fields/scl12_sentiment_fast_d1?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live API search response: `https://api.worldquantbrain.com/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=scl12_sentiment_fast_d1&universe=TOP3000`
- Saved live API inventory from the current browser session: `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`
