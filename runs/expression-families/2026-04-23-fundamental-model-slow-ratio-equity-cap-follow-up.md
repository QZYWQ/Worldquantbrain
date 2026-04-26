# Fundamental / Model Slow Ratio Equity / Cap Follow-up Expression Family

## Metadata

- Date: `2026-04-23`
- Topic: `fundamental_model_slow_ratio_equity_cap_follow_up`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`
- Upstream evidence:
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/raw/pages/hc-en-us-community-posts-20051403346583-BRAIN-TIPS-Finding-Alphas-Fundamental-and-Model-Data-5b0a7e2b6d.txt`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/raw/pages/hc-en-us-community-posts-39411791834647-8d78a1331f.txt`
  - `./runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`

## Hypothesis

The forum-backed slow-ratio lane is still valid on this account, but the usable fields are balance-sheet style numerators that actually exist here rather than the invalid `mdl110_*` shortlist. `shareholders_equity_total_2 / cap` is the first accessible, higher-coverage branch that materially beats the earlier `cashflow / cap` control.

## Confirmed Inputs

- `shareholders_equity_total_2` coverage: `84.69%`
- `total_assets_amount` coverage: `80.35%`
- `cashflow` coverage: `50.00%`
- `working_capital` coverage: `50.00%`
- `cap` coverage: `100.00%`
- confirmed grouping: `subindustry`, `industry`

## Live Evidence

- `ts_rank(group_rank(shareholders_equity_total_2 / cap, subindustry), 63)`
  - default aggregate view before showing test period:
    `Sharpe 0.81 / Fitness 0.50 / Turnover 14.96% / Returns 5.64% / Drawdown 7.17% / Margin 7.54‱`
  - aggregate view with `Show test period`:
    `Sharpe 1.05 / Fitness 0.63 / Turnover 14.67% / Returns 5.34% / Drawdown 4.73% / Margin 7.28‱`
  - visible IS testing status:
    `4 PASS / 3 FAIL / 1 PENDING`
  - `Check Submission` stayed disabled.
- `ts_rank(group_rank(shareholders_equity_total_2 / cap, subindustry), 84)`
  - default aggregate view before showing test period:
    `Sharpe 0.79 / Fitness 0.52 / Turnover 13.12% / Returns 5.62% / Drawdown 7.87% / Margin 8.57‱`
  - aggregate view with `Show test period`:
    `Sharpe 1.13 / Fitness 0.78 / Turnover 12.87% / Returns 6.06% / Drawdown 4.89% / Margin 9.41‱`
  - visible IS testing status:
    `5 PASS / 2 FAIL / 1 PENDING`
  - `Check Submission` stayed disabled.
- `ts_rank(group_rank(shareholders_equity_total_2 / cap, subindustry), 90)`
  - default aggregate view before showing test period:
    `Sharpe 0.79 / Fitness 0.53 / Turnover 12.73% / Returns 5.67% / Drawdown 8.02% / Margin 8.91‱`
  - aggregate view with `Show test period`:
    `Sharpe 1.15 / Fitness 0.81 / Turnover 12.50% / Returns 6.21% / Drawdown 4.87% / Margin 9.93‱`
  - visible IS testing status:
    `5 PASS / 2 FAIL / 1 PENDING`
  - `Check Submission` stayed disabled.
- `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)`
  - default aggregate view before showing test period:
    `Sharpe 0.79 / Fitness 0.52 / Turnover 14.73% / Returns 6.27% / Drawdown 10.17% / Margin 8.50‱`
  - aggregate view with `Show test period`:
    `Sharpe 1.43 / Fitness 1.10 / Turnover 14.34% / Returns 8.44% / Drawdown 4.97% / Margin 11.77‱`
  - visible IS testing status:
    `5 PASS / 2 FAIL / 1 PENDING`
  - `Check Submission` stayed disabled.
- `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 84)`
  - default aggregate view before showing test period:
    `Sharpe 0.80 / Fitness 0.52 / Turnover 15.16% / Returns 6.31% / Drawdown 9.86% / Margin 8.33‱`
  - aggregate view with `Show test period`:
    `Sharpe 1.40 / Fitness 1.04 / Turnover 14.75% / Returns 8.18% / Drawdown 4.98% / Margin 11.10‱`
  - visible IS testing status:
    `5 PASS / 2 FAIL / 1 PENDING`
  - `Check Submission` stayed disabled.
- `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 63)`
  - default aggregate view before showing test period:
    `Sharpe 0.85 / Fitness 0.52 / Turnover 17.13% / Returns 6.42% / Drawdown 8.30% / Margin 7.50‱`
  - aggregate view with `Show test period`:
    `Sharpe 1.31 / Fitness 0.86 / Turnover 16.60% / Returns 7.23% / Drawdown 4.63% / Margin 8.71‱`
  - visible IS testing status:
    `5 PASS / 2 FAIL / 1 PENDING`
  - `Check Submission` stayed disabled.
- `ts_rank(group_rank(total_assets_amount / cap, industry), 90)`
  - default aggregate view before showing test period:
    `Sharpe 0.74 / Fitness 0.49 / Turnover 15.07% / Returns 6.51% / Drawdown 8.26% / Margin 8.64‱`
  - aggregate view with `Show test period`:
    `Sharpe 1.16 / Fitness 0.83 / Turnover 14.87% / Returns 7.62% / Drawdown 4.25% / Margin 10.25‱`
  - visible IS testing status:
    `5 PASS / 2 FAIL / 1 PENDING`
  - `Check Submission` stayed disabled.
- `ts_rank(group_rank(total_assets_amount / cap, industry), 84)`
  - default aggregate view before showing test period:
    `Sharpe 0.75 / Fitness 0.48 / Turnover 15.49% / Returns 6.47% / Drawdown 8.14% / Margin 8.36‱`
  - aggregate view with `Show test period`:
    `Sharpe 1.13 / Fitness 0.78 / Turnover 15.28% / Returns 7.37% / Drawdown 4.15% / Margin 9.65‱`
  - visible IS testing status:
    `5 PASS / 2 FAIL / 1 PENDING`
  - `Check Submission` stayed disabled.
- `ts_rank(group_rank(working_capital / cap, industry), 90)`
  - default aggregate view before showing test period:
    `Sharpe 0.55 / Fitness 0.29 / Turnover 13.76% / Returns 3.80% / Drawdown 8.53% / Margin 5.53‱`
  - aggregate view with `Show test period`:
    `Sharpe 0.34 / Fitness 0.12 / Turnover 13.48% / Returns 1.55% / Drawdown 6.41% / Margin 2.30‱`
  - visible IS testing status:
    `5 PASS / 2 FAIL / 1 PENDING`
  - `Check Submission` stayed disabled.
- `ts_rank(group_rank(total_assets_amount / cap, industry), 63)`
  - default aggregate view before showing test period:
    `Sharpe 0.81 / Fitness 0.50 / Turnover 17.45% / Returns 6.77% / Drawdown 7.67% / Margin 7.76‱`
  - aggregate view with `Show test period`:
    `Sharpe 0.95 / Fitness 0.56 / Turnover 17.14% / Returns 5.86% / Drawdown 4.04% / Margin 6.84‱`
  - visible IS testing status:
    `5 PASS / 2 FAIL / 1 PENDING`
  - `Check Submission` stayed disabled.

## Account-Specific Kill Notes

- Kill the local `mdl110_value / market_cap` and `mdl110_score / market_cap` shortlist on this account.
- The official simulate editor returned `Invalid data field mdl110_value`.
- The official simulate editor returned `Attempted to use unknown variable "market_cap"`.
- Keep those local scorecard outputs as miner heuristics only; they are not runnable account truth here.

## Decision

- Frozen: `shareholders_equity_total_2 / cap`.
- Current best official line (not submit-ready): `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)`.
- The grouping control flipped the branch: `industry 90` materially beats `subindustry 90` on the shown-test-period aggregate view while keeping the same visible IS testing status.
- Inside the verified `industry` window sweep, the ordering is `90 > 84 > 63` on the shown-test-period aggregate view.
- Demote: `subindustry` variants to controls, with `subindustry 90` the strongest backup inside that grouping.
- Demote: `cashflow / cap` to backup only.
- Hold: `total_assets_amount / cap` as a weaker accessible sibling; verified sibling ordering is `90 > 84 > 63`, and the full sibling branch stays materially below the equity / cap anchor.
- Kill: `working_capital / cap` on first official control.
- Freeze this family: the neutralization-axis probe did not improve full-IS Sharpe/Fitness over the raw-ratio anchor, so there is no remaining official budget here.

## Neutralization Probe Result

- Axis: group / neutralization only; same numerator, denominator, and 90d horizon.
- Alpha: `VkYR9LvA`
- Full-IS: `Sharpe 0.86 / Fitness 0.62`
- Test-period: `Sharpe 1.56 / Fitness 1.40`
- Gate readout: `LOW_SHARPE FAIL`, `LOW_FITNESS FAIL`, `LOW_TURNOVER PASS`, `HIGH_TURNOVER PASS`, `CONCENTRATED_WEIGHT PASS`, `LOW_SUB_UNIVERSE_SHARPE PASS`, `SELF_CORRELATION PENDING`, `MATCHES_COMPETITION PASS`.
- Decision: freeze this family; the probe improved the test card but not the official full-IS gate.

## Latest Blocker

- On `2026-04-23 13:49 CST (+0800)`, attempting to rerun `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)` did not return a fresh summary card.
- The official simulate page surfaced the message `不正确的身份认证信息。`
- Treat this as an authentication/session blocker rather than an alpha-quality signal.
- Further official verification is blocked until the logged-in session is re-authenticated.

## Recovery Check

- After the logged-in session was restored, the page briefly fell into the tutorial overlay; closing that overlay restored the normal summary card.
- Rerunning `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)` returned the same visible shown-test-period aggregate view as before:
  `Sharpe 1.43 / Fitness 1.10 / Turnover 14.34% / Returns 8.44% / Drawdown 4.97% / Margin 11.77‱`
- Visible IS testing status remained `5 PASS / 2 FAIL / 1 PENDING`.
- `Check Submission` remained disabled.
- Net result: the authentication blocker was cleared, but there was no visible progression in the anchor's testing/submission state.

## API Check Breakdown

- The completed simulation `3jvMzT5ji4ue8YoCEpvAlp9` resolved to alpha `ZYWzZlgZ` for `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)`.
- Direct `GET /alphas/ZYWzZlgZ` at `2026-04-23 14:05:47 CST (+0800)` exposed the exact IS gate split behind the visible `5 PASS / 2 FAIL / 1 PENDING`.
- `LOW_SHARPE`: `FAIL`, limit `1.25`, value `0.89`.
- `LOW_FITNESS`: `FAIL`, limit `1.0`, value `0.60`.
- `LOW_TURNOVER`: `PASS`, limit `0.01`, value `0.1465`.
- `HIGH_TURNOVER`: `PASS`, limit `0.70`, value `0.1465`.
- `CONCENTRATED_WEIGHT`: `PASS`.
- `LOW_SUB_UNIVERSE_SHARPE`: `PASS`, limit `0.39`, value `0.71`.
- `SELF_CORRELATION`: `PENDING`.
- `MATCHES_COMPETITION`: `PASS` for `Challenge` and `IQC2026S1`.
- The binding blockers are the full-IS values, not the shown-test-period card: IS `Sharpe 0.89 / Fitness 0.60` versus shown-test-period `Sharpe 1.43 / Fitness 1.10`.
- Short re-polling after the API read still left `SELF_CORRELATION` at `PENDING`, so there is still no new submission-state transition to act on.
- The neutralization-axis control above has now been run and failed the full-IS improvement stop condition, so freeze the family and stop additional official tests under current budget.

## Structural Branch Check

- Official test: `group_rank(ts_mean(shareholders_equity_total_2 / cap, 84), industry)`
  - simulation `UmHBJ61G565b75d8EbL7Ij` -> alpha `2rn6NegP`
  - full-IS gate values: `Sharpe 0.34 / Fitness 0.15`
  - exact failures: `LOW_SHARPE`, `LOW_FITNESS`, `LOW_SUB_UNIVERSE_SHARPE`
  - `SELF_CORRELATION` stayed `PENDING`
  - result: kill the simple `group_rank(ts_mean(...), industry)` branch
- Official test: `ts_rank(group_rank(ts_mean(shareholders_equity_total_2 / cap, 63), industry), 252)`
  - simulation `29fGhsbgU4GJaGPbejr4pqK` -> alpha `akWz1Z05`
  - full-IS gate values: `Sharpe 0.18 / Fitness 0.06`
  - exact failures: `LOW_SHARPE`, `LOW_FITNESS`, `LOW_SUB_UNIVERSE_SHARPE`
  - shown-test-period view was directionally misleading again at `Sharpe 1.29 / Fitness 1.07`
  - `SELF_CORRELATION` stayed `PENDING`
  - result: kill the smoothed-history `ts_mean -> group_rank -> ts_rank(252)` branch
- Net result: the original raw-ratio anchor `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)` remains the best official result inside the accessible equity / cap family even though it still fails full-IS `LOW_SHARPE` and `LOW_FITNESS`.
