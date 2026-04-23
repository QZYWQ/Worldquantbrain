# Fundamental / Model Slow Ratio Follow-up Expression Family

## Metadata

- Date: `2026-04-23`
- Topic: `fundamental_model_slow_ratio_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-catalog.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/decision-notes.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/knowledge-link-map.md`

## Hypothesis

Net income scaled by market cap should behave like a slow value / quality ratio and compare more cleanly across peers than a raw level. The forum crawl repeats ratio form, industry grouping, and a long comparison frame for this family. Model fields stay as a secondary backup for the same slow-ratio shape.

## Confirmed Or Assumed Inputs

- Confirmed forum-backed fields:
  - `net_income`
  - `market_cap`
  - `mdl110_score`
  - `mdl110_value`
  - `mdl_analyst_sentiment`
- Confirmed grouping:
  - `industry`
  - `subindustry`
- Assumptions to test:
  - `subindustry` may be the best first grouping for the strongest anchor.
  - `63d` smoothing is a useful small-window baseline.
  - `72d`, `84d`, `90d`, and `126d` are the smallest nearby window controls worth checking first.
  - Model-data ratios should stay secondary to the net-income ratio.

## Baseline Expression

```text
ts_rank(group_rank(ts_mean(net_income / market_cap, 63), subindustry), 252)
```

## Variant 1

- Goal:
  Compare the direct subindustry anchor against the 63d smoothed baseline.
- Main lever:
  Remove the `ts_mean` layer.

```text
ts_rank(group_rank(net_income / market_cap, subindustry), 252)
```

## Variant 2

- Goal:
  Test the same direct ratio at the broader industry group.
- Main lever:
  Swap `subindustry` for `industry`.

```text
ts_rank(group_rank(net_income / market_cap, industry), 252)
```

## Variant 3

- Goal:
  Test whether the 63d smoother is still useful at the broader group level.
- Main lever:
  Keep the smoother and switch to `industry`.

```text
ts_rank(group_rank(ts_mean(net_income / market_cap, 63), industry), 252)
```

## Variant 4

- Goal:
  Check a slightly faster smoother for the same group structure.
- Main lever:
  Replace `63` with `72`.

```text
ts_rank(group_rank(ts_mean(net_income / market_cap, 72), industry), 252)
```

## Variant 5

- Goal:
  Check a slightly slower smoother for the same group structure.
- Main lever:
  Replace `63` with `84`.

```text
ts_rank(group_rank(ts_mean(net_income / market_cap, 84), industry), 252)
```

## Variant 6

- Goal:
  Check a slower smoother that still sits near the same slow-ratio frame.
- Main lever:
  Replace `63` with `90`.

```text
ts_rank(group_rank(ts_mean(net_income / market_cap, 90), industry), 252)
```

## Variant 7

- Goal:
  Check the slowest of the nearby compact windows before moving wider.
- Main lever:
  Replace `63` with `126`.

```text
ts_rank(group_rank(ts_mean(net_income / market_cap, 126), industry), 252)
```

## Variant 8

- Goal:
  See whether a simpler cross-sectional form is enough without the 252d history rank.
- Main lever:
  Remove the outer `ts_rank` layer.

```text
group_rank(ts_mean(net_income / market_cap, 63), industry)
```

## Variant 9

- Goal:
  Compare the same simplified form at subindustry level.
- Main lever:
  Swap `industry` for `subindustry`.

```text
group_rank(ts_mean(net_income / market_cap, 63), subindustry)
```

## Variant 10

- Goal:
  Use the model score as the first backup ratio shape.
- Main lever:
  Replace the numerator with `mdl110_score`.

```text
ts_rank(group_rank(mdl110_score / market_cap, industry), 252)
```

## Variant 11

- Goal:
  Check the same model-score backup at subindustry level.
- Main lever:
  Swap `industry` for `subindustry`.

```text
ts_rank(group_rank(mdl110_score / market_cap, subindustry), 252)
```

