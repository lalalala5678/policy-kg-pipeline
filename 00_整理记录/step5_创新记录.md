# Step5 创新记录（rebind11 -> rebind12）

更新时间：2026-02-11

对应产物前缀：
- 旧版：`step5_seq_step2_v2_rebind11_fixabc`
- 最新：`step5_seq_step2_v2_rebind12_fixabcd`

## 1. 本步目标
- 在不重跑 Step4 模型的前提下，利用规则归一化 + 机制二次纠偏提升可入图质量。
- 重点修复四类高风险问题：
  - A：`duration_month_context` 误吞电价/电量/年份；
  - B：户数被误配为金额；
  - C：`1:1:1` 资金分担比例语义桶不准确；
  - D：`strict_high` 在弱约束场景门禁不一致。

## 2. 关键创新点

### 2.1 归一化防串值（核心）
- 将归一化上下文从“全 clause 任意借值”收敛到“mention 优先”。
- 对价格规则增加“值一致性”约束，避免 `170/260/4440` 被映射到同句 `0.05 元/千瓦时`。
- 新增 mention-unit 配对门禁：在密集条款中发现 `raw_unit` 可能误配时，优先丢弃错误 unit。

### 2.2 A/B 定向修复
- `duration_month_context` 改为“强阈值前缀 + 语境词”触发，并加入价格/物理单位冲突过滤。
- 年份值（如 `至2018`）不再落入 month；疑似错配改为 `no_match`。
- 新增户数邻域规则：若出现 `raw_value + 户/家/个/人`，禁止落入 `subsidy_amount/yuan`。

### 2.3 C 语义细化
- `ratio_sequence` 在“资金由/分担/中央-省-市-县-区”语境下映射为 `funding_share_ratio`，不再统一落入 `ratio_target`。

### 2.4 D 门禁一致化
- `strict_high` 新增两道门禁：
  - `param_type/raw_unit/norm_unit` 兼容性检查；
  - 括号弱约束过滤（如 `（不少于两个月）` 不进入 strict_high）。

## 3. 质量结果（rebind11 -> rebind12）
- mention_total：`1141 -> 1141`
- normalization_matched：`1103 -> 1079`
- strict_high：`960 -> 924`
- strict_high_rate_valid_numeric：`0.870354 -> 0.856348`
- all_targets_passed：`true -> true`

## 4. A/B/C/D 专项变化
- `duration_month_context`：`29 -> 7`
- `duration_month_context + raw_unit`：`13 -> 0`
- duration 进入 strict_high：`29 -> 1`
- 弱括号 duration 进入 strict_high：`9 -> 0`
- `1:1:1` 作为 `funding_share_ratio`：`0 -> 7`
- `1:1:1` 仍在 `ratio_target`：`11 -> 4`
- 关键样本：
  - `pm_0642...`：`duration_threshold_month -> no_match`
  - `pm_0e905...`：`duration_threshold_month -> no_match`
  - `pm_296552...`：`subsidy_amount -> no_match`
  - `pm_106b35...`：`ratio_target -> funding_share_ratio`
  - `pm_00f41...`：`strict_high true -> false`

## 5. 产物与脚本
- `00_整理记录/scripts/policy_extraction_utils.py`
- `00_整理记录/scripts/run_step5_normalize_validate.py`
- `00_整理记录/tests/test_step5_normalizer.py`
- `00_整理记录/tests/test_step5_binding_rules.py`
- `00_整理记录/step5_seq_step2_v2_rebind12_fixabcd_*.jsonl/json/md`
- `00_整理记录/step5_fixabcd_issueAtoD_eval.json`

## 7. rebind14（plus2）进一步优化结论
- 对比基线：`rebind12_fixabcd`。
- 新增优化：
  - 大额 `price_value(yuan)` 在补贴语境下回收为 `subsidy_amount`；
  - 百分比分型使用更严格价格变动触发词（`上浮/下浮/加价/降价/调价/提高/降低`）。
- 量化变化（strict_high）：
  - `price_value >= 10`：`3 -> 0`
  - `ratio_target + 局部价格变动词`：`54 -> 0`
  - `price_delta_pct + 局部无价格变动词`：`6 -> 1`
  - `amount_param + non_subsidy mechanism`：`2 -> 0`
- 主指标仍达标：
  - `strict_high_rate_valid_numeric = 0.848934`
  - `all_targets_passed = true`
- 对应文件：
  - `00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_validation_report.json`
  - `00_整理记录/step5_fixabcd_plus2_eval.json`
  - `00_整理记录/step6_iter4_fixabcd_plus_iaa_report.json`
