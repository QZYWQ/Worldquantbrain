# Operating Income Smoothed History Position Follow-up Expression Family

## Metadata

- Date: `2026-04-21`
- Topic: `operating_income_smoothed_history_position_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/simulation-captures/2026-04-21-operating-income-history-position-batch-04.json`
  - `./runs/expression-families/2026-04-21-operating-income-history-position-follow-up.md`

## Hypothesis

The history-position branch improved again once the raw `operating_income` field was lightly smoothed before the `252d` historical rank, so the next batch should isolate whether the gain came mainly from the `63d` smoothing choice, from the interaction with the `252d` rank window, or from both together.

## Confirmed Or Assumed Inputs

- Confirmed platform field:
  - `operating_income`
- Confirmed neutralization:
  - `industry`
- Assumptions to test:
  - The branch may still want moderate smoothing, but `63d` is unlikely to be the only usable smoothing length.
  - A slower rank window may combine well with smoothing because the raw `504d` branch improved Fitness and margin.
  - Over-smoothing could flatten the signal and give back Sharpe even if turnover falls.

## Baseline Expression

```text
group_rank(ts_rank(ts_mean(operating_income, 63), 252), industry)
```

## Variant 1

- Goal:
  Test whether lighter smoothing keeps the new edge while reacting faster to profitability regime shifts.
- Main lever:
  Reduce the smoothing window from `63` to `21`.

```text
group_rank(ts_rank(ts_mean(operating_income, 21), 252), industry)
```

## Variant 2

- Goal:
  Test whether heavier smoothing improves stability and Fitness further without killing the signal.
- Main lever:
  Increase the smoothing window from `63` to `126`.

```text
group_rank(ts_rank(ts_mean(operating_income, 126), 252), industry)
```

## Variant 3

- Goal:
  Test whether the branch gets an extra lift from combining the winning `63d` smoothing with a slower historical-rank window.
- Main lever:
  Keep `ts_mean(..., 63)` and extend the history rank from `252` to `504`.

```text
group_rank(ts_rank(ts_mean(operating_income, 63), 504), industry)
```

## Expected First Failure

- Sharpe:
  The current winner is strong enough to justify one more focused batch, but a bad smoothing choice could quickly flatten the edge.
- Fitness:
  This remains the live bottleneck even after the jump to `0.87`, so the next round should prioritize robustness over cosmetic Sharpe chasing.
- Turnover:
  Turnover is now healthier, which means the next batch can spend a little turnover budget if it buys clear Fitness.
- Weight:
  Sparse `fundamental6` coverage still leaves concentration risk unresolved until official submission-style checks are visible.
- Sub-universe:
  Still structurally risky because no non-null official subuniverse evidence has appeared yet.
- Self-correlation:
  Unknown until real check evidence exists.

## Optimization Order

1. Sweep smoothing strength and one slower history-rank combination before changing neutralization or adding more operators.
2. Keep the family interpretable; do not stack extra transforms on top of smoothing until this focused batch settles the stability question.
3. If the best smoothed follow-up still cannot move beyond `Needs Improvement` with a materially higher Fitness, then stop polishing this field family and branch to the next non-analyst lane.
