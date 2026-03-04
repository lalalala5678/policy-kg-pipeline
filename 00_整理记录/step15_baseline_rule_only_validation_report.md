# step15_baseline_rule_only normalization + correction + validation report

## Inputs
- clause_pred_file: `00_整理记录/step4_seq_step2_clause_predictions.jsonl`
- clause_source_file: `00_整理记录/step3_clause_corpus.jsonl`
- clause_total: 2022
- strict_high_threshold: 0.6
- bind_min_score: 1.0
- binding_mode: rule_only
- disable_strict_high_guards: False

## Frozen Denominators
- all_clause: 2022
- mention_total: 1141
- valid_all: 1141
- valid_numeric: 1122

## Main Metrics (num/den/rate)
- normalization_matched_on_mentions: 1122/1141 = 0.983348
- mechanism_bound_on_valid_all: 1128/1141 = 0.988606
- mechanism_bound_on_valid_numeric: 1117/1122 = 0.995544
- strict_all_on_valid_numeric: 1117/1122 = 0.995544
- strict_high_on_valid_numeric: 933/1122 = 0.831551

## Target Check
- normalization_matched_rate >= 0.9: True
- mechanism_bound_rate_valid_numeric >= 0.85: True
- strict_high_rate_valid_numeric >= 0.65: True
- local_supported_rate_valid_numeric >= 0.85: True

## Top Bind Reasons
- keyword_plus_prior: 711
- param_type_map: 147
- keyword_hit: 145
- candidate_score: 125
- no_candidate: 13

## Artifacts
- `00_整理记录/step15_baseline_rule_only_parameter_mentions.jsonl`
- `00_整理记录/step15_baseline_rule_only_parameter_definitions.jsonl`
- `00_整理记录/step15_baseline_rule_only_triples_spo.jsonl`
- `00_整理记录/step15_baseline_rule_only_validation_report.json`
