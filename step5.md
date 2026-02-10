# Step5: Rule Normalization, Rebinding, and Validation

Updated: 2026-02-11

## Goal
- Keep Step4 fixed and do second-stage correction in Step5.
- Improve graph-ingestion usability with schema-frozen metrics.
- Output deterministic mention/definition/triple artifacts with strict gates.

## Input
- `00_整理记录/step4_seq_step2_clause_predictions.jsonl`
- `00_整理记录/step3_clause_corpus.jsonl`

## Core upgrades
1. Frozen denominator metrics
- `all_clause`: clause-level denominator (aligned to Step4 total 2022).
- `valid_all`: mention denominator (`span_valid && normalization_attempted`).
- `valid_numeric`: mention denominator (`span_valid && normalization_matched && is_numeric_like`).
- All main metrics are printed as `num/den/rate`.

2. Two-stage mechanism rebinding (Step5 only)
- Clause-level candidates: `score = pos*w1 - neg*w2 + param_prior*w3 + step4_inherit*w4`.
- Mention-level binding: select candidate with param-type-aware adjustment.
- Negative-domain guard: pollution-only context blocks pricing-mechanism binding.
- Output fields: `mechanism_bind_before`, `mechanism_bind_after`, `mechanism_bind_reason`, `bind_confidence`.

3. Strict dual-track gates
- `strict_all`: `span_valid && normalization_matched && bind_after in KNOWN_MECHANISMS`.
- `strict_high`: `strict_all && bind_confidence>=threshold && high_conf_reason && no_negative_conflict`.

4. Normalization improvements
- Added/strengthened: `kwh_threshold_range`, `duration_hour`, `duration_month_context`, `household_count`, `yuan_per_ton`, `yuan_per_watt`, watt-to-kw conversion.
- Context leakage control: prioritize raw mention text to avoid cross-value contamination.
- Early mention filter: remove obvious non-parameter items and time-metadata noise before normalization.

## Main script and tests
- Script: `00_整理记录/scripts/run_step5_normalize_validate.py`
- Normalizer utils: `00_整理记录/scripts/policy_extraction_utils.py`
- Tests:
- `00_整理记录/tests/test_step5_normalizer.py`
- `00_整理记录/tests/test_step5_binding_rules.py`

## Output (final iteration)
- `00_整理记录/step5_seq_step2_v2_rebind4_parameter_mentions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind4_parameter_definitions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind4_triples_spo.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind4_validation_report.json`
- `00_整理记录/step5_seq_step2_v2_rebind4_validation_report.md`

## Key results (v2_rebind4)
- mention_total: 1141
- definition_total: 353
- triple_total: 3283
- span_valid_rate: 1.000000
- normalization_matched_rate: 0.988606
- mechanism_bound_rate_valid_numeric: 1.000000
- strict_high_rate_valid_numeric: 0.845745
- local_supported_rate_valid_numeric: 0.882092
- pricing_negative_conflict_rate_valid_numeric: 0.000000
- all_targets_passed: true

## Target thresholds and status
- normalization_matched_rate >= 0.90: pass
- mechanism_bound_rate_valid_numeric >= 0.85: pass
- strict_high_rate_valid_numeric >= 0.65: pass
- local_supported_rate_valid_numeric >= 0.85: pass
