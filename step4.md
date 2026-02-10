# Step4（知识图谱可导入优化）技术说明与创新点

更新时间：2026-02-09

## 1. Step4 的目标
Step4 的目标不是追求模型推理速度，而是提升三元组入图前的“可导入性”和“可追溯性”：
- 字段结构完整（schema key 完整）
- 证据可回指（span 与关键词证据有效）
- 条款可计算（机制、条款类型、参数、任务字段可组合）
- 可量化评分（每轮都可复现比较）

评分口径见：`00_整理记录/scripts/step4_kb_score.py`

## 2. Step4 实际使用的技术

### 2.1 两阶段 UIE 基线抽取（doc-level + clause-level）
脚本：`00_整理记录/scripts/run_step4_uie_baseline.py`

- 使用 PaddleNLP `Taskflow("information_extraction")`
- 文档级字段抽取：`title/document_no/issue_date/org_name/...`
- 条款级字段抽取：`mechanism_type/clause_type/raw_value/raw_unit/...`
- 支持 GPU/CPU 自动选择、批处理、输入长度截断、最小置信度过滤
- 批失败后自动退化到单条重试，避免整批丢失

### 2.2 规则后处理回填（Postfill v1/v2）
脚本：`00_整理记录/scripts/step4_kb_postfill_optimize.py`

对 UIE 结果做结构化补强，核心逻辑：
- `A1`：`clause_type` 空值由 Step3 的 `clause_type_prelim` 回填
- `A2`：`mechanism_type` 先用机制模式词规则回填；未命中再按 `clause_type_prelim` 做 fallback
- `A3`：参数值与单位正则补抽（高精度优先），并补 `direction`
- 任务型条款字段补抽：`task_subject/task_action/task_deadline/task_assessment`
- 参数挂靠机制：输出 `param_bind_mechanism` 与 `bind_reason`
- 文档级补偿：标题回填、日期/文号正则补偿、机构名标题前缀抽取

### 2.3 证据门禁与可导入性评分
脚本：`00_整理记录/scripts/step4_kb_score.py`

- `raw_value` 做 span 严格校验：`text[start:end] == raw_value`
- `mechanism_type` 证据校验：
  - 正常 span 命中通过
  - `rule_pattern` 使用 `postfill.mechanism_keyword(+start/end)` 作为证据
  - `fallback_clause_type*` 允许继承 Step3 条款分类证据
- 评分仅针对 KB 可导入性（不含性能）：
  - `structure_score(20)`、`evidence_score(20)`、`doc_score(15)`、`clause_score(45)`

### 2.4 迭代评估闭环
脚本：`00_整理记录/scripts/build_step4_iteration_report.py`

- 每轮产出 `*_kb_score.json` 与 `*_kb_score.md`
- 汇总 `iter0~iter3` 到统一对比报表
- 达标阈值：`good_threshold=75`

## 3. Step4 的创新点（已落地、可复现）

### 创新点 1：UIE + 规则后处理的“可计算优先”混合抽取
不是单纯追求 UIE 字段命中率，而是围绕入图需求，把机制、条款类型、参数和任务字段做联合补强，直接服务三元组生成。

### 创新点 2：机制证据双通道校验
`mechanism_type` 不只依赖 UIE span，还支持规则关键词证据和条款分类继承证据，兼顾召回与可审计性。

### 创新点 3：参数挂靠机制显式化
引入 `param_bind_mechanism` 与 `bind_reason`，把“参数出现”变成“参数属于哪个机制”的显式结构，减少孤立参数。

### 创新点 4：任务型条款结构化
对弱数值条款补抽任务四元字段（主体/动作/期限/考核），提升“无数值但有政策动作”的可计算性。

### 创新点 5：评分体系与优化策略绑定
将优化目标绑定到 `strict_triplet_ready_rate`、`param_bind_rate`、`task_ready_rate` 等可解释指标，支持逐轮定位瓶颈。

## 4. 迭代结果（真实结果）
来源：`00_整理记录/step4_iteration_scores.md`

- `iter0_baseline`：`39.482`
- `iter1_v1`：`56.896`
- `iter2_v2`：`72.817`
- `iter3_v2plus`：`76.332`（达标）

最终轮关键指标（`00_整理记录/step4_iter3_v2plus_kb_score.json`）：
- `mechanism_non_empty_rate = 0.781405`
- `clause_type_non_empty_rate = 1.0`
- `raw_non_empty_rate = 0.290307`
- `strict_triplet_ready_rate = 0.251731`
- `param_bind_rate = 0.88075`
- `task_ready_rate = 0.279426`
- `raw_value_span_valid_rate = 1.0`
- `mechanism_evidence_rate = 1.0`

## 5. 当前边界与后续方向
- 当前“达标”主要来自规则增强后的可导入性提升，不等于 UIE 监督微调已充分完成。
- `strict_triplet_ready_rate` 仍有提升空间（约 25.17%），下一步应在 Step5/Step6 针对高价值机制做标注与微调，重点压降 fallback 依赖比例。

