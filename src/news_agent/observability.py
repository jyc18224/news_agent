import os

from news_agent.utils.logger import logger


def langfuse_enabled() -> bool:
    return os.getenv("LANGFUSE_ENABLED", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_langfuse():
    if not langfuse_enabled():
        return None
    try:
        from langfuse import Langfuse

        return Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )
    except Exception as exc:
        logger.warning("Langfuse is enabled but could not be initialized: %s", exc)
        return None


def capture_run_trace(
    *,
    task_id: str,
    user_input: str,
    intent: str,
    model_output: str,
    duration_ms: int,
    status: str,
    error_message: str | None = None,
) -> None:
    langfuse = get_langfuse()
    if langfuse is None:
        return

    try:
        langfuse.trace(
            name="news-agent",
            session_id=task_id,
            input={
                "query": user_input,
                "intent": intent,
            },
            output={
                "status": status,
                "duration_ms": duration_ms,
                "report_preview": model_output[:500],
                "error": error_message,
            },
            metadata={
                "source": "news_agent",
                "task_id": task_id,
            },
        )
        langfuse.flush()
    except Exception as exc:
        logger.warning("Failed to capture Langfuse trace: %s", exc)
