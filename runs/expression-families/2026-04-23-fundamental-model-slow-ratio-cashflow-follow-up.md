# Fundamental / Model Slow Ratio Cashflow Follow-up Expression Family

## Metadata

- Date: `2026-04-23`
- Topic: `fundamental_model_slow_ratio_cashflow_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/raw/pages/hc-en-us-community-posts-39411791834647-8d78a1331f.txt`
  - `./runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`

## Hypothesis

The forum lane frames `cashflow / cap` and `cashflow / assets` as the same slow-ratio family. On this account, the cap-normalized version is still alive but weak; the assets-normalized version looks invalid here.

## Confirmed Or Assumed Inputs

- `cashflow` coverage: `50%`
- `assets` coverage: `50%`
- `cap` coverage: `100%`
- `subindustry` is the current group axis
- The forum raw thread explicitly places `cashflow / cap` and `cashflow / assets` in the same slow-ratio lane.

## Live Evidence

- `ts_rank(group_rank(cashflow / cap, subindustry), 90)`
  - `Sharpe 0.44 / Fitness 0.15 / Turnover 10.69% / Returns 1.41% / Drawdown 5.37% / Margin 2.64‱`
- `ts_rank(group_rank(cashflow / cap, industry), 90)`
  - `Needs Improvement`
  - `Sharpe 0.40 / Fitness 0.13 / Turnover 13.49% / Returns 1.36% / Drawdown 6.40% / Margin 2.02‱`
- `ts_rank(group_rank(cashflow / cap, subindustry), 63)`
  - `Needs Improvement`
  - `Sharpe 0.34 / Fitness 0.10 / Turnover 12.97% / Returns 1.12% / Drawdown 5.23% / Margin 1.73‱`
- `ts_rank(group_rank(cashflow / cap, subindustry), 126)`
  - `Needs Improvement`
  - `Sharpe 0.28 / Fitness 0.08 / Turnover 8.90% / Returns 0.91% / Drawdown 5.35% / Margin 2.05‱`
- `ts_rank(group_rank(cashflow / assets, subindustry), 90)`
  - `Needs Improvement`
  - `Sharpe -0.13 / Fitness -0.02 / Turnover 9.45% / Returns -0.31% / Drawdown 3.95% / Margin -0.65‱`
  - Visible label: `Single Data Set Alpha`

## Decision

- Branch: `cashflow / cap` only; `subindustry` remains the stronger anchor than `industry`.
- Drop: `cashflow / assets`.
- Do not expand into new numerators or a wider family until the cap lane proves sturdier.

## Baseline Expression

```text
ts_rank(group_rank(cashflow / cap, subindustry), 90)
```

## Variant 1

- Goal:
  Keep the same slow-ratio lane but check the recorded 63d control.
- Main lever:
  Window axis from `90` to `63`.

```text
ts_rank(group_rank(cashflow / cap, subindustry), 63)
```

## Variant 2

- Goal:
  Check the nearby 84d window.
- Main lever:
  Window axis from `90` to `84`.

```text
ts_rank(group_rank(cashflow / cap, subindustry), 84)
```

## Variant 3

- Goal:
  Check the slower 126d window.
- Main lever:
  Window axis from `90` to `126`.

```text
ts_rank(group_rank(cashflow / cap, subindustry), 126)
```

## Next Smallest Test Set

- Keep the same `ts_rank(group_rank(...))` stack.
- The 63d and 126d probes are now recorded and weaker than the 90d anchor.
- Next test: `ts_rank(group_rank(ts_mean(cashflow / cap, 63), subindustry), 90)`.
- Keep `industry` as a weak control and do not retest assets.
