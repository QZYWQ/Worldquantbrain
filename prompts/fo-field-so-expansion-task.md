# 任务：执行 FO Field SO Expansion

## 目标
对两个FO初测通过的field进行SO升阶测试

## 已有资源

### 1. fn_interest_paid_net_q（已创建batch）
- Batch文件: `/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches/2026-05-19-fn-interest-paid-net-q-expansion.json`
- Script: `/Users/zpdedn/Documents/github/worldquantAPI/user/run_fn_interest_paid_net_q_so.py`
- 变体数: 15个

**执行命令**:
```bash
cd /Users/zpdedn/Documents/github/worldquantAPI/user && python3 run_fn_interest_paid_net_q_so.py
```

**检查结果**: 查看 `/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/2026-05-19-fn-interest-paid-net-q-expansion_results.json`

### 2. trade_when_momentum（需新建batch）

**Field**: `trade_when_momentum`
**FO Sharpe**: 0.71
**注意**: trade_when已知可能产生SC问题，测试时需谨慎

**创建Batch文件**: `/Users/zpdedn/Documents/project/Worldquantbrain/runs/candidate-batches/2026-05-21-trade-when-momentum-so.json`

```json
{
  "_instructions": [
    "FO batch: trade_when_momentum field exploration",
    "FO Sharpe=0.71, 初测通过",
    "注意: trade_when操作已知可能产生SC问题，需测试SC",
    "参考成功案例: QPn0vn3X (trade_when + sector neutralization + decay=15)"
  ],
  "schema_version": "1.0.0",
  "capture_id": "2026-05-21-trade-when-momentum-so",
  "topic": "trade_when_momentum_so",
  "author": "Claude",
  "source": "hypothesis_driven",
  "hypothesis": "动量触发时交易，捕捉市场情绪转换点",
  "settings_template": {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "decay": 0,
    "neutralization": "SUBINDUSTRY",
    "truncation": 0.08,
    "pasteurization": "ON",
    "unitHandling": "VERIFY",
    "nanHandling": "ON",
    "language": "FASTEXPR"
  },
  "candidates": [
    {
      "name": "baseline_rank",
      "description": "Baseline: rank(trade_when_momentum)",
      "expression": "rank(trade_when_momentum)",
      "settings": {}
    },
    {
      "name": "baseline_zscore",
      "description": "Baseline: zscore",
      "expression": "zscore(trade_when_momentum)",
      "settings": {}
    },
    {
      "name": "group_neutralize_industry",
      "description": "Industry neutralized",
      "expression": "group_neutralize(rank(trade_when_momentum), industry)",
      "settings": {}
    },
    {
      "name": "group_neutralize_sector",
      "description": "Sector neutralized per QPn0vn3X pattern",
      "expression": "group_neutralize(rank(trade_when_momentum), sector)",
      "settings": {}
    },
    {
      "name": "decay15_sector",
      "description": "decay=15 + sector per QPn0vn3X success",
      "expression": "group_neutralize(rank(trade_when_momentum), sector)",
      "settings": {"decay": 15}
    },
    {
      "name": "decay6_sector",
      "description": "decay=6 + sector",
      "expression": "group_neutralize(rank(trade_when_momentum), sector)",
      "settings": {"decay": 6}
    },
    {
      "name": "ts_zscore_10",
      "description": "10-day ts_zscore smoothing",
      "expression": "ts_zscore(rank(trade_when_momentum), 10)",
      "settings": {}
    },
    {
      "name": "ts_mean_10",
      "description": "10-day ts_mean smoothing",
      "expression": "ts_mean(rank(trade_when_momentum), 10)",
      "settings": {}
    },
    {
      "name": "group_rank_market",
      "description": "Market group rank",
      "expression": "group_rank(rank(trade_when_momentum), market)",
      "settings": {}
    }
  ]
}
```

**创建Script**: `/Users/zpdedn/Documents/github/worldquantAPI/user/run_trade_when_momentum_so.py`

参考 `run_fn_interest_paid_net_q_so.py` 的格式，修改:
- `BATCH_FILE` 指向新建的 batch json
- `OUTPUT_DIR` 不变

**执行命令**:
```bash
cd /Users/zpdedn/Documents/github/worldquantAPI/user && python3 run_trade_when_momentum_so.py
```

## 升阶标准

通过条件:
- Sharpe >= 1.25
- Fitness >= 1.0
- TVR <= 0.7
- Self-Correlation < 0.7

## 输出要求

1. 记录每个变体的 Sharpe, Fitness, TVR, SC (如有)
2. 标记PASS和FAIL的变体
3. 对SC超标的变体，分析是否结构性问题

## 注意

- fn_interest_paid_net_q 的batch已存在，先检查是否已有结果，如有则分析结果不再重复运行
- trade_when_momentum 测试时关注SC值，trade_when已知可能产生高自相关