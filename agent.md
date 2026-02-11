# AGENT.md — 政策三元组抽取与知识图谱推演任务说明

更新时间：2026-02-11（step6 Gold/IAA completed）

## 当前执行状态
- Step 1（领域 Schema 设计）：已完成
- Step 2（样本文档抽样与标注规范）：已完成
- Step 3（预处理与切分策略）：已完成
- Step 4（UIE 基线抽取 + 可导入性迭代优化）：已完成（达到良好阈值）
- Step 5（规则化归一与校验）：已完成（最新前缀 `step5_seq_step2_v2_rebind12_fixabcd`）
- Step 6（Gold/IAA 构建与一致性评测）：已完成（最新前缀 `step6_iter3_fixabcd`，全量门禁达标）
- 交付文件：
  - `00_整理记录/schema_v1.yaml`（v1.4，已修复枚举冲突并扩展工程参数适配）
  - `00_整理记录/schema_step1_readthrough_report.md`
  - `00_整理记录/schema_change_log.md`
  - `00_整理记录/policy_readthrough_profile.json`
  - `00_整理记录/policy_readthrough_summary.json`
  - `00_整理记录/step2_theme_sampling.json`
  - `00_整理记录/step2_theme_sampling.md`
  - `00_整理记录/step2_doccano_annotation_guideline.md`
  - `00_整理记录/step2_doccano_seed_doc_level.jsonl`
  - `00_整理记录/step2_doccano_seed_clause_level.jsonl`
  - `00_整理记录/step2_doccano_labeled_examples.jsonl`
  - `00_整理记录/scripts/build_step2_sampling.py`
  - `step2.md`
  - `00_整理记录/step3_input_manifest.json`
  - `00_整理记录/step3_document_corpus.jsonl`
  - `00_整理记录/step3_clause_corpus.jsonl`
  - `00_整理记录/step3_offset_map.jsonl`
  - `00_整理记录/step3_qc_report.json`
  - `00_整理记录/step3_qc_report.md`
  - `00_整理记录/step3_evaluation.md`
  - `00_整理记录/scripts/step3_preprocess_utils.py`
  - `00_整理记录/scripts/run_step3_preprocess.py`
  - `step3.md`
  - `00_整理记录/scripts/run_step4_uie_baseline.py`
  - `00_整理记录/step4_gpu_doc_doc_predictions.jsonl`
  - `00_整理记录/step4_gpu_doc_summary.json`
  - `00_整理记录/step4_gpu_clause_clause_predictions.jsonl`
  - `00_整理记录/step4_gpu_clause_summary.json`
  - `00_整理记录/step4_gpu_run.md`
  - `00_整理记录/step4_iter0_baseline_kb_score.json`
  - `00_整理记录/step4_iter1_v1_kb_score.json`
  - `00_整理记录/step4_iter2_v2_kb_score.json`
  - `00_整理记录/step4_iter3_v2plus_kb_score.json`
  - `00_整理记录/step4_iter3_v2plus_clause_predictions.jsonl`
  - `00_整理记录/step4_iter3_v2plus_doc_predictions.jsonl`
  - `00_整理记录/step4_iteration_scores.md`
  - `00_整理记录/scripts/step4_kb_postfill_optimize.py`
  - `00_整理记录/scripts/step4_kb_score.py`
  - `00_整理记录/scripts/build_step4_iteration_report.py`
  - `step4.md`
  - `00_整理记录/scripts/run_step5_normalize_validate.py`
  - `00_整理记录/step5_seq_step2_parameter_mentions.jsonl`
  - `00_整理记录/step5_seq_step2_parameter_definitions.jsonl`
  - `00_整理记录/step5_seq_step2_triples_spo.jsonl`
  - `00_整理记录/step5_seq_step2_validation_report.json`
  - `00_整理记录/step5_seq_step2_validation_report.md`
  - `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_parameter_mentions.jsonl`
  - `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_parameter_definitions.jsonl`
  - `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_triples_spo.jsonl`
  - `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_validation_report.json`
  - `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_validation_report.md`
  - `00_整理记录/step5_fixabcd_issueAtoD_eval.json`
  - `00_整理记录/tests/test_step5_normalizer.py`
  - `00_整理记录/scripts/run_step6_gold_iaa.py`
  - `00_整理记录/step6_gold_sample_v1.jsonl`
  - `00_整理记录/step6_gold_passA_labels.jsonl`
  - `00_整理记录/step6_gold_passB_labels.jsonl`
  - `00_整理记录/step6_gold_adjudicated.jsonl`
  - `00_整理记录/step6_iaa_report.json`
  - `00_整理记录/step6_iaa_report.md`
  - `00_整理记录/step6_iter3_fixabcd_gold_adjudicated.jsonl`
  - `00_整理记录/step6_iter3_fixabcd_iaa_report.json`
  - `00_整理记录/step6_iter3_fixabcd_iaa_report.md`
  - `00_整理记录/step6_fixabcd_eval.json`
  - `00_整理记录/step6_测评参数与计算口径.md`
  - `step5.md`
  - `step6.md`
