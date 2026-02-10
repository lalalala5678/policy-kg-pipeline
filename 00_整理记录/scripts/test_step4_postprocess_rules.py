from __future__ import annotations

from policy_extraction_utils import normalize_parameter
from step4_kb_score import is_numeric_like_text


def test_normalize_parameter_priority() -> None:
    a = normalize_parameter("0.53元/度")
    assert a["matched"] is True
    assert a["rule"] == "yuan_per_degree_to_yuan_per_kwh"
    assert a["norm_unit"] == "yuan_per_kwh"
    assert abs(float(a["norm_value"]) - 0.53) < 1e-9

    b = normalize_parameter("3万元/村")
    assert b["matched"] is True
    assert b["rule"] == "ten_thousand_yuan_per_village"
    assert b["norm_unit"] == "ten_thousand_yuan"
    assert b.get("scope_unit") == "village"
    assert abs(float(b["norm_value"]) - 3.0) < 1e-9

    c = normalize_parameter("5万吨级")
    assert c["matched"] is True
    assert c["rule"] == "tonnage_class_threshold"
    assert c["norm_unit"] == "ton"
    assert abs(float(c["norm_value"]) - 50000.0) < 1e-9


def test_numeric_like_detection() -> None:
    assert is_numeric_like_text("10")
    assert is_numeric_like_text("百分之十")
    assert is_numeric_like_text("10:00-12:00")
    assert is_numeric_like_text("1.5:1:0.5")
    assert is_numeric_like_text("十五")
    assert not is_numeric_like_text("按规定执行")


if __name__ == "__main__":
    test_normalize_parameter_priority()
    test_numeric_like_detection()
    print("tests passed")

