# 学习循环：从课程材料到 LITE S0 参数扫描环

## 来源
用户提供的 WorldQuant 量化课程材料，包含 50 个 Alpha 的表现分析。

## 关键洞察
- 同一因子在不同 Decay/Neutralization 组合下表现差异巨大
- Alpha 10 (Decay=1, No Neutralization) → 高回报高风险
- Alpha 26 (Decay=55, Subindustry Neutralization) → 低风险稳定回报
- 课程明确建议"调整 Decay 和 Neutralization 进行优化"

## 当前骨架缺口
我们的 S0 基线验证仅使用 `ts_rank(field, 60)` 单一参数，可能导致：
- 因子本身有信号，但对默认 60 天 Decay 不敏感 → 被误杀
- 因子需要 Neutralization 控制风险，但未测试 → 裸值表现差

## 落地方案
在 LITE S0 阶段加入 6 组轻量参数扫描环：
- 3 Decay (20, 60, 120) × 2 Neutralization (None, Market)
- 取最佳 TEST Sharpe 作为判定依据
- 通过环境变量 LITE_PARAM_SCAN 控制开关
- 保持 S0 的极简特性，不进入参数优化

## 影响范围
- 仅增强 LITE 引擎，不影响 RECURVE/LENS 主线
- 等 pv13 候选进入 S0 时实际执行
- 不修改孵化协议核心规则

## 日期
2026-04-27
