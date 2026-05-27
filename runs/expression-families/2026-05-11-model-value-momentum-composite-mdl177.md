# Expression Family: model_value_momentum_composite (mdl177)

## Metadata
- Family key: `model_value_momentum_composite`
- Stage: **S-1 STOP** (signal too weak — Sharpe 0.24, below 0.3 stop threshold)
- Generated: 2026-05-11
- Simulated: 2026-05-11
- Source: mdl177_valuemomemtummodel_vm_compositesn — Value Momentum Composite SN
- Region: USA | Universe: TOP3000 | Delay: 1

---

## Hypothesis

**Causal statement:** Model-generated value-momentum composites (mdl177) capture regime shifts in how the market prices growth-versus-value relative to recent price momentum, before that repricing is reflected in cross-sectional rankings.

**Mechanism class:** Market microstructure / model signal — the platform's value-momentum composite model identifies stocks that are mispriced relative to their value-momentum profile, and the cross-section slowly incorporates this signal.

**Why this source is genuinely new:**
- `fscore_total` (model16) is frozen — 29.46% coverage, different dataset
- `multi_factor_static_score_derivative` and `relative_valuation_rank_derivative` are frozen (model16 rerating lanes)
- `mdl177_valuemomemtummodel_vm_compositesn` is model77, a **different dataset** from model16
- It is a **Value Momentum Composite** — distinct mechanism from pure value or pure momentum
- It has 100% coverage in USA/TOP3000/D1, 88 users, 152 alphas — moderate crowd, not zero
- **Key differentiator from frozen lanes:** This is not a rerating signal (change in score), it is the composite signal itself — the actual value-momentum blend, not its derivative

**Falsifier:** If ts_rank of mdl177 produces no alpha (alphaId=null) or Sharpe < 0.3, this lane is dead.

**Reverse event test:** Would flipping sign produce an equally strong opposite signal? If so, the sign is wrong; if not, the composite has a structural directional bias worth exploiting.

---

## Field Health Summary

| Field | Dataset | Coverage | Users | Alphas | Type |
|-------|---------|----------|-------|--------|------|
| `mdl177_valuemomemtummodel_vm_compositesn` | model77 | **100%** | 88 | 152 | MATRIX |

- Field health diagnostics for mdl177 were submitted (COMPLETE status in capture) — results returned empty IS (field health only, no alpha metrics expected)
- Coverage and volatility tests confirmed field accepts standard operators

---

## Baseline Expression

```
group_rank(ts_rank(mdl177_valuemomemtummodel_vm_compositesn, 20), industry)
```

Settings:
- InstrumentType: EQUITY
- Region: USA
- Universe: TOP3000
- Delay: 1
- Decay: 0
- Neutralization: INDUSTRY
- Truncation: 0.08
- Pasteurization: ON
- UnitHandling: VERIFY
- nanHandling: OFF

---

## Sign Control

```
-group_rank(ts_rank(mdl177_valuemomemtummodel_vm_compositesn, 20), industry)
```

Expected sign: POSITIVE — model value-momentum composites should have a structural bullish bias (value+momentum both predict positive returns independently; their composite should too).

---

## Bounded Family Variants (one axis at a time)

| Axis | Variant name | Expression | Purpose |
|------|-------------|------------|---------|
| Window | `mdl177_w20_industry` | baseline | 20-day rank anchor |
| Window | `mdl177_w60_industry` | `group_rank(ts_rank(mdl177_valuemomemtummodel_vm_compositesn, 60), industry)` | Slower lookback |
| Sign | `mdl177_neg_industry` | sign control | Confirm direction |
| Neutralization | `mdl177_w20_neutral` | `ts_rank(mdl177_valuemomemtummodel_vm_compositesn, 20)` (no group_rank) | Remove industry neutralization |
| Composite | `mdl177_fscore_stack` | `group_rank(ts_rank(mdl177_valuemomemtummodel_vm_compositesn, 20), industry) * group_rank(ts_rank(fscore_total, 20), industry)` | Stack with fscore (if coverage passes 50%) |

---

## Main Risks

| Risk | Assessment |
|------|------------|
| **Sharpe** | mdl177 composite is a third-party model output — if market already prices it, alpha may be zero |
| **Coverage** | 100% confirmed — no issue |
| **Crowding** | 152 alphas, 88 users — moderate; needs low-corr angle to be viable |
| **Turnover** | Unknown — model composite may be smooth, turnover manageable |
| **Self-corr** | Unknown — first simulation will reveal |

---

## Optimization Order

1. **First:** Baseline + sign control (2 sims) — determine if direction is correct
2. **If positive:** Window axis (60-day lookback variant)
3. **If strong:** Composite with fscore_total (requires fscore coverage check first)
4. **Do not touch:** Decay, truncation, neutralization type until sign+window are confirmed

---

## Incubation Stage Contract

- S-1 gate: distinctness + signal presence scores (snapshot pass before backtest)
- S0 gate: baseline simulated + sign flip confirmed
- A gate: baseline passes absolute floor (Sharpe > 0.25, Fitness > 0.08)
- Budget: max 2 variants for S-1, 1 budget unit

---

## Submission Posture

**Decision: STOP — 2026-05-11**

**Results from 2026-05-11 simulation:**
- Baseline (positive): IS Sharpe -0.24, Fitness -0.03, FAIL LOW_SHARPE/LOW_FITNESS
- Sign-flipped (negative): IS Sharpe +0.24, Fitness +0.03, FAIL LOW_SHARPE/LOW_FITNESS/LOW_SUB_UNIVERSE_SHARPE

**Analysis:**
- Sign is confirmed correct (flipping sign properly reverses Sharpe)
- BUT absolute signal is far too weak — Sharpe 0.24 vs B-stage floor 0.25
- Sub-universe test fails on the sign-flipped control
- Per stop condition: "If Sharpe < 0.3, STOP" — triggered

**Memo:** `runs/notes/daily/2026-05-11-mdl177-stop-memo.md`
**Simulation:** `runs/simulation-captures/2026-05-11-mdl177-value-momentum-composite-batch.json`
