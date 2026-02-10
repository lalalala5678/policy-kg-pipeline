# Step6 Innovation Notes (Gold/IAA by Codex)

Updated: 2026-02-11

## 1) Blind-pass protocol without human annotators
- Built a strict two-pass blind annotation protocol (`Pass-A`, `Pass-B`) in one reproducible pipeline.
- Pass-B is run on shuffled sample order and does not read Pass-A outputs.
- This provides measurable agreement under the same model-driven workflow.

## 2) Frozen denominator evaluation
- Kept denominator discipline from Step5/Step6 spec:
  - `all_clause`
  - `valid_all`
  - `valid_numeric`
- All key metrics are output as `num/den/rate` for reproducibility.

## 3) Hard-error-first adjudication
- Adjudication prioritizes explicit hard errors before tie-break:
  - time token mis-typing (`time_window`/`time_point`)
  - threshold-vs-price leakage (`raw>=100` but `yuan_per_kwh` tiny value)
  - negative domain pricing conflicts
- Outside hard-error cases, Gold keeps Step5 values to avoid over-correction drift.

## 4) Stratified sample design with hard-case guarantees
- Sample is stratified by mechanism, param type, bind reason, strict status, and hard-case tags.
- Hard-case coverage and strict coverage are guaranteed by construction.

## 5) Achieved quality gates
- `kappa_mechanism = 0.991943`
- `kappa_param_type = 1.000000`
- `exact_match_norm_unit = 1.000000`
- `agreement_strict_high_eligible = 1.000000`
- `mechanism_precision_on_valid_numeric = 0.953237`
- `normalization_precision_on_valid_numeric = 0.992857`
- `strict_high_precision = 0.973799`
- All Step6 targets passed in final run (`step6_*` artifacts).
