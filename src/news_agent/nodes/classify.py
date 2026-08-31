import os
import json
import re
from datetime import datetime
from typing import List, Dict

from openai import OpenAI

from ..utils.logger import logger
from ..utils.cache import get_category_cache, set_category_cache

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

CATEGORIES = ["科技", "财经", "娱乐", "体育", "教育", "健康", "其他"]


def classify_batch(articles: List[Dict]) -> List[Dict]:
    if not articles:
        return []

    need_classify_indices = []
    for idx, art in enumerate(articles):
        title = art.get("title", "")
        cached_cat = get_category_cache(title)
        if cached_cat:
            art["category"] = cached_cat
        else:
            need_classify_indices.append(idx)

    if not need_classify_indices:
        logger.info("所有文章分类均在缓存中找到。")
        return articles

    lines = [
        f"{i+1}. 标题: {articles[idx].get('title', '')}"
        for i, idx in enumerate(need_classify_indices)
    ]

    prompt = f"""
请将以下新闻标题归类到这些类别中：{', '.join(CATEGORIES)}。
要求：
1. 仅返回一个 JSON 数组，包含分类名称字符串。
2. 数组长度必须与输入标题数量完全一致。
3. 不要包含任何解释或多余文本。
4. 如果无法确定分类，请归类为“其他”。

新闻标题列表：
{chr(10).join(lines)}

JSON 数组：
"""

    try:
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
        )
        content = resp.choices[0].message.content.strip()

        match = re.search(r"\[.*\]", content, re.DOTALL)
        if match:
            results = json.loads(match.group(0))
            for i, idx in enumerate(need_classify_indices):
                if i < len(results):
                    cat = results[i] if results[i] in CATEGORIES else "其他"
                    articles[idx]["category"] = cat
                    set_category_cache(articles[idx].get("title", ""), cat)

    except Exception as e:
        logger.error(f"批量分类失败: {e}")
        for idx in need_classify_indices:
            articles[idx]["category"] = "其他"

    return articles


def classify_node(state: dict) -> dict:
    logger.info("开始文章分类...")
    start_time = datetime.now()

    articles = state.get("deduped_articles", [])
    classified = classify_batch(articles)

    cost = (datetime.now() - start_time).total_seconds()
    logger.info(f"分类完成：共处理 {len(classified)} 篇文章 | 耗时: {cost:.2f}s")

    return {"classified_articles": classified}
