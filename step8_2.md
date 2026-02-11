# Step8.2：图查询样例包与冲突信号化

更新时间：2026-02-11
状态：已完成（门禁达标，可进入 Step9）

## 1. 功能定义（固定口径）
Step8.2 只做两件事：

1) 产出一套图查询与多跳样例包（体现可推演能力）
- 以 `strict_high` 为主图，`strict_all` 为补充。
- 产出 10~20 条固定查询模板（建议先做 12 条）：
  - `Policy -> contains_clause -> clause_supports_mechanism -> Mechanism`
  - `Mechanism -> mechanism_has_parameter_definition -> Definition -> Mention -> Clause -> Policy`
  - 按 `region / target_group / time_window / threshold` 做过滤与聚合
  - 同机制跨条款参数冲突定位（结合 `conflicts.jsonl`）

2) 把冲突升级为可用信号（不只是日志）
- 给每条最终保留事实边增加：
  - `conflict_count`
  - `alt_candidates_count`
  - `conflict_type`（`dedup_aggregation` / `semantic_collision`）
  - `risk_level`（`low / medium / high`）
- 供下游检索/推演做置信提示：高冲突事实默认降权或仅检索展示。

## 2. 执行思路
### 2.1 查询样例包
- 输入：`graph_pkg/step8_iter1/strict_high/*`、`graph_pkg/step8_iter1/strict_all/*`
- 输出：
  - `query_pack.cql`（固定模板）
  - `query_examples.json`（每条模板的参数示例）
  - `query_pack_readme.md`（用途、输入、输出解释）

### 2.2 冲突信号化
- 输入：`graph_pkg/step8_iter1/conflicts.jsonl`、`strict_high/edges.csv`、`strict_all/edges.csv`
- 输出：
  - `edge_signals.csv`（按边补充冲突信号）
  - `conflict_signal_report.json`（分布与阈值统计）

### 2.3 不做事项
- 不重跑 Step4/5/6/7。
- 不改 schema_v1.4 主体定义。
- 不将 `strict_all` 直接并入主图推演路径。

## 3. 产出清单（Step8.2 完成标准）
- `00_整理记录/graph_pkg/step8_2_iter1/query_pack.cql`
- `00_整理记录/graph_pkg/step8_2_iter1/query_examples.json`
- `00_整理记录/graph_pkg/step8_2_iter1/query_pack_readme.md`
- `00_整理记录/graph_pkg/step8_2_iter1/edge_signals.csv`
- `00_整理记录/graph_pkg/step8_2_iter1/conflict_signal_report.json`
- `00_整理记录/graph_pkg/step8_2_iter1/step8_2_eval_report.json`

## 4. 评测指标（Step8.2 门禁）
### A. 查询样例包指标
- `query_template_count`：10~20（目标=12）
- `query_execution_success_rate`：100%
- `core_path_coverage`：100%
  - 必须覆盖 `Policy-Clause-Mechanism-Definition-Mention` 主链与反查链
- `parameterized_example_coverage`：100%
  - 每个模板至少 1 组可执行参数样例

### B. 冲突信号指标
- `edge_signal_coverage_on_strict_high`：100%
  - 每条主图边都要有 `conflict_count / alt_candidates_count / risk_level`
- `conflict_type_classification_coverage`：>=95%
  - 冲突记录可归类为 `dedup_aggregation` 或 `semantic_collision`
- `high_risk_edge_ratio`：监控指标（不设硬阈值，作为 Step9 风险输入）

### C. 可复现指标
- `deterministic_pack_rebuild_match`：100%
  - 同输入同参数二次生成，文件哈希一致

## 5. 进入 Step9 的条件
- Step8.2 所有硬门禁（A/B/C）通过。
- 查询样例包可直接用于 Step9 的评测与推演准备。

## 6. 本轮结果（step8_2_iter1）
- 产出目录：`00_整理记录/graph_pkg/step8_2_iter1`
- 评测报告：`00_整理记录/graph_pkg/step8_2_iter1/step8_2_eval_report.json`
- 指标结果：
  - `query_template_count = 12`
  - `query_execution_success_rate = 1.0`
  - `core_path_coverage = 1.0`
  - `parameterized_example_coverage = 1.0`
  - `edge_signal_coverage_on_strict_high = 1.0`
  - `conflict_type_classification_coverage = 1.0`
  - `deterministic_pack_rebuild_match = true`
  - `all_targets_passed = true`
