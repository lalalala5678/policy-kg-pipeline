# step15_baseline_no_rebind normalization + correction + validation report

## Inputs
- clause_pred_file: `00_整理记录/step4_seq_step2_clause_predictions.jsonl`
- clause_source_file: `00_整理记录/step3_clause_corpus.jsonl`
- clause_total: 2022
- strict_high_threshold: 0.6
- bind_min_score: 99.0
- binding_mode: full
- disable_strict_high_guards: False

## Frozen Denominators
- all_clause: 2022
- mention_total: 1141
- valid_all: 1141
- valid_numeric: 1122

## Main Metrics (num/den/rate)
- normalization_matched_on_mentions: 1122/1141 = 0.983348
- mechanism_bound_on_valid_all: 1052/1141 = 0.921998
- mechanism_bound_on_valid_numeric: 1034/1122 = 0.921569
- strict_all_on_valid_numeric: 1034/1122 = 0.921569
- strict_high_on_valid_numeric: 0/1122 = 0.000000

## Target Check
- normalization_matched_rate >= 0.9: True
- mechanism_bound_rate_valid_numeric >= 0.85: True
- strict_high_rate_valid_numeric >= 0.65: False
- local_supported_rate_valid_numeric >= 0.85: False

## Top Bind Reasons
- step4_fallback: 1052
- unknown_low_score: 88
- no_candidate: 1

## Artifacts
- `00_整理记录/step15_baseline_no_rebind_parameter_mentions.jsonl`
- `00_整理记录/step15_baseline_no_rebind_parameter_definitions.jsonl`
- `00_整理记录/step15_baseline_no_rebind_triples_spo.jsonl`
- `00_整理记录/step15_baseline_no_rebind_validation_report.json`
