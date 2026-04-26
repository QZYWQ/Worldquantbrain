# 2026-04-24 EPS And Cashflow Freeze

## Current Read

- The live EPS-close cluster is not a submit path.
- The current live unsubmitted triage shows the strongest EPS-close rows all fail self-correlation against `d5l07rpX` / `E5repQ81`.
- `RRk8k3Ln` improved nothing material versus `qMmld9JE`: the queue is still weak on holdout, and the cluster remains blocked by the existing self-correlation structure.
- The less-crowded analyst sibling field `anl4_afv4_median_eps` is confirmed on the platform, but the fresh simulation resolved to the existing active alpha `E5repQ81`, not a new candidate.

## Active Reference Alpha

- Alpha: `E5repQ81`
- Name: `analyst_afv4MedEPS_close_ts60_indrank_us3k_d1_v1`
- Expression: `group_rank(ts_rank(anl4_afv4_median_eps/close, 60), industry)`
- Status: `ACTIVE`
- Stage: `OS`
- OS checks: `IS_SHARPE=PENDING`, `SHARPE=PENDING`, `SELF_CORRELATION=PENDING`, `OTHERS=PENDING`
- IS summary: `Sharpe 1.93 / Fitness 1.40 / Turnover 17.68% / Returns 9.35%`
- Test summary: `Sharpe 1.23 / Fitness 0.59 / Turnover 17.51% / Returns 4.07%`
- Visible IS checks all pass, including `LOW_SHARPE`, `LOW_FITNESS`, `LOW_TURNOVER`, `HIGH_TURNOVER`, `CONCENTRATED_WEIGHT`, `LOW_SUB_UNIVERSE_SHARPE`, and `MATCHES_COMPETITION`.

## Cashflow Recheck

- The cashflow/cap branch was rechecked on `Jj5kq9pn`.
- Official alpha detail:
  - `IS Sharpe 0.29 / Fitness 0.08 / Turnover 7.28% / Returns 0.93%`
  - `TEST Sharpe 1.40 / Fitness 0.82 / Turnover 7.02% / Returns 4.25%`
- Official check posture:
  - `LOW_SHARPE=FAIL`
  - `LOW_FITNESS=FAIL`
  - `LOW_SUB_UNIVERSE_SHARPE=FAIL`
  - `UNITS=WARNING`
  - `SELF_CORRELATION=PENDING`
- The family is frozen; the 90d smoothing follow-up does not rescue it.

## Decision

- Freeze the EPS-close / EPS-sibling cluster for new research budget.
- Freeze the cashflow/cap branch.
- Do not spend more budget on same-family lookback or smoothing tweaks.
- Keep monitoring the existing active OS alpha `E5repQ81`; do not treat it as a new submit target.
- The only remaining useful next step is a materially different family or a genuinely new field source.

## Source Trace

- `runs/submission-memos/2026-04-24-live-unsubmitted-triage.md`
- `runs/submission-memos/2026-04-24-fundamental-model-slow-ratio-cashflow-cap-live-recheck.md`
- `runs/research-contracts/2026-04-24-family-registry.json`
