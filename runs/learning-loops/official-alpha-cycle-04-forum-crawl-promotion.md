# Forum Crawl Promotion Candidate

## Promotion Guardrail

- This file is a promotion candidate, not automatic truth.
- Only move items into the external KB or skill layer after they look reusable beyond one forum thread and stay valid without account-specific state.
- Source artifacts:
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-catalog.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/decision-notes.md`
  - `./runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/knowledge-link-map.md`
  - `./runs/expression-families/2026-04-22-operating-income-sales-ratio-follow-up.md`
  - `./runs/field-search-packs/2026-04-22-operating-income-sales-ratio.md`

## Skill-Candidate Heuristics

- Data evaluation / freshness checks should stay in skill because they are workflow discipline, not a single alpha family.
- NaN handling / missingness should stay in skill because it governs how to avoid fake coverage and bad fill logic.
- Validation / overfitting discipline should stay in skill because it changes how every family is tested.
- Low-parameter robustness should stay in skill because it generalizes across families and prevents operator soup.
- Statistical neutralization should stay in skill because it is a reusable risk-control rule, not a one-off template.

## KB-Candidate Heuristics

- Price / volume short horizon belongs in KB because it is a reusable alpha family template.
- Fundamental / slow ratio belongs in KB because it is a reusable family template and now has a concrete operating_income / sales branch queued.
- Event trigger / low turnover belongs in KB because it is a reusable template family with clear trigger / exit structure.
- Options / volatility belongs in KB because it is a reusable template family, even when a specific branch is later killed.
- Sentiment / news attention belongs in KB because it is a reusable family template with multiple smoothing windows.
- Alpha and risk factors belongs in KB because it is a reusable classification / neutrality family rather than a single formula.

## Project-Local Only

- Single-post formulas and comments stay project-local until they recur in multiple threads or multiple simulation batches.
- One-off workaround language stays project-local until it proves reusable.
- Any formula that already failed cleanly on TEST should remain a negative control, not a promoted method.

## Why This Belongs In Promotion Review

- The same scaffold recurs across the community posts: source + transform + window + grouping / neutralization + risk control.
- The workflow rules are method-level and independent of the current alpha status labels.
- The template families are concrete enough to seed new alpha branches, but they are still not candidate-ready just because they appeared in the forum.

## Current Judgment

- Skill layer: the forum crawl reinforces existing skill rules; no urgent new skill file is required unless we want a narrower forum-crawl workflow section.
- KB layer: the new external KB pages are the right place for the reusable template families.
- Project layer: the captured forum evidence and the current operating_income / sales branch should stay in the project until real simulation results prove the new lane.

## Promotion Posture

- Status: `REVIEW`
- Destination guidance: keep the skill layer unchanged for now, keep the reusable templates in KB, and keep the project runs as the evidence layer.

## Deeper Skill Verdict

- The five `skill-candidate` heuristics from the crawl are real workflow rules, but most of the same discipline already exists in the current WorldQuant skill's hypothesis-first, early-triage, and branch/kill guidance.
- Because of that overlap, there is no urgent case for a broad skill rewrite just to absorb these forum findings.
- The one skill-level hook that may still be worth adding later is a narrow `forum-backed template mining` workflow: crawl evidence, split it into workflow rule / template family / project-local snippet, and only promote items after they recur across threads or cycles.
- Until that narrower hook proves repeatedly useful, keep the forum-mining logic as project + KB material rather than hard-coding it into the skill core.
