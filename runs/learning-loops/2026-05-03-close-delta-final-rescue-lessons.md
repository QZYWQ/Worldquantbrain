# 2026-05-03 Close Delta Final Rescue Lessons

Date: 2026-05-03

## Lesson

For a short-horizon price-only family, lowering turnover is not enough if Returns, Sharpe, and Fitness fall faster.

The close-delta family showed this pattern clearly:

- Baseline sign-flip had usable Sharpe but failed Fitness.
- Decay `10` lowered turnover, but Fitness stayed below `1.00`.
- `trade_when` lowered turnover again, but Sharpe and Returns fell too much.
- `hump` suppressed the signal and produced negative Sharpe.

## Reusable Rule

When a price-only short-horizon family has already tested:

- sign flip
- one group axis change
- one lookback/window change
- one platform decay rescue
- one final holding/smoothing mechanism

and it still fails Fitness, stop the lane unless a genuinely new information source or economic condition is introduced.

Do not keep spending official budget on more variants that only adjust:

- group level
- rank window
- decay
- truncation
- smoothing wrapper

## D0 / D1 Route Note

Competition route matching is not a quality pass.

For this family, `MATCHES_COMPETITION` passed for the useful-looking variants, but the actual quality checks still failed. The route gate should decide where to test first. It should not keep a weak Alpha alive after Sharpe/Fitness evidence says to stop.

