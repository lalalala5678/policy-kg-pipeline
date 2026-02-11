# Step6 iter3 人工抽测记录（Codex）

时间：2026-02-11  
数据源：`00_整理记录/step6_iter3_fixabcd_gold_adjudicated.jsonl`

## 抽测目标
- 复核 A/B/C/D 修复是否落到样本结果。
- 抽测 strict_high 样本，确认无明显语义错配进入高置信集合。

## A/B/C/D 焦点样本
- `pm_106b35c73d16a957c011`：`1:1:1` -> `funding_share_ratio`，`strict_high=true`，判定：通过。
- `pm_296552a3297b9f0030f2`：`3071` -> `no_match`，`strict_high=false`，判定：通过（不再误入金额）。
- `pm_0642d8a0dd09dda47c47`：未进入本轮 300 样本，但在 Step5 全量中已从 `duration_threshold_month` 修复为 `no_match`。
- `pm_0e9050822c1d12a4c933`：未进入本轮 300 样本，但在 Step5 全量中已从 `duration_threshold_month` 修复为 `no_match`。
- `pm_00f41be4f5cef15eaf85`：未进入本轮 300 样本，但在 Step5 全量中已从 `strict_high=true` 调整为 `strict_high=false`（弱括号约束）。
- `pm_152d1770732a3dc52686`：未进入本轮 300 样本，但在 Step5 全量中已从 `duration_threshold_month` 修复为 `no_match`。

## strict_high 随机抽测（10 条）
- `pm_ab389d03dd62ddbd7a78`：`19:30-21:30` -> `time_window`/`tou_pricing`，通过。
- `pm_dd3ba3a88cebcba6375b`：`13:00-17:00` -> `time_window`/`tou_pricing`，通过。
- `pm_450f39544093f7b289bf`：`171-260` -> `consumption_threshold_kwh`/`tiered_pricing`，通过。
- `pm_23409eb9f66c20d18dc8`：`340` -> `consumption_threshold_kwh`/`tiered_pricing`，通过。
- `pm_0534d54d8a59a9de5ad9`：`3041` -> `target_household_count`，通过。
- `pm_2685fd65e7b77888bab4`：`20` -> `tonnage_threshold`，通过。
- `pm_c785a7eb6983cf007887`：`200` -> `consumption_threshold_kwh`，通过。
- `pm_526fdc7f348591ec04d9`：`50` -> `ratio_target`，通过。
- `pm_98011c10aa729ac591c6`：`40` -> `ratio_target`，通过。
- `pm_a2f773f937d13323868f`：`10` -> `consumption_threshold_kwh`，通过。

## 抽测结论
- 本次抽测未发现 A/B/C/D 旧问题在 `strict_high` 主集复现。
- 与量化指标一致：`strict_high_true_gold_false = 0`（见 `00_整理记录/step6_fixabcd_eval.json`）。
