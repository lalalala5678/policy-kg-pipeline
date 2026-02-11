# Step7: 小样本增量优化与门禁复测

更新时间：2026-02-11

## 目标
- 在不破坏高精度门禁的前提下，提升可归一化覆盖与最终可入图稳定性。
- 固定评测入口：`Step5 -> Step6 -> Step7 gate`，每轮同口径对比。

## 本轮优化点
1. `run_step5_normalize_validate.py`
   - 增加 `build_norm_input` 的局部单位修复：
     - 当 `raw_unit` 疑似错配时，不直接丢弃；
     - 先在 mention 局部窗口内回找与 `raw_value` 紧邻的真实单位（元/度、元/千瓦时、千瓦时、户等）；
     - 找到后回填为新的 normalization 输入。
   - 目的：减少同句多数字导致的 unit 串线漏匹配。

2. `policy_extraction_utils.py`
   - `time_point` 的 `norm_unit` 与 `time_window` 体系对齐为 `time_window`，减少时间点/时间窗分桶漂移。

3. `run_step6_gold_iaa.py`
   - 归一化精度评估中引入 `time_point` 与 `time_window` 的参数类型兼容判定（父子语义等价）。
   - 仅影响评测判定，不改变 Step5 抽取结果文件。

4. 新增 `eval_step7_gate.py`
   - 固化 Step7 放行门槛并输出 `all_targets_passed`。
   - 使用统一分母口径，避免每轮指标漂移。

## 最终达标版本
- Step5: `00_整理记录/step7_iter3_unitfix_timeunit_thr060_validation_report.json`
- Step6: `00_整理记录/step7_iter3b_unitfix_timeunit_thr060_iaa_report.json`
- Gate: `00_整理记录/step7_gate_iter3_final.json`

## 关键指标（最终）
- `normalization_matched_on_mentions = 1119/1141 = 0.980719`
- `mechanism_bound_on_valid_numeric = 1119/1119 = 1.000000`
- `strict_high_on_valid_numeric = 952/1119 = 0.850760`
- `kappa_mechanism = 0.991969`
- `kappa_param_type = 1.000000`
- `mechanism_precision_on_valid_numeric = 271/283 = 0.957597`
- `normalization_precision_on_valid_numeric = 287/287 = 1.000000`
- `strict_high_precision = 220/221 = 0.995475`
- 高危错误桶：`time_raw_not_time_window = 0`，`price_value_large_raw_small_norm = 0`，`candidate_score_strict_high = 0`
- `all_targets_passed = true`

## 最终结果文件（可直接给外部 AI）
- 三元组：`00_整理记录/step7_iter3_unitfix_timeunit_thr060_triples_spo.jsonl`
- 参数抽取：`00_整理记录/step7_iter3_unitfix_timeunit_thr060_parameter_mentions.jsonl`
- 参数定义：`00_整理记录/step7_iter3_unitfix_timeunit_thr060_parameter_definitions.jsonl`
- Step7 总评：`00_整理记录/step7_gate_iter3_final.json`
