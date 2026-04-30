# Self-Correlation After Submission Project Lessons

## Metadata

- Date: 2026-04-30
- Scope: project-level durable learning loop
- Evidence status: based on user-reported official Check Submission text plus earlier official API capture
- Source artifacts:
  - `runs/simulation-captures/2026-04-30-pv-price-volume-corr-rescue.json`
  - `runs/submission-memos/2026-04-30-price-volume-corr-self-corr-stop.md`
  - `runs/submission-memos/2026-04-30-sales-estimate-count-decay10-submitted.md`

## Event

The user submitted:

```text
rank(ts_mean(anl4_totassets_flag, 20))
```

Then the candidate:

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 9), subindustry)
```

failed Check Submission:

```text
Self-correlation 0.9896 is above cutoff of 0.7 and Sharpe not better by 10.0% or more.
```

## Corrected Lesson

Formula-level family labels are only a screening heuristic. The official self-correlation check is the submission truth.

The two formulas used different information sources:

- price / volume behavior
- analyst total-assets flag

But the platform still measured an almost identical realized behavior after the submitted set changed. Therefore the price-volume correlation candidate is stopped for submission despite passing Sharpe, Fitness, turnover, weight, Sub-universe, and competition checks.

## Practical Rule

- `SELF_CORRELATION: PENDING` means near-pass, not ready.
- A candidate can be non-overlapping by formula and still fail by realized behavior.
- Submission order matters because each newly submitted alpha changes the correlation set for later candidates.
- If self-correlation is above `0.95`, do not treat it as a small rescue problem.
- After a very high self-correlation failure, avoid minor parameter edits such as lookback `60/70/80`, decay `8/9/10`, or group-axis churn.

## Submission Queue Implication

When there are multiple candidates:

1. Submit or check the strongest, most orthogonal candidate first.
2. Re-run or wait for self-correlation on the next candidate after the submitted set changes.
3. Promote only candidates with completed self-correlation evidence.
4. If a later candidate fails self-correlation hard, stop its branch and move to a genuinely different data source or mechanism.

## Applied Decision

- Keep `rank(ts_mean(anl4_totassets_flag, 20))` as the submitted survivor.
- Stop `zqPX5OkX` and same close-delta / close-volume-correlation near-neighbors for submission.
- Do not let the earlier "visible gates pass except pending self-corr" capture be used as a submit-ready memo.
