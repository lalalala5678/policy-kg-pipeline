# Step6 性能指标目标（Gold/IAA 构建与一致性评测）

更新时间：2026-02-11  
输入基线：`step5_seq_step2_v2_rebind11_fixabc`

## 执行状态（最新）
- Step6 已执行完成，且达标通过。
- 最终报告：`00_整理记录/step6_iaa_report.json`
- 结论：`all_targets_passed = true`

## 1. Step6 定位
- Step6 的目标不是继续调规则提分，而是构建可复核的 Gold/IAA 基准集。
- Step6 完成后，Step7 才开始小样本微调；避免在噪声标签上训练。
- 本阶段全部由 Codex 执行：抽样、标注、复核、仲裁、统计、报告。

## 2. 输入与口径冻结
- 主输入：
  - `00_整理记录/step5_seq_step2_v2_rebind11_fixabc_parameter_mentions.jsonl`
  - `00_整理记录/step5_seq_step2_v2_rebind11_fixabc_parameter_definitions.jsonl`
  - `00_整理记录/step5_seq_step2_v2_rebind11_fixabc_validation_report.json`
  - `00_整理记录/step3_clause_corpus.jsonl`
- 冻结分母（必须同报）：
  - `all_clause`
  - `valid_all = span_valid && normalization_attempted`
  - `valid_numeric = span_valid && normalization_matched && is_numeric_like`
- 冻结 valid 判定：
  - `span_valid == true`
  - `normalization_matched == true`（numeric 轨）
  - 指标统一输出 `num/den/rate`。

## 3. Gold 样本抽样设计（分层）
- 抽样单元：`parameter_mention`。
- 分层维度：
  - `mechanism_bind_after`
  - `param_type`
  - `bind_reason`（high_conf / candidate_score / fallback）
  - `strict_high`（true/false）
  - 难例簇（时间点、阈值-价格同句、污染域、任务型条款）
- 建议最小规模（本轮执行目标）：
  - Gold 主集：`N >= 240`
  - 其中 strict_high 至少 `120`
  - 难例专项至少 `60`

## 4. IAA 执行协议（无真人）
- 双遍独立标注（同一条样本）：
  - Pass-A：基于 schema 与证据 span 的严格判读
  - Pass-B：重排样本顺序并屏蔽 Pass-A 结果，独立判读
- 比较字段：
  - `mechanism_bind_after`
  - `param_type`
  - `norm_value` / `norm_unit`
  - `strict_high_eligible`
- 自动仲裁：
  - 规则优先（证据 span + 单位解析一致）；
  - 规则冲突时进入 adjudication 字段并保留理由。

## 5. Step6 通过阈值（进入 Step7 的门槛）

### 5.1 IAA 一致性
- `kappa(mechanism_bind_after) >= 0.80`
- `kappa(param_type) >= 0.80`
- `exact_match(norm_unit) >= 0.90`
- `strict_high_eligible agreement >= 0.90`

### 5.2 Gold 质量（相对 Step5 输出）
- Gold 子集机制绑定 precision >= `0.90`
- Gold 子集归一化 precision >= `0.90`
- Gold 子集 strict_high precision >= `0.92`

### 5.3 错误簇上限
- `time_raw_not_time_window` 在 Gold 中 `= 0`
- `price_value_large_raw_small_norm` 在 Gold 中 `= 0`
- `candidate_score` 进入 strict_high 的比例 `= 0`

## 6. Step6 固定输出文件
- `00_整理记录/step6_gold_sampling_plan.json`
- `00_整理记录/step6_gold_sample_v1.jsonl`
- `00_整理记录/step6_gold_passA_labels.jsonl`
- `00_整理记录/step6_gold_passB_labels.jsonl`
- `00_整理记录/step6_gold_adjudicated.jsonl`
- `00_整理记录/step6_iaa_report.json`
- `00_整理记录/step6_iaa_report.md`
- `00_整理记录/step6_error_clusters.md`

## 7. 与 Step7 的衔接
- Step7 微调仅使用 `step6_gold_adjudicated.jsonl` 作为监督数据来源。
- 若 Step6 不达标，先修复 Step5/标注协议，再重跑 Step6；不直接进入微调。
