# Schema v1.4 体检报告

生成时间：2026-02-09 18:08:29
检查对象：00_整理记录/schema_v1.yaml
语料规模：151 份政策文本

## 1. 结论（可直接用于阶段汇报）
- 结构一致性：11/11 通过（100%），v1.4 关键修正项全部落地。
- 数据适配度：机制相关文本覆盖率 96.03%（145/151），参数相关文本覆盖率 70.2%（106/151）。
- 汇总拼接文本预切分可执行：4/4 文件含 <h2>file: 锚点，预计可拆分子文档 170 段。
- 综合评价：可进入 Step2（标注规范 + UIE 基线），但建议先补充“文号抽取策略”和“非数值型任务类条款参数化策略”。

## 2. v1.4 一致性门禁检查
- PASS: schema_version_1_4
- PASS: has_pre_ingestion_split
- PASS: has_general_price_adjustment
- PASS: clause_enum_has_table_row_clause
- PASS: segmentation_emit_table_row_clause
- PASS: has_new_param_types
- PASS: has_new_norm_units
- PASS: has_parameter_type_mapping_rules
- PASS: has_gate_clause_type_enum_alignment
- PASS: has_gate_compiled_file_split
- PASS: has_alias_yuan_per_degree

## 3. 关键覆盖率（全量151份）
### 3.1 元信息与机制
- has_issue_date: 83.44%（126）
- has_org: 46.36%（70）
- has_region: 96.69%（146）
- has_target: 88.08%（133）
- has_doc_no: 7.95%（12）
- mech_tou: 37.75%（57）
- mech_tier: 31.13%（47）
- mech_diff: 14.57%（22）
- mech_general_price_adjustment: 14.57%（22）
- mech_subsidy: 22.52%（34）
- mech_task: 39.74%（60）
- mech_tech: 31.13%（47）

### 3.2 参数类型信号（含 v1.4 新增）
- param_time_window: 17.88%（27）
- param_price_value_like: 29.8%（45）
- param_percent: 39.74%（60）
- param_threshold_kwh: 32.45%（49）
- param_area_subsidy_amount_like: 3.31%（5）
- param_capacity_threshold_like: 18.54%（28）
- param_tonnage_threshold_like: 7.28%（11）

## 4. 风险样本（用于 Step2 标注集优先抽样）
- 无机制关键词文本：6 份（示例见 JSON）。
- 无参数关键词文本：25 份（多为规划/意见/任务类文本）。
- 元信息较弱文本：23 份（适合加入文件名补偿规则）。

## 5. 建议的下一步（按优先级）
- 优先1：在 document-level 抽取中加入文件名补偿策略（issue_date/doc_type/document_no 候选）并做冲突仲裁。
- 优先2：在 clause-level 增加“任务型条款”结构化字段（主体/动作/期限/考核）以提升无参数文本可计算性。
- 优先3：用 no_parameter_top25 作为首批标注集，验证 UIE 在弱数值文本下的机制召回与误抽率。
- 优先4：在 postprocess 中增加 元/度->yuan_per_kwh、万元/村、吨级 的优先归一顺序单测。
