import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "00_整理记录" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_step5_normalize_validate import build_clause_candidates, choose_binding_for_mention  # noqa: E402


class TestStep5BindingRules(unittest.TestCase):
    def test_negative_domain_rejects_pricing(self):
        text = "二氧化硫、氮氧化物排放量减少10%以上，空气质量优良天数比例达到80%以上。"
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
        self.assertIn(bind_reason, {"drop_by_negative", "unknown_low_score", "keyword_hit", "keyword_plus_prior", "param_type_map", "candidate_score"})

    def test_tou_clause_prefers_tou(self):
        text = "高峰电价在平段电价基础上上浮50%，低谷电价下浮50%，执行时段为11:00-13:00。"
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


if __name__ == "__main__":
    unittest.main()

