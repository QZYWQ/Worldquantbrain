# Skill Candidate: New Dataset Quick Evaluation Gate

## Scope Guardrail

This is a workflow-level candidate for WorldQuant BRAIN alpha engineering. It should not promote any specific datafield, dataset, or alpha formula as durable truth.

## Source Artifacts

- Forum crawl snapshot: `runs/forum-crawl/2026-04-22-support-worldquantbrain/raw/pages/hc-en-us-community-posts-11807866133911-BRAIN-TIPS-6-ways-to-quickly-evaluate-a-new-dataset-51955fc6ac.txt`
- Existing forum extraction: `runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-excerpts.md`
- Existing catalog: `runs/forum-crawl/2026-04-22-support-worldquantbrain/analysis/template-catalog.md`
- Project lesson: `runs/learning-loops/2026-05-02-new-dataset-quick-eval-project-lessons.md`

## Candidate Skill Rule

When a task involves a new or unfamiliar BRAIN datafield, require a field-health diagnostic pack before alpha-family expansion:

- run diagnostics with `None` neutralization and decay `0`
- inspect `Long Count` and `Short Count` rather than Sharpe or Fitness
- record approximate coverage, non-zero coverage, update frequency, bounds, long-window center, and distribution band behavior
- keep diagnostics out of candidate-batch triage
- block or hold local mining if the diagnostics contradict the intended horizon or show unusable coverage

## Why This Belongs In Skill

- It improves research efficiency before official simulation budget is spent on variants.
- It directly supports the existing skill rule to start from field judgment rather than operator soup.
- It reduces false confidence from Data Explorer metadata alone by forcing empirical field behavior checks.
- It is workflow-level and reusable across field families.

## Anti-Patterns To Add

- Do not generate a family from a new dataset solely because the Data Explorer coverage looks high.
- Do not interpret the diagnostic pack as alpha evidence.
- Do not compare diagnostic expressions with non-`None` neutralization, because boolean constants can be neutralized into zero-like outputs.

## Promotion Posture

- Status: `PROMOTED`
- Promoted at: 2026-05-02
- Promotion target: `/Users/zpdedn/.codex/skills/worldquant-brain-alpha-engineering/SKILL.md`
- Reason: user confirmed the source post is an official tutorial post with unusually high support-community signal; the promoted content is a workflow gate only and does not encode field access, account facts, or platform thresholds.
