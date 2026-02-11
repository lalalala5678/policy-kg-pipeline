# Step8：双轨图包导出与工程验收

更新时间：2026-02-11

## 1. 目标
- 将 Step7b 的结构化结果导出为可直接入图、可复现、可审计的数据包。
- 形成双轨产物：
  - `strict_high`：高置信主图（用于推演与正式分析）
  - `strict_all`：扩展召回图（用于补充检索与复核）

## 2. 输入与脚本
- 主要输入：
  - `00_整理记录/step7b_iterB_rulefix_parameter_mentions.jsonl`
  - `00_整理记录/step7b_iterB_rulefix_parameter_definitions.jsonl`
  - `00_整理记录/step3_clause_corpus.jsonl`
- 主要脚本：
  - `00_整理记录/scripts/run_step8_export_graph.py`
  - `00_整理记录/scripts/validate_step8_pkg.py`

## 3. 输出目录（当前有效）
- `结果文件夹/step8_iter1/`
- `结果文件夹/step8_iter1_replay/`（同配置重放）

主要文件：
- `manifest.json`、`config.json`、`stats.json`
- `validation_report.json`
- `rejects.jsonl`、`conflicts.jsonl`
- `strict_high/nodes.csv`、`strict_high/edges.csv`、`strict_high/triples_spo.jsonl`
- `strict_all/nodes.csv`、`strict_all/edges.csv`、`strict_all/triples_spo.jsonl`

## 4. 工程验收结果
来源：`结果文件夹/step8_iter1/validation_report.json`
- `all_targets_passed = true`
- `deterministic_replay_match = true`
- `conflict_explainability = true`
- `strict_high` 与 `strict_all` 在 PK/FK/schema/evidence/unit/dry-run 均通过

来源：`结果文件夹/step8_iter1/stats.json`
- strict_high：`nodes=2494, edges=4868, triples=4868`
- strict_all：`nodes=2892, edges=5742, triples=5742`
- strict_high 拒收：`186`（`E_STRICT_FILTER=167`, `E_FK_MISSING=19`）
- strict_all 拒收：`19`（`E_FK_MISSING=19`）

## 5. Step8 创新点
- 双轨导出机制：同源数据同时支撑高精推演与高召回复核。
- 确定性打包：manifest 哈希与 replay 一致性校验支持可复现研究。
- 冲突与拒收显式化：通过 `conflicts.jsonl` 与 `rejects.jsonl` 保持可解释治理链。
- 工程门禁前置：在入图库前完成结构、外键、单位、证据的完整性验证。

## 6. 与 Step8.2 的边界
- Step8 负责：数据包构建与工程验收。
- Step8.2 负责：查询样例包与冲突信号升级，不改动 Step8 主包结构。
