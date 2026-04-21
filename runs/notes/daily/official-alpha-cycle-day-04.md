# Daily Research Note - 2026-04-21

## Research Direction
operating_income_smoothed_history_position_follow_up

## Hypothesis
Light smoothing on operating_income combined with a long history-rank window still helps, and batch 08 suggests the ridge has moved slightly left: 78d now edges 84d on Sharpe/Fitness, while 84d remains the low-turnover balance point.

## Candidate Fields
- operating_income

## Expression
`group_rank(ts_rank(ts_mean(operating_income, 84), 504), industry)`

## Settings
- `Region`: USA
- `Universe`: TOP3000
- `Delay`: 1

## Result Summary
Batch 08 reran the 504-day smoothing ridge around the 84d control with 72d, 78d, 84d, and 90d probes. The 78-day smoothed 504-day rank was the best visible probe in the batch with IS Sharpe 1.26, Fitness 0.96, Turnover 3.04%, and Returns 7.32%. The 84-day control stayed on the low-turnover side of the ridge with Sharpe 1.25, Fitness 0.96, Turnover 2.98%, and Returns 7.33%. The 72d probe matched the visible Sharpe/Fitness but carried slightly more turnover, and the 90d probe drifted off the ridge. No visible Check Submission evidence or non-null subuniverse verdict appeared for this family. Separately, the official submitted list still shows `analyst_afv4MedEPS_close_ts120_indrank_us3k_d1_v1` as `ACTIVE` with `Date Submitted (EST) = 04/21/2026 EDT` and `IS Testing Status = 8 PASS`.

## First Failure
The ridge is shallow rather than sharply peaked, and the absence of real submission-check or subuniverse evidence still blocks packaging.

## Next Experiments
- Keep the operating_income smoothed-history branch separate and only continue with real simulation evidence.
- Narrow the next sweep around the 78d/84d ridge, e.g. 81d and 87d or another tighter pair, before changing neutralization or adding operators.
- Monitor the submitted EPS alpha OS status separately; do not reopen manual submission review for it.
- Do not create a candidate-batch JSON for either lane until real submission-check evidence or non-null subuniverse evidence appears.

## Decision
polish the operating_income branch around the 78d/84d ridge and keep the submitted EPS alpha locked
