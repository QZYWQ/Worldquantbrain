# 2026-04-24 Live Unsubmitted Triage

- Re-check time: `2026-04-24 19:00:33 CST (+0800)`
- Scope: live official `Unsubmitted` list on `https://platform.worldquantbrain.com/alphas/unsubmitted`
- Official source used: logged-in browser session plus `/users/self/alphas` and `/alphas/{id}/check`

## What I Checked

I scanned the current `UNSUBMITTED | IS_FAIL` queue from the live official API and then checked the strongest-looking rows one by one.

The strongest rows in the current queue are all either:

- passable on IS metrics but fail self-correlation against existing alphas, or
- passable on Sharpe but still fail Fitness / Turnover, so they are not submission candidates yet.

## Live Official Results

| Alpha | Expression | IS Sharpe | IS Fitness | Turnover | `/check` result | Reference alpha(s) |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `KPwQ2Pjz` | `group_rank(ts_rank(earnings_per_share_median_value/close, 84), subindustry)` | `1.71` | `1.12` | `15.37%` | `SELF_CORRELATION=FAIL` at `0.9652` | `d5l07rpX`, `E5repQ81` |
| `qMm6xPVv` | `group_rank(ts_rank(anl4_qfv4_median_eps/close, 60), industry)` | `1.65` | `1.04` | `17.29%` | `SELF_CORRELATION=FAIL` at `0.9155` | `d5l07rpX`, `E5repQ81` |
| `qMmld9JE` | `group_rank(ts_rank(earnings_per_share_average/close, 60), industry)` | `1.64` | `1.03` | `17.32%` | `SELF_CORRELATION=FAIL` at `0.9182` | `d5l07rpX`, `E5repQ81` |
| `RRk8k3Ln` | `group_rank(ts_rank(earnings_per_share_median_value/close, 60), industry)` | `1.64` | `1.03` | `17.29%` | `SELF_CORRELATION=FAIL` at `0.9162` | `d5l07rpX`, `E5repQ81` |
| `A1O2Arjg` | `group_rank(ts_rank(anl4_af_eps_value / close, 120), industry)` | `1.34` | `1.04` | `12.88%` | `SELF_CORRELATION=FAIL` at `0.7965` | `d5l07rpX` |
| `d5lPJzpx` | `group_rank(ts_rank(anl4_af_eps_value / close, 60), industry)` | `1.58` | `1.05` | `17.90%` | `SELF_CORRELATION=FAIL` at `0.7604` | `d5l07rpX` |
| `RRkvG6Za` | `- group_rank(ts_zscore(close - vwap, 10), industry)` | `1.78` | `0.56` | `86.37%` | `SELF_CORRELATION=PENDING` | likely the opposite-side close-vwap crowding cluster |

## Decision

- There is no submit-ready alpha in the current live unsubmitted queue.
- The EPS-close family is not worth squeezing further right now: the best-looking variants all fail live self-correlation against `d5l07rpX` / `E5repQ81` with values in the `0.76-0.97` range.
- `RRkvG6Za` is the only row with obviously strong Sharpe on the current page, but it still fails Fitness and High Turnover, so it is not a practical near-submit candidate.
- The correct next move is to branch into a materially different family, not to keep polishing these near-clones.

## Recommendation

- Freeze the current EPS-close / EPS-sibling cluster.
- Do not spend more time on sign flips or tiny lookback edits inside this cluster.
- If we continue immediately, the next research hour should go to a genuinely different field family or a different comparison frame, because correlation reduction here is not a small adjustment problem anymore.
