# 2026-05-09 Short Interest / Ownership Concentration Research Decision

## Metadata

- Recorded at: 2026-05-09
- Session type: autonomous research queue decision
- API status: RATE LIMITED

## Decision Summary

### Why This Direction

Analyzed all existing research and submission evidence:

1. **E5g7vMjJ** (price/volume correlation) - submitted, ACTIVE
2. **A1gVE97w** (EPS quality/yield) - submitted, ACTIVE/OS
3. **pcr-oi-720** - extensively explored, multiple rescue failures, STOP
4. **assets/cap** - hump rescue failed, STOP
5. **QP2v6rVW** (EPS backup) - self-corr 0.92 FAIL, frozen

**Gap**: No submitted alpha uses **short interest** or **ownership concentration** as primary signal.

### Hypothesis Selected

**Short Interest Squeeze Signal:**

> High short interest relative to 60-day historical average signals crowded bearish positioning within subindustry. Subsequent short covering creates upward price momentum independent of fundamental news.

**Secondary: Ownership Churn:**

> Institutional ownership percentage changes predict future trading activity; increasing ownership signals informed accumulation.

### Why Orthogonal

| vs E5g7vMjJ | vs A1gVE97w |
|---|---|
| Not price-volume correlation | Not earnings quality |
| Short seller behavior signal | Not accounting data |
| Market microstructure | Analyst sentiment |
| **Orthogonal** | **Orthogonal** |

## Created Artifacts

### Field Search Pack
- `runs/field-search-packs/2026-05-09-short-interest-ownership-concentration.md`

### Research Queue
- `runs/research-queues/2026-05-09-short-interest-research-queue.json`

### Diagnostic Batch (ready to execute)
- `runs/candidate-batches/2026-05-09-short-interest-field-health-batch.json`

## Execution Plan

**Phase 1: Field Health Diagnostic (blocked by rate limit)**
- Run 8 diagnostic expressions with decay=0, neutralization=None
- Gate: short_interest non-zero >50%, 20d update rate >60%
- Gate: days_to_cover non-zero >30%

**Phase 2: Baseline + Sign Control (if health passes)**
- Baseline: `-group_rank(ts_zscore(short_interest / ts_mean(short_interest, 60), 20), industry)`
- Sign control: positive variant
- Settings: decay=6, industry neutralization

**Phase 3: Family Expansion (if baseline viable)**
- Days-to-cover variant
- Hybrid: short_interest × ownership_stability
- Industry vs subindustry neutralization comparison

## Current Blockers

1. **API rate limit** - must wait for reset
2. **Field availability unknown** - diagnostics required

## Next Action When API Available

```bash
cd /Users/zpdedn/Documents/project/Worldquantbrain
# Run field health diagnostic batch
python3 scripts/alpha_batch_miner.py runs/candidate-batches/2026-05-09-short-interest-field-health-batch.json
```

## Frozen Families (do not explore)

- pcr_oi_720
- assets_cap_hump
- eps_quality_yield_backup
- price_volume_reversal_cluster (self-corr saturated)
- model_derivative_concentration_cluster (CONCENTRATED_WEIGHT failed)
