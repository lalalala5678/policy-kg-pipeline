# STEP1-STEP9 成果测评创新总览

更新时间：2026-02-11  
用途：交付/论文写作/外部评审统一材料

## Step1 领域 Schema 设计
- 主要产出：
  - `结果文件夹/schema_v1.yaml`
  - `00_整理记录/policy_readthrough_profile.json`
  - `00_整理记录/policy_readthrough_summary.json`
  - `00_整理记录/schema_change_log.md`
- 核心测评数据（来自 `policy_readthrough_summary.json`）：
  - 文件数：`151`
  - 编码识别：`utf-8=151`, `gbk=0`
  - 含机构元信息文档：`72`
  - 含日期元信息文档：`128`
  - 含区域范围文档：`140`
  - 含对象范围文档：`140`
- 创新点：
  - 采用“全量阅读驱动 Schema”而非先验拍脑袋建模。
  - 引入机制+参数并行的可计算结构，为后续多跳推演留接口。

## Step2 样本抽样与标注规范
- 主要产出：
  - `00_整理记录/step2_theme_sampling.json`
  - `00_整理记录/step2_doccano_annotation_guideline.md`
  - `00_整理记录/step2_doccano_seed_doc_level.jsonl`
  - `00_整理记录/step2_doccano_seed_clause_level.jsonl`
- 核心测评数据：
  - 有效政策语料范围：`147`（`step2_theme_sampling.json`）
  - 主题数：`6`（分时/阶梯/差别/补贴/岸电/清洁取暖）
  - 每主题抽样：`8`（共 6 组 `sampled_count=8`）
  - 去重标注池文档：`38`（`annotation_pool_union.doc_count`）
  - doc 级种子：`38`；clause 级种子：`42`；弱标注示例：`12`
- 创新点：
  - 主题分层抽样 + 年份覆盖，避免样本集中在单一政策体裁。
  - doc 与 clause 双层标注准则并行设计，直接对接 Step4/Step5。

## Step3 预处理与切分策略
- 主要产出：
  - `00_整理记录/step3_input_manifest.json`
  - `00_整理记录/step3_document_corpus.jsonl`
  - `00_整理记录/step3_clause_corpus.jsonl`
  - `00_整理记录/step3_offset_map.jsonl`
  - `00_整理记录/step3_qc_report.json`
- 核心测评数据（来自 `step3_qc_report.json`）：
  - 源文件：`151`
  - 拆分后文档单元：`317`
  - 条款数：`2022`
  - offset 映射 mismatch：`0`
  - 非法 clause span：`0`
  - 质量门禁：`overall_pass=true`
- 创新点：
  - 建立 clean/raw 双向 offset 映射，确保证据可回溯。
  - 对拼接文 `<h2>file:` 先切块再条款切分，避免文档边界污染。

## Step4 UIE 基线抽取与入图可用性优化
- 主要产出：
  - `00_整理记录/step4_iter3_v2plus_clause_predictions.jsonl`
  - `00_整理记录/step4_iter3_v2plus_doc_predictions.jsonl`
  - `00_整理记录/step4_iter3_v2plus_kb_score.json`
  - `00_整理记录/step4_iteration_scores.json`
- 核心测评数据（来自 `step4_iter3_v2plus_kb_score.json`）：
  - 总分：`76.332`（阈值 75，达标）
  - `mechanism_non_empty_rate = 0.781405`
  - `raw_non_empty_rate = 0.290307`
  - `strict_triplet_ready_rate = 0.251731`
  - `raw_value_span_valid_rate = 1.0`
  - `mechanism_evidence_rate = 1.0`
- 创新点：
  - UIE 抽取 + 规则后填充联合架构，目标从“抽到”转为“可入图”。
  - 引入参数绑定字段（`param_bind_mechanism`, `bind_reason`）降低孤立值。

## Step5 规则化归一与校验
- 主要产出：
  - `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_mentions.jsonl`
  - `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_definitions.jsonl`
  - `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_triples_spo.jsonl`
  - `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_validation_report.json`
- 核心测评数据（来自该 validation report）：
  - mention：`1141`；definition：`339`；triple：`3176`
  - `normalization_matched_rate = 0.945662`
  - `mechanism_bound_rate_valid_numeric = 1.0`
  - `strict_high_rate_valid_numeric = 0.848934`
  - `local_supported_rate_valid_numeric = 0.895273`
  - `all_targets_passed = true`
- 创新点：
  - 固化三套分母口径（all_clause / valid_all / valid_numeric），防止指标漂移。
  - clause 级候选 + mention 级绑定两阶段纠偏，配合负域词典抑制错绑。
  - strict_all/strict_high 双轨门禁，兼顾召回池与高置信主集。

## Step6 Gold/IAA 双盲评测
- 主要产出：
  - `00_整理记录/step6_iter4_fixabcd_plus_gold_adjudicated.jsonl`
  - `00_整理记录/step6_iter4_fixabcd_plus_iaa_report.json`
  - `00_整理记录/step6_iter4_fixabcd_plus_gold_sampling_plan.json`
- 核心测评数据（来自 `step6_iter4_fixabcd_plus_iaa_report.json`）：
  - 样本总量：`300`；strict 样本：`214`；hard case：`157`
  - `kappa_mechanism = 0.987997`
  - `kappa_param_type = 1.0`
  - `mechanism_precision_on_valid_numeric = 261/274 = 0.952555`
  - `normalization_precision_on_valid_numeric = 277/278 = 0.996403`
  - `strict_high_precision = 213/214 = 0.995327`
  - `all_targets_passed = true`
