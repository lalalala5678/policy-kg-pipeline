# Step8：双轨图包导出与工程验收

更新时间：2026-02-11

## 目标
- 将 Step7b 抽取结果导出为可复现、可回滚、可审计的图谱数据包。
- 形成双轨产物：
  - `strict_high`：高置信主图（用于推演）
  - `strict_all`：扩展图（用于召回/复核）

## 已完成内容
- 导出脚本：`00_整理记录/scripts/run_step8_export_graph.py`
- 校验脚本：`00_整理记录/scripts/validate_step8_pkg.py`
- 产物包：`00_整理记录/graph_pkg/step8_iter1`
  - `manifest.json`、`config.json`、`stats.json`
  - `rejects.jsonl`、`conflicts.jsonl`
  - `strict_high/nodes.csv`、`strict_high/edges.csv`、`strict_high/triples_spo.jsonl`
  - `strict_all/nodes.csv`、`strict_all/edges.csv`、`strict_all/triples_spo.jsonl`

## Step8 验收结论
- `all_targets_passed = true`
- `deterministic_replay_match = true`
- `strict_high` 与 `strict_all` 在 PK/FK/schema/dry-run 等工程门禁均通过。

## 与 Step8.2 的边界
- Step8 负责“数据包导出与工程验收”。
- Step8.2 负责“查询样例包与冲突信号化”（不重跑抽取，不改主干图结构）。

