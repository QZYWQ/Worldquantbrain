# 2026-04-25 Bootstrap And Sign-Flip Enforcement

## Conclusion

The project now has a code-level path for the two process issues that kept leaking through chat memory:

- fresh windows now get the bootstrap protocol embedded directly into generated resume/session briefs
- simulation captures can declare a required sign-flip source index, and the validator enforces that the immediate next control is the sign-flipped final executable expression

This turns the rule from a note in `AGENTS.md` into a repeatable project artifact check.

## Evidence

- `harness/lib/report_documents.py` now injects a `Fresh-Window Protocol` section into both `resume-brief` and `session-open` output.
- `harness/lib/content-validator.py` now checks `batch_policy.required_sign_flip_source_index` for simulation captures and rejects captures that skip the required sign-flip control.
- `templates/simulation-capture.template.json` now carries the batch-policy field so new captures have a standard place to record the trigger.
- `harness/tests/content-validator.sh`, `harness/tests/session-open.sh`, and `harness/tests/resume-brief.sh` now exercise the new behavior.

## Practical Rule

- If the baseline or first simple control Sharpe is negative, write the next control as `-expr` or `-1 * expr` and record the triggering index in `batch_policy.required_sign_flip_source_index`.
- If the sign-flipped control is still weak, freeze or rotate instead of polishing the original sign.

## Verification

- `bash ./harness/tests/content-validator.sh`
- `bash ./harness/tests/session-open.sh`
- `bash ./harness/tests/resume-brief.sh`

## Residual Note

- `bash ./harness/tests/all.sh` still reports an unrelated `local-alpha-loop.sh` count mismatch in the existing worktree; this change did not touch the local-alpha-loop code path.
