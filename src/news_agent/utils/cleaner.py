import re
from news_agent.utils.logger import logger
from datetime import datetime
from ..state import AgentState


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def clean_articles_node(state: AgentState):
    # 【新增日志】：开始清洗的提示
    logger.info("🧹 开始清洗文章...")
    # 【新增耗时统计】：记录开始时间
    start = datetime.now()
    # ===================== 【6.5新增】安全获取文章 =====================
    articles = state.get("deduped_articles", [])

    logger.info(f"【清洗】拿到文章数：{len(articles)}")

    cleaned = []
    for art in articles:
        cleaned.append({
            **art,
            "title": clean_text(art.get("title", "")),
            # ===================== 【6.5新增】摘要默认值 =====================
            "summary": clean_text(art.get("summary", "暂无摘要"))
            # ==================================================================
        })

    cost = (datetime.now() - start).total_seconds()
    logger.info(f"✅ 清洗完成 | 耗时 {cost:.2f}s")
    return {"cleaned_articles": cleaned}