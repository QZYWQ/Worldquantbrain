# Operating Income History Position Follow-up Expression Family

## Metadata

- Date: `2026-04-21`
- Topic: `operating_income_history_position_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/simulation-captures/2026-04-21-operating-income-follow-up-batch-03.json`
  - `./runs/field-search-packs/2026-04-21-sales-delta-fundamental.md`

## Hypothesis

The best improvement came from ranking current operating income against its own history instead of ranking slow deltas, so the next batch should test whether the win came from the raw `252d` history window itself or from the more general idea of profitability history position.

## Confirmed Or Assumed Inputs

- Confirmed platform field:
  - `operating_income`
- Confirmed neutralization:
  - `industry`
- Assumptions to test:
  - `252d` may be near the right memory length, but shorter and longer history windows could still improve Fitness.
  - Mild smoothing of the raw field may help stability without destroying the profitability-state signal.

## Baseline Expression

```text
group_rank(ts_rank(operating_income, 252), industry)
```

## Variant 1

- Goal:
  Test whether a shorter history window reacts better to newer profitability regime changes.
- Main lever:
  History window from `252` to `126`.

```text
group_rank(ts_rank(operating_income, 126), industry)
```

## Variant 2

- Goal:
  Test whether a slower history window produces a more persistent profitability-state ranking.
- Main lever:
  History window from `252` to `504`.

```text
group_rank(ts_rank(operating_income, 504), industry)
```

## Variant 3

- Goal:
  Test whether slight smoothing of the raw profitability field improves robustness before the history-position rank.
- Main lever:
  Add `ts_mean(..., 63)` before the `252d` history rank.

```text
group_rank(ts_rank(ts_mean(operating_income, 63), 252), industry)
```

## Expected First Failure

- Sharpe:
  The raw history-position branch is stronger, but it may still plateau below the true submission floor.
- Fitness:
  This remains the key live bottleneck because even the new winner only reached `0.73`.
- Turnover:
  Turnover is still acceptable, so the next batch should not trade Sharpe away just to go slower.
- Weight:
  Sparse `fundamental6` coverage can still create concentration risk even when the signal quality improves.
- Sub-universe:
  Still structurally risky because the verified field family only showed `50%` coverage on the official Data page.
- Self-correlation:
  Unknown until real check evidence exists.

## Optimization Order

1. Sweep the operating-income history-position window before touching neutralization or adding more operators.
2. Use only one smoothed-field control; do not add multiple cosmetic transforms in the same round.
3. If none of these variants beats the `252d` history-position baseline materially, stop polishing this family and branch to a new non-analyst lane instead of forcing it.
