# Daily Research Note - 2026-04-18

## Research Direction
analyst_eps_price_industry

## Hypothesis
Stocks whose analyst EPS expectations are high relative to current price, measured inside industry groups, may outperform because estimate information diffuses gradually and industry-relative ranking reduces broad sector drift.

## Candidate Fields
- earnings_per_share_average
- earnings_per_share_median_value
- anl4_afv4_median_eps
- close

## Expression
`group_rank(ts_rank(earnings_per_share_average/close, 60), industry)`

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
The 60-day average-EPS baseline is the best current primary line with IS Sharpe 1.64, Fitness 1.03, Turnover 0.1732, and positive but weak test-period performance. The 60-day median-field sibling matched it closely and stays alive as a backup. The 20-day fast branch failed fitness, while the 120-day slow branch looked strong in-sample but broke in the holdout slice. A 2026-04-19 official check refresh confirmed concentrated-weight PASS for all four lines, self-correlation PASS for the 60-day baseline, 120-day branch, and 60-day median sibling, and self-correlation still PENDING for the 20-day fast branch.

## First Failure
Holdout robustness is the first real bottleneck. The 60-day baseline stays only weakly positive in the test slice, and the 120-day branch flips negative out of sample, which is a stronger warning than any visible IS threshold issue.

## Next Experiments
- Write the submission memo with the 60-day average-EPS line as primary, the 60-day median sibling as backup, and explicit warnings on weak holdout strength.
- Search one less-crowded analyst sibling around anl4_afv4_median_eps and test a 60-day industry-relative branch instead of speeding up the same average-EPS line.
- Recheck the 20-day fast branch later only if the self-correlation status resolves and a meaningful gating idea appears; otherwise keep it deprioritized because fitness already fails.

## Decision
polish primary baseline and branch a backup rather than submit now
