from difflib import SequenceMatcher
from datetime import datetime
from ..state import AgentState
from ..utils.logger import logger

def similarity(a: str, b: str) -> float:
    """计算两个字符串的相似度比例。"""
    return SequenceMatcher(None, a, b).ratio()

def dedup_node(state: AgentState) -> dict:
    """
    LangGraph 节点：基于标题相似度对文章进行去重。
    """
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
            
        # 精确标题匹配校验
        if title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(art)

    cost = (datetime.now() - start_time).total_seconds()
    logger.info(f"去重完成：{len(raw_articles)} -> {len(unique_articles)} 篇 | 耗时: {cost:.2f}s")

    return {"deduped_articles": unique_articles}