# ANL4 Success And PV Corr Self-Corr Failure Lessons

## Metadata

- Date: 2026-04-30
- Scope: project-level durable learning loop
- Evidence status: mixed
  - `Xg2X2jxl` metrics came from official API evidence captured in the live session before user-reported submission.
  - `zqPX5OkX` failure came from user-reported official Check Submission text.
- Source artifacts:
  - `runs/submission-memos/2026-04-30-anl4-totalassets-flag-submitted.md`
  - `runs/submission-memos/2026-04-30-price-volume-corr-self-corr-stop.md`
  - `runs/simulation-captures/2026-04-30-pv-price-volume-corr-rescue.json`

## The Pair

### Successful Submitted Candidate

```text
rank(ts_mean(anl4_totassets_flag, 20))
```

- Alpha ID: `Xg2X2jxl`
- Status: user-reported submitted
- Family: analyst / fundamental flag
- Sharpe: `1.30`
- Fitness: `1.30`
- Returns: `12.47%`
- Turnover: `2.41%`
- Sub-universe Sharpe: `0.75 / 0.56`

### Failed Follow-Up Candidate

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 9), subindustry)
```

- Alpha ID: `zqPX5OkX`
- Family: close-delta / close-volume-correlation price-volume signal
- Sharpe: `1.30`
- Fitness: `1.04`
- Turnover: `14.08%`
- Sub-universe Sharpe before self-corr check: `0.56 / 0.56`
- Final failed gate: self-correlation `0.9896 / 0.7`

## What Actually Happened

At the formula level, the two candidates looked different:

- one used an analyst / fundamental total-assets flag
- one used price and volume behavior

That distinction was useful for initial triage, but it was not enough for submission coexistence. Once the first alpha was submitted, the second candidate failed realized self-correlation almost completely.

## Success Lesson

The submitted `anl4_totassets_flag` line was the right priority because it had the better full-gate profile:

- stronger Fitness margin,
- much lower turnover,
- wider Sub-universe margin,
- cleaner information-source story,
- and less dependence on a thin edge.

The expression was also simple:

```text
rank(ts_mean(field, 20))
```

The important lesson is not that this exact field is universally good. The reusable lesson is that a simple smoothed flag / coverage-style signal can be a better submission priority than a more technical candidate if it has stronger robustness margins and a more distinct information source.

## Failure Lesson

The price-volume correlation line was not a small miss. It failed self-correlation at `0.9896`, which means it behaved almost identically to the active submitted set. Small edits such as:

- `corr` lookback `60 / 70 / 80`,
- decay `8 / 9 / 10`,
- `industry` vs `subindustry`,
- or cosmetic wrapping

should be treated as low expected value after this failure.

## Submission Queue Rule

When two candidates are both near-pass:

1. Rank by robustness margin, not only by headline Sharpe.
2. Prefer the candidate with lower turnover and wider Sub-universe margin when Sharpe is similar.
3. Submit or fully check the most orthogonal candidate first.
4. After one submission, re-check the rest of the queue against the new submitted set.
5. If the next candidate fails self-correlation above `0.95`, stop that branch and rotate to a new information source or mechanism.

## Future Use

Before recommending "both can submit", require completed self-correlation evidence for both candidates against the current submitted set. Formula-level family labels can guide triage, but they do not replace the official self-correlation gate.
