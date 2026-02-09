# Step3 评分与评估（满分 100）

时间：2026-02-09

## 总分
- **94 / 100**

## 评分维度

### 1) 审计链与可复现性（30分）
- 得分：30/30
- 依据：
  - `step3_input_manifest.json` 已记录 `encoding_used/preprocess_version/git_commit/pipeline_params_hash`
  - `doc_id` 与 `doc_instance_id` 规则明确且可复现
  - 输入冻结与源文件哈希齐全

### 2) Offset 映射与证据回溯（30分）
- 得分：30/30
- 依据：
  - 已生成 `step3_offset_map.jsonl`
  - `docs_with_mismatch=0`
  - `mismatch_char_total=0`
  - `all_clause_span_valid=true`

### 3) 切分质量与结构约束（25分）
- 得分：21/25
- 依据：
  - `docs_without_clause=0`
  - clause 长度约束满足（min=20, max=400）
  - 表格兜底生效（`table_row_clause=130`）
- 扣分点：
  - `other` 类型比例仍高（527/2022），说明 clause 类型启发式还可继续优化。

### 4) 产物可用性（15分）
- 得分：13/15
- 依据：
  - document/clause 两套语料已输出且可解析
  - 可直接作为 Step4 UIE 输入
- 扣分点：
  - 还未加入“基于人工样本的切分准确率”评测（当前主要是结构与一致性门禁）。

## 结论
- Step3 已达到“可进入 Step4”的工程就绪状态，且审计链完整、offset 安全。
- 当前主要改进方向是：降低 `other` clause 占比，提高条款类型预分类可解释性。

## 建议的下一步优化（进入 Step4 前可并行）
1. 对 `other` clause 做 100 条人工抽检，细化规则把一部分归入 `scope_rule/execution_rule/task_assessment`。
2. 增加“切分准确率小样本评估”（人工金标对比），形成可论文引用的误差项。
3. 在 Step4 抽取日志里保留 `clause_id + raw_span`，实现端到端证据追溯闭环。
