# step5_seq_step2_v2_rebind15_fixabcd_plus3 normalization + correction + validation report

## Inputs
- clause_pred_file: `00_整理记录/step4_seq_step2_clause_predictions.jsonl`
- clause_source_file: `00_整理记录/step3_clause_corpus.jsonl`
- clause_total: 2022
- strict_high_threshold: 0.6
- bind_min_score: 1.0

## Frozen Denominators
- all_clause: 2022
- mention_total: 1141
- valid_all: 1141
- valid_numeric: 1079

## Main Metrics (num/den/rate)
- normalization_matched_on_mentions: 1079/1141 = 0.945662
- mechanism_bound_on_valid_all: 1140/1141 = 0.999124
- mechanism_bound_on_valid_numeric: 1079/1079 = 1.000000
- strict_all_on_valid_numeric: 1079/1079 = 1.000000
- strict_high_on_valid_numeric: 890/1079 = 0.824838

## Target Check
- normalization_matched_rate >= 0.9: True
- mechanism_bound_rate_valid_numeric >= 0.85: True
- strict_high_rate_valid_numeric >= 0.65: True
- local_supported_rate_valid_numeric >= 0.85: True

## Top Bind Reasons
- keyword_plus_prior: 690
- keyword_hit: 223
- param_type_map: 98
- candidate_score: 95
- step4_inherit: 22
- step4_fallback: 12
- no_candidate: 1

## Artifacts
- `00_整理记录/step5_seq_step2_v2_rebind15_fixabcd_plus3_parameter_mentions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind15_fixabcd_plus3_parameter_definitions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind15_fixabcd_plus3_triples_spo.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind15_fixabcd_plus3_validation_report.json`
