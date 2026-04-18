# Skill 调用与门禁协议

## 何时读取

遇到下列情况时读取本文件：

- 任务可能匹配一个或多个 Skill
- 任务是模糊设计、多步实现或高风险决策
- 任务涉及调试、验证或完成声明

默认不读本文件。只有当 Skill 选择或门禁顺序会影响执行结果时才加载。

## 总规则

- 命中的 Skill 是执行协议，不是可选建议。
- 先走流程型 Skill，再走领域型 Skill。
- 用户说“直接做”不等于可以跳过门禁。
- 已有书面计划时，优先按计划执行，不要临场改成随意推进。

## 常见触发

### 模糊、高风险、跨模块、约束不清

先用：

- `evolutionary-constraint-engineering`

### 新的多步实现，但还没有被批准的实施计划

先用：

- `writing-plans`

### 已经有正式实施计划，需要按计划执行

先用：

- `executing-plans`

### Alpha 研究、Fast Expression、字段发现、指标诊断、submission triage

先用：

- `worldquant-brain-alpha-engineering`

### 缺陷排查、测试失败、结果异常

先用：

- `systematic-debugging`

### 任何“已完成 / 已修复 / 已通过 / 可提交”声明前

必须用：

- `verification-before-completion`

## 组合顺序

推荐顺序：

1. 约束或计划类 Skill
2. 领域类 Skill
3. 验证类 Skill

示例：

- 模糊的 alpha 研究任务：
  `evolutionary-constraint-engineering` -> `worldquant-brain-alpha-engineering`
- 已有计划的功能落地：
  `executing-plans` -> 相关领域 Skill -> `verification-before-completion`
- 调试任务：
  `systematic-debugging` -> 相关领域 Skill -> `verification-before-completion`

## 硬门禁

- 没有完成前置 Skill，不开始实现。
- 没有 fresh verification，不声明成功。
- 不能因为任务描述很长，就跳过 Skill。
- 不能把 Skill 当成仅供参考的背景材料。
