# Policy KG Pipeline

基于电力与电能替代政策文本，构建可复现、可审计、可推演的知识图谱流水线。

当前仓库已完成 `Step1-Step9` 主流程，并提供 `Step11` 的 LangGraph + Neo4j + DeepSeek Web 问答服务。

## 1. 项目目标
- 将原始政策文本转化为结构化图谱。
- 建立从抽取、归一化、门禁、导出到 Neo4j 落地的端到端闭环。
- 支持图谱检索、风险信号标注与多轮问答推演。

## 2. 当前完成度
- `Step1-Step9`：已完成，包含图谱构建、质量门禁、Neo4j 导入与查询评测。
- `Step10`：DeepSeek + Neo4j 的脚本化问答入口。
- `Step11`：鉴权 Web 前后端，多轮查询进度展示，面向人机交互。

核心成果入口：
- `结果文件夹/README_使用指南.md`
- `结果文件夹/STEP1-STEP9_成果测评创新总览.md`

## 3. 目录结构

```text
.
├── 00_整理记录/                  # 脚本、评测报告、中间产物
│   ├── scripts/
│   └── tests/
├── 01_电价政策/                  # 电价政策文本
├── 02_电能替代与清洁取暖/         # 电能替代/清洁取暖政策文本
├── langgraph_qa/                 # Step11 Web 服务（FastAPI + LangGraph）
├── 结果文件夹/                    # 可交付结果包（Step8/Step8.2/总览）
├── step1.md ... step11.md        # 各步骤说明
└── README.md
```

## 4. 环境要求
- OS: Ubuntu 22.04+（其他 Linux 发行版也可）
- Python: `3.11+`（当前环境为 `3.12`）
- Neo4j: 已导入 Step8 图包（默认 `bolt://127.0.0.1:17687`）
- DeepSeek API Key（用于 Step10/Step11 LLM 推理）

## 5. 快速开始

### 5.1 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements-web.txt
```

如需跑 Step4 UIE 基线抽取，再安装：

```bash
pip install -r requirements-step4.txt
```

### 5.2 配置环境变量

```bash
cp .env.example .env.local
# 按需修改账号密码、Neo4j、DeepSeek 配置
```

### 5.3 启动 Step11 Web 服务

```bash
bash 00_整理记录/scripts/run_step11_langgraph_server.sh
```

默认地址：`http://127.0.0.1:18081`

### 5.4 健康检查

```bash
curl -s http://127.0.0.1:18081/api/health | jq .
```

## 6. 常用命令

### Step9（Neo4j 评测闭环）

```bash
python3 00_整理记录/scripts/run_step9_neo4j_eval.py --overwrite
python3 00_整理记录/scripts/run_step9_query_eval.py
python3 00_整理记录/scripts/run_step9_simulation.py
python3 00_整理记录/scripts/eval_step9_gate.py
```

### Step10（脚本化自然语言问答）

```bash
python3 00_整理记录/scripts/run_step10_deepseek_graph_qa.py \
  --question "列出高风险事实最多的机制类型前10名" \
  --neo4j-url http://127.0.0.1:17474 \
  --neo4j-user neo4j \
  --neo4j-password "<your_password>" \
  --deepseek-model deepseek-chat \
  --print-cypher
```

## 7. 测试与质量
- Step5 规则层单元测试：`00_整理记录/tests/`
- Step8 导出包验收：`结果文件夹/step8_iter1/validation_report.json`
- Step8.2 查询包验收：`结果文件夹/step8_2_iter1/step8_2_eval_report.json`
- Step9 总门禁：`00_整理记录/step9_iter1/step9_gate_report.json`

## 8. 安全与运维建议
- 不要把真实密钥写入仓库；使用 `.env.local` 或系统环境变量。
- 生产环境务必修改默认 `APP_USERNAME` / `APP_PASSWORD` / `APP_SESSION_SECRET`。
- 若开放公网访问，请配置防火墙白名单、反向代理与 HTTPS。

## 9. 协作开发
- 贡献规范见：`CONTRIBUTING.md`
- 推荐先阅读：`agent.md` 与各步骤文档 `step*.md`

## 10. 许可证
当前仓库未单独声明开源许可证。对外发布前请先补齐许可证与数据合规声明。
