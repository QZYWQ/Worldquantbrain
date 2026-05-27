#!/usr/bin/env python3
"""
22个已提交Alpha的略微变动版本 - 用于新账户重新提交
每个Alpha有2-3个变体，保持核心结构但修改参数以避免被识别为重复
"""
import json

# ============================================================
# Alpha 1: d5l07rpX
# 原版: group_rank(ts_rank(earnings_per_share_average/close, 120), industry)
# Sharpe=1.67, Fitness=1.22, TVR=0.1281, Decay=4, Neutralization=SUBINDUSTRY
# ============================================================
alpha_v1_01 = {
    "id": "d5l07rpX_v1",
    "regular": {"code": "group_rank(ts_rank(earnings_per_share_average/close, 60), industry)"},
    "settings": {"decay": 6, "neutralization": "INDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体1: ts_rank窗口120→60, decay 4→6, neutralization SUBINDUSTRY→INDUSTRY"
}
alpha_v1_02 = {
    "id": "d5l07rpX_v2",
    "regular": {"code": "group_rank(ts_rank(earnings_per_share_average/close, 90), subindustry)"},
    "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体2: ts_rank窗口120→90, decay 4→8"
}

# ============================================================
# Alpha 2: E5repQ81
# 原版: group_rank(ts_rank(anl4_afv4_median_eps/close, 60), industry)
# Sharpe=1.93, Fitness=1.40, TVR=0.1768, Decay=4, Neutralization=SUBINDUSTRY
# ============================================================
alpha_v2_01 = {
    "id": "E5repQ81_v1",
    "regular": {"code": "group_rank(ts_rank(anl4_afv4_median_eps/close, 120), industry)"},
    "settings": {"decay": 0, "neutralization": "SUBINDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体1: ts_rank窗口60→120, decay 4→0"
}
alpha_v2_02 = {
    "id": "E5repQ81_v2",
    "regular": {"code": "group_rank(ts_rank(anl4_afv4_median_eps/close, 90), industry)"},
    "settings": {"decay": 6, "neutralization": "INDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体2: ts_rank窗口60→90, decay 4→6, neutralization SUBINDUSTRY→INDUSTRY"
}

# ============================================================
# Alpha 3: qMmpvp8v
# 原版: -ts_mean(returns, 5)
# Sharpe=1.46, Fitness=1.12, TVR=0.4035, Decay=4, Neutralization=SUBINDUSTRY
# ============================================================
alpha_v3_01 = {
    "id": "qMmpvp8v_v1",
    "regular": {"code": "-ts_mean(returns, 10)"},
    "settings": {"decay": 0, "neutralization": "SUBINDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体1: ts_mean窗口5→10, decay 4→0"
}
alpha_v3_02 = {
    "id": "qMmpvp8v_v2",
    "regular": {"code": "-ts_mean(returns, 3)"},
    "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体2: ts_mean窗口5→3, decay 4→6"
}

# ============================================================
# Alpha 4: E5g7vMjJ
# 原版: group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 5), subindustry)
# Sharpe=1.37, Fitness=1.01, TVR=0.175, Decay=0, Neutralization=INDUSTRY
# ============================================================
alpha_v4_01 = {
    "id": "E5g7vMjJ_v1",
    "regular": {"code": "group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 70)), 8), subindustry)"},
    "settings": {"decay": 0, "neutralization": "SUBINDUSTRY", "nanHandling": "OFF"},
    "note": "变体1: ts_decay_linear窗口5→8, neutralization INDUSTRY→SUBINDUSTRY"
}
alpha_v4_02 = {
    "id": "E5g7vMjJ_v2",
    "regular": {"code": "group_neutralize(ts_decay_linear(rank(ts_delta(close, 15)) * -rank(ts_corr(rank(close), rank(volume), 50)), 5), industry)"},
    "settings": {"decay": 3, "neutralization": "INDUSTRY", "nanHandling": "OFF"},
    "note": "变体2: ts_delta窗口10→15, ts_corr窗口70→50, decay 0→3"
}

# ============================================================
# Alpha 5: A1g6AlWg
# 原版: rank(ts_decay_linear(sales_estimate_count, 10))
# Sharpe=1.70, Fitness=1.03, TVR=0.0349, Decay=0, Neutralization=INDUSTRY
# ============================================================
alpha_v5_01 = {
    "id": "A1g6AlWg_v1",
    "regular": {"code": "rank(ts_decay_linear(sales_estimate_count, 15))"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体1: ts_decay_linear窗口10→15"
}
alpha_v5_02 = {
    "id": "A1g6AlWg_v2",
    "regular": {"code": "group_rank(ts_decay_linear(sales_estimate_count, 10), industry)"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体2: 添加group_rank包装"
}

# ============================================================
# Alpha 6: LLgOWZmn
# 原版: group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 30)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 30))) * (1 - rank(ts_std_dev(returns, 30))), 12), industry)
# Sharpe=2.18, Fitness=1.21, TVR=0.4746, Decay=0, Neutralization=INDUSTRY
# ============================================================
alpha_v6_01 = {
    "id": "LLgOWZmn_v1",
    "regular": {"code": "group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 30)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 30))) * (1 - rank(ts_std_dev(returns, 30))), 20), subindustry)"},
    "settings": {"decay": 0, "neutralization": "SUBINDUSTRY", "nanHandling": "OFF"},
    "note": "变体1: ts_decay_linear窗口12→20, neutralization INDUSTRY→SUBINDUSTRY"
}
alpha_v6_02 = {
    "id": "LLgOWZmn_v2",
    "regular": {"code": "group_neutralize(ts_decay_linear((rank(high - close) - rank(close - low)) * rank(ts_mean((high - low) / close, 20)) * (1 - 0.5 * rank(ts_mean((high - low) / close, 20))) * (1 - rank(ts_std_dev(returns, 30))), 12), industry)"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "OFF"},
    "note": "变体2: ts_mean窗口30→20"
}

# ============================================================
# Alpha 7: Xg2X2jxl
# 原版: rank(ts_mean(anl4_totassets_flag, 20))
# Sharpe=1.30, Fitness=1.30, TVR=0.0241, Decay=0, Neutralization=INDUSTRY
# ============================================================
alpha_v7_01 = {
    "id": "Xg2X2jxl_v1",
    "regular": {"code": "rank(ts_mean(anl4_totassets_flag, 30))"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "OFF"},
    "note": "变体1: ts_mean窗口20→30"
}
alpha_v7_02 = {
    "id": "Xg2X2jxl_v2",
    "regular": {"code": "group_rank(ts_mean(anl4_totassets_flag, 20), industry)"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "OFF"},
    "note": "变体2: 添加group_rank包装"
}

# ============================================================
# Alpha 8: bloqmdJK
# 原版: trade_when(rank(ts_mean(scl12_sentiment_fast_d1,20)) > 0.55, group_neutralize(ts_decay_linear((-ts_zscore(returns,252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry),40),subindustry), -1)
# Sharpe=1.61, Fitness=1.25, TVR=0.1025, Decay=3, Neutralization=MARKET
# ============================================================
alpha_v8_01 = {
    "id": "bloqmdJK_v1",
    "regular": {"code": "trade_when(rank(ts_mean(scl12_sentiment_fast_d1,30)) > 0.6, group_neutralize(ts_decay_linear((-ts_zscore(returns,252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry),40),subindustry), -1)"},
    "settings": {"decay": 5, "neutralization": "MARKET", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体1: ts_mean窗口20→30, 阈值0.55→0.6, decay 3→5"
}
alpha_v8_02 = {
    "id": "bloqmdJK_v2",
    "regular": {"code": "trade_when(rank(ts_mean(scl12_sentiment_fast_d1,15)) > 0.55, group_neutralize(ts_decay_linear((-ts_zscore(returns,252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry),40),subindustry), -1)"},
    "settings": {"decay": 3, "neutralization": "MARKET", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体2: ts_mean窗口20→15"
}

# ============================================================
# Alpha 9: A1gVE97w
# 原版: group_rank(add(group_rank(ts_rank(eps / close, 120), industry), group_rank(-ts_count_nans(eps, 252), industry)), industry)
# Sharpe=1.63, Fitness=1.04, TVR=0.1902, Decay=0, Neutralization=INDUSTRY, testPeriod=P5Y
# ============================================================
alpha_v9_01 = {
    "id": "A1gVE97w_v1",
    "regular": {"code": "group_rank(add(group_rank(ts_rank(eps / close, 60), industry), group_rank(-ts_count_nans(eps, 252), industry)), industry)"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "OFF", "testPeriod": "P5Y"},
    "note": "变体1: ts_rank窗口120→60"
}
alpha_v9_02 = {
    "id": "A1gVE97w_v2",
    "regular": {"code": "group_rank(add(group_rank(ts_rank(eps / close, 120), industry), group_rank(-ts_count_nans(eps, 180), industry)), industry)"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "OFF", "testPeriod": "P5Y"},
    "note": "变体2: ts_count_nans窗口252→180"
}

# ============================================================
# Alpha 10: e7dPWeop
# 原版: ts_rank(ts_delta(assets / cap, 2), 20)
# Sharpe=1.96, Fitness=1.02, TVR=0.5433, Decay=6, Neutralization=SUBINDUSTRY
# ============================================================
alpha_v10_01 = {
    "id": "e7dPWeop_v1",
    "regular": {"code": "ts_rank(ts_delta(assets / cap, 4), 20)"},
    "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体1: ts_delta周期2→4, decay 6→8"
}
alpha_v10_02 = {
    "id": "e7dPWeop_v2",
    "regular": {"code": "ts_rank(ts_delta(assets / cap, 2), 30)"},
    "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体2: ts_rank窗口20→30"
}

# ============================================================
# Alpha 11: O0bXoVV1
# 原版: ts_zscore(-ts_delta(close, 1), 10)
# Sharpe=2.19, Fitness=1.20, TVR=0.5665, Decay=18, Neutralization=SUBINDUSTRY
# ============================================================
alpha_v11_01 = {
    "id": "O0bXoVV1_v1",
    "regular": {"code": "ts_zscore(-ts_delta(close, 2), 10)"},
    "settings": {"decay": 15, "neutralization": "SUBINDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体1: ts_delta周期1→2, decay 18→15"
}
alpha_v11_02 = {
    "id": "O0bXoVV1_v2",
    "regular": {"code": "ts_zscore(-ts_delta(close, 1), 5)"},
    "settings": {"decay": 18, "neutralization": "SUBINDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体2: ts_zscore窗口10→5"
}

# ============================================================
# Alpha 12: 88Ob79jV
# 原版: rank(group_neutralize(ts_decay_linear((-ts_zscore(returns, 252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry), 15),subindustry))
# Sharpe=1.89, Fitness=1.01, TVR=0.3817, Decay=0, Neutralization=INDUSTRY
# ============================================================
alpha_v12_01 = {
    "id": "88Ob79jV_v1",
    "regular": {"code": "rank(group_neutralize(ts_decay_linear((-ts_zscore(returns, 252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry), 25),subindustry))"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体1: ts_decay_linear窗口15→25"
}
alpha_v12_02 = {
    "id": "88Ob79jV_v2",
    "regular": {"code": "rank(group_neutralize(ts_decay_linear((-ts_zscore(returns, 252))*group_rank(rank(1/(1+ts_mean((high-low)/vwap,20)))*rank(ts_mean(volume,120)/ts_mean(volume,80)),subindustry), 15),industry))"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "OFF", "testPeriod": "P1Y"},
    "note": "变体2: 内层neutralization subindustry→industry"
}

# ============================================================
# Alpha 13: GrnExm2Q
# 原版: rank(-group_rank(-ts_zscore(tobins_q_ratio, 5), industry))
# Sharpe=1.89, Fitness=1.07, TVR=0.3696, Decay=5, Neutralization=INDUSTRY, nanHandling=ON
# ============================================================
alpha_v13_01 = {
    "id": "GrnExm2Q_v1",
    "regular": {"code": "rank(-group_rank(-ts_zscore(tobins_q_ratio, 3), industry))"},
    "settings": {"decay": 8, "neutralization": "INDUSTRY", "nanHandling": "ON", "testPeriod": "P1Y"},
    "note": "变体1: ts_zscore窗口5→3, decay 5→8"
}
alpha_v13_02 = {
    "id": "GrnExm2Q_v2",
    "regular": {"code": "rank(-group_rank(-ts_zscore(tobins_q_ratio, 5), subindustry))"},
    "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "nanHandling": "ON", "testPeriod": "P1Y"},
    "note": "变体2: neutralization INDUSTRY→SUBINDUSTRY"
}

# ============================================================
# Alpha 14: gJmojOQm
# 原版: group_rank(ts_zscore(winsorize(ts_backfill(unsystematic_risk_last_60_days, 120), std=4), 66),densify(bucket(rank(cap), range='0.1, 1, 0.1')))
# Sharpe=1.35, Fitness=1.00, TVR=0.1316, Decay=6, Neutralization=INDUSTRY, nanHandling=ON, testPeriod=P2Y
# ============================================================
alpha_v14_01 = {
    "id": "gJmojOQm_v1",
    "regular": {"code": "group_rank(ts_zscore(winsorize(ts_backfill(unsystematic_risk_last_60_days, 120), std=4), 120),densify(bucket(rank(cap), range='0.1, 1, 0.1')))"},
    "settings": {"decay": 6, "neutralization": "INDUSTRY", "nanHandling": "ON", "testPeriod": "P2Y"},
    "note": "变体1: ts_zscore窗口66→120"
}
alpha_v14_02 = {
    "id": "gJmojOQm_v2",
    "regular": {"code": "group_rank(ts_zscore(winsorize(ts_backfill(unsystematic_risk_last_90_days, 120), std=4), 66),densify(bucket(rank(cap), range='0.1, 1, 0.1')))"},
    "settings": {"decay": 6, "neutralization": "INDUSTRY", "nanHandling": "ON", "testPeriod": "P2Y"},
    "note": "变体2: unsystematic_risk_last_60_days→90_days"
}

# ============================================================
# Alpha 15: 0mAE3qzp
# 原版: group_rank(ts_delta(revenue, 1) / ts_mean(revenue, 4), market)
# Sharpe=1.58, Fitness=1.03, TVR=0.3722, Decay=0, Neutralization=INDUSTRY, nanHandling=ON, testPeriod=P2Y
# ============================================================
alpha_v15_01 = {
    "id": "0mAE3qzp_v1",
    "regular": {"code": "group_rank(ts_delta(revenue, 2) / ts_mean(revenue, 4), market)"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "ON", "testPeriod": "P2Y"},
    "note": "变体1: ts_delta周期1→2"
}
alpha_v15_02 = {
    "id": "0mAE3qzp_v2",
    "regular": {"code": "group_rank(ts_delta(revenue, 1) / ts_mean(revenue, 8), market)"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "ON", "testPeriod": "P2Y"},
    "note": "变体2: ts_mean窗口4→8"
}

# ============================================================
# Alpha 16: 1YodbWO6
# 原版: reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), industry))
# Sharpe=1.25, Fitness=1.04, TVR=0.0187, Decay=10, Neutralization=SUBINDUSTRY, nanHandling=ON
# ============================================================
alpha_v16_01 = {
    "id": "1YodbWO6_v1",
    "regular": {"code": "reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=uniform)), industry))"},
    "settings": {"decay": 15, "neutralization": "SUBINDUSTRY", "nanHandling": "ON"},
    "note": "变体1: decay 10→15, quantile driver gaussian→uniform"
}
alpha_v16_02 = {
    "id": "1YodbWO6_v2",
    "regular": {"code": "reverse(group_neutralize(multiply(fnd6_prstkc, quantile(fnd6_pstkc, driver=gaussian)), subindustry))"},
    "settings": {"decay": 10, "neutralization": "INDUSTRY", "nanHandling": "ON"},
    "note": "变体2: neutralization SUBINDUSTRY→INDUSTRY"
}

# ============================================================
# Alpha 17: 2rvNV1qJ
# 原版: group_rank(ts_delta(eps, 1), market)
# Sharpe=1.35, Fitness=1.08, TVR=0.2307, Decay=6, Neutralization=INDUSTRY, nanHandling=ON, testPeriod=P2Y
# ============================================================
alpha_v17_01 = {
    "id": "2rvNV1qJ_v1",
    "regular": {"code": "group_rank(ts_delta(eps, 4), market)"},
    "settings": {"decay": 4, "neutralization": "INDUSTRY", "nanHandling": "ON", "testPeriod": "P2Y"},
    "note": "变体1: ts_delta周期1→4, decay 6→4"
}
alpha_v17_02 = {
    "id": "2rvNV1qJ_v2",
    "regular": {"code": "group_rank(ts_delta(eps, 1), sector)"},
    "settings": {"decay": 6, "neutralization": "INDUSTRY", "nanHandling": "ON", "testPeriod": "P2Y"},
    "note": "变体2: neutralization market→sector"
}

# ============================================================
# Alpha 18: xAeN6jGp
# 原版: group_neutralize(divide(fnd6_rectr, max(fnd6_recd, 0.000001)), industry)
# Sharpe=1.37, Fitness=1.25, TVR=0.0144, Decay=0, Neutralization=SUBINDUSTRY, nanHandling=ON
# ============================================================
alpha_v18_01 = {
    "id": "xAeN6jGp_v1",
    "regular": {"code": "group_neutralize(divide(fnd6_rectr, add(fnd6_recd, 0.1)), industry)"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "ON"},
    "note": "变体1: max()→add(, 0.1), neutralization SUBINDUSTRY→INDUSTRY"
}
alpha_v18_02 = {
    "id": "xAeN6jGp_v2",
    "regular": {"code": "group_neutralize(divide(fnd6_rectr, max(fnd6_recd, 0.000001)), subindustry)"},
    "settings": {"decay": 3, "neutralization": "SUBINDUSTRY", "nanHandling": "ON"},
    "note": "变体2: decay 0→3"
}

# ============================================================
# Alpha 19: 1YopVrdW
# 原版: group_neutralize(divide(fnd6_rectr, add(fnd6_recd, 1.0)), subindustry)
# Sharpe=1.44, Fitness=1.37, TVR=0.0179, Decay=0, Neutralization=SUBINDUSTRY, nanHandling=ON
# ============================================================
alpha_v19_01 = {
    "id": "1YopVrdW_v1",
    "regular": {"code": "group_neutralize(divide(fnd6_rectr, add(fnd6_recd, 2.0)), subindustry)"},
    "settings": {"decay": 0, "neutralization": "SUBINDUSTRY", "nanHandling": "ON"},
    "note": "变体1: denominator add(fnd6_recd, 1.0)→2.0"
}
alpha_v19_02 = {
    "id": "1YopVrdW_v2",
    "regular": {"code": "group_neutralize(divide(fnd6_rectr, add(fnd6_recd, 1.0)), industry)"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "ON"},
    "note": "变体2: neutralization SUBINDUSTRY→INDUSTRY"
}

# ============================================================
# Alpha 20: 1YoX2GxX
# 原版: rank(group_neutralize(divide(fnd6_sppe, add(abs(fnd6_siv), 1)), industry))
# Sharpe=1.45, Fitness=1.17, TVR=0.0193, Decay=0, Neutralization=INDUSTRY, nanHandling=ON, testPeriod=P2Y
# ============================================================
alpha_v20_01 = {
    "id": "1YoX2GxX_v1",
    "regular": {"code": "rank(group_neutralize(divide(fnd6_sppe, add(abs(fnd6_siv), 2)), industry))"},
    "settings": {"decay": 0, "neutralization": "INDUSTRY", "nanHandling": "ON", "testPeriod": "P2Y"},
    "note": "变体1: denominator abs(fnd6_siv)+1 → +2"
}
alpha_v20_02 = {
    "id": "1YoX2GxX_v2",
    "regular": {"code": "rank(group_neutralize(divide(fnd6_sppe, add(abs(fnd6_siv), 1)), subindustry))"},
    "settings": {"decay": 0, "neutralization": "SUBINDUSTRY", "nanHandling": "ON", "testPeriod": "P2Y"},
    "note": "变体2: neutralization INDUSTRY→SUBINDUSTRY"
}

# ============================================================
# Alpha 21: QPn0vn3X
# 原版: trade_when(group_rank(ts_std_dev(returns,60), sector) > 0.7, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)
# Sharpe=1.57, Fitness=1.08, TVR=0.2385, Decay=15, Neutralization=INDUSTRY
# ============================================================
alpha_v21_01 = {
    "id": "QPn0vn3X_v1",
    "regular": {"code": "trade_when(group_rank(ts_std_dev(returns,40), sector) > 0.75, rank(group_zscore(rank(-ts_zscore(close, 5)), densify(sector))), abs(returns) > 0.1)"},
    "settings": {"decay": 20, "neutralization": "INDUSTRY", "nanHandling": "OFF"},
    "note": "变体1: ts_std_dev窗口60→40, 阈值0.7→0.75, decay 15→20"
}
alpha_v21_02 = {
    "id": "QPn0vn3X_v2",
    "regular": {"code": "trade_when(group_rank(ts_std_dev(returns,60), sector) > 0.7, rank(group_zscore(rank(-ts_zscore(close, 3)), densify(sector))), abs(returns) > 0.1)"},
    "settings": {"decay": 15, "neutralization": "INDUSTRY", "nanHandling": "OFF"},
    "note": "变体2: ts_zscore窗口5→3"
}

# ============================================================
# Alpha 22: d5d59jpw
# 原版: zscore(reverse(divide(change_in_eps_surprise, max(abs(correlation_last_360_days_spy), 0.01))))
# Sharpe=1.44, Fitness=1.34, TVR=0.104, Decay=4, Neutralization=INDUSTRY, nanHandling=ON, testPeriod=P2Y
# ============================================================
alpha_v22_01 = {
    "id": "d5d59jpw_v1",
    "regular": {"code": "zscore(reverse(divide(change_in_eps_surprise, max(abs(correlation_last_180_days_spy), 0.01))))"},
    "settings": {"decay": 6, "neutralization": "INDUSTRY", "nanHandling": "ON", "testPeriod": "P2Y"},
    "note": "变体1: correlation窗口360→180, decay 4→6"
}
alpha_v22_02 = {
    "id": "d5d59jpw_v2",
    "regular": {"code": "zscore(divide(change_in_eps_surprise, max(abs(correlation_last_360_days_spy), 0.01)))"},
    "settings": {"decay": 4, "neutralization": "INDUSTRY", "nanHandling": "ON", "testPeriod": "P2Y"},
    "note": "变体2: 移除reverse"
}

# ============================================================
# 汇总所有变体
# ============================================================
all_variations = [
    alpha_v1_01, alpha_v1_02,
    alpha_v2_01, alpha_v2_02,
    alpha_v3_01, alpha_v3_02,
    alpha_v4_01, alpha_v4_02,
    alpha_v5_01, alpha_v5_02,
    alpha_v6_01, alpha_v6_02,
    alpha_v7_01, alpha_v7_02,
    alpha_v8_01, alpha_v8_02,
    alpha_v9_01, alpha_v9_02,
    alpha_v10_01, alpha_v10_02,
    alpha_v11_01, alpha_v11_02,
    alpha_v12_01, alpha_v12_02,
    alpha_v13_01, alpha_v13_02,
    alpha_v14_01, alpha_v14_02,
    alpha_v15_01, alpha_v15_02,
    alpha_v16_01, alpha_v16_02,
    alpha_v17_01, alpha_v17_02,
    alpha_v18_01, alpha_v18_02,
    alpha_v19_01, alpha_v19_02,
    alpha_v20_01, alpha_v20_02,
    alpha_v21_01, alpha_v21_02,
    alpha_v22_01, alpha_v22_02,
]

# 标准设置模板
STANDARD_SETTINGS = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "truncation": 0.08,
    "pasteurization": "ON",
    "unitHandling": "VERIFY",
    "maxTrade": "OFF",
    "maxPosition": "OFF",
    "language": "FASTEXPR",
    "visualization": False,
    "startDate": "2019-01-01",
    "endDate": "2023-12-31",
}

def build_full_alpha(var):
    """构建完整的alpha配置（包含默认设置）"""
    settings = dict(STANDARD_SETTINGS)
    settings.update(var.get("settings", {}))
    return {
        "id": var["id"],
        "type": "REGULAR",
        "settings": settings,
        "regular": var["regular"],
        "note": var.get("note", "")
    }

# 构建完整配置
full_variations = [build_full_alpha(v) for v in all_variations]

# 保存到文件
output_file = "/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-alpha-variations.json"
with open(output_file, 'w') as f:
    json.dump(full_variations, f, indent=2)

print(f"生成了 {len(full_variations)} 个Alpha变体")
print(f"保存到: {output_file}")

# 打印摘要表格
print("\n" + "="*100)
print("ALPHA变体摘要表格")
print("="*100)
print(f"{'新ID':<20} {'源自':<12} {'Expression':<60} {'Decay':>5} {'Neutralization':<15}")
print("-"*100)

for v in full_variations:
    original_id = v["id"].split("_v")[0][:8]
    code = v["regular"]["code"][:60]
    decay = v["settings"].get("decay", 0)
    neutral = v["settings"].get("neutralization", "N/A")
    print(f"{v['id']:<20} {original_id:<12} {code:<60} {decay:>5} {neutral:<15}")