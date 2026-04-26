# Window Bootstrap And Sign Flip Protocol

## Purpose

Make fresh chat windows usable even when there is no trusted conversational memory.

The project must remain executable from artifacts alone:

- project rules and workflow docs
- official WorldQuant BRAIN pages / API
- durable `runs/` artifacts
- harness state when long-running work is involved

Chat memory is helpful, but it is not the source of truth.

## Stateless Bootstrap Order

When a new window starts, or when the current window has no reliable memory of the last research state, rebuild context in this order:

1. `./AGENTS.md`
2. `./00-项目总索引.md`
3. `./02-工作流索引.md`
4. `./harness/AGENTS.md` if the task may span sessions or needs tracked state
5. `./runs/research-contracts/current-incubation-summary.md`
6. `./harness/incubation-protocol.json`
7. the latest family registry
8. the latest next-step decision
9. the latest freeze / stop / closure memo
10. the latest official live recheck / submission memo
11. the latest simulation capture
12. the current field-search pack and expression-family for the active lane, if one exists

If one of these artifacts is missing, proceed with the best available project evidence and record the gap explicitly.

## Negative Sharpe Rule

If the baseline or the first simple control has negative Sharpe, the next mandatory control is the sign-flipped final executable expression:

- use `-expr` or `-1 * expr`
- flip the final executable expression, not a cosmetic subterm
- do not continue polishing the original sign before the flipped control has been simulated and compared
- do not spend extra budget on lookback, smoothing, neutralization, or group tweaks until the sign-flipped control is captured

If the sign-flipped control is still weak, freeze the family or rotate away.
Do not keep polishing a negative-sign lane just because it is familiar.

## D-Stage Platform-Blocked Rule

When a D-stage or equivalent robustness check fails because the account cannot evaluate the required path (for example an unknown variable, unavailable operator, blocked delay-0 setting, or similar platform limitation), treat the lane as platform-blocked rather than signal-weak.

- keep the family on hold and reclaim remaining budget to `cold_pool`
- do not keep retrying the same source with cosmetic same-path variants in the same session
- only resume if a genuinely new field, delay, or mechanism removes the blockage

## E-Stage Rescue Cap

After the first official Check Submission failure on a lane, the rescue loop is bounded.

- allow at most two targeted rescue variants
- each rescue variant should change only one major lever and should target the dominant failing check
- if the same core failure persists after the cap, branch away or keep the lane on hold instead of sweeping more cosmetic edits

## Machine-Readable Capture Policy

When you write a simulation capture for a batch that triggered the negative Sharpe rule:

- set `batch_policy.required_sign_flip_source_index` to `0` for a negative baseline or `1` for a negative first simple control
- write a short `batch_policy.required_sign_flip_reason`
- keep the sign-flipped control immediately after the negative source control in the `alphas` array

This is the field-level contract that the content validator enforces for new captures.

## Memoryless Window Rule

Treat a fresh window as stateless until project artifacts are loaded.

- Chat history is advisory only.
- Project files are binding when they exist.
- Official platform data wins for current platform facts.
- If chat memory and project artifacts conflict, trust the project artifacts and official pages.

## First Actions In A Fresh Window

1. Reconstruct the current open lane from `./runs/research-contracts/current-incubation-summary.md`.
2. Confirm which family, if any, is active.
3. Confirm whether the current lane is explore, branch, hold, kill, freeze, or exploit.
4. Check whether the next required action is a field check, a field-search pack, an expression-family draft, or a sign-flipped control.
5. Only then consider writing new research artifacts or running simulations.

## Operational Reminder

This protocol exists to stop two failure modes:

- starting from memory and drifting away from the project truth
- polishing the wrong sign when the first result is already telling you to flip

It is a project execution rule, not a suggestion.
