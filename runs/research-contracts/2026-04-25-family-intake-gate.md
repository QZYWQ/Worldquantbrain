# Family Intake Gate

## Purpose

Use this gate before creating a new `field-search-pack` or `expression-family`.

Its job is to stop the two biggest research leaks:

- spending batch budget on a pseudo-new family that is only a cosmetic neighbor of a killed lane
- spending batch budget on a source that is officially visible but too crowded, too thin, or too close to the current pool to be worth a first probe

This gate sits in front of `runs/research-contracts/2026-04-24-alpha-hard-gate-checklist.md`.
If a family fails here, do not move on to the harder expression-level checklist.

## Truth Sources

Only use these sources for gate decisions:

- official WorldQuant BRAIN pages / API
- project `runs/` artifacts

For current platform behavior, the official submission page and simulation docs are the binding source.

## No-Memory Bootstrap

When the current window has no reliable memory of the active lane, reconstruct state before making any family decision.

Load, at minimum:

- `./AGENTS.md`
- `./00-项目总索引.md`
- `./02-工作流索引.md`
- `./runs/research-contracts/window-bootstrap-and-signflip-protocol.md`
- the latest family registry
- the latest next-step decision
- the latest freeze / stop / closure memo
- the latest official live recheck / submission memo
- the latest simulation capture

Do not treat chat history as binding if those artifacts exist.

## Gate Order

### Gate 0: Family Declaration

Write a one-sentence thesis before anything else.

Required:

- one plain-language mechanism
- one primary data category
- one intended holding horizon
- one explicit kill condition
- one explicit reason this family is not just a near-neighbor of a frozen or killed lane

Hard stop:

- if the thesis needs two unrelated mechanisms, split it into two families
- if the sign cannot be explained in one sentence, do not simulate yet

### Gate 1: Official Field Verification

Verify the source on the official Data Explorer page for the current region, delay, and universe.

Record:

- field name
- dataset / category
- field type
- coverage
- date coverage
- visible alpha count

Minimum expectation:

- the field must exist in the current account view
- the field must match the intended `USA / D1 / TOP3000` style setup, unless there is a deliberate reason to leave that lane
- the field type must be understood before the first batch

Hard stop:

- if the field is not visible in the current account, hold or kill the family
- if the family only works by pretending a missing field exists, kill it

### Gate 2: Distinctness From Frozen Memory

Check whether the family is economically distinct from the current frozen / locked / active pool.

Material differences include:

- new data category
- new mechanism
- new comparison frame
- new gating condition
- genuinely different universe or delay logic

Non-differences that do **not** qualify as a new family:

- sign flip only
- lookback only
- smoothing only
- neutralization / group tweak only
- cosmetic parameter retuning around the same thesis

Hard stop:

- if the only change is a cosmetic neighbor move, do not call it a new family
- if the family is a near-neighbor of a frozen lane and the failure mode is the same, kill or hold it

### Gate 3: Coverage, Crowding, and Branchability

Ask whether the field can support a real family rather than a one-off.

Check:

- coverage is enough to support the thesis without heavy patching
- date coverage is not misleadingly sparse
- crowding / visible alpha count is acceptable for the intended use
- the source can plausibly generate at least 3 non-cosmetic variants

Heuristic interpretation:

- high coverage is a strong plus, but not enough by itself
- moderate coverage can still be usable if the economic source is distinct and the thesis is clean
- very sparse coverage is only acceptable if the family is intentionally sparse and the first batch can prove why it deserves attention

Hard stop:

- if the family only survives by smoothing or backfilling away the sparsity, hold it
- if only one shape works and all other variants are cosmetic, the source is too weak to promote

### Gate 4: Baseline Plausibility

The first baseline must be explainable before it is optimized.

Required:

- one baseline expression that directly matches the thesis
- one sign-control expression
- one or two sibling controls that change a single meaningful axis

Do not let the first batch mutate multiple axes at once.

Good axes:

- field axis
- comparison frame axis
- gating axis
- true horizon axis
- true data source axis

Bad axes when used alone as the only change:

- sign only
- lookback only
- smoothing only
- group tweak only

Hard stop:

- if the baseline needs three or more unrelated levers to become readable, it is not ready
- if the first control is obviously just a retune of the baseline, it does not count as a real branch

### Gate 5: First-Batch Budget Contract

Only spend the first official batch if Gates 0 to 4 pass.

Batch shape:

- 1 baseline
- 1 sign control
- 2 sibling controls

Budget rule:

- one family, one batch, one dominant thesis
- do not spread the first batch across unrelated ideas
- do not turn the first batch into a parameter sweep

## Decision Labels

### `admit`

Use when:

- the field is official and visible
- the source is materially distinct
- the crowding / coverage balance is acceptable
- the baseline is readable
- the family can branch meaningfully

