# 附录表格摘要

## 表3 门禁阈值与实测（摘录）
| gate_item | threshold | observed | pass |
|---|---|---|---|
| normalization_matched_rate | >=0.95 | 0.980719 | True |
| mechanism_bound_rate_valid_numeric | =1.0 | 1.0 | True |
| strict_high_rate_valid_numeric | >=0.85 | 0.85076 | True |
| local_supported_rate_valid_numeric | >=0.85 | 0.899017 | True |
| kappa_mechanism | >=0.90 | 0.991969 | True |
| kappa_param_type | >=0.95 | 1.0 | True |
| mechanism_precision_on_valid_numeric | >=0.95 | 0.957597 | True |
| normalization_precision_on_valid_numeric | >=0.995 | 1.0 | True |

## 表4 消融结果（摘录）
| ablation_type | metric | full_method | ablation | delta |
|---|---|---|---|---|
| Ablation-A_no_rule_postprocess | step4_total_score | 76.332 | 39.482 | 36.85 |
| Ablation-A_no_rule_postprocess | step4_strict_triplet_ready_rate | 0.251731 | 0.0 | 0.251731 |
| Ablation-A_no_rule_postprocess | step4_param_bind_rate | 0.88075 | 0.0 | 0.88075 |
| Ablation-B_bind_min_score_99 | step5_mechanism_bound_rate_valid_all | 0.999124 | 0.921998 | 0.077126 |
| Ablation-B_bind_min_score_99 | step5_strict_high_rate_valid_all | 0.802805 | 0.0 | 0.802805 |
| Ablation-B_bind_min_score_99 | step5_local_supported_rate_valid_all | 0.846626 | 0.489921 | 0.356705 |
| Ablation-B_bind_min_score_99 | step5_all_targets_passed | True | False |  |

## 表6 成本画像（摘录）
| benchmark_id | elapsed_sec | return_code |
|---|---|---|
| step5_normalize_validate_costprobe | 0.469 | 0 |
| step6_gold_iaa_costprobe | 0.189 | 0 |
| step8_2_query_pack_costprobe | 0.343 | 0 |
| step9_query_eval | 0.342 | 0 |
| step9_gate_eval | 0.042 | 0 |
