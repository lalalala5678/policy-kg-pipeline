# Step14 错误画像与风险剖面报告

## 硬错误桶
- time_raw_not_time_window: 0 (pass=True)
- price_value_large_raw_small_norm: 0 (pass=True)
- candidate_score_strict_high: 0 (pass=True)

## 冲突分布（Step8.2）
- conflict_total: 3929
- dedup_aggregation: 3875 (0.986256)
- semantic_collision: 54 (0.013744)

## 守卫与过滤动作（Step5）
- raw_value_filtered_non_value_count: 69
- raw_value_filtered_by_rule_count: 147
- unit_pairing_dropped_count: 98
- strict_high_compat_block_count: 11
- strict_high_weak_constraint_block_count: 5
- clause_negative_count: 56
- low_confidence_cap_count: 23

## 门禁余量（Margin）
- normalization_matched_rate_margin: 0.030719
- strict_high_rate_valid_numeric_margin: 0.00076
- local_supported_rate_valid_numeric_margin: 0.049017
- kappa_mechanism_margin: 0.091969
- kappa_param_type_margin: 0.05
- mechanism_precision_margin: 0.007597
- normalization_precision_margin: 0.005
- strict_high_precision_margin: 0.003475

## 最弱年份（按 strict_high_rate_valid_all）
| year | valid_all | strict_high_rate_valid_all | normalization_matched_rate_on_valid_all |
|---|---:|---:|---:|
| 2017 | 36 | 0.500000 | 0.972222 |
| 2019 | 51 | 0.666667 | 0.803922 |
| 2021 | 85 | 0.823529 | 0.941176 |

## 风险结论
- Hard-error buckets are all zero in current gate report; current risk is dominated by soft conflicts and threshold sensitivity.
- strict_high_rate_valid_numeric is close to threshold (small positive margin), indicating potential regression risk under domain shift.
- Cross-year strict_high variability is significantly larger than mechanism binding variability, suggesting expression-style sensitivity.
