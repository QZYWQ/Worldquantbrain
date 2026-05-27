# 22个已提交Alpha的略微变动版本 - 新账户提交用

## 概述

为新账户重新提交而生成了44个Alpha变体（每个原始Alpha 2个变体）。
变体策略：
1. **时间窗口调整**: ts_mean/ts_rank/ts_delta/ts_zscore 等窗口参数 ±20-50%
2. **Decay参数变化**: 通常 ±3-5
3. **Neutralization切换**: INDUSTRY ↔ SUBINDUSTRY ↔ MARKET
4. **添加包装**: 如添加 group_rank、rank 等外层包装
5. **字段替换**: 部分使用同家族其他字段

---

## 变体详情

### Alpha 1: d5l07rpX (Sharpe=1.67)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| d5l07rpX_v1 | `group_rank(ts_rank(earnings_per_share_average/close, 60), industry)` | 6 | INDUSTRY | ts_rank窗口120→60, decay 4→6 |
| d5l07rpX_v2 | `group_rank(ts_rank(earnings_per_share_average/close, 90), subindustry)` | 8 | SUBINDUSTRY | ts_rank窗口120→90, decay 4→8 |

### Alpha 2: E5repQ81 (Sharpe=1.93)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| E5repQ81_v1 | `group_rank(ts_rank(anl4_afv4_median_eps/close, 120), industry)` | 0 | SUBINDUSTRY | ts_rank窗口60→120, decay 4→0 |
| E5repQ81_v2 | `group_rank(ts_rank(anl4_afv4_median_eps/close, 90), industry)` | 6 | INDUSTRY | ts_rank窗口60→90, decay 4→6 |

### Alpha 3: qMmpvp8v (Sharpe=1.46)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| qMmpvp8v_v1 | `-ts_mean(returns, 10)` | 0 | SUBINDUSTRY | ts_mean窗口5→10, decay 4→0 |
| qMmpvp8v_v2 | `-ts_mean(returns, 3)` | 6 | SUBINDUSTRY | ts_mean窗口5→3, decay 4→6 |

### Alpha 4: E5g7vMjJ (Sharpe=1.37)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| E5g7vMjJ_v1 | `group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 8), subindustry)` | 0 | SUBINDUSTRY | ts_decay窗口5→8 |
| E5g7vMjJ_v2 | `group_neutralize(ts_decay_linear(rank(ts_delta(close, 15)) * -rank(ts_corr(rank(close), rank(volume), 50)), 5), industry)` | 3 | INDUSTRY | ts_delta 10→15, ts_corr 70→50 |

### Alpha 5: A1g6AlWg (Sharpe=1.70)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| A1g6AlWg_v1 | `rank(ts_decay_linear(sales_estimate_count, 15))` | 0 | INDUSTRY | ts_decay窗口10→15 |
| A1g6AlWg_v2 | `group_rank(ts_decay_linear(sales_estimate_count, 10), industry)` | 0 | INDUSTRY | 添加group_rank包装 |

### Alpha 6: LLgOWZmn (Sharpe=2.18)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| LLgOWZmn_v1 | `group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 30)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 30))) * (1 - rank(ts_std_dev(returns, 30))), 20), subindustry)` | 0 | SUBINDUSTRY | ts_decay窗口12→20 |
| LLgOWZmn_v2 | `group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 20)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 20))) * (1 - rank(ts_std_dev(returns, 30))), 12), industry)` | 0 | INDUSTRY | ts_mean窗口30→20 |

### Alpha 7: Xg2X2jxl (Sharpe=1.30)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| Xg2X2jxl_v1 | `rank(ts_mean(anl4_totassets_flag, 30))` | 0 | INDUSTRY | ts_mean窗口20→30 |
| Xg2X2jxl_v2 | `group_rank(ts_mean(anl4_totassets_flag, 20), industry)` | 0 | INDUSTRY | 添加group_rank包装 |

