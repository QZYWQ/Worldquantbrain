# Batch S0 Screening Workflow

## Overview
Batch S0 screening is a fast pre-filter for a field candidate batch. It expands a field list into a set of simple expression controls, removes exact duplicates, ranks the survivors, and surfaces the top N candidates for deeper incubation.

## Preconditions
- A LENS recon report exists for the current domain.
- `scripts/dedupe_gate.py` and `scripts/result_ledger.py` are available.
- The field candidate JSON file is filled from the template.
- Paths are resolved from the repository root, not from the current shell directory.

## Field List Filling Guide
| JSON field | Meaning | Source |
| --- | --- | --- |
| `batch_id` | Unique batch identifier such as `YYYY-MM-DD-domain-batch-NN` | Manual |
| `source` | Short description of the batch source | LENS report |
| `source_report` | Relative path to the source recon report | LENS report |
| `fields[].name` | Exact field name spelling | Data Explorer |
| `fields[].source_domain` | Dataset or domain label | Data Explorer |
| `fields[].type` | Field type such as `MATRIX` or `VECTOR` | Data Explorer |
| `fields[].coverage` | Coverage ratio on a 0-1 scale | Data Explorer |
| `fields[].user_count` | Number of users already using the field | Data Explorer |
| `fields[].alpha_count` | Number of existing alphas using the field | Data Explorer |
| `fields[].priority` | Local priority hint such as `high`, `medium`, or `low` | Analysis |
| `fields[].description` | Original platform description | Data Explorer |
| `template_overrides` | Optional replacement templates for the batch | Analysis |
| `param_overrides` | Optional overrides for decays, neutralizations, or weights | Analysis |

## Sorting Weights
The default ranking score is:

`final_score = 0.5 * (1 / (alpha_count + 1)) + 0.3 * coverage + 0.2 * complexity_score`

Where `complexity_score = 1.0` for simple templates and `0.5` for nested templates.

The weights can be overridden in the JSON file via `param_overrides.sort_weights`.
Sorting keeps simple templates ahead of nested templates, then applies the score within each complexity tier.

## Operating Steps

### Step 1: Prepare the field list
Copy the template file, then fill in the field list from the LENS recon report.

### Step 2: Dry-run preview
```bash
python3 scripts/batch_s0_scan.py --fields runs/research-contracts/field_candidates.json --run-mode dry
```
Review the candidate count, duplicate filtering, ranking order, and top recommendations.

### Step 3: Review the plan
Check for spelling errors, overly crowded fields, or obvious template mismatches before any later live integration work.

### Step 4: Live execution placeholder
```bash
python3 scripts/batch_s0_scan.py --fields runs/research-contracts/field_candidates.json --run-mode live --top 3
```
The current repository version keeps live interaction as a placeholder and does not call platform APIs.

### Step 5: Analyze results
- Review the top 3 by TEST Sharpe and Fitness once real results exist.
- Promote successful candidates into the deeper incubation workflow.
- Record failed batches as learning loops.

## Relationship to Deep Incubation
- Batch S0 is a pre-filter before A-stage incubation.
- It does not replace the deeper A -> B -> C -> D -> E workflow.
- It is intentionally looser than the deep-incubation gate to reduce the chance of missing a promising field.
