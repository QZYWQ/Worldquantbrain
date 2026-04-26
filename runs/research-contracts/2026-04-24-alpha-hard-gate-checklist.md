# Alpha Hard Gate Checklist

## Purpose

Use this checklist before starting a new family or promoting a family from `explore` to `branch`.

Its job is to stop three common failures early:

- field choice before field verification
- parameter polishing before thesis validation
- near-duplicate branches being mistaken for new research

## Gate 0: Family Declaration

Fill these in before writing or editing the first expression.

- [ ] One-sentence thesis written in plain language.
- [ ] Primary information source chosen from only one family:
  - [ ] analyst / sentiment
  - [ ] fundamentals / slow ratio
  - [ ] price-volume / short horizon
  - [ ] event / low turnover
- [ ] Family key assigned.
- [ ] Family state assigned: `explore`, `branch`, `hold`, `kill`, or `exploit`.
- [ ] Explicit kill condition written.
- [ ] Explicit reason this family is distinct from the last killed family written.

If any item is missing, do not simulate yet.

## Gate 1: Data Readiness

Check the field before the expression.

- [ ] Field exists in the current account's Data Explorer.
- [ ] Region, delay, and universe match the intended simulation setup.
- [ ] Field type is understood: `MATRIX`, `VECTOR`, `GROUP`, or other.
- [ ] Coverage and date coverage are acceptable for the thesis.
- [ ] Crowding is checked through alpha count / user count, not ignored.
- [ ] Any known missingness / NaN / backfill policy is explicit.
- [ ] Any vector-to-matrix handling is explicit.

Hard stop:

- if the field does not exist on the account, kill the branch or replace the field before any batch
- if coverage is too sparse for the thesis, do not rescue it with window polishing alone

## Gate 2: Mechanism Clarity

The first batch must explain itself.

- [ ] The expression has one main economic idea.
- [ ] The sign is stated explicitly and tested directly.
- [ ] The group / neutralization choice is justified.
- [ ] The lookback window matches the thesis horizon.
- [ ] The expression does not mix multiple unrelated theses.
- [ ] The expression is readable enough that the first failure will be diagnosable.

Hard stop:

- if the family needs three or more unrelated levers to make sense, it is too vague
- if the sign cannot be explained in one sentence, do not branch further

## Gate 3: Minimal First Batch

The first batch should answer one question, not ten.

- [ ] Baseline sign control included.
- [ ] One sibling field included, if available.
- [ ] One horizon control included.
- [ ] One structural control included only if it probes a genuinely different mechanism.
- [ ] No extra smoothing layers unless the thesis is already valid.
- [ ] No event gates unless the event itself is part of the thesis.

Hard stop:

- if the first batch changes both thesis and mechanics at once, the result is not interpretable
- if the batch is already complex, it is probably not a first batch

## Gate 4: Result Triage Order

Always read results in this order.

1. field existence / coverage / weight concentration
2. full-IS Sharpe
3. full-IS Fitness
4. sub-universe behavior
5. self-correlation status
6. turnover
7. test-period card

Hard stop:

- do not use a pretty test-period card to override a failing full-IS gate
- do not promote a branch while self-correlation is unresolved or missing

## Gate 5: Branch / Kill Decision

Use the observed failure type, not hope.

### Keep exploring

- thesis is still coherent
- the first batch is informative
- the next change is a true single-axis follow-up

### Branch once

- the thesis is valid
- the next lever is clearly different
- a second probe can still teach something new

### Kill

- sign control is wrong or structurally weak
- repeated smoothing / window changes are the only repairs left
- the family is a near-neighbor of a killed family
- full-IS gate fails twice in a row on the same thesis
- the branch only survives in a misleading test-period view

### Mandatory Negative-Sharpe Control

If the baseline or first simple control has negative Sharpe:

- the next required control is the sign-flipped final executable expression
- use `-expr` or `-1 * expr`
- do not move to lookback, smoothing, neutralization, or group tweaks until the flipped control has been simulated and captured
- if the sign-flipped control is still weak, freeze the family instead of polishing the original sign
- if the formula has multiple legs, flip the final composite expression that drives the PnL, not a cosmetic subterm

### Exploit

- full official gates are passing
- self-correlation is resolved
- the family is not a near-neighbor of a killed line
- the evidence is strong enough to justify scarce official budget

## Gate 6: Submit-Ready Standard

Do not call a line submit-ready unless all of these are true.

- [ ] Real official full-IS gates have been run.
- [ ] No required gate is failing.
- [ ] `SELF_CORRELATION` is resolved to a non-failing status.
- [ ] There is no known killed-family near-neighbor risk.
- [ ] The candidate has project evidence, not just a template or hypothesis.
- [ ] The candidate can be explained without relying on hidden assumptions.

## What Does Not Count

- [ ] A template expression copied from examples.
- [ ] A family that only changed one constant after a bad result.
- [ ] A family that is only “less bad” on the test card while full-IS gates fail.
- [ ] A field that is not actually present on this account.
- [ ] A candidate-batch JSON written before real evidence exists.

## Recommended Operating Rule

If a family fails any hard stop twice, freeze it.

If a family only survives by adding more smoothing, more windows, or more shape tweaks, it is probably not a new alpha family.

If a family clears all gates, promote it into the registry as `exploit` and stop spending exploratory budget on near-duplicates.

## Evidence Anchors In This Project

- `runs/learning-loops/2026-04-24-alpha-framework-postmortem.md`
- `runs/submission-memos/analyst-sibling-submission-memo.md`
- `runs/learning-loops/2026-04-23-daily-alpha-runner-203907.json`
- `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response`
