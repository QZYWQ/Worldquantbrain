# 2026-04-25 Current Skeleton And Failure Pain Points

## Purpose

This memo is a handoff brief for a second AI. It describes the current WorldQuant BRAIN project skeleton, the real operating state, and the main failure points that are blocking new submit-ready alphas.

## Current State Snapshot

- Harness active cycle: `./harness/cycles/official-alpha-cycle-04.json`
- Harness status: no active feature, session idle
- Submit-ready alpha count in the latest registry snapshot: `0`
- Latest family registry snapshot: `25` families, with `branch=3`, `hold=17`, `kill=5`, `exploit=0`
- Locked / anchor state:
  - `qMmpvp8v` is submitted and locked, with `OS Testing Status = 4 PENDING`
  - `E5repQ81` is the live OS reference alpha only, also `OS Testing Status = 4 PENDING`
- Latest next-step decision: verify `pcr_oi_720` on the official Data Explorer page first, and only spend a minimal first batch if it clears the front-door gate

## What The Project Skeleton Actually Is

### 1) Truth-source hierarchy

The project deliberately separates truth layers:

- Current project state comes from files in this repo first
- Current platform facts come from official WorldQuant BRAIN pages / API first
- The external knowledge base is secondary and should not override current project files or official platform evidence

This is important because the project is not meant to be a chat-memory workflow. It is meant to be reconstructable from artifacts.

### 2) Progressive disclosure / layered governance

The skeleton is intentionally layered:

- `AGENTS.md` defines the high-level project rules
- `00-项目总索引.md` and `02-工作流索引.md` route work to the right artifact type
- `03-代理工程化规则索引.md` routes to the correct policy file only when needed
- `harness/AGENTS.md` handles long-running, resumable, evidence-backed execution

This prevents the agent from reading everything every time, but still gives a deterministic path for long tasks.

### 3) Harness structure

The harness is a long-running execution shell around the research process:

- `active-cycle.txt` points to the current cycle definition
- `progress.md` tracks runtime session state
- `decision-log.md` records durable operational decisions
- `reports/` stores closure and handoff artifacts
- `artifacts/` stores verification evidence

It is explicitly designed to survive context loss across windows.

### 4) Research artifact pipeline

The alpha workflow is staged:

1. official field verification
2. field-search pack
3. expression-family draft
4. first official batch
5. simulation capture
6. live first-batch memo
7. stop / rotate / continue decision
8. registry update or freeze memo

This means the project is not just “write an expression and test it.” It is a source-selection pipeline with artifact checkpoints.

### 5) Mandatory sign-flip protocol

The current skeleton now treats negative Sharpe as a control-flow signal:

- if the baseline or first simple control has negative Sharpe, the next mandatory control is the sign-flipped final executable expression
- the sign flip must be on the final executable expression, not on cosmetic subterms
- do not keep polishing the original sign before the flipped version is simulated and compared

This rule is now backed by project artifacts and harness validation, not just by a note in `AGENTS.md`.

### 6) Decision labels

The family / lane posture vocabulary is:

- `admit`
- `hold`
- `rotate`
- `kill`
- `exploit`

The family registry uses these states to track whether a source deserves more budget, should wait, should stop, or can be promoted.

## What The Skeleton Is Good At

- It preserves long-session continuity better than chat memory alone
- It keeps the work traceable through `runs/` artifacts
- It enforces sign-flip discipline when a baseline is negative
- It is very good at documenting why a lane should stop
- It prevents a lot of accidental reopening of frozen or killed lanes

In short: it is a good execution and stop-loss skeleton.

## What The Skeleton Is Not Good At

- It does not automatically find high-quality new family sources
- It does not reliably rank candidate sources by distinctness and branchability before the first batch
- It does not yet have a strong enough front-door intake filter to prevent budget waste on pseudo-new lanes
- It is stronger at pruning weak ideas than at discovering strong ones

## Core Failure Pain Points

### 1) Family intake is the main bottleneck

The biggest failure is upstream: the project still lets too many weak or near-duplicate families into the first official batch.

The current problem is not mainly expression polishing. It is choosing the wrong source too early.

What keeps happening:

- a field is officially visible, but the source is not actually worth the batch
- the lane looks “new,” but it is really a cosmetic neighbor of a frozen lane
- the first batch reveals that the source is too crowded, too weak, or too unstable

### 2) Cosmetic changes are being mistaken for new family work

The project has already learned that these do not count as real family moves:

- sign flip only
- lookback only
- smoothing only
- group / neutralization tweak only

Those are repair moves, not new family sources.

### 3) Official visibility is necessary but not sufficient

The fact that Data Explorer shows a field does not mean the field deserves budget.

A source must also clear:

- coverage quality
- date coverage
- visible crowding
- economic distinctness from the frozen / locked / active pool
- branchability beyond one cosmetic shape

