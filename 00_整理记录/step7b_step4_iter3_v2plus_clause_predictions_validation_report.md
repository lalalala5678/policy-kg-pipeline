# step7b_step4_iter3_v2plus_clause_predictions normalization + correction + validation report

## Inputs
- clause_pred_file: `00_整理记录/step4_iter3_v2plus_clause_predictions.jsonl`
- clause_source_file: `00_整理记录/step3_clause_corpus.jsonl`
- clause_total: 2022
- strict_high_threshold: 0.6
- bind_min_score: 1.0

## Frozen Denominators
- all_clause: 2022
- mention_total: 1082
- valid_all: 1082
- valid_numeric: 1071

## Main Metrics (num/den/rate)
- normalization_matched_on_mentions: 1071/1082 = 0.989834
- mechanism_bound_on_valid_all: 1077/1082 = 0.995379
- mechanism_bound_on_valid_numeric: 1067/1071 = 0.996265
- strict_all_on_valid_numeric: 1067/1071 = 0.996265
- strict_high_on_valid_numeric: 917/1071 = 0.856209

## Target Check
- normalization_matched_rate >= 0.9: True
- mechanism_bound_rate_valid_numeric >= 0.85: True
- strict_high_rate_valid_numeric >= 0.65: True
- local_supported_rate_valid_numeric >= 0.85: True

## Top Bind Reasons
- keyword_plus_prior: 676
- keyword_hit: 158
- param_type_map: 139
- candidate_score: 102
- no_candidate: 5
- step4_inherit: 1
- step4_fallback: 1

## Artifacts
- `00_整理记录/step7b_step4_iter3_v2plus_clause_predictions_parameter_mentions.jsonl`
- `00_整理记录/step7b_step4_iter3_v2plus_clause_predictions_parameter_definitions.jsonl`
- `00_整理记录/step7b_step4_iter3_v2plus_clause_predictions_triples_spo.jsonl`
- `00_整理记录/step7b_step4_iter3_v2plus_clause_predictions_validation_report.json`
