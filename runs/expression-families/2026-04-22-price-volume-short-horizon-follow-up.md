# Expression Family

## Metadata

- Date: 2026-04-22
- Topic: price_volume_short_horizon_follow_up
- Region: USA
- Universe: TOP3000
- Delay: 1

## Hypothesis

Short-horizon price action and volume-aware pressure can produce an interpretable industry-relative alpha.

## Confirmed Or Assumed Inputs

- Confirmed platform fields: `close`, `high`, `low`, `open`, `volume`, `vwap`, `adv20`, `returns`, `industry`
- Equivalent fallback fields: `close`, `high`, `open`, `volume`
- Unconfirmed assumptions: none for the first batch beyond standard matrix compatibility

## Baseline Expression

```text
group_rank(ts_zscore(ts_sum(close - ts_delay(close, 1), 20), 20), industry)
```

## Variant 1

- Goal: test a simpler volume-aware pressure proxy after the recent-high template hit an operator limit on this account
- Main lever: compare close against vwap instead of relying on `ts_max`

```text
group_rank(ts_zscore(close - vwap, 10), industry)
```

## Variant 2

- Goal: test volume-confirmed price pressure
- Main lever: combine price spread with volume expansion and a short-horizon rank term

```text
group_rank(ts_zscore(multiply(ts_sum(volume * (close - open), 10), ts_rank(close - open, 10)), 20), industry)
```

## Variant 3

- Goal: test the cheapest direct-control momentum branch
- Main lever: simplify the signal to raw short-horizon delta with a time-series rank

```text
group_rank(ts_rank(ts_delta(close, 3), 20), industry)
```

## Expected First Failure

- Sharpe: may be crowded if the raw price-action thesis is too common
- Fitness: may lag if turnover stays high without enough edge
- Turnover: likely elevated on the direct momentum branch
- Weight: likely manageable with industry grouping, but still watch concentration
- Sub-universe: may weaken if the signal is concentrated in the liquid names only
- Self-correlation: likely the first bottleneck if the branch is too close to standard momentum
- Operator availability: some forum-style templates may not be directly runnable here, so keep a supported fallback ready

## Optimization Order

1. Compare the accessible pressure proxy vs direct momentum before adding any more operators
2. If turnover is too high, smooth the raw price move rather than adding new factors
3. If the branch survives, use volume confirmation as the next lever

## Current Live Probe

- Simulation 19 tested the smoothed momentum baseline:

```text
group_rank(ts_zscore(ts_sum(close - ts_delay(close, 1), 20), 20), industry)
```

- IS summary:
  `Sharpe -0.87 / Fitness -0.39 / Turnover 28.27% / Returns -5.80% / Drawdown 28.29% / Margin -4.10‱`
- Year breakdown stayed negative in every year shown, with Sharpe ranging from `-1.53` in 2019 to `-0.26` in 2022.
- No visible `Check Submission` evidence or non-null `subuniverse_pass` appeared, and `Submit Alpha` stayed disabled.

## Variant 3 Update

- Simulation 19 tested the direct-momentum fallback:

```text
group_rank(ts_rank(ts_delta(close, 3), 20), industry)
```

- IS summary:
  `Sharpe -1.56 / Fitness -0.70 / Turnover 55.70% / Returns -11.26% / Drawdown 49.54% / Margin -4.04‱`
- The direct-control momentum branch is materially worse than the smoothed baseline and does not rescue the family.
- No visible `Check Submission` evidence or non-null `subuniverse_pass` appeared, and `Submit Alpha` stayed disabled.

## Decision

- Kill the price-volume short-horizon family.
- Keep the baseline and direct-momentum captures as negative controls only.
- Branch the next live work back to a stronger family rather than polishing this lane further.
