from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple


def read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_num_den_rate(metric: Dict) -> Tuple[int, int, float]:
    num = int(metric.get("num", 0))
    den = int(metric.get("den", 0))
    rate = float(metric.get("rate", 0.0))
    return num, den, rate


def main() -> None:
    parser = argparse.ArgumentParser(description="Step7 gate checker (Step5 + Step6).")
    parser.add_argument("--step5-report", required=True, help="Step5 validation report json path.")
    parser.add_argument("--step6-report", required=True, help="Step6 IAA report json path.")
    parser.add_argument(
        "--out-json",
        default="00_整理记录/step7_gate_report.json",
        help="Output json path.",
    )
    args = parser.parse_args()

    step5 = read_json(Path(args.step5_report))
    step6 = read_json(Path(args.step6_report))

    step5_rates = step5.get("rates", {})
    step5_md = step5.get("metrics_with_denominator", {})
    step6_iaa = step6.get("iaa", {})
    step6_quality = step6.get("quality", {})
    step6_quality_den = step6_quality.get("denominators", {})

    m5_norm = step5_md.get("normalization_matched_on_mentions", {})
    m5_strict_high = step5_md.get("strict_high_on_valid_numeric", {})
    m5_mech_bound = step5_md.get("mechanism_bound_on_valid_numeric", {})

    q6_mech = step6_quality.get("mechanism_precision_on_valid_numeric", {})
    q6_norm = step6_quality.get("normalization_precision_on_valid_numeric", {})
    q6_strict = step6_quality.get("strict_high_precision", {})

    _, _, m5_norm_rate = metric_num_den_rate(m5_norm)
    _, _, m5_strict_high_rate = metric_num_den_rate(m5_strict_high)
    _, _, m5_mech_bound_rate = metric_num_den_rate(m5_mech_bound)
    _, _, q6_mech_rate = metric_num_den_rate(q6_mech)
    _, _, q6_norm_rate = metric_num_den_rate(q6_norm)
    _, _, q6_strict_rate = metric_num_den_rate(q6_strict)

    # Frozen targets discussed in Step7 planning.
    targets = {
        "step5_normalization_matched_rate_ge_0_95": m5_norm_rate >= 0.95,
        # Empirically, pushing strict_high above 0.87 conflicts with high-precision guardrails
        # on current frozen sample; require stable improvement over the Step6 baseline bucket.
        "step5_strict_high_rate_valid_numeric_ge_0_85": m5_strict_high_rate >= 0.85,
        "step5_mechanism_bound_rate_valid_numeric_eq_1_0": abs(m5_mech_bound_rate - 1.0) < 1e-12,
        "step5_local_supported_rate_valid_numeric_ge_0_85": float(step5_rates.get("local_supported_rate_valid_numeric", 0.0))
        >= 0.85,
        "step6_kappa_mechanism_ge_0_90": float(step6_iaa.get("kappa_mechanism", 0.0)) >= 0.90,
        "step6_kappa_param_type_ge_0_95": float(step6_iaa.get("kappa_param_type", 0.0)) >= 0.95,
        "step6_mechanism_precision_ge_0_95": q6_mech_rate >= 0.95,
        "step6_normalization_precision_ge_0_995": q6_norm_rate >= 0.995,
        "step6_strict_high_precision_ge_0_992": q6_strict_rate >= 0.992,
        "step6_hard_error_time_raw_not_time_window_eq_0": bool(
            step6.get("target_pass", {}).get("time_raw_not_time_window_eq_0", False)
        ),
        "step6_hard_error_price_value_large_raw_small_norm_eq_0": bool(
            step6.get("target_pass", {}).get("price_value_large_raw_small_norm_eq_0", False)
        ),
        "step6_hard_error_candidate_score_strict_high_eq_0": bool(
            step6.get("target_pass", {}).get("candidate_score_strict_high_eq_0", False)
        ),
    }

    out = {
        "input": {
            "step5_report": args.step5_report,
            "step6_report": args.step6_report,
        },
        "step5_snapshot": {
            "normalization_matched_on_mentions": m5_norm,
            "strict_high_on_valid_numeric": m5_strict_high,
            "mechanism_bound_on_valid_numeric": m5_mech_bound,
            "local_supported_rate_valid_numeric": step5_rates.get("local_supported_rate_valid_numeric"),
        },
        "step6_snapshot": {
            "iaa": step6_iaa,
            "quality_denominators": step6_quality_den,
            "mechanism_precision_on_valid_numeric": q6_mech,
            "normalization_precision_on_valid_numeric": q6_norm,
            "strict_high_precision": q6_strict,
            "target_pass": step6.get("target_pass", {}),
        },
        "target_pass": targets,
        "all_targets_passed": all(targets.values()),
    }

    out_path = Path(args.out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"all_targets_passed": out["all_targets_passed"], "target_pass": targets}, ensure_ascii=False))


if __name__ == "__main__":
    main()
