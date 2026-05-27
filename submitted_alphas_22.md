# WorldQuant BRAIN Alpha Mining - 22 Submitted Alphas

**Generated**: 2026-05-22
**Account**: PZ96147
**Total Submitted**: 22 alphas

---

## Alpha List

| # | Alpha ID | Expression | decay | neutral | Sharpe | Fitness | TVR | SC | 提交日期 |
|---|----------|------------|-------|---------|--------|---------|-----|------|----------|
| 1 | d5d59jpw | zscore(reverse(divide(change_in_eps_surprise, max(abs(correlation_last_360_days_spy), 0.01)))) | 4 | INDUSTRY | 1.44 | 1.34 | 0.104 | 0.6004 | 2026-05-21 |
| 2 | QPn0vn3X | trade_when(group_rank(ts_std_dev(returns,60), sector) > 0.7, rank(group_neutralize(returns, subindustry), -1)) | 15 | INDUSTRY | 1.57 | 1.08 | 0.239 | 0.6977 | 2026-05-18 |
| 3 | 1YoX2GxX | rank(group_neutralize(divide(fnd6_sppe, add(abs(fnd6_siv), 1)), industry)) | 0 | INDUSTRY | 1.45 | 1.17 | 0.019 | 0.6018 | 2026-05-17 |
| 4 | 1YopVrdW | group_neutralize(divide(fnd6_rectr, add(fnd6_recd, 1.0)), subindustry) | 0 | SUBINDUSTRY | 1.44 | 1.37 | 0.018 | 0.4857 | 2026-05-16 |
| 5 | xAeN6jGp | group_neutralize(divide(fnd6_rectr, max(fnd6_recd, 0.000001)), industry)) | 0 | SUBINDUSTRY | 1.37 | 1.25 | 0.014 | 0.4698 | 2026-05-16 |
| 6 | 2rvNV1qJ | group_rank(ts_delta(eps, 1), market) | 6 | INDUSTRY | 1.35 | 1.08 | 0.231 | 0.6185 | 2026-05-16 |
| 7 | 1YodbWO6 | reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian, buckets=10)), subindustry)) | 10 | SUBINDUSTRY | 1.25 | 1.04 | 0.019 | 0.1781 | 2026-05-16 |
| 8 | 0mAE3qzp | group_rank(ts_delta(revenue, 1) / ts_mean(revenue, 4), market) | 0 | INDUSTRY | 1.58 | 1.03 | 0.372 | 0.5253 | 2026-05-15 |
| 9 | gJmojOQm | group_rank(ts_zscore(winsorize(ts_backfill(unsystematic_risk_last_60_days, 120)), 60), industry) | 6 | INDUSTRY | 1.35 | 1.0 | 0.132 | 0.2997 | 2026-05-14 |
| 10 | GrnExm2Q | rank(-group_rank(-ts_zscore(tobins_q_ratio, 5), industry)) | 5 | INDUSTRY | 1.89 | 1.07 | 0.370 | 0.6864 | 2026-05-13 |
| 11 | 88Ob79jV | rank(group_neutralize(ts_decay_linear((-ts_zscore(returns, 252))*group_rank(rank(cap), industry), 40), industry)) | 0 | INDUSTRY | 1.89 | 1.01 | 0.382 | 0.6796 | 2026-05-11 |
| 12 | O0bXoVV1 | ts_zscore(-ts_delta(close, 1), 10) | 18 | SUBINDUSTRY | 2.19 | 1.2 | 0.567 | 0.875 | 2026-05-10 |
| 13 | e7dPWeop | ts_rank(ts_delta(assets / cap, 2), 20) | 6 | SUBINDUSTRY | 1.96 | 1.02 | 0.543 | 0.6647 | 2026-05-09 |
| 14 | A1gVE97w | group_rank(add(group_rank(ts_rank(eps / close, 120), industry), group_rank(ts_rank(vol_5, 20), industry)), industry) | 0 | INDUSTRY | 1.63 | 1.04 | 0.190 | 0.3835 | 2026-05-07 |
| 15 | bloqmdJK | trade_when(rank(ts_mean(scl12_sentiment_fast_d1,20)) > 0.55, group_neutralize(returns, market), -1) | 3 | MARKET | 1.61 | 1.25 | 0.103 | 0.6368 | 2026-05-04 |
| 16 | Xg2X2jxl | rank(ts_mean(anl4_totassets_flag, 20)) | 0 | INDUSTRY | 1.3 | 1.3 | 0.024 | 0.4267 | 2026-04-30 |
| 17 | LLgOWZmn | group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(volume), 20), industry)) | 0 | INDUSTRY | 2.18 | 1.21 | 0.475 | 0.6392 | 2026-05-01 |
| 18 | A1g6AlWg | rank(ts_decay_linear(sales_estimate_count, 10)) | 0 | INDUSTRY | 1.7 | 1.03 | 0.035 | 0.0771 | 2026-04-30 |
| 19 | E5g7vMjJ | group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_delta(volume, 10)), 20), industry) | 0 | INDUSTRY | 1.37 | 1.01 | 0.175 | 0.6804 | 2026-04-28 |
| 20 | qMmpvp8v | -ts_mean(returns, 5) | 4 | SUBINDUSTRY | 1.46 | 1.12 | 0.404 | 0.4641 | 2026-04-24 |
| 21 | E5repQ81 | group_rank(ts_rank(anl4_afv4_median_eps/close, 60), industry) | 4 | SUBINDUSTRY | 1.93 | 1.4 | 0.177 | 0.0 | 2026-04-18 |
| 22 | d5l07rpX | group_rank(ts_rank(earnings_per_share_average/close, 120), industry) | 4 | SUBINDUSTRY | 1.67 | 1.22 | 0.128 | 0.6806 | 2026-04-21 |

