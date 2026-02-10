# Step5 readiness assessment

## Decision
- ready_for_next_step_full: False
- ready_for_next_step_partial: True
- recommended_mode: partial

## Manual gold metrics (n=40)
- valid_parameter_rate: 0.775
- normalization_precision_on_matched: 0.7
- unmatched_decision_precision: 0.9
- mechanism_binding_precision_on_valid: 0.741935
- strict_usable_rate_on_valid: 0.516129
- strict_usable_rate_on_sample: 0.4

## Full-readiness thresholds
- normalization_precision_on_matched >= 0.85: False
- mechanism_binding_precision_on_valid >= 0.85: False
- strict_usable_rate_on_valid >= 0.7: False
- unmatched_decision_precision >= 0.9: True

## Rule-level normalization precision
- kwh_threshold: 0.375 (3/8)
- percent_numeric: 1.0 (10/10)
- time_window: 0.833333 (5/6)
- yuan_generic: 0.5 (3/6)

## Rule-level mechanism precision (valid parameter subset)
- kwh_threshold: 0.75 (6/8)
- no_match: 0.0 (0/1)
- percent_numeric: 0.6 (6/10)
- time_window: 1.0 (6/6)
- yuan_generic: 0.833333 (5/6)

## Artifacts
- `00_整理记录/step5_manual_gold_sample40.json`
- `00_整理记录/step5_manual_gold_review40.jsonl`
- `00_整理记录/step5_manual_gold_review40_summary.json`
- `00_整理记录/step5_readiness_assessment.json`
