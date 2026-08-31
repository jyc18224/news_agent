# NewsAgent

NewsAgent 是一个面向个人和团队的 AI 新闻早报 Agent。它从多个 RSS 新闻源自动抓取内容，完成去重、清洗、分类、摘要、综述、Markdown 日报生成与邮件推送，并通过标准化 HTTP API 和 Web 控制台对外提供服务。

---

## 核心能力

### 1. 业务闭环

NewsAgent 覆盖完整业务链路：

```text
RSS 新闻源 -> 异步抓取 -> 标题去重 -> 文本清洗 -> 意图识别
           -> AI 分类 -> AI 摘要 -> 分类综述 -> 日报生成 -> 邮件推送
```

系统输出可直接阅读、归档和二次分发的 Markdown 日报，而不是只停留在模型调用阶段。

### 2. 工程可靠性

- 使用 LangGraph `StateGraph` 管理节点、状态、条件路由和 checkpoint
- 每个数据源独立抓取，单个 RSS 失败不会中断整条链路
- 分类、摘要、分类综述均带本地缓存，避免重复消耗 Token
- 日志记录运行过程与错误信息
- 提供 Dockerfile、健康检查、自动化测试和 SQLite 任务历史

### 3. 任务规划能力

- 入口处增加意图识别，自动分流：
  - `看今日简报` 进入日报生成流程
  - `查特定主题` 进入主题检索流程
- 使用条件路由处理文章数量超过阈值的情况
- 工作流状态通过统一 `AgentState` 传递，为后续扩展任务规划节点保留清晰边界

### 4. 上下文管理

- 将配置、原始文章、去重结果、清洗结果、分类结果、摘要、报告分别放入独立状态字段
- 每个 LLM 节点只使用当前任务所需的最小子集，避免无关历史信息进入 prompt
- 缓存以标题为键，降低重复内容对上下文的污染和 Token 成本

### 5. 监控与评测

- 内置日志体系，记录抓取、清洗、分类、摘要、报告、邮件各环节耗时
- 可选接入 Langfuse，为每次 Agent 运行生成 trace
- SQLite 保存任务 ID、用户输入、模型输出、执行耗时、任务状态与错误信息
- 提供自动化测试，覆盖配置解析、意图识别、持久化、清洗、去重和演示输出

### 6. 人类干预机制

- 邮件发送前支持 Y/N 人工确认
- 支持 `--no-send` 干跑模式，不触发真实邮件
- API 默认不发送邮件，避免 Web 请求意外触发外发行为

---

## 快速开始

### 无密钥演示

不需要 API Key、邮箱或 RSS 网络：

```bash
python main/demo_product.py
```

生成示例日报：

```text
examples/demo_report.md
```

### 本地启动 Web 服务

```bash
uv sync
uv run uvicorn news_agent.api:app --host 0.0.0.0 --port 8000
```

访问：

- Web 控制台：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 配置环境变量

复制 `.env.example` 为 `.env`：

```text
DASHSCOPE_API_KEY=
EMAIL_SENDER=
EMAIL_AUTH_CODE=
EMAIL_TO=
LANGFUSE_ENABLED=false
NEWS_AGENT_DB_PATH=data/news_agent.db
```

### 命令行运行

```bash
# 完整日报流程
python main/run_graph.py

# 邮件发送前要求 Y/N 确认
python main/run_graph.py --confirm-email

# 禁止发送邮件
python main/run_graph.py --no-send

# 定时运行
python main/auto_run.py
```

---

## HTTP API

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| GET | `/` | Web 控制台 |
| GET | `/health` | 健康检查 |
| GET | `/api/demo` | 获取内置演示日报 |
| POST | `/api/agent/run` | 运行 Agent，自动识别意图 |
| GET | `/api/tasks` | 查询历史任务 |
| GET | `/api/tasks/{task_id}` | 查询任务详情 |

运行 Agent 示例：

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

---

## 容器化部署

### 本地 Docker 构建

```bash
docker build -t news-agent .
docker run --rm -p 8000:8000 \
  -e DASHSCOPE_API_KEY=your_key \
  news-agent
```

### Docker Compose

```bash
docker compose up --build
```

### Render

项目包含 `render.yaml`，Render 可自动识别 Docker 部署配置：

```text
type: web
runtime: docker
dockerfilePath: ./Dockerfile
healthCheckPath: /health
```

### Railway

项目包含 `railway.json` 和 `Dockerfile`，Railway 可直接使用 Docker 构建。

---

## 部署证明

### 本地验证

- Python 测试：`21 passed`
- FastAPI 健康检查：`GET /health` 返回 `200 OK`
- Web 控制台：`GET /` 返回 `200 OK`
- 演示报告接口：`GET /api/demo` 返回完整 Markdown 日报
- 主题检索接口：`POST /api/agent/run` 成功写入 SQLite 任务记录
- Docker 配置：`Dockerfile`、`docker-compose.yml`、`render.yaml`、`railway.json` 已提供
- Docker Compose 配置校验：`docker compose config --quiet` 通过

### 公网部署状态

当前公网部署尚未完成。原因是本机未配置 Render 或 Railway 的账号凭据，无法代替用户完成账号注册、实名认证和云资源创建。

Docker 镜像构建在本机尝试时因 Docker Hub 基础镜像拉取超时未完成，Dockerfile 本身已通过 Docker 构建器解析，Compose 配置已通过本地校验。

部署文件已就绪。完成账号配置后，可按以下流程上线：

1. 将本仓库推送到 GitHub
2. 在 Render 中选择 Blueprint 或 Docker 服务，关联仓库
3. 配置 `DASHSCOPE_API_KEY`、`EMAIL_SENDER`、`EMAIL_AUTH_CODE`、`EMAIL_TO`
4. 获取公网 URL 后补充到本 README 的部署证明板块

---

## 项目结构

```text
config/sources.yaml              # 新闻源、邮件与任务配置
main/run_graph.py                # 命令行完整工作流
main/demo_product.py             # 无密钥产品演示
src/news_agent/api.py            # FastAPI 服务
src/news_agent/web/index.html    # Web 控制台
src/news_agent/service.py        # Agent 业务服务层
src/news_agent/intent.py         # 意图识别分流
src/news_agent/storage.py        # SQLite 持久化
src/news_agent/observability.py  # Langfuse 追踪
src/news_agent/graph.py          # LangGraph 工作流
tests/                           # 自动化测试
examples/demo_report.md          # 示例日报
docs/INTERVIEW.md                # 作品说明与答辩材料
Dockerfile                       # 容器镜像
docker-compose.yml               # 本地容器编排
render.yaml                      # Render 部署配置
railway.json                     # Railway 部署配置
```

---

## 测试

```bash
uv run pytest tests/
```

当前测试覆盖：

- 配置文件解析
- 运行环境依赖
- 文本清洗
- 标题去重
- 意图识别
- SQLite 持久化
- 产品演示输出
