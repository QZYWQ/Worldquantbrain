# Sentiment Buzz Stability Field Search Pack

## Metadata

- Date: `2026-04-20`
- Topic: `sentiment_buzz_stability`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Official page context: `platform.worldquantbrain.com/data/data-fields/scl12_buzz?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`

## Hypothesis

Stocks with persistently elevated relative sentiment volume may keep attracting attention and flow for longer than a one-day buzz spike, so a short stability window on buzz could rank continuation candidates better than raw single-day sentiment noise.

## Why This Could Matter

- Relative buzz is structurally different from the submitted analyst EPS family, so it is a cleaner low-correlation follow-up lane than another EPS clone.
- A stable multi-day buzz signal may capture attention persistence instead of one-off event spikes that reverse immediately.
- Full official coverage on the chosen field reduces the first-pass risk of a structural Sub-universe failure.

## Data Explorer Search Terms

- Primary terms: `buzz`, `relative sentiment volume`, `sentiment volume`
- Synonyms: `sentiment`, `social media`, `attention`
- Abbreviations: `scl12`, `snt`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `scl12_buzz` | `socialmedia12` / `Sentiment Data for Equity` | Cleanest confirmed primary field for persistent buzz; exact official field page shows `relative sentiment volume` | Official field page in this session: `Matrix`, `100%` coverage, `100%` date coverage in `USA / D1 / TOP3000` | High crowding risk: `19292` alphas on the official field page |
| `scl12_buzz_fast_d1` | `socialmedia12` / `Sentiment Data for Equity` | Faster sibling if the main field is too slow or too crowded | Official search result in this session: `Matrix`, `98%` coverage, `100%` date coverage | Lower visible alpha count than the main field: `102` alphas |
| `snt_buzz` | `socialmedia12` / `Sentiment Data for Equity` | Negative-relative-buzz alternative if the signed interpretation matters more than the generic buzz level | Official search result in this session: `Matrix`, `100%` coverage, `100%` date coverage | Still crowded, but lower than `scl12_buzz`: `8824` alphas |
| `snt_buzz_fast_d1` | `socialmedia12` / `Sentiment Data for Equity` | Faster signed-buzz fallback if the simple lane stalls | Official search result in this session: `Matrix`, `98%` coverage, `100%` date coverage | Much lighter usage than the slow signed field: `114` alphas |

## Coverage And Quality Checks

- Coverage:
  `scl12_buzz` is the strongest structural choice for the first batch because the official field page shows full `100%` coverage in the exact target setup.
- Missingness:
  No missingness warning is visible on the official field page, and the `100%` coverage display makes this lane structurally cleaner than the blocked analyst-disagreement branch.
- Region / delay compatibility:
  The official page was verified in this session under `USA / D1 / TOP3000`.
- Field type:
  `scl12_buzz` is confirmed as a `Matrix` field.

## Baseline Expression Ideas

1. `group_rank(ts_mean(scl12_buzz, 5), industry)`
2. `group_rank(ts_mean(scl12_buzz, 10), industry)`
3. `group_rank(ts_mean(scl12_buzz, 20), industry)`

## Likely First Failure

- Sharpe:
  The signal may be directionally real but already priced because the main field is widely used.
- Fitness:
  The biggest early robustness risk is crowding rather than missing data.
- Turnover:
  The shortest `5d` window is the main turnover risk if buzz spikes decay too fast.
- Weight:
  Lower structural risk than the analyst-disagreement branch because the chosen primary field shows full coverage.
- Sub-universe:
  Still needs real simulation evidence, but the full official coverage makes a hard Sub-universe failure less likely.
- Self-correlation:
  Most likely first hard bottleneck because `scl12_buzz` already has very high visible alpha usage.

## Next Action

- Which field should be tried first?
  `scl12_buzz`
- Which baseline expression should be simulated first?
  `group_rank(ts_mean(scl12_buzz, 5), industry)`
- Which 2-3 same-family variants should follow?
  `group_rank(ts_mean(scl12_buzz, 10), industry)`, `group_rank(ts_mean(scl12_buzz, 20), industry)`, and one unsmoothed control `group_rank(ts_rank(scl12_buzz, 10), industry)`.
