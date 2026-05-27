# 2026-05-11 当前情况总结

## 一、已提交的Alpha状态

| Alpha | 家族 | Sharpe | Fitness | 状态 |
|-------|------|--------|---------|------|
| `E5g7vMjJ` | price_volume_corr | 1.37 | 1.01 | ACTIVE |
| `A1gVE97w` | eps_quality_yield | 1.63 | 1.04 | ACTIVE/OS |
| `bloqmdJK` | price_volume_social_gate | 1.61 | 1.25 | UNSUBMITTED (已通过所有检查) |

## 二、待确认的Alpha（Self-Correlation检查中）

**Close Delta家族 12个变体：**
- 所有变体共用同一底层信号 `-ts_delta(close,1)`
- IS Self-Correlation = 0.875（会超过0.7阈值）
- 所有12个的SC检查状态：**PENDING**
- 预计结果：很可能全部FAIL（同一信号源）

## 三、已失败的家族

| 家族 | 原因 |
|------|------|
| `short_interest_squeeze` | `short_interest`等字段不存在（unknown variable） |
| `eps_quality_yield_backup (QP2v6rVW)` | Self-Correlation = 0.9221 FAIL |
| `close_delta_family` | 共享同一信号源，预期SC会FAIL |

## 四、新研究探索（2026-05-11）

### Field Health诊断结果

| 数据源 | 字段 | 类型 | 可用性 |
|--------|------|------|--------|
| News18 | `nws18_qcm`, `nws18_bam` | EVENT(MATRIX) | **不可用** - 时间序列操作符不支持event输入 |
| Social12 | `scl12_buzz`, `scl12_sentiment` | VECTOR | 存在但产生无alpha（数据可能为常量/NaN） |
| Fundamental6 | `eps`, `assets` | VECTOR | **可用** - 已知工作正常 |
| Model16/77 | `fscore_total`, `mdl177_*` | VECTOR | 未测试，预计可用 |

### 关键发现
- News event字段是EVENT类型，无法与`ts_zscore`、`ts_rank`、`ts_mean`、`group_rank`一起使用
- Social media字段存在但可能数据有问题
- EPS/earnings字段在之前的研究中工作正常（`A1gVE97w`使用`eps/close`）

## 五、最佳决策建议

### 推荐路径：Model-Based Factor家族

**理由：**
1. `fscore_total`、`relative_valuation_rank_derivative`等是VECTOR类型，支持标准操作符
2. 覆盖率100%，用户少（100-150），竞争低
3. 与价格/情绪信号正交
4. 来自model16/model77数据集，之前未探索

### 候选字段
- `fscore_total` - 综合评分（含加速度）
- `relative_valuation_rank_derivative` - 估值排名变化
- `mdl177_valuemomemtummodel_vm_compositesn` - 价值动量复合信号

### 基础表达式思路
```
group_rank(ts_rank(fscore_total, 20), industry)
group_rank(ts_rank(relative_valuation_rank_derivative, 20), industry)
group_rank(ts_rank(mdl177_valuemomemtummodel_vm_compositesn, 20), industry)
```

## 六、下一步行动

1. **首先**：等待Close Delta的SC检查完成（如果FAIL，则确认需要新信号源）
2. **其次**：测试Model16/77字段的field health
3. **然后**：如果field health通过，运行基础表达式+sign control
4. **最后**：根据结果扩展家族

---

## 新窗口继续用提示词

请在新Claude Code窗口中使用以下提示词启动：

---

**提示词：**

```
继续WorldQuant BRAIN研究项目。当前情况：

1. 已提交活跃Alpha（3个）：
   - E5g7vMjJ (price_volume_corr): Sharpe 1.37
   - A1gVE97w (eps_quality_yield): Sharpe 1.63
   - bloqmdJK (price_volume_social_gate): Sharpe 1.61, SC PASS, UNSUBMITTED

2. 待确认Alpha：Close Delta家族12个变体，共用同一信号源(ts_delta close,1)，SC检查PENDING，预计FAIL

3. 已停止的家族：
   - short_interest（字段不存在）
   - eps_quality_yield_backup（SC 0.9221 FAIL）
   - news_sentiment（EVENT字段不支持ts_*操作符）

4. 可用数据源：
   - fundamental6 (eps, assets) - 已验证可用
   - model16/77 (fscore_total, mdl177_*) - 未测试，推荐

5. 研究队列：runs/research-queues/2026-05-11-research-queue.json

任务：
1. 首先通过API检查bloqmdJK是否可以提交（所有检查已通过）
2. 测试model16/77字段（fscore_total, relative_valuation_rank_derivative）的field health
3. 如果field health通过，运行基础表达式模拟
4. 基于结果扩展低相关性Alpha家族

凭证文件：scripts/wqb_session_creds.json
Chrome CDP端口：9333（已登录状态）
```

---

## 当前阻塞问题

- Chrome CDP session的API调用因认证问题间歇性返回401
- 需要在Chrome中保持登录状态
- 模拟运行时间较长（需要轮询等待完成）

## 文件位置

- 研究队列表：`runs/research-queues/2026-05-11-research-queue.json`
- Field Health结果：`runs/notes/daily/2026-05-11-field-health-diagnostic-results.md`
- 凭证文件：`scripts/wqb_session_creds.json`
- Playwright探针脚本：`scripts/wqb_playwright_probe.js`