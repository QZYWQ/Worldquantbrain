# 2026-05-02 Automation Low-Efficiency Root Cause

Date: 2026-05-02

## Question

The automation pipeline is producing many low-value WorldQuant BRAIN alpha candidates. Recent official manual review also showed that the `2026-05-01` and `2026-05-02` unsubmitted pools contain many high-headline-metric but low-rescue-probability alphas.

This memo records why the current automation is inefficient and what needs to change before spending more official simulation budget.

## Short Answer

The project already has several good governance modules, but the actual candidate-production path is still too weakly connected to them.

The main problem is not lack of mutation volume. The problem is that the generator optimizes an offline surrogate objective that rewards syntactic novelty and ledger-derived structure more than official pass probability. As a result, it keeps manufacturing candidates that look different locally but are obviously bad by WQB standards: polluted fields, group labels used as raw signals, diagnostic operators treated as alphas, identity ratios, narrow-book model-derivative expressions, and families already known to fail official gates.

## Evidence From Current Code

### Evolution score is not pass-probability aligned

In `harness/lib/evolution/evolution_config.json`, the default scoring weights are:

- `base = 0.3`
- `novelty = 0.5`
- `complexity = 0.18`
- `risk = 0.05`

This makes novelty the largest explicit score component. In `harness/lib/evolution/engine.py`, novelty is computed from operator and field token Jaccard distance, then added directly into `surrogate_score`. That means a candidate can score better simply by introducing strange fields or unusual operator combinations, even when the expression is economically meaningless or structurally likely to fail official gates.

The current score does not directly model:

- Weight concentration risk
- Long / short book breadth
- Sub-universe failure risk
- Fitness repair probability
- Self-correlation risk versus already submitted alphas
- Whether a field is a real WQB data field or a project artifact token

### Mutation field pool is polluted

In `harness/lib/evolution/mutation.py`, `_mutate_field()` builds the replacement pool from:

- fields in the current expression
- config `known_fields`
- compiler `known_fields`

There is no role/type distinction between:

- real numeric signal fields
- group fields such as `industry`, `sector`, `subindustry`
- project artifact names
- generated batch labels
- diagnostic or intermediate labels

Observed generated expressions include project artifact tokens as if they were official WQB fields:

- `fundamental_model_slow_ratio_equity_cap_follow_up_batch_04`
- `fundamental_model_slow_ratio_equity_cap_follow_up_batch_11_api_checks`
- `news_attention_qcm_branch_batch_01`

### Group fields are being used as raw alpha signals

Generated candidates include expressions such as:

- `group_sum(ts_rank(industry/close, 60), industry)`
- `group_rank(ts_rank(subindustry/close, 48), industry)`
- `ts_median(subindustry, 60)`

This is a semantic/type failure. Group identifiers should normally appear as grouping arguments to group operators, not as numeric time-series signals or arithmetic operands.

### Diagnostic operators leak into production candidates

Generated candidates include:

- `ts_count_nans(...)`
- `bucket(...)`

These are useful for dataset diagnostics, coverage analysis, or bucketing designs, but they should not be treated as normal production alpha expressions unless the mode is explicitly `dataset-diagnostic`.

### Identity and near-constant expressions still leak

Previous generated candidates included:

- `anl4_afv4_median_eps/anl4_afv4_median_eps`
- `close/close`

`engine.py` now has a trivial identity guard for direct division/subtraction, but generated history shows the validator needs broader semantic checks, including identity under wrappers and group operators.

### Winner / ledger source may be too permissive

`harness/lib/evolution/population.py::load_winners_from_ledger()` loads rows using:

- `status_values = ["passed"]`
- `min_sharpe = 0.0`

The code should be audited to confirm that `status = passed` means true official full-gate pass, not a local / dry-run / partial pass. If the seed source contains locally convenient but officially weak rows, the evolution engine will amplify bad families.

### S0 scan ranking is too primitive

`scripts/batch_s0_scan.py` has:

- `alpha_count = 0.5`
- `coverage = 0.3`
- `template_complexity = 0.2`

That ranking is field/template oriented. It does not penalize known official failure mechanisms strongly enough:

- `CONCENTRATED_WEIGHT`
- `LOW_SUB_UNIVERSE_SHARPE`
- persistent `LOW_FITNESS`
- self-correlation conflicts
- tiny long/short books
- project artifact token pollution
- group fields used as numeric operands

## Evidence From Generated Batches

A focused scan of recent evolution outputs showed obvious semantic pollution:

| File | Total | Artifact fields | Group-as-signal | Diagnostic ops | Identity ratios |
| --- | ---: | ---: | ---: | ---: | ---: |
| `runs/evolution/generations/gen_001.json` | 20 | 2 | 2 | 0 | 2 |
| `runs/evolution/generations/opt-r1/gen_001.json` | 20 | 1 | 2 | 2 | 0 |
| `runs/evolution/generations/opt-r1/gen_002.json` | 20 | 5 | 2 | 1 | 0 |
| `runs/evolution/generations/opt-r1/gen_003.json` | 20 | 5 | 1 | 1 | 0 |

