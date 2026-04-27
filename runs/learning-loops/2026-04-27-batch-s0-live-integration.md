# 批量 S0 Live 集成记录

## 审计发现

- `scripts/worldquant_alpha_report.py` 已经提供了可复用的 WorldQuant 交互样式：
  - `POST /simulations` 提交模拟
  - 通过 `Location` 和 `Retry-After` 轮询结果
  - 解析 `alpha_id`、`Sharpe`、`Fitness`、`Turnover`
  - 支持 `BRAIN_USERNAME` / `BRAIN_PASSWORD`、`BRAIN_SESSION_COOKIE`、`BRAIN_AUTH_HEADERS`
- `scripts/result_ledger.py` 已有 `ResultLedger.insert_result(...)`，可直接写入本地 SQLite 账本。
- `runs/simulation-captures/` 的最近样本表明平台返回结构通常包含：
  - 顶层：`alphas`, `capture_id`, `captured_at`, `evidence`, `platform_settings`, `topic`
  - alpha 项：`alpha_id`, `expression`, `metrics`, `tests`, `status`, `stage`, `notes`
  - 指标项里常见 `test_sharpe`, `test_fitness`, `test_turnover`
- `harness/config.env` 当前只有 `EXTERNAL_KB_ROOT` 和 `WQB_SCRIPT_ROOT`，没有现成的 live 认证配置。

## 改造内容

- 在 `scripts/batch_s0_scan.py` 中补齐了 live 运行链路：
  - `load_config()`：从环境变量与 `harness/config.env` 读取 API 基址与认证信息
  - `load_progress()` / `save_progress()`：支持断点续跑；test-mode 下只打印不落盘
  - `submit_simulation()`：发送提交请求；test-mode 下打印请求方法、URL、请求头、请求体
  - `poll_result()`：轮询结果；test-mode 下返回 `TEST_MODE_DUMMY`
  - `write_result_to_ledger()`：真实模式写入 SQLite；test-mode 下仅打印即将写入的数据
  - `run_live()`：串联提交、轮询、记账、进度更新、节流与限流
- 支持：
  - 断点恢复：通过 `runs/evidence/batch_progress.json` 识别已完成/进行中的 candidate
  - 频率控制：每次提交后等待 30 秒，每 5 次提交后额外等待 120 秒
  - 每日上限：接近 4000 次时报错级别警告，达到上限停止新提交
  - 401 认证失败：重认证一次，仍失败则停止批次
  - 429 限流：等待 5 分钟，最多重试 3 次

## 当前限制

- 真实 live 仍依赖用户提供可用的 `WQ_API_BASE` 与认证凭据/头信息。
- test-mode 只能验证请求组装、进度更新与流程连通性，不能证明真实平台返回一定与模拟一致。
- 目前的结果解析依赖捕获样本与通用字段推断；若真实 live 返回结构不同，可能需要微调映射。
- 断点恢复以本地 progress 文件为主，若外部手工改写 progress 结构，恢复能力会下降。

## 下一步建议

1. 先在 test-mode 下用 1-2 个候选做一次完整流程复查。
2. 再用最小批次真实 live 验证 `POST /simulations`、轮询、结果 JSON 与账本入库。
3. 如果真实返回结构与捕获样本略有差异，再做一次字段映射修正。
4. 确认无误后，才把批量 live 作为常规工作流启用。
