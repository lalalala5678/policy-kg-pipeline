# 投稿版图表包

本目录用于论文投稿阶段直接引用的数据表与图件指引。

## 文件清单
- `table01_pipeline_overview.csv`：Step1-Step9 关键指标总览
- `table02_step4_iteration_scores.csv`：Step4 迭代评分明细
- `table03_protocol_gate_threshold_vs_observed.csv`：门禁阈值与实测对比
- `table04_ablation_results.csv`：最小消融结果
- `table05_cross_year_robustness.csv`：跨年份稳健性
- `table06_cost_profile_benchmarks.csv`：成本画像耗时
- `table07_query_template_execution.csv`：查询模板执行统计
- `table08_graph_and_db_metrics.csv`：图包与数据库规模指标
- `table09_error_risk_profile.csv`：错误与风险画像（若已生成 Step14）
- `table10_external_baseline_comparison.csv`：外部基线同口径对照（若已生成 Step15）
- `table11_query_latency_by_template.csv`：查询延迟 P50/P95（若已生成 Step17）
- `table12_annotation_protocol_summary.csv`：标注流程与一致性摘要（若已生成 Step18）
- `FIGURE_GUIDE.md`：建议图件映射与绘图指引

## 生成方式
```bash
python3 00_整理记录/scripts/build_step13_submission_tables.py
```