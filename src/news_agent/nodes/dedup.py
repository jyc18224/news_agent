from difflib import SequenceMatcher
from datetime import datetime
from ..state import AgentState
from ..utils.logger import logger


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def dedup_node(state: AgentState) -> dict:
    logger.info("开始文章去重...")
    start_time = datetime.now()

    raw_articles = state.get("raw_articles", [])
    if not raw_articles:
        logger.warning("没有可去重的文章。")
        return {"deduped_articles": []}

    seen_titles = set()
    unique_articles = []

    for art in raw_articles:
        title = art.get("title", "").strip()
        if not title:
            continue

        if title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(art)

    cost = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"去重完成：{len(raw_articles)} -> {len(unique_articles)} 篇 | 耗时: {cost:.2f}s"
    )

    return {"deduped_articles": unique_articles}
