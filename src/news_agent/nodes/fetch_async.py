import asyncio
import aiohttp
import feedparser
from typing import Dict, List
from datetime import datetime

from ..utils.logger import logger

from ..state import AgentState


async def fetch_one_rss(
    session: aiohttp.ClientSession, rss_url: str, timeout: int = 10
) -> List[Dict]:
    try:
        async with session.get(
            rss_url, timeout=aiohttp.ClientTimeout(total=timeout)
        ) as resp:
            if resp.status != 200:
                logger.error(f"抓取失败 (状态码 {resp.status}): {rss_url}")
                return []
            html = await resp.text()

        feed = feedparser.parse(html)
        articles = []

        for entry in feed.entries[:5]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            if not title or not link:
                continue

            articles.append(
                {
                    "title": title,
                    "link": link,
                    "summary": entry.get("summary", "暂无摘要").strip(),
                    "published": entry.get("published", "未知时间").strip(),
                }
            )

        logger.info(f"成功从 {rss_url} 抓取 {len(articles)} 篇文章")
        return articles

    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"抓取 {rss_url} 时发生网络错误: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"解析 {rss_url} 时发生错误: {str(e)}")
        return []


async def fetch_sources_async_node(state: AgentState) -> AgentState:
    logger.info("开始并发抓取新闻源...")
    start_time = datetime.now()

    config = state.get("config", {})
    sources = config.get("sources", [])

    if not sources:
        logger.warning("未在配置中找到新闻源")
        state["raw_articles"] = []
        return state

    all_articles = []
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_one_rss(session, source.get("url", "").strip())
            for source in sources
            if source.get("url", "").strip()
        ]

        results = await asyncio.gather(*tasks)

    for res in results:
        all_articles.extend(res)

    cost = (datetime.now() - start_time).total_seconds()
    logger.info(f"抓取完成：共获取 {len(all_articles)} 篇原始文章 | 耗时: {cost:.2f}s")

    state["raw_articles"] = all_articles
    return state
