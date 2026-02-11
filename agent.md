# AGENT.md — 政策三元组抽取与知识图谱推演任务说明

更新时间：2026-02-11（已更新至 Step8.2 完成）
最新提交：`08825ce`（step8: export dual-track graph package with deterministic validation）

## 当前执行状态（按步骤）
- Step 1（领域 Schema 设计）：已完成（`00_整理记录/schema_v1.yaml`，当前 v1.4）
- Step 2（样本文档抽样与标注规范）：已完成
- Step 3（预处理与切分策略）：已完成（offset 映射 + QC 门禁落地）
- Step 4（UIE 基线抽取）：已完成（317 doc + 2022 clause）
- Step 5（规则化归一与校验）：已完成并持续迭代优化
- Step 6（Gold/IAA 构建与一致性评测）：已完成（门禁达标）
- Step 7（规则增量优化与门禁复测）：已完成（门禁达标）
- Step 7b（固定 Gold 门禁增益实验）：已完成并通过（`all_targets_passed=true`）
- Step 8（三元组与多跳结构输出）：已完成（双轨入图库+工程验收通过）
- Step 8.2（图查询样例包 + 冲突信号化）：已完成（门禁达标）
- Step 9（评测与推演准备）：可开始

## 最新可用产物（建议作为下游输入）
- Step8 包目录：`00_整理记录/graph_pkg/step8_iter1`
- Step8 验证报告：`00_整理记录/graph_pkg/step8_iter1/validation_report.json`
- 三元组：`00_整理记录/step7b_iterB_rulefix_triples_spo.jsonl`
- 参数 mention：`00_整理记录/step7b_iterB_rulefix_parameter_mentions.jsonl`
- 参数定义：`00_整理记录/step7b_iterB_rulefix_parameter_definitions.jsonl`
- Step5 质量报告：`00_整理记录/step7b_iterB_rulefix_validation_report.json`
- Step6/IAA 报告：`00_整理记录/step7b_iterB_rulefix_iaa_report.json`
- Step7b 门禁报告：`00_整理记录/step7b_iterB_rulefix_gate.json`
- Step7b 说明文档：`step7b.md`

## Step7b 关键结果（用于 Step8 准入）
- 门禁结论：`all_targets_passed = true`
- 固定 Gold 增益：`strict_high_tp_delta = +2`（220 -> 222）
- 固定 Gold 精度：
  - `fixed_gold_mechanism_precision = 0.958904`
  - `fixed_gold_normalization_precision = 0.993127`
  - `fixed_gold_strict_high_precision = 0.995516`
- Step5 关键率：
  - `normalization_matched_rate = 0.983348`
  - `strict_high_rate_valid_numeric = 0.851159`
  - `mechanism_bound_rate_valid_numeric = 1.000000`
- Step6 关键一致性：
  - `kappa_mechanism = 0.987945`
  - `kappa_param_type = 1.000000`

## Step8 完成状态（入图库验收）
- 包完整性：`manifest/config/stats/rejects/conflicts` 全部生成
- 双轨导出：
  - `strict_high/nodes.csv` `strict_high/edges.csv` `strict_high/triples_spo.jsonl`
  - `strict_all/nodes.csv` `strict_all/edges.csv` `strict_all/triples_spo.jsonl`
- 校验结果：`all_targets_passed = true`
- 重复导出一致性：`deterministic_replay_match = true`
- 规模：
  - `strict_high`: `nodes=2494`, `edges=4868`
  - `strict_all`: `nodes=2892`, `edges=5742`

## 是否可以进入 Step9（结论）
结论：可以进入 Step9。

依据：
- Step8 工程门禁全通过（PK/FK/schema/evidence/unit/dry-run）。
- Step8.2 已完成“查询样例包 + 冲突信号化”并通过全部门禁。
- Step9 可直接基于 `step8_2_iter1` 产物执行评测与推演准备。

## Step8.2 完成状态（摘要）
- 功能1：产出 10~20 条固定查询模板（主图 strict_high + 扩展图 strict_all）
- 功能2：把冲突日志升级为边级信号（`conflict_count`、`alt_candidates_count`、`risk_level`）
- 结果：
  - `query_template_count = 12`
  - `query_execution_success_rate = 1.0`
  - `core_path_coverage = 1.0`
  - `edge_signal_coverage_on_strict_high = 1.0`
  - `conflict_type_classification_coverage = 1.0`
  - `deterministic_pack_rebuild_match = true`
  - `all_targets_passed = true`
- 产物目录：`00_整理记录/graph_pkg/step8_2_iter1`
- 评测报告：`00_整理记录/graph_pkg/step8_2_iter1/step8_2_eval_report.json`
- 详细方案文档：`step8_2.md`

## Step8 执行建议（本轮）
1. 采用双轨入图：
- `strict_high` 作为“高置信主图”
- `strict_all` 作为“候选扩展图”（不进入核心推演）
2. 输出统一主键与版本信息：
- `doc_id / clause_id / mention_id / definition_id / extraction_version / schema_version`
3. 入图前门禁（必须）：
- 单位标准化通过
- 证据可回溯（span/anchor 完整）
- mechanism 在已知枚举内
4. 对外评估优先喂文件：
- `00_整理记录/step7b_iterB_rulefix_triples_spo.jsonl`
- `00_整理记录/step7b_iterB_rulefix_validation_report.json`
- `00_整理记录/step7b_iterB_rulefix_iaa_report.json`
- `00_整理记录/step7b_iterB_rulefix_gate.json`

## 风险与控制点
- 风险：规则链仍有 domain-specific 漏网（跨句、多机制同句、表格行文本）。
- 控制：保持“固定 Gold + 固定门禁”回归，不以单次 rate 波动判优。
- 风险：候选扩展图（strict_all）噪声高于主图。
- 控制：推演默认仅使用 strict_high 主图；strict_all 只作召回补充与人工复核池。
