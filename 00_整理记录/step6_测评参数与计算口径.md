# Step6 测评参数与计算口径（全量）

更新时间：2026-02-11  
对应结果文件：`00_整理记录/step6_iter4_fixabcd_plus_iaa_report.json`

## 1. 结论
- 当前 Step6 已达标：`all_targets_passed = true`
- 本文件包含 Step6 全部测评参数的当前值与计算方式（与脚本 `run_step6_gold_iaa.py` 一致）。

## 2. 数据来源与执行参数
- 脚本：`00_整理记录/scripts/run_step6_gold_iaa.py`
- 输入：
  - `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_mentions.jsonl`
  - `00_整理记录/step3_clause_corpus.jsonl`
- 运行参数（config）：
  - `sample_size = 300`
  - `strict_min = 140`
  - `hard_min = 80`
  - `seed = 20260211`

## 3. 分母口径（冻结）
- `all_clause = 2022`（Step3 clause 总量）
- `sample_total = len(adjudicated_rows) = 300`
- `valid_all = count(span_ok && normalization_attempted) = 300`
- `valid_numeric = count(span_ok && normalization_matched && numeric_like) = 278`

## 4. 抽样类指标（sampling）
- `target_total = 300`
- `actual_total = 300`
- `strict_high_count = 214`
- `hard_case_count = 152`
- 其余分布详见：`00_整理记录/step6_iter4_fixabcd_plus_iaa_report.json` 的 `sampling` 字段。

## 5. IAA 指标（Pass-A vs Pass-B）
- `kappa_mechanism = 0.987997`
- `kappa_param_type = 1.000000`
- `exact_match_norm_unit = 1.000000`
- `agreement_strict_high_eligible = 1.000000`

## 6. 质量指标（quality，Step5 对比 adjudicated Gold）
- `mechanism_precision_on_valid_numeric = 261/274 = 0.952555`
- `normalization_precision_on_valid_numeric = 277/278 = 0.996403`
- `strict_high_precision = 213/214 = 0.995327`

## 7. 错误簇指标（error_clusters）
- `time_raw_not_time_window = 0`
- `price_value_large_raw_small_norm = 0`
- `candidate_score_strict_high = 0`

## 8. 目标阈值与达标状态（target_pass）
- `kappa_mechanism >= 0.80`：`true`
- `kappa_param_type >= 0.80`：`true`
- `exact_match_norm_unit >= 0.90`：`true`
- `agreement_strict_high_eligible >= 0.90`：`true`
- `mechanism_precision >= 0.90`：`true`
- `normalization_precision >= 0.90`：`true`
- `strict_high_precision >= 0.92`：`true`
- `time_raw_not_time_window == 0`：`true`
- `price_value_large_raw_small_norm == 0`：`true`
- `candidate_score_strict_high == 0`：`true`
- `sample_size >= 240`：`true`
- `sample_strict >= 120`：`true`
- `sample_hard >= 60`：`true`

## 9. 总状态
- `all_targets_passed = true`

## 10. 本轮优化对比（rebind12 -> rebind14）
- 参考：`00_整理记录/step5_fixabcd_plus2_eval.json`
- strict `price_value>=10`：`3 -> 0`
- strict `ratio_target + 局部价格变动词`：`54 -> 0`
- strict `price_delta_pct + 局部无价格变动词`：`6 -> 1`
- strict `amount_param + non_subsidy mechanism`：`2 -> 0`