Action:

- write the `field-search-pack`
- write the `expression-family`
- run the minimal first batch

### `hold`

Use when:

- the family is plausible but one gate is not yet strong enough
- the source needs a second official confirmation
- the family is distinct enough to revisit but not good enough for immediate budget

Action:

- do not run a batch yet
- keep the family in the queue
- revisit only if a more distinct or better-covered source appears

### `rotate`

Use when:

- the family had a first batch but the evidence says the lane should stop
- the family is not dead in theory, but it is not the best use of the next hour

Action:

- freeze the lane for the current budget
- move to the next source family

### `kill`

Use when:

- the family is a cosmetic near-neighbor of a killed lane
- the family repeatedly fails the same structural reason
- the source cannot support a clean first batch
- the only surviving repairs are sign, window, smoothing, or grouping retunes

Action:

- stop the lane
- do not reopen it unless a genuinely new source or mechanism appears

### `exploit`

Use when:

- the family has cleared real official gates
- self-correlation risk is understood or resolved
- the source is distinct enough to justify scarce budget

Action:

- promote into the registry as a serious candidate
- stop spending exploratory budget on near-duplicates

## Current Source Queue Snapshot

This is the current queue as of `2026-04-25`.
It is a snapshot, not a permanent ranking.

1. `anl4_af_eps_value` / actual-EPS style analyst source
   - status: `admit-to-probe`
   - why: strongest mix of coverage, crowding, and economic distinctness so far
   - caution: do not let it collapse back into a close-price ratio clone of an already-locked alpha

2. `option_breakeven_30`
   - status: `hold -> next candidate`
   - why: fresh options analytics source with enough structure to justify a first probe
   - caution: treat as its own mechanism, not as a retuned `put_breakeven_60` lane

3. `call_breakeven_60`
   - status: `hold -> sibling candidate`
   - why: still a distinct options source, useful only if it is not just a mirror of the already-frozen put family
   - caution: do not reopen `put_breakeven_60` by a side door

4. `snt_social_value`
   - status: `probe only`
   - why: official social-media coverage is real and the field is easy to explain
   - caution: crowding is high, so this is a short diagnostic lane, not a durable primary source by default

5. `socialmedia8`
   - status: `freeze`
   - why: the first batch was negative on TEST and the lane already earned a stop memo
   - caution: do not reopen on sign / lookback / smoothing / grouping tweaks

6. `socialmedia12`
   - status: `kill`
   - why: the fast lane had low ceiling and the sign-flip control did not rescue it
   - caution: do not reopen

7. `put_breakeven_60`
   - status: `freeze`
   - why: the first batch failed on Fitness and concentration
   - caution: do not reopen on cosmetic variants

## Intake Card

Fill this in before writing any new family documents.

- Family key:
- One-sentence thesis:
- Official field page URL:
- Region / delay / universe:
- Dataset / category:
- Field type:
- Coverage / date coverage:
- Visible alphas / user count:
- Why this is distinct from the frozen pool:
- Which old family it is *not*:
- Baseline expression:
- Sign-control expression:
- Two sibling controls:
- Likely first failure:
- Decision: `admit`, `hold`, `rotate`, `kill`, or `exploit`

## Relation To The Existing Hard Gate

If a family passes this front-door gate, the next step is the harder expression and execution checklist in:

- `runs/research-contracts/2026-04-24-alpha-hard-gate-checklist.md`

That checklist handles expression readability, first-batch shape, triage order, and submit-ready discipline.
This gate only decides whether a family deserves to get that far.

## Evidence Anchors

Official docs:

- `https://platform.worldquantbrain.com/learn/documentation/interpret-results/alpha-submission`
- `https://platform.worldquantbrain.com/learn/documentation/create-alphas/simulation-settings`
- `https://platform.worldquantbrain.com/learn/documentation/create-alphas/how-brain-platform-works`
- `https://platform.worldquantbrain.com/learn/documentation/examples/sample-alpha-concepts`

Project artifacts:

- `runs/learning-loops/2026-04-25-family-intake-postmortem.md`
- `runs/learning-loops/2026-04-25-next-step-decision.md`
- `runs/research-contracts/2026-04-24-family-registry.md`
- `runs/research-contracts/2026-04-24-alpha-hard-gate-checklist.md`
- `runs/submission-memos/2026-04-25-socialmedia12-sentiment-fast-stop-memo.md`
- `runs/submission-memos/2026-04-25-socialmedia8-sentiment-value-stop-memo.md`
- `runs/submission-memos/2026-04-25-put-breakeven-60-live-first-batch.md`
- `runs/submission-memos/2026-04-24-actual-eps-live-recheck.md`
- `runs/submission-memos/2026-04-24-actual-eps-subindustry-recheck.md`
