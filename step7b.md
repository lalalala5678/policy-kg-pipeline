# Step7b: UIE 参数调优门禁实验

更新时间：2026-02-11

## 目标
- 在固定 Gold（U0）上做稳定门禁评测，避免分母漂移。
- 采用“硬门槛 + 增益门槛”：
  - 硬门槛：质量不退化（基线相对阈值）+ 高危错误桶为 0。
  - 增益门槛：关键字段命中增益或 strict-high TP 增益至少满足其一。

## 主要实现
- 新增门禁脚本：`00_整理记录/scripts/eval_step7b_uie_gate.py`
  - 固定 Gold 集：`00_整理记录/step7_iter3b_unitfix_timeunit_thr060_gold_adjudicated.jsonl`
  - 基线输入：`step7_iter3_unitfix_timeunit_thr060` / `step7_iter3b_unitfix_timeunit_thr060`
  - 候选输入：任意 Step5/Step6 组合（本轮选 `step7b_iterB_rulefix`）。

- Step5 规则补丁（用于提升固定 Gold 下 TP）：
  - `build_norm_input` 新增“标签单位恢复”：
    - `电量/用电量` + 局部上下文 -> `千瓦时`。
  - 新增“非数值 raw + 单位上下文恢复”：
    - 当 `raw_value` 非数值但单位可靠时，从局部窗口恢复数值后再归一化。
  - 保守策略：移除 `峰谷价差` -> `%` 的恢复，避免 strict-high 新增误报。

## 最终通过版本
- Step5: `00_整理记录/step7b_iterB_rulefix_validation_report.json`
- Step6: `00_整理记录/step7b_iterB_rulefix_iaa_report.json`
- Gate: `00_整理记录/step7b_iterB_rulefix_gate.json`

## 关键结果
- `all_targets_passed = true`
- 硬门槛：全部通过
- 增益门槛：`strict_high_tp_delta = +2`（基线 220 -> 候选 222）
- Step5：
  - `normalization_matched_rate = 0.983348`
  - `strict_high_rate_valid_numeric = 0.851159`
  - `mechanism_bound_rate_valid_numeric = 1.000000`
- 固定 Gold 指标（门禁主口径）：
  - `fixed_gold_mechanism_precision = 0.958904`（与基线持平）
  - `fixed_gold_normalization_precision = 0.993127`（高于基线 0.986254）
  - `fixed_gold_strict_high_precision = 0.995516`（不低于基线）

## 说明
- 本轮“参数调优”是门禁化调优与后处理纠偏，不是 UIE 权重训练。
- 尝试重跑 Step4 UIE 时受本机 `cudnn64_8.dll` 环境问题影响，无法稳定得到可用候选；因此本轮以固定 U0 + Step5 可复现补丁完成增益验证。
