# Family Intake Postmortem

## Conclusion

Yes — the current project is stronger at killing weak lanes than at finding reliable new family sources.

The root problem is not mainly expression polishing. It is upstream family intake: the process that ranks and filters candidate data families before the first official batch.

The existing skeleton already has useful triage, failure memory, and anti-neighbor controls, but it is still too weak at selecting a source that is simultaneously:

- officially confirmed in the current account,
- economically distinct from the locked / frozen / active pool,
- and crowded enough to be interesting but not so crowded that it is just a clone magnet.

## Evidence

### Official BRAIN rules

- The submission page says low correlation matters more than a minor performance gain, and self-correlation is part of the gate.
- The same page states the practical self-correlation cutoff is `0.7`, or a 10% Sharpe improvement over correlated submitted alphas.
- The simulation settings page confirms that delay, decay, neutralization, pasteurization, and NaN handling all affect the signal shape, but decay is only a secondary lever for turnover reduction.
- The platform workflow page shows the alpha engine is just turning a field matrix into weights, PnL, turnover, and holdout behavior; if the source is wrong, later tuning only changes the failure mode.

### Project history

- `socialmedia12-sentiment-fast` was a clean field check but froze after the first batch because the ceiling was low and the sign flip only mirrored the weakness.
- `socialmedia8-sentiment-value` had a confirmed official field page, but the first batch was negative on TEST and was frozen.
- `put_breakeven_60` was a direct options source with decent structure, but Fitness and concentration failed and the lane was frozen.
- `actual_eps_value_close_industry` was the best example of a genuinely strong source: full coverage, lower crowding than the older estimate lanes, and good IS performance — but it still died on official self-correlation against an existing alpha.

That last case is the key signal: even a good family can fail if the source is not distinct enough from the existing alpha pool.

## Diagnosis

### What the current skeleton does well

- It remembers killed families and frozen lanes.
- It blocks cosmetic retuning from being treated as new research.
- It has allocator / distinctness / failure-memory code that tries to stop repeated near-neighbor collapse.
- It supports fast stop / freeze / rotate decisions.

### What it still does poorly

- It does not rank candidate family sources hard enough before spending batch budget.
- It does not treat source quality, coverage, crowding, and distinctness as a single front-door gate.
- It still allows too much effort to flow into lanes that are only slightly different from already-failed families.
- It is better at post-hoc triage than at pre-sim family selection.

## What A Reliable Family Looks Like

A family is worth official budget only if all of these are true:

- The field is confirmed in the official Data Explorer for the current region / delay / universe.
- Coverage is good enough to support the thesis without heavy patching.
- Crowd pressure is not absurdly high.
- The thesis is economically distinct from the active / locked / frozen pool.
- The baseline has a plausible sign, not just a lucky metric spike.
- The family can produce at least 3 meaningful branches without becoming cosmetic.

Cosmetic changes do **not** count:

- sign flip only,
- lookback only,
- smoothing only,
- group tweak only.

## Ranked Source Queue

This is the queue I would use next if the goal is to maximize the chance of finding a durable family.

1. Fully covered analyst4 actual-EPS style sources
   - Best combination so far of coverage and lower crowding.
   - Promising only if the next branch is materially different from the existing close-ratio family and not a self-corr near-neighbor.

2. Options analytics sources such as `option_breakeven_30` or `call_breakeven_60`
   - Good if the thesis is genuinely options-demand / downside-demand / expectation structure.
   - Better than social-media only if the family is treated as a distinct economic source, not a retuned ratio lane.

3. `socialmedia8 / snt_social_value`
   - Usable as a quick sentiment probe.
   - Too crowded to trust as a long-lived primary lane unless the first batch proves real breadth.

4. `socialmedia12`
   - Closed.
   - Do not reopen.

## Practical Fix

The project needs a stricter front-end family intake gate.

Suggested gate order:

1. Confirm the field on the official Data Explorer page.
2. Score coverage and visible crowding.
3. Compare against the active / locked pool and the frozen family memory.
4. Reject anything that is just a cosmetic neighbor of a killed line.
5. Only then spend the first official batch on a baseline plus 3 variants.

If a source cannot pass steps 1-4, it should not get batch budget.

## Decision

- Continue research, but change the research process.
- Do not assume more expression tweaking will solve the family problem.
- Treat family intake as the main bottleneck until a source passes both official field checks and distinctness checks.

## Source Trace

- `https://platform.worldquantbrain.com/learn/documentation/interpret-results/alpha-submission`
- `https://platform.worldquantbrain.com/learn/documentation/create-alphas/simulation-settings`
- `https://platform.worldquantbrain.com/learn/documentation/create-alphas/how-brain-platform-works`
- `runs/research-contracts/2026-04-24-family-registry.md`
- `runs/learning-loops/2026-04-25-next-step-decision.md`
- `runs/learning-loops/2026-04-24-alpha-framework-postmortem.md`
- `runs/submission-memos/2026-04-25-socialmedia12-sentiment-fast-stop-memo.md`
- `runs/submission-memos/2026-04-25-socialmedia8-sentiment-value-stop-memo.md`
- `runs/submission-memos/2026-04-25-put-breakeven-60-live-first-batch.md`
- `runs/submission-memos/2026-04-24-actual-eps-live-recheck.md`
- `runs/submission-memos/2026-04-24-actual-eps-subindustry-recheck.md`
