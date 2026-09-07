# NewsAgent

NewsAgent 是一个面向个人和团队的 AI 新闻早报 Agent。它从多个 RSS 新闻源抓取内容，自动完成去重、清洗、分类、摘要和分类综述，生成 Markdown 日报，并可通过邮件推送；同时提供 HTTP API、Web 控制台和命令行入口，方便接入已有工作流。

## 核心能力

- **完整新闻流水线**：异步并发抓取 RSS -> 标题去重 -> 文本清洗 -> AI 分类 -> 单篇摘要 -> 分类综述 -> Markdown 日报 -> 可选邮件推送。
- **意图识别与分流**：HTTP 入口自动识别“看今日简报”或“查某主题”等请求，分别进入日报生成与主题检索流程。
- **生产级工作流**：基于 LangGraph `StateGraph` 管理状态、节点、条件路由与 checkpoint；单个 RSS 源失败不会中断整条链路。
- **成本与上下文控制**：分类、摘要和分类综述均带本地缓存，每个 LLM 节点只读取当前步骤所需的最小状态。
- **可观测与持久化**：内置日志、环节耗时统计、可选 Langfuse trace，以及 SQLite 任务历史。
- **安全交付**：API 默认不发送邮件；CLI 支持 `--no-send` 干跑和发送前 Y/N 人工确认。

技术栈：Python 3.11、FastAPI、LangGraph、aiohttp + feedparser、DashScope 兼容接口（qwen-turbo）、SQLite、Docker。

## 在线体验

| 入口 | 地址 |
| :--- | :--- |
| Web 控制台 | https://news-agent-production-7e22.up.railway.app |
| API 文档 | https://news-agent-production-7e22.up.railway.app/docs |
| 健康检查 | https://news-agent-production-7e22.up.railway.app/health |

## 快速开始

### 安装

需要 Python 3.11+，建议使用 [uv](https://docs.astral.sh/uv/) 管理依赖：

```bash
git clone https://github.com/jyc18224/news_agent.git
cd news_agent
uv sync
```

### 无密钥演示

不配置 API Key、邮箱或 RSS 网络即可生成一份产品示例日报：

```bash
uv run python main/demo_product.py
```

运行后会生成 `examples/demo_report.md`。

### 配置环境变量

```bash
cp .env.example .env
```

按需填写 `.env`：

- `DASHSCOPE_API_KEY`：运行真实日报流程必需。
- `EMAIL_SENDER`、`EMAIL_AUTH_CODE`、`EMAIL_TO`：需要邮件推送时配置。
- `LANGFUSE_ENABLED` 与 `LANGFUSE_*`：可选，用于开启 Langfuse 追踪。
- `NEWS_AGENT_DB_PATH`：可选，SQLite 数据库文件路径，默认 `data/news_agent.db`。

新闻源在 `config/sources.yaml` 中配置，系统默认接入 OpenAI Blog、Hacker News 和 TechCrunch AI。

### 运行 Web 服务

```bash
uv run uvicorn news_agent.api:app --port 8000 --env-file .env
```

访问：

- Web 控制台：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

如需让局域网其他设备访问，请加上 `--host 0.0.0.0`，并确认防火墙已放行 `8000` 端口。

### 命令行运行

```bash
# 完整日报流程
uv run python main/run_graph.py

# 禁止发送邮件
uv run python main/run_graph.py --no-send

# 邮件发送前要求 Y/N 确认
uv run python main/run_graph.py --confirm-email

# 自定义报告输出位置
uv run python main/run_graph.py --output report.md
```

`main/auto_run.py` 可作为定时任务的包装入口，配合 cron、systemd timer 或云调度器使用。

## HTTP API

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| GET | `/` | Web 控制台 |
| GET | `/health` | 健康检查 |
| GET | `/api/demo` | 获取内置演示日报 |
| POST | `/api/agent/run` | 运行 Agent，自动识别意图 |
| GET | `/api/tasks` | 查询历史任务 |
| GET | `/api/tasks/{task_id}` | 查询任务详情 |

请求体支持 `query`、`send_email` 和 `confirm_email`，其中 `send_email` 默认 `false`。

```bash
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{"query":"看今日简报","send_email":false}'
```

主题检索示例：

```bash
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{"query":"查一下 AI Agent 主题","send_email":false}'
```

## 部署

### Docker

```bash
docker build -t news-agent .
docker run --rm -p 8000:8000 \
  -e DASHSCOPE_API_KEY=your_key \
  news-agent
```

需要邮件、Langfuse 等更多配置时，使用 Docker Compose：

```bash
docker compose up --build
```

### Render 与 Railway

项目根目录包含 `render.yaml` 和 `railway.toml`。选择 Dockerfile 构建，按 `.env.example` 配置环境变量即可；服务健康检查路径为 `/health`。

## 项目结构

```text
main/
  run_graph.py              # 命令行完整工作流
  demo_product.py           # 无密钥演示日报
  auto_run.py               # 定时任务包装入口
src/news_agent/
  api.py                    # FastAPI 服务与 Web 入口
  service.py                # Agent 业务服务层
  graph.py                  # LangGraph 工作流
  intent.py                 # 意图识别分流
  nodes/                    # 抓取、去重、分类、摘要、发送等节点
  storage.py                # SQLite 持久化
  observability.py          # Langfuse 追踪
  web/index.html            # Web 控制台
config/sources.yaml         # RSS 新闻源与任务配置
examples/demo_report.md     # 示例日报
tests/                      # 自动化测试
Dockerfile                  # 容器镜像
docker-compose.yml          # 本地容器编排
render.yaml                 # Render 部署配置
railway.toml                # Railway 部署配置
```

## 测试

```bash
uv run pytest tests/
```

当前测试覆盖配置解析、运行环境、文本清洗、标题去重、意图识别、SQLite 持久化、产品演示输出、邮件发送和 HTTP API。
