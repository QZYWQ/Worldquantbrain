# Volatility-Gated Event Alpha Queue

- Date: `2026-04-22`
- Status: `branch away / killed`

## Current Decision

The field-based `event_trigger_low_turnover_volatility_gate` lane has now been killed on live evidence. The returns-volatility fallback also failed to rescue it: the 4-sim batch stayed negative on Sharpe and Fitness, never surfaced real submission-style evidence, and never produced a non-null `subuniverse_pass`.

## Next Live Lane

- Topic: `sentiment_news_attention`
- Reason: the event / VWAP-pressure thesis is now dead, so the next branch should move to a different KB-backed information source instead of polishing the same lane further.
- First batch shape: re-check one sentiment / news attention field on the official Data page, then open a small stability-focused batch only if the field is visible and usable.

## Backup Lane

- If the next sentiment / news attention branch is also weak, rotate to the next KB-backed family instead of returning to any of the dead pressure or fundamentals lines.

## Branch Posture

- Do not create a candidate-batch JSON unless `Check Submission` evidence appears and `subuniverse_pass` is non-null.
- Treat the entire volatility-gated pressure lane as dead.
- Keep the next branch exploratory until real TEST behavior improves or a fresh family shows submission-style evidence.
