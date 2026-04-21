# Promotion Gate

## Metadata
- Generated at: 2026-04-21T22:41:18+0800
- Source cycle: `./harness/cycles/official-alpha-cycle-04.json`
- Source docs:
  - https://platform.worldquantbrain.com/learn/documentation/examples/19-alpha-examples
  - https://platform.worldquantbrain.com/learn/documentation/examples/sample-alpha-concepts
- Related project artifacts:
  - `./runs/learning-loops/official-alpha-cycle-04-project-lessons.md`
  - `./runs/learning-loops/official-alpha-cycle-04-kb-candidate.md`
- `./runs/learning-loops/official-alpha-cycle-04-skill-candidate.md`
- `./runs/notes/daily/official-alpha-cycle-day-04.md`
- `./runs/simulation-captures/2026-04-21-operating-income-smoothed-history-position-batch-08.json`
- `./runs/simulation-captures/2026-04-22-capital-structure-balance-sheet-batch-01.json`

## Promotion Ladder
- `project-lessons`: keep project-specific facts and carry-forward conclusions.
- `kb-candidate`: only promote method-level heuristics that look reusable beyond one cycle.
- `skill-candidate`: only promote workflow-level rules that improve future research discipline.

## KB Gate
- Status: `REVIEW`
- Minimum bar:
  - Statement is not a current-platform fact that belongs to official verification.
  - Statement is not just a one-field or one-family verdict.
  - Statement is backed by durable project outputs and can plausibly generalize across cycles.
- Current readout:
  - The official example scaffold is reusable across beginner and bronze pages.
  - The rule is about batch design and diagnostic discipline, not about one alpha family.
  - The current operating_income ridge confirms the same narrow-sweep principle in live project work.
  - Batch 09 shows the ridge has saturated: the 81d probe underperformed the ridge anchors and the visible test-period/overall readout stayed negative, so the family is now a backup example rather than the main live lane.
  - The live `snt_buzz` replacement lane now has a completed negative sweep: 21d was weak, 126d collapsed further, and the 252d test-period control failed at `Sharpe -0.44 / Fitness -0.17 / Turnover 1.73%`, so the family is now dead rather than exploratory.
  - The revenue smoothed-history branch now has its own negative sweep: the 63d baseline was weak and the 126d probe was worse, so the line is dead rather than exploratory.
- Candidate items:
  - Start a new family with hypothesis -> implementation -> hint -> settings.
  - Convert official hints into one narrow diagnostic branch.
  - Keep first batches to one semantic signal and one lever change.
  - When branching for lower correlation, prefer a new information source or a grouping / neutralization change before leaning on window-length tuning alone.
  - Before calling a family robust, test small parameter changes and the relevant universe / region shifts instead of trusting one backtest slice.
  - After a completed negative sweep, branch to a distinct fundamentals family instead of revisiting the dead buzz or option lane.

## Skill Gate
- Status: `HOLD`
- Minimum bar:
  - Rule is workflow-level, not alpha-family-specific.
  - Rule tightens evidence, prioritization, or branch-kill discipline.
  - Rule does not weaken existing hard rules in the WorldQuant skill.
- Current readout:
  - The candidate rules are useful, but much of the discipline already exists in the current skill's default mode and output contract.
  - The marginal gain of editing the skill now is smaller than the gain of keeping the rules as reusable candidate material.
  - A later cycle can decide whether the scaffold deserves a permanent skill hook.
- Candidate items:
  - Add an example-scaffold intake rule: always extract hypothesis, implementation, hint, and settings before writing the first batch.
  - Add a narrow-branch rule: treat hints as a single lever change, not a broad redesign.
  - Add a verification rule: keep course examples as baselines only and require live simulation evidence before any submission claim.

## Explicit Do-Not-Promote Cases
- Example formulas as universal winners.
- Account-specific field availability or tutorial settings as current platform facts.
- One cycle's ridge or failure mode as a permanent family verdict.

## Next Action
- Keep `project-lessons` and `kb-candidate` as the active carry-forward layers.
- Hold the skill candidate until another cycle shows the scaffold adds clearer value than the current skill wording.

## Capital Structure Readout
- The current live run is the liquidity baseline, not another revenue or operating-income polish pass.
- The 63d leverage sign-control anchor remains the strongest observed point in the batch:
  `group_rank(ts_rank(ts_mean(liabilities / assets, 63), 504), industry)`
- The 21d clone is a clear weak control, so same-family smoothing alone is not a useful next lever.
- The liquidity subindustry follow-up improved the TEST view to `Sharpe 0.39 / Fitness 0.13 / Turnover 2.38%`, but IS stayed negative at `Sharpe -0.43 / Fitness -0.14 / Turnover 2.65%`, `Check Submission` never became visible, and `Submit Alpha` stayed disabled.
- The visible testing status stayed at `4 PASS / 3 FAIL / 1 PENDING`, which confirms the lane is not candidate-ready even though the test slice is mildly positive.
- The settings modal confirmed the run is still exploratory: `Subindustry` neutralization, `USA / TOP3000 / D1`, `decay 4`, `truncation 0.08`, `test period = 1Y`.
- Current posture: `kill`, not `submit` or `polish`; move the next live branch to a distinct fundamentals family.
