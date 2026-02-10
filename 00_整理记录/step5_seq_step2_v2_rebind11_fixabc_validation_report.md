# step5_seq_step2_v2_rebind11_fixabc normalization + correction + validation report

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
- valid_numeric: 1103

## Main Metrics (num/den/rate)
- normalization_matched_on_mentions: 1103/1141 = 0.966696
- mechanism_bound_on_valid_all: 1140/1141 = 0.999124
- mechanism_bound_on_valid_numeric: 1103/1103 = 1.000000
- strict_all_on_valid_numeric: 1103/1103 = 1.000000
- strict_high_on_valid_numeric: 960/1103 = 0.870354

## Target Check
- normalization_matched_rate >= 0.9: True
- mechanism_bound_rate_valid_numeric >= 0.85: True
- strict_high_rate_valid_numeric >= 0.65: True
- local_supported_rate_valid_numeric >= 0.85: True

## Top Bind Reasons
- keyword_plus_prior: 735
- keyword_hit: 178
- param_type_map: 101
- candidate_score: 97
- step4_inherit: 22
- step4_fallback: 7
- no_candidate: 1

## Artifacts
- `00_整理记录/step5_seq_step2_v2_rebind11_fixabc_parameter_mentions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind11_fixabc_parameter_definitions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind11_fixabc_triples_spo.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind11_fixabc_validation_report.json`
