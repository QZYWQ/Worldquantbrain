# Manual Submission Steps (Preview Only)

- Date: 2026-04-28
- Status: preparation only, no live submission executed
- Scope: based on current official `platform.worldquantbrain.com` UI observed in this session

## Recommended submission order

Use the top 3 first, then stop and inspect results before considering the backup 2.

1. `gen001-8c5bbca421a8` — `ts_rank(anl4_af_eps_value / close, 60)`
2. `gen001-232ac5c76bd9` — `ts_mean(pv13_revere_index_value, 63)`
3. `gen001-8344235797bd` — `group_rank(ts_sum(earnings_per_share_average/close, 60), industry)`
4. `gen001-bba7a731f511` — backup only
5. `gen001-7bb07f9b2ffa` — backup only

## Current UI flow

### 1) Open Simulate

- Go to `https://platform.worldquantbrain.com/simulate`.
- Paste one candidate Fast Expression into the editor.
- Use the `CODE` / `RESULTS` tabs to switch between editing and result inspection.

### 2) Save / validate the alpha

- Fill the right-side properties panel if needed:
  - `Name`
  - `Category`
  - `Tags`
  - `Description`
- Run the simulation / validation flow.
- Wait until the UI shows a completed result state.
- The `Check Submission` and `Submit Alpha` buttons are disabled until the alpha is ready.

### 3) Check submission conditions

- Click `Check Submission` once the alpha is ready.
- Confirm the platform checks pass.
- Do not proceed if the platform shows an error, captcha, or authentication issue.

### 4) Submit manually

- Click `Submit Alpha` only after the platform shows the alpha is ready.
- Submit one alpha at a time.
- Pause after each alpha and inspect the result before continuing.

### 5) Confirm in Alphas list

- Open `https://platform.worldquantbrain.com/alphas/unsubmitted`.
- Verify the new alpha appears in the account table.
- Review the `Sharpe`, `Returns`, and `Turnover` columns.

## Required safety gate

- Before any live submission, export `WQB_API_ENABLED=true` in the same shell that launches the live command.
- Keep live submission manual and user-confirmed.
- If the site shows authentication problems, stop immediately and report the issue.
