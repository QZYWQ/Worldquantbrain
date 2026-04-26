# 2026-04-27 S0 Failure Pattern Response

## Background

- Seven consecutive S0 failures were observed across the recent scouting flow: qfv4 x3, profitability/value x4.
- The growth rerating path was initially misread, which reinforced the need to verify the field directly in Data Explorer before generating the scout.
- The corrected `growth_potential_rank_derivative` probe cleared S-1 but failed S0, confirming that source novelty alone was not enough to justify deeper budget.
- This note records the decision response so the next window starts from the corrected research posture.

## Root Cause

- The process over-relied on field-search-pack logic and directional inference instead of cross-checking the actual Data Explorer novelty of the field.
- That made model-label similarity look like diversification even when the candidate source was not yet independently verified.
- The result was repeated same-lane polishing before the information source was fully validated.

## Correction

- Future S-1 candidate generation must browse at least one new data domain before scout creation.
- Prefer fields whose statistical distribution or delay behavior is visibly different from the current anchor pool, rather than fields that are only semantically adjacent by model label.
- Treat a search miss during S-1 as pending_verification, not source_missing.

## Protocol Supplement

- The new rule is recorded in `harness/decision-log.md` because `harness/incubation-protocol.json` has no safe schema slot for a direct inline flag update.
- The intended future protocol addition is:
  - `s1_precheck_require_dataexplorer_verification: true`
  - `s1_precheck_verification_note: Field must be located in Data Explorer before scout generation; search failures are pending_verification, not source_missing.`

## pcr_oi_720 Downgrade

- `pcr_oi_720` remains frozen at resurrection priority C until a new orthogonal family clears S0 with robust fitness.
- Last E-stage repair candidates: `ZYWOgoMY`, `3qn8XVVX`.
- Both repairs were constrained by `LOW_FITNESS`.

## Output

- Frozen pipeline list written to `runs/research-queues/2026-04-27-frozen-pipeline.md`.
- Idle-window workspace cleanup is complete and is being committed together with the captured live probe evidence.
