# Options + Sentiment Field Discovery — STOP MEMO

## Fields Tested

| Field | Type | Raw Signal | Industry Neutralized | Verdict |
|-------|------|-----------|---------------------|---------|
| `pcr_oi_30` | PCR (put-call ratio OI) | ERROR — unknown field | N/A | STOP |
| `pcr_oi_60` | PCR (put-call ratio OI) | Sharpe 0.77, Fitness 0.99 | **Sharpe 0.05** (destroyed) | STOP |
| `pcr_vol_20` | PCR (put-call ratio vol) | Sharpe 0.78, Fitness 0.57 | N/A | STOP |
| `put_breakeven_60` | Put breakeven | Sharpe 0.68 | N/A | STOP |
| `call_breakeven_60` | Call breakeven | Sharpe 0.70 | N/A | STOP |
| `option_breakeven_30` | Option breakeven | Sharpe 0.70 | N/A | STOP |
| `historical_volatility_20` | Historical vol | Sharpe 0.76 | N/A | STOP |
| `snt1_d1_dynamicfocusrank` | Sentiment rank | Sharpe 0.85, Fitness 1.5 | **Sharpe -0.15** (destroyed) | STOP |
| `vsm3_iv_skew_20` | IV skew | ERROR — unknown field | N/A | STOP |

## Key Finding: Industry Effect Dominates

**All options/sentiment fields are industry-level signals.**

Evidence:
- `pcr_oi_60` raw: Sharpe 0.77 → with INDUSTRY neutralization: **Sharpe 0.05** (signal destroyed)
- `snt1_d1_dynamicfocusrank` raw: Sharpe 0.85, Fitness 1.5 → with INDUSTRY neutralization: **Sharpe -0.15**

**Interpretation:** These fields carry strong industry-wide component. Within-industry ranking removes the signal entirely. The signal is "buy options sentiment when whole sector is bullish" not "buy stock-specific options signal."

## Structural Constraints

1. **CONCENTRATED_WEIGHT** — all options variants fail concentration check (likely sector-level clustering)
2. **LOW_SUB_UNIVERSE_SHARPE** — sub-universe performance fails when neutralized
3. **Sign is correct but signal is too weak post-neutralization**

## Academic Backing

These are not traditional CrossSection signals. Options-implied volatility measures (IV skew, smile, PCR) are documented in:
- CrossSection Volatility category: `betaVIX`, `ForecastDispersion`, `IdioVol3F`, `IdioVolAHT`, `MaxRet`, `RealizedVol`
- CrossSection Liquidity category: `BidAskSpread`, `zerotrade6M`, etc.

But these BRAIN fields (pcr_*, put_breakeven_*, call_breakeven_*) are **not the same as CrossSection's documented signals** — they appear to be BRAIN-specific derivatives with strong industry loading.

## Decision

**STOP all options/sentiment exploration.** The signals exist and have correct sign, but they fail structural checks (concentration, sub-universe) and industry neutralization destroys them. Not viable for submission regardless of sign.

## Evidence

- Simulation captures:
  - `runs/simulation-captures/2026-05-11-options-pcr-breakeven-field-health.json` — raw field results
  - `runs/simulation-captures/2026-05-11-snt1-pcr-industry-neutral-field-health.json` — with industry neutralization

---
STOP memo written: 2026-05-11
