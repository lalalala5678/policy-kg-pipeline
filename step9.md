# Step9：Neo4j评测与推演落地

更新时间：2026-02-12  
状态：已完成并通过

## 1. 目标
- 把 Step8/Step8.2 产物在 Neo4j 上完成可复跑落地。
- 验证导入、查询、多跳路径、风险信号、推演输出的端到端可用性。

## 2. 输入
- 主图包：`结果文件夹/step8_iter1/strict_high/*`
- 扩展图包：`结果文件夹/step8_iter1/strict_all/*`
- 查询模板：`结果文件夹/step8_2_iter1/query_pack.cql`
- 查询样例：`结果文件夹/step8_2_iter1/query_examples.json`
- 风险信号：`结果文件夹/step8_2_iter1/edge_signals.csv`

## 3. 脚本
- `00_整理记录/scripts/step9_neo4j_utils.py`
- `00_整理记录/scripts/run_step9_neo4j_eval.py`
- `00_整理记录/scripts/run_step9_query_eval.py`
- `00_整理记录/scripts/run_step9_simulation.py`
- `00_整理记录/scripts/eval_step9_gate.py`

## 4. 输出
- `00_整理记录/step9_iter1/step9_neo4j_import_report.json`
- `00_整理记录/step9_iter1/step9_query_exec_report.json`
- `00_整理记录/step9_iter1/step9_simulation_casebook.json`
- `00_整理记录/step9_iter1/step9_gate_report.json`

## 5. 核心结果
来源：`00_整理记录/step9_iter1/step9_gate_report.json`
- `all_targets_passed = true`
- `node_total = 2892`
- `edge_total = 10610`
- `traceability_rate = 1.0`
- `query_template_count = 12`
- `query_execution_success_rate = 1.0`
- `core_path_coverage = 1.0`
- `risk_aware_rerank_non_regression = true`

## 6. 运行说明
1. 导入与验收  
`python3 00_整理记录/scripts/run_step9_neo4j_eval.py --overwrite`
2. 查询评测  
`python3 00_整理记录/scripts/run_step9_query_eval.py`
3. 推演输出  
`python3 00_整理记录/scripts/run_step9_simulation.py`
4. 总门禁  
`python3 00_整理记录/scripts/eval_step9_gate.py`

