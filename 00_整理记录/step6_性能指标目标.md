# Step6 性能指标目标（小样本微调与迭代）

更新时间：2026-02-11
基线输入：`step5_seq_step2_v2_rebind11_fixabc`

## 1. Step6 目标定位
- Step6 不追求“盲目拉高覆盖率”，而是提升语义正确性与可计算稳定性。
- 优先优化低置信池与难例（尤其是机制错绑、参数类型边界、弱数值表达）。

## 2. 建议冻结的评测口径
- 分母固定：
  - `all_clause`
  - `valid_all = span_valid && normalization_attempted`
  - `valid_numeric = span_valid && normalization_matched && is_numeric_like`
- 主指标统一输出 `num/den/rate`。
- 严格区分：
  - `strict_all`（结构就绪）
  - `strict_high`（高置信入图）

## 3. Step6 建议达标指标（建议作为验收门槛）

### 3.1 硬门槛（必须满足）
- `time_raw_not_time_window = 0`
- `price_value_large_raw_small_norm = 0`
- `price_value_large_raw_small_norm_strict_high = 0`
- `candidate_score_strict_high = 0`
- `pricing_negative_conflict_rate_valid_numeric <= 0.005`

### 3.2 结构与入图可用性（必须满足）
- `mechanism_bound_rate_valid_numeric >= 0.995`
- `strict_high_rate_valid_numeric >= 0.88`
- `local_supported_rate_valid_numeric >= 0.90`
- `normalization_matched_rate >= 0.965`

### 3.3 语义正确性（人工金标，建议强约束）
- `strict_high` 子集人工 precision >= `0.92`
- 机制绑定人工 precision（valid 子集）>= `0.90`
- 归一化人工 precision（matched 子集）>= `0.90`
- 95% 置信区间下界建议：
  - strict_high precision 下界 >= `0.85`
  - mechanism precision 下界 >= `0.83`

## 4. 建议评测集规模
- 机制绑定人工复核：不少于 `120` 条（覆盖 6+ 机制类型）。
- 归一化人工复核：不少于 `120` 条（覆盖价格/阈值/时段/金额/百分比）。
- 难例专项集：不少于 `60` 条（时间点、阈值-价格同句、污染目标条款、交通能耗条款）。

## 5. 当前基线（rebind11）与 Step6 差距
- 当前已达成：
  - `strict_high_rate_valid_numeric = 0.870354`
  - `local_supported_rate_valid_numeric = 0.891206`
  - `normalization_matched_rate = 0.966696`
  - A/B/C 高风险硬错误已清零（按专项计数口径）
- 仍需在 Step6 提升：
  - 低置信池（candidate_score）语义精度与可解释性；
  - unmatched 回收能力（不破坏 A/B/C 硬门槛）。

## 6. 结论
- Step6 建议以“高置信语义精度优先”的策略推进。
- 若达成上述硬门槛 + 人工 precision 门槛，则可进入 Step7/Step8（稳定入图与推演）。
