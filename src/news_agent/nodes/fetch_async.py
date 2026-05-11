# 导入异步核心库，用于异步任务调度
import asyncio
# 异步网络请求库，相当于异步版的requests，专门做异步爬虫
import aiohttp
# 专门用来解析RSS/XML订阅源的库
import feedparser
# 类型注解：用来标记字典、列表类型，方便代码可读性和IDE提示
from typing import Dict, List
# 导入自定义日志工具，用来打印格式化的日志（INFO/ERROR）
from news_agent.utils.logger import logger
# 👇 从根目录导入 state
from ..state import AgentState
from datetime import datetime


# ===================== 单个RSS源 异步抓取函数 =====================
async def fetch_one_rss(session: aiohttp.ClientSession, rss_url: str, timeout: int = 10) -> List[Dict]:
    """异步抓取单个RSS，最多返回5篇"""
    try:
        async with session.get(rss_url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
            if resp.status != 200:
                logger.error(f"RSS状态码异常: {rss_url}  status={resp.status}")
                return []
            # 这里用 html 还是 text 都可以！不影响！
            html = await resp.text()

        feed = feedparser.parse(html)
        articles = []

        for entry in feed.entries[:5]:
            # ===================== 【6.5新增】异常加固 =====================
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not title or not link:
                logger.warning("⚠️ 无效文章（无标题/无链接），自动跳过")
                continue
            # ============================================================

            articles.append({
                "title": title,
                "link": link,
                # ===================== 【6.5新增】默认值 =====================
                "summary": entry.get("summary", "暂无摘要").strip(),
                "published": entry.get("published", "未知时间").strip()
                # ============================================================
            })

        logger.info(f"✅ 成功抓取 {len(articles)} 篇文章: {rss_url}")
        return articles

    except aiohttp.ClientError as e:
        logger.error(f"❌ 网络连接失败 {rss_url} : {str(e)}")
        return []
    except Exception as e:
        logger.error(f"❌ 解析RSS失败 {rss_url} : {str(e)}")
        return []


# ===================== 异步并发批量抓取所有RSS源 =====================
async def fetch_sources_async_node(state: AgentState):
    logger.info("🚀 开始抓取新闻源...")  # 6.4 新增：开始日志
    start = datetime.now()  # 6.4 新增：开始计时

    config = state["config"]
    sources = config.get("sources", [])

    if not sources:
        logger.warning("没有新闻源")
        return {"raw_articles": []}

    all_articles = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for source in sources:
            # ===================== 【6.5新增】单源URL判空 =====================
            url = source.get("url", "").strip()
            name = source.get("name", "未知源")
            if not url:
                logger.warning(f"⚠️ 新闻源【{name}】无有效RSS地址，跳过")
                continue
            logger.info(f"🔍 准备抓取: {source.get('name', '')} | {url}")
            tasks.append(fetch_one_rss(session, url))
        results = await asyncio.gather(*tasks)

    for res in results:
        all_articles.extend(res)

    logger.info(f"📊 抓取结束，共 {len(all_articles)} 篇原始文章")
    # 6.4 新增：结束日志 + 耗时
    cost = (datetime.now() - start).total_seconds()
    logger.info(f"📊 抓取完成，总计 {len(all_articles)} 篇 | 耗时 {cost:.2f}s")
    # 异步必须手动写进 state，再返回
    state["raw_articles"] = all_articles
    return state