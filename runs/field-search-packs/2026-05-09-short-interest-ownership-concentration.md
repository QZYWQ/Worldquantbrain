# Short Interest / Ownership Concentration Field Search Pack

## Metadata

- Date: `2026-05-09`
- Topic: `short_interest_ownership_concentration`
- Region: `USA` (verify)
- Universe: `TOP3000` (verify)
- Delay: `1` (verify)

## Hypothesis

### Primary Thesis: Short Interest Concentration as Contrarian Signal

**What information changes:**
- Short interest ratio (short shares / float) increases when bears accumulate
- High short interest + declining price = crowded bearish bet
- Short covering (buy to cover) creates upward pressure independently of fundamental news

**Who reacts slowly:**
- Short sellers as a group are informed but subject to crowding and forced covering
- When short interest reaches extreme levels, the risk/reward of staying short deteriorates
- Market makers covering synthetic positions can amplify short squeeze dynamics

**Over what horizon:**
- Short-term: 1-4 weeks (short covering momentum)
- Medium-term: 1-3 months (fundamental repricing after extreme positioning)

**Cross-sectional ranking:**
- Rank stocks within subindustry by: short_interest / avg_short_interest(industry)
- High ratio relative to peers = more crowded bearish bet = higher short covering probability

**Failure mode:**
- Short interest can stay elevated for months without covering
- High short interest can persist in declining stocks (valid bearish signal, not squeeze)
- Must verify the mechanism is squeeze, not just continued bearish pressure

### Secondary Thesis: Institutional Ownership Churn

**What information changes:**
- Institutional ownership percentage changes when large funds rebalance
- Ownership churn predicts future trading activity and liquidity
- High ownership stability with low churn = informed holders staying put

**Failure mode:**
- Ownership data is quarterly/lagged
- Fund flows may predict price, not vice versa

## Data Explorer Search Terms

### Short Interest Family
- Primary: `short`, `short_interest`, `short_ratio`, `short_float`, `days_to_cover`
- Sibling: `short_exempt`, `total_shorted`, `short_interest_ratio`

### Ownership / Holder Structure Family
- Primary: `institutional`, `institutional_holding`, `ownership`, `holder_count`, `institution_count`
- Sibling: `mutual_fund_holding`, `etf_holding`, `fund_holding`, `top10_holding`, `top5_holding`
- Alternative: `float`, `public_float`, `restricted_shares`

### Normalization / Peer Comparison
- Denominator terms: `cap`, `volume`, `shares_outstanding`, `float`, `public_float`

## Candidate Fields

| Field | Dataset | Hypothesis Fit | Coverage Risk | Crowding Risk |
|---|---|---|---|---|
| `short_interest` | verify | Direct short interest ratio | Must verify coverage in TOP3000 | Likely common but not universal |
| `days_to_cover` | verify | Short squeeze potential if elevated | Depends on short interest coverage | Less crowded than raw short |
| `short_interest / cap` | computed | Size-normalized short interest | Depends on both field avail | Overlaps with size factor if not industry-neutralized |
| `institutional_holding` | verify | Institutional ownership % | Quarterly data, lagged | Very common |
| `holder_count` | verify | Number of institutions reporting | Incomplete coverage | Less crowded than pct |
| `top10_holding_pct` | verify | Concentration of top holders | Varies by source | May overlap with quality factors |
| `ownership_churn` | ts_delta of ownership | Change in institutional ownership | Quarterly data problem | Unknown |

## New Dataset Quick Evaluation

Run diagnostics with `None` neutralization and decay `0`. Inspect `Long Count + Short Count` as field-health evidence only.

| Diagnostic | Expression | What to inspect |
|---|---|---|
| Short interest raw coverage | `short_interest` | Long Count / Short Count vs universe size |
| Days to cover coverage | `days_to_cover` | Long Count vs universe |
| Short interest non-zero | `short_interest != 0 ? 1 : 0` | Daily non-zero rate |
| Update frequency 20d | `ts_std_dev(short_interest, 20) != 0 ? 1 : 0` | Whether short interest updates reactively |
| Update frequency 60d | `ts_std_dev(short_interest, 60) != 0 ? 1 : 0` | Quarterly update check |
| Ratio vs cap non-zero | `(short_interest / cap) != 0 ? 1 : 0` | Combined field availability |
| Bounds check | `abs(short_interest) > 0.5` | Extreme values |
| Holder count coverage | `holder_count` | Institutional coverage |
| Ownership churn non-zero | `ts_delta(institutional_holding, 20) != 0 ? 1 : 0` | Update frequency |

## Baseline Expression Ideas

### Short Interest Family Baselines

1. **Short squeeze signal:**
```
-group_rank(ts_zscore(short_interest / ts_mean(short_interest, 60), 20), industry)
```

2. **Days to cover signal:**
```
-group_rank(ts_zscore(days_to_cover / ts_mean(days_to_cover, 60), 20), industry)
```

3. **Short interest rank within subindustry (no time normalization):**
```
group_rank(short_interest, subindustry)
```

4. **Short interest vs market:**
```
ts_zscore(short_interest / market_avg(short_interest), 20)
```

### Ownership Concentration Baselines

5. **Institutional ownership churn (increase = more bullish):**
```
group_rank(ts_delta(institutional_holding, 60), industry)
```

6. **Holder count increase:**
```
group_rank(ts_delta(holder_count, 20), industry)
```

7. **Top10 concentration vs historical:**
```
group_rank(ts_zscore(top10_holding_pct / ts_mean(top10_holding_pct, 252), 60), industry)
```

### Hybrid Baselines

8. **Short squeeze + ownership stability:**
```
-group_rank(short_interest, subindustry) * group_rank(institutional_holding, subindustry)
```

## Likely First Failure

- **Sharpe**: Short interest direction is ambiguous - high SI can mean valid bearish signal, not squeeze
- **Fitness**: Quarterly data lag in ownership fields makes them feel "slow" vs delay-1 requirement
- **Turnover**: Short interest changes infrequently, so signal may be too sticky
- **Sub-universe**: Small-cap SI coverage may be thin, failing sub-universe tests
- **Self-correlation**: Could overlap with existing value/gravity factors

## Sign Control Requirement

**Mandatory.** Both positive and negative signs must be tested:
- High SI → squeeze signal → positive
- High SI → valid bearish → negative

Without sign control, direction is unconfirmed.

## Field Health Gate

If `short_interest` shows <50% non-zero coverage or <60% 20d update rate in diagnostics, stop this family before alpha mining.

## Competition Route

Start D1-first (delay=1). The short squeeze mechanism is a classic D1 idea.

## Next Action

1. Field health diagnostics on `short_interest`, `days_to_cover`, `institutional_holding`, `holder_count`
2. If health passes gate, run baseline + sign control (expressions 1-2)
3. Evaluate sign and fitness before family expansion
