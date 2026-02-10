import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "00_\u6574\u7406\u8bb0\u5f55" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_step5_normalize_validate import (  # noqa: E402
    apply_post_normalization_guards,
    build_norm_input,
    build_clause_candidates,
    canonicalize_unit_alias,
    choose_binding_for_mention,
)


class TestStep5BindingRules(unittest.TestCase):
    def test_negative_domain_rejects_pricing(self):
        text = "\u91cd\u70b9\u533a\u57dfPM2.5\u5e74\u5747\u6d53\u5ea6\u4e0b\u964d10%\u4ee5\u4e0a\uff0c\u7a7a\u6c14\u8d28\u91cf\u4f18\u826f\u5929\u6570\u6bd4\u7387\u8fbe\u523080%\u4ee5\u4e0a\u3002"
        candidates, neg_hits = build_clause_candidates(
            clause_text=text,
            step4_mechanism="tou_pricing",
            step4_source="fallback_clause_type_lowconf",
            clause_param_types=["ratio_target"],
        )
        self.assertGreater(neg_hits, 0)
        bind_after, bind_reason, _, _, _ = choose_binding_for_mention(
            candidates=candidates,
            mention_param_type="ratio_target",
            step4_mechanism="tou_pricing",
            bind_min_score=1.0,
        )
        self.assertNotEqual(bind_after, "tou_pricing")
        self.assertIn(
            bind_reason,
            {"drop_by_negative", "unknown_low_score", "keyword_hit", "keyword_plus_prior", "param_type_map", "candidate_score"},
        )

    def test_tou_clause_prefers_tou(self):
        text = "\u9ad8\u5cf0\u7535\u4ef7\u5728\u5e73\u6bb5\u7535\u4ef7\u57fa\u7840\u4e0a\u4e0a\u6d6e50%\uff0c\u4f4e\u8c37\u7535\u4ef7\u4e0b\u6d6e50%\uff0c\u6267\u884c\u65f6\u6bb5\u4e3a11:00-13:00\u3002"
        candidates, _ = build_clause_candidates(
            clause_text=text,
            step4_mechanism="tou_pricing",
            step4_source="rule_pattern",
            clause_param_types=["price_delta_pct", "time_window"],
        )
        bind_after, _, conf, _, _ = choose_binding_for_mention(
            candidates=candidates,
            mention_param_type="price_delta_pct",
            step4_mechanism="tou_pricing",
            bind_min_score=1.0,
        )
        self.assertEqual(bind_after, "tou_pricing")
        self.assertGreater(conf, 0.5)

    def test_guard_retypes_price_conflict_to_kwh(self):
        norm = {
            "matched": True,
            "rule": "yuan_per_kwh",
            "param_type": "price_value",
            "norm_value": 0.05,
            "norm_unit": "yuan_per_kwh",
            "norm_start": None,
            "norm_end": None,
            "range_start": None,
            "range_end": None,
            "op": None,
            "scope_unit": None,
        }
        adjusted, action = apply_post_normalization_guards(
            raw_value="170",
            raw_unit="\u5343\u74e6\u65f6",
            clause_text="\u7b2c\u4e00\u6863170\u5343\u74e6\u65f6\u4ee5\u4e0a\u90e8\u5206\u52a0\u4ef70.05\u5143/\u5343\u74e6\u65f6\u3002",
            raw_start=0,
            raw_end=3,
            norm=norm,
        )
        self.assertTrue(adjusted["matched"])
        self.assertEqual(adjusted["param_type"], "consumption_threshold_kwh")
        self.assertEqual(adjusted["norm_unit"], "kwh")
        self.assertEqual(adjusted["norm_value"], 170.0)
        self.assertIn(action, {"price_conflict_retyped_to_kwh", "tier_threshold_retyped"})

    def test_guard_retypes_time_point(self):
        norm = {
            "matched": True,
            "rule": "ratio_sequence",
            "param_type": "ratio_target",
            "norm_value": "22:00",
            "norm_unit": "none",
            "norm_start": None,
            "norm_end": None,
            "range_start": None,
            "range_end": None,
            "op": None,
            "scope_unit": None,
        }
        adjusted, action = apply_post_normalization_guards(
            raw_value="22:00",
            raw_unit=None,
            clause_text="\u53c2\u4e0e\u5e02\u573a\u5316\u4ea4\u6613\u7684\u4f9b\u6696\u7528\u7535\u6267\u884c22:00-7:00\u3002",
            raw_start=0,
            raw_end=5,
            norm=norm,
        )
        self.assertTrue(adjusted["matched"])
        self.assertEqual(adjusted["param_type"], "time_window")
        self.assertEqual(adjusted["norm_unit"], "time_point")
        self.assertEqual(adjusted["norm_value"], "22:00")
        self.assertEqual(action, "time_point_retyped")

    def test_build_norm_input_drops_mispair_for_price_value(self):
        merged, dropped = build_norm_input(
            raw_value="0.507",
            raw_unit="\u5343\u74e6\u65f6",
            clause_text="\u6708\u7528\u7535\u91cf2600\u5343\u74e6\u65f6\u4ee5\u5185\u63090.2862\u5143/\u5343\u74e6\u65f6\uff0c\u8d85\u8fc7\u7684\u63090.507\u5143/\u5343\u74e6\u65f6\u3002",
            raw_start=25,
            raw_end=30,
        )
        self.assertTrue(dropped)
        self.assertEqual(merged, "0.507")

    def test_build_norm_input_keeps_real_threshold_unit(self):
        merged, dropped = build_norm_input(
            raw_value="170",
            raw_unit="\u5343\u74e6\u65f6",
            clause_text="\u7b2c\u4e00\u6863170\u5343\u74e6\u65f6\u4ee5\u4e0a\u90e8\u5206\u52a0\u4ef70.05\u5143/\u5343\u74e6\u65f6\u3002",
            raw_start=3,
            raw_end=6,
        )
        self.assertFalse(dropped)
        self.assertEqual(merged, "170\u5343\u74e6\u65f6")

    def test_canonicalize_unit_alias(self):
        self.assertEqual(canonicalize_unit_alias("Ԫ/ǧ��ʱ"), "\u5143/\u5343\u74e6\u65f6")
        self.assertEqual(canonicalize_unit_alias("��Ԫ"), "\u4e07\u5143")
        self.assertEqual(canonicalize_unit_alias("\u6237"), "\u6237")


if __name__ == "__main__":
    unittest.main()
