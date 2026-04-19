# Analyst Disagreement Candidate Batch Blocked

- Date: `2026-04-20`
- Topic: `analyst_disagreement_dts_spe_industry`
- Source capture: `./runs/simulation-captures/analyst-disagreement-branch.json`
- Evidence: `./harness/artifacts/2026-04-20/ALPHA-CAND-003/candidate-check-status.json`

## Why No Candidate Batch JSON Was Written

- The project validator requires real `subuniverse_pass` values for every candidate.
- This disagreement batch still does not have real sub-universe or submission-check evidence.
- Writing `./runs/candidate-batches/...json` here would require placeholders, which is explicitly disallowed.

## Recovered Real Page Evidence

- `analyst_disagreement_afv4_inverse_120`
  - real unsubmitted alpha page recovered as `2rnp2GQb`
  - IS summary remained weak and no visible `Check Submission` section was available
- `analyst_disagreement_qfv4_inverse_60`
  - real unsubmitted alpha page recovered as `QP5GoVZG`
  - IS summary remained weak and no visible `Check Submission` section was available

## Triage Posture

- `group_rank(ts_rank(anl4_afv4_dts_spe, 60), industry)`: keep only as a diagnostic note; do not promote to candidate batch
- `group_rank(-ts_rank(anl4_afv4_dts_spe, 60), industry)`: kill
- `group_rank(-ts_rank(anl4_qfv4_dts_spe, 60), industry)`: kill
- `group_rank(-ts_rank(anl4_afv4_dts_spe, 120), industry)`: kill

## Outcome

`ALPHA-CAND-003` should be blocked, not completed as a valid candidate-batch build.
