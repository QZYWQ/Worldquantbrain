# Alpha Framework Postmortem

## 结论先行

这次复盘的核心结论不是“WorldQuant Alpha 做不出来”，而是“当前流程能偶尔做出强候选，但还没有把强候选稳定转成可复用的生产流程”。

项目里已经出现过真实强结果：`E5repQ81 / anl4_afv4_median_60d_industry` 在官方检查层面拿到过 `CONCENTRATED_WEIGHT=PASS`、`LOW_FITNESS=PASS`、`LOW_SUB_UNIVERSE_SHARPE=PASS`、`SELF_CORRELATION=PASS` 的证据；但后续大量分支又连续死在覆盖率、holdout、sub-universe、full-IS gate、或“只是近邻微调”上。

所以真正的失败点是：

- 不是没有信号
- 不是没有调参
- 而是缺少一套能持续筛掉伪强候选、保留真强候选、并且阻止近邻死循环的研究操作系统

## 这次复盘的真实证据

- `runs/submission-memos/analyst-sibling-submission-memo.md` 记录了 `2026-04-19` 的真实提交 `E5repQ81`。
- `runs/submission-memos/E5repQ81-os-status-2026-04-19.md`、`runs/submission-memos/E5repQ81-os-status-2026-04-20.md`、`runs/submission-memos/E5repQ81-os-status-2026-04-20-0201.md` 记录了页面层面的 `ACTV / 4 PENDING` 观察。
- `runs/learning-loops/2026-04-23-daily-alpha-runner-203907.json` 记录了后来 `/alphas/{id}/check` 的更鲜活结果：`CONCENTRATED_WEIGHT=PASS`、`LOW_FITNESS=PASS`、`LOW_SUB_UNIVERSE_SHARPE=PASS`、`SELF_CORRELATION=PASS`。
- `runs/session-briefs/data-fields-USA-TOP3000-20260423.network-response` 记录了当前账号的真实 Data Explorer 字段覆盖与 crowding。

## 目前最重要的盲区

### 1) 先验字段验证不够硬

很多分支一开始默认“这个字段应该存在”，但官方 Data Explorer 里真正可用的字段并不等于记忆里的字段名。

当前账号里已经明确看到：

- `market_cap` 不在这份 Data Explorer 结果里
- `cashflow`、`working_capital`、`liabilities`、`assets`、`sales`、`revenue`、`operating_income` 只有约 `50%` coverage
- `shareholders_equity_total_2` coverage `84.69%`
- `total_assets_amount` coverage `80.35%`
- `anl4_afv4_median_eps` coverage `100%`
- `anl4_qfv4_median_eps` coverage `100%`
- `anl4_afv4_dts_spe` coverage `69.10%`
- `anl4_qfv4_dts_spe` coverage `72.37%`
- `snt_buzz` coverage `100%`

这说明一个根本问题：很多“研究失败”其实不是表达式失败，而是字段/数据家族选择阶段就已经埋雷。

### 2) 把“近邻微调”误当成“新研究”

大量失败分支只是在同一个 thesis 上做：

- 窗口长短变化
- 轻微 smoothing
- 直接 sign flip
- 同 family 里换一个相近字段

这类动作常常只是“参数化的重复”，不是真正的新信息源。

典型例子：

- `runs/expression-families/2026-04-21-operating-income-smoothed-history-position-follow-up.md`
- `runs/expression-families/2026-04-21-revenue-smoothed-history-position-follow-up.md`
- `runs/expression-families/2026-04-22-operating-income-sales-ratio-follow-up.md`
- `runs/expression-families/2026-04-22-capital-structure-balance-sheet-follow-up.md`

这些分支不断证明一件事：如果 thesis 本身没有换，单纯抠窗口最后只会把同一个洞挖深。

### 3) 对 holdout / full-IS 的权重还不够高

项目里已经多次出现“显示出来的 test card 看上去不错，但 full-IS gate 其实没过”的情况。

最典型的是：

- `runs/research-queues/2026-04-23-fundamental-model-slow-ratio-equity-cap.md`

里面明确写了：

- shown test-period card 可能很强
- 但 full-IS `LOW_SHARPE` / `LOW_FITNESS` 仍然失败

这类案例说明：如果决策被显示层面的 TEST 卡片牵着走，就会反复把资源投向“看起来活着、其实已经死了”的分支。

### 4) crowding 没有被系统化纳入第一层决策

字段可用不代表字段值得做。

当前 Data Explorer 里有些字段虽然覆盖高，但 crowding 已经很明显：

- `snt_buzz` alphaCount `9018`
- `volume` alphaCount `290781`
- `close` alphaCount `519483`
- `adv20` alphaCount `98264`

反过来，有些当前更适合做研究起点：

- `anl4_qfv4_median_eps` alphaCount `39`
- `anl4_afv4_median_eps` alphaCount `138`
- `anl4_afv4_dts_spe` alphaCount `82`
- `shareholders_equity_total_2` alphaCount `26`
- `total_assets_amount` alphaCount `85`

所以“覆盖率高”只是入场券，不是可用性证明；还必须看 crowding、userCount、以及你要不要真的把这个家族继续做下去。

### 5) kill 规则还不够像机器，不够像门禁

项目里其实已经有 kill 直觉，但还不够硬。

你现在最容易掉进的模式是：

- 一次失败后继续补窗口
- 第二次失败后再补 smoothing
- 第三次失败后换 group
- 最后把同一个家族包装成“又一个新思路”