This is enough to explain low official efficiency. A meaningful fraction of the generated population should be rejected before any official simulation.

## Relationship To Recent Official Rescue Review

The official May1 / May2 rescue review concluded that the remaining high-Sharpe unsubmitted pools are mostly low-probability rescue candidates:

- model-derivative families often have strong headline Sharpe but fail `CONCENTRATED_WEIGHT` through tiny books
- fscore variants can show extreme Sharpe but fail high turnover and concentration
- risk-field variants are broad but cannot reach Fitness after reasonable repairs
- close-delta variants improve with decay but still fail Fitness
- sign-flip repairs can get near the gate but fail Sub-universe and quickly run out of cheap rescue levers

Relevant project evidence:

- `runs/submission-memos/2026-05-02-may1-may2-rescue-deep-review.md`
- `runs/learning-loops/2026-05-02-may1-may2-rescue-stop-project-lessons.md`
- `runs/simulation-captures/2026-05-02-deep-recheck-may1-may2-summary.json`
- `runs/simulation-captures/2026-05-02-deep-recheck-may1-may2-checks.json`

The automation should learn from those official failure shapes. Currently, the evolution and S0 paths do not appear to use this negative memory as a hard enough pre-simulation filter.

## Root Causes

1. **Wrong optimization target**
   The offline surrogate score is optimized for novelty and structural variation, not expected official pass probability.

2. **Weak semantic validation**
   The compiler can say an expression is syntactically valid while the expression is economically or type-wise nonsense.

3. **Field role contamination**
   Project artifact labels and group identifiers leak into the numeric signal field pool.

4. **Diagnostic tooling mixed with alpha production**
   Operators that should support coverage / diagnostics are treated as production candidates.

5. **Gate modules are not wired into the critical path**
   The project has `field_readiness`, `research_contract`, `mechanism_failure_memory`, `economic_distinctness`, and `evidence_ladder` modules, but the evolution engine and S0 scan still let bad expressions reach candidate batches.

6. **Negative official memory is too soft**
   Known official failures should become blocking or heavy-penalty features, not just notes.

7. **Winner seed hygiene is uncertain**
   The ledger loader should verify that seeds are true official winners or explicitly label them as local / partial evidence.

## Recommended Architecture Fix

Add a production candidate gate between expression generation and ranking.

Required gate layers:

1. `semantic_expression_gate`
   - reject project artifact tokens
   - reject group fields outside grouping arguments
   - reject diagnostic operators in production mode
   - reject identity / near-constant arithmetic
   - reject unit-unsafe arithmetic between group labels and numeric fields

2. `official_failure_prior_gate`
   - block or heavily penalize families whose known official failures match the candidate mechanism
   - include concentration, Sub-universe, self-correlation, persistent low Fitness, and high turnover patterns

3. `pass_probability_score`
   - replace novelty-heavy score with a score that estimates official gate pass probability
   - novelty should be a tie-breaker after validity and passability, not the main reward

4. `seed_hygiene_gate`
   - only true official full-gate submissions should be used as high-trust winners
   - local / partial / dry-run passes should be stored separately and weighted lower

5. `S0 ranking upgrade`
   - rank by expected official value per simulation slot
   - include mechanism failure memory and semantic gate results
   - require explicit reason when a known-failed mechanism is allowed through

## Priority Remediation Plan

### P0: Stop wasting official slots

- Add semantic gate tests for the invalid examples in this memo.
- Make candidate export skip expressions that fail the semantic gate.
- Do not run official simulations from evolution output until P0 tests pass.

### P1: Rewire scoring

- Lower novelty weight substantially.
- Add hard penalties for concentration-prone mechanisms and tiny-book signatures.
- Add official-failure-memory features to candidate metadata.

### P2: Clean seed source

- Audit `result_ledger.db` status semantics.
- Split true official full passes from local / partial / dry-run rows.
- Rebuild `known_fields` from verified field-search / official field sources, not generated artifact names.

### P3: Improve batch S0 triage

- Replace field-count / coverage / template-complexity sorting with pass-probability-aware scoring.
- Penalize known failure mechanisms before official budget assignment.

### P4: Add reporting

Every generated batch should report:

- rejected by semantic gate
- rejected by official-failure prior
- artifact-field rejects
- group-field misuse rejects
- diagnostic-operator rejects
- identity / near-constant rejects
- final candidates eligible for official simulation

## Decision

Do not increase simulation volume yet.

The next best action is an engineering cleanup of the candidate-production path. More official simulations before fixing semantic gates and score alignment will mostly produce more of the same low-value near-pass or structurally invalid candidates.

