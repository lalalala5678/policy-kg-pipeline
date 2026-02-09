# Step3 预处理与切分体检报告

- 生成时间: 2026-02-09 19:06:28
- preprocess_version: step3_preprocess_v1.0
- git_commit: 5c7c40a6b036ddb63edece4e1f97bc539a5c41d8
- pipeline_params_hash: cd182077a4ddf8c8941b9edfe2f484adead9ae497bcddf77b927566f669616b0

## 输入与切分规模
- 原始 source 文件数: 151
- 独立 unit 文档数: 317
- 汇总拼接来源文件数: 4
- 汇总拆分后 chunk 数: 170
- 编码使用统计: {'utf-8': 151, 'gb18030': 0}

## 文本预处理变化
- 总 raw 字符数: 128968
- 总 clean 字符数: 127771
- 删除 BOM: 0
- CRLF 归一: 1197
- CR 转 LF: 0
- 删除控制字符: 0

## Offset 映射质量
- 映射 mismatch 文档数: 0
- mismatch 字符总数: 0
- mismatch 比例: 0.0

## 条款切分质量
- clause 总数: 2022
- 无 clause 文档数: 0
- 平均 clause/文档: 6.3785
- clause 长度统计: {'count': 2022, 'min': 20, 'max': 400, 'avg': 71.44, 'p90': 134}
- clause 类型分布: {'time_rule': 527, 'pricing_rule': 207, 'scope_rule': 77, 'other': 527, 'execution_rule': 113, 'subsidy_rule': 361, 'task_assessment': 80, 'table_row_clause': 130}

## 门禁结果
- all_doc_have_ids: True
- all_clause_span_valid: True
- no_offset_mismatch: True
- clause_non_empty_rate_ge_99: True
- clause_max_len_le_400: True
- overall_pass: True

## 产物
- `00_整理记录/step3_input_manifest.json`
- `00_整理记录/step3_document_corpus.jsonl`
- `00_整理记录/step3_clause_corpus.jsonl`
- `00_整理记录/step3_offset_map.jsonl`
- `00_整理记录/step3_qc_report.json`
