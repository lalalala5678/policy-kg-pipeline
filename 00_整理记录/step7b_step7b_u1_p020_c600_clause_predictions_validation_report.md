# step7b_step7b_u1_p020_c600_clause_predictions normalization + correction + validation report

## Inputs
- clause_pred_file: `00_整理记录/step7b_u1_p020_c600_clause_predictions.jsonl`
- clause_source_file: `00_整理记录/step3_clause_corpus.jsonl`
- clause_total: 2022
- strict_high_threshold: 0.6
- bind_min_score: 1.0

## Frozen Denominators
- all_clause: 2022
- mention_total: 0
- valid_all: 0
- valid_numeric: 0

## Main Metrics (num/den/rate)
- normalization_matched_on_mentions: 0/0 = 0.000000
- mechanism_bound_on_valid_all: 0/0 = 0.000000
- mechanism_bound_on_valid_numeric: 0/0 = 0.000000
- strict_all_on_valid_numeric: 0/0 = 0.000000
- strict_high_on_valid_numeric: 0/0 = 0.000000

## Target Check
- normalization_matched_rate >= 0.9: False
- mechanism_bound_rate_valid_numeric >= 0.85: False
- strict_high_rate_valid_numeric >= 0.65: False
- local_supported_rate_valid_numeric >= 0.85: False

## Top Bind Reasons

## Artifacts
- `00_整理记录/step7b_step7b_u1_p020_c600_clause_predictions_parameter_mentions.jsonl`
- `00_整理记录/step7b_step7b_u1_p020_c600_clause_predictions_parameter_definitions.jsonl`
- `00_整理记录/step7b_step7b_u1_p020_c600_clause_predictions_triples_spo.jsonl`
- `00_整理记录/step7b_step7b_u1_p020_c600_clause_predictions_validation_report.json`
