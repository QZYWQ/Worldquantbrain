# 自动生产摘要（优化闭环）

- 生成时间：2026-04-28 07:49:29 (Asia/Shanghai)
- 模式：完全离线
- WQB API：未调用
- 真实提交：未执行
- `agent-policies/`：未修改

## 轮次结果

- Round 1：完成，结构质量从 B 提升到 **A**。
- canonical candidates：20
- average novelty：0.386
- unique operator types：7
- unique field types：16
- dry-run planned candidates：10
- dry-run top recommendations：10

## 最终推荐

- `ts_rank(sentiment_focus_rank, 60)`
- `ts_mean(pv13_revere_index_value, 63)`
- `ts_rank(anl4_af_eps_value / close, 60)`
- `ts_rank(anl4_afv4_median_eps/close, 60)`
- `group_rank(ts_rank(fundamental_model_slow_ratio_equity_cap_follow_up_batch_06/close, 120), industry)`

## 风险提示

- 所有提交必须由用户手动执行。
- 如果要 live submit，先显式设置 `WQB_API_ENABLED=true` 并准备凭证。
- 当前结果已经达到可用的 A 级结构质量，但仍建议先做小批量人工检查。