---

## Alpha Family Summary

| Family | Alpha IDs | Count |
|--------|-----------|-------|
| close_delta | O0bXoVV1 | 1 |
| returns_vwap | 88Ob79jV | 1 |
| tobins_q_ratio | GrnExm2Q | 1 |
| assets_cap | e7dPWeop | 1 |
| eps_family | A1gVE97w, 2rvNV1qJ, E5repQ81, d5l07rpX | 4 |
| sentiment | bloqmdJK | 1 |
| sales_estimate | A1g6AlWg | 1 |
| total_assets | Xg2X2jxl | 1 |
| unsystematic_risk | gJmojOQm | 1 |
| range | LLgOWZmn | 1 |
| revenue_growth | 0mAE3qzp | 1 |
| fnd6_family | 1YoX2GxX, 1YopVrdW, xAeN6jGp, 1YodbWO6 | 4 |
| trade_when_sector | QPn0vn3X | 1 |
| eps_surprise | d5d59jpw | 1 |
| mixed | E5g7vMjJ, qMmpvp8v | 2 |

---

## Risk Monitoring

### High Self-Correlation (SC > 0.7)
| Alpha ID | SC | Action |
|----------|-----|--------|
| O0bXoVV1 | 0.875 | ⚠️ Monitor closely |
| QPn0vn3X | 0.6977 | ⚠️ Near threshold |
| E5g7vMjJ | 0.6804 | ⚠️ Near threshold |
| 88Ob79jV | 0.6796 | ⚠️ Near threshold |

### Top Performers (Sharpe > 1.8)
| Alpha ID | Sharpe | Fitness | TVR | Notes |
|----------|--------|---------|-----|-------|
| O0bXoVV1 | 2.19 | 1.2 | 0.567 | close_delta |
| LLgOWZmn | 2.18 | 1.21 | 0.475 | range family |
| GrnExm2Q | 1.89 | 1.07 | 0.370 | tobins_q |
| 88Ob79jV | 1.89 | 1.01 | 0.382 | returns_vwap |
| E5repQ81 | 1.93 | 1.4 | 0.177 | eps family |

---

## Statistics

| Metric | Value |
|--------|-------|
| Total Alphas | 22 |
| Average Sharpe | 1.62 |
| Average Fitness | 1.15 |
| Average TVR | 0.228 |
| Average SC | 0.52 |
| Date Range | 2026-04-18 to 2026-05-21 |

### SC Distribution
- SC < 0.3: 2 (gJmojOQm, A1g6AlWg)
- SC 0.3-0.5: 5
- SC 0.5-0.7: 13
- SC > 0.7: 2 (O0bXoVV1 at 0.875)

---

## Settings Distribution

### Decay Values
- decay=0: 8 alphas
- decay=3-6: 8 alphas
- decay=10+: 4 alphas

### Neutralization
- INDUSTRY: 12
- SUBINDUSTRY: 8
- MARKET: 1
- NONE: 1

---

*Document generated by Claude Code - WorldQuant BRAIN Alpha Mining System*