- 说明：
  - Step 1 基于全量 151 份政策文本通读统计，不是抽样推断。
  - Step 2 在排除 `02_汇总拼接` 与压缩包目录后，对 147 份独立政策文本做主题抽样；每主题 8 份，去重样本池 38 份。

## 任务理解（共识）
目标是基于现有政策文本，构建可控、可评测的领域 Schema，并使用 Schema 驱动的统一信息抽取（UIE）+ 规则归一与校验，输出可入图的三元组与可计算的多跳结构，以支持政策推演。

核心要求：
- Schema 需要覆盖元信息（发布机构/发布日期/适用地区/适用对象）与机制/条款实体（分时、阶梯、差别电价、补贴条款、考核任务、技术路线）及其参数（峰谷时段、电价幅度、补贴标准、阈值条件等）。
- 抽取流程需可落地、可复现、可评测。
- 对硬参数做规则化归一、证据对齐、冲突检测。
- 输出既包含标准 SPO，也包含机制/条款实体化后的多跳结构。

## 数据范围（当前目录结构）
- 01_电价政策
  - 01_分时电价（35）
  - 02_阶梯与差别电价（37）
  - 03_综合与其他（9）
- 02_电能替代与清洁取暖
  - 01_政策文本（66）
  - 02_汇总拼接（4，uni*.txt，不建议直接抽取）
  - 03_原始压缩包（1）

当前状态：已完成去重与归档；未做 OCR、页眉页脚清洗；编码采用 UTF-8 strict + GBK fallback；`02_汇总拼接` 已在 schema 中定义预切分规则（按 `<h2>file:` 拆分后再抽取）。

## 主要输出（预期交付物）
- Schema 定义（JSON/YAML）：实体、关系、事件与参数字段
- 标注规范与样例（doccano 标签体系）
- UIE 推理/微调配置与脚本（PaddleNLP Taskflow/UIE）
- 规则化与校验模块（时间/金额/时段/比例等）
- 抽取结果：
  - 三元组（SPO）
  - 机制/条款实体化多跳结构
- 评测报告：实体/关系 F1、数值归一准确率、证据可回溯率

## 任务步骤拆分（执行顺序）
1. 领域 Schema 设计
   - 定义核心实体/关系/事件与参数字段
   - 明确层级与适用范围（国家/省/市）
   - 输出 Schema JSON/YAML 版本（已完成：`00_整理记录/schema_v1.yaml`，当前 v1.4）

2. 样本文档抽样与标注规范
   - 按主题抽样（分时/阶梯/差别/补贴/岸电/清洁取暖等）
   - 制定标注准则与示例（doccano）
   - 当前状态：已完成（`00_整理记录/step2_theme_sampling.json`、`00_整理记录/step2_doccano_annotation_guideline.md`）

