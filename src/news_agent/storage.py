import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_DB_PATH = Path(os.getenv("NEWS_AGENT_DB_PATH", "data/news_agent.db"))
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_db_path(db_path: str | Path | None = None) -> Path:
    if db_path:
        return Path(db_path)
    configured = os.getenv("NEWS_AGENT_DB_PATH")
    if configured:
        return Path(configured)
    return PROJECT_ROOT / DEFAULT_DB_PATH


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path | None = None) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                user_input TEXT NOT NULL,
                intent TEXT NOT NULL,
                model_output TEXT,
                duration_ms INTEGER,
                status TEXT NOT NULL,
                error_message TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def new_task_id() -> str:
    return uuid.uuid4().hex[:12]


def save_task_run(
    *,
    task_id: str | None = None,
    user_input: str,
    intent: str,
    model_output: str,
    duration_ms: int,
    status: str,
    error_message: str | None = None,
    db_path: str | Path | None = None,
) -> str:
    init_db(db_path)
    task_id = task_id or new_task_id()
    created_at = datetime.now(timezone.utc).isoformat()
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO task_runs (
                task_id, user_input, intent, model_output, duration_ms,
                status, error_message, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                user_input,
                intent,
                model_output,
                int(duration_ms),
                status,
                error_message,
                created_at,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return task_id


def list_task_runs(limit: int = 20, db_path: str | Path | None = None) -> list[dict]:
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT task_id, user_input, intent, status, duration_ms, created_at
            FROM task_runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_task_run(task_id: str, db_path: str | Path | None = None) -> dict | None:
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT task_id, user_input, intent, model_output, duration_ms,
                   status, error_message, created_at
            FROM task_runs
            WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
