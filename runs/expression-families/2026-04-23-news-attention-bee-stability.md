# News Attention Bee Stability Expression Family

## Metadata

- Date: `2026-04-23`
- Topic: `news_attention_bee_stability`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

Company-specific news sentiment around earnings growth may be more stable than generic buzz and deserves a slow, readable smoothing sweep before any field replacement.

## Confirmed Or Assumed Inputs

- Confirmed platform fields:
  - `nws18_bee`
  - `industry`
- Equivalent fallback fields:
  - `nws18_qcm`
  - `nws18_relevance`
  - `nws18_nip`
- Unconfirmed assumptions:
  - A 63d smoothing window is a sensible starting ridge.
  - Window changes should be tested before changing the field.
  - `industry` neutralization is the cleanest first grouping choice.

## Baseline Expression

```text
group_rank(ts_mean(nws18_bee, 63), industry)
```

## Variant 1

- Goal:
  Test whether a faster smoothing window reacts better to fresh news flow.
- Main lever:
  Reduce the smoothing window from `63` to `21`.

```text
group_rank(ts_mean(nws18_bee, 21), industry)
```

## Variant 2

- Goal:
  Test whether heavier smoothing improves stability and Fitness.
- Main lever:
  Increase the smoothing window from `63` to `126`.

```text
group_rank(ts_mean(nws18_bee, 126), industry)
```

## Variant 3

- Goal:
  Test whether very slow smoothing changes the family enough to improve the test-period view.
- Main lever:
  Increase the smoothing window from `63` to `252`.

```text
group_rank(ts_mean(nws18_bee, 252), industry)
```

## Expected First Failure

- Sharpe:
  The sentiment-growth signal may still be too weak after smoothing.
- Fitness:
  Crowding or weak directional edge may remain the first bottleneck.
- Turnover:
  Faster windows could still be too active.
- Weight:
  Concentration may show up if only a narrow subset of names carries the useful signal.
- Sub-universe:
  Still unknown until real simulation results and testing status evidence appear.
- Self-correlation:
  Unknown until live checks exist.

## Optimization Order

1. Keep one field fixed and sweep the smoothing window first.
2. Only if the 63d ridge fails should the lane branch to `nws18_qcm`, `nws18_relevance`, or `nws18_nip`.
3. If the full window sweep is weak, switch to a different field family in the next cycle instead of adding operator soup.

## Next Simulation Batch

- Baseline:
  `group_rank(ts_mean(nws18_bee, 63), industry)`
- Variant 1:
  `group_rank(ts_mean(nws18_bee, 21), industry)`
- Variant 2:
  `group_rank(ts_mean(nws18_bee, 126), industry)`
- Variant 3:
  `group_rank(ts_mean(nws18_bee, 252), industry)`
