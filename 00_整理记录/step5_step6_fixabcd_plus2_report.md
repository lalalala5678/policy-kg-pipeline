# Step5/Step6 优化与测评报告（fixabcd_plus2）

更新时间：2026-02-11

## 1. 本轮目标
- 在已有 A/B/C/D 修复基础上继续降低高风险误差，重点处理：
  - 大额金额被误归 `price_value`；
  - 百分比分型在价格语义与目标语义间的漂移；
  - 金额参数落到非补贴机制。

## 2. 本轮规则优化
- `policy_extraction_utils.py`
  - percent 分型由宽泛价格词改为“价格变动触发词” (`上浮/下浮/加价/降价/调价/提高/降低`)。
- `run_step5_normalize_validate.py`
  - 新增 `price_value -> subsidy_amount` 回收规则（大额 `yuan` + 补贴语境 + 非每度/每千瓦时局部语境）。
  - 保留此前 `subsidy_amount -> price_value` 的局部价差回收规则。
- 测试更新：
  - `test_step5_normalizer.py`
  - `test_step5_binding_rules.py`

## 3. 版本对比与选型
- 试跑了 `rebind13`、`rebind14`、`rebind15`。
- 最终选择 `rebind14_fixabcd_plus2`（平衡最佳）：
  - `rebind15` 虽进一步压缩了 `price_delta_pct` 局部误差，但导致 strict 覆盖下降且 `ratio_target + 价格词` 回弹，不采用。

## 4. Step5 最终结果（rebind14_fixabcd_plus2）
产物：
- `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_mentions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_definitions.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_triples_spo.jsonl`
- `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_validation_report.json`
- `00_整理记录/step5_fixabcd_plus2_eval.json`

主指标：
- `normalization_matched_rate = 0.945662`
- `mechanism_bound_rate_valid_numeric = 1.000000`
- `strict_high_rate_valid_numeric = 0.848934`
- `local_supported_rate_valid_numeric = 0.895273`
- `all_targets_passed = true`

风险指标对比（rebind12 -> rebind14）：
- strict `price_value >= 10`：`3 -> 0`
- strict `ratio_target + 局部价格变动词`：`54 -> 0`
- strict `price_delta_pct + 局部无价格变动词`：`6 -> 1`
- strict `amount_param + non_subsidy mechanism`：`2 -> 0`

## 5. Step6 最终结果（iter4_fixabcd_plus）
产物：
- `00_整理记录/step6_iter4_fixabcd_plus_gold_adjudicated.jsonl`
- `00_整理记录/step6_iter4_fixabcd_plus_iaa_report.json`
- `00_整理记录/step6_fixabcd_plus2_eval.json`

核心指标：
- `kappa_mechanism = 0.987997`
- `kappa_param_type = 1.000000`
- `normalization_precision_on_valid_numeric = 277/278 = 0.996403`
- `mechanism_precision_on_valid_numeric = 261/274 = 0.952555`
- `strict_high_precision = 213/214 = 0.995305`
- `all_targets_passed = true`

## 6. 结论
- 本轮优化已完成并达成门禁目标。
- 高风险错误显著下降，且 Step6 一致性/精度保持高位。
- 结果可进入你下一步外部评审与后续迭代。
