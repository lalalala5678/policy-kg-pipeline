# Step17 性能与延迟评测报告

## Step9 导入耗时与峰值内存
- elapsed_sec: 215.91
- max_rss_kb: 27776
- return_code: 0

## 查询延迟总体
- query_count: 12
- repeat: 30
- successful_runs: 360/360
- latency_ms_p50: 5.354
- latency_ms_p95: 130.423
- latency_ms_mean: 17.665

## 每个模板延迟（P50/P95）
| query_id | title | success_runs | latency_ms_p50 | latency_ms_p95 |
|---|---|---:|---:|---:|
| Q01 | policy_to_mechanism_path | 30 | 6.806 | 10.966 |
| Q02 | mechanism_reverse_to_policy | 30 | 4.907 | 7.811 |
| Q03 | mechanism_to_definitions | 30 | 4.97 | 7.877 |
| Q04 | definition_reverse_to_policy | 30 | 5.677 | 8.51 |
| Q05 | time_window_mechanisms_by_policy | 30 | 4.768 | 9.01 |
| Q06 | threshold_filter_by_param_type | 30 | 5.322 | 7.406 |
| Q07 | region_proxy_filter | 30 | 5.018 | 7.817 |
| Q08 | target_group_proxy_filter | 30 | 4.555 | 6.897 |
| Q09 | mechanism_conflict_rank | 30 | 12.582 | 16.972 |
| Q10 | high_risk_facts | 30 | 5.224 | 9.315 |
| Q11 | cross_clause_conflict_by_mechanism_type | 30 | 4.431 | 6.313 |
| Q12 | strict_all_backfill_candidates | 30 | 130.776 | 218.261 |
