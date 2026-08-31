from __future__ import annotations

from collections import defaultdict
from time import perf_counter

from news_agent.config import PROJECT_ROOT, load_config
from news_agent.graph import graph
from news_agent.intent import extract_topic, detect_intent
from news_agent.nodes.dedup import dedup_node
from news_agent.nodes.fetch_async import fetch_sources_async_node
from news_agent.observability import capture_run_trace
from news_agent.storage import new_task_id, save_task_run
from news_agent.utils.cleaner import clean_articles_node


def _initial_state(config: dict) -> dict:
    return {
        "config": config,
        "raw_articles": [],
        "deduped_articles": [],
        "cleaned_articles": [],
        "classified_articles": [],
        "category_summary": {},
        "report": "",
        "email_sent": False,
        "email_error": None,
    }


async def run_daily_briefing(
    *,
    sources_path: str = "config/sources.yaml",
    output_path: str | None = None,
    confirm_email: bool = False,
    send_email: bool | None = None,
) -> dict:
    config = load_config(sources_path)
    email_config = config.setdefault("email", {})
    if send_email is False:
        email_config["enabled"] = False
    if send_email is True:
        email_config["enabled"] = True
    if confirm_email:
        email_config["confirm_before_send"] = True

    start = perf_counter()
    final_state = await graph.ainvoke(
        _initial_state(config),
        {"configurable": {"thread_id": "news_agent"}},
    )
    duration_ms = int((perf_counter() - start) * 1000)

    report = final_state.get("report", "")
    if output_path and report:
        output = PROJECT_ROOT / output_path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")

    return {
        "report": report,
        "duration_ms": duration_ms,
        "stats": {
            "raw_articles": len(final_state.get("raw_articles", [])),
            "cleaned_articles": len(final_state.get("cleaned_articles", [])),
            "classified_articles": len(final_state.get("classified_articles", [])),
            "email_sent": final_state.get("email_sent", False),
            "email_error": final_state.get("email_error"),
        },
    }


def _render_topic_report(topic: str, articles: list[dict]) -> str:
    lines = [
        f"# 主题检索报告：{topic}",
        "",
        f"共找到 {len(articles)} 篇相关新闻。",
        "",
    ]
    grouped = defaultdict(list)
    for article in articles:
        grouped[article.get("category", "未分类")].append(article)

    for category, items in grouped.items():
        lines.append(f"## 【{category}】 ({len(items)} 篇)")
        lines.append("")
        lines.append("| 标题 | 摘要 | 来源 |")
        lines.append("| :--- | :--- | :--- |")
        for article in items:
            title = article.get("title", "无标题").replace("|", " ").replace("\n", " ")
            summary = (
                article.get("summary", "无摘要").replace("|", " ").replace("\n", " ")
            )
            source = article.get("source", "-").replace("|", " ").replace("\n", " ")
            lines.append(f"| {title} | {summary} | {source} |")
        lines.append("")

    return "\n".join(lines)


async def run_topic_search(
    *,
    query: str,
    sources_path: str = "config/sources.yaml",
    max_articles: int = 10,
) -> dict:
    topic = extract_topic(query)
    config = load_config(sources_path)
    state = await fetch_sources_async_node(_initial_state(config))
    state = dedup_node(state)
    state = clean_articles_node(state)

    terms = [part for part in topic.lower().split() if part]
    matched = []
    for article in state.get("cleaned_articles", []):
        haystack = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        if any(term in haystack for term in terms) or topic.lower() in haystack:
            matched.append(article)
        if len(matched) >= max_articles:
            break

    report = _render_topic_report(topic, matched)
    return {
        "report": report,
        "topic": topic,
        "matched_articles": len(matched),
    }


async def route_agent_request(
    *,
    query: str,
    confirm_email: bool = False,
    send_email: bool = False,
    sources_path: str = "config/sources.yaml",
) -> dict:
    task_id = new_task_id()
    intent = detect_intent(query)
    start = perf_counter()

    try:
        if intent == "topic_search":
            result = await run_topic_search(query=query, sources_path=sources_path)
        else:
            result = await run_daily_briefing(
                sources_path=sources_path,
                confirm_email=confirm_email,
                send_email=send_email,
            )

        duration_ms = int((perf_counter() - start) * 1000)
        model_output = result.get("report", "")
        save_task_run(
            task_id=task_id,
            user_input=query,
            intent=intent,
            model_output=model_output,
            duration_ms=duration_ms,
            status="success",
        )
        capture_run_trace(
            task_id=task_id,
            user_input=query,
            intent=intent,
            model_output=model_output,
            duration_ms=duration_ms,
            status="success",
        )
        return {
            "task_id": task_id,
            "intent": intent,
            "status": "success",
            "duration_ms": duration_ms,
            "report": model_output,
            **result,
        }
    except Exception as exc:
        duration_ms = int((perf_counter() - start) * 1000)
        error_message = str(exc)
        save_task_run(
            task_id=task_id,
            user_input=query,
            intent=intent,
            model_output="",
            duration_ms=duration_ms,
            status="failed",
            error_message=error_message,
        )
        capture_run_trace(
            task_id=task_id,
            user_input=query,
            intent=intent,
            model_output="",
            duration_ms=duration_ms,
            status="failed",
            error_message=error_message,
        )
        raise
