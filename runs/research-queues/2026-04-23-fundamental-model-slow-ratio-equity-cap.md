# Fundamental / Model Slow Ratio Equity / Cap Queue

- Date: `2026-04-23`
- Status: `frozen / analyst sibling frozen / neutralization probe failed`

## Current Decision

The analyst sibling qfv4 line is frozen and out of budget. The former active live lane `shareholders_equity_total_2 / cap` has now been frozen as well after the neutralization-axis probe failed the full-IS improvement stop condition. No active main remains on this lane.

## Family Order

1. `shareholders_equity_total_2 / cap` - frozen after failed neutralization probe
2. `total_assets_amount / cap` - frozen sibling control
3. `cashflow / cap` - backup only
4. `working_capital / cap` - kill
5. `mdl110_* / market_cap` - kill on this account

## First Batch Shape

- Anchor:
  `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 90)`
- Control 1:
  `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 84)`
- Control 2:
  `ts_rank(group_rank(shareholders_equity_total_2 / cap, industry), 63)`
- Control 3:
  `ts_rank(group_rank(shareholders_equity_total_2 / cap, subindustry), 90)`
- Sibling:
  `ts_rank(group_rank(total_assets_amount / cap, industry), 90)`

## Notes

- `63d` already beats the earlier `cashflow / cap` branch.
- `industry 90d` currently beats the `subindustry 90d`, `84d`, and `63d` variants already verified.
- The verified `industry` window ordering is now `90 > 84 > 63`.
- `total_assets_amount / cap, industry 90d` is live-valid but clearly weaker than the main `shareholders_equity_total_2 / cap` branch.
- `total_assets_amount / cap` has not improved on the adjacent `84d` control; current visible sibling ordering is `90 > 84`.
- `total_assets_amount / cap` now has a complete verified mini-sweep of `90 > 84 > 63`, and the whole sibling branch remains below the main anchor.
- `working_capital / cap, industry 90d` is killed on first official control.
- `Check Submission` is still disabled on the verified `63d` and `84d` runs.
- `Check Submission` is still disabled on the verified `90d` run.
- Historical blocker: rerunning the main `shareholders_equity_total_2 / cap, industry 90d` anchor surfaced `不正确的身份认证信息。`; official simulate was temporarily blocked by session authentication rather than by a new alpha result.
- Recovery status: authentication was restored and the anchor was rerun, but the visible anchor state stayed unchanged at `5 PASS / 2 FAIL / 1 PENDING`, with `Check Submission` still disabled.
- Direct API confirmation for anchor alpha `ZYWzZlgZ` now removes the ambiguity in that split: `LOW_SHARPE` failed at `0.89 < 1.25`, `LOW_FITNESS` failed at `0.60 < 1.0`, and `SELF_CORRELATION` remained `PENDING` on a short re-poll at `2026-04-23 14:05:47 CST (+0800)`.
- The neutralization-axis probe completed on `2026-04-24` as alpha `VkYR9LvA`: full-IS `Sharpe 0.86 / Fitness 0.62`, test-period `Sharpe 1.56 / Fitness 1.40`, and the gate readout still failed `LOW_SHARPE` / `LOW_FITNESS`.
- Decision implication: freeze the family; the neutralization probe improved the test card but not the official gate, so there is no active main left on this lane.
- Structural follow-up check 1 is now killed on official evidence: `group_rank(ts_mean(shareholders_equity_total_2 / cap, 84), industry)` produced `Sharpe 0.34 / Fitness 0.15` on full IS and additionally failed `LOW_SUB_UNIVERSE_SHARPE`.
- Structural follow-up check 2 is also killed on official evidence: `ts_rank(group_rank(ts_mean(shareholders_equity_total_2 / cap, 63), industry), 252)` produced `Sharpe 0.18 / Fitness 0.06` on full IS and also failed `LOW_SUB_UNIVERSE_SHARPE`, despite a stronger shown-test-period card.
- Updated implication: the raw-ratio `industry 90d` anchor remains the best official line inside the family, but the family is now frozen because the neutralization-axis probe did not improve full-IS Sharpe/Fitness.
