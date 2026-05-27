# Skill Promotion: New Dataset Intake Gate

## Metadata

- Date: 2026-05-02
- Source post: `https://support.worldquantbrain.com/hc/en-us/community/posts/11807866133911--BRAIN-TIPS-6-ways-to-quickly-evaluate-a-new-dataset`
- Source snapshot: `runs/forum-crawl/2026-04-22-support-worldquantbrain/raw/pages/hc-en-us-community-posts-11807866133911-BRAIN-TIPS-6-ways-to-quickly-evaluate-a-new-dataset-51955fc6ac.txt`
- Promotion target: `/Users/zpdedn/.codex/skills/worldquant-brain-alpha-engineering/SKILL.md`

## Promoted Rule

The WorldQuant BRAIN skill now has a formal `New Dataset Intake Gate`.

Before a new or unfamiliar datafield is expanded into an alpha family, run a diagnostic pack with `None` neutralization and decay `0`, then inspect `Long Count + Short Count` rather than alpha metrics:

- raw field coverage
- non-zero coverage
- update frequency
- value bounds
- long-window center
- normalized distribution bands

## Boundaries Preserved

- This does not confirm that any field is available on the current account.
- This does not change official submission criteria.
- This does not allow diagnostic expressions to be treated as alpha candidates.
- This does not replace official simulation, Test Period, Sub-universe, Self-correlation, or Check Submission evidence.

## Follow-Up Candidate

The forum comment thread mentions adding skewness and kurtosis to automated dataset evaluation. Keep that as a future automation candidate until a local script or repeated project use justifies it.
