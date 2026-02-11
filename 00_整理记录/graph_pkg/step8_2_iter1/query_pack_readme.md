# Step8.2 Query Pack

- query count: 12
- execution success rate: 1.0000
- core path coverage: 1.0000
- edge signal coverage on strict_high: 1.0000

## Query list
- Q01 `policy_to_mechanism_path`: 主链路：政策到机制
- Q02 `mechanism_reverse_to_policy`: 反查链路：机制回到政策
- Q03 `mechanism_to_definitions`: 机制参数定义明细
- Q04 `definition_reverse_to_policy`: 定义反查到政策
- Q05 `time_window_mechanisms_by_policy`: 按时段筛选机制
- Q06 `threshold_filter_by_param_type`: 按阈值类参数过滤
- Q07 `region_proxy_filter`: 按地区关键词（source_path代理）过滤
- Q08 `target_group_proxy_filter`: 按目标对象代理参数过滤
- Q09 `mechanism_conflict_rank`: 按机制聚合冲突强度
- Q10 `high_risk_facts`: 高风险事实定位
- Q11 `cross_clause_conflict_by_mechanism_type`: 同机制跨条款冲突定位
- Q12 `strict_all_backfill_candidates`: strict_all 对 strict_high 的候选补充

## Files
- query_pack.cql
- query_examples.json
- edge_signals.csv
- conflict_signal_report.json
- step8_2_eval_report.json
