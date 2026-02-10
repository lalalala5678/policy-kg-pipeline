import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "00_整理记录" / "scripts"
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

    def test_time_window(self):
        result = normalize_parameter("10:00-12:30")
        self.assertTrue(result["matched"])
        self.assertEqual(result["param_type"], "time_window")
        self.assertEqual(result["norm_unit"], "time_window")
        self.assertEqual(result["norm_start"], "10:00")
        self.assertEqual(result["norm_end"], "12:30")

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

    def test_no_context_leakage_for_yuan(self):
        clause = "第三档电量为351千瓦时及以上，价格在第一档基础上每千瓦时提高0.3元。"
        result = normalize_parameter("0.3元", clause)
        self.assertTrue(result["matched"])
        self.assertNotEqual(result["rule"], "kwh_threshold")
        self.assertNotEqual(result["rule"], "kwh_threshold_range")
        self.assertEqual(result["norm_unit"], "yuan")

    def test_no_context_leakage_for_percent(self):
        clause = "在11:00-12:00和15:00-17:00执行，尖峰电价上浮25%。"
        result = normalize_parameter("25%", clause)
        self.assertTrue(result["matched"])
        self.assertIn(result["rule"], {"percent_numeric", "percent_chinese"})
        self.assertEqual(result["norm_unit"], "percent")

    def test_kwh_range(self):
        result = normalize_parameter("181-400千瓦时")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "kwh_threshold_range")
        self.assertEqual(result["param_type"], "consumption_threshold_kwh")
        self.assertEqual(result["norm_unit"], "kwh")
        self.assertEqual(result["range_start"], 181.0)
        self.assertEqual(result["range_end"], 400.0)
        self.assertEqual(result["op"], "between")

    def test_duration_month(self):
        result = normalize_parameter("不少于两个月")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "duration_month")
        self.assertEqual(result["param_type"], "duration_threshold_month")
        self.assertEqual(result["norm_unit"], "month")
        self.assertEqual(result["norm_value"], 2.0)

    def test_duration_hour(self):
        result = normalize_parameter("8小时")
        self.assertTrue(result["matched"])
        self.assertEqual(result["rule"], "duration_hour")
        self.assertEqual(result["param_type"], "duration_threshold_hour")
        self.assertEqual(result["norm_unit"], "hour")
        self.assertEqual(result["norm_value"], 8.0)

    def test_household_count(self):
        result = normalize_parameter("500户")
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