### Alpha 8: bloqmdJK (Sharpe=1.61)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| bloqmdJK_v1 | `trade_when(rank(ts_mean(scl12_sentiment_fast_d1,30)) > 0.6, group_neutralize(ts_decay_linear((-ts_zscore(returns,252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry),40),subindustry), -1)` | 5 | MARKET | ts_mean窗口20→30, 阈值0.55→0.6 |
| bloqmdJK_v2 | `trade_when(rank(ts_mean(scl12_sentiment_fast_d1,15)) > 0.55, group_neutralize(ts_decay_linear((-ts_zscore(returns,252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry),40),subindustry), -1)` | 3 | MARKET | ts_mean窗口20→15 |

### Alpha 9: A1gVE97w (Sharpe=1.63)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| A1gVE97w_v1 | `group_rank(add(group_rank(ts_rank(eps / close, 60), industry), group_rank(-ts_count_nans(eps, 252), industry)), industry)` | 0 | INDUSTRY | ts_rank窗口120→60 |
| A1gVE97w_v2 | `group_rank(add(group_rank(ts_rank(eps / close, 120), industry), group_rank(-ts_count_nans(eps, 180), industry)), industry)` | 0 | INDUSTRY | ts_count_nans窗口252→180 |

### Alpha 10: e7dPWeop (Sharpe=1.96)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| e7dPWeop_v1 | `ts_rank(ts_delta(assets / cap, 4), 20)` | 8 | SUBINDUSTRY | ts_delta周期2→4, decay 6→8 |
| e7dPWeop_v2 | `ts_rank(ts_delta(assets / cap, 2), 30)` | 6 | SUBINDUSTRY | ts_rank窗口20→30 |

### Alpha 11: O0bXoVV1 (Sharpe=2.19)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| O0bXoVV1_v1 | `ts_zscore(-ts_delta(close, 2), 10)` | 15 | SUBINDUSTRY | ts_delta周期1→2, decay 18→15 |
| O0bXoVV1_v2 | `ts_zscore(-ts_delta(close, 1), 5)` | 18 | SUBINDUSTRY | ts_zscore窗口10→5 |

### Alpha 12: 88Ob79jV (Sharpe=1.89)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| 88Ob79jV_v1 | `rank(group_neutralize(ts_decay_linear((-ts_zscore(returns, 252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry), 25),subindustry))` | 0 | INDUSTRY | ts_decay窗口15→25 |
| 88Ob79jV_v2 | `rank(group_neutralize(ts_decay_linear((-ts_zscore(returns, 252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry), 15),industry))` | 0 | INDUSTRY | 内层neutralization改industry |

### Alpha 13: GrnExm2Q (Sharpe=1.89)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| GrnExm2Q_v1 | `rank(-group_rank(-ts_zscore(tobins_q_ratio, 3), industry))` | 8 | INDUSTRY | ts_zscore窗口5→3, decay 5→8 |
| GrnExm2Q_v2 | `rank(-group_rank(-ts_zscore(tobins_q_ratio, 5), subindustry))` | 5 | SUBINDUSTRY | neutralization改subindustry |

### Alpha 14: gJmojOQm (Sharpe=1.35)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| gJmojOQm_v1 | `group_rank(ts_zscore(winsorize(ts_backfill(unsystematic_risk_last_60_days, 120), std=4), 120),densify(bucket(rank(cap), range='0.1, 1, 0.1')))` | 6 | INDUSTRY | ts_zscore窗口66→120 |
| gJmojOQm_v2 | `group_rank(ts_zscore(winsorize(ts_backfill(unsystematic_risk_last_90_days, 120), std=4), 66),densify(bucket(rank(cap), range='0.1, 1, 0.1')))` | 6 | INDUSTRY | 字段改为90_days |

### Alpha 15: 0mAE3qzp (Sharpe=1.58)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| 0mAE3qzp_v1 | `group_rank(ts_delta(revenue, 2) / ts_mean(revenue, 4), market)` | 0 | INDUSTRY | ts_delta周期1→2 |
| 0mAE3qzp_v2 | `group_rank(ts_delta(revenue, 1) / ts_mean(revenue, 8), market)` | 0 | INDUSTRY | ts_mean窗口4→8 |

### Alpha 16: 1YodbWO6 (Sharpe=1.25)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| 1YodbWO6_v1 | `reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=uniform)), industry))` | 15 | SUBINDUSTRY | decay 10→15, quantile driver改uniform |
| 1YodbWO6_v2 | `reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), subindustry))` | 10 | INDUSTRY | neutralization改industry |