## Variant 12

- Goal:
  Check whether the model-score backup benefits from the same 63d smoothing.
- Main lever:
  Add `ts_mean` before the rank.

```text
ts_rank(group_rank(ts_mean(mdl110_score / market_cap, 63), industry), 252)
```

## Variant 13

- Goal:
  Check a slower model-score smoother.
- Main lever:
  Replace `63` with `126`.

```text
ts_rank(group_rank(ts_mean(mdl110_score / market_cap, 126), industry), 252)
```

## Variant 14

- Goal:
  Try the model-value field as a second backup ratio.
- Main lever:
  Replace the numerator with `mdl110_value`.

```text
ts_rank(group_rank(mdl110_value / market_cap, industry), 252)
```

## Variant 15

- Goal:
  Try the analyst-sentiment model field in the same slow-ratio shape.
- Main lever:
  Replace the numerator with `mdl_analyst_sentiment`.

```text
ts_rank(group_rank(mdl_analyst_sentiment / market_cap, industry), 252)
```

## Variant 16

- Goal:
  Use the model-value field with the same 63d smoothing.
- Main lever:
  Add `ts_mean` before the rank.

```text
ts_rank(group_rank(ts_mean(mdl110_value / market_cap, 63), industry), 252)
```

## Variant 17

- Goal:
  See whether the model-score backup can survive without the outer history rank.
- Main lever:
  Remove the outer `ts_rank` layer.

```text
group_rank(ts_mean(mdl110_score / market_cap, 63), industry)
```

## Variant 18

- Goal:
  See whether the model-value backup can survive without the outer history rank.
- Main lever:
  Remove the outer `ts_rank` layer.

```text
group_rank(ts_mean(mdl110_value / market_cap, 63), industry)
```

## Variant 19

- Goal:
  Use a broader-group model-score backup without extra smoothing.
- Main lever:
  Swap `industry` for `subindustry`.

```text
ts_rank(group_rank(mdl110_score / market_cap, subindustry), 252)
```

## Variant 20

- Goal:
  Keep the net-income ratio in the simpler cross-sectional form at the broader group level.
- Main lever:
  Remove the outer `ts_rank` layer.

```text
group_rank(ts_mean(net_income / market_cap, 63), subindustry)
```

## Optimization Order

1. Compare the direct `net_income / market_cap` anchor against the 63d smoothed baseline.
2. Keep `subindustry` and `industry` side by side so the group choice is explicit.
3. Check `72d / 84d / 90d / 126d` only after the 63d frame is understood.
4. Keep `mdl110_score` and `mdl110_value` as backup fields rather than the first choice.

## Next Simulation Batch

- Baseline:
  `ts_rank(group_rank(ts_mean(net_income / market_cap, 63), subindustry), 252)`
- Variant 1:
  `ts_rank(group_rank(net_income / market_cap, subindustry), 252)`
- Variant 2:
  `ts_rank(group_rank(net_income / market_cap, industry), 252)`
- Variant 3:
  `ts_rank(group_rank(ts_mean(net_income / market_cap, 63), industry), 252)`
- Variant 4:
  `ts_rank(group_rank(ts_mean(net_income / market_cap, 84), industry), 252)`
- Variant 5:
  `ts_rank(group_rank(mdl110_score / market_cap, industry), 252)`

## Local Mining Snapshot

- Candidate pool size: `1264`
- Scorecard input size after local filtering: `540`
- Keep / review split: `31 keep`, `509 review`
- Highest local score: `ts_rank(group_rank(mdl110_value / market_cap, subindustry), 63)` at `62.84`
- Strong secondary ridge: `ts_rank(group_rank(mdl110_score / market_cap, industry), 90)` at `62.02`
- Clean forum anchor still in range: `ts_rank(group_rank(net_income / market_cap, subindustry), 90)` at `58.24`
- Local takeaway: the family is still worth a branch, and the model-data ratio ridge currently looks strongest in the local scorecard.
