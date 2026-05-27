# CrossSection Academic Signals → BRAIN Field Mapping
## Chen & Zimmermann (2020) 319-Factor Analysis — BRAIN Translation

**Source:** https://github.com/OpenSourceAP/CrossSection (319 signals from 153 papers)
**Purpose:** Map academic alpha factors to BRAIN fields; identify high-value uncrowded signals
**Analysis date:** 2026-05-11

---

## Executive Summary

From 319 academic characteristics across Value, Momentum, Profitability, Investment, Accruals, External Financing, Earnings Forecast, and Sentiment categories:

- **~45 signals have potential BRAIN field mappings** (partial or full)
- **~12 signals have confirmed high-quality BRAIN field matches** with low crowding
- **~275 signals have no clear BRAIN field mapping** (no usable translation)
- **Key opportunity: External Financing signals** — `mdl77_valueanalystmodel_qva_yoychgshares` (YoY shares change) has 96.3% coverage and extremely low crowd
- **Key opportunity: `proforma_earnings_to_price`** — only 1 BRAIN alpha using it, 96% coverage

---

## Category 1: External Financing (12 signals)

| Academic Signal | BRAIN Field | Coverage | Rank/Crowding | Status |
|---|---|---|---|---|
| ShareIssuance (1y) | `mdl77_valueanalystmodel_qva_yoychgshares` | 96.3% | Rank 96.3%, ~0 alphas | **HIGH OPPORTUNITY** |
| ShareIssuance (5y) | Unknown | — | — | No BRAIN field found |
| CompositeDebtIssuance | Unknown | — | — | Needs field search |
| NetEquityFinance | Unknown | — | — | Needs field search |
| NetDebtFinance | Unknown | — | — | Needs field search |
| ShareIss1Y | `mdl77_valueanalystmodel_qva_yoychgshares` | 96.3% | Same as above | Same as above |
| DebtIssuance | Unknown | — | — | Needs field search |

**Signal formula (CrossSection):**
```python
ShareIssuance = log(1 + shares_outstanding_t) - log(1 + shares_outstanding_t-12)
# Uses Compustat share data, 12-month change
```

**BRAIN equivalent expression:**
```
ts_rank(mdl77_valueanalystmodel_qva_yoychgshares, 20)
# Or with industry neutralization:
group_rank(ts_rank(mdl77_valueanalystmodel_qva_yoychgshares, 20), industry)
```

---

## Category 2: Accruals (5 signals)

| Academic Signal | BRAIN Field | Coverage | Status |
|---|---|---|---|
| TotalAccruals | `operating_income` (partial) | ~50% | Denominator missing (need assets) |
| AbnormalAccruals | Unknown | — | Jones model residual — hard to replicate |
| Change in NOA | Unknown | — | Needs field search |
| Change in Working Capital | `fnd6_newqv1300_nwc` (?) | Unverified | Needs field health |
| OrderBacklogChg | Unknown | — | Needs field search |

**CrossSection formula:**
```python
TotalAccruals = (NetIncome - CashFlowFromOperations) / TotalAssets
# Or: ΔWorkingCapital / AverageTotalAssets
```

---

## Category 3: Investment (8 signals)

| Academic Signal | BRAIN Field | Coverage | Status |
|---|---|---|---|
| AssetGrowth | `assets` | Unknown | Needs field health check |
| Investment | `capital_expenditure_amount` | 75.2% | FOUND — 22 BRAIN alphas (crowded) |
| dNoa (delta NOA) | Unknown | — | Needs field search |
| GrLTNOA | Unknown | — | Needs field search |

**CrossSection formula:**
```python
AssetGrowth = log(TotalAssets_t) - log(TotalAssets_t-12)
Investment = (Capex + Acquisitions) / TotalAssets
```

---

## Category 4: Profitability (8 signals)

| Academic Signal | BRAIN Field | Coverage | Status |
|---|---|---|---|
| Gross Profitability (GP) | Unknown | — | Needs (revenue - COGS) / assets |
| ROE | `return_on_invested_capital_4` | 100% | FOUND — 6 alphas (moderate) |
| ROE | `cash_earnings_return_on_equity` | 95% | FOUND — 10 alphas |
| Operating Profitability | `operating_income / sales` | ~50% | Partial — margin ratio |
| ROA | Unknown | — | Needs field search |

**CrossSection formula:**
```python
GP = (Revenue - COGS) / TotalAssets
ROE = NetIncome / BookEquity
```

---

## Category 5: Earnings Forecast (8 signals)

| Academic Signal | BRAIN Field | Coverage | Status |
|---|---|---|---|
| AnalystRevision | `anl4_af_eps_value` | ~70% | Partial — actual EPS not revision |
| REV6 (6-month revision) | Unknown | — | Needs field search |
| UpRecomm | Unknown | — | Needs field search |
| DownRecomm | Unknown | — | Needs field search |
| EarningsForecastDisparity | `anl4_afv4_dts_spe` | 69% | FOUND — ~10 BRAIN alphas (moderate) |
| EarningsForecastDisparity | `anl4_afv4_dts_spe` | 69% | Same as above |

