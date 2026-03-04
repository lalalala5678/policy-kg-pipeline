# 投稿图件指引

## Figure 1: Step1-Step9 闭环总览
- 数据来源: `table01_pipeline_overview.csv`
- 建议图型: 分阶段流程图 + 关键指标注释

## Figure 2: Step4 迭代提升曲线
- 数据来源: `table02_step4_iteration_scores.csv`
- 建议图型: 折线图（total_score, strict_triplet_ready_rate, param_bind_rate）

## Figure 3: 门禁协议通过矩阵
- 数据来源: `table03_protocol_gate_threshold_vs_observed.csv`
- 建议图型: 热力表/对勾矩阵

## Figure 4: 消融对比
- 数据来源: `table04_ablation_results.csv`
- 建议图型: 分组柱状图

## Figure 5: 跨年份稳健性
- 数据来源: `table05_cross_year_robustness.csv`
- 建议图型: 多折线图（norm/mec_bound/strict_high）

## Figure 6: 运行成本画像
- 数据来源: `table06_cost_profile_benchmarks.csv`, `00_整理记录/step12_cost_profile_report.json`
- 建议图型: 条形图（脚本耗时）+ 表格（产物体量）

## Figure 7: 查询模板执行覆盖
- 数据来源: `table07_query_template_execution.csv`
- 建议图型: 条形图（result_count）+ 成功率摘要

## Figure 8: 图包与数据库规模
- 数据来源: `table08_graph_and_db_metrics.csv`
- 建议图型: 对比柱状图（strict_high vs strict_all vs neo4j totals）

## Figure 9: 错误与风险画像
- 数据来源: `table09_error_risk_profile.csv`, `00_整理记录/step14_error_profile_report.md`
- 建议图型: 风险雷达图/门禁余量条形图

## Figure 10: 外部基线对照
- 数据来源: `table10_external_baseline_comparison.csv`
- 建议图型: 分组柱状图（strict_high/local_supported）

## Figure 11: 查询延迟分布
- 数据来源: `table11_query_latency_by_template.csv`
- 建议图型: 每模板 P50/P95 误差条

## Figure 12: 标注流程与一致性
- 数据来源: `table12_annotation_protocol_summary.csv`
- 建议图型: 流程图 + 指标卡片
