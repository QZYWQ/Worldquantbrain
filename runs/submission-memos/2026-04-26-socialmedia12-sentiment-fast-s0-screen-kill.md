# 2026-04-26 Social Media Sentiment Fast S0 Recheck / Screen Kill

## Decision

- Screen-kill `socialmedia12`.
- Return the lane to the scout pool.
- Do not spend deeper budget.
- Keep `min_depth_completed` at `false`; do not write a permanent stop memo.

## Official Evidence

- `runs/submission-memos/2026-04-25-socialmedia12-sentiment-fast-stop-memo.md`
- `runs/simulation-captures/2026-04-25-socialmedia12-sentiment-fast-batch-01.json`
- `runs/simulation-captures/2026-04-26-socialmedia12-sentiment-fast-s0-recheck-batch-02.json`
- `runs/simulation-captures/2026-04-26-socialmedia12-sentiment-fast-s0-recheck-result.png`

## S0 Recheck Result

- Official Simulate page contract: USA / TOP3000 / delay 1 / decay 4 / Subindustry / truncation 0.08 / pasteurization On / unitHandling Verify / nanHandling On / testPeriod 1Y.
- Baseline expression: `scl12_sentiment_fast_d1`.
- IS summary on the official page: `Sharpe -0.51`, `Fitness -0.13`, `Turnover 76.02%`, `Returns -5.12%`, `Drawdown 50.37%`, `Margin -1.35‱`.
- The page still shows `Needs Improvement`; `Check Submission` and `Submit Alpha` remain disabled.
- The prior batch01 sign-flip control already failed, so there is no rescue path worth more budget.

## Conclusion

- The lane did not clear the S0 recheck.
- Treat it as pure noise for this cycle, screen-kill it, and return it to the scout pool.
- This is not a permanent stop memo because `min_depth_completed` remains `false`.

## Next Hop

- No further budget should be spent on `socialmedia12` under the current cycle.
- If a genuinely new social-media source appears, start a fresh scout lane instead of reopening this one.

## Status

- `screen_kill`
- `returned_to_scout_pool`
