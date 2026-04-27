# Batch S0 Pipeline Learning Loop

## Motivation
Manual candidate-by-candidate screening is too slow for broad field exploration. The batch S0 layer reduces repetitive work by turning a field list into a ranked shortlist automatically.

## Core Design
- Field x template x parameter expansion
- Three-tier dedupe gate integration
- SQLite-backed result ledger reads for historical context
- Deterministic ranking before any later live integration

## Integration Points
- `scripts/dedupe_gate.py` for duplicate checks
- `scripts/result_ledger.py` for historical lookup and local evidence storage
- `runs/research-contracts/field_candidates_template.json` for batch input structure
- `runs/research-contracts/2026-04-27-batch-s0-workflow.md` for operator instructions

## Safety Design
- Default run mode is dry-run
- Maximum batch size is capped by `--max-simulations`
- Platform interaction is left as explicit PLACEHOLDER comments
- Paths resolve from the repository root to avoid stray writes under `scripts/runs/`

## Current Limits
- Live submission is not implemented in this offline skeleton
- The script only prepares plans, dedupe output, and ranking output
- Real platform submission can be wired in later without changing the batch shape
