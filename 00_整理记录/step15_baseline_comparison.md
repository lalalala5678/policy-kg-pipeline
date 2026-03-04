# Step15 外部基线对照（同口径）

## 设计
- `full`: 完整方法（full binding + strict_high guards）
- `uie_only`: 仅使用 Step4 机制绑定，不使用候选重绑定
- `rule_only`: 忽略 Step4 机制先验/回退，仅靠规则候选
- `no_rebind`: `bind_min_score=99`，近似关闭候选驱动重绑定
- `no_gate`: 关闭 strict_high guards（strict_high=strict_all）

## 结果表
| baseline | valid_all | valid_numeric | norm_matched | mech_bound(valid_all) | strict_high(valid_all) | local_supported(valid_all) | all_targets_passed |
|---|---:|---:|---:|---:|---:|---:|---|
| full | 1141 | 1122 | 0.983348 | 0.999124 | 0.836985 | 0.884312 | True |
| uie_only | 1141 | 1122 | 0.983348 | 0.990359 | 0.000000 | 0.490798 | False |
| rule_only | 1141 | 1122 | 0.983348 | 0.988606 | 0.817704 | 0.869413 | True |
| no_rebind | 1141 | 1122 | 0.983348 | 0.921998 | 0.000000 | 0.489921 | False |
| no_gate | 1141 | 1122 | 0.983348 | 0.999124 | 0.983348 | 0.884312 | True |

## 运行记录
- full: return_code=0, elapsed_sec=0.479, cmd=`python3 00_整理记录/scripts/run_step5_normalize_validate.py --clause-pred-file 00_整理记录/step4_seq_step2_clause_predictions.jsonl --clause-source-file 00_整理记录/step3_clause_corpus.jsonl --strict-high-threshold 0.6 --bind-min-score 1.0 --output-prefix step15_baseline_full --binding-mode full`
- uie_only: return_code=0, elapsed_sec=0.469, cmd=`python3 00_整理记录/scripts/run_step5_normalize_validate.py --clause-pred-file 00_整理记录/step4_seq_step2_clause_predictions.jsonl --clause-source-file 00_整理记录/step3_clause_corpus.jsonl --strict-high-threshold 0.6 --bind-min-score 1.0 --output-prefix step15_baseline_uie_only --binding-mode uie_only`
- rule_only: return_code=0, elapsed_sec=0.486, cmd=`python3 00_整理记录/scripts/run_step5_normalize_validate.py --clause-pred-file 00_整理记录/step4_seq_step2_clause_predictions.jsonl --clause-source-file 00_整理记录/step3_clause_corpus.jsonl --strict-high-threshold 0.6 --bind-min-score 1.0 --output-prefix step15_baseline_rule_only --binding-mode rule_only`
- no_rebind: return_code=0, elapsed_sec=0.477, cmd=`python3 00_整理记录/scripts/run_step5_normalize_validate.py --clause-pred-file 00_整理记录/step4_seq_step2_clause_predictions.jsonl --clause-source-file 00_整理记录/step3_clause_corpus.jsonl --strict-high-threshold 0.6 --bind-min-score 1.0 --output-prefix step15_baseline_no_rebind --binding-mode full --bind-min-score 99`
- no_gate: return_code=0, elapsed_sec=0.49, cmd=`python3 00_整理记录/scripts/run_step5_normalize_validate.py --clause-pred-file 00_整理记录/step4_seq_step2_clause_predictions.jsonl --clause-source-file 00_整理记录/step3_clause_corpus.jsonl --strict-high-threshold 0.6 --bind-min-score 1.0 --output-prefix step15_baseline_no_gate --binding-mode full --disable-strict-high-guards`
