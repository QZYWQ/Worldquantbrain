# Skill Promotion Candidate

## Scope Guardrail
- Only promote workflow-level heuristics into the WorldQuant skill.
- Do not encode one family, one field, or one cycle outcome as a permanent skill rule.
- Source cycle: `./harness/cycles/official-alpha-cycle-03.json`
- Source report: `./harness/reports/official-alpha-cycle-03-report.md`

## Candidate Skill Rules
- Add a post-submit operating rule: keep OS monitoring separate from the next research lane, and do not reopen manual submission review for a locked submitted alpha.
- Add a hard gate before candidate-batch generation: require non-null real submission-check or subuniverse evidence; otherwise block the feature instead of fabricating a batch.
- Add a fast-kill heuristic for fresh families: if the direct-sign control remains far below candidate quality after the first simple batch, demote the family and switch lanes.

## Explicit Non-Rules
- Do not turn a weak branch result into a global statement that the whole family is always bad.
- Do not weaken evidence requirements just because a branch feels promising.

## Blocking Evidence To Keep In Mind
- Blocked because the analyst-disagreement batch still lacks real subuniverse/check evidence, so no valid candidate-batch JSON can be written without placeholders.

