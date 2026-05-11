import os
from datetime import datetime
from typing import List, Dict

from openai import OpenAI

from ..utils.logger import logger
from ..utils.cache import (
    get_category_cache,
    set_category_cache
)

# 初始化 LLM 客户端（全局唯一，规范）
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 预定义分类（全局常量）
CATEGORIES = ["科技", "财经", "娱乐", "体育", "教育", "健康", "其他"]

# ----------------------
# 5.23 单篇分类（保留备用）
# ----------------------
def classify_single(title: str, content: str = "") -> str:
    if not title:
        return "其他"

    prompt = f"""你是新闻分类助手，只返回分类名称。
可选类别：{','.join(CATEGORIES)}
标题：{title}
分类："""

    try:
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10
        )
        res = resp.choices[0].message.content.strip()
        return res if res in CATEGORIES else "其他"
    except Exception:
        return "其他"

# ----------------------
# 5.24 批量分类（核心）
# ----------------------
def classify_batch(articles: List[Dict]) -> List[Dict]:
    if not articles:
        return []

    # 需要分类的文章（缓存里没有的）
    need_classify = []
    # 先遍历缓存
    for idx, art in enumerate(articles):
        title = art.get("title", "")
        # ===================== 【缓存】 =====================
        cached_cat = get_category_cache(title)
        if cached_cat is not None:
            art["category"] = cached_cat
        else:
            need_classify.append(idx)
        # ====================================================

    # 只对缓存没有的文章进行分类
    lines = []
    for idx in need_classify:
        art = articles[idx]
        title = art.get("title", "")
        lines.append(f"{len(lines) + 1}. 标题：{title}")

    if not lines:
        logger.info("✅ 所有文章分类都在缓存中，无需调用LLM！")
        return articles
    prompt = f"""
你是新闻分类助手，请对以下新闻标题进行分类。
只能从以下类别选择：{','.join(CATEGORIES)}
要求：
1. 严格返回 JSON 数组，例如 ["科技","财经","其他"]
2. 数量必须与输入一致
3. 不要解释，不要多余内容
4. 分类错误则填“其他”

待分类列表：
{chr(10).join(lines)}

返回 JSON 数组：
"""

    try:
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200
        )
        result = resp.choices[0].message.content.strip()
        import json
        import re
        match = re.search(r"\[.*\]", result, re.DOTALL)
        categories = json.loads(match.group(0)) if match else []

        # 把结果填回去 + 写入缓存
        for i, idx in enumerate(need_classify):
            cat = categories[i] if i < len(categories) else "其他"
            articles[idx]["category"] = cat
            # ===================== 【缓存】 =====================
            set_category_cache(articles[idx]["title"], cat)

        return articles

    except Exception as e:
        logger.error(f"批量分类失败：{str(e)}")
        for art in articles:
            art["category"] = "其他"
        return articles

# ----------------------
# 5.25 分类节点（给图用）
# ----------------------
def classify_node(state):
    # 【新增日志】：开始分类的提示
    logger.info("🏷️  开始批量分类...")
    # 【新增耗时统计】：记录开始时间
    start = datetime.now()
    articles = state.get("cleaned_articles", [])
    if not articles:
        logger.info("✅ 无文章，分类直接完成")
        return {"classified_articles": []}
    classified_articles = classify_batch(articles)
    # 【新增耗时统计】：计算并打印耗时
    cost = (datetime.now() - start).total_seconds()
    logger.info(f"✅ 分类完成，共 {len(classified_articles)} 篇 | 耗时 {cost:.2f}s")

    return {
        "classified_articles": classified_articles
    }