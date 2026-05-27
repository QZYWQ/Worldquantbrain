| family_name | name | axis | value | is_baseline | ordinal | expression |
| --- | --- | --- | --- | --- | --- | --- |
| assets-cap-delta-zscore-subindustry | assets-cap-delta-zscore-subindustry__baseline | baseline | - | true | 1 | group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), subindustry) |
| assets-cap-delta-zscore-subindustry | assets-cap-delta-zscore-subindustry__sign=- | sign | "-" | false | 2 | -group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), subindustry) |
| assets-cap-delta-zscore-subindustry | assets-cap-delta-zscore-subindustry__stat_op=ts_rank | stat_op | "ts_rank" | false | 3 | group_rank(ts_rank(ts_delta(assets / cap, 2), 20), subindustry) |
| assets-cap-delta-zscore-subindustry | assets-cap-delta-zscore-subindustry__ratio_expr=ts_backfill_assets_60_cap | ratio_expr | "ts_backfill(assets, 60) / cap" | false | 4 | group_rank(ts_zscore(ts_delta(ts_backfill(assets, 60) / cap, 2), 20), subindustry) |
| assets-cap-delta-zscore-subindustry | assets-cap-delta-zscore-subindustry__ratio_expr=ts_backfill_assets_cap_60 | ratio_expr | "ts_backfill(assets / cap, 60)" | false | 5 | group_rank(ts_zscore(ts_delta(ts_backfill(assets / cap, 60), 2), 20), subindustry) |
| assets-cap-delta-zscore-subindustry | assets-cap-delta-zscore-subindustry__delta_days=5 | delta_days | 5 | false | 6 | group_rank(ts_zscore(ts_delta(assets / cap, 5), 20), subindustry) |
| assets-cap-delta-zscore-subindustry | assets-cap-delta-zscore-subindustry__delta_days=10 | delta_days | 10 | false | 7 | group_rank(ts_zscore(ts_delta(assets / cap, 10), 20), subindustry) |
| assets-cap-delta-zscore-subindustry | assets-cap-delta-zscore-subindustry__stat_window=60 | stat_window | 60 | false | 8 | group_rank(ts_zscore(ts_delta(assets / cap, 2), 60), subindustry) |
| assets-cap-delta-zscore-subindustry | assets-cap-delta-zscore-subindustry__stat_window=120 | stat_window | 120 | false | 9 | group_rank(ts_zscore(ts_delta(assets / cap, 2), 120), subindustry) |
| assets-cap-delta-zscore-subindustry | assets-cap-delta-zscore-subindustry__group=industry | group | "industry" | false | 10 | group_rank(ts_zscore(ts_delta(assets / cap, 2), 20), industry) |