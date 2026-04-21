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
Batch 09 then tested the 81d smoothing probe and confirmed the ridge had saturated: the IS view dropped to Sharpe 0.96, Fitness 0.63, Turnover 2.92%, Returns 5.43%, and Margin 37.23‱, while the shown test-period/overall readout stayed negative and `Submit Alpha` remained disabled.
The sentiment lane's 21d control also finished at Sharpe 0.22, Fitness 0.06, Turnover 2.79%, Returns 1.05%, Drawdown 7.13%, and Margin 7.52‱. It is still weaker than the 63d baseline on the quality metrics that matter, so the lane remains exploratory until the 126d and 252d probes land.
The 126d probe then underperformed sharply at Sharpe 0.03, Fitness 0.00, Turnover 2.45%, Returns 0.11%, Drawdown 4.47%, and Margin 0.90‱. That makes 252d the last meaningful control before the family should be branched away or killed.
The 252d control then failed outright on the test-period view at Sharpe -0.44, Fitness -0.17, Turnover 1.73%, Returns -1.76%, Drawdown 5.94%, and Margin -20.33‱, with visible testing counts of 4 PASS / 3 FAIL / 1 PENDING. `Submit Alpha` stayed disabled and no real Check Submission or non-null subuniverse evidence appeared, so the sentiment lane is now dead.

## First Failure
The ridge is shallow rather than sharply peaked, and the absence of real submission-check or subuniverse evidence still blocks packaging.

## Next Experiments
- Keep the operating_income smoothed-history branch separate and only continue with real simulation evidence.
- Narrow the next sweep around the 78d/84d ridge, e.g. 81d and 87d or another tighter pair, before changing neutralization or adding operators.
- Monitor the submitted EPS alpha OS status separately; do not reopen manual submission review for it.
- Do not create a candidate-batch JSON for either lane until real submission-check evidence or non-null subuniverse evidence appears.
- Move the next live simulation effort to the strongest remaining fundamentals branch instead of any more buzz or option smoothing.

## Decision
branch away from the operating_income ridge to a distinct non-analyst lane, and keep the submitted EPS alpha locked

## Sentiment Pivot Update
- The new live branch is `snt_buzz_sm63_indrank_us3k_d1_v1` with `group_rank(ts_mean(snt_buzz, 63), industry)`.
- The 63d baseline is real but only `Needs Improvement` with IS Sharpe 0.39, Fitness 0.14, Turnover 3.68%, and visible testing counts of 5 PASS / 2 FAIL / 1 PENDING.
- The 21d control is now confirmed weak at Sharpe 0.22 / Fitness 0.06 / Turnover 2.79%, so keep the remaining 126d and 252d probes before deciding whether this lane deserves polishing or should be killed quickly.
- The 252d probe failed cleanly on the test-period view at Sharpe -0.44 / Fitness -0.17 / Turnover 1.73% / Returns -1.76% / Drawdown 5.94% / Margin -20.33‱, with visible testing counts of 4 PASS / 3 FAIL / 1 PENDING.
- The sentiment lane is now a completed kill; the next live branch should come from the strongest remaining fundamentals family.

## Revenue Smoothed-History Update
The revenue smoothed-history branch was tested as a new top-line control using `group_rank(ts_rank(ts_mean(revenue, 63), 504), industry)` and then `group_rank(ts_rank(ts_mean(revenue, 126), 504), industry)`. The 63d baseline only reached `Sharpe 0.31 / Fitness 0.11 / Turnover 3.22% / Returns 1.70% / Drawdown 12.35% / Margin 10.57‱`, while the 126d probe weakened further to `Sharpe 0.19 / Fitness 0.06 / Turnover 2.52% / Returns 1.05% / Drawdown 12.45% / Margin 8.30‱`. No visible Check Submission evidence or non-null subuniverse verdict appeared, and `Submit Alpha` stayed disabled, so this revenue lane should be treated as dead.

## Revenue Next Step
Do not keep smoothing revenue. The next live branch should come from a stronger fundamentals or model-dataset lane, ideally with a different information source or a neutralization change rather than more revenue-only tuning.

## Capital Structure Update
- The logged-in WorldQuant BRAIN session was restored after the browser was closed, and the current live lane is now the capital-structure follow-up.
- Simulation 15 holds the 63d leverage sign-control anchor:
  `group_rank(ts_rank(ts_mean(liabilities / assets, 63), 504), industry)`
  with IS `Sharpe 0.37 / Fitness 0.12 / Turnover 2.50% / Returns 1.35% / Drawdown 7.07% / Margin 10.76‱` and TEST `Sharpe 0.60 / Fitness 0.29 / Turnover 2.24% / Returns 2.95% / Drawdown 6.05% / Margin 26.35‱`.
- Simulation 16 is the 21d clone:
  `group_rank(ts_rank(ts_mean(liabilities / assets, 21), 504), industry)`
  and its visible IS aggregate is much weaker at `Sharpe 0.03 / Fitness 0.00 / Turnover 3.19% / Returns 0.10% / Drawdown 9.21% / Margin 0.64‱`.
- Simulation 17 then tested the planned subindustry branch on the same leverage family:
  `group_rank(ts_rank(ts_mean(liabilities / assets, 63), 504), subindustry)`
  with IS `Sharpe 0.30 / Fitness 0.08 / Turnover 2.43% / Returns 0.99% / Drawdown 6.23% / Margin 8.17‱`
  and TEST `Sharpe 0.62 / Fitness 0.29 / Turnover 2.17% / Returns 2.82% / Drawdown 5.49% / Margin 25.96‱`.
- Simulation 17 then tested the liquidity fallback baseline on the same run:
  `group_rank(ts_rank(ts_mean(assets_curr / liabilities_curr, 63), 504), industry)`
  with IS `Sharpe -0.72 / Fitness -0.29 / Turnover 2.82% / Returns -2.02% / Drawdown 11.29% / Margin -14.36‱`
  and TEST `Sharpe 0.45 / Fitness 0.17 / Turnover 2.48% / Returns 1.73% / Drawdown 3.73% / Margin 13.99‱`.
- The liquidity subindustry follow-up then tested the same slow-rank / history stack with the neutralization axis switched to `subindustry`:
  `group_rank(ts_rank(ts_mean(assets_curr / liabilities_curr, 63), 504), subindustry)`
  and it settled at TEST `Sharpe 0.39 / Fitness 0.13 / Turnover 2.38% / Returns 1.37% / Drawdown 3.55% / Margin 11.49‱`
  while the IS view remained negative at `Sharpe -0.43 / Fitness -0.14 / Turnover 2.65% / Returns -1.24% / Drawdown 11.89% / Margin -9.33‱`.
- The visible testing status stayed at `4 PASS / 3 FAIL / 1 PENDING`, `Check Submission` never became visible, and `Submit Alpha` stayed disabled.
- The settings modal confirmed `Fast Expression / Equity / USA / TOP3000 / Subindustry / 1Y` with `decay 4` and `truncation 0.08`.
- No real `Check Submission` evidence or non-null `subuniverse_pass` appeared in this session, so do not create a candidate-batch JSON yet.
- Decision: kill the capital-structure lane and keep the branch-threshold rule as project-local lesson material only.
