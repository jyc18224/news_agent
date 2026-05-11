from difflib import SequenceMatcher
from state import AgentState
from utils.logger import logger
from datetime import datetime

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def dedup_node(state: AgentState):
    # ===================== 【6.5新增】安全获取文章 =====================
    raw = state.get("raw_articles", [])
    # 【新增日志】：开始去重的提示
    logger.info("🔍 开始去重...")
    # 【新增耗时统计】：记录开始时间
    start = datetime.now()

    raw = state["raw_articles"]
    logger.info(f"【去重】拿到文章数：{len(raw)}")

    seen = set()
    new_articles = []
    for art in raw:
        # ===================== 【6.5新增】空标题跳过 =====================
        title = art.get("title", "").strip()
        if not title:
            continue
        if title not in seen:
            seen.add(title)
            new_articles.append(art)

    # 【新增耗时统计】：计算并打印耗时
    cost = (datetime.now() - start).total_seconds()
    logger.info(f"✅ 去重完成：{len(raw)} → {len(new_articles)} 篇 | 耗时 {cost:.2f}s")

    return {"deduped_articles": new_articles}