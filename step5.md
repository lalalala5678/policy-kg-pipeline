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
- Added A/B/C-focused guards:
- Time point repair: `7:00/22:00` no longer falls into `ratio_target`; now typed as `time_window/time_point`.
- Threshold-vs-price repair: avoid cross-value leakage from clause-level price text into threshold mentions.
- Low-confidence cap: candidate/fallback inherit reasons are confidence-capped and excluded from strict-high.
- Unit pairing guard: when `raw_unit` is likely mis-paired in dense clauses, normalization falls back to raw-only mention.

## Main script and tests
- Script: `00_整理记录/scripts/run_step5_normalize_validate.py`
- Normalizer utils: `00_整理记录/scripts/policy_extraction_utils.py`
- Tests:
- `00_整理记录/tests/test_step5_normalizer.py`
- `00_整理记录/tests/test_step5_binding_rules.py`

## Output (final iteration)
- `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_parameter_mentions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_parameter_definitions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_triples_spo.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_validation_report.json`
- `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_validation_report.md`
- `00_整理记录/step5_fixabcd_issueAtoD_eval.json`

## Key results (v2_rebind12_fixabcd)
- mention_total: 1141
- definition_total: 341
- triple_total: 3176
- span_valid_rate: 1.000000
- normalization_matched_rate: 0.945662
- mechanism_bound_rate_valid_numeric: 1.000000
- strict_high_rate_valid_numeric: 0.856348
- local_supported_rate_valid_numeric: 0.889713
- pricing_negative_conflict_rate_valid_numeric: 0.000000
- all_targets_passed: true

## A/B/C/D issue delta (rebind11_fixabc -> rebind12_fixabcd)
- `duration_month_context` count: `29 -> 7`
- `duration_month_context` with raw unit: `13 -> 0`
- duration entries in `strict_high`: `29 -> 1`
- weak parenthetical duration in `strict_high`: `9 -> 0`
- `1:1:1`-style ratio mapped as `funding_share_ratio`: `0 -> 7`
- `1:1:1`-style ratio still mapped as `ratio_target`: `11 -> 4`
- Focus case `pm_0642...` (`6000`): `duration_threshold_month -> no_match`
- Focus case `pm_0e905...` (`0.0634`): `duration_threshold_month -> no_match`
- Focus case `pm_296552...` (`3071`): `subsidy_amount -> no_match`
- Focus case `pm_106b35...` (`1:1:1`): `ratio_target -> funding_share_ratio`
- Focus case `pm_00f41...` (`不少于两`): `strict_high true -> false`

## Target thresholds and status
- normalization_matched_rate >= 0.90: pass
- mechanism_bound_rate_valid_numeric >= 0.85: pass
- strict_high_rate_valid_numeric >= 0.65: pass
- local_supported_rate_valid_numeric >= 0.85: pass

## Handoff to Step6 (Gold/IAA)
- Step6 does not modify Step5 outputs in-place; it builds a frozen Gold/IAA benchmark on top of `v2_rebind11_fixabc`.
- Frozen input and denominator definitions are documented in `00_整理记录/step6_性能指标目标.md`.
- Step7 fine-tuning can start only after Step6 IAA/Gold thresholds are met.
- Current status: Step6 has been completed and passed all thresholds (`00_整理记录/step6_iaa_report.json`).
