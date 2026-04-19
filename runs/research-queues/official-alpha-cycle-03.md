| rank | name | recommendation | queue_score | summary | next_step |
| --- | --- | --- | --- | --- | --- |
| 1 | analyst_disagreement_afv4_inverse_industry | prioritize | 25 | best expected reward per hour in current queue | Simulate group_rank(-ts_rank(anl4_afv4_dts_spe, 60), industry) as the first inverse-disagreement baseline. |
| 2 | sentiment_buzz_stability | prioritize | 21 | high execution friction | Re-check one sentiment buzz-style field on the official Data page before opening a baseline with 5/10/20-day stability windows. |
| 3 | event_option_volume_gate | prioritize | 21 | high execution friction | Re-verify option sentiment field visibility before opening one minimal trade_when baseline. |
| 4 | analyst_disagreement_qfv4_inverse_industry | hold | 19 | balanced queue candidate | If the afv4 disagreement baseline is directionally promising but too sparse, simulate group_rank(-ts_rank(anl4_qfv4_dts_spe, 60), industry). |