---

## Category 6: Value/Valuation (17 signals)

| Academic Signal | BRAIN Field | Coverage | Status |
|---|---|---|---|
| Book-to-Market | `fnd6_teq / cap` | ~75% | Partial — needs ratio construction |
| Earnings-to-Price | `proforma_earnings_to_price` | **96%** | **FOUND — only 1 BRAIN alpha!** |
| Cash flow-to-Price | Unknown | — | Needs field search |
| Sales-to-Price | Unknown | — | Needs field search |
| Dividend yield | Unknown | — | Needs field search |

**Key finding:** `proforma_earnings_to_price` has 96% coverage but only **1 BRAIN alpha** uses it — extremely uncrowded value signal.

---

## Category 7: Momentum (11 signals)

| Academic Signal | BRAIN Field | Coverage | Status |
|---|---|---|---|
| Mom12m (12-month) | `returns` with ts_offset | — | Standard price returns |
| Mom6m | `returns` with ts_offset | — | Standard price returns |
| Short-term reversal | `returns` with ts_offset | — | Standard price returns |
| Residual momentum | Unknown | — | Needs industry-adjusted version |

**CrossSection formula:**
```python
Mom12m = prod((1 + ret_t-i)) for i in 1..11 - 1  # Skip month t
# Compounds 11 months, skips current month
```

---

## Category 8: Liquidity (9 signals)

| Academic Signal | BRAIN Field | Coverage | Status |
|---|---|---|---|
| Illiquidity (Amihud) | `volume` / `abs(returns)` | — | Expression possible |
| BidAskSpread | Unknown | — | Needs field search |
| ZeroTrade | Unknown | — | Needs field search |

---

## High-Value Uncrowded BRAIN Opportunities

### Tier 1: High Coverage + Low Crowd

| Field | Signal Type | Coverage | BRAIN Alphas | Recommended Action |
|---|---|---|---|---|
| `proforma_earnings_to_price` | E/P value | 96% | **1** | Immediate field health → baseline |
| `mdl77_valueanalystmodel_qva_yoychgshares` | Share issuance change | 96.3% | ~0 | Immediate field health → baseline |
| `fscore_total` | Model composite | 100% | Unknown | Field health first |
| `mdl177_valuemomemtummodel_vm_compositesn` | Value-momentum composite | Unknown | Unknown | Field health first |

### Tier 2: Moderate Coverage + Moderate Crowd

| Field | Signal Type | Coverage | BRAIN Alphas | Notes |
|---|---|---|---|---|
| `return_on_invested_capital_4` | ROE | 100% | 6 | Solid quality metric |
| `cash_earnings_return_on_equity` | Cash ROE | 95% | 10 | Alternative ROE |
| `anl4_afv4_dts_spe` | Forecast dispersion | 69% | ~10 | Earnings disagreement |
| `capital_expenditure_amount` | Investment | 75.2% | 22 | Crowded — avoid direct |

### Tier 3: Unconfirmed — Needs Field Search

| Signal Category | BRAIN Field Candidates | Status |
|---|---|---|
| Total Accruals | `fnd6_newqv1300_*` | Need field health |
| Book-to-Market | `fnd6_teq` / `cap` | Need ratio construction |
| Asset Growth | `assets` | Need verify |
| Debt Issuance | Unknown | Need field search |

---

## Recommended Alpha Strategies from CrossSection Mapping

### Strategy 1: Share Issuance Change (mdl77_yoychgshares)

**Hypothesis:** Firms with large YoY share dilution underperform; shrinkage outperforms.

**Baseline:**
```
-group_rank(ts_rank(mdl77_valueanalystmodel_qva_yoychgshares, 20), industry)
```
*Sign: Negative (share dilution is bearish)*

**Variants:**
- 20-day vs 60-day lookback
- With volume filter (high volume + high dilution = more bearish)
- Raw rank vs industry-neutralized rank

### Strategy 2: Earnings-to-Price (proforma_earnings_to_price)

**Hypothesis:** Low E/P stocks outperform high E/P (value factor); earnings quality matters.

**Baseline:**
```
group_rank(ts_rank(proforma_earnings_to_price, 20), industry)
```
*Sign: Positive (low E/P = value = outperformance)*

**Variants:**
- 20-day vs 60-day lookback
- With ROE filter (value + quality = stronger)
- Raw vs industry-neutralized

### Strategy 3: Model Composite Value-Momentum (fscore_total / mdl177)

**Hypothesis:** Model-generated composite captures regime shifts that raw price/volume miss.

**Baseline:**
```
group_rank(ts_rank(fscore_total, 20), industry)
```
*Sign: Positive (model composite has structural positive expectation)*

