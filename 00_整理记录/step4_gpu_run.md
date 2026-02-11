# Step4 GPU Full Run Report

生成时间：2026-02-09

## 运行环境
- 机器：本机 Windows（NVIDIA GeForce RTX 3070 Laptop GPU, 8GB）
- Python 环境：`C:\Users\jihan\.conda\envs\py39`
- Paddle：`paddlepaddle-gpu==2.6.2`
- GPU 运行时：
  - `cudatoolkit=11.8`
  - `cudnn=8.9`
- 关键设置：
  - `device=gpu:0`
  - `OMP_NUM_THREADS=1`
  - `MKL_NUM_THREADS=1`
  - 运行前将 `py39` 的 `Library/bin` 加入 `PATH`

## 输入规模
- 文档级输入：`00_整理记录/step3_document_corpus.jsonl`（317）
- 条款级输入：`00_整理记录/step3_clause_corpus.jsonl`（2022）

## 执行结果
- 文档级（全量）：
  - 用时：59.735s
  - 吞吐：5.307 doc/s
  - 失败：`batch_error_count=0`，`item_error_count=0`
- 条款级（全量）：
  - 用时：340.553s
  - 吞吐：5.937 clause/s
  - 失败：`batch_error_count=0`，`item_error_count=0`
  - 截断：`truncated_input_count=0`
- 总耗时：约 400.288s（6 分 40 秒）

## 产物文件
- 文档预测：`00_整理记录/step4_gpu_doc_doc_predictions.jsonl`（317 行）
- 文档摘要：`00_整理记录/step4_gpu_doc_summary.json`
- 条款预测：`00_整理记录/step4_gpu_clause_clause_predictions.jsonl`（2022 行）
- 条款摘要：`00_整理记录/step4_gpu_clause_summary.json`

## 备注
- 由于 `conda run` 在当前终端的中文输出存在编码异常，本次使用“直接调用 `py39\\python.exe` + 显式 PATH”方式执行。
- 目前是零样本 UIE 基线，字段命中率仅作流程基线；该阶段后续已完成 Step5 规则化与 Step6 Gold/IAA，当前下一步为 Step7 小样本微调。
