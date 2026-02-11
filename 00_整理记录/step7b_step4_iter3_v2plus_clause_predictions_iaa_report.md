# Step6 Gold/IAA Report

## Sampling
- total: 300
- strict_high_in_sample: 233
- hard_case_in_sample: 157

## IAA
- kappa_mechanism: 0.992021
- kappa_param_type: 1.000000
- exact_match_norm_unit: 1.000000
- agreement_strict_high_eligible: 1.000000

## Quality vs Step5
- mechanism_precision_on_valid_numeric: 271/285 = 0.950877
- normalization_precision_on_valid_numeric: 290/290 = 1.000000
- strict_high_precision: 232/233 = 0.995708

## Error Clusters
- time_raw_not_time_window: 0
- price_value_large_raw_small_norm: 0
- candidate_score_strict_high: 0

## Targets
- kappa_mechanism_ge_0_80: True
- kappa_param_type_ge_0_80: True
- exact_match_norm_unit_ge_0_90: True
- agreement_strict_high_eligible_ge_0_90: True
- mechanism_precision_ge_0_90: True
- normalization_precision_ge_0_90: True
- strict_high_precision_ge_0_92: True
- time_raw_not_time_window_eq_0: True
- price_value_large_raw_small_norm_eq_0: True
- candidate_score_strict_high_eq_0: True
- sample_size_ge_240: True
- sample_strict_ge_120: True
- sample_hard_ge_60: True

- all_targets_passed: True
