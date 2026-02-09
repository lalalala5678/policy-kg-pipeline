# Step3：预处理与切分策略

时间：2026-02-09

## 目标
- 在不丢失审计链的前提下，把政策原文转换为可直接用于 Step4（UIE）的两类输入：
  - document-level 语料
  - clause-level 语料
- 解决两个关键问题：
  - 汇总拼接文件拆分为独立政策单元
  - 预处理后 offset 可回溯（raw -> clean）

## 方法

### 1. 输入冻结与审计链
- 输入范围：`01_电价政策` + `02_电能替代与清洁取暖` 下全部 `.txt`（共 151 文件）。
- 在 `step3_input_manifest.json` 记录：
  - `encoding_used`（utf-8 / gb18030）
  - `preprocess_version`
  - `git_commit`
  - `pipeline_params_hash`
  - `doc_id_rule`
- `doc_id` 规则：
  - 主键：`sha256(unit_raw_text)`（内容哈希，路径改名不影响）
  - 实例键：`sha256(source_path + source_file_sha256 + chunk_index + raw_text_sha256)`（保留谱系）

### 2. 预处理（最小损失）
- 解码：`utf-8` 优先，失败时 `gb18030` 回退。
- 规范化：
  - `\r\n -> \n`
  - `\r -> \n`
  - 去 BOM
  - 去控制字符（保留 `\t`/`\n`）
- 保证证据回溯：
  - 输出 `clean_to_raw_start/clean_to_raw_end/raw_to_clean`
  - 生成 `step3_offset_map.jsonl`
  - 做 roundtrip 校验（clean 字符回查 raw）

### 3. 汇总拼接文件预切分
- 对 `02_电能替代与清洁取暖/02_汇总拼接/*.txt` 按 `<h2>file:` 拆分。
- 每个 chunk 保留：
  - `parent_source_path`
  - `chunk_index`
  - `chunk_title`
  - `chunk_raw_start/end`

### 4. 条款切分
- 第一层：按条款编号（第X条/款/项、（一）、1. 等）切分。
- 第二层：按 `；`、`。` 再切分。
- 超长条款二次切分：按逗号和最大长度（400）再切。
- 表格兜底：按行 + 多空格/Tab 切 `table_row_clause`。
- 保留字段：
  - `clause_id`
  - `clause_text`
  - `clause_type_prelim`
  - `article_no`
  - `clean/raw span`

## 产出文件
- `00_整理记录/step3_input_manifest.json`
- `00_整理记录/step3_document_corpus.jsonl`
- `00_整理记录/step3_clause_corpus.jsonl`
- `00_整理记录/step3_offset_map.jsonl`
- `00_整理记录/step3_qc_report.json`
- `00_整理记录/step3_qc_report.md`
- `00_整理记录/step3_debug_samples.json`
- 执行脚本：
  - `00_整理记录/scripts/step3_preprocess_utils.py`
  - `00_整理记录/scripts/run_step3_preprocess.py`

## 结果摘要
- source 文件数：151
- 拆分后 unit 文档数：317（含汇总拆分 chunk 170）
- clause 数：2022
- offset roundtrip mismatch：0
- clause span 非法：0
- 无 clause 文档：0
- 质量门禁：全部通过
