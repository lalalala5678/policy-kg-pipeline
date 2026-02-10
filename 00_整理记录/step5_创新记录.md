# Step5 创新记录（rebind11）

更新时间：2026-02-11
对应产物前缀：`step5_seq_step2_v2_rebind11_fixabc`

## 1. 本步目标
- 在不重跑 Step4 模型的前提下，利用规则归一化 + 机制二次纠偏提升可入图质量。
- 重点修复三类高风险问题：
  - A：时间点被错当比例目标；
  - B：阈值值被错归一到价格值；
  - C：低证据 `candidate_score` 绑定簇污染解释性。

## 2. 关键创新点

### 2.1 归一化防串值（核心）
- 将归一化上下文从“全 clause 任意借值”收敛到“mention 优先”。
- 对价格规则增加“值一致性”约束，避免 `170/260/4440` 被映射到同句的 `0.05 元/千瓦时`。
- 新增 mention-unit 配对门禁：在密集条款中发现 `raw_unit` 可能误配时，优先丢弃错误 unit，避免把价格参数错写为阈值（或反之）。

### 2.2 时间表达纠偏
- 增加 `time_point` 归一化规则（如 `7:00`, `22:00`）。
- 强制禁止时间点落入 `ratio_target`，统一到 `time_window/time_point`。
- 在分时语境下（峰谷/分时词命中）优先绑定 `tou_pricing`。

### 2.3 机制绑定置信治理
- 维持双轨 strict：`strict_all` 与 `strict_high`。
- 对 `candidate_score/step4_inherit/step4_fallback` 施加低置信上限，确保不会误入 `strict_high`。
- 在交通/能耗类上下文中抑制电价机制 fallback，减少“语境错绑”。

### 2.4 评测口径冻结与可审计性
- 固定三套分母：`all_clause / valid_all / valid_numeric`。
- 报告统一输出 `num/den/rate`，并保留中间分布（bind reason、skip reason、冲突组等）。

## 3. 质量结果（与 rebind4 对比）

### 3.1 主指标变化
- `normalization_matched_rate`: `0.988606 -> 0.966696`
- `mechanism_bound_rate_valid_numeric`: `1.000000 -> 1.000000`
- `strict_high_rate_valid_numeric`: `0.845745 -> 0.870354`
- `local_supported_rate_valid_numeric`: `0.882092 -> 0.891206`
- `pricing_negative_conflict_rate_valid_numeric`: `0.000000 -> 0.000000`
- `all_targets_passed`: `true`

### 3.2 问题专项变化（A/B/C）
- 时间点误分型（A）：`10 -> 0`
- 阈值错归一到价格（B）：`20 -> 0`
- 上述问题在 strict_high 子集（B）：`10 -> 0`
- `candidate_score` 条目（C）：`106 -> 97`
- `candidate_score` 进入 strict_high（C）：`0 -> 0`

## 4. 人工复核结论
- 文件：`00_整理记录/step5_seq_step2_v2_rebind11_fixabc_manual_audit.md`
- 结果摘要：
  - 时间点修复样本：10/10 正确；
  - 阈值重判样本：10/10 正确；
  - 随机 strict_high 抽样：30/30 未发现明确错误；
  - candidate_score 抽样：均保持 strict_high=false。

## 5. 残余问题（实事求是）
- `normalization_unmatched` 从 13 增至 38，属于“防串值后召回下降”的副作用。
- 低置信池仍存在少量语义错配，但不在 strict_high 主入图集合。
- 下一步（Step6）应通过小样本微调提升低置信池语义判别能力，而不是回退当前门禁。
