# Learning Loop: Dedupe Gate + Result Ledger Integration

## Source
- worldquant-miner deep analysis identified the `generation_two/template_similarity` style gate and the `backtest_storage` style ledger as the safest integration seed.

## Delivered Artifacts
- `scripts/dedupe_gate.py` — three-tier local duplicate gate
- `scripts/result_ledger.py` — SQLite result ledger and backfill helper
- `runs/research-contracts/2026-04-27-lite-sop.md` — updated with the S-1.5 dedupe step
- `scripts/lite-scout.sh` — updated with the dedupe placeholder

## Expected Effect
- Reduce duplicate simulation noise before S0
- Preserve a durable local history layer for every future incubation decision
- Keep the integration offline, deterministic, and compatible with the existing LITE workflow

## Integration Principle
- Low risk
- No platform API calls
- No protocol changes
- Historical evidence lives in `runs/evidence/`

## Date
- 2026-04-27
