# Step8.2：查询样例包与冲突信号化

更新时间：2026-02-11  
状态：已完成（可进入 Step9）

## 1. 目标
- 基于 Step8 图包提供固定查询模板，验证多跳路径可用性。
- 把冲突日志升级为边级信号，供检索/推演做风险提示。

## 2. 输入与脚本
- 输入：
  - `结果文件夹/step8_iter1/strict_high/*`
  - `结果文件夹/step8_iter1/strict_all/*`
  - `结果文件夹/step8_iter1/conflicts.jsonl`
- 脚本：
  - `00_整理记录/scripts/run_step8_2_query_pack.py`

## 3. 输出目录
- `结果文件夹/step8_2_iter1/`

文件清单：
- `query_pack.cql`：固定 Cypher 查询模板
- `query_examples.json`：参数化样例与预览
- `query_pack_readme.md`：查询包使用说明
- `edge_signals.csv`：边级风险信号（`conflict_count`, `alt_candidates_count`, `conflict_type`, `risk_level`）
- `conflict_signal_report.json`：冲突信号统计
- `step8_2_eval_report.json`：门禁评测结果

## 4. 评测结果（门禁）
来源：`结果文件夹/step8_2_iter1/step8_2_eval_report.json`
- `query_template_count = 12`
- `query_execution_success_rate = 1.0`
- `core_path_coverage = 1.0`
- `parameterized_example_coverage = 1.0`
- `edge_signal_coverage_on_strict_high = 1.0`
- `conflict_type_classification_coverage = 1.0`
- `deterministic_pack_rebuild_match = true`
- `all_targets_passed = true`

## 5. 创新点
- 查询模板化：将多跳能力固化为可复跑、可审计的查询集合。
- 冲突信号产品化：把 `conflicts.jsonl` 转成可直接用于图查询排序的风险特征。
- 主图/扩展图协同：`strict_high` 保精度，`strict_all` 提召回，查询层统一消费。

## 6. Step9 前置价值
- Step9 可直接复用查询模板开展推演评测。
- Step9 可直接使用 `edge_signals.csv` 执行风险感知检索与冲突分析。
