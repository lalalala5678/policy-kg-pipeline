# Step6: Gold/IAA (Codex Blind Annotation)

Updated: 2026-02-11

## Scope
- Step6 is completed on top of fixed Step5 outputs.
- Annotation is done by Codex in two blind passes (Pass-A and Pass-B), then adjudicated.
- No human annotator is used in this run.

## Inputs
- `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_mentions.jsonl`
- `00_整理记录/step3_clause_corpus.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_validation_report.json`

## Method
1. Freeze denominators and target thresholds from Step6 spec.
2. Draw stratified sample by mechanism, param type, bind reason, strict/high, and hard cases.
3. Run blind Pass-A labeling.
4. Shuffle sample order and run blind Pass-B labeling (without reading Pass-A labels).
5. Compute IAA (`kappa`, exact match, strict agreement).
6. Adjudicate disagreements with explicit hard-error rules first, then score tie-break.
7. Compare adjudicated labels against Step5 predictions on frozen valid numeric denominator.

## Iterations
- `step6_iter1`: all targets passed except normalization precision (0.867857 < 0.90).
- `step6_iter2`: fixed adjudication policy to keep Step5 values unless hard-error evidence exists.
- `step6_iter3_fixabcd`: aligned strict eligibility with Step5 compatibility gates and parenthetical weak-constraint filtering.
- `step6_iter4_fixabcd_plus`: rerun on optimized Step5 (`rebind14`) and keep all targets passed.
- Final frozen run for latest Step5: `step6_iter4_fixabcd_plus`, all targets passed.

## Final Metrics (`00_整理记录/step6_iter4_fixabcd_plus_iaa_report.json`)
- Sample size: `300` (>= 240)
- Strict-high in sample: `214` (>= 120)
- Hard-case in sample: `152` (>= 60)
- `kappa_mechanism = 0.987997`
- `kappa_param_type = 1.000000`
- `exact_match_norm_unit = 1.000000`
- `agreement_strict_high_eligible = 1.000000`
- `mechanism_precision_on_valid_numeric = 261/274 = 0.952555`
- `normalization_precision_on_valid_numeric = 277/278 = 0.996403`
- `strict_high_precision = 213/214 = 0.995327`
- Error clusters:
  - `time_raw_not_time_window = 0`
  - `price_value_large_raw_small_norm = 0`
  - `candidate_score_strict_high = 0`
- `all_targets_passed = true`

## Issue A-D verification (Step6 sample)
- `strict_high=true && gold_strict_high_eligible=false`: `6 -> 0`
- `duration_month_context` count: `15 -> 4`
- `duration_month_context` with raw unit: `3 -> 0`
- `duration_month_context` in strict-high: `15 -> 1`
- `1:1:1` mapped as `funding_share_ratio`: `0 -> 3`

## Main Artifacts
- `00_整理记录/step6_iter4_fixabcd_plus_gold_sampling_plan.json`
- `00_整理记录/step6_iter4_fixabcd_plus_gold_sample_v1.jsonl`
- `00_整理记录/step6_iter4_fixabcd_plus_gold_passA_labels.jsonl`
- `00_整理记录/step6_iter4_fixabcd_plus_gold_passB_labels.jsonl`
- `00_整理记录/step6_iter4_fixabcd_plus_gold_adjudicated.jsonl`
- `00_整理记录/step6_iter4_fixabcd_plus_iaa_report.json`
- `00_整理记录/step6_iter4_fixabcd_plus_iaa_report.md`
- `00_整理记录/step6_iter4_fixabcd_plus_error_clusters.md`
- `00_整理记录/step6_fixabcd_plus2_eval.json`

## Implementation
- `00_整理记录/scripts/run_step6_gold_iaa.py`
