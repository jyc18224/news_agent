import os
from datetime import datetime
from typing import List, Dict
from collections import defaultdict
from openai import OpenAI

from ..utils.cache import (
    get_summary_cache,
    get_category_summary_cache,
    set_summary_cache,
)
from ..utils.logger import logger

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def generate_summary(article: Dict) -> Dict:
    title = article.get("title", "").strip()
    content = article.get("content", "").strip()

    cached = get_summary_cache(title)
    if cached:
        article["summary"] = cached
        return article

    if not content or len(content) < 50:
        summary = title
    else:
        prompt = f"""请为以下新闻生成简洁摘要（20-50字）。
标题：{title}
正文：{content}
摘要："""
        try:
            resp = client.chat.completions.create(
                model="qwen-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150,
            )
            summary = resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"摘要生成失败 '{title}': {e}")
            summary = title

    article["summary"] = summary
    set_summary_cache(title, summary)
    return article


def summarize_single_batch_node(state: dict) -> dict:
    logger.info("开始生成单篇摘要...")
    start_time = datetime.now()

    articles = state.get("classified_articles", [])
    summarized = [generate_summary(art) for art in articles]

    cost = (datetime.now() - start_time).total_seconds()
    logger.info(f"单篇摘要完成：共处理 {len(summarized)} 篇文章 | 耗时: {cost:.2f}s")

    return {"classified_articles": summarized}


def summarize_by_category(articles: List[Dict]) -> Dict:
    grouped = defaultdict(list)
    for art in articles:
        cat = art.get("category", "其他")
        grouped[cat].append(art)

    category_summary = {}
    for cat, arts in grouped.items():
        cached_summary = get_category_summary_cache(cat)
        if cached_summary:
            category_summary[cat] = {"count": len(arts), "summary": cached_summary}
            continue

        titles_text = "\n".join([f"- {a.get('title', '无标题')}" for a in arts])
        prompt = f"""你是专业的新闻编辑。请为以下【{cat}】类的新闻生成一段 80-150 字的整合摘要。
新闻标题列表：
{titles_text}

整合摘要："""

        try:
            resp = client.chat.completions.create(
                model="qwen-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500,
            )
            summary = resp.choices[0].message.content.strip()
            category_summary[cat] = {"count": len(arts), "summary": summary}
        except Exception as e:
            logger.error(f"分类汇总摘要失败 '{cat}': {e}")
            category_summary[cat] = {
                "count": len(arts),
                "summary": "生成汇总摘要失败。",
            }

    return category_summary


def summarize_category_node(state: dict) -> dict:
    logger.info("开始生成类别汇总摘要...")
    start_time = datetime.now()

    articles = state.get("classified_articles", [])
    summary_result = summarize_by_category(articles)

    cost = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"类别汇总完成：共处理 {len(summary_result)} 个类别 | 耗时: {cost:.2f}s"
    )

    return {"category_summary": summary_result}


def extra_check_node(state: dict) -> dict:
    count = len(state.get("classified_articles", []))
    logger.info(f"触发额外校验节点：正在处理 {count} 篇文章。")
    return state
