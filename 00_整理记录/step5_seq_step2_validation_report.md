# step5_seq_step2 normalization + validation report

## Inputs
- clause_pred_file: `00_整理记录/step4_seq_step2_clause_predictions.jsonl`
- clause_source_file: `00_整理记录/step3_clause_corpus.jsonl`
- clause_total: 2022

## Counts
- mention_total: 1357
- definition_total: 296
- triple_total: 3291
- span_valid_count: 1357
- normalization_matched_count: 1180
- canonical_key_count: 1180
- mechanism_bound_count: 1334
- ready_with_mechanism_count: 1167
- unit_conflict_group_count: 7

## Rates
- span_valid_rate: 1.000000
- normalization_matched_rate: 0.869565
- canonical_key_rate: 0.869565
- mechanism_bound_rate: 0.983051
- ready_with_mechanism_rate: 0.859985

## Top Rules
- percent_numeric: 458
- yuan_generic: 154
- kwh_threshold: 151
- time_window: 139
- no_match: 133
- yuan_per_kwh: 74
- ten_thousand_yuan_generic: 60
- date_like_filtered: 44
- yuan_per_degree_to_yuan_per_kwh: 37
- ratio_sequence: 36
- yuan_per_sqm: 34
- ten_thousand_yuan_per_village: 27
- tonnage_value: 6
- capacity_value: 4

## Artifacts
- `00_整理记录/step5_seq_step2_parameter_mentions.jsonl`
- `00_整理记录/step5_seq_step2_parameter_definitions.jsonl`
- `00_整理记录/step5_seq_step2_triples_spo.jsonl`
- `00_整理记录/step5_seq_step2_validation_report.json`
