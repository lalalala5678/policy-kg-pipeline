from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple


KEY_FIELD_TYPES = {
    "time_window",
    "time_point",
    "price_value",
    "price_delta_pct",
    "ratio_target",
    "subsidy_amount",
    "area_subsidy_amount",
}
KNOWN_MECHANISMS = {
    "tou_pricing",
    "tiered_pricing",
    "differential_penalty_pricing",
    "general_price_adjustment",
    "subsidy",
    "task_assessment",
    "technology_route",
}


def read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> Iterable[Dict]:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def metric_rate(obj: Dict, key: str) -> float:
    return float(obj.get(key, {}).get("rate", 0.0))


def is_param_type_compatible(pred: Optional[str], gold: Optional[str]) -> bool:
    p = str(pred or "")
    g = str(gold or "")
    if p == g:
        return True
    if p in {"time_window", "time_point"} and g in {"time_window", "time_point"}:
        return True
    return False


def mk_span_key(row: Dict) -> Tuple[str, Optional[int], Optional[int], str]:
    return (
        str(row.get("clause_id") or ""),
        row.get("evidence_span_start") if isinstance(row.get("evidence_span_start"), int) else None,
        row.get("evidence_span_end") if isinstance(row.get("evidence_span_end"), int) else None,
        str(row.get("raw_value") or ""),
    )


def build_candidate_index(rows: Iterable[Dict]) -> Dict[str, Dict]:
    by_id: Dict[str, Dict] = {}
    by_span: Dict[Tuple[str, Optional[int], Optional[int], str], Dict] = {}
    by_clause_raw: Dict[Tuple[str, str], list] = {}
    for r in rows:
        pmid = str(r.get("param_mention_id") or "")
        if pmid:
            by_id[pmid] = r
        span_key = mk_span_key(r)
        if span_key[0] and span_key[3]:
            by_span[span_key] = r
            by_clause_raw.setdefault((span_key[0], span_key[3]), []).append(r)
    return {"by_id": by_id, "by_span": by_span, "by_clause_raw": by_clause_raw}