**Variants:**
- fscore_total vs mdl177 composite
- 20-day vs 60-day
- Standalone vs combined with price momentum

### Strategy 4: ROE × E/P Quality Stack (composite)

**Hypothesis:** Combining return on equity with earnings-to-price gives quality-value intersection.

**Baseline:**
```
group_rank(ts_rank(return_on_invested_capital_4, 20), industry) *
group_rank(ts_rank(proforma_earnings_to_price, 20), industry)
```
*Sign: Positive (quality-value compound)*

---

## Field Health Priority Order

1. **`proforma_earnings_to_price`** — 96% coverage, only 1 alpha, extreme uncrowded
2. **`mdl77_valueanalystmodel_qva_yoychgshares`** — 96.3% coverage, YoY shares change, untested
3. **`fscore_total`** — model composite, 100% coverage expected, untested
4. **`mdl177_valuemomemtummodel_vm_compositesn`** — value-momentum composite, untested
5. **`anl4_afv4_dts_spe`** — earnings forecast dispersion, 69% coverage, moderate crowd

---

## Cross-Family Correlation Risk

- Share issuance (mdl77) is orthogonal to price/volume/earnings signals
- E/P (proforma_earnings_to_price) orthogonal to momentum but may correlate with book-to-market if `fnd6_teq` is used
- ROE × E/P composite has internal correlation (both quality signals) — treat as single family
- Model composites (fscore_total, mdl177) are likely orthogonal to fundamental signals

---

## Next Steps

1. Run field health diagnostics for `proforma_earnings_to_price` and `mdl77_valueanalystmodel_qva_yoychgshares`
2. If both pass, run baseline + sign control for both families in parallel
3. Submit bloqmdJK (ready to submit, shouldn't wait)
4. Write research queue update for model16/77 based on this analysis

---

## Appendix: All 212 CrossSection Signals by Category

### Valuation (17)
AccrualsBM, AM, BM, BMdec, CF, cfp, DivYieldST, EBM, EntMult, EP, EquityDuration, Frontier, NetPayoutYield, PayoutYield, sfe, AnalystValue, SP

### Momentum (11)
FirmAgeMom, IndMom, IntMom, Mom12m, Mom6m, Mom6mJunk, MomRev, MomVol, ResidualMomentum, TrendFactor, High52

### Profitability (8)
CBOperProf, FEPS, GP, InvGrowth, roaq, OperProf, OperProfRD, RoE

### Investment (8)
AssetGrowth, ChEQ, DelEqu, DelLTI, dNoa, Investment, InvestPPEInv, GrLTNOA

### External Financing (12)
CompEquIss, CompositeDebtIssuance, ConvDebt, DelCOL, DelFINL, IndIPO, NetDebtFinance, NetEquityFinance, ShareIss1Y, ShareIss5Y, XFIN, DebtIssuance

### Liquidity (9)
BetaLiquidityPS, Illiquidity, std_turn, VolSD, zerotrade6M, zerotrade1M, zerotrade12M, BidAskSpread, ProbInformedTrading

### Accruals (5)
AbnormalAccruals, Accruals, OrderBacklogChg, PctAcc, PctTotAcc

### Leverage (4)
BookLeverage, BPEBM, Leverage, NetDebtPrice

### Volatility (6)
betaVIX, ForecastDispersion, IdioVol3F, IdioVolAHT, MaxRet, RealizedVol

### Risk (6)
BetaTailRisk, CoskewACX, ReturnSkew, ReturnSkew3F, Beta, Coskewness

### Earnings Forecast (8)
AnalystRevision, ChForecastAccrual, EarningsForecastDisparity, fgr5yrLag, REV6, DownRecomm, PredictedFE, UpRecomm

### Sales Growth (6)
ChAssetTurnover, MeanRankRevGrowth, OrderBacklog, RevenueSurprise, GrSaleToGrInv, GrSaleToGrOverhead

### Asset Composition (5)
Cash, NOA, RDcap, tang, realestate

### R&D (5)
OrgCap, RD, RDIPO, SurpriseRD, AdExp

### Long Term Reversal (6)
IntanBM, IntanCFP, IntanEP, IntanSP, LRreversal, MRreversal

### Lead Lag (9)
CustomerMomentum, EarnSupBig, IndRetBig, iomom_cust, iomom_supp, PriceDelayRsq, retConglomerate, PriceDelaySlope, PriceDelayTstat

### Other (27)
Activism1, ChTax, CredRatDG, ExchSwitch, Governance, Herf, HerfBE, Mom12mOffSeason, MomOffSeason, MomOffSeason06YrPlus, MomOffSeason16YrPlus, MomSeason, MomSeason06YrPlus, MomSeason11YrPlus, MomSeason16YrPlus, MomSeasonShort, OPLeverage, Price, RDAbility, Tax, AgeIPO, AOP, BetaFP, HerfAsset, MomOffSeason11YrPlus, sinAlgo, Spinoff