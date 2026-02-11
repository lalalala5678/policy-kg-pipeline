# Step6 测评参数与计算口径（全量）

更新时间：2026-02-11  
对应结果文件：`00_整理记录/step6_iter3_fixabcd_iaa_report.json`

## 1. 结论
- 当前 Step6 已达标：`all_targets_passed = true`
- 本文件包含 Step6 全部测评参数的当前值与计算方式（与脚本 `run_step6_gold_iaa.py` 一致）。

## 2. 数据来源与执行参数
- 脚本：`00_整理记录/scripts/run_step6_gold_iaa.py`
- 输入：
  - `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_parameter_mentions.jsonl`
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
- `valid_numeric = count(span_ok && normalization_matched && numeric_like) = 277`
- `numeric_like` 定义：
  - `row.is_numeric_like == true` 或
  - `raw_value` 命中数字/时间窗口/百分比正则

## 4. 抽样类指标（sampling）
- `target_total = 300`
  - 计算：命令行参数 `--sample-size`
- `actual_total = 300`
  - 计算：`len(sampled)`
- `strict_high_count = 223`
  - 计算：`count(sample.strict_high == true)`
- `hard_case_count = 155`
  - 计算：`count(sample._hard_tags 非空)`
- `mechanism_distribution`
  - 计算：`Counter(sample.mechanism_bind_after)`
  - 当前值：`subsidy=47, task_assessment=75, technology_route=43, general_price_adjustment=34, tiered_pricing=43, tou_pricing=56, differential_penalty_pricing=1, None=1`
- `param_type_distribution`
  - 计算：`Counter(sample.param_type)`
  - 当前值：`subsidy_amount=17, ratio_target=111, target_household_count=13, None=23, price_delta_pct=30, funding_share_ratio=4, time_window=29, duration_threshold_hour=5, consumption_threshold_kwh=25, tonnage_threshold=2, price_value=30, other=3, duration_threshold_year=2, area_subsidy_amount=4, duration_threshold_month=2`
- `bind_group_distribution`
  - 计算：`Counter(bind_reason_group(sample.mechanism_bind_reason))`
  - 当前值：`high_conf=242, fallback=25, candidate_score=32, other=1`
- `hard_tag_distribution`
  - 计算：对每个 sample 的 hard tags 展平后做 `Counter`
  - 当前值：`negative_domain=44, task_clause=40, candidate_score=32, time_token=29, threshold_price_same_clause=26`

## 5. IAA 指标（Pass-A vs Pass-B）
- `kappa_mechanism = 0.987985`
  - 计算：`cohen_kappa(PassA.mechanism_bind_after, PassB.mechanism_bind_after)`
  - 公式：`kappa = (observed - expected) / (1 - expected)`
  - 其中：
    - `observed = 一致样本数 / N`
    - `expected = Σc P_A(c) * P_B(c)`（按类别边际概率）
- `kappa_param_type = 1.000000`
  - 计算：`cohen_kappa(PassA.param_type, PassB.param_type)`
- `exact_match_norm_unit = 1.000000`
  - 计算：`count(PassA.norm_unit == PassB.norm_unit) / N`
- `agreement_strict_high_eligible = 1.000000`
  - 计算：`count(PassA.strict_high_eligible == PassB.strict_high_eligible) / N`
- 其中 `N = sample_total = 300`

## 6. 质量指标（quality，Step5 对比 adjudicated Gold）
- `mechanism_precision_on_valid_numeric = 262/274 = 0.956204`
  - 分母 `274`：`valid_numeric` 中 `gold_mechanism_bind_after ∈ KNOWN_MECHANISMS`
  - 分子 `262`：上述分母集合内 `step5.mechanism_bind_after == gold_mechanism_bind_after`
- `normalization_precision_on_valid_numeric = 274/277 = 0.989170`
  - 分母 `277`：`valid_numeric` 中 `gold_param_type` 与 `gold_norm_unit` 均非空
  - 分子 `274`：上述分母集合内同时满足：
    - `step5.param_type == gold_param_type`
    - `step5.norm_unit == gold_norm_unit`
- `strict_high_precision = 223/223 = 1.000000`
  - 分母 `223`：`step5.strict_high == true`
  - 分子 `223`：上述分母集合内 `gold_strict_high_eligible == true`

## 7. 错误簇指标（error_clusters）
- `time_raw_not_time_window = 0`
  - 计算：`raw_value` 命中时间点/时间段，但 `gold_param_type` 不在 `{time_window, time_point}`
- `price_value_large_raw_small_norm = 0`
  - 计算：
    - `raw_num >= 100`
    - `gold_norm_unit == yuan_per_kwh`
    - `gold_norm_value <= 2.0`
- `candidate_score_strict_high = 0`
  - 计算：`step5.mechanism_bind_reason == candidate_score && gold_strict_high_eligible == true`

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

## 10. 本轮额外校验（A/B/C/D）
- 文件：`00_整理记录/step6_fixabcd_eval.json`
- 对比（旧 `step6_gold_adjudicated.jsonl` -> 新 `step6_iter3_fixabcd_gold_adjudicated.jsonl`）：
  - `strict_high=true && gold_strict_high_eligible=false`：`6 -> 0`
  - `duration_month_context`：`15 -> 4`
  - `duration_month_context + raw_unit`：`3 -> 0`
  - `duration_month_context` 进入 strict_high：`15 -> 1`
  - `1:1:1` 作为 `funding_share_ratio`：`0 -> 3`
