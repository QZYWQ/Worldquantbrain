# Daily Research Note - 2026-04-20

## Research Direction
sentiment_buzz_stability

## Hypothesis
Persistent sentiment buzz might create a medium-horizon attention-continuation effect, so short stability windows on a confirmed buzz field could produce a lower-correlation non-analyst follow-up lane after the submitted analyst EPS alpha.

## Candidate Fields
- scl12_buzz
- scl12_buzz_fast_d1
- snt_buzz
- snt_buzz_fast_d1

## Expression
`group_rank(ts_rank(scl12_buzz, 10), industry)`

## Settings
- `Region`: USA
- `Universe`: TOP3000
- `Delay`: 1

## Result Summary
A fresh official Data check confirmed scl12_buzz on the live account in USA / D1 / TOP3000 with Matrix type, 100% coverage, 100% date coverage, and very high visible alpha usage. The first real four-simulation batch then failed cleanly: the 5d, 10d, and 20d rolling-mean variants all produced negative aggregate IS Sharpe and Fitness, while the least-bad 10d ts_rank control only reached Sharpe 0.11, Fitness 0.01, and Turnover 63.60%. No real submission-check evidence or non-null subuniverse verdict appeared, so the lane never approached candidate-batch quality.

## First Failure
The first failed assumption was that full coverage plus a non-analyst data family would be enough to make the buzz lane worth polishing. In practice the confirmed field looked structurally healthy but too weak or too crowded for this first simple family.

## Next Experiments
- Keep monitoring E5repQ81 official OS status, but do not reopen manual submission review while it remains unresolved.
- Kill the current scl12_buzz family instead of polishing it further.
- Switch the active non-analyst follow-up lane to event_option_volume_gate and verify a real option/event field on the official Data page before writing the next pack.

## Decision
kill the sentiment_buzz_stability lane and branch immediately to event_option_volume_gate