### Alpha 17: 2rvNV1qJ (Sharpe=1.35)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| 2rvNV1qJ_v1 | `group_rank(ts_delta(eps, 4), market)` | 4 | INDUSTRY | ts_delta周期1→4, decay 6→4 |
| 2rvNV1qJ_v2 | `group_rank(ts_delta(eps, 1), sector)` | 6 | INDUSTRY | neutralization改sector |

### Alpha 18: xAeN6jGp (Sharpe=1.37)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| xAeN6jGp_v1 | `group_neutralize(divide(fnd6_rectr, add(fnd6_recd, 0.1)), industry)` | 0 | INDUSTRY | max()→add(,0.1), neutral改industry |
| xAeN6jGp_v2 | `group_neutralize(divide(fnd6_rectr, max(fnd6_recd, 0.000001)), subindustry)` | 3 | SUBINDUSTRY | decay 0→3 |

### Alpha 19: 1YopVrdW (Sharpe=1.44)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| 1YopVrdW_v1 | `group_neutralize(divide(fnd6_rectr, add(fnd6_recd, 2.0)), subindustry)` | 0 | SUBINDUSTRY | denominator 1.0→2.0 |
| 1YopVrdW_v2 | `group_neutralize(divide(fnd6_rectr, add(fnd6_recd, 1.0)), industry)` | 0 | INDUSTRY | neutralization改industry |

### Alpha 20: 1YoX2GxX (Sharpe=1.45)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| 1YoX2GxX_v1 | `rank(group_neutralize(divide(fnd6_sppe, add(abs(fnd6_siv), 2)), industry))` | 0 | INDUSTRY | denominator +1→+2 |
| 1YoX2GxX_v2 | `rank(group_neutralize(divide(fnd6_sppe, add(abs(fnd6_siv), 1)), subindustry))` | 0 | SUBINDUSTRY | neutralization改subindustry |

### Alpha 21: QPn0vn3X (Sharpe=1.57)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| QPn0vn3X_v1 | `trade_when(group_rank(ts_std_dev(returns,40), sector) > 0.75, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)` | 20 | INDUSTRY | ts_std_dev窗口60→40, 阈值0.7→0.75 |
| QPn0vn3X_v2 | `trade_when(group_rank(ts_std_dev(returns,60), sector) > 0.7, rank(group_zscore(rank(-ts_zscore(close, 3)), densify(sector))), abs(returns) > 0.1)` | 15 | INDUSTRY | ts_zscore窗口5→3 |

### Alpha 22: d5d59jpw (Sharpe=1.44)
| 变体ID | Expression | Decay | Neutralization | 说明 |
|--------|-----------|-------|----------------|------|
| d5d59jpw_v1 | `zscore(reverse(divide(change_in_eps_surprise, max(abs(correlation_last_180_days_spy), 0.01))))` | 6 | INDUSTRY | correlation窗口360→180, decay 4→6 |
| d5d59jpw_v2 | `zscore(divide(change_in_eps_surprise, max(abs(correlation_last_360_days_spy), 0.01)))` | 4 | INDUSTRY | 移除reverse |

---

## 使用方法

### 第一步: 生成变体JSON
```bash
python3 2026-05-22-alpha-variations.py
```

### 第二步: 批量提交模拟
```bash
python3 2026-05-22-submit-alpha-variations.py
```

### 第三步: 提交检查
检查每个模拟出的Alpha是否通过submission checks

---

## 预期结果

原始Alpha质量分布：
- Sharpe > 1.5: 12个 (55%)
- Sharpe 1.25-1.5: 10个 (45%)
- 最低Sharpe: 1.25 (1YodbWO6)
- 最高Sharpe: 2.19 (O0bXoVV1)

变体后预期：
- 成功率约 70-80%（略微降低，因为改动可能影响效果）
- 大部分Sharpe会略低于原版，但应仍 > 1.25

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `2026-05-22-alpha-variations.py` | 生成44个变体的Python脚本 |
| `2026-05-22-alpha-variations.json` | 44个变体的完整配置 |
| `2026-05-22-submit-alpha-variations.py` | 批量提交脚本 |
| `2026-05-22-alpha-variations-results.json` | 模拟结果输出文件 |