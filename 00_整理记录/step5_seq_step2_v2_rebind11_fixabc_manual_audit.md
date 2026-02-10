# Step5 rebind11 Manual Audit

Date: 2026-02-11
Target artifact:
- `00_整理记录/step5_seq_step2_v2_rebind11_fixabc_parameter_mentions.jsonl`

## Audit protocol
- Manual read on escaped clause text (`ensure_ascii=True`) to avoid terminal codepage rendering errors.
- Focus set A: all repaired time-point cases (`normalization_rule=time_point`).
- Focus set B: 10 sampled cases changed from `price_value` -> `consumption_threshold_kwh`.
- Focus set C: 30 random `strict_high=true` mentions.
- Focus set D: 12 random `candidate_score` mentions (expected low-confidence bucket).

## Manual findings
- Focus A (10/10): all correct
  - Time points (`7:00`, `22:00` etc.) are now typed as `time_window/time_point` and bound to `tou_pricing` in clear TOU clauses.
- Focus B (10/10): all correct
  - Threshold values (e.g., `170/260/4440 千瓦时`) are no longer normalized to price values.
- Focus C (30 random strict_high): no definite wrong case found (30/30)
  - All sampled items had text support for mechanism + value type.
- Focus D (12 random candidate_score): all stayed `strict_high=false`; no spillover into strict-high.

## Residual issues (observed)
- One known low-confidence binding anomaly remains:
  - `param_mention_id=pm_d5ec0d452f5002f0fe49`
  - Vehicle energy-consumption context; current mechanism is low-confidence and `strict_high=false`.
  - Not in strict-high ingest set, but should be improved in next iteration.
- `normalization_unmatched` increased vs baseline due stricter anti-leakage behavior.
  - Trade-off accepted to remove severe threshold->price contamination.

## Practical conclusion
- For strict-high ingest, current quality is materially cleaner than baseline on the target A/B/C issues.
- Remaining errors are concentrated in low-confidence buckets and non-strict-high entries.
