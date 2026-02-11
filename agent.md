# AGENT.md - 政策知识图谱项目执行状态

更新时间：2026-02-12

## 1. 当前阶段状态
- Step1（领域 Schema 设计）：已完成
- Step2（样本抽样与标注规范）：已完成
- Step3（预处理与切分）：已完成
- Step4（UIE 基线抽取）：已完成
- Step5（规则归一与校验）：已完成并达标
- Step6（Gold/IAA）：已完成并达标
- Step7（规则增量优化与门禁复测）：已完成并达标
- Step7b（固定 Gold 门禁增益实验）：已完成并通过
- Step8（图包导出与工程验收）：已完成并通过
- Step8.2（查询样例包与冲突信号化）：已完成并通过
- Step9（评测与推演落地）：已完成并通过

## 2. 交付物主目录（最新）
- `结果文件夹/`

其中核心可用内容：
- Step8 图包：`结果文件夹/step8_iter1`
- Step8 重放包：`结果文件夹/step8_iter1_replay`
- Step8.2 查询与信号包：`结果文件夹/step8_2_iter1`
- Step9 评测与推演报告：`00_整理记录/step9_iter1`
- Schema：`结果文件夹/schema_v1.yaml`
- 使用说明：`结果文件夹/README_使用指南.md`

## 3. 关键验收结果

### 3.1 Step7b 门禁（固定 Gold）
来源：`00_整理记录/step7b_iterB_rulefix_gate.json`
- `all_targets_passed = true`
- `strict_high_tp_delta = +2`（220 -> 222）
- `fixed_gold_mechanism_precision = 0.958904`
- `fixed_gold_normalization_precision = 0.993127`
- `fixed_gold_strict_high_precision = 0.995516`

### 3.2 Step8 工程验收
来源：`结果文件夹/step8_iter1/validation_report.json`
- `all_targets_passed = true`
- `deterministic_replay_match = true`
- `conflict_explainability = true`

来源：`结果文件夹/step8_iter1/stats.json`
- strict_high：`nodes=2494, edges=4868, triples=4868`
- strict_all：`nodes=2892, edges=5742, triples=5742`

### 3.3 Step8.2 门禁
来源：`结果文件夹/step8_2_iter1/step8_2_eval_report.json`
- `query_template_count = 12`
- `query_execution_success_rate = 1.0`
- `core_path_coverage = 1.0`
- `edge_signal_coverage_on_strict_high = 1.0`
- `conflict_type_classification_coverage = 1.0`
- `deterministic_pack_rebuild_match = true`
- `all_targets_passed = true`

### 3.4 Step9 门禁（Neo4j 实跑）
来源：`00_整理记录/step9_iter1/step9_gate_report.json`
- `all_targets_passed = true`
- `node_total = 2892`
- `edge_total = 10610`
- `traceability_rate = 1.0`
- `query_template_count = 12`
- `query_execution_success_rate = 1.0`
- `core_path_coverage = 1.0`
- `risk_aware_rerank_non_regression = true`

## 4. Neo4j 导入建议
- 生产主图：`结果文件夹/step8_iter1/strict_high/nodes.csv` + `结果文件夹/step8_iter1/strict_high/edges.csv`
- 扩展召回：`结果文件夹/step8_iter1/strict_all/nodes.csv` + `结果文件夹/step8_iter1/strict_all/edges.csv`
- 冲突风险信号：`结果文件夹/step8_2_iter1/edge_signals.csv`
- 查询模板：`结果文件夹/step8_2_iter1/query_pack.cql`

## 5. Step9 执行产物
1. 导入与验收：`00_整理记录/step9_iter1/step9_neo4j_import_report.json`
2. 查询评测：`00_整理记录/step9_iter1/step9_query_exec_report.json`
3. 推演案例：`00_整理记录/step9_iter1/step9_simulation_casebook.json`
4. 总门禁：`00_整理记录/step9_iter1/step9_gate_report.json`
