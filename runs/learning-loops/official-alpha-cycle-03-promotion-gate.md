# Promotion Gate

## Metadata
- Generated at: 2026-04-20T03:03:27+0800
- Source cycle: `./harness/cycles/official-alpha-cycle-03.json`
- Source report: `./harness/reports/official-alpha-cycle-03-report.md`

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
- Candidate heuristics exist and the cycle left at least two durable outputs.
- Keep the scope at method-level guidance, not family-level verdicts.
- Candidate items:
- Post-submit cycles should treat the submitted alpha as locked while OS remains unresolved, and move follow-up research to a separate branch.
- A new family should get a cheap first sign/control test before spending more time on candidate packaging or same-family polishing.
- If real subuniverse or submission-check evidence is missing, record a blocked memo instead of backfilling a candidate-batch JSON with placeholders.

## Skill Gate
- Status: `REVIEW`
- Minimum bar:
- Rule is workflow-level, not alpha-family-specific.
- Rule tightens evidence, prioritization, or branch-kill discipline.
- Rule does not weaken existing hard rules in the WorldQuant skill.
- Current readout:
- Candidate items are workflow-level and supported by durable outputs plus real blocking evidence.
- Promotion should still update the skill conservatively, as a process rule rather than a signal verdict.
- Candidate items:
- Add a post-submit operating rule: keep OS monitoring separate from the next research lane, and do not reopen manual submission review for a locked submitted alpha.
- Add a hard gate before candidate-batch generation: require non-null real submission-check or subuniverse evidence; otherwise block the feature instead of fabricating a batch.
- Add a fast-kill heuristic for fresh families: if the direct-sign control remains far below candidate quality after the first simple batch, demote the family and switch lanes.

## Explicit Do-Not-Promote Cases
- Current account-specific field availability claims.
- One-cycle verdicts like 'family X is always bad'.
- Temporary UI or OS-status states that belong to official re-check, not long-term method knowledge.

## Next Action
- If status is `REVIEW`, inspect the candidate file and decide whether to promote it into the external KB or the skill in a separate deliberate change.
- If status is `HOLD`, keep the lesson in the project layer and wait for repeated evidence from later cycles.

