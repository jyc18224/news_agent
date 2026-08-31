import re
from datetime import datetime
from ..utils.logger import logger
from ..state import AgentState


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_articles_node(state: AgentState) -> dict:
    logger.info("开始文章文本清洗...")
    start_time = datetime.now()

    articles = state.get("deduped_articles", [])
    cleaned_articles = []

    for art in articles:
        cleaned_articles.append(
            {
                **art,
                "title": clean_text(art.get("title", "")),
                "summary": clean_text(art.get("summary", "暂无摘要")),
            }
        )

    cost = (datetime.now() - start_time).total_seconds()
    logger.info(f"清洗完成：共处理 {len(cleaned_articles)} 篇文章 | 耗时: {cost:.2f}s")

    return {"cleaned_articles": cleaned_articles}
