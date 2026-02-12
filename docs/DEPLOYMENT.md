# Deployment Guide

本文档给出 Step11 Web 服务在 Ubuntu 上的最小可运维部署方式。

## 1. 前置条件
- 已有 Neo4j 实例并可通过 `bolt://` 访问。
- 已准备 DeepSeek API Key。
- 服务器已安装 Python 3.11+。

## 2. 安装依赖

```bash
cd /path/to/policy-kg-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements-web.txt
```

## 3. 配置环境变量

```bash
cp .env.example .env.local
```

至少修改：
- `APP_PASSWORD`
- `APP_SESSION_SECRET`
- `NEO4J_PASSWORD`
- `DEEPSEEK_API_KEY`

## 4. 前台启动（调试）

```bash
bash 00_整理记录/scripts/run_step11_langgraph_server.sh
```

默认监听：
- `0.0.0.0:18081`

## 5. 健康检查

```bash
curl -s http://127.0.0.1:18081/api/health | jq .
```

## 6. systemd 部署（推荐）

示例单元文件 `/etc/systemd/system/langgraph-policy-qa.service`：

```ini
[Unit]
Description=LangGraph Policy QA Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/policy-kg-pipeline
Environment=PYTHONUNBUFFERED=1
Environment=APP_PORT=18081
ExecStart=/home/ubuntu/policy-kg-pipeline/.venv/bin/uvicorn langgraph_qa.server:app --host 0.0.0.0 --port 18081
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启停命令：

```bash
sudo systemctl daemon-reload
sudo systemctl enable langgraph-policy-qa
sudo systemctl restart langgraph-policy-qa
sudo systemctl status langgraph-policy-qa --no-pager
```

## 7. 端口与防火墙
- Neo4j HTTP/Browse：按你的 Neo4j 配置放行（例如 `17474`）
- Neo4j Bolt：按你的 Neo4j 配置放行（例如 `17687`）
- Step11 Web：`18081`

## 8. 反向代理建议
- 生产环境建议在 Nginx/Caddy 后挂载该服务。
- 强制 HTTPS。
- 对外仅开放 80/443，服务端口仅内网可访问。
