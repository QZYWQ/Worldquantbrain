# Social Media Sentiment Value Field Search Pack

## Metadata

- Date: `2026-04-25`
- Topic: `socialmedia8-sentiment-value`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

`socialmedia8` may still carry a usable direct sentiment signal even after the `socialmedia12` fast lane froze, because `snt_social_value` is a clean z-score sentiment field from a different dataset family, not a recycled analyst, model, or event proxy. The field is crowded, but it is simple, interpretable, and worth a minimal official probe before the lane is dismissed.

## Why This Could Matter

- This is a genuinely different sentiment source from the frozen `socialmedia12` lane.
- The live official Data Explorer page shows `snt_social_value` as a direct matrix field with full date coverage in `USA / D1 / TOP3000`.
- The field is simple enough to test without operator soup, which keeps the first batch cheap and interpretable.
- The dataset is broad enough to justify a first probe, but the crowding is high enough that the family still needs a real official read instead of optimism.

## Data Explorer Search Terms

- Primary terms: `social media`, `socialmedia8`, `snt_social_value`
- Synonyms: `social sentiment`, `z-score of sentiment`, `social value`
- Abbreviations: `snt_social`, `socialmedia8`

## Candidate Fields

| Field | Dataset | Why it might fit | Coverage notes | Crowding notes |
| --- | --- | --- | --- | --- |
| `snt_social_value` | `socialmedia8` / `Social Media Data for Equity` | Best first baseline; direct z-score sentiment field with a clean interpretation | Live Data Explorer: `Matrix`, `86%` coverage, `100%` date coverage, `USA / D1 / TOP3000` | Live Data Explorer: `4,855` visible alphas |
| `snt_social_volume` | `socialmedia8` / `Social Media Data for Equity` | Sibling control if the value field is flat or flips badly | Live Data Explorer: `Matrix`, `86%` coverage, `100%` date coverage | Live Data Explorer: `4,788` visible alphas |

## Coverage And Quality Checks

- Coverage: `snt_social_value` is usable for a first official batch, with `86%` coverage and `100%` date coverage on the live page.
- Missingness: coverage is materially lower than the fully covered fields, so concentration and sparse-name behavior still need watchfulness.
- Region / delay compatibility: confirmed live on the official Data Explorer page under `USA / 1 / TOP3000`.
- Field type: the chosen first-pass field is `Matrix`.

## Baseline Expression Ideas

1. `snt_social_value`
2. `-snt_social_value`
3. `ts_rank(snt_social_value, 20)`

## Likely First Failure

- Sharpe: the field may be too crowded to carry fresh edge on its own.
- Fitness: crowding / self-correlation is the main risk.
- Turnover: probably acceptable if the signal is real, but still worth checking.
- Weight: the field is broad enough that structural weight failure is less likely than in sparse event lanes.
- Sub-universe: still needs the real official result because coverage is not full.
- Self-correlation: the most likely first hard bottleneck.

## Next Action

- Which field should be tried first? `snt_social_value`
- Which baseline expression should be simulated first? `snt_social_value`
- Which 2-3 same-family variants should follow? `-snt_social_value`, `ts_rank(snt_social_value, 20)`, `ts_rank(snt_social_value, 60)`

## Official Evidence

- Live Data Explorer search for `snt_social_value`: `https://platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=snt_social_value&universe=TOP3000`
- Live Data Explorer field page: `https://platform.worldquantbrain.com/data/data-fields/snt_social_value?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
- Live Data Explorer search for `snt_social_volume`: `https://platform.worldquantbrain.com/data/search/data-fields?delay=1&instrumentType=EQUITY&limit=20&offset=0&region=USA&search=snt_social_volume&universe=TOP3000`