3. 预处理与切分策略
   - 编码统一、段落切分、长文本滑窗
   - 先按 `<h2>file:` 拆分 uni*.txt 拼接文，再执行 clause 切分
   - 当前状态：已完成（offset 映射层与 QC 门禁已落地）

4. UIE 基线抽取
   - 使用 Schema prompt 做零样本推理
   - 产出初版结构化结果，识别误抽点
   - 当前状态：已完成 GPU 全量基线（317 doc + 2022 clause），并完成迭代优化（baseline->v1->v2->v2plus）

5. 规则化归一与校验
   - 正则/词典/单位解析器
   - 证据对齐（span 回溯）与一致性检查
   - 当前状态：已完成（最新 `rebind12_fixabcd` 已产出并通过门禁）

6. Gold/IAA 构建与一致性评测
   - 冻结 Step5 输入版本、分母口径与样本抽样规则
   - 生成机器辅助金标（双盲两遍）并进行自动仲裁
   - 输出 IAA 指标（kappa/F1/一致率）与误差簇分析
   - 当前状态：已完成（`step6_iter3_fixabcd_iaa_report.json` 显示 `all_targets_passed=true`）

7. 小样本微调与迭代
   - 基于标注数据微调 UIE
   - 对关键字段（时段/电价/补贴）强化
   - 当前状态：待开始（以 `step6_gold_adjudicated.jsonl` 为监督数据）

8. 三元组与多跳结构输出
   - 生成 SPO + 机制/条款实体化结构
   - 输出可入图格式（CSV/JSONL）

9. 评测与推演准备
   - 指标：实体/关系 F1、数值归一准确率、证据可回溯率
   - 时间有效性、政策层级与版本衔接校验

## v1.4 关键适配修正
- 修复 `table_row_clause` 输出与 `Clause.clause_type` 枚举不一致问题。
- 新增机制类型 `general_price_adjustment`，覆盖“降价/下调/一般性电价调整”文本。
- 扩展参数类型与单位：
  - 参数：`area_subsidy_amount`、`capacity_threshold`、`tonnage_threshold`
  - 单位：`yuan_per_sqm`、`kw/mw/kva`、`ton/ton_per_hour/deadweight_ton`、`sqm`
- 新增规则化模块：面积/容量/吨位归一规则 + 参数类型映射规则。
- 新增质量门禁：`clause_type_enum_alignment`、`compiled_file_split_consistency`。

## 四项优先改进执行状态
- 优先1（document-level 文件名补偿+冲突仲裁）：已实现并落地到 `document_level_compensation_rules`。
- 优先2（clause-level 任务型条款结构化）：已实现，新增 `task_subject/task_action/task_deadline/task_assessment` 字段。
- 优先3（no_parameter_top25 首批验证）：已生成首批标注集并输出弱数值机制识别评估。
- 优先4（postprocess 归一顺序单测）：已增加单测并通过。

## 新增执行文件
- `00_整理记录/scripts/policy_extraction_utils.py`
- `00_整理记录/scripts/run_priority_updates.py`
- `00_整理记录/scripts/build_step2_sampling.py`
- `00_整理记录/tests/test_postprocess_normalizer.py`
- `00_整理记录/schema_v1_4_fit_check_after_priority_updates.json`
- `00_整理记录/schema_v1_4_fit_check_after_priority_updates.md`
- `00_整理记录/step2_theme_sampling.json`
- `00_整理记录/step2_theme_sampling.md`
- `00_整理记录/step2_doccano_annotation_guideline.md`
- `00_整理记录/step2_doccano_seed_doc_level.jsonl`
- `00_整理记录/step2_doccano_seed_clause_level.jsonl`
- `00_整理记录/step2_doccano_labeled_examples.jsonl`
- `step2.md`

## 风险与控制点
- 长文本切分可能导致关系断裂，需要跨句合并策略
- 数值抽取易受单位与口径影响，必须规则归一
- 政策层级与时效关系需显式建模，避免推演错误
