# step4_seq_semantic_audit_recheck

- sample_size: 80
- missing_columns: []
- duplicate_clause_count: 0
- empty_text_rows: 0
- auto_logic_mismatch_count: 0
- agreement_rate: 0.9
- cohen_kappa: 0.72766
- judgement: Auto audit is structurally valid and reasonably stable under independent recheck.

## Confusion Matrix
- auto_true_indep_true: 57
- auto_true_indep_false: 0
- auto_false_indep_true: 8
- auto_false_indep_false: 15

## Bucket Summary
- lowconf: count=15, auto_true_rate=0.0, indep_true_rate=0.0, agreement_rate=1.0
- rule_highconf: count=65, auto_true_rate=0.876923, indep_true_rate=1.0, agreement_rate=0.876923

## Artifacts
- `00_整理记录/step4_seq_semantic_audit_recheck.json`
- `00_整理记录/step4_seq_semantic_audit_recheck_disagreements.csv`
