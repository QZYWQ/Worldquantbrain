# Operating Income Delta Follow-up Expression Family

## Metadata

- Date: `2026-04-21`
- Topic: `operating_income_delta_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/simulation-captures/2026-04-21-sales-delta-fundamental-batch-02.json`
  - `./runs/field-search-packs/2026-04-21-sales-delta-fundamental.md`

## Hypothesis

The first fundamentals branch only became meaningfully better after shifting from top-line delta to slow operating-income delta, so the next real batch should test whether this strength comes from the 126d profitability-change representation itself or from a nearby slow-history variant.

## Confirmed Or Assumed Inputs

- Confirmed platform field:
  - `operating_income`
- Confirmed neutralization:
  - `industry`
- Assumptions to test:
  - `126d` may already be near the right horizon, but a slower `252d` control is still worth one check.
  - A history-position representation can improve Fitness without destroying turnover.

## Baseline Expression

```text
group_rank(ts_delta(operating_income, 126), industry)
```

## Variant 1

- Goal:
  Test whether the stronger operating-income branch still prefers an even slower horizon.
- Main lever:
  Horizon from `126` to `252`.

```text
group_rank(ts_delta(operating_income, 252), industry)
```

## Variant 2

- Goal:
  Reduce noisy absolute jumps by ranking the `126d` delta against its own 1-year history before the cross-sectional industry rank.
- Main lever:
  Add `ts_rank(..., 252)` around the winning `126d` delta.

```text
group_rank(ts_rank(ts_delta(operating_income, 126), 252), industry)
```

## Variant 3

- Goal:
  Branch from pure delta into the earlier fallback idea of an operating-income history-position signal.
- Main lever:
  Replace `ts_delta` with direct `ts_rank` on the raw field.

```text
group_rank(ts_rank(operating_income, 252), industry)
```

## Expected First Failure

- Sharpe:
  The profitability move may still be too slow and cyclical to clear the candidate threshold consistently.
- Fitness:
  This is still the main live bottleneck because the strongest batch-2 line only reached `0.52`.
- Turnover:
  Turnover is currently healthy, so the next batch should not optimize for lower turnover first.
- Weight:
  `fundamental6` sparsity can still concentrate the effective book even when the aggregate IS looks better.
- Sub-universe:
  Still structurally risky because the confirmed field family only showed `50%` coverage on the official Data page.
- Self-correlation:
  Unknown until real check evidence exists.

## Optimization Order

1. Re-test the winning operating-income branch with one slower-horizon control and two history-position variants.
2. Keep the next batch to four lines total and compare against the live baseline rather than opening a new unrelated family.
3. If none of these variants materially beat `group_rank(ts_delta(operating_income, 126), industry)`, stop polishing this sparse fundamentals family and branch away instead of adding operator soup.
