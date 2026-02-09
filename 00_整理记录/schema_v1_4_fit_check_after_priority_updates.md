# v1.4 优先项改后体检报告

生成时间：2026-02-09 18:20:34

## 总结
- 优先1（文件名补偿+冲突仲裁）：issue_date 覆盖 83.44% -> 83.44%，doc_type 覆盖 98.68% -> 98.68%，document_no 覆盖 7.95% -> 8.61%。
- 优先2（任务型条款结构化）：任务条款 279 条，主体覆盖 27.24%，动作覆盖 93.19%，期限覆盖 34.41%，考核覆盖 10.39%。
- 优先3（no_parameter_top25 验证）：样本 25 份，机制召回（micro_recall）1.0，误抽率（false_positive_rate）0.0，完全匹配率 1.0。
- 优先4（归一顺序单测）：测试通过=True（return_code=0）。

## 产物文件
- priority1: `00_整理记录/priority1_doc_meta_compensation.json`
- priority1 sample: `00_整理记录/priority1_doc_meta_compensation_sample.json`
- priority2 records: `00_整理记录/priority2_task_clause_structured.jsonl`
- priority2 summary: `00_整理记录/priority2_task_clause_summary.json`
- priority3 set: `00_整理记录/priority3_no_parameter_top25_annotation.jsonl`
- priority3 eval: `00_整理记录/priority3_uie_weak_value_eval.json`
- priority4 tests: `00_整理记录/priority4_normalization_tests.json`
- after check json: `00_整理记录/schema_v1_4_fit_check_after_priority_updates.json`

## 说明
- 优先3当前使用 `uie_proxy_keyword_baseline` 进行弱数值样本预验收；同一评估脚本可替换成真实 UIE 预测结果继续复用。
