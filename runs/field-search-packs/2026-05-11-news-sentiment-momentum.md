# News Sentiment Momentum Field Search Pack

## Metadata
- Date: `2026-05-11`
- Topic: `news_sentiment_momentum`
- Region: `USA`
- Universe: `TOP3000`
- Delay: `1`

## Hypothesis

### Primary Thesis: News Sentiment as Short-Term Alpha

**What information changes:**
- Financial news sentiment (qcm, bam, sse) changes when earnings/financial events occur
- High confidence sentiment signals (nws18_qcm) capture analyst-level assessment shifts
- Relevance filtering ensures signal is about the specific company, not general noise

**Who reacts slowly:**
- News travels slowly to retail; institutional investors react to first-order sentiment
- High relevance + high sentiment magnitude = crowded informed position = reversal risk
- Social media amplifies news within 1-2 days, creating momentum that can be fadeable

**Over what horizon:**
- Short-term: 1-5 days (news → sentiment → position)
- Medium-term: 5-20 days (earnings revision drift)

**Cross-sectional ranking:**
- Rank stocks within industry by: zscore(news_sentiment) × relevance_weight
- Positive sentiment + high relevance = short-term bullish positioning
- Negative sentiment + high relevance = squeeze candidate OR continued bearish

**Failure modes:**
- News sentiment can be fake/ manufactured for small caps
- Sentiment doesn't always translate to actual trading pressure
- Turnover may spike around earnings events
- Low relevance stories add noise, not signal

### Secondary Thesis: Sentiment Momentum Acceleration

**What information changes:**
- Change in sentiment (ts_delta) captures sentiment acceleration
- Rapid sentiment shifts around events create exploitable momentum

## Data Explorer Search Terms

### News Sentiment Fields
- Primary: `nws18_qcm` (high confidence sentiment), `nws18_bam` (M&A sentiment), `nws18_sse` (continuous sentiment)
- Sibling: `nws18_qep` (equities sentiment), `nws18_acb` (corporate action sentiment)
- Filter: `nws18_relevance` (story relevance to entity)

### News Impact Fields
- Primary: `rp_nip_equity` (news impact projection equity action)
- Alternative: `rp_ess_partner` (event sentiment partnership)

## Candidate Fields

| Field | Dataset | Hypothesis Fit | Coverage Risk | Crowding Risk |
|---|---|---|---|---|
| `nws18_qcm` | news18 | Direct high-confidence sentiment signal | 0.50 (50% of universe) | Unknown (631 alphas) |
| `nws18_bam` | news18 | M&A sentiment, company-specific | 0.50 | 984 alphas using - moderate |
| `nws18_sse` | news18 | Continuous -1 to +1 sentiment | 0.50 | 367 alphas - low crowd |
| `nws18_relevance` | news18 | Story relevance filter | 0.50 | 653 alphas - moderate |
| `rp_nip_equity` | news18 | News impact projection | 0.50 | 767 alphas - moderate |

## New Dataset Quick Evaluation

Run diagnostics with `None` neutralization and decay `0`. Inspect `Long Count + Short Count` as field-health evidence only.

| Diagnostic | Expression | What to inspect |
|---|---|---|
| Sentiment coverage | `nws18_qcm != 0 ? 1 : 0` | Long/Short count vs universe |
| M&A sentiment coverage | `nws18_bam != 0 ? 1 : 0` | Same |
| Continuous sentiment coverage | `nws18_sse != 0 ? 1 : 0` | Same |
| Relevance non-zero | `nws18_relevance > 0.5 ? 1 : 0` | Relevance threshold coverage |
| Sentiment magnitude | `abs(nws18_qcm) > 0` | Distribution of sentiment values |
| Combined signal | `nws18_qcm * (nws18_relevance / 100)` | Weighted signal quality |

## Baseline Expression Ideas

### News Sentiment Baselines

1. **High-confidence sentiment negative (bearish signal):**
```
-group_rank(ts_zscore(nws18_qcm, 20), industry)
```

2. **M&A sentiment positive (bullish signal):**
```
group_rank(ts_zscore(nws18_bam, 20), industry)
```

3. **Continuous sentiment drift:**
```
ts_zscore(nws18_sse, 20) - ts_zscore(nws18_sse, 60)
```

4. **Relevance-weighted sentiment:**
```
ts_zscore(nws18_qcm * (nws18_relevance / 50), 20)
```

5. **Sentiment × short-term returns momentum:**
```
group_rank(ts_zscore(nws18_qcm, 20), industry) * ts_rank(returns, 5)
```

### Sign Control Requirement
**Mandatory.** News sentiment direction is ambiguous - negative news doesn't always mean bearish price action (can be short squeeze).

Without sign control, direction is unconfirmed.

## Field Health Gate

If `nws18_qcm` shows <40% non-zero coverage in diagnostics, stop this family before alpha mining.

## Competition Route

Start D1-first (delay=1). News sentiment is a classic D1 idea.

## Next Action

1. Field health diagnostics on `nws18_qcm`, `nws18_bam`, `nws18_sse`, `nws18_relevance`
2. If health passes gate, run baseline + sign control (expressions 1-5)
3. Evaluate sign and fitness before family expansion