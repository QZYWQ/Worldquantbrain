# kq17QGe8 Submission Memo Draft

Date: 2026-04-28

Status: DO NOT SUBMIT YET.

## Alpha

- alpha id: kq17QGe8
- current lead status: lead candidate inside the local V2 branch

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 60)), 5), subindustry)
```

## Metrics

- sharpe: 1.32
- fitness: 0.94
- turnover: 0.1783
- margin: 0.001013
- drawdown: 0.0582
- returns: 0.0903

## Internal Candidate Screen

- candidate-screen pass: yes
- fitness > 0.8
- sharpe > 1.25
- returns > 0
- margin > 0
- turnover < 0.3

## Platform Blockers

- LOW_FITNESS=FAIL
- LOW_SUB_UNIVERSE_SHARPE=FAIL

## Why It Is Promising

- The expression is interpretable: a smoothed price-delta signal penalized by price-volume correlation pressure, neutralized by subindustry.
- The V2 corr60 branch improved Sharpe and fitness versus the original hopeful alpha.
- Turnover is controlled below 0.3 while returns and margin remain positive.
- A nearby corr90 variant cleared LOW_SUB_UNIVERSE_SHARPE, suggesting robustness may be improved by longer correlation windows.

## Why It Is Not Ready

- V2 still fails LOW_FITNESS on platform checks.
- V2 still fails LOW_SUB_UNIVERSE_SHARPE.
- Variant SELF_CORRELATION checks are still pending.
- The best robustness branch, corr90, reduced Sharpe below the current lead.

## Second-Round Comparison Summary

- corr40: weaker than V2, kept LOW_SUB_UNIVERSE_SHARPE fail.
- corr90: lower Sharpe and fitness than V2, but cleared LOW_SUB_UNIVERSE_SHARPE.
- corr60_decay10: improved fitness and turnover, but Sharpe fell below V2 and LOW_SUB_UNIVERSE_SHARPE still failed.

## Risk Notes

- LOW_FITNESS still failed.
- LOW_SUB_UNIVERSE_SHARPE still failed for V2.
- SELF_CORRELATION pending for variants.
- Current family is still close to a price-volume technical structure, so correlation risk should be checked before submission.

## Decision

Do not submit yet.

## Next Validation Plan

Run a third round with at most 3 variants combining the corr90 robustness branch and decay smoothing:

- corr90_decay10_subindustry
- corr90_decay20_subindustry
- corr120_decay10_subindustry

Submission can be reconsidered only if a variant keeps strong metrics and resolves the major platform blockers.

## Third-Round Summary

Third-round variants were run on 2026-04-28. All three simulations completed.

| Variant | Alpha ID | Sharpe | Fitness | Turnover | Margin | Drawdown | Returns | Platform Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| corr90_decay10_subindustry | Vk297b7Y | 1.15 | 0.90 | 0.1322 | 0.001234 | 0.0880 | 0.0816 | LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, SELF_CORRELATION=PENDING; LOW_SUB_UNIVERSE_SHARPE cleared |
| corr90_decay20_subindustry | 6Xa8lej5 | 0.99 | 0.74 | 0.0923 | 0.001514 | 0.0987 | 0.0699 | LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, SELF_CORRELATION=PENDING; LOW_SUB_UNIVERSE_SHARPE cleared |
| corr120_decay10_subindustry | mLr3j5Wp | 0.95 | 0.69 | 0.1295 | 0.001056 | 0.0991 | 0.0683 | LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_SUB_UNIVERSE_SHARPE=FAIL, SELF_CORRELATION=PENDING |

## Updated Submission Decision

DO NOT SUBMIT YET.

No third-round variant beat V2 on both Sharpe and fitness. The corr90 smoothing variants improved sub-universe behavior, but their headline metrics are weaker than V2 and LOW_FITNESS still failed. V2 remains the current lead candidate, but the family needs either a cleaner robustness fix or a different branch before submission.

## Fourth-Round Summary

Fourth-round variants were run on 2026-04-28. All three simulations completed.

| Variant | Alpha ID | Sharpe | Fitness | Turnover | Margin | Drawdown | Returns | Platform Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| corr70_decay5_subindustry | E5g7vMjJ | 1.37 | 1.01 | 0.1750 | 0.001088 | 0.0737 | 0.0952 | SELF_CORRELATION=PENDING; LOW_FITNESS and LOW_SUB_UNIVERSE_SHARPE cleared |
| corr80_decay5_subindustry | xAP6Y5zm | 1.29 | 0.94 | 0.1729 | 0.001057 | 0.0819 | 0.0914 | LOW_FITNESS=FAIL, SELF_CORRELATION=PENDING; LOW_SUB_UNIVERSE_SHARPE cleared |
| corr90_decay5_industry | 9qavV3w2 | 1.15 | 0.88 | 0.1656 | 0.001167 | 0.1107 | 0.0967 | LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, SELF_CORRELATION=PENDING |

## Updated Lead

The lead changed from V2 / `kq17QGe8` to `corr70_decay5_subindustry` / `E5g7vMjJ`.

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 5), subindustry)
```

Why it is stronger than V2:

- Sharpe improved from 1.32 to 1.37.
- Fitness improved from 0.94 to 1.01.
- Returns improved from 0.0903 to 0.0952.
- Margin improved from 0.001013 to 0.001088.
- Turnover stayed controlled at 0.1750.
- LOW_FITNESS and LOW_SUB_UNIVERSE_SHARPE did not fail.

## Current Submission Decision

DO NOT SUBMIT YET.

`E5g7vMjJ` is the new lead candidate, but SELF_CORRELATION is still pending. Submission should wait until correlation posture is known and acceptable. If SELF_CORRELATION clears, prepare a focused submission memo around `E5g7vMjJ` rather than the older V2 expression.

## Self-correlation Re-check

Checked at: 2026-04-28 19:01:04 CST

- alpha id: E5g7vMjJ
- LOW_SHARPE: PASS
- LOW_FITNESS: PASS
- LOW_TURNOVER: PASS
- HIGH_TURNOVER: PASS
- CONCENTRATED_WEIGHT: PASS
- LOW_SUB_UNIVERSE_SHARPE: PASS
- MATCHES_COMPETITION: PASS
- SELF_CORRELATION: PENDING

Updated decision: DO NOT SUBMIT YET.

The only current non-pass check is SELF_CORRELATION=PENDING. No additional local variants should be run until this pending status resolves or a later re-check shows a clear failure.

## Latest Pending Re-check

Checked at: 2026-04-28 19:06:46 CST

SELF_CORRELATION remains PENDING. All other latest checks remain PASS, including LOW_SHARPE, LOW_FITNESS, LOW_SUB_UNIVERSE_SHARPE, turnover checks, CONCENTRATED_WEIGHT, and MATCHES_COMPETITION.

Updated decision: DO NOT SUBMIT YET. Do not run additional local variants unless SELF_CORRELATION changes to FAIL.
