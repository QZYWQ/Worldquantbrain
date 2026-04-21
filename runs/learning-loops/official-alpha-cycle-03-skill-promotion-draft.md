# Skill Promotion Draft

## Promotion Posture
- Status: `REVIEW`
- Source cycle: `./harness/cycles/official-alpha-cycle-03.json`
- Source report: `./harness/reports/official-alpha-cycle-03-report.md`

## Candidate Rules
- Add a post-submit operating rule: keep OS monitoring separate from the next research lane, and do not reopen manual submission review for a locked submitted alpha.
- Add a hard gate before candidate-batch generation: require non-null real submission-check or subuniverse evidence; otherwise block the feature instead of fabricating a batch.
- Add a fast-kill heuristic for fresh families: if the direct-sign control remains far below candidate quality after the first simple batch, demote the family and switch lanes.

## Why This Is Or Is Not Ready
- Candidate items are workflow-level and supported by durable outputs plus real blocking evidence.
- Promotion should still update the skill conservatively, as a process rule rather than a signal verdict.

## Destination Guidance
- Promote only workflow-level rules into the WorldQuant skill.
- Keep signal-specific claims, field judgments, and current platform facts out of the skill body.

## Promotion Checklist
- Rewrite each item as a stable execution rule or gating rule.
- Check that the new rule tightens rigor without slowing trivial work unnecessarily.
- Verify the rule does not conflict with existing hard rules in the skill.

