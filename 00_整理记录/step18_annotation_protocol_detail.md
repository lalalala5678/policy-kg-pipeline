# Step18 标注流程细节报告

## 角色与流程
- blind_annotators: 2
- adjudication_stage: 1
- total_roles: 3
- Step-A: passA blind labeling
- Step-B: passB blind labeling
- Step-C: disagreement adjudication and gold finalization

## 样本与轮次规模
- sample_v1_count: 300
- passA_count: 300
- passB_count: 300
- adjudicated_count: 300
- target_total: 300
- actual_total: 300
- strict_high_count: 214
- hard_case_count: 157

## IAA 指标
- kappa_mechanism: 0.987997
- kappa_param_type: 1.0
- exact_match_norm_unit: 1.0
- agreement_strict_high_eligible: 1.0

## Gold 质量指标
- denominators: {'all_clause': 2022, 'sample_total': 300, 'valid_all': 300, 'valid_numeric': 278}
- mechanism_precision_on_valid_numeric: {'num': 261, 'den': 274, 'rate': 0.952555}
- normalization_precision_on_valid_numeric: {'num': 277, 'den': 278, 'rate': 0.996403}
- strict_high_precision: {'num': 213, 'den': 214, 'rate': 0.995327}

## 硬错误簇
- time_raw_not_time_window: 0
- price_value_large_raw_small_norm: 0
- candidate_score_strict_high: 0

- all_targets_passed: True
