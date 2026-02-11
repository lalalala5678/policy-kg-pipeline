# step7b_step4_gpu_clause_clause_predictions normalization + correction + validation report

## Inputs
- clause_pred_file: `00_整理记录/step4_gpu_clause_clause_predictions.jsonl`
- clause_source_file: `00_整理记录/step3_clause_corpus.jsonl`
- clause_total: 2022
- strict_high_threshold: 0.6
- bind_min_score: 1.0

## Frozen Denominators
- all_clause: 2022
- mention_total: 7
- valid_all: 7
- valid_numeric: 7

## Main Metrics (num/den/rate)
- normalization_matched_on_mentions: 7/7 = 1.000000
- mechanism_bound_on_valid_all: 3/7 = 0.428571
- mechanism_bound_on_valid_numeric: 3/7 = 0.428571
- strict_all_on_valid_numeric: 3/7 = 0.428571
- strict_high_on_valid_numeric: 3/7 = 0.428571

## Target Check
- normalization_matched_rate >= 0.9: True
- mechanism_bound_rate_valid_numeric >= 0.85: False
- strict_high_rate_valid_numeric >= 0.65: False
- local_supported_rate_valid_numeric >= 0.85: False

## Top Bind Reasons
- no_candidate: 4
- keyword_plus_prior: 3

## Artifacts
- `00_整理记录/step7b_step4_gpu_clause_clause_predictions_parameter_mentions.jsonl`
- `00_整理记录/step7b_step4_gpu_clause_clause_predictions_parameter_definitions.jsonl`
- `00_整理记录/step7b_step4_gpu_clause_clause_predictions_triples_spo.jsonl`
- `00_整理记录/step7b_step4_gpu_clause_clause_predictions_validation_report.json`
