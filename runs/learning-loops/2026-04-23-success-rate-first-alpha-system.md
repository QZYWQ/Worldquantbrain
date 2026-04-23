# Success-Rate-First Alpha System

## Metadata
- Date: 2026-04-23
- Scope: durable design note only
- Worker: D
- Evidence status: no alpha metrics, official checks, or candidate-batch records are asserted here

## Objective
Maximize internally submit-ready alphas per official submission slot.

The system should treat official slots as scarce. More simulations are useful only when they improve the probability that a consumed official slot is backed by a genuinely submit-ready alpha.

## Internal Submit-Ready Gate
An alpha is internally submit-ready only when all requirements are satisfied:

- Real official full-IS gates have been run and every gate is non-failing.
- `SELF_CORRELATION` is resolved to a non-failing status; missing, pending, failing, or stale self-correlation evidence blocks promotion.
- The alpha is not a near-neighbor of a killed family.
- Evidence comes from real official results or project artifacts derived from those results, not templates, placeholders, hypotheses, or copied examples.

Near-neighbor means the candidate shares the same economic thesis and likely failure mode as a killed family, with only minor field, window, operator, neutralization, or sign changes.

## Family Registry States
Every alpha family should have exactly one registry state:

- `explore`: early evidence gathering with small bounded probes.
- `branch`: one or more evidence-backed variants justify limited expansion.
- `hold`: insufficient priority or budget; do not spend official slots until reopened.
- `kill`: stop generating near-neighbor candidates unless a materially new thesis or evidence source is introduced.
- `exploit`: allocate scarce official checks and submission slots to the best evidenced variants.

State changes must be driven by observed outcomes, not by template expectations or unverified intuition.

## Outcome Memory
Record outcomes by failure type so the scheduler can avoid repeating known dead ends. At minimum, memory should distinguish:

- official gate failure
- `SELF_CORRELATION` failure or unresolved status
- sub-universe or test-period failure
- weak performance readout
- turnover or margin problem
- field or dataset availability problem
- near-neighbor of killed family
- budget-blocked or evidence-missing candidate

Failure memory belongs at both candidate and family level. A killed family should carry the reason it was killed and the boundary of what counts as a near-neighbor.

## Budget Scheduler Hard Limits
The scheduler must enforce explicit hard limits before work starts:

- maximum simulations per batch
- maximum official checks per batch or cycle
- maximum official submission slots available for the cycle
- maximum branches allowed from one family before a hold or kill decision
- maximum retries after the same failure type

If a proposed batch exceeds any hard limit, it should be refused or reduced before execution. Exploration budget should not consume exploit budget unless the user explicitly reallocates it.

## Candidate-Batch JSON Rule
Do not create candidate-batch JSON without real evidence.

A candidate-batch artifact requires real result evidence such as official simulation/check output or a project capture derived from that output. A promising expression, template row, or planned batch is not enough.
