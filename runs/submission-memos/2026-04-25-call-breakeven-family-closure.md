# 2026-04-25 Call Breakeven Family Closure

- Closure time: `2026-04-25 01:28:13 CST (+0800)`
- Verification boundary: live official WorldQuant BRAIN Data Explorer and alpha API from the logged-in browser session
- Family: `call_breakeven_60`

## Decision

- Freeze / kill the current `call_breakeven_60` branch for the current budget.
- Keep `mLxN1mlX` as the best historical anchor, but do not spend more same-family budget on it.
- Rotate the next research hour to a new family or a new information source.

## Why

The branch was promising, but the last set of repairs could not produce a compliant alpha:

- `mLxN1mlX` remained the best overall candidate on raw Sharpe / holdout, but it still failed `LOW_FITNESS` and `CONCENTRATED_WEIGHT`.
- `6XYQ2955` and `LLlw2roL` showed that smoothing can repair concentration, but both lost too much Sharpe / low-sub-universe quality.
- `2rnxxJA8` and `kqLM6Qdk` showed the concentration-safe branch, but they still missed Sharpe and Fitness.
- `d5l6r9VE` showed that extending the rank horizon did not rescue the repaired line; it remained below floor and also lost low-sub-universe Sharpe.

## Official Evidence Used

- Data Explorer `option9`: `call_breakeven_60` coverage `70%`, date coverage `100%`, visible alphas `542`
- `mLxN1mlX`
  - `group_rank(ts_rank(call_breakeven_60 / close, 20), industry)`
  - IS `Sharpe 1.44 / Fitness 0.62`
  - Test `Sharpe 2.18 / Fitness 0.89`
  - `LOW_SHARPE=PASS`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=PASS`
- `O05jg5Og`
  - `group_rank(ts_rank(call_breakeven_60 / close, 60), industry)`
  - IS `Sharpe 1.34 / Fitness 0.66`
  - `LOW_SHARPE=PASS`, `LOW_FITNESS=FAIL`, `CONCENTRATED_WEIGHT=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`
- `6XYQ2955`
  - `group_rank(ts_rank(ts_mean(call_breakeven_60 / close, 5), 20), industry)`
  - IS `Sharpe 1.04 / Fitness 0.43`
  - `CONCENTRATED_WEIGHT=PASS`, but `LOW_SHARPE=FAIL`, `LOW_FITNESS=FAIL`, `LOW_SUB_UNIVERSE_SHARPE=FAIL`
- `LLlw2roL`
  - `group_rank(ts_rank(ts_mean(call_breakeven_60 / close, 3), 20), industry)`
  - IS `Sharpe 1.22 / Fitness 0.52`
  - still below floor and low-sub-universe fails
- `2rnxxJA8`
  - `group_rank(ts_rank(ts_mean(call_breakeven_60 / close, 2), 20), subindustry)`
  - IS `Sharpe 1.36 / Fitness 0.58`
  - `CONCENTRATED_WEIGHT=PASS`, but `LOW_SUB_UNIVERSE_SHARPE` misses
- `kqLM6Qdk`
  - `group_rank(ts_rank(ts_mean(call_breakeven_60 / close, 2), 20), industry)`
  - IS `Sharpe 1.12 / Fitness 0.49`
  - `CONCENTRATED_WEIGHT=PASS`, `LOW_SUB_UNIVERSE_SHARPE=PASS`, but both Sharpe and Fitness fail
- `d5l6r9VE`
  - `group_rank(ts_rank(ts_mean(call_breakeven_60 / close, 2), 60), industry)`
  - IS `Sharpe 1.04 / Fitness 0.53`
  - concentration passes, but Sharpe / Fitness / low-sub-universe still fail

## Conclusion

- The family has enough evidence to keep it alive for a while, but not enough to justify more budget now.
- The branch never found a point where concentration repair and Sharpe/Fitness repair held together at once.
- That makes this a budgeted freeze, not a submit path.

## Next Step

- Move to a genuinely different family or a new information source.
- Do not return to `call_breakeven_60` unless a fresh structural idea appears that is not just another tenor / smoothing tweak.