更合理的做法应该是：

- 一旦 first-control 证明 thesis 方向错了，立刻 kill
- 一旦同源变体连续失败，直接切 family
- 只有当失败原因明显只是 coverage / NaN / group 结构时，才允许继续做一层修正

### 6) 研究预算分配过于集中

当前流程会很认真地打磨单个 family，但对“同时保留多个真正不同的信息源”不够激进。

这会导致：

- 一条线还没完全死，就占了太多注意力
- 新 family 没有足够快地进入并行对照
- 最终演化成“在一条旧线里反复抛光”

项目里的 `runs/learning-loops/2026-04-23-seed-expander-203907.md` 已经显示出一个更健康的方向：先把 family 分成 `explore / branch / hold / kill / exploit`，再按证据分配预算。

## 当前项目里已经证明有效的研究骨架

下面这些不是“想法”，而是已经在项目里被证据支持过的骨架：

### A. Analyst sibling / disagreement 比无脑 EPS 克隆更有机会

- `runs/expression-families/analyst-sibling-branch.md`
- `runs/expression-families/analyst-disagreement-branch.md`

这两类比单纯 EPS 级别的自我复制更像“换了信息源”。

### B. 低覆盖 fundamentals 不是不能做，但必须先把 coverage 和 crowding 看清

- `runs/expression-families/2026-04-23-fundamental-model-slow-ratio-cashflow-follow-up.md`
- `runs/expression-families/2026-04-23-fundamental-model-slow-ratio-equity-cap-follow-up.md`

它们说明：

- `cashflow / cap` 这类慢 ratio 可以活
- 但 `cashflow / assets`、`working_capital / cap` 之类很容易死
- 真正有效的入口不是“慢”，而是“慢 + 真实存在 + 覆盖够 + crowding 可接受”

### C. 真正的 first-pass 研究要把字段、分组、窗口拆开

这点在 `runs/learning-loops/official-alpha-cycle-04-project-lessons.md` 和 `runs/research-queues/official-alpha-cycle-04.json` 里已经反复出现：

- 先验证字段
- 再用一个最简单表达式
- 再只改一个 lever

这才是能复现的研究骨架。

## 重写后的 Alpha 整套流程

### Step 0: 先做真相源门禁

任何新 family 在写表达式前，先确认：

- 字段是否真的存在于当前账号的 Data Explorer
- coverage / dateCoverage / type / dataset / crowding 是否可接受
- region / delay / universe 是否匹配

没有这一步，后面的表达式优化很可能只是“在不存在的地面上盖楼”。

### Step 1: 写一句人话 thesis

必须明确三件事：

- 你在预测什么相对变化
- 为什么它应该存在
- 它更像短期、 中期、 还是慢变量

如果一句话说不清，就不要写表达式。

### Step 2: 选一个主信息源，不要混三类

先在下面四类里只选一类：

- analyst / sentiment
- fundamentals / slow ratio
- price-volume / short horizon
- event / low turnover

不要一开始把两到三类揉在一起。

### Step 3: 第一批只跑“直签名控制 + 一个主变体”

第一批必须足够小，建议只看：

- baseline sign
- 一个窗口控制
- 一个 field sibling

不要一上来加平滑、加事件门、加更复杂 group。

### Step 4: 先看失败类别，再看收益

读结果时优先级固定为：

1. 字段/coverage/weight 问题
2. full-IS Sharpe / Fitness
3. sub-universe
4. self-correlation
5. turnover
6. 才是 test card 的漂亮程度

### Step 5: follow-up 只能改一个轴

每次只允许改一个主轴：

- 信息源轴：换字段家族
- 比较轴：换 group / neutralization
- 时间轴：换窗口
- 形态轴：换 rank / ts_rank / ts_mean / zscore / backfill

一次改两个以上，后面就不知道到底是什么在起作用。

### Step 6: kill 规则要明确

建议把 family 直接分成三种结果：

- `keep exploring`
- `branch once`
- `kill`

建议的 kill 条件：

- 直签名控制都不成立
- 连续两次只靠 smoothing/window 变化也救不活
- full-IS gate 反复失败
- sub-universe 或 self-correlation 反复卡死
- 只是在重复已死 family 的近邻

### Step 7: 只有 full gates 过了才谈 submit-ready

submit-ready 必须同时满足：

- real official full-IS gates
- `SELF_CORRELATION` resolved
- 没有明显失败门
- 不是 killed family 的近邻

显示层面的 TEST card 只能做诊断，不能单独做结论。

## 以后最该执行的硬规则

1. 任何新家族先查 Data Explorer，不许先写表达式后补字段。
2. 任何 family 只允许一个主 thesis，不许把多个 thesis 混在一起。
3. 任何 follow-up 只改一个 lever，不许多轴一起改。
4. 任何连续两次弱结果的 family 都要切换，不许无限抛光。
5. 任何 submit-ready 判断都必须依赖真实官方 gate，而不是截图里的漂亮 TEST 卡。
6. 任何近邻分支都必须先证明自己不是 killed family 的轻微变体。

## 这次复盘真正补上的认知

- 成功不是随机出现的，而是对“字段真相、家族分类、门禁证据、kill 纪律”的综合结果。
- 不是所有看起来像 alpha 的表达式都值得继续研究。
- 真正的研究效率，不是更会改表达式，而是更早识别“这条线已经死了”。
- 你现在缺的不是更多想法，而是更硬的研究操作系统。