- 创新点：
  - 固定抽样计划 + 双盲复核 + adjudication 流程可复跑。
  - 将“高危错误桶”并入门禁，避免只看平均分掩盖灾难性错误。

## Step7 规则增量优化与门禁复测
- 主要产出：
  - `00_整理记录/step7_iter3_unitfix_timeunit_thr060_validation_report.json`
  - `00_整理记录/step7_iter3b_unitfix_timeunit_thr060_iaa_report.json`
  - `00_整理记录/step7_gate_iter3_final.json`
- 核心测评数据（来自 `step7_gate_iter3_final.json`）：
  - `normalization_matched_on_mentions = 1119/1141 = 0.980719`
  - `strict_high_on_valid_numeric = 952/1119 = 0.850760`
  - `mechanism_bound_on_valid_numeric = 1119/1119 = 1.0`
  - `kappa_mechanism = 0.991969`
  - `kappa_param_type = 1.0`
  - `mechanism_precision_on_valid_numeric = 271/283 = 0.957597`
  - `normalization_precision_on_valid_numeric = 287/287 = 1.0`
  - `strict_high_precision = 220/221 = 0.995475`
  - `all_targets_passed = true`
- 创新点：
  - 修复单位串线与 time_point/time_window 语义对齐，减少类型漂移。
  - 统一 Step5+Step6 联合门禁，保证优化不以牺牲精度换召回。

## Step7b 固定 Gold 门禁增益实验
- 主要产出：
  - `00_整理记录/step7b_iterB_rulefix_validation_report.json`
  - `00_整理记录/step7b_iterB_rulefix_iaa_report.json`
  - `00_整理记录/step7b_iterB_rulefix_gate.json`
- 核心测评数据（来自 `step7b_iterB_rulefix_gate.json`）：
  - `all_targets_passed = true`
  - `strict_high_tp_delta = +2`（220 -> 222）
  - `fixed_gold_mechanism_precision = 0.958904`
  - `fixed_gold_normalization_precision = 0.993127`
  - `fixed_gold_strict_high_precision = 0.995516`
- 创新点：
  - 使用“硬门槛 + 增益门槛”双判据，既防退化又要求可验证增益。
  - 固定 Gold 口径对比，避免分母变化导致的假提升。

## Step8 双轨图包导出与验收
- 主要产出：
  - `结果文件夹/step8_iter1/`（主包）
  - `结果文件夹/step8_iter1_replay/`（重放包）
  - `结果文件夹/step8_iter1/validation_report.json`
  - `结果文件夹/step8_iter1/stats.json`
- 核心测评数据：
  - `all_targets_passed = true`
  - `deterministic_replay_match = true`
  - strict_high：`nodes=2494, edges=4868, triples=4868`
  - strict_all：`nodes=2892, edges=5742, triples=5742`
  - 拒收统计：
    - strict_high：`186`（`E_STRICT_FILTER=167`, `E_FK_MISSING=19`）
    - strict_all：`19`（`E_FK_MISSING=19`）
- 创新点：
  - 双轨包（高精主图 + 高召回扩展图）同时交付。
  - manifest+hash+replay 形成可复现与可回滚链路。

## Step8.2 查询样例包与冲突信号化
- 主要产出：
  - `结果文件夹/step8_2_iter1/query_pack.cql`
  - `结果文件夹/step8_2_iter1/query_examples.json`
  - `结果文件夹/step8_2_iter1/edge_signals.csv`
  - `结果文件夹/step8_2_iter1/conflict_signal_report.json`
  - `结果文件夹/step8_2_iter1/step8_2_eval_report.json`
- 核心测评数据（来自 `step8_2_eval_report.json`）：
  - `query_template_count = 12`
  - `query_execution_success_rate = 1.0`
  - `core_path_coverage = 1.0`
  - `parameterized_example_coverage = 1.0`
  - `edge_signal_coverage_on_strict_high = 1.0`
  - `conflict_type_classification_coverage = 1.0`
  - `deterministic_pack_rebuild_match = true`
  - `all_targets_passed = true`
- 创新点：
  - 将冲突日志转为可消费的边级风险特征（可直接用于检索排序与推演降权）。
  - 固化多跳查询模板，形成可复跑的推演评测入口。

## Step9 评测与推演准备（当前状态）
- 当前状态：待执行
- 建议输入：
  - 主图：`结果文件夹/step8_iter1/strict_high/nodes.csv` + `结果文件夹/step8_iter1/strict_high/edges.csv`
  - 扩展图：`结果文件夹/step8_iter1/strict_all/nodes.csv` + `结果文件夹/step8_iter1/strict_all/edges.csv`
  - 查询模板：`结果文件夹/step8_2_iter1/query_pack.cql`
  - 风险信号：`结果文件夹/step8_2_iter1/edge_signals.csv`
- 目标指标建议：
  - 导入成功率 `=100%`
  - 查询模板执行成功率 `=100%`
  - 核心多跳路径覆盖率 `=100%`
  - 结果可追溯率 `=100%`

## 附：当前交付主入口
- `结果文件夹/README_使用指南.md`
- `结果文件夹/STEP1-STEP9_成果测评创新总览.md`（本文）
