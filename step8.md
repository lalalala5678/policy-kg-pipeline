# Step8：入图库导出与工程验收

更新时间：2026-02-11

## 目标
- 将 Step7b 抽取结果导出为可复现、可回滚、可审计的图谱数据包。
- 采用双轨导出：
  - `strict_high`：高置信主图（用于政策推演）
  - `strict_all`：扩展图（用于召回和复核）

## 实现
- 新增导出脚本：`00_整理记录/scripts/run_step8_export_graph.py`
  - 输入：`step7b_iterB_rulefix_parameter_mentions/definitions` + `step3_clause_corpus`
  - 输出：`00_整理记录/graph_pkg/step8_iter1`
  - 产物：
    - `manifest.json`、`config.json`、`stats.json`
    - `rejects.jsonl`（拒收原因码）
    - `conflicts.jsonl`（冲突聚合解释）
    - `strict_high/nodes.csv`、`strict_high/edges.csv`、`strict_high/triples_spo.jsonl`
    - `strict_all/nodes.csv`、`strict_all/edges.csv`、`strict_all/triples_spo.jsonl`
- 新增校验脚本：`00_整理记录/scripts/validate_step8_pkg.py`
  - 校验项：
    - `PK` 唯一性（nodes/edges）
    - `FK` 完整性
    - schema 关系约束一致性
    - `strict_high` 证据锚点完整性
    - `strict_high` 单位合法性（canonical unit）
    - 导入 dry-run 模拟可通过
    - 冲突解释完整
    - 重复导出一致性（对比 replay 包）

## 关键设计口径
- `strict_high` 以 Step5/Step6 裁判结果为准，不用 `confidence>=阈值` 替代。
- 主图默认 clause 级事实键，避免跨条款误合并。
- 同 fact 重复证据采用 `evidence_anchors` 聚合，并记录冲突处理日志。
- 输出采用固定排序 + 固定序列化，保证可重复导出一致。

## 测评结果（step8_iter1）
- 主结论：`all_targets_passed = true`
- 重复导出一致性：`deterministic_replay_match = true`
- 结构校验：
  - `strict_high`：PK/FK/schema/evidence/unit/dry-run 全通过
  - `strict_all`：PK/FK/schema/dry-run 全通过
- 规模：
  - `strict_high`：`nodes=2494`，`edges=4868`
  - `strict_all`：`nodes=2892`，`edges=5742`
- 说明：
  - `rejects.jsonl` 共 205 条（含 strict 过滤和缺失外键）
  - `conflicts.jsonl` 共 3929 条（均为同键聚合证据，已保留解释）

## 核心结果文件
- 包目录：`00_整理记录/graph_pkg/step8_iter1`
- 验证报告：`00_整理记录/graph_pkg/step8_iter1/validation_report.json`
