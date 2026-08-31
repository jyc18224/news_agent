from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from news_agent.config import PROJECT_ROOT
from news_agent.service import route_agent_request
from news_agent.storage import get_task_run, init_db, list_task_runs


APP_VERSION = "0.2.0"
WEB_INDEX = Path(__file__).resolve().parent / "web" / "index.html"
DEMO_REPORT = PROJECT_ROOT / "examples" / "demo_report.md"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="NewsAgent Agent Service",
    description="AI 新闻早报 Agent 的标准化 HTTP API 与 Web 入口",
    version=APP_VERSION,
    lifespan=lifespan,
)


class AgentRunRequest(BaseModel):
    query: str = "看今日简报"
    confirm_email: bool = False
    send_email: bool = False


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    if WEB_INDEX.exists():
        return WEB_INDEX.read_text(encoding="utf-8")
    return """
    <html>
      <body style="font-family:sans-serif;padding:2rem">
        <h1>NewsAgent</h1>
        <p>Web UI file not found. Use the API at /api/agent/run.</p>
      </body>
    </html>
    """


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "news-agent",
        "version": APP_VERSION,
    }


@app.get("/api/demo")
async def demo_report() -> dict:
    if DEMO_REPORT.exists():
        return {"report": DEMO_REPORT.read_text(encoding="utf-8")}
    return {"report": "示例报告暂时不可用。"}


@app.post("/api/agent/run")
async def run_agent(request: AgentRunRequest) -> dict:
    try:
        return await route_agent_request(
            query=request.query,
            confirm_email=request.confirm_email,
            send_email=request.send_email,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent 运行失败：{exc}") from exc


@app.get("/api/tasks")
async def tasks(limit: int = 20) -> dict:
    return {"tasks": list_task_runs(limit=limit)}


@app.get("/api/tasks/{task_id}")
async def task_detail(task_id: str) -> dict:
    task = get_task_run(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task