def find_candidate(gold_row: Dict, idx: Dict[str, Dict]) -> Optional[Dict]:
    pmid = str(gold_row.get("param_mention_id") or "")
    if pmid and pmid in idx["by_id"]:
        return idx["by_id"][pmid]
    span_key = mk_span_key(gold_row)
    if span_key in idx["by_span"]:
        return idx["by_span"][span_key]
    clause_id = str(gold_row.get("clause_id") or "")
    raw_value = str(gold_row.get("raw_value") or "")
    bucket = idx["by_clause_raw"].get((clause_id, raw_value), [])
    if len(bucket) == 1:
        return bucket[0]
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Step7b gate with baseline-relative thresholds and gain constraints.")
    parser.add_argument("--baseline-step5-report", required=True, help="Baseline Step5 report JSON.")
    parser.add_argument("--baseline-step6-report", required=True, help="Baseline Step6 report JSON.")
    parser.add_argument("--candidate-step5-report", required=True, help="Candidate Step5 report JSON.")
    parser.add_argument("--candidate-step6-report", required=True, help="Candidate Step6 report JSON.")
    parser.add_argument("--gold-adjudicated", required=True, help="Frozen gold adjudicated JSONL (U0).")
    parser.add_argument("--candidate-mentions", required=True, help="Candidate Step5 mentions JSONL.")
    parser.add_argument("--precision-tol-pp", type=float, default=0.005, help="Relative tolerance in absolute rate.")
    parser.add_argument("--strict-high-abs-floor", type=float, default=0.99)
    parser.add_argument("--mechanism-abs-floor", type=float, default=0.95)
    parser.add_argument("--normalization-abs-floor", type=float, default=0.98)
    parser.add_argument(
        "--gain-keyfield-hit",
        type=int,
        default=1,
        help="Minimum key-field hit gain on frozen gold over U0.",
    )
    parser.add_argument(
        "--gain-strict-tp",
        type=int,
        default=1,
        help="Minimum strict-high TP gain on frozen gold over U0.",
    )
    parser.add_argument(
        "--out-json",
        default="00_整理记录/step7b_uie_gate_report.json",
        help="Output JSON path.",
    )
    args = parser.parse_args()

    b5 = read_json(Path(args.baseline_step5_report))
    b6 = read_json(Path(args.baseline_step6_report))
    c5 = read_json(Path(args.candidate_step5_report))
    c6 = read_json(Path(args.candidate_step6_report))
    gold_rows = list(read_jsonl(Path(args.gold_adjudicated)))
    cand_idx = build_candidate_index(read_jsonl(Path(args.candidate_mentions)))

    b6_quality = b6.get("quality", {})
    c6_quality = c6.get("quality", {})

    # Keep Step6 native metrics for reference; hard checks use fixed-gold metrics below.
    base_mech_step6 = metric_rate(b6_quality, "mechanism_precision_on_valid_numeric")
    base_norm_step6 = metric_rate(b6_quality, "normalization_precision_on_valid_numeric")
    base_strict_step6 = metric_rate(b6_quality, "strict_high_precision")
    cand_mech_step6 = metric_rate(c6_quality, "mechanism_precision_on_valid_numeric")
    cand_norm_step6 = metric_rate(c6_quality, "normalization_precision_on_valid_numeric")
    cand_strict_step6 = metric_rate(c6_quality, "strict_high_precision")

    key_gold_den = 0
    key_base_hit = 0
    key_cand_hit = 0
    strict_gold_den = 0
    strict_base_tp = 0
    strict_cand_tp = 0
    strict_base_pred = 0
    strict_cand_pred = 0
    mech_gold_den = 0
    mech_base_ok = 0
    mech_cand_ok = 0
    norm_gold_den = 0
    norm_base_ok = 0
    norm_cand_ok = 0
    candidate_match_count = 0

    for g in gold_rows:
        cand = find_candidate(g, cand_idx)
        if cand is not None:
            candidate_match_count += 1

        gold_mech = str(g.get("gold_mechanism_bind_after") or "")
        if gold_mech in KNOWN_MECHANISMS:
            mech_gold_den += 1
            if str(g.get("mechanism_bind_after") or "") == gold_mech:
                mech_base_ok += 1
            if cand is not None and str(cand.get("mechanism_bind_after") or "") == gold_mech:
                mech_cand_ok += 1

        gold_pt = g.get("gold_param_type")
        gold_unit = g.get("gold_norm_unit")
        if gold_pt and gold_unit:
            norm_gold_den += 1
            if is_param_type_compatible(g.get("param_type"), gold_pt) and str(g.get("norm_unit") or "") == str(gold_unit):
                norm_base_ok += 1
            if (
                cand is not None
                and is_param_type_compatible(cand.get("param_type"), gold_pt)
                and str(cand.get("norm_unit") or "") == str(gold_unit)
            ):
                norm_cand_ok += 1

        gold_type = gold_pt
        if gold_type in KEY_FIELD_TYPES:
            key_gold_den += 1
            if is_param_type_compatible(g.get("param_type"), gold_type):
                key_base_hit += 1
            if cand is not None and is_param_type_compatible(cand.get("param_type"), gold_type):
                key_cand_hit += 1

        if bool(g.get("gold_strict_high_eligible")):
            strict_gold_den += 1
            if bool(g.get("strict_high")):
                strict_base_tp += 1
            if cand is not None and bool(cand.get("strict_high")):
                strict_cand_tp += 1
        if bool(g.get("strict_high")):
            strict_base_pred += 1
        if cand is not None and bool(cand.get("strict_high")):
            strict_cand_pred += 1

    key_base_recall = float(key_base_hit) / float(key_gold_den) if key_gold_den else 0.0
    key_cand_recall = float(key_cand_hit) / float(key_gold_den) if key_gold_den else 0.0
    key_hit_delta = key_cand_hit - key_base_hit
    key_recall_delta = key_cand_recall - key_base_recall
    strict_tp_delta = strict_cand_tp - strict_base_tp
    base_mech = float(mech_base_ok) / float(mech_gold_den) if mech_gold_den else 0.0
    cand_mech = float(mech_cand_ok) / float(mech_gold_den) if mech_gold_den else 0.0
    base_norm = float(norm_base_ok) / float(norm_gold_den) if norm_gold_den else 0.0
    cand_norm = float(norm_cand_ok) / float(norm_gold_den) if norm_gold_den else 0.0
    base_strict = float(strict_base_tp) / float(strict_base_pred) if strict_base_pred else 0.0
    cand_strict = float(strict_cand_tp) / float(strict_cand_pred) if strict_cand_pred else 0.0

    mech_floor = max(base_mech - float(args.precision_tol_pp), float(args.mechanism_abs_floor))
    norm_floor = max(base_norm - float(args.precision_tol_pp), float(args.normalization_abs_floor))
    strict_floor = max(base_strict - float(args.precision_tol_pp), float(args.strict_high_abs_floor))

    hard_checks = {
        "step5_normalization_matched_rate_ge_0_95": float(c5.get("rates", {}).get("normalization_matched_rate", 0.0)) >= 0.95,
        "step5_mechanism_bound_rate_valid_numeric_eq_1_0": abs(
            float(c5.get("metrics_with_denominator", {}).get("mechanism_bound_on_valid_numeric", {}).get("rate", 0.0)) - 1.0
        )
        < 1e-12,
        "step5_local_supported_rate_valid_numeric_ge_0_85": float(
            c5.get("rates", {}).get("local_supported_rate_valid_numeric", 0.0)
        )
        >= 0.85,
        "step6_kappa_mechanism_ge_0_90": float(c6.get("iaa", {}).get("kappa_mechanism", 0.0)) >= 0.90,
        "step6_kappa_param_type_ge_0_95": float(c6.get("iaa", {}).get("kappa_param_type", 0.0)) >= 0.95,
        "step6_mechanism_precision_rel_floor": cand_mech >= mech_floor,
        "step6_normalization_precision_rel_floor": cand_norm >= norm_floor,
        "step6_strict_high_precision_rel_floor": cand_strict >= strict_floor,
        "step6_hard_error_time_raw_not_time_window_eq_0": bool(
            c6.get("target_pass", {}).get("time_raw_not_time_window_eq_0", False)
        ),
        "step6_hard_error_price_value_large_raw_small_norm_eq_0": bool(
            c6.get("target_pass", {}).get("price_value_large_raw_small_norm_eq_0", False)
        ),
        "step6_hard_error_candidate_score_strict_high_eq_0": bool(
            c6.get("target_pass", {}).get("candidate_score_strict_high_eq_0", False)
        ),
    }
    hard_pass = all(hard_checks.values())

    gain_checks = {
        "gold_keyfield_hit_delta_ge_threshold": key_hit_delta >= int(args.gain_keyfield_hit),
        "gold_strict_high_tp_delta_ge_threshold": strict_tp_delta >= int(args.gain_strict_tp),
    }
    gain_pass = any(gain_checks.values())

    out = {
        "input": {
            "baseline_step5_report": args.baseline_step5_report,
            "baseline_step6_report": args.baseline_step6_report,
            "candidate_step5_report": args.candidate_step5_report,
            "candidate_step6_report": args.candidate_step6_report,
            "gold_adjudicated": args.gold_adjudicated,
            "candidate_mentions": args.candidate_mentions,
        },
        "thresholds": {
            "precision_tol_pp": float(args.precision_tol_pp),
            "mechanism_floor": mech_floor,
            "normalization_floor": norm_floor,
            "strict_high_floor": strict_floor,
            "gain_keyfield_hit": int(args.gain_keyfield_hit),
            "gain_strict_tp": int(args.gain_strict_tp),
        },
        "baseline_snapshot": {
            "step6_mechanism_precision": base_mech_step6,
            "step6_normalization_precision": base_norm_step6,
            "step6_strict_high_precision": base_strict_step6,
            "fixed_gold_mechanism_precision": base_mech,
            "fixed_gold_normalization_precision": base_norm,
            "fixed_gold_strict_high_precision": base_strict,
            "keyfield_recall": key_base_recall,
            "strict_high_tp_on_gold": strict_base_tp,
        },
        "candidate_snapshot": {
            "step6_mechanism_precision": cand_mech_step6,
            "step6_normalization_precision": cand_norm_step6,
            "step6_strict_high_precision": cand_strict_step6,
            "fixed_gold_mechanism_precision": cand_mech,
            "fixed_gold_normalization_precision": cand_norm,
            "fixed_gold_strict_high_precision": cand_strict,
            "keyfield_recall": key_cand_recall,
            "strict_high_tp_on_gold": strict_cand_tp,
            "candidate_match_count_on_gold": candidate_match_count,
        },
        "gain": {
            "keyfield_gold_den": key_gold_den,
            "strict_high_gold_den": strict_gold_den,
            "mechanism_gold_den": mech_gold_den,
            "normalization_gold_den": norm_gold_den,
            "strict_high_pred_den_baseline": strict_base_pred,
            "strict_high_pred_den_candidate": strict_cand_pred,
            "keyfield_hit_baseline": key_base_hit,
            "keyfield_hit_candidate": key_cand_hit,
            "keyfield_hit_delta": key_hit_delta,
            "keyfield_recall_delta": key_recall_delta,
            "strict_high_tp_delta": strict_tp_delta,
        },
        "hard_checks": hard_checks,
        "hard_pass": hard_pass,
        "gain_checks": gain_checks,
        "gain_pass": gain_pass,
        "all_targets_passed": bool(hard_pass and gain_pass),
    }

    out_path = Path(args.out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"hard_pass": hard_pass, "gain_pass": gain_pass, "all_targets_passed": out["all_targets_passed"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