### 4) IS and TEST often diverge too hard

A common failure mode is:

- IS looks acceptable or even decent
- TEST collapses, flips negative, or stays too soft
- the family does not survive the continuation floor

That means the source is often not robust enough, even when the raw baseline is not terrible.

### 5) The project is better at stopping than selecting

The current system can produce good freeze / stop / rotate memos, but it still struggles to identify a family source that deserves the first batch in the first place.

This is why the project has many postmortems but no submit-ready alpha yet.

### 6) The search space is being exhausted by repeated near-neighbors

Many older lanes are already frozen, killed, or locked:

- model rerating lanes are frozen
- analyst annual-sales / top-line guidance / model valuation / growth-related lanes are already spent
- socialmedia12 is closed
- socialmedia8 is closed
- `pcr_vol_90` and `pcr_oi_30` are frozen after batch 01

That means the remaining search space is getting narrower, and the intake filter needs to be stricter, not looser.

### 7) Budget gets consumed before the lane proves it deserves more

The recurring pattern is:

- official field check passes
- one baseline and a few small variants run
- the first batch shows the lane is not durable
- the family is frozen

This is not a modeling failure alone. It is a source-ranking failure.

### 8) The project skeleton still behaves more like a risk manager than a discovery engine

That is the most important conceptual diagnosis.

The skeleton is good at:

- preventing drift
- preventing memory-based mistakes
- preventing cosmetic reopening of dead lanes

But it is still weak at:

- scoring candidate family quality before batch spend
- separating “interesting” from “worth funding”
- ranking source distinctness against the current anchor pool

## Concrete Examples Of Failure Modes

### Social media lanes

- `socialmedia12-sentiment-fast`:
  - baseline Sharpe was negative
  - sign-flip control improved IS but flipped negative on TEST
  - high turnover and concentration pressure made the family low ceiling
- `socialmedia8-sentiment-value`:
  - direct field was officially visible and simple
  - IS was only modestly positive
  - TEST was strongly negative
  - the family did not clear the continuation floor

### Options PCR lanes

- `pcr_vol_90`:
  - baseline had a weak IS read
  - sign flip just mirrored the same edge
  - the family froze after batch 01
- `pcr_oi_30`:
  - IS was modestly positive
  - TEST was too soft
  - the 360d sibling turned negative on TEST
  - the lane rotated out instead of being polished further

### Options breakeven lane

- `call_breakeven_60`:
  - the family got close on some repairs
  - but it still failed the fitness gate
  - even near-passing sources are not enough if they do not cross the full threshold

These examples matter because they show that the failure is not always “bad expression.” Sometimes it is “not enough source quality,” “wrong source family,” or “crowded near-neighbor.”

## What A Second AI Should Focus On

If another AI is going to analyze this project, the best questions are:

1. How can the project rank candidate family sources before batch spend?
2. What objective front-door gate should distinguish a real family from a cosmetic neighbor?
3. How can crowding, coverage, distinctness, and branchability be scored together?
4. How can the system detect that a source is too close to the frozen / locked / active pool?
5. How should the project decide when to rotate immediately instead of trying another variant?
6. How should the sign-flip protocol and no-cosmetic-neighbor rule be enforced across new windows?

## Short Diagnosis

The skeleton is now solid as an execution harness, but weak as a family discovery engine.

The main pain point is not “we can’t run alphas.”
The main pain point is “we still cannot reliably select a source worth funding before the first batch.”

## Source Trace

- `AGENTS.md`
- `00-项目总索引.md`
- `02-工作流索引.md`
- `03-代理工程化规则索引.md`
- `harness/AGENTS.md`
- `harness/active-cycle.txt`
- `harness/progress.md`
- `harness/decision-log.md`
- `harness/project-surfaces.json`
- `runs/research-contracts/window-bootstrap-and-signflip-protocol.md`
- `runs/research-contracts/2026-04-24-family-registry.md`
- `runs/learning-loops/2026-04-25-next-step-decision.md`
- `runs/learning-loops/2026-04-25-family-intake-postmortem.md`
- `runs/learning-loops/2026-04-25-bootstrap-signflip-enforcement.md`
- `runs/submission-memos/qMmpvp8v-os-status-2026-04-24.md`
- `runs/submission-memos/E5repQ81-os-status-2026-04-24.md`
- `runs/submission-memos/2026-04-25-socialmedia12-sentiment-fast-stop-memo.md`
- `runs/submission-memos/2026-04-25-socialmedia8-sentiment-value-stop-memo.md`
- `runs/submission-memos/2026-04-25-pcr-oi-30-stop-memo.md`
- `runs/submission-memos/2026-04-25-pcr-vol-90-stop-memo.md`
- `runs/submission-memos/2026-04-25-call-breakeven-family-stop.md`
