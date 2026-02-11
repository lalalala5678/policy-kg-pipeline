import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "00_\u6574\u7406\u8bb0\u5f55" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from policy_extraction_utils import normalize_parameter  # noqa: E402


class TestStep5Normalizer(unittest.TestCase):
    def test_fen_per_kwh_to_yuan_per_kwh(self):
        result = normalize_parameter("\u4e0a\u6d6e5\u5206/\u5343\u74e6\u65f6")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "fen_per_kwh_to_yuan_per_kwh")
        self.assertEqual(result["norm_unit"], "yuan_per_kwh")
        self.assertAlmostEqual(result["norm_value"], 0.05, places=6)

    def test_percent_chinese(self):
        result = normalize_parameter("\u4ef7\u5dee\u4e3a\u767e\u5206\u4e4b\u4e09\u5341")
        self.assertTrue(result["matched"])
        self.assertEqual(result["norm_unit"], "percent")
        self.assertAlmostEqual(result["norm_value"], 30.0, places=6)

    def test_percent_without_delta_cue_is_ratio_target(self):
        result = normalize_parameter("覆盖率达到80%")
        self.assertTrue(result["matched"])
        self.assertEqual(result["norm_unit"], "percent")
        self.assertEqual(result["param_type"], "ratio_target")

    def test_percent_with_delta_cue_is_price_delta_pct(self):
        result = normalize_parameter("峰段电价上浮25%")
        self.assertTrue(result["matched"])
        self.assertEqual(result["norm_unit"], "percent")
        self.assertEqual(result["param_type"], "price_delta_pct")

    def test_time_window(self):
        result = normalize_parameter("10:00-12:30")
        self.assertTrue(result["matched"])
        self.assertEqual(result["param_type"], "time_window")
        self.assertEqual(result["norm_unit"], "time_window")
        self.assertEqual(result["norm_start"], "10:00")
        self.assertEqual(result["norm_end"], "12:30")

    def test_time_point_not_ratio_target(self):
        result = normalize_parameter("7:00")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "time_point")
        self.assertEqual(result["param_type"], "time_window")
        self.assertEqual(result["norm_unit"], "time_point")
        self.assertEqual(result["norm_value"], "07:00")

    def test_date_like_filtered(self):
        result = normalize_parameter("2024-09")
        self.assertFalse(result["matched"])
        self.assertEqual(result["rule"], "date_like_filtered")

    def test_capacity_ten_thousand_kw_to_mw(self):
        result = normalize_parameter("\u7cfb\u7edf\u5bb9\u91cf\u4e0d\u4f4e\u4e8e2\u4e07\u5343\u74e6")
        self.assertTrue(result["matched"])
        self.assertEqual(result["norm_unit"], "mw")
        self.assertAlmostEqual(result["norm_value"], 20.0, places=6)

    def test_kwh_threshold_from_chinese_number(self):
        result = normalize_parameter("\u4e0d\u4f4e\u4e8e\u4e09\u767e\u5343\u74e6\u65f6")
        self.assertTrue(result["matched"])
        self.assertEqual(result["param_type"], "consumption_threshold_kwh")
        self.assertEqual(result["norm_unit"], "kwh")
        self.assertAlmostEqual(result["norm_value"], 300.0, places=6)

    def test_ratio_sequence(self):
        result = normalize_parameter("1.5:1:0.5")
        self.assertTrue(result["matched"])
        self.assertEqual(result["param_type"], "ratio_target")
        self.assertEqual(result["norm_unit"], "none")
        self.assertEqual(result["norm_value"], "1.5:1:0.5")

    def test_ratio_sequence_funding_share(self):
        clause = "补贴资金由中央、市、区按照1:1:1比例分担。"
        result = normalize_parameter("1:1:1", clause)
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "ratio_sequence")
        self.assertEqual(result["param_type"], "funding_share_ratio")
        self.assertEqual(result["norm_unit"], "none")

    def test_duration_context_does_not_swallow_price_value(self):
        clause = "其余月份为0.0634元/千瓦时。"
        result = normalize_parameter("0.0634", clause)
        self.assertTrue(result["matched"])
        self.assertEqual(result["param_type"], "price_value")
        self.assertEqual(result["norm_unit"], "yuan_per_kwh")
        self.assertNotEqual(result["rule"], "duration_month_context")

    def test_no_context_leakage_for_yuan(self):
        clause = "\u7b2c\u4e00\u6863\u7535\u91cf\u4e3a351\u5343\u74e6\u65f6\u53ca\u4ee5\u4e0b\uff0c\u8d85\u51fa\u90e8\u5206\u6bcf\u5343\u74e6\u65f6\u52a0\u4ef70.3\u5143\u3002"
        result = normalize_parameter("0.3\u5143", clause)
        self.assertTrue(result["matched"])
        self.assertNotEqual(result["rule"], "kwh_threshold")
        self.assertNotEqual(result["rule"], "kwh_threshold_range")
        self.assertEqual(result["norm_unit"], "yuan")

    def test_no_context_leakage_for_percent(self):
        clause = "\u572811:00-12:00\u548c15:00-17:00\u6267\u884c\uff0c\u5cf0\u6bb5\u7535\u4ef7\u4e0a\u6d6e25%\u3002"
        result = normalize_parameter("25%", clause)
        self.assertTrue(result["matched"])
        self.assertIn(result["rule"], {"percent_numeric", "percent_chinese"})
        self.assertEqual(result["norm_unit"], "percent")

    def test_no_context_leakage_threshold_vs_price(self):
        clause = "\u7b2c\u4e00\u6863170\u5343\u74e6\u65f6\u4ee5\u4e0a\u52a0\u4ef70.05\u5143/\u5343\u74e6\u65f6\u3002"
        result = normalize_parameter("170\u5343\u74e6\u65f6", clause)
        self.assertTrue(result["matched"])
        self.assertEqual(result["param_type"], "consumption_threshold_kwh")
        self.assertEqual(result["norm_unit"], "kwh")
        self.assertEqual(result["norm_value"], 170.0)

    def test_kwh_range(self):
        result = normalize_parameter("181-400\u5343\u74e6\u65f6")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "kwh_threshold_range")
        self.assertEqual(result["param_type"], "consumption_threshold_kwh")
        self.assertEqual(result["norm_unit"], "kwh")
        self.assertEqual(result["range_start"], 181.0)
        self.assertEqual(result["range_end"], 400.0)
        self.assertEqual(result["op"], "between")

    def test_duration_month(self):
        result = normalize_parameter("\u4e0d\u5c11\u4e8e\u4e24\u4e2a\u6708")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "duration_month")
        self.assertEqual(result["param_type"], "duration_threshold_month")
        self.assertEqual(result["norm_unit"], "month")
        self.assertEqual(result["norm_value"], 2.0)

    def test_duration_year(self):
        result = normalize_parameter("不低于3年")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "duration_month")
        self.assertEqual(result["param_type"], "duration_threshold_year")
        self.assertEqual(result["norm_unit"], "year")
        self.assertEqual(result["norm_value"], 3.0)

    def test_duration_hour(self):
        result = normalize_parameter("8\u5c0f\u65f6")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "duration_hour")
        self.assertEqual(result["param_type"], "duration_threshold_hour")
        self.assertEqual(result["norm_unit"], "hour")
        self.assertEqual(result["norm_value"], 8.0)

    def test_household_count(self):
        result = normalize_parameter("500\u6237")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "household_count")
        self.assertEqual(result["param_type"], "target_household_count")
        self.assertEqual(result["norm_unit"], "household")
        self.assertEqual(result["norm_value"], 500.0)

    def test_watt_to_kw_capacity(self):
        result = normalize_parameter("100W")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "capacity_value")
        self.assertEqual(result["norm_unit"], "kw")
        self.assertAlmostEqual(result["norm_value"], 0.1, places=6)


if __name__ == "__main__":
    unittest.main()
