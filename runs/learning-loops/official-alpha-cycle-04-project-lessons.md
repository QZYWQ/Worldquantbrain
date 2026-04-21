# Project Learning Loop

## Metadata
- Generated at: 2026-04-21T22:41:18+0800
- Source cycle: `./harness/cycles/official-alpha-cycle-04.json`
- Source docs:
  - https://platform.worldquantbrain.com/learn/documentation/examples/19-alpha-examples
  - https://platform.worldquantbrain.com/learn/documentation/examples/sample-alpha-concepts
- Related project artifacts:
  - `./runs/notes/daily/official-alpha-cycle-day-04.md`
  - `./runs/simulation-captures/2026-04-21-operating-income-smoothed-history-position-batch-08.json`
  - `./runs/expression-families/2026-04-21-operating-income-smoothed-history-position-follow-up.md`

## Official Example Takeaways
- The beginner page is a canonical one-field history template. It shows the usual shape: pose a simple hypothesis, map it to one field, then test a short and readable expression against the field's own history.
- The bronze page broadens the idea without making the branch messy. It uses ratio, z-score, correlation, and volatility examples to show how a family can branch while staying short and interpretable.
- The official hints are most useful as one-lever diagnostics. "Use a shorter window", "try another cash-flow type", or "use backfill" should become a single narrow batch, not a redesign.
- These pages are teaching scaffolds, not proof that a formula is candidate-grade or that a field is available on this account.

## Project Carry-Forward
- The current operating_income branch is still the best live example of the beginner scaffold in action: one field, one transform chain, one clear ridge.
- Batch 08 confirms the live ridge is still shallow and centered around the 78d/84d smoothing band; that is an incremental optimization story, not a signal that the family has stopped being a valid example.
- Batch 09 adds the decisive sign that the ridge has saturated: the 81d probe underperformed the ridge anchors and the visible test-period/overall readout stayed negative, so the family should now be treated as a backup rather than the main lane.
- The current live replacement lane is `snt_buzz` with the 63d baseline `group_rank(ts_mean(snt_buzz, 63), industry)`; it is a real result but still only `Needs Improvement`, so it stays exploratory until the 21d/126d/252d sweep finishes.
- The 21d control is now a clear weak negative control: `Sharpe 0.22 / Fitness 0.06 / Turnover 2.79% / Returns 1.05% / Drawdown 7.13% / Margin 7.52‱`, so the lane still needs the slower `126d` and `252d` probes before anyone calls it a keep or kill.
- The 126d probe then collapsed further to `Sharpe 0.03 / Fitness 0.00 / Turnover 2.45% / Returns 0.11% / Drawdown 4.47% / Margin 0.90‱`, which is a strong sign that window-length tuning alone is exhausted.
- The 252d probe then failed outright on the test-period view at `Sharpe -0.44 / Fitness -0.17 / Turnover 1.73% / Returns -1.76% / Drawdown 5.94% / Margin -20.33‱`, with visible testing status counts of `4 PASS / 3 FAIL / 1 PENDING`, so the sentiment lane should now be treated as killed.
- The option-volume fallback lane already failed cleanly in its own batch, so the next live branch should return to the strongest open fundamentals family instead of any more buzz or option variants.
- The revenue smoothed-history branch `revenue_sm63_hist504_indrank_us3k_d1_v1` also failed as a negative control: batch 01 was only `Sharpe 0.31 / Fitness 0.11 / Turnover 3.22% / Returns 1.70% / Margin 10.57‱`, and batch 02 weakened further to `Sharpe 0.19 / Fitness 0.06 / Turnover 2.52% / Returns 1.05% / Margin 8.30‱`.
- That revenue result is project-local kill material, not KB or skill material yet; it mainly confirms that the operating_income ridge pattern did not generalize to a sparse top-line revenue branch.
- If a future lane is opened from the bronze page or the lower-correlation follow-up plan, the first branch should stay equally compact: one economic intuition, one ratio or volatility object, one neutralization choice.

## Next Use In This Project
- Use the beginner page when the family needs a minimal baseline.
- Use the bronze page when the family needs a compact second branch in valuation, cash-flow, correlation, or volatility.
- Keep the official examples in the reference layer, but do not treat them as submitability evidence.
- For the next live lane, prefer the lower-correlation follow-up plan's non-analyst branch over more operating_income smoothing.
- Keep the `参考资料/` raw-folder structure unchanged; the existing KB raw-index and intake-template pages are enough to map new documents without renaming the source archive.

## Capital Structure Pivot
- The live branch has now moved off the operating_income ridge and into a balance-sheet / capital-structure lane.
- The current batch anchor is the 63d leverage sign-control expression:
  `group_rank(ts_rank(ts_mean(liabilities / assets, 63), 504), industry)`
- The 21d clone collapsed badly to `Sharpe 0.03 / Fitness 0.00 / Turnover 3.19% / Returns 0.10% / Drawdown 9.21% / Margin 0.64‱`, so faster smoothing did not rescue the lane.
- Simulation 17 then tested the planned subindustry branch on the same leverage family:
  `group_rank(ts_rank(ts_mean(liabilities / assets, 63), 504), subindustry)`
  and it settled at IS `Sharpe 0.30 / Fitness 0.08 / Turnover 2.43% / Returns 0.99% / Drawdown 6.23% / Margin 8.17‱`
  with TEST `Sharpe 0.62 / Fitness 0.29 / Turnover 2.17% / Returns 2.82% / Drawdown 5.49% / Margin 25.96‱`.
- The settings modal confirmed the current run is `Fast Expression / Equity / USA / TOP3000 / Subindustry / 1Y` with `decay 4` and `truncation 0.08`.
- No real `Check Submission` evidence or non-null `subuniverse_pass` appeared in the current session, so this remains exploratory only and no candidate-batch JSON should be created yet.
- Decision: keep the 63d leverage anchor as the best current reference, but branch to the liquidity fallback (`assets_curr / liabilities_curr`) only if the lane stays open; otherwise kill the capital-structure lane instead of polishing the same family further.
