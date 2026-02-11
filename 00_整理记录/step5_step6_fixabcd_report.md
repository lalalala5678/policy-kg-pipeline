# Step5/Step6 修复与测评报告（fixabcd）

更新时间：2026-02-11

## 1. 修复目标
- A：避免 `duration_month_context` 将电价/电量/年份误归一为 month。
- B：避免户数（如 3071 户）被误配为 `subsidy_amount/yuan`。
- C：将 `1:1:1` 资金分担比例从 `ratio_target` 细化为 `funding_share_ratio`。
- D：统一 `strict_high` 资格门禁，消除弱约束误入高置信集合。

## 2. 代码改动
- `00_整理记录/scripts/policy_extraction_utils.py`
  - 收紧 `duration_month_context` 触发条件。
  - `ratio_sequence` 支持资金分担语义映射 `funding_share_ratio`。
  - 新增 `duration_threshold_year`。
- `00_整理记录/scripts/run_step5_normalize_validate.py`
  - 新增 `strict_compat_ok` 与 `strict_weak_constraint` 门禁字段。
  - 新增户数邻域误配纠偏与单位配对拦截。
  - strict_high 判定加入兼容性与弱约束过滤。
- `00_整理记录/scripts/run_step6_gold_iaa.py`
  - 对齐 Step5 门禁逻辑（compat + weak constraint）。
  - 支持 `funding_share_ratio` 与 `duration_threshold_year`。
  - 路径输出增加 `rel_or_posix` 兼容，避免中文路径失败。
- 测试：
  - `00_整理记录/tests/test_step5_normalizer.py`
  - `00_整理记录/tests/test_step5_binding_rules.py`

## 3. Step5 测评结果（旧 -> 新）
来源：`00_整理记录/step5_fixabcd_issueAtoD_eval.json`

- `duration_month_context`：`29 -> 7`
- `duration_month_context + raw_unit`：`13 -> 0`
- duration 进入 strict_high：`29 -> 1`
- 弱括号 duration 进入 strict_high：`9 -> 0`
- `1:1:1` 作为 `funding_share_ratio`：`0 -> 7`
- `1:1:1` 仍在 `ratio_target`：`11 -> 4`

Step5 主指标（`step5_seq_step2_v2_rebind12_fixabcd_validation_report.json`）：
- `normalization_matched_rate = 0.945662`
- `mechanism_bound_rate_valid_numeric = 1.000000`
- `strict_high_rate_valid_numeric = 0.856348`
- `local_supported_rate_valid_numeric = 0.889713`
- `all_targets_passed = true`

## 4. Step6 测评结果（旧 -> 新）
来源：`00_整理记录/step6_fixabcd_eval.json`

- `strict_high=true && gold_strict_high_eligible=false`：`6 -> 0`
- `duration_month_context`：`15 -> 4`
- `duration_month_context + raw_unit`：`3 -> 0`
- `duration_month_context` 进入 strict_high：`15 -> 1`
- `1:1:1` 作为 `funding_share_ratio`：`0 -> 3`

Step6 主指标（`step6_iter3_fixabcd_iaa_report.json`）：
- `kappa_mechanism = 0.987985`
- `kappa_param_type = 1.000000`
- `exact_match_norm_unit = 1.000000`
- `agreement_strict_high_eligible = 1.000000`
- `mechanism_precision_on_valid_numeric = 262/274 = 0.956204`
- `normalization_precision_on_valid_numeric = 274/277 = 0.989170`
- `strict_high_precision = 223/223 = 1.000000`
- `all_targets_passed = true`

## 5. 关键样本复核
- `pm_0642d8...`：`6000`，`duration_threshold_month -> no_match`。
- `pm_0e9050...`：`0.0634`，`duration_threshold_month -> no_match`。
- `pm_296552...`：`3071`，`subsidy_amount -> no_match`。
- `pm_106b35...`：`1:1:1`，`ratio_target -> funding_share_ratio`。
- `pm_00f41b...`：`（不少于两个月）`，`strict_high true -> false`。
- `pm_152d17...`：`至2018`，`duration_threshold_month -> no_match`。

## 6. 当前结论
- A/B/C/D 问题均完成针对性修复。
- Step5 与 Step6 均保持阈值达标。
- 高置信集合更保守且一致性更高，适合继续进入后续训练/入图阶段。
