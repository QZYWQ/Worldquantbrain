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
