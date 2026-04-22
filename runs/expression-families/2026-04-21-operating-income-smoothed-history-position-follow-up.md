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

## Batch 06 Update

- `84d` smoothing on the `504d` rank window became the new working baseline:
  `group_rank(ts_rank(ts_mean(operating_income, 84), 504), industry)`
- It improved the family to `Sharpe 1.25 / Fitness 0.96 / Turnover 2.98% / Returns 7.33% / Margin 49.23‱`.
- The lighter `21d` smoothing probe lagged the stronger anchors and did not change the branch decision.
- The family now looks like a `504d` history sweep centered around `84d` smoothing, not a `252d` history sweep centered on `63d`.

## Batch 07 Update

- `72d` smoothing became the highest-Sharpe probe in the 504-history sweep and tied the best Fitness with the control anchor:
  `group_rank(ts_rank(ts_mean(operating_income, 72), 504), industry)`
- `84d` remained the lowest-turnover balance point and is still the working control:
  `group_rank(ts_rank(ts_mean(operating_income, 84), 504), industry)`
- `96d` and `108d` both leaned toward cheaper turnover, but each gave back some Fitness versus the `72d`/`84d` ridge.
- The family now looks like a shallow ridge around `72d` to `84d` rather than a single sharp peak.

## Batch 08 Update

- The 504-history sweep tightened again and the live ridge shifted slightly left from the `84d` control.
- `78d` became the best visible probe in the batch:
  `group_rank(ts_rank(ts_mean(operating_income, 78), 504), industry)`
- `84d` remains the low-turnover control and the most stable anchor for the ridge:
  `group_rank(ts_rank(ts_mean(operating_income, 84), 504), industry)`
- `72d` stayed competitive on visible Sharpe/Fitness, but it gave back a bit of turnover and margin.
- `90d` drifted off the ridge and should be treated as a right-tail probe rather than the new center.

## Batch 09 Update

- `81d` smoothing did not improve the ridge and underperformed the current controls:
  `group_rank(ts_rank(ts_mean(operating_income, 81), 504), industry)`
- The visible IS summary landed at `Sharpe 0.96 / Fitness 0.63 / Turnover 2.92% / Returns 5.43% / Margin 37.23‱`.
- With the test period shown, the visible aggregate readout stayed negative and `Submit Alpha` remained disabled.
- No visible `Check Submission` evidence or non-null subuniverse verdict appeared for this probe.
- The `81d` point should not replace the `78d`/`84d` ridge anchors.

## Batch 10 Update

- The current live probe in Simulation 13 is the `78d` subindustry variant:
  `group_rank(ts_rank(ts_mean(operating_income, 78), 504), subindustry)`
- The visible IS summary improved to `Sharpe 0.98 / Fitness 0.62 / Turnover 2.88% / Returns 5.08% / Margin 35.24‱`.
- The TEST view remained negative at `Sharpe -0.29 / Fitness -0.09 / Turnover 2.54% / Returns -1.34% / Margin -10.54‱`.
- `IS Testing Status` still showed `4 PASS / 3 FAIL / 1 PENDING`, with `Check Submission` and `Submit Alpha` still disabled.
- This is a real backup result, not a submission-ready ridge.

## Batch 11 Update

- Simulation 19 is now the `63d` / `504d` operating-income smoothing probe:
  `group_rank(ts_rank(ts_mean(operating_income, 63), 504), industry)`
- IS summary:
  `Sharpe 1.23 / Fitness 0.93 / Turnover 3.28% / Returns 7.10% / Drawdown 8.31% / Margin 43.31‱`
- TEST summary:
  `Sharpe -0.37 / Fitness -0.14 / Turnover 2.80% / Returns -1.81% / Drawdown 6.17% / Margin -12.93‱`
- `IS Testing Status` shows `5 PASS / 2 FAIL / 1 PENDING`, but `Check Submission` and `Submit Alpha` are still disabled and no non-null subuniverse evidence appeared.
- This is a strong IS anchor, but the negative TEST view keeps it below submission readiness.

## Batch 12 Update

- The `126d` / `252d` operating-income control is now the current live probe:
  `group_rank(ts_rank(ts_mean(operating_income, 126), 252), industry)`
- IS summary:
  `Sharpe 1.25 / Fitness 0.91 / Turnover 2.96% / Returns 6.64% / Drawdown 8.52% / Margin 44.89‱`
- TEST summary:
  `Sharpe -0.60 / Fitness -0.27 / Turnover 2.57% / Returns -2.50% / Drawdown 5.61% / Margin -19.43‱`
- `IS Testing Status` shows `4 PASS / 3 FAIL / 1 PENDING`, and `Check Submission` / `Submit Alpha` are still disabled.
- This control is weaker on TEST than the current IS anchor, so it is not submission-ready and does not change the branch decision.

## Batch 13 Update

- The `21d` / `252d` operating-income control has now been tested:
  `group_rank(ts_rank(ts_mean(operating_income, 21), 252), industry)`
- IS summary:
  `Sharpe 1.28 / Fitness 0.89 / Turnover 4.53% / Returns 6.00% / Drawdown 8.27% / Margin 26.48‱`
- TEST summary:
  `Sharpe -0.12 / Fitness -0.02 / Turnover 4.01% / Returns -0.45% / Drawdown 4.42% / Margin -2.25‱`
- `IS Testing Status` shows `5 PASS / 2 FAIL / 1 PENDING`, and `Check Submission` / `Submit Alpha` are still disabled.
- This is the least-bad operating-income control so far, but it still fails TEST, so the lane should be branched away from now.

## Optimization Order

1. Stop polishing operating-income and branch to a new forum-backed family.
2. Keep only one or two leading variants live at a time; do not reopen the dead revenue, capital-structure, or price-volume lanes.
3. Use the forum-backed branch to reset the information source and reduce correlation distance from this stalled lane.

## Next Simulation Batch

- Live comparison:
  branch to a new forum-backed family instead of continuing operating-income.
- Backup comparison:
  use the next family to search for a distinct information source, template, or horizon rather than more operating-income polishing.
