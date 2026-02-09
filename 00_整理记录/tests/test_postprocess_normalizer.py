import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "00_整理记录" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from policy_extraction_utils import normalize_parameter  # noqa: E402


class TestPostprocessNormalizationOrder(unittest.TestCase):
    def test_yuan_per_degree_prioritized(self):
        result = normalize_parameter("低谷电价0.3元/度")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "yuan_per_degree_to_yuan_per_kwh")
        self.assertEqual(result["norm_unit"], "yuan_per_kwh")
        self.assertAlmostEqual(result["norm_value"], 0.3, places=6)

    def test_ten_thousand_yuan_per_village_prioritized(self):
        result = normalize_parameter("补贴16.2万元/村，按标准执行")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "ten_thousand_yuan_per_village")
        self.assertEqual(result["norm_unit"], "ten_thousand_yuan")
        self.assertEqual(result["scope_unit"], "village")
        self.assertAlmostEqual(result["norm_value"], 16.2, places=6)

    def test_tonnage_class_prioritized(self):
        result = normalize_parameter("5万吨级以上干散货泊位具备供电能力")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "tonnage_class_threshold")
        self.assertEqual(result["param_type"], "tonnage_threshold")
        self.assertEqual(result["norm_unit"], "ton")
        self.assertAlmostEqual(result["norm_value"], 50000.0, places=6)


if __name__ == "__main__":
    unittest.main()
