# step5_seq_step2_v2_rebind2 normalization + correction + validation report

## Inputs
- clause_pred_file: `00_整理记录/step4_seq_step2_clause_predictions.jsonl`
- clause_source_file: `00_整理记录/step3_clause_corpus.jsonl`
- clause_total: 2022
- strict_high_threshold: 0.8
- bind_min_score: 1.0

## Frozen Denominators
- all_clause: 2022
- mention_total: 1288
- valid_all: 1288
- valid_numeric: 1071

## Main Metrics (num/den/rate)
- normalization_matched_on_mentions: 1080/1288 = 0.838509
- mechanism_bound_on_valid_all: 1286/1288 = 0.998447
- mechanism_bound_on_valid_numeric: 1071/1071 = 1.000000
- strict_all_on_valid_numeric: 1071/1071 = 1.000000
- strict_high_on_valid_numeric: 241/1071 = 0.225023

## Target Check
- normalization_matched_rate >= 0.9: False
- mechanism_bound_rate_valid_numeric >= 0.85: True
- strict_high_rate_valid_numeric >= 0.65: False
- local_supported_rate_valid_numeric >= 0.85: True

## Top Bind Reasons
- keyword_plus_prior: 780
- keyword_hit: 241
- candidate_score: 114
- param_type_map: 85
- step4_fallback: 44
- step4_inherit: 22
- no_candidate: 2

## Artifacts
- `00_整理记录/step5_seq_step2_v2_rebind2_parameter_mentions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind2_parameter_definitions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind2_triples_spo.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind2_validation_report.json`
