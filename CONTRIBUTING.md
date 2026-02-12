# Contributing Guide

## 1. 分支与提交
- 主分支：`main`
- 新功能建议从 `main` 拉分支，例如：`feat/step11-auth-hardening`
- 提交信息建议使用清晰前缀：
  - `feat:` 新功能
  - `fix:` 缺陷修复
  - `docs:` 文档更新
  - `refactor:` 重构
  - `test:` 测试补充

## 2. 代码与文档要求
- 不提交密钥、口令、私有证书与本地 `.env.*` 文件。
- 任何流程变更都要同步更新对应 `step*.md` 或结果说明。
- 新增脚本请放在 `00_整理记录/scripts/`，并补充最小使用示例。

## 3. 本地自检
- Web 服务语法检查：

```bash
python3 -m py_compile langgraph_qa/server.py langgraph_qa/workflow.py
```

- Step5 规则层测试：

```bash
python3 -m unittest discover -s 00_整理记录/tests -p 'test_*.py'
```

## 4. 评测与门禁
- Step8 工程包验收报告：
  - `结果文件夹/step8_iter1/validation_report.json`
- Step8.2 查询与信号评测：
  - `结果文件夹/step8_2_iter1/step8_2_eval_report.json`
- Step9 总门禁报告：
  - `00_整理记录/step9_iter1/step9_gate_report.json`

变更涉及图谱结构、抽取逻辑或推演逻辑时，至少应保证对应门禁报告仍通过。

## 5. Pull Request 建议模板
- 变更背景
- 主要修改点
- 影响范围（StepX、脚本、数据包）
- 验证方式（命令与关键结果）
- 风险与回滚方案
