# Daily Research Note - 2026-04-19

## Research Direction
analyst_eps_sibling_qfv4_industry

## Hypothesis
Lower-crowding analyst4 EPS siblings, especially quarterly median and mean estimates relative to price inside industry groups, may preserve the first-cycle analyst expectation-drift thesis while improving robustness or correlation posture.

## Candidate Fields
- anl4_qfv4_median_eps
- anl4_qfv4_eps_mean
- anl4_afv4_median_eps
- close

## Expression
`group_rank(ts_rank(anl4_afv4_median_eps/close, 60), industry)`

## Settings
- `Region`: USA
- `Universe`: TOP3000
- `Delay`: 1
- `Decay`: 4
- `Neutralization`: SUBINDUSTRY
- `Truncation`: 0.08
- `Testperiod`: P1Y
- `Pasteurization`: ON
- `Nanhandling`: OFF
- `Unithandling`: VERIFY

## Result Summary
Official field checks showed qfv4 median and qfv4 mean EPS siblings both had full coverage and materially lower crowding than the first-cycle annual mean baseline. Real simulations then showed the two qfv4 siblings improved the first-cycle holdout slice only modestly, while the annual-median analyst4 control unexpectedly became the strongest line with IS Sharpe 1.93, Fitness 1.40, Turnover 0.1768, and test Sharpe 1.23, Fitness 0.59, Returns 0.0407. A later 2026-04-19 official /alphas/{id}/check refresh resolved concentrated-weight PASS, self-correlation PASS, low-fitness PASS, and low-sub-universe-sharpe PASS for the annual-median control as well.

## First Failure
The first failed assumption was that lower field crowding would automatically create the best sibling. The qfv4 siblings were cleaner on metadata but did not beat the annual-median analyst4 control in holdout performance.

## Next Experiments
- Monitor the official OS page for `E5repQ81` until the post-submit `4 PENDING` checks resolve.
- Clone the submitted alpha and branch into a more distinct follow-up line, starting with analyst disagreement around `anl4_afv4_dts_spe` or a non-analyst lane.
- Keep `qMm6xPVv` as a same-family backup, but do not let the next session collapse into more EPS-level clone polishing.

## Decision
submit `E5repQ81` as the first formal alpha, lock it while OS runs, and shift the next session to lower-correlation follow-up work
