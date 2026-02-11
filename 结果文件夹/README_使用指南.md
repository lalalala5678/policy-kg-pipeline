# 结果文件夹使用指南

## 1. 本目录是什么
`结果文件夹` 汇总了当前可用于 Neo4j 入图、查询样例、冲突信号分析、质量校验与复现实验的全部核心产物。

建议先读：
- `STEP1-STEP9_成果测评创新总览.md`（按步骤查看产出、测评数据、创新点）

当前主要包含 4 组内容：
- `step8_iter1`：主导出包（strict_high + strict_all）
- `step8_iter1_replay`：同配置重放包（用于一致性/复现核验）
- `step8_2_iter1`：查询模板与冲突信号增强包
- `schema_v1.yaml`：图谱 Schema 定义

---

## 2. 目录与文件用途

### 2.1 `schema_v1.yaml`
- 用途：定义实体类型、关系类型、字段语义，是所有导出与评测口径的结构依据。
- 典型使用：给第三方 AI / 论文 / 工程同事说明图结构时优先提供此文件。

### 2.2 `step8_iter1/`（主导出包）
- `strict_high/nodes.csv`：高置信主图节点（推荐优先入 Neo4j）
- `strict_high/edges.csv`：高置信主图边（推荐优先入 Neo4j）
- `strict_high/triples_spo.jsonl`：高置信 SPO 交换格式（调试/审阅）
- `strict_all/nodes.csv`：扩展召回节点（包含更多候选）
- `strict_all/edges.csv`：扩展召回边（用于检索补充/复核）
- `strict_all/triples_spo.jsonl`：扩展召回 SPO 交换格式
- `manifest.json`：导出包索引、行数与 sha256、版本信息
- `config.json`：本次导出冻结配置
- `stats.json`：节点/边/拒收统计
- `validation_report.json`：结构化校验结果（FK/PK/单位/一致性等）
- `rejects.jsonl`：拒收明细（含拒收原因码）
- `conflicts.jsonl`：冲突明细（可解释冲突记录）

### 2.3 `step8_iter1_replay/`（复现实验包）
- 与 `step8_iter1` 同结构。
- 用途：验证同输入同配置是否可重建一致结果，支撑复现性结论。
- 典型使用：做论文附录或工程回归时与 `step8_iter1` 对比。

### 2.4 `step8_2_iter1/`（查询与冲突信号包）
- `query_pack.cql`：固定 Neo4j/Cypher 查询模板（多跳路径、冲突定位、回填候选）
- `query_examples.json`：模板参数示例与执行预览
- `query_pack_readme.md`：查询包说明
- `edge_signals.csv`：边级信号（如 `conflict_count`、`alt_candidates_count`、`risk_level`）
- `conflict_signal_report.json`：冲突信号汇总统计
- `step8_2_eval_report.json`：Step8.2 评测结果与达标状态

---

## 3. Neo4j 入图建议

### 3.1 推荐入图顺序
1. 先导入高置信主图（生产/推演优先）  
   - `step8_iter1/strict_high/nodes.csv`
   - `step8_iter1/strict_high/edges.csv`
2. 再按需导入扩展召回图（检索增强/人工复核）  
   - `step8_iter1/strict_all/nodes.csv`
   - `step8_iter1/strict_all/edges.csv`
3. 若需要风险提示，额外加载  
   - `step8_2_iter1/edge_signals.csv`

### 3.2 strict_high 与 strict_all 如何选
- `strict_high`：精度优先，适合政策推演与正式分析。
- `strict_all`：召回优先，适合发现候选与补充证据；建议结合 `edge_signals.csv` 使用。

---

## 4. 给第三方 AI/评审最小投喂集

若只想让外部模型快速评估能力，建议最小组合：
1. `schema_v1.yaml`
2. `step8_iter1/strict_high/nodes.csv`
3. `step8_iter1/strict_high/edges.csv`
4. `step8_iter1/manifest.json`
5. `step8_iter1/stats.json`

若要评估冲突治理与多跳查询能力，再追加：
6. `step8_iter1/conflicts.jsonl`
7. `step8_2_iter1/edge_signals.csv`
8. `step8_2_iter1/query_pack.cql`

---

## 5. 快速自检清单（导入前）
- `manifest.json` 中 `row_count` 与文件行数一致。
- `validation_report.json` 中关键门禁为通过状态。
- 先跑 `strict_high` 导入与查询，再决定是否叠加 `strict_all`。
- 若出现语义冲突，优先查看 `conflicts.jsonl` 与 `edge_signals.csv`。

---

## 6. 当前版本标识（便于追踪）
- 主导出运行：`step8_iter1`
- Schema 版本：`schema_v1.4`（见 `manifest.json`）
- 抽取版本：`step7b_iterB_rulefix`（见 `manifest.json`）
- Step8.2 评测：`step8_2_eval_report.json` 中 `all_targets_passed = true`
