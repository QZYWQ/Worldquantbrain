# Submission UI Audit Log

- Timestamp: 2026-04-28 09:34 (Asia/Shanghai)
- Scope: offline review of current WorldQuant BRAIN UI; no live submission executed
- WQB API: not enabled in this session
- `agent-policies/`: not touched

## Reviewed candidate queue

Source: `runs/recommended_submission.json`

Top live-valid queue members currently recommended for manual submission are:

1. `gen001-8c5bbca421a8` — `ts_rank(anl4_af_eps_value / close, 60)`
2. `gen001-232ac5c76bd9` — `ts_mean(pv13_revere_index_value, 63)`
3. `gen001-8344235797bd` — `group_rank(ts_sum(earnings_per_share_average/close, 60), industry)`
4. `gen001-bba7a731f511` — `group_rank(ts_rank(earnings_per_share_average/close, 120), pv13_revere_key_sector_total)`
5. `gen001-7bb07f9b2ffa` — `group_rank(ts_rank(anl4_af_eps_value / close, 60), pv13_revere_key_sector_total)`

## Official UI checks performed

### Simulate page

- Opened `https://platform.worldquantbrain.com/simulate`.
- Confirmed the page exposes `CODE`, `RESULTS`, and `Settings` controls.
- Confirmed the editor is present and accepts Fast Expression input.
- Confirmed that after simulation flow opens the properties panel, the right side contains:
  - `Name`
  - `Category`
  - `Tags`
  - `Color`
  - `Description`
  - `Check Submission`
  - `Submit Alpha`
- Observed that `Check Submission` and `Submit Alpha` are disabled until the simulation / validation state is ready.
- Observed the RESULTS pane placeholder text: `Simulate an alpha to view the results here.` when no completed simulation is selected.

### Alphas page

- Opened `https://platform.worldquantbrain.com/alphas/unsubmitted`.
- Confirmed the page has `Unsubmitted` and `Submitted` tabs plus a filterable table.
- Confirmed the table includes columns such as:
  - Name
  - Competition
  - Type
  - Status
  - Language
  - Date Created (EST)
  - Region
  - Universe
  - Sharpe
  - Returns
  - Turnover
  - Date Submitted (EST)
- Observed the page is currently populated with existing UNSUBMITTED alphas from the account.

## Submission safety reminder

- No alpha was submitted.
- Before any live submission, the launching shell must set `WQB_API_ENABLED=true`.
- Live submission still requires explicit user confirmation and credentials.
