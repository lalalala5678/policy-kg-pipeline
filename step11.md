# Step11 - LangGraph 前后端问答部署

目标：
- 在新端口部署“登录鉴权 + 多轮查询 + 推演回答”的 Web 工具。
- 技术栈使用 `langgraph` 与 `neo4j-graphrag-python`，并接入 DeepSeek。

## 交付物
- `langgraph_qa/server.py`
- `langgraph_qa/workflow.py`
- `langgraph_qa/static/index.html`
- `00_整理记录/scripts/run_step11_langgraph_server.sh`
- 系统服务：`/etc/systemd/system/langgraph-policy-qa.service`

## 默认运行配置
- 端口：`18081`
- 登录账号：`neo4j`
- 登录密码：`policykg_step9`
- Neo4j：`bolt://127.0.0.1:17687`
- DeepSeek 模型：`deepseek-chat`（DeepSeek API 当前可用模型之一）

## 已验证链路（本机 127.0.0.1）
1. `GET /api/health` 返回 `ok=true`。
2. `POST /api/login` 使用 `neo4j/policykg_step9` 登录成功。
3. `POST /api/ask` 返回：
   - 规划出的 `subquestions`；
   - 多轮 `steps`（每轮含 `cypher`、`row_count`、`rows`）；
   - `final_answer`（基于查询结果综合回答）。

## 说明
- 鉴权与 Neo4j Browser 保持同一组账号密码（按当前需求）。
- 当前服务依赖 `.env.langgraph` 与 `.env.local` 中的敏感配置，已通过 `.gitignore` 排除。